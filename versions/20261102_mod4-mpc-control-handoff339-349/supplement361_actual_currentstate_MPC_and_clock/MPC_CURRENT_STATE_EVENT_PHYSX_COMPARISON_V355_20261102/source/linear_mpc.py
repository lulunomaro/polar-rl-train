"""Condensed, bounded finite-horizon tracking MPC for the MOD4 ground chart.

No MuJoCo import or physics execution occurs here.  The 14-state order follows
``full_lqr.AsymmetricPlant``::

    x, yaw, pitch, Lhip, Lcrank-Lhip, Rhip, Rcrank-Rhip,
    xdot, yawdot, pitchdot, Lhipdot, Ldeltadot, Rhipdot, Rdeltadot

Torque order is (Lhip,Lcrank,Lwheel,Rhip,Rcrank,Rwheel).  ``command`` returns
one absolute torque vector; ``last_log``, ``predicted`` (N+1 by14) and
``predicted_tau`` (N by6) expose diagnostics and the optimized prediction.
The plant's existing inverse-PD/processed-target delay/DC-envelope path still
owns actual application.  This planning model does not simulate those queues.

The linearization center ALWAYS remains the supplied nominal q/tau.  A changed
tracking reference changes only a linear cost term, not force equilibrium::

    e_next = Ad @ (x - x_equilibrium) + Bd @ (tau - tau_equilibrium)

The cost is 1/2 times sum_{k=0}^{N-1}(e_k-r)'Q(e_k-r)+du_k'Rdu_k,
plus terminal (e_N-r)'P(e_N-r).  The initial-state cost is included in logs
but omitted from optimization as a constant.  Q,R,P come from the LQR gain.
With terminal DARE P and an inactive bound, zero-reference MPC equals LQR.

Prediction, Hessian, reference maps and unconstrained feedback maps are built
once.  L-BFGS-B receives analytic gradients for a diagonally equilibrated QP;
no optional optimizer package is installed.  ``velocity6`` freezes the CURRENT
signed DC envelope over the horizon as an explicit approximation.  Execution
must still clip against actual speed every physical step.  The module records
measured solve time; a 20 ms runtime target is not a timing guarantee.
"""
from __future__ import annotations

from numbers import Integral
import argparse
import json
import math
import time

import numpy as np

STATE_DIM = 14
CONTROL_DIM = 6
ACTUATOR_ORDER = (
    "left_hip", "left_crank", "left_wheel_spin",
    "right_hip", "right_crank", "right_wheel_spin",
)
DEFAULT_Q = np.diag([10., 100., 600., 100., 200., 100., 200.,
                     20., 15., 40., 8., 10., 8., 10.])
DEFAULT_R = np.diag([.08, .08, .1] * 2)
EFFORT6 = np.array([40., 40., 5.775909774436091] * 2)
STALL6 = np.array([53.333333333333336, 53.333333333333336,
                   28.18532894736838] * 2)
NO_LOAD6 = np.array([16.755160819145562, 16.755160819145562, 55.3557] * 2)


def _array(value, shape, name):
    result = np.asarray(value, dtype=np.float64)
    if result.shape != shape or not np.isfinite(result).all():
        raise ValueError(f"{name} must have finite shape {shape}")
    return result.copy()


def _matvec(matrix, vector):
    """Small dense matvec without a many-thread BLAS dispatch per iteration."""
    return np.einsum('ij,j->i', matrix, vector, optimize=False)


def _weight(value, size, name, positive=False):
    matrix = _array(value, (size, size), name)
    if not np.allclose(matrix, matrix.T, atol=1e-10, rtol=1e-10):
        raise ValueError(name + " must be symmetric")
    matrix = .5 * (matrix + matrix.T)
    minimum = float(np.linalg.eigvalsh(matrix)[0])
    if minimum < -1e-9 or (positive and minimum <= 0):
        raise ValueError(name + " must be positive " + ("definite" if positive else "semidefinite"))
    return matrix


class LinearMPC:
    """One fixed-ground-linearization tracking MPC with feasible warm starts.

    ``gain`` is the dict returned by full_lqr, including nominal ``q`` (7 or14),
    ``tau`` (6), continuous A/B or discrete Ad/Bd, and preferably Q/R/P/K.
    Ad/Bd are assumed to use gain['dt'] or .01 seconds when no clock is stored.
    ``command(x14, ref14, velocity6=None)`` returns an ndarray shape(6,).

    Public tuning: max_iterations=60, gradient_tolerance=1e-5,
    function_tolerance=1e-9.  A failed/limited solve selects the lower-cost
    feasible candidate between its result and the shifted prior trajectory.
    Call reset() after episode reset or changing to a different plant phase.
    This local ground controller does not implement flight/landing logic.
    """

    def __init__(self, gain, horizon=20, dt=.01):
        if not isinstance(gain, dict):
            raise ValueError("gain must be the full_lqr return dict")
        if isinstance(horizon, bool) or not isinstance(horizon, Integral) or horizon < 1:
            raise ValueError("horizon must be a positive integer")
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be positive and finite")
        self.horizon = int(horizon)
        self.dt = float(dt)
        self.max_iterations = 60
        self.gradient_tolerance = 1e-5
        self.function_tolerance = 1e-9
        center = np.asarray(gain['q'], dtype=np.float64)
        if center.shape == (7,):
            center = np.r_[center, np.zeros(7)]
        self.x_equilibrium = _array(center, (STATE_DIM,), "gain q")
        self.tau_equilibrium = _array(gain['tau'], (CONTROL_DIM,), "gain tau")
        self.Q = _weight(gain.get('Q', DEFAULT_Q), STATE_DIM, 'Q')
        self.R = _weight(gain.get('R', DEFAULT_R), CONTROL_DIM, 'R', positive=True)
        gain_dt = float(gain.get('dt', gain.get('dt_s', .01)))
        use_saved_discrete = ('Ad' in gain and 'Bd' in gain and
                              np.isclose(gain_dt, self.dt, atol=1e-14, rtol=0))
        if use_saved_discrete:
            self.Ad = _array(gain['Ad'], (STATE_DIM, STATE_DIM), 'Ad')
            self.Bd = _array(gain['Bd'], (STATE_DIM, CONTROL_DIM), 'Bd')
        else:
            from scipy.linalg import expm
            continuous_a = _array(gain['A'], (STATE_DIM, STATE_DIM), 'A')
            continuous_b = _array(gain['B'], (STATE_DIM, CONTROL_DIM), 'B')
            augmented = np.zeros((STATE_DIM + CONTROL_DIM, STATE_DIM + CONTROL_DIM))
            augmented[:STATE_DIM, :STATE_DIM] = continuous_a
            augmented[:STATE_DIM, STATE_DIM:] = continuous_b
            discrete = expm(augmented * self.dt)
            self.Ad = discrete[:STATE_DIM, :STATE_DIM]
            self.Bd = discrete[:STATE_DIM, STATE_DIM:]
        if 'P' in gain and use_saved_discrete:
            terminal = gain['P']
        else:
            from scipy.linalg import solve_discrete_are
            terminal = solve_discrete_are(self.Ad, self.Bd, self.Q, self.R)
        self.P = _weight(terminal, STATE_DIM, 'P')
        if 'K' in gain and use_saved_discrete:
            self.K = _array(gain['K'], (CONTROL_DIM, STATE_DIM), 'K')
        else:
            self.K = np.linalg.solve(self.R + self.Bd.T @ self.P @ self.Bd,
                                     self.Bd.T @ self.P @ self.Ad)

        n, m, N = STATE_DIM, CONTROL_DIM, self.horizon
        self.Sx = np.zeros((N * n, n))
        self.Su = np.zeros((N * n, N * m))
        powers = [np.eye(n)]
        for _ in range(N):
            powers.append(powers[-1] @ self.Ad)
        for row in range(N):
            self.Sx[row*n:(row+1)*n] = powers[row+1]
            for col in range(row+1):
                self.Su[row*n:(row+1)*n, col*m:(col+1)*m] = powers[row-col] @ self.Bd
        weighted_su = self.Su.copy()
        weighted_sx = self.Sx.copy()
        reference_matrix = np.zeros((N*n, n))
        for row in range(N):
            block = slice(row*n, (row+1)*n)
            weight = self.P if row == N-1 else self.Q
            weighted_su[block] = weight @ self.Su[block]
            weighted_sx[block] = weight @ self.Sx[block]
            reference_matrix[block] = weight
        self.Rbar = np.kron(np.eye(N), self.R)
        self.H = self.Su.T @ weighted_su + self.Rbar
        self.H = .5 * (self.H + self.H.T)
        # Fail before control if malformed weights/model produce an indefinite QP.
        np.linalg.cholesky(self.H)
        self.Gx = self.Su.T @ weighted_sx
        self.Gref = self.Su.T @ reference_matrix
        solved = np.linalg.solve(self.H, np.c_[self.Gx, self.Gref])
        self._Hinv_Gx = solved[:, :n]
        self._Hinv_Gref = solved[:, n:]
        self.variable_scale = 1. / np.sqrt(np.diag(self.H))
        self._Hs = self.variable_scale[:, None] * self.H * self.variable_scale[None, :]
        self._last_reference = None
        self._reference_linear = np.zeros(N*m)
        self._reference_unconstrained = np.zeros(N*m)
        try:
            from scipy.optimize import minimize
        except ImportError:
            # The pure NumPy self-test and feasible unconstrained branch need
            # no SciPy; the first genuinely bounded solve reports its absence.
            self._minimize = None
        else:
            self._minimize = minimize
        self.reset()

    def reset(self):
        """Clear the previous plan; do not change dynamics, weights or reference."""
        self._warm = None
        self.predicted = None
        self.predicted_tau = None
        self.last_log = None

    def _torque_bounds(self, velocity6=None):
        if velocity6 is None:
            return -EFFORT6.copy(), EFFORT6.copy()
        speed = _array(velocity6, (CONTROL_DIM,), 'velocity6')
        effective_speed = np.clip(speed, -NO_LOAD6*(1.+EFFORT6/STALL6),
                                  NO_LOAD6*(1.+EFFORT6/STALL6))
        lower = np.maximum(-EFFORT6, STALL6*(-1.-effective_speed/NO_LOAD6))
        upper = np.minimum(EFFORT6, STALL6*(1.-effective_speed/NO_LOAD6))
        return lower, upper

    def _objective(self, du, linear):
        return float(.5 * du @ _matvec(self.H, du) + linear @ du)

    def _scaled_objective(self, scaled, scaled_linear):
        product = _matvec(self._Hs, scaled)
        return float(.5 * scaled @ product + scaled_linear @ scaled), product + scaled_linear

    def _prediction(self, error, du):
        future_error = (_matvec(self.Sx, error) + _matvec(self.Su, du)).reshape(self.horizon, STATE_DIM)
        future = future_error + self.x_equilibrium
        return future_error, future

    def _cost(self, error, reference_error, du, future_error):
        # State0..N-1 get Q; stateN gets P, including the initial constant.
        state_cost = float((error-reference_error) @ self.Q @ (error-reference_error))
        for i in range(self.horizon-1):
            tracking = future_error[i] - reference_error
            state_cost += float(tracking @ self.Q @ tracking)
        terminal = future_error[-1] - reference_error
        state_cost += float(terminal @ self.P @ terminal)
        return .5 * (state_cost + float(du @ _matvec(self.Rbar, du)))

    def command(self, x14, ref14, velocity6=None):
        """Optimize one horizon; return bounded first absolute torque command.

        A constant reference is held over the horizon.  A yaw reference is
        shifted by whole turns to the closest branch to current yaw.  The
        model itself remains the fixed local LQR ground approximation.
        ``velocity6`` is current actuator-output joint rad/s, not state14 rates.
        ``last_log`` is JSON-serializable and contains measured wall time.
        """
        started = time.perf_counter()
        x = _array(x14, (STATE_DIM,), 'x14')
        reference = _array(ref14, (STATE_DIM,), 'ref14')
        error = x - self.x_equilibrium
        reference_error = reference - self.x_equilibrium
        # Avoid a false 2*pi yaw tracking error at the wrapped angle boundary.
        yaw_turn = int(np.rint((x[1]-reference[1])/(2.*math.pi)))
        reference_error[1] = reference[1] + 2.*math.pi*yaw_turn - self.x_equilibrium[1]
        reference_changed = self._last_reference is None or not np.array_equal(reference_error, self._last_reference)
        if reference_changed:
            self._reference_linear = -_matvec(self.Gref, reference_error)
            self._reference_unconstrained = _matvec(self._Hinv_Gref, reference_error)
            self._last_reference = reference_error.copy()
        linear = _matvec(self.Gx, error) + self._reference_linear
        lower_tau, upper_tau = self._torque_bounds(velocity6)
        lower = np.tile(lower_tau-self.tau_equilibrium, self.horizon)
        upper = np.tile(upper_tau-self.tau_equilibrium, self.horizon)
        if not np.all(lower <= upper):
            raise ValueError('inconsistent signed motor torque bounds')
        if self._warm is None:
            # A bounded LQR rollout is a feasible first warm start, not an
            # assertion that a nonzero tracking target is a force equilibrium.
            initial = np.zeros((self.horizon, CONTROL_DIM))
            state = error.copy()
            for i in range(self.horizon):
                initial[i] = np.clip(-self.K @ (state-reference_error),
                                     lower_tau-self.tau_equilibrium,
                                     upper_tau-self.tau_equilibrium)
                state = self.Ad @ state + self.Bd @ initial[i]
            initial = initial.reshape(-1)
        else:
            initial = np.clip(self._warm.reshape(-1), lower, upper)
        unconstrained = -_matvec(self._Hinv_Gx, error) + self._reference_unconstrained
        iterations, evaluations = 0, 0
        converged, status, message = True, 0, 'unconstrained optimum is feasible'
        fallback = False
        if np.all(upper-lower <= 1e-12):
            solution = lower.copy()
            solver = 'fixed_signed_DC_bounds'
            message = 'every decision is fixed by the signed speed envelope'
        elif np.all(unconstrained >= lower-1e-9) and np.all(unconstrained <= upper+1e-9):
            solution = np.clip(unconstrained, lower, upper)
            solver = 'precomputed_unconstrained_condensed_QP'
        else:
            if self._minimize is None:
                from scipy.optimize import minimize
                self._minimize = minimize
            scaled_initial = initial / self.variable_scale
            scaled_lower, scaled_upper = lower/self.variable_scale, upper/self.variable_scale
            scaled_linear = linear * self.variable_scale
            result = self._minimize(
                self._scaled_objective, scaled_initial, args=(scaled_linear,),
                jac=True, method='L-BFGS-B', bounds=list(zip(scaled_lower, scaled_upper)),
                options={'maxiter': int(self.max_iterations), 'gtol': float(self.gradient_tolerance),
                         'ftol': float(self.function_tolerance), 'maxls': 20, 'maxcor': 10},
            )
            candidate = np.asarray(result.x, dtype=float) * self.variable_scale
            finite_candidate = candidate.shape == initial.shape and np.isfinite(candidate).all()
            candidate = np.clip(candidate, lower, upper) if finite_candidate else initial
            fallback = not finite_candidate or self._objective(candidate, linear) > self._objective(initial, linear)
            solution = initial if fallback else candidate
            iterations = int(result.nit)
            evaluations = int(result.nfev)
            converged = bool(result.success) and not fallback
            status = int(result.status)
            message = str(result.message)
            solver = 'scipy_L-BFGS-B_analytic_condensed_QP'
        future_error, future = self._prediction(error, solution)
        plan = solution.reshape(self.horizon, CONTROL_DIM) + self.tau_equilibrium
        self.predicted = np.vstack((x, future))
        self.predicted_tau = plan.copy()
        self._warm = np.vstack((solution.reshape(self.horizon, CONTROL_DIM)[1:],
                                solution.reshape(self.horizon, CONTROL_DIM)[-1:]))
        scaled_solution = solution / self.variable_scale
        _, gradient = self._scaled_objective(scaled_solution, linear*self.variable_scale)
        lower_active = solution <= lower + 1e-8
        upper_active = solution >= upper - 1e-8
        projected = gradient.copy()
        projected[lower_active & (gradient > 0)] = 0
        projected[upper_active & (gradient < 0)] = 0
        torque = plan[0].copy()
        self.last_log = {
            'solver': solver, 'converged': converged, 'iterations': iterations,
            'function_evaluations': evaluations, 'status': status, 'message': message,
            'cost': self._cost(error, reference_error, solution, future_error),
            'initial_feasible_plan_cost': self._cost(error, reference_error, initial,
                                                    self._prediction(error, initial)[0]),
            'used_feasible_warm_start_fallback': fallback,
            'projected_gradient_inf_equilibrated': float(np.max(np.abs(projected))),
            'solve_ms': (time.perf_counter()-started)*1000.,
            'horizon': self.horizon, 'dt_s': self.dt,
            'reference_linear_term_updated': reference_changed,
            'bound_model': 'current_speed_signed_DC_frozen_all_stages' if velocity6 is not None else 'static_effort_all_stages',
            'bound_model_predicts_future_speeds': False,
            'torque_lower6': lower_tau.tolist(), 'torque_upper6': upper_tau.tolist(),
            'first_torque6': torque.tolist(),
            'first_torque_at_bound6': (lower_active[:CONTROL_DIM] | upper_active[:CONTROL_DIM]).tolist(),
            'predicted_terminal_state14': self.predicted[-1].tolist(),
            'predicted_tau_absmax6': np.max(np.abs(plan), axis=0).tolist(),
            'actuator_order': list(ACTUATOR_ORDER),
            'fixed_nominal_linearization': True, 'flight_model_claimed': False,
            'application_target_delay_modeled': False,
        }
        return torque


def _math_self_test():
    """Prediction/gradient/constraint/cache checks using only NumPy."""
    rng = np.random.default_rng(20261101)
    n, m, N = STATE_DIM, CONTROL_DIM, 5
    Ad = .92*np.eye(n)
    Ad[:7, 7:] = .01*np.eye(7)
    Bd = rng.normal(0, .005, (n, m))
    gain = {'q': np.zeros(7), 'tau': np.array([.2, -.3, .1]*2),
            'Ad': Ad, 'Bd': Bd, 'Q': np.eye(n), 'R': .1*np.eye(m),
            'P': 4.*np.eye(n), 'K': np.zeros((m, n))}
    controller = LinearMPC(gain, N)
    error = rng.normal(0, .03, n)
    du = rng.normal(0, .1, N*m)
    future_error, _ = controller._prediction(error, du)
    recurrence = error.copy()
    for i in range(N):
        recurrence = Ad@recurrence + Bd@du[i*m:(i+1)*m]
        assert np.allclose(recurrence, future_error[i], atol=1e-13, rtol=1e-13)
    reference = rng.normal(0, .01, n)
    linear = controller.Gx@error-controller.Gref@reference
    scaled = du/controller.variable_scale
    value, gradient = controller._scaled_objective(scaled, linear*controller.variable_scale)
    finite_difference = np.zeros(N*m)
    eps = 1e-6
    for i in range(N*m):
        plus, minus = scaled.copy(), scaled.copy()
        plus[i] += eps
        minus[i] -= eps
        fp, _ = controller._scaled_objective(plus, linear*controller.variable_scale)
        fm, _ = controller._scaled_objective(minus, linear*controller.variable_scale)
        finite_difference[i] = (fp-fm)/(2*eps)
    assert np.allclose(gradient, finite_difference, atol=1e-9, rtol=2e-6), 'analytic gradient'
    # The condensed objective differs from explicit rollout cost by a constant.
    explicit_difference = controller._cost(error, reference, du, future_error)-controller._cost(error, reference, np.zeros(N*m), controller._prediction(error, np.zeros(N*m))[0])
    assert np.isclose(explicit_difference, controller._objective(du, linear), atol=1e-12)
    x, ref = error.copy(), reference.copy()
    output = controller.command(x, ref)
    expected = -np.linalg.solve(controller.H, linear)
    assert np.allclose(output, gain['tau']+expected[:m], atol=1e-12)
    assert controller.last_log['converged'] and controller.last_log['iterations'] == 0
    assert np.allclose(controller.predicted[0], x)
    assert np.allclose(controller._warm[:-1], expected.reshape(N, m)[1:], atol=1e-13, rtol=1e-13)
    controller.command(x, ref)
    assert not controller.last_log['reference_linear_term_updated']
    json.dumps(controller.last_log, allow_nan=False)
    assert np.array_equal(x, error) and np.array_equal(ref, reference), 'caller inputs unchanged'
    lo, hi = controller._torque_bounds(NO_LOAD6*3)
    assert np.allclose(lo, -EFFORT6) and np.allclose(hi, -EFFORT6)
    lo, hi = controller._torque_bounds(-NO_LOAD6*3)
    assert np.allclose(lo, EFFORT6) and np.allclose(hi, EFFORT6)
    controller.reset()
    assert controller.predicted is None and controller._warm is None
    return {'passed': True, 'physics_steps': 0,
            'checks': ['condensed prediction equals recurrence', 'analytic gradient finite differences',
                       'condensed cost equals explicit cost up to constant', 'unconstrained optimum',
                       'shifted warm start', 'reference linear cache', 'signed DC speed bounds',
                       'input immutability', 'JSON diagnostics', 'episode reset']}


def _solver_self_test():
    """Optional SciPy-only bounded solve and DARE/LQR equivalence checks."""
    from scipy.linalg import solve_discrete_are
    n, m, N = STATE_DIM, CONTROL_DIM, 20
    Ad = .94*np.eye(n)
    Bd = np.zeros((n, m))
    Bd[:m] = .2*np.eye(m)
    Q, R = np.eye(n), .1*np.eye(m)
    P = solve_discrete_are(Ad, Bd, Q, R)
    K = np.linalg.solve(R+Bd.T@P@Bd, Bd.T@P@Ad)
    gain = {'q': np.zeros(7), 'tau': np.zeros(m), 'Ad': Ad, 'Bd': Bd,
            'Q': Q, 'R': R, 'P': P, 'K': K}
    controller = LinearMPC(gain, N)
    near = np.full(n, .01)
    torque = controller.command(near, np.zeros(n))
    assert np.allclose(torque, -K@near, atol=1e-12), 'DARE terminal MPC must equal unconstrained LQR'
    far = np.full(n, 100.)
    torque = controller.command(far, np.zeros(n))
    assert np.all(controller.predicted_tau <= EFFORT6+1e-9)
    assert np.all(controller.predicted_tau >= -EFFORT6-1e-9)
    assert controller.last_log['cost'] <= controller.last_log['initial_feasible_plan_cost']+1e-8
    assert controller.last_log['converged'], controller.last_log
    bounded = dict(controller.last_log)
    controller.command(far, np.zeros(n), velocity6=NO_LOAD6*3)
    assert np.allclose(controller.predicted_tau, -EFFORT6)
    return {'passed': True, 'physics_steps': 0,
            'checks': ['DARE terminal equals LQR', 'bounded analytic-gradient SciPy solve',
                       'feasible plan cost does not increase', 'overspeed braking bounds'],
            'bounded_solver_log': bounded}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pure mathematics MPC self-checks; no MuJoCo')
    parser.add_argument('--solver-self-test', action='store_true')
    options = parser.parse_args()
    result = {'math': _math_self_test()}
    if options.solver_self_test:
        result['scipy_solver'] = _solver_self_test()
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))

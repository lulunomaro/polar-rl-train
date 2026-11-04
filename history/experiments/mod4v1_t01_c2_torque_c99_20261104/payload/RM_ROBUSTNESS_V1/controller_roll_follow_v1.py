"""T01 candidate 1: differential leg references from sensor-only relative wheel height.

The bilateral ground prior is a CONTROLLER assumption, not contact detection.
Wheel-center height difference is not terrain height. No MuJoCo/plant input.
Common nominal joint reference, sagittal K, shaper, yaw loop and effort stay intact.
This candidate is not wired into the UI or the unqualified moving-jump action.
"""
import math
import numpy as np
from FLAT_STABILITY_FIX_V1.controller_v2 import GroundController as Base

VARIANT = 'coord_soft_roll_follow_v1'


class GroundController(Base):
    def __init__(self, gain, config=None, variant='coord_soft', geometry=None):
        if geometry is None:
            raise ValueError('Explicit public linkage geometry is required')
        cfg = dict(config or {})
        # Replace rather than double-stack the old direct-joint roll term.
        cfg.update(roll_kp=0., roll_kd=0.)
        super().__init__(gain, cfg, variant='coord_soft')
        self.mode = VARIANT
        self.geom = geometry
        self.q0 = np.array([self.ref[3], self.ref[3]+self.ref[4]], float)
        self.height_difference = 0.
        self.solution = np.zeros(2)
        self.delta = np.zeros(2)
        self.follow_diag = dict(calls=0, inverse_holds=0, height_clip_calls=0,
            max_abs_raw_wheel_center_height_difference_m=0., max_abs_reference_delta_rad=0.,
            max_inverse_residual_m=0., bilateral_ground_prior=True,
            contact_identity_confirmed=False, truth_inputs=False)

    def _fk(self, q, side):
        _, r, J, _ = self.geom.wheel_kinematics(float(q[0]), float(q[1]),
            0., 0., 0., np.zeros(3), side)
        return np.asarray(r), np.asarray(J)

    def _admissible(self, delta):
        for q in (self.q0+delta, self.q0-delta):
            if np.max(np.abs(q)) > 2.9 or not -1.05 <= q[1]-q[0] <= .82:
                return False
        try:
            self._fk(self.q0+delta, 'left')
            self._fk(self.q0-delta, 'right')
        except ValueError:
            return False
        return True

    def _solve_difference(self, target_z):
        # Opposite joint deltas keep the common absolute hip/crank reference exact.
        # Two equations: reference wheel X difference=0, Z difference=target_z.
        d = self.solution.copy()
        target = np.array([0., target_z])
        residual = math.inf
        for _ in range(4):
            left, JL = self._fk(self.q0+d, 'left')
            right, JR = self._fk(self.q0-d, 'right')
            error = target-(left-right)[[0, 2]]
            residual = float(np.linalg.norm(error))
            if residual < 1e-7:
                break
            A = (JL+JR)[[0, 2], :]
            if abs(float(np.linalg.det(A))) < 1e-5:
                return self.solution.copy(), residual, False
            step = np.linalg.solve(A, error)
            step *= min(1., .08/max(float(np.max(np.abs(step))), 1e-12))
            accepted = False
            for _ in range(5):
                trial = d+step
                if self._admissible(trial):
                    d = trial; accepted = True; break
                step *= .5
            if not accepted:
                return self.solution.copy(), residual, False
        left, _ = self._fk(self.q0+d, 'left')
        right, _ = self._fk(self.q0-d, 'right')
        residual = float(np.linalg.norm(target-(left-right)[[0, 2]]))
        return d, residual, residual <= .002

    def command(self, e, forward, yaw_rate):
        x = np.asarray(e.state14, float)
        roll, pitch = float(e.roll), float(x[2])
        if not np.isfinite(np.r_[x, roll, e.omega_body]).all():
            raise ValueError('ROLL_FOLLOW_NONFINITE')
        if abs(pitch) > .35 or abs(roll) > .65:
            raise ValueError('ROLL_FOLLOW_T01_GROUND_DOMAIN')
        qL = np.array([x[3], x[3]+x[4]])
        qR = np.array([x[5], x[5]+x[6]])
        left, _ = self._fk(qL, 'left')
        right, _ = self._fk(qR, 'right')
        nB = np.array([-math.sin(pitch), math.sin(roll)*math.cos(pitch),
                       math.cos(roll)*math.cos(pitch)])
        raw = float(nB@(left-right))
        desired = float(np.clip(raw, -.18, .18))
        # Filter and slew the inferred differential height, not the estimator.
        increment = self.dt/(.08+self.dt)*(desired-self.height_difference)
        self.height_difference += float(np.clip(increment, -.18*self.dt, .18*self.dt))
        solution, residual, valid = self._solve_difference(self.height_difference/math.cos(pitch))
        if valid:
            self.solution = solution
        else:
            self.follow_diag['inverse_holds'] += 1
        self.delta += np.clip(self.solution-self.delta, -.8*self.dt, .8*self.dt)
        left_ref, right_ref = self.q0+self.delta, self.q0-self.delta
        self.ref[3], self.ref[4] = left_ref[0], left_ref[1]-left_ref[0]
        self.ref[5], self.ref[6] = right_ref[0], right_ref[1]-right_ref[0]
        tau = super().command(e, forward, yaw_rate)
        d = self.follow_diag
        d['calls'] += 1
        d['height_clip_calls'] += int(abs(raw) > .18)
        d['max_abs_raw_wheel_center_height_difference_m'] = max(d['max_abs_raw_wheel_center_height_difference_m'], abs(raw))
        d['max_abs_reference_delta_rad'] = max(d['max_abs_reference_delta_rad'], float(np.max(np.abs(self.delta))))
        d['max_inverse_residual_m'] = max(d['max_inverse_residual_m'], residual)
        d['last_reference_delta_rad2'] = self.delta.tolist()
        d['last_inferred_height_difference_m'] = self.height_difference
        return tau

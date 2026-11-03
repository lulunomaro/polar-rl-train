"""Synthetic scalar algebra only. No source/model/SDK imports or file I/O.
Candidate: DISABLED learner-only dense signed-upright reward, not PBRS.
PBRS helpers below are theorem counterexamples, never a second candidate.
"""
import io
import json
import math
import sys
import unittest

DT = 0.02
GAMMA = 0.99
K_SYNTHETIC = 0.2  # arbitrary toy value, not a selected experimental setting


def axis_quat(axis, angle):
    v = [0.0, 0.0, 0.0]
    v[axis] = math.sin(angle / 2)
    return (math.cos(angle / 2), *v)  # vendor wxyz


def gravity_wxyz(q):
    norm = math.sqrt(sum(v * v for v in q))
    if norm == 0 or not math.isfinite(norm):
        raise ValueError('finite nonzero synthetic quaternion required')
    w, x, y, z = (v / norm for v in q)
    # Exactly negative row 2 of vendor geometry.quat_to_mat.
    return (-2 * (x*z - w*y), -2 * (y*z + w*x), -(1 - 2*(x*x + y*y)))


def gravity_sdk_xyzw(q):
    x, y, z, w = q
    return gravity_wxyz((w, x, y, z))


def upright(q):
    return max(0.0, min(1.0, (1 - gravity_wxyz(q)[2]) / 2))


def request(recipe, age_before):
    return recipe != 12 and age_before < 300


def shaping(q_physical_next, recipe, age_before, kappa=None, enabled=False):
    if not enabled:
        return 0.0
    if kappa is None or not math.isfinite(kappa) or kappa <= 0:
        raise ValueError('NEW kappa must be selected and positive before enable')
    if not request(recipe, age_before):
        return 0.0
    return kappa * DT * upright(q_physical_next)


def old_orientation_cost(q, command_vx=0.0):
    gx, gy, _ = gravity_wxyz(q)
    gain = 2 * math.exp(-command_vx**2) + 2
    return 4*gx*gx + gain*gain*(gx*gx + gy*gy)


def old_peak_delta(peak, q, active=True):
    u = upright(q)
    return max(u - peak, 0.0) if active else 0.0


def discounted(rewards, gamma=GAMMA, continuations=None, value=0.0):
    survival, total = 1.0, 0.0
    for t, reward in enumerate(rewards):
        total += gamma**t * survival * reward
        if continuations is not None:
            survival *= continuations[t]
    return total + gamma**len(rewards) * survival * value


def pbrs_reference(phi0, phi1, gamma=GAMMA, continuation=1.0):
    return gamma * continuation * phi1 - phi0


class FormulaContracts(unittest.TestCase):
    def test_01_identity_is_upright_and_pitch_pi_is_inverted(self):
        self.assertEqual(gravity_wxyz((1, 0, 0, 0)), (0, 0, -1))
        self.assertEqual(upright((1, 0, 0, 0)), 1.0)
        self.assertAlmostEqual(gravity_wxyz(axis_quat(1, math.pi))[2], 1.0)
        self.assertAlmostEqual(upright(axis_quat(1, math.pi)), 0.0)

    def test_02_actual_bridge_reorder_xyzw_to_wxyz(self):
        q = axis_quat(0, 0.71)
        sdk = (q[1], q[2], q[3], q[0])
        self.assertEqual(gravity_sdk_xyzw(sdk), gravity_wxyz(q))
        self.assertNotEqual(gravity_wxyz(sdk), gravity_wxyz(q))

    def test_03_quaternion_sign_scale_and_yaw_invariance(self):
        q = axis_quat(1, 0.73)
        self.assertEqual(gravity_wxyz(q), gravity_wxyz(tuple(-x for x in q)))
        for a, b in zip(gravity_wxyz(q), gravity_wxyz(tuple(3*x for x in q))):
            self.assertAlmostEqual(a, b, places=14)  # normalization roundoff, not exact bits
        for yaw in (-2, 0, 1, math.pi):
            self.assertEqual(upright(axis_quat(2, yaw)), 1.0)

    def test_04_pitch_and_roll_match_analytic_gravity(self):
        a = 0.38
        self.assertAlmostEqual(gravity_wxyz(axis_quat(1, a))[0], math.sin(a))
        self.assertAlmostEqual(gravity_wxyz(axis_quat(0, a))[1], -math.sin(a))
        for axis in (0, 1):
            self.assertAlmostEqual(upright(axis_quat(axis, a)), (1+math.cos(a))/2)

    def test_05_old_single_component_cannot_distinguish_up_down(self):
        for axis in (0, 1):
            up, down = axis_quat(axis, 0), axis_quat(axis, math.pi)
            self.assertAlmostEqual(old_orientation_cost(up), 0.0)
            self.assertAlmostEqual(old_orientation_cost(down), 0.0)
            self.assertNotEqual(upright(up), upright(down))
        # A different original reward component can be positive at both.
        self.assertGreater(1.7 * DT - old_orientation_cost(down) * DT, 0)

    def test_06_old_cost_is_twenty_pitch_sixteen_roll(self):
        a = 0.21
        self.assertAlmostEqual(old_orientation_cost(axis_quat(1, a)), 20*math.sin(a)**2)
        self.assertAlmostEqual(old_orientation_cost(axis_quat(0, a)), 16*math.sin(a)**2)

    def test_07_original_peak_already_has_signed_information(self):
        up, down = axis_quat(1, 0), axis_quat(1, math.pi)
        self.assertAlmostEqual(old_peak_delta(0, up), 1.0)
        self.assertAlmostEqual(old_peak_delta(0, down), 0.0)
        self.assertAlmostEqual(old_peak_delta(1, up), 0.0)
        self.assertGreater(shaping(up, 0, 0, K_SYNTHETIC, True), 0)

    def test_08_exact_inversion_still_has_zero_angle_first_derivative(self):
        for axis in (0, 1):
            eps = 1e-5
            central = (upright(axis_quat(axis, math.pi+eps)) -
                       upright(axis_quat(axis, math.pi-eps))) / (2*eps)
            self.assertAlmostEqual(central, 0.0, places=9)
            self.assertAlmostEqual(upright(axis_quat(axis, math.pi-eps))/eps**2, 0.25, places=5)

    def test_09_small_angle_barrier_witness_not_training_evidence(self):
        eps = 1e-4
        for axis, curvature in ((1, 20), (0, 16)):
            q = axis_quat(axis, math.pi-eps)
            threshold = DT * old_orientation_cost(q) / (DT * upright(q))
            self.assertAlmostEqual(threshold, 4*curvature, places=4)
            self.assertLess(DT/3*upright(q) - DT*old_orientation_cost(q), 0)

    def test_10_default_disabled_even_without_weight(self):
        self.assertEqual(shaping((1, 0, 0, 0), 0, 0), 0.0)
        with self.assertRaisesRegex(ValueError, 'NEW kappa'):
            shaping((1, 0, 0, 0), 0, 0, enabled=True)

    def test_11_normal_six_are_exactly_zero(self):
        six_quats = [axis_quat(i % 3, 0.31*i) for i in range(6)]
        values = [shaping(q, 12, i*2, K_SYNTHETIC, True) for i, q in enumerate(six_quats)]
        self.assertEqual(values, [0.0]*6)
        self.assertEqual(sum(v != 0 for v in values), 0)

    def test_12_latched_request_298_included_300_excluded(self):
        q = (1, 0, 0, 0)
        self.assertTrue(request(0, 298))
        self.assertFalse(request(0, 300))
        self.assertGreater(shaping(q, 0, 298, K_SYNTHETIC, True), 0)
        self.assertEqual(shaping(q, 0, 300, K_SYNTHETIC, True), 0)
        ages = range(0, 302, 2)
        self.assertEqual(sum(request(0, a) for a in ages), 150)

    def test_13_original_three_seconds_and_stable_half_second(self):
        self.assertAlmostEqual(150*DT, 3.0)
        stable = 0
        for _ in range(24):
            stable += 2
        self.assertLess(stable, 50)
        stable += 2
        self.assertGreaterEqual(stable, 50)
        self.assertAlmostEqual(25*DT, 0.5)
        stable = 0  # a failed original predicate resets the streak
        self.assertLess(stable, 50)

    def test_14_terminal_reward_uses_physical_state_not_reset_state(self):
        physical_down, reset_up = axis_quat(1, math.pi), (1, 0, 0, 0)
        for term, trunc in ((True, False), (False, True)):
            done = term or trunc
            self.assertTrue(done)
            correct = shaping(physical_down, 0, 0, K_SYNTHETIC, True)
            wrong = shaping(reset_up, 0, 0, K_SYNTHETIC, True)
            self.assertAlmostEqual(correct, 0)
            self.assertGreater(wrong, correct)

    def test_15_terminal_and_timeout_keep_current_reward_then_stop_future(self):
        for term, trunc in ((True, False), (False, True), (True, True)):
            done = term or trunc
            reward_now = shaping((1, 0, 0, 0), 0, 2, K_SYNTHETIC, True)
            self.assertGreater(reward_now, 0)
            self.assertEqual(discounted([reward_now, 99], continuations=[1-float(done), 1], value=7), reward_now)

    def test_16_command_t_copied_not_returned_reset_command(self):
        command_t, after = [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]
        latched = tuple(command_t)
        command_t[:] = after
        q = axis_quat(1, 0.5)
        self.assertEqual(latched, (0.0, 0.0, 0.0))
        self.assertNotEqual(old_orientation_cost(q, latched[0]), old_orientation_cost(q, after[0]))

    def test_17_dt_applied_once_and_event_delta_not_rescaled(self):
        new = shaping((1, 0, 0, 0), 0, 0, K_SYNTHETIC, True)
        self.assertEqual(new, K_SYNTHETIC*DT)
        event_delta = 1.0
        self.assertEqual((event_delta/DT)*DT, 1.0)
        self.assertNotEqual(new, K_SYNTHETIC*DT*DT)

    def test_18_reward_split_and_actor_data_are_unchanged(self):
        original = -0.73
        actor_original = (0.4, 0.1, -0.3)  # synthetic observation, no cleanstate field
        actor_before = tuple(actor_original)
        extra = shaping((1, 0, 0, 0), 0, 0, K_SYNTHETIC, True)
        row = dict(r_original=original, r_shaping=extra, r_learning=original+extra)
        self.assertEqual(row['r_original'], original)
        self.assertAlmostEqual(row['r_learning']-row['r_original'], extra)
        self.assertEqual(actor_original, actor_before)

    def test_19_calibration_envelope_and_discounted_bound(self):
        kappa = 1/3  # proposed NEW upper envelope, not an enabled setting
        seq = [shaping((1, 0, 0, 0), 0, 2*t, kappa, True) for t in range(150)]
        self.assertAlmostEqual(sum(seq), 1.0)
        bound = DT*kappa*(1-GAMMA**150)/(1-GAMMA)
        self.assertAlmostEqual(discounted(seq), bound)
        self.assertLess(discounted(seq), 1.0)

    def test_20_h16_is_not_no_future_reward(self):
        self.assertAlmostEqual(16*DT, 0.32)
        with_bootstrap = discounted([0.0]*16, value=2.0)
        self.assertAlmostEqual(with_bootstrap, GAMMA**16*2.0)
        self.assertGreater(with_bootstrap, 0)

    def test_21_dense_candidate_changes_objective_not_pbrs(self):
        # Same start/end potential, different intermediate upright occupancy.
        path_a, path_b = [0, 1, 0], [0, 0, 0]
        self.assertGreater(discounted([DT*K_SYNTHETIC*u for u in path_a[1:]]),
                           discounted([DT*K_SYNTHETIC*u for u in path_b[1:]]))

    def test_22_pbrs_reference_exact_horizon_with_value_shift(self):
        phi, rewards, value = [0.2, 0.5, 0.7], [0.1, -0.3], 1.4
        f = [pbrs_reference(phi[t], phi[t+1]) for t in range(2)]
        base = discounted(rewards, value=value)
        shaped = discounted([r+x for r, x in zip(rewards, f)], value=value-phi[-1])
        self.assertAlmostEqual(shaped, base-phi[0])

    def test_23_pbrs_wrong_gamma_leaves_path_dependent_residual(self):
        phi = [0.2, 0.5, 0.7]
        wrong = [phi[t+1]-phi[t] for t in range(2)]
        residual = discounted(wrong, value=-phi[-1]) + phi[0]
        self.assertGreater(abs(residual), 1e-6)
        self.assertNotEqual(GAMMA, 0.9801)  # historical PPO gamma != SM path

    def test_24_pbrs_terminal_zero_continuation_required(self):
        phi0, phi1 = 0.2, 0.9
        correct = pbrs_reference(phi0, phi1, continuation=0)
        wrong = pbrs_reference(phi0, phi1, continuation=1)
        self.assertEqual(correct, -phi0)
        self.assertAlmostEqual(wrong-correct, GAMMA*phi1)

    def test_25_timeout_bootstrap_semantics_must_match(self):
        phi0, phi1, next_value = 0.2, 0.8, 1.3
        correct_if_trunc_is_terminal = pbrs_reference(phi0, phi1, continuation=0)
        mixed = pbrs_reference(phi0, phi1, continuation=1)  # but no timeout bootstrap
        self.assertNotEqual(correct_if_trunc_is_terminal, mixed)
        continuing = mixed + GAMMA*(next_value-phi1)
        self.assertAlmostEqual(continuing, GAMMA*next_value-phi0)

    def test_26_pbrs_missing_horizon_value_transform_fails(self):
        phi0, phi1 = 0.2, 0.8
        f = pbrs_reference(phi0, phi1)
        without_shift = f + GAMMA*1.3
        expected = GAMMA*1.3-phi0
        self.assertAlmostEqual(without_shift-expected, GAMMA*phi1)

    def test_27_pbrs_request_mask_is_part_of_state_not_outer_gate(self):
        u0, u1, m0, m1 = 0.6, 0.8, 1, 0
        correct = pbrs_reference(m0*u0, m1*u1)
        wrong = m0*pbrs_reference(u0, u1)
        self.assertEqual(correct, -0.6)
        self.assertNotEqual(correct, wrong)
        self.assertAlmostEqual(wrong-correct, GAMMA*u1)

    def test_28_soft_continuation_algebra_needs_same_factor_everywhere(self):
        phi, cont, reward, value = [0.2, 0.5, 0.7], [0.3, 0.6], [0.1, -0.3], 1.4
        f = [pbrs_reference(phi[t], phi[t+1], continuation=cont[t]) for t in range(2)]
        base = discounted(reward, continuations=cont, value=value)
        shaped = discounted([r+x for r, x in zip(reward, f)], continuations=cont, value=value-phi[-1])
        self.assertAlmostEqual(shaped, base-phi[0])
        # Algebra with a consistent soft factor is not proof the learned heads satisfy it.


if __name__ == '__main__':
    names = unittest.defaultTestLoader.getTestCaseNames(FormulaContracts)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(FormulaContracts))
    print(json.dumps(dict(
        schema='E3_SIGNED_UPRIGHT_SYNTHETIC_STDLIB_V1',
        status='PASS' if result.wasSuccessful() else 'FAIL',
        enabled=False, experimental_kappa_NEW=None, synthetic_only=True,
        interpreter=sys.executable, isolation_flags=dict(isolated=sys.flags.isolated,
            no_site=sys.flags.no_site, dont_write_bytecode=sys.dont_write_bytecode),
        torch_imported='torch' in sys.modules,
        real_source_imports=0, model_reads=0, SDK_calls=0, training_starts=0,
        skill_proven=False, causal_failure_explanation_proven=False,
        tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        tests=names,
        numeric_witnesses=dict(
            up_gz=-1, inverted_gz=1,
            synthetic_kappa_only=K_SYNTHETIC,
            new_kappa_envelope_max=1/3,
            request_controls=150, original_stable_controls=25,
            old_pitch_roll_cost_curvature=[20, 16],
            isolated_small_angle_balance_kappa_reward_per_s=[80, 64],
            discounted_request_time_factor_s=DT*(1-GAMMA**150)/(1-GAMMA),
            h16_seconds=16*DT, h16_gamma=GAMMA**16),
        test_runner='OK' if result.wasSuccessful() else stream.getvalue()), indent=2, allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)

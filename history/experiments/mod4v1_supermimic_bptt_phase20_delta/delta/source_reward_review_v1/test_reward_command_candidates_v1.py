"""Pure stdlib CPU formula / source-join / falsification tests. No audited imports.
A passing test says nothing about real skill success. Run Python -S -B.
"""
from __future__ import annotations
import ast
import io
import json
import math
from pathlib import Path
import sys
import unittest
import reward_command_candidates_v1 as f

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
PARAMS = json.loads((OUT / 'ROLE_EFFECTIVE_REWARD_PARAMS_SOURCE_V1.json').read_text(encoding='utf-8'))


class ExponentialAndCompositeTests(unittest.TestCase):
    def test_01_legacy_std_is_denominator_not_squared(self):
        self.assertAlmostEqual(f.exp_denominator(0.5, 0.25), math.exp(-1))
        self.assertNotAlmostEqual(f.exp_denominator(0.5, 0.25), math.exp(-4))

    def test_02_e_minus_one_radius_is_sqrt_denominator(self):
        for d in [0.25, 0.01, 0.001, 0.1]:
            self.assertAlmostEqual(f.exp_denominator(math.sqrt(d), d), math.exp(-1))

    def test_03_derivative_matches_finite_difference(self):
        for d, e in [(0.25, 0.3), (0.01, 0.05), (0.001, 0.02)]:
            h = 1e-7
            fd = (f.exp_denominator(e+h, d)-f.exp_denominator(e-h, d))/(2*h)
            self.assertAlmostEqual(fd, f.exp_error_slope(e, d), places=7)

    def test_04_tight_error_one_has_tiny_slope(self):
        self.assertLess(abs(f.exp_error_slope(1.0, 0.01)), 1e-40)

    def test_05_yaw_four_exp_tail_and_square_are_different(self):
        self.assertLess(f.exp_denominator(4, 0.25), 2e-28)
        h = 1e-6
        fd = (f.scut_yaw_rate(4+h)-f.scut_yaw_rate(4-h))/(2*h)
        self.assertAlmostEqual(fd, -0.5, places=7)

    def test_06_float32_min_subnormal_comparison_is_not_fp32_execution(self):
        fp32_min_subnormal = 2.0**-149
        self.assertLess(f.exp_denominator(1.5, 0.01), fp32_min_subnormal)
        self.assertLess(f.exp_denominator(4*math.pi, 0.25), fp32_min_subnormal)

    def test_07_gap_is_strict_on_squared_error_not_speed_half(self):
        self.assertEqual(float(0.5**2 > 0.5), 0.0)
        self.assertEqual(float(0.7070**2 > 0.5), 0.0)
        self.assertEqual(float(0.7072**2 > 0.5), 1.0)

    def test_08_forward_error_has_pitch_projection(self):
        self.assertAlmostEqual(f.scut_forward_error(0.3, 0.3, 0), 0)
        self.assertAlmostEqual(f.scut_forward_error(0.3, 0.3, 1), 0.3)

    def test_09_linear_tracking_has_no_lateral_input(self):
        self.assertEqual(f.scut_forward_error(0.3, 0.3, 0), 0)
        self.assertNotIn('vy', f.scut_forward_error.__annotations__)

    def test_10_stationary_small_command_has_positive_rate(self):
        self.assertGreater(f.scut_linear_rate(0.3), 0.69)
        self.assertLess(f.scut_linear_rate(0.3), f.scut_linear_rate(0))

    def test_11_height_excursion_can_outweigh_tracking_advantage(self):
        advantage = f.scut_linear_rate(0)-f.scut_linear_rate(0.3)
        height_loss = f.scut_height_rate(0)-f.scut_height_rate(0.1)
        self.assertAlmostEqual(advantage, 0.507923991968152, places=13)
        self.assertGreater(height_loss, advantage)

    def test_12_two_centimeter_height_cost_is_nonzero(self):
        self.assertGreater(f.scut_height_rate(0)-f.scut_height_rate(0.02), 0.12)

    def test_13_positive_height_contact_reward_uses_distinct_denominators(self):
        self.assertAlmostEqual(f.scut_height_rate(0), 1.3)
        self.assertAlmostEqual(f.scut_height_rate(0, False), 1.0)

    def test_14_orientation_name_velocity_is_gravity_not_rate(self):
        self.assertEqual(f.scut_orientation_cost(0, 0, 0), 0)
        self.assertEqual(f.scut_orientation_cost(1, 0, 0), 20)
        self.assertGreater(f.scut_orientation_cost(1, 0, 0), f.scut_orientation_cost(1, 0, 1.5))

    def test_15_second_difference_penalty_can_cost_twice_on_one_step(self):
        actions = [0, 0, 1, 1]
        cost = sum((actions[i]-2*actions[i-1]+actions[i-2])**2 for i in [2, 3])
        self.assertEqual(cost, 2)
        self.assertAlmostEqual(-0.05*6*cost, -0.6)

    def test_16_rolling_loaded_tail_is_clipped(self):
        self.assertEqual(f.rolling_scalar_cost(0.4, 10), f.rolling_scalar_cost(2, 10))

    def test_17_rolling_unloading_counterexample(self):
        self.assertEqual(f.rolling_scalar_cost(1, 0), 0.25)
        self.assertEqual(f.rolling_scalar_cost(1, 10), 4)

    def test_18_force_norm_contact_is_not_positive_average_fz(self):
        historical_force = (3.0, 0.0, -2.0)
        norm = math.sqrt(sum(x*x for x in historical_force))
        self.assertGreater(norm, 1)
        self.assertLessEqual(max(0, historical_force[2]), 1)

    def test_19_linear_height_gate_has_zero_tail_but_mode_off_bypasses_it(self):
        self.assertEqual(f.linear_band_gate(0.15, 0.05, 0.10), 0)
        self.assertEqual(f.linear_band_gate(0.025, 0.05, 0.10), 1)
        self.assertAlmostEqual(f.linear_band_gate(0.075, 0.05, 0.10), 0.5)


class CommandAndAcceptanceTests(unittest.TestCase):
    def test_20_world_body_round_trip(self):
        for yaw in [0, math.pi/2, -1.1, math.pi]:
            b = f.world_to_body_xy(0.4, -0.2, yaw)
            w = f.body_to_world_xy(*b, yaw)
            self.assertAlmostEqual(w[0], 0.4)
            self.assertAlmostEqual(w[1], -0.2)

    def test_21_nonholonomic_mapping_is_not_world_constant_at_each_instant(self):
        vx = f.original_nonholonomic_body_vx(0.5, math.pi/2, 0)
        world = f.body_to_world_xy(vx, 0, math.pi/2)
        self.assertAlmostEqual(world[0], 0)
        self.assertNotAlmostEqual(world[0], 0.5)

    def test_22_nonholonomic_full_cycle_mean_has_original_speed(self):
        n = 4000
        xy = [f.body_to_world_xy(f.original_nonholonomic_body_vx(0.5, t*2*math.pi/n, 0),
                                 0, t*2*math.pi/n) for t in range(n)]
        self.assertAlmostEqual(sum(p[0] for p in xy)/n, 0.5, places=12)
        self.assertAlmostEqual(sum(p[1] for p in xy)/n, 0, places=12)

    def test_23_h16_fixed_command_error_is_not_small_for_e2(self):
        span = 16*0.02*4
        self.assertAlmostEqual(math.degrees(span), 73.33859777674537)
        self.assertGreater(1-math.cos(span), 0.71)
        self.assertGreater(2*math.sin(span/2), 1.19)

    def test_24_w35_negative_body_command_uses_pi(self):
        a = f.signed_body_axis(0, -0.3)
        along, cross = f.project_xy(-0.6, 0, a, 2)
        self.assertAlmostEqual(along, 0.3)
        self.assertAlmostEqual(cross, 0)
        self.assertAlmostEqual(f.project_xy(-0.6, 0, 0, 2)[0], -0.3)

    def test_25_projected_along_is_speed_not_total_displacement(self):
        self.assertAlmostEqual(f.project_xy(1, 0, 0, 2)[0], 0.5)

    def test_26_zero_duration_does_not_make_a_cycle(self):
        with self.assertRaises(ValueError):
            f.project_xy(1, 0, 0, 0)

    def test_27_e2_complete_terminal_cycle_fails(self):
        self.assertTrue(f.e2_cycle_accept(0.5, 0, 0, 1, True, False, False))
        self.assertFalse(f.e2_cycle_accept(0.5, 0, 0, 1, True, True, False))
        self.assertFalse(f.e2_cycle_accept(0.5, 0, 0, 1, True, False, True))

    def test_28_e2_along_cross_yaw_and_completeness_each_matter(self):
        for values in [(0.56, 0, 0, 1, True), (0.5, 0.051, 0, 1, True),
                       (0.5, 0, 0.201, 1, True), (0.5, 0, 0, 1, False)]:
            self.assertFalse(f.e2_cycle_accept(*values, False, False))

    def test_29_ordered_endpoint_keeps_prefix_if_failure_is_later(self):
        self.assertTrue(f.endpoint_ordered(3, 7, 8))
        self.assertFalse(f.endpoint_ordered(3, 7, 6))
        self.assertFalse(f.endpoint_ordered(7, 3, None))

    def test_30_progress_is_not_endpoint_contact_acceptance(self):
        large_progress, both_wheels_positive_avg_Fz = True, False
        self.assertFalse(large_progress and both_wheels_positive_avg_Fz)


class RecoveryTests(unittest.TestCase):
    def test_31_twenty_four_good_steps_are_not_yet_credit(self):
        r = f.RecoveryPhaseFixture(0)
        for _ in range(24):
            r.step(-1, 0, 0)
        self.assertFalse(r.credited)
        r.step(-1, 0, 0)
        self.assertTrue(r.credited)

    def test_32_event_delta_zero_later_but_credit_stays(self):
        r = f.RecoveryPhaseFixture(1)
        for _ in range(25):
            event = r.step(-1, 0, 0)
        self.assertEqual(event, 1)
        self.assertEqual(r.step(-1, 0, 0), 0)
        self.assertTrue(r.credited)

    def test_33_upright_peak_with_excess_speed_is_not_credit(self):
        r = f.RecoveryPhaseFixture(1)
        self.assertEqual(r.step(-1, 0.04, 0), 1)
        for _ in range(30):
            r.step(-1, 0.04, 0)
        self.assertFalse(r.credited)

    def test_34_normal_recipe12_never_rescue_credit(self):
        r = f.RecoveryPhaseFixture(12)
        for _ in range(100):
            self.assertEqual(r.step(-1, 0, 0), 0)
        self.assertFalse(r.credited)

    def test_35_request_ends_after_150_controls(self):
        r = f.RecoveryPhaseFixture(2)
        for _ in range(150):
            r.step(1, 0, 0)
        self.assertEqual(r.age, 300)
        for _ in range(30):
            r.step(-1, 0, 0)
        self.assertFalse(r.request)
        self.assertFalse(r.credited)

    def test_36_good_streak_is_consecutive(self):
        r = f.RecoveryPhaseFixture(3)
        for _ in range(24):
            r.step(-1, 0, 0)
        r.step(-1, 0.03, 0)
        r.step(-1, 0, 0)
        self.assertFalse(r.credited)
        self.assertEqual(r.stable, 2)

    def test_37_upside_down_gravity_xy_zero_is_orientation_local_counterexample(self):
        # Algebraic fixture only, no claim this is an attainable dynamic equilibrium.
        self.assertEqual(f.scut_orientation_cost(0, 0, 0), 0)
        r = f.RecoveryPhaseFixture(0)
        self.assertEqual(r.step(1, 0, 0), 0)
        self.assertFalse(r.credited)


class CandidateAndPotentialTests(unittest.TestCase):
    def test_38_rational_matches_center_curvature_not_far_tail(self):
        e, h = 0, 1e-4
        rational_curv = (f.bounded_tracking(h, 0.5)-2*f.bounded_tracking(e, 0.5)
                         + f.bounded_tracking(-h, 0.5))/h**2
        self.assertAlmostEqual(rational_curv, -8, places=5)
        self.assertGreater(f.bounded_tracking(1.5, 0.5), f.exp_denominator(1.5, 0.25))

    def test_39_rational_can_raise_reward_for_bad_tracking(self):
        self.assertAlmostEqual(f.bounded_tracking(4, 0.5), 1/65)
        self.assertGreater(f.bounded_tracking(4, 0.5), f.exp_denominator(4, 0.25))

    def test_40_huber_linear_tail_has_nonzero_slope_but_is_unbounded(self):
        self.assertAlmostEqual(f.huber_cost_slope(4, 0.5), 2)
        self.assertGreater(f.huber_tracking_cost(10, 0.5), f.huber_tracking_cost(4, 0.5))

    def test_41_clipped_huber_has_zero_slope_counterexample(self):
        def clipped(e):
            return min(3, f.huber_tracking_cost(e, 0.5))
        self.assertEqual(clipped(4), clipped(4.01))

    def test_42_soft_floor_only_declared_phase(self):
        self.assertEqual(f.phase_gate(0, True), 0.25)
        self.assertEqual(f.phase_gate(0, False), 0)
        self.assertEqual(f.phase_gate(0.8, True), 0.8)
        self.assertEqual(f.declared_phase_cost_multiplier(True), 0.5)
        self.assertEqual(f.declared_phase_cost_multiplier(False), 1.0)

    def test_43_finite_horizon_bootstrap_corrected_potential_telescopes(self):
        r, c, phis, g, v = [1, 2, 3], [1, 1, 1], [0.3, 0.8, -0.2, 0.7], 0.99, 5
        self.assertAlmostEqual(f.potential_augmented_return(r, c, phis, g, v),
                               f.discounted_return(r, c, g, v)-phis[0])

    def test_44_terminal_reward_is_kept_and_no_terminal_bootstrap(self):
        r, c, phis, g = [1, 2], [1, 0], [0.3, 0.8, 999], 0.99
        self.assertAlmostEqual(f.potential_augmented_return(r, c, phis, g, 999),
                               1+g*2-phis[0])

    def test_45_same_soft_continuation_telescopes_only_algebraically(self):
        r, c, phis, g = [1, 2], [0.9, 0.4], [0.3, 0.8, -0.4], 0.99
        self.assertAlmostEqual(f.potential_augmented_return(r, c, phis, g, 5),
                               f.discounted_return(r, c, g, 5)-phis[0])

    def test_46_gamma_one_delta_shaping_is_not_gamma099_invariant(self):
        g, phis = 0.99, [0, 1, 0]
        naive = [phis[i+1]-phis[i] for i in range(2)]
        proper = [f.potential_transition(phis[i], phis[i+1], g) for i in range(2)]
        self.assertNotAlmostEqual(f.discounted_return(naive, [1, 1], g), 0)
        self.assertAlmostEqual(f.discounted_return(proper, [1, 1], g), 0)

    def test_47_omitted_bootstrap_shift_leaves_terminal_potential(self):
        g, phis = 0.99, [0, 0.6]
        shaped = [f.potential_transition(*phis, g)]
        self.assertAlmostEqual(f.discounted_return(shaped, [1], g, 0), g*0.6)

    def test_48_wrong_continuation_breaks_terminal_identity(self):
        g, phis = 0.99, [0.3, 0.8]
        wrong = f.potential_transition(*phis, g, 1)
        self.assertNotAlmostEqual(wrong, -phis[0])
        self.assertEqual(f.potential_transition(*phis, g, 0), -phis[0])

    def test_49_reward_manager_dt_is_applied_once_for_increment(self):
        rate = f.potential_manager_rate(0.1, 0.3, 0.99, 1, 0.02)
        self.assertAlmostEqual(rate*0.02, f.potential_transition(0.1, 0.3, 0.99))
        self.assertNotAlmostEqual(f.potential_transition(0.1, 0.3, 0.99)*0.02,
                                  f.potential_transition(0.1, 0.3, 0.99))

    def test_50_reset_join_can_create_false_progress(self):
        physical_phi1, reset_phi1 = -0.8, 0.8
        self.assertNotEqual(f.potential_transition(0, physical_phi1, 0.99),
                            f.potential_transition(0, reset_phi1, 0.99))


class SourceJoinTests(unittest.TestCase):
    def test_51_exactly_eight_non_h1_roles(self):
        self.assertEqual(len(PARAMS['roles']), 8)
        self.assertNotIn('H1', PARAMS['roles'])

    def test_52_all_role_exp_values_come_from_metadata_join(self):
        for role in PARAMS['roles'].values():
            for key, expected in [('SCUT_LIN_SIGMA', .25), ('SCUT_LIN_TIGHT_SIGMA', .01),
                                  ('SCUT_ANG_SIGMA', .25), ('SCUT_H_TIGHT_SIGMA', .001)]:
                p = role['constants'][key]
                self.assertEqual(p['value'], expected)
                self.assertEqual(p['provenance'], 'metadata_env')

    def test_53_zero_alive_term_and_height_square_are_not_defaults(self):
        for role in PARAMS['roles'].values():
            for key in ['SCUT_ALIVE_W', 'SCUT_TERM_W', 'SCUT_H_SQ_W', 'SCUT_BASE_CONTACT_W']:
                self.assertEqual(role['constants'][key]['value'], 0)
            self.assertEqual(role['constants']['SCUT_H_SQ_W']['default'], -1)
            self.assertEqual(role['constants']['SCUT_BASE_CONTACT_W']['default'], -2)

    def test_54_height_gate_off_and_gyro_curriculum_off_in_all(self):
        for role in PARAMS['roles'].values():
            self.assertEqual(role['velocity_height_gate']['mode'], 'off')
            self.assertFalse(role['registered_gyro_curriculum'])
            self.assertEqual(role['original_height_command_range'], [.25, .25])

    def test_55_common_task_and_reward_functions_verified_separately_from_file_hashes(self):
        self.assertTrue(PARAMS['all_eight_task_hashes_equal'])
        self.assertTrue(PARAMS['all_eight_skills_hashes_equal'])
        self.assertTrue(PARAMS['all_eight_scut_reward_functions_AST_equal'])
        self.assertFalse(PARAMS['all_eight_scut_hashes_equal'])

    def test_56_direct_exp_registration_is_not_gated_wrapper(self):
        path = Path(PARAMS['roles']['E0']['entry']).parent / 'mod4_task.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        rewards = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RewardsCfg')
        assigns = {n.targets[0].id:n.value for n in rewards.body
                   if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
        for key, name in [('track_lin_vel', 'linear_exp'), ('track_lin_vel_tight', 'linear_exp'),
                          ('track_ang_vel', 'yaw_exp')]:
            func = next(k.value for k in assigns[key].keywords if k.arg == 'func')
            self.assertEqual(func.value.id, 'scut_rescue')
            self.assertEqual(func.attr, name)

    def test_57_supermimic_gamma_is_099_source_not_original_ppo_09801(self):
        path = ROOT / 'source_core_review/evidence/learner.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cfg = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SuperMimicConfig')
        gamma = next(ast.literal_eval(n.value) for n in cfg.body
                     if isinstance(n, ast.AnnAssign) and n.target.id == 'gamma')
        self.assertEqual(gamma, .99)
        self.assertNotEqual(gamma, .9801)

    def test_58_e0_and_s50_original_binary_gaps_stay_null(self):
        contract = json.loads((ROOT/'source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json')
                              .read_text(encoding='utf-8'))
        roles = contract['experts']
        self.assertIsNone(roles['E0']['original_atomic_predicate'])
        self.assertIsNone(roles['SLOPE_INDEPENDENT50']['original_atomic_predicate'])

    def test_59_manager_step_order_termination_reward_reset_command(self):
        text = (ROOT/'discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py').read_text(encoding='utf-8')
        markers = ['self.reset_buf = self.termination_manager.compute()',
                   'self.reward_buf = self.reward_manager.compute(dt=self.step_dt)',
                   'self._reset_idx(reset_env_ids)', 'self.command_manager.compute(dt=self.step_dt)']
        locations = [text.index(m) for m in markers]
        self.assertEqual(locations, sorted(locations))

    def test_60_candidates_import_only_stdlib_math(self):
        tree = ast.parse((OUT/'reward_command_candidates_v1.py').read_text(encoding='utf-8'))
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        names = [n.module if isinstance(n, ast.ImportFrom) else n.names[0].name for n in imports]
        self.assertEqual(set(names), {'__future__', 'math'})

    def test_61_manager_multiplies_weight_dt_and_skips_zero_weight(self):
        path = ROOT/'discovery/sdk_reward_scale_v1/managers/reward_manager.py'
        text = path.read_text(encoding='utf-8')
        self.assertIn('value = term_cfg.func(self._env, **term_cfg.params) * term_cfg.weight * dt', text)
        self.assertIn('if term_cfg.weight == 0.0:', text)
        self.assertIn('self._step_reward[:, term_idx] = value / dt', text)

    def test_62_action_rate_is_discrete_difference_not_physical_derivative(self):
        text = (ROOT/'discovery/sdk_reward_scale_v1/envs/mdp/rewards.py').read_text(encoding='utf-8')
        tree = ast.parse(text)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'action_rate_l2')
        segment = ast.get_source_segment(text, function)
        self.assertNotIn('/ env.step_dt', segment)
        self.assertIn('action - env.action_manager.prev_action', segment)


def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    buffer = io.StringIO()
    result = unittest.TextTestRunner(stream=buffer, verbosity=2).run(suite)
    report = dict(kind='STDLIB_CPU_FORMULA_AND_SOURCE_TESTS_NOT_SKILL_VALIDATION',
                  tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                  skipped=len(result.skipped), passed=result.wasSuccessful(),
                  SDK_imports=0, torch_imports=0, audited_task_imports=0,
                  models_read=0, raw_read=0, training_executed=False, details=buffer.getvalue())
    (OUT/'CPU_TEST_RESULTS_V1.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n',
                                              encoding='utf-8')
    print(buffer.getvalue(), end='')
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()

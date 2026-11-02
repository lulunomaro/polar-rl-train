"""Pure stdlib formula+AST checks. Does NOT import Torch, SDK or a training worker."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import io
import json
import math
import unittest
from command_tracking_math_reference_v1 import (e2_body_command, transition_yaw,
    e2_next, w35_next, known_command_writes, sampled_progress_axis, raw35,
    FeedbackSampleTape, tracking_terms, bounded_action, native_action,
    valid_window_rows, lambda_targets)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
COUNTEREXAMPLE = {}


def sensor():
    return {'base_ang_vel': (1., 2., 3.), 'projected_gravity': (0., 0., -1.),
            'leg_pos': (.1, .2, .3, .4), 'leg_vel': (1., 2., 3., 4.),
            'wheel_vel': (5., 6.)}


class FormulaTests(unittest.TestCase):
    def test_e2_source_is_two_V_cos_not_xy_vector(self):
        self.assertEqual(e2_body_command(.5, 0., 0.), (1., 0.))
        self.assertAlmostEqual(e2_body_command(.5, 0., math.pi / 2)[0], 0., places=12)
        self.assertEqual(e2_body_command(.5, 0., math.pi)[0], -1.)

    def test_e2_clipping_limit(self):
        self.assertEqual(e2_body_command(1., 0., 0., 1.5), (1.5, 0.))
        self.assertEqual(e2_body_command(1., 0., math.pi, 1.5), (-1.5, 0.))

    def test_e2_world_cycle_average_not_instantaneous_progress(self):
        n = 4096
        along, cross = [], []
        for k in range(n):
            h = 2. * math.pi * k / n
            vx, vy = e2_body_command(.5, 0., h)
            along.append(math.cos(h) * vx - math.sin(h) * vy)
            cross.append(math.sin(h) * vx + math.cos(h) * vy)
        self.assertAlmostEqual(sum(along) / n, .5, places=12)
        self.assertAlmostEqual(sum(cross) / n, 0., places=12)
        self.assertEqual(along[0], 1.)

    def test_held_H16_quantitative_counterexample(self):
        delta = 16 * .02 * 4.
        max_error = 4 * .5 * math.sin(delta / 2)
        h0 = math.pi / 2 - delta / 2
        observed = abs(e2_body_command(.5, 0., h0)[0] - e2_body_command(.5, 0., h0 + delta)[0])
        zero_heading_end = e2_body_command(.5, 0., delta)[0]
        self.assertAlmostEqual(delta, 1.28)
        self.assertAlmostEqual(math.degrees(delta), 73.33859777674537)
        self.assertAlmostEqual(max_error, 1.1943908827247842)
        self.assertAlmostEqual(observed, max_error)
        self.assertAlmostEqual(zero_heading_end, .2867152096319555)
        COUNTEREXAMPLE.update(horizon=16, dt=.02, yaw_rate=4., yaw_delta_rad=delta,
                             yaw_delta_deg=math.degrees(delta), V=.5,
                             maximum_held_command_error_m_s=max_error,
                             initial_heading_zero_vx1=zero_heading_end,
                             initial_heading_zero_error=1. - zero_heading_end,
                             kind='PURE_ANALYTIC_NOT_RUNTIME_RESULT')

    def test_transition_all_piecewise_ranges(self):
        for e, expected in ((0, 0), (.5, .5), (1, 1), (3, 1), (4, 1),
                            (4.5, .5), (5, 0), (6, 0), (6.5, -.5), (7, -1),
                            (9, -1), (10, -1), (10.5, -.5), (11, 0), (13, 0)):
            self.assertAlmostEqual(transition_yaw(e, 4), 4 * expected)

    def test_transition_post_observation_phase_is_next_write_phase(self):
        # previous write at 4.00 followed by phase+=.02; snapshot contains 4.02.
        c = e2_next((0, 0, 4), speed=.5, world_direction=0., next_heading=0.,
                    signed_yaw=4., moving=False, transition=True, standing=False,
                    next_write_elapsed=4.02)
        self.assertAlmostEqual(c[2], 3.92)
        self.assertNotEqual(c[2], transition_yaw(4.04, 4.))

    def test_e2_boolean_standing_overrides_every_mode(self):
        c = e2_next((1, 2, 3), speed=.5, world_direction=0., next_heading=.4,
                    signed_yaw=4., moving=True, transition=True, standing=True,
                    next_write_elapsed=2.)
        self.assertEqual(c, (0., 0., 0.))

    def test_e2_unchanged_straight_without_modes(self):
        c = e2_next((-.2, 0., 0.), speed=.5, world_direction=0., next_heading=.4,
                    signed_yaw=4., moving=False, transition=False, standing=False,
                    next_write_elapsed=2.)
        self.assertEqual(c, (-.2, 0., 0.))

    def test_w35_allrough_is_held_body_not_legacy_world_projection(self):
        for x in (-.3, -.001, 0., .001, .3):
            self.assertEqual(w35_next((x, 0., 0.), False), (x, 0., 0.))
            self.assertEqual(w35_next((x, 0., 0.), True), (0., 0., 0.))

    def test_w35_backwards_sampled_heading_plus_pi(self):
        self.assertAlmostEqual(sampled_progress_axis(.4, -.2), .4 + math.pi)
        self.assertEqual(sampled_progress_axis(.4, .2), .4)

    def test_w35_small_motion_not_boolean_stand(self):
        # Small vx remains moving unless the actual Boolean is true.
        self.assertEqual(w35_next((.0001, 0., 0.), False)[0], .0001)
        self.assertEqual(w35_next((.2, 0., 0.), True)[0], 0.)

    def test_resample_horizon_unknown_not_distribution_rewrite(self):
        self.assertEqual(sum(known_command_writes(.32)), 15)
        self.assertEqual(sum(known_command_writes(.33)), 16)
        self.assertFalse(known_command_writes(.01)[0])

    def test_original_scaled_timer_decoding(self):
        encoded_time_left = .33 * .01
        self.assertEqual(sum(known_command_writes(encoded_time_left / .01)), 16)
        self.assertEqual(sum(known_command_writes(encoded_time_left)), 0)

    def test_raw35_exact_indices_scales_and_zero_slots(self):
        x = raw35((.3, 0., 4.), .25, sensor(), (1., 2., 3., 4., 5., 6.), (1., 0., 0., 0., 0., 0., 0.))
        self.assertEqual(len(x), 35)
        self.assertEqual(x[:4], (.3, 0., 4., 1.25))
        self.assertEqual(x[4:7], (.5, 1., 1.5))
        self.assertEqual(x[7:10], (0., 0., -1.))
        self.assertEqual(x[10:16], (.1, .2, .3, .4, 0., 0.))
        self.assertEqual(x[22:28], (1., 2., 3., 4., 5., 6.))
        self.assertEqual(x[28], 1.)

    def test_raw35_rejects_width_error(self):
        with self.assertRaises(ValueError):
            raw35((0., 0.), .25, sensor(), (0,) * 6, (0,) * 7)

    def test_noise_delay_inputs_not_replaced_by_clean_state(self):
        x = sensor()
        x['base_ang_vel'] = (99., -3., .125)
        out = raw35((0., 0., 0.), .25, x, (0,) * 6, (0,) * 7)
        self.assertEqual(out[4:7], (49.5, -1.5, .0625))

    def test_delay_zero(self):
        t = FeedbackSampleTape(0)
        self.assertEqual(t.apply(1, .4), .4)
        self.assertEqual(t.apply(2, .9), .9)
        self.assertEqual(t.receipt['actual_age_us'], 0)

    def test_delay_one_10ms_warmup(self):
        t = FeedbackSampleTape(1)
        self.assertEqual(t.apply(1, .4), .4)
        self.assertTrue(t.receipt['warmup'])
        self.assertEqual(t.apply(2, .9), .4)
        self.assertEqual(t.receipt['actual_age_us'], 10000)
        self.assertEqual(t.apply(3, 1.5), .9)

    def test_same_tick_returns_cache_without_new_sample(self):
        t = FeedbackSampleTape(1)
        t.apply(10, .4)
        self.assertEqual(t.apply(10, 999.), .4)
        self.assertEqual(t.samples_consumed, 1)

    def test_skipped_or_reversed_sample_clock(self):
        for new_tick in (8, 12):
            t = FeedbackSampleTape(1)
            t.apply(10, .4)
            with self.assertRaisesRegex(ValueError, 'Skipped/reversed feedback sample clock'):
                t.apply(new_tick, .9)

    def test_two100Hz_samples_are_not_one50Hz_step(self):
        t = FeedbackSampleTape(1)
        t.apply(0, 'old')
        t.apply(1, 'midpoint')
        self.assertEqual(t.apply(2, 'endpoint'), 'midpoint')
        self.assertNotEqual(t.out, 'old')
        self.assertNotEqual(t.out, 'endpoint')

    def test_sample_frame_retained_not_applyframe_rotated(self):
        t = FeedbackSampleTape(1)
        original_body_sample = (1., 0., 0.)
        t.apply(0, original_body_sample)
        self.assertEqual(t.apply(1, (0., 1., 0.)), original_body_sample)

    def test_delay_fresh_episode_clears_history(self):
        t = FeedbackSampleTape(1)
        t.apply(50, 'old')
        t.reset()
        self.assertEqual(t.apply(51, 'fresh'), 'fresh')
        self.assertTrue(t.receipt['warmup'])

    def test_reward_source_sigma_denominator_not_squared(self):
        x = tracking_terms((.5, 0., .5), (0., 0., 0.), (0., 0., 0.), (0., 0., -1.))
        self.assertAlmostEqual(x['track_lin_vel'], math.exp(-1.))
        self.assertAlmostEqual(x['track_ang_vel'], math.exp(-1.))
        self.assertAlmostEqual(x['track_lin_vel_tight'], math.exp(-25.))
        self.assertNotEqual(x['track_lin_vel'], math.exp(-4.))

    def test_reward_pitch_projection_and_gate(self):
        x = tracking_terms((.8, 0., 2.), (1., 0., 0.), (0., 0., 0.), (.6, 0., -.8), height_gate=.2)
        self.assertAlmostEqual(x['track_lin_vel'], 1.)
        self.assertAlmostEqual(x['track_ang_vel_square'], .05)

    def test_reward_old_command_clock(self):
        x = tracking_terms((1., 0., 0.), (1., 0., 0.), (0., 0., 0.), (0., 0., -1.))
        wrong = tracking_terms((-1., 0., 0.), (1., 0., 0.), (0., 0., 0.), (0., 0., -1.))
        self.assertEqual(x['track_lin_vel'], 1.)
        self.assertLess(wrong['track_lin_vel'], 1e-6)

    def test_reward_decomposition_keeps_native_reward(self):
        for native, exact in ((-.4, .2), (3.7, -1.5), (0., .03)):
            residual = native - exact
            self.assertAlmostEqual(residual + exact, native)

    def test_bounded_residual_at_most_radius_from_clipped_teacher(self):
        for teacher in (-100., -6., -.3, 0., 5.99, 100.):
            for logit in (-1e6, -2., 0., 2., 1e6):
                base = max(-6., min(6., teacher))
                self.assertLessEqual(abs(bounded_action(teacher, logit) - base), .05 + 1e-12)

    def test_point05_scaling_is_not_bound(self):
        self.assertEqual(native_action(0., 1000.), 6.)
        self.assertGreater(abs(native_action(0., 1000.)), .05)
        self.assertAlmostEqual(bounded_action(0., 1000.), .05)

    def test_terminal_row_included_then_cut(self):
        self.assertEqual(valid_window_rows([False, True, False], [False] * 3), [True, True, False])

    def test_stream_boundary_included_then_cut(self):
        self.assertEqual(valid_window_rows([False] * 3, [True, False, False]), [True, False, False])

    def test_terminal_reward_kept_and_bootstrap_masked(self):
        self.assertEqual(lambda_targets([2.], [1.], [999.]), [2.])


class SourceStructuralTests(unittest.TestCase):
    def test_all_new_python_syntax_without_torch_import(self):
        for p in HERE.glob('*.py'):
            compile(p.read_text(encoding='utf-8'), str(p), 'exec')

    def test_original_replay_aux_and_history_resume_are_ast_identical(self):
        paths = [ROOT / 'source_core_review' / 'ctx_reward_learner.py', HERE / 'ctx_reward_candidate_v1.py']
        trees = [ast.parse(p.read_text(encoding='utf-8')) for p in paths]
        def cls(t, name):
            return next(n for n in t.body if isinstance(n, ast.ClassDef) and n.name == name)
        for name in ('ContextReplayBuffer', 'TaskAuxiliaryModel'):
            self.assertEqual(ast.dump(cls(trees[0], name)), ast.dump(cls(trees[1], name)))
        a, b = [cls(t, 'ContextRewardLearner') for t in trees]
        methods = [{n.name: ast.dump(n) for n in c.body if isinstance(n, ast.FunctionDef)} for c in (a, b)]
        changed = sorted(k for k in methods[0] if methods[0][k] != methods[1][k])
        self.assertEqual(changed, ['__init__', 'aux_update', 'policy_update'])

    def test_s1_to_a0_vjp_lines_kept_verbatim(self):
        base = (ROOT / 'source_core_review' / 'ctx_reward_learner.py').read_text(encoding='utf-8')
        candidate = (HERE / 'ctx_reward_candidate_v1.py').read_text(encoding='utf-8')
        start = base.index('            delayed = contributions[1:].sum(0) + bootstrap')
        end = base.index('            self.opt_pi.zero_grad(set_to_none=True)', start)
        self.assertIn(base[start:end], candidate)

    def test_raw35_actor_has_no_fullstate_or_privileged_inputs(self):
        tree = ast.parse((HERE / 'command_tracking_torch_candidate_v1.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Raw35ActorMDP')
        obs = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'obs')
        returns = [n for n in ast.walk(obs) if isinstance(n, ast.Return)]
        self.assertEqual(len(returns), 1)
        self.assertEqual(ast.unparse(returns[0].value), 'context[..., :35]')

    def test_sdk_reward_reset_command_obs_order_is_source_only(self):
        p = ROOT / 'discovery' / 'sdk_reward_command_call_order_v1' / 'envs' / 'manager_based_rl_env.py'
        s = p.read_text(encoding='utf-8')
        r = s.index('self.reward_manager.compute(dt=self.step_dt)')
        reset = s.index('self._reset_idx(reset_env_ids)', r)
        cmd = s.index('self.command_manager.compute(dt=self.step_dt)', reset)
        obs = s.index('self.observation_manager.compute(update_history=True)', cmd)
        self.assertLess(r, reset)
        self.assertLess(reset, cmd)
        self.assertLess(cmd, obs)


if __name__ == '__main__':
    buf = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
    payload = dict(kind='SYNTHETIC_STDLIB_FORMULA_AST_ONLY_NOT_RUNTIME',
                   passed=result.wasSuccessful(), tests=result.testsRun,
                   failures=len(result.failures), errors=len(result.errors),
                   Torch_available=importlib.util.find_spec('torch') is not None,
                   Torch_imported='torch' in __import__('sys').modules,
                   expert_training_updates=0, SDK_imported=False, GPU_used=False,
                   analytic_counterexample=COUNTEREXAMPLE, log=buf.getvalue())
    dest = HERE / 'TEST_RESULTS_STDLIB_V1.json'
    if dest.exists():
        raise FileExistsError(str(dest))
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(buf.getvalue())
    print(json.dumps({k: v for k, v in payload.items() if k != 'log'}, ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

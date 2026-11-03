"""Executable stdlib-only contract tests. No native numerical-parity claim."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch
import fake_runtime as fake
from passive_capture import (BoundedRecorder, PassiveCapture, UNKNOWN,
    stdlib_snapshot, install_passive_capture, _root_asset_configuration)
from source_api import build_manifest, pin, verify_callable, verify_class, closure_functions

HERE = Path(__file__).resolve().parent


def attach_fixture(env, *, first=32, last=32, cap=256, snapshot=stdlib_snapshot):
    """Test internals only. Production install always runs fail-closed preflight."""
    bridge = fake.FakeBridge(env)
    recorder = BoundedRecorder(first=first, last=last, max_events=cap)
    tap = PassiveCapture(env, bridge, fake, recorder, snapshot,
        dict(kind='FAKE_ONLY_NO_NATIVE_BINDING', native_enabled=False, exact=False)).attach()
    return tap, bridge


def events(tap, kind='feedback'):
    # First/last may overlap; deduplicate fixed-size snapshots for assertions only.
    rows = tap.recorder.report()
    merged = {r['sequence']: r for r in rows['retained_first'] + rows['retained_last']}
    return [r['payload'] for _, r in sorted(merged.items()) if r['kind'] == kind]


class CaptureContractTests(unittest.TestCase):
    def setUp(self):
        self.taps = []

    def tap(self, env, **kw):
        tap, bridge = attach_fixture(env, **kw)
        self.taps.append(tap)
        return tap, bridge

    def tearDown(self):
        for tap in reversed(self.taps):
            tap.close()

    def test_baseline_actor35_queue_rng_getters_and_call_counts_equal(self):
        baseline, observed = fake.FakeEnv(), fake.FakeEnv()
        baseline_bridge = fake.FakeBridge(baseline)
        tap, bridge = self.tap(observed)
        global_rng_before = random.getstate()
        for k in range(5):
            action = [(k + j) * .125 for j in range(6)]
            terminal = [1] if k == 2 else []
            left = baseline.step(action, terminal)
            right = observed.step(action, terminal)
            self.assertEqual(left, right)
            self.assertTrue(all(len(row) == 35 for row in right[0]))
            self.assertIs(right, observed.last_step_return)
            self.assertEqual(baseline.evidence(), observed.evidence())
        self.assertEqual(random.getstate(), global_rng_before)
        self.assertEqual((baseline_bridge.pack_calls, baseline_bridge.capture_calls), (bridge.pack_calls, bridge.capture_calls))
        self.assertEqual(bridge.pack_calls, 5)
        self.assertEqual(observed.counts['raw_getter'], 75)  # 10 original sample + 5 original manager terms/control
        self.assertEqual(observed.counts['observe'], 5)
        self.assertEqual(tap.calls['sensor_apply'], observed._sensor_mild.calls['apply'])
        self.assertEqual(tap.calls['delay_apply'], observed._feedback_delay_mild.calls['apply'])
        self.assertEqual(tap.recorder.capture_errors, 0)
        self.assertFalse(tap.report()['native_enabled'])
        self.assertFalse(tap.report()['exact'])

    def test_two_original_100hz_slots_per_control_not_every_eight(self):
        env = fake.FakeEnv()
        tap, _ = self.tap(env)
        env.step([0.] * 6)
        rows = events(tap)
        sampled = [r for r in rows if r['clock']['is_original_100hz_slot']]
        self.assertEqual(len(sampled), 10)
        self.assertEqual(sorted({r['clock']['physics_tick'] for r in sampled}), [4, 8])
        self.assertEqual(sorted({r['clock']['sim_time_us'] for r in sampled}), [10000, 20000])
        self.assertEqual(sorted({r['clock']['control_slot'] for r in sampled}), ['end', 'mid'])
        self.assertEqual(len([r for r in rows if r['clock']['phase'] == 'outside_scene_update']), 5)
        self.assertEqual(env._sensor_mild.draw_counts, {k: 6 for k in fake.CHANNELS})
        self.assertEqual(env._sensor_mild.batch_draws, {k: 2 for k in fake.CHANNELS})

    def test_same_tick_changed_clean_does_not_relabel_cached_delay_as_fresh(self):
        env = fake.FakeEnv(2)
        tap, _ = self.tap(env)
        env._feedback_100hz_tick = 7
        a = [[1., 2., 3.], [4., 5., 6.]]
        out_a = fake.feedback(env, 'base_ang_vel', a)
        self.assertIs(out_a, env._feedback_delay_mild.last_return)
        noise = fake.copy(env._sensor_mild.cache['base_ang_vel'][1])
        before = env.evidence()
        b = [[101., 102., 103.], [104., 105., 106.]]
        out_b = fake.feedback(env, 'base_ang_vel', b)
        self.assertIs(out_b, env._feedback_delay_mild.last_return)
        self.assertEqual(out_a, out_b)  # original delay reuses out at same tick
        self.assertEqual(noise, env._sensor_mild.cache['base_ang_vel'][1])
        self.assertEqual(before['sensor']['rng'], env.evidence()['sensor']['rng'])
        r = events(tap)[-1]
        self.assertEqual(r['clean'], b)
        self.assertNotEqual(r['sensor_stage']['actual_noisy_return'], r['return'])
        self.assertEqual(r['sensor_stage']['before']['noise_cache_last'], [7, 7])
        self.assertEqual(r['sensor_stage']['noise_cache_last'], [7, 7])
        self.assertEqual(r['delay_stage']['before'], r['delay_stage']['after'])
        self.assertEqual(r['delay_stage']['after']['cache']['sample_tick'], [7, 7])
        self.assertEqual(r['sensor_stage']['fresh_due_local'], UNKNOWN)
        self.assertEqual(r['delay_stage']['local_delayed_mask'], UNKNOWN)

    def test_partial_reset_same_tick_fresh_only_reset_row_warmup_age_zero(self):
        env = fake.FakeEnv(3)
        tap, _ = self.tap(env)
        env._feedback_100hz_tick = 8
        old = [[1.] * 4, [2.] * 4, [3.] * 4]
        prior = fake.feedback(env, 'leg_pos', old)
        env._reset_idx([1])
        env._feedback_delay_mild.delay[1] = 1  # fixture request: warmup lag1
        fresh = [[11.] * 4, [102.] * 4, [13.] * 4]
        out = fake.feedback(env, 'leg_pos', fresh)
        self.assertIs(out, env._feedback_delay_mild.last_return)
        self.assertEqual(out[0], prior[0])
        self.assertEqual(out[2], prior[2])
        self.assertEqual(out[1], env._sensor_mild.last_return[1])
        self.assertEqual(env._sensor_mild.draw_counts['leg_pos'], 4)
        r = events(tap)[-1]
        self.assertEqual(r['sensor_stage']['before']['noise_cache_last'], [8, -1, 8])
        self.assertEqual(r['sensor_stage']['episode'], [0, 1, 0])
        self.assertEqual(r['sensor_stage']['noise_cache_last'], [8, 8, 8])
        self.assertEqual(r['delay_stage']['after']['cache']['sample_tick'], [8, 8, 8])
        self.assertFalse(r['delay_stage']['after']['cache']['ready'][1])
        self.assertEqual(r['delay_stage']['before']['cache']['last'], [8, -1, 8])
        reset = events(tap, 'reset_boundary')[0]
        self.assertEqual(reset['before']['sensor_episode'], [0, 0, 0])
        self.assertEqual(reset['after']['sensor_episode'], [0, 1, 0])

    def test_queue_real_lag_selection_before_after_and_no_alias(self):
        env = fake.FakeEnv(2)
        tap, _ = self.tap(env)
        env._feedback_delay_mild.delay[:] = [0, 1]
        first_raw = [[1., 2., 3.], [4., 5., 6.]]
        first_out = fake.feedback(env, 'base_ang_vel', first_raw)
        env._feedback_100hz_tick = 1
        second_raw = [[10., 20., 30.], [40., 50., 60.]]
        second_out = fake.feedback(env, 'base_ang_vel', second_raw)
        self.assertEqual(second_out[1], first_out[1])
        self.assertEqual(second_out[0], env._sensor_mild.last_return[0])
        r = events(tap)[-1]
        self.assertEqual(r['delay_stage']['after']['cache']['sample_tick'], [1, 0])
        self.assertEqual(r['delay_stage']['after']['cache']['cur'], r['delay_actual_input'])
        self.assertEqual(r['delay_stage']['before']['cache']['cur'], first_out)
        saved = fake.copy(r)
        second_raw[0][0] = 9000.
        env._sensor_mild.cache['base_ang_vel'][1][0][0] = 7000.
        env._feedback_delay_mild.cache['base_ang_vel']['out'][0][0] = 8000.
        self.assertEqual(r, saved)

    def test_terminal_pre_reset_is_existing_bridge_pack_not_postreset_obs(self):
        env = fake.FakeEnv(2)
        tap, bridge = self.tap(env)
        result = env.step([.5] * 6, [1])
        self.assertIs(result, env.last_step_return)
        terminal = events(tap, 'terminal_pre_reset')[0]
        self.assertEqual(terminal['bridge_pre']['s1']['physical_episode'], [0, 0])
        self.assertEqual(terminal['bridge_pre']['term'], [False, True])
        self.assertEqual(terminal['episode'], [0, 0])
        self.assertEqual(env.physical_episode, [0, 1])
        self.assertEqual(bridge.pack_calls, 1)
        all_events = sorted({r['sequence']: r for r in tap.recorder.first}.values(), key=lambda x: x['sequence'])
        kinds = [r['kind'] for r in all_events]
        self.assertLess(kinds.index('terminal_pre_reset'), kinds.index('reset_boundary'))
        self.assertEqual(events(tap)[-1]['sensor_stage']['episode'], [0, 1])
        self.assertEqual(terminal['terminal_clean35'], UNKNOWN)

    def test_return_identity_when_profiles_off_and_no_noise_cache_is_unknown(self):
        env = fake.FakeEnv(2)
        env._sensor_mild.profile = 'off'
        env._feedback_delay_mild.enabled = False
        tap, _ = self.tap(env)
        raw = [[1., 2., 3.], [4., 5., 6.]]
        out = fake.feedback(env, 'base_ang_vel', raw)
        self.assertIs(out, raw)
        self.assertIs(out, env._sensor_mild.last_return)
        self.assertIs(out, env._feedback_delay_mild.last_return)
        row = events(tap)[0]
        self.assertEqual(row['sensor_stage']['noise_used'], UNKNOWN)
        self.assertEqual(row['delay_stage']['after']['cache'], UNKNOWN)
        self.assertEqual(env._sensor_mild.draw_counts['base_ang_vel'], 0)

    def test_original_exception_identity_exactly_once_no_observer_recovery(self):
        env = fake.FakeEnv()
        error = RuntimeError('original sensor failure fixture')
        original_calls = []
        def fail(*args, **kwargs):
            original_calls.append((args, kwargs))
            raise error
        env._sensor_mild.apply = fail
        tap, _ = self.tap(env)
        with self.assertRaises(RuntimeError) as caught:
            fake.feedback(env, 'base_ang_vel', [[0.] * 3 for _ in range(3)])
        self.assertIs(caught.exception, error)
        self.assertEqual(len(original_calls), 1)
        self.assertEqual(tap.calls['feedback'], 1)
        self.assertEqual(tap.calls['sensor_apply'], 1)
        self.assertEqual(tap.calls['delay_apply'], 0)
        self.assertEqual(events(tap)[0]['exception']['message'], str(error))
        self.assertIsNone(tap._active)

    def test_original_delay_clock_exception_keeps_prior_rng_mutation_order(self):
        baseline, observed = fake.FakeEnv(2), fake.FakeEnv(2)
        fake.FakeBridge(baseline)
        tap, _ = self.tap(observed)
        raw = [[0.] * 3 for _ in range(2)]
        for env in (baseline, observed):
            fake.feedback(env, 'base_ang_vel', raw)
            env._feedback_100hz_tick = 2
            with self.assertRaisesRegex(AssertionError, 'Skipped/reversed feedback sample clock'):
                fake.feedback(env, 'base_ang_vel', raw)
        self.assertEqual(baseline.evidence(), observed.evidence())
        self.assertEqual(events(tap)[-1]['exception']['type'], 'AssertionError')

    def test_observer_snapshot_error_does_not_replace_original_return(self):
        env = fake.FakeEnv(2)
        def broken(_):
            raise ValueError('observer snapshot fixture')
        tap, _ = self.tap(env, snapshot=broken)
        raw = [[0.] * 3 for _ in range(2)]
        out = fake.feedback(env, 'base_ang_vel', raw)
        self.assertIs(out, env._feedback_delay_mild.last_return)
        self.assertGreater(tap.recorder.capture_errors, 0)
        self.assertFalse(tap.report()['capture_complete'])
        self.assertEqual(env._sensor_mild.calls['apply'], 1)
        self.assertEqual(env._feedback_delay_mild.calls['apply'], 1)

    def test_bounded_first_last_count_cap_continues_original_calls(self):
        env = fake.FakeEnv(1)
        calls = []
        def snapshot(x):
            calls.append(1)
            return stdlib_snapshot(x)
        tap, _ = self.tap(env, first=2, last=3, cap=5, snapshot=snapshot)
        for k in range(10000):
            env._feedback_100hz_tick = k
            fake.feedback(env, 'wheel_vel', [[float(k), .5]])
            if k == 4:
                snapshot_calls_at_cap = len(calls)
        self.assertEqual(len(calls), snapshot_calls_at_cap)
        report = tap.recorder.report()
        self.assertEqual((report['count'], report['captured']), (10000, 5))
        self.assertEqual([r['sequence'] for r in report['retained_first']], [1, 2])
        self.assertEqual([r['sequence'] for r in report['retained_last']], [3, 4, 5])
        self.assertEqual(len(tap.recorder.first) + len(tap.recorder.last), 5)
        self.assertEqual(env._sensor_mild.draw_counts['wheel_vel'], 10000)
        self.assertEqual(env._feedback_delay_mild.calls['apply'], 10000)
        self.assertEqual(tap.recorder._pending, 0)

    def test_restore_exact_instance_dictionary_and_module_symbol(self):
        env = fake.FakeEnv()
        original_feedback = fake.feedback
        sensor_dict = dict(vars(env._sensor_mild))
        delay_dict = dict(vars(env._feedback_delay_mild))
        self.assertNotIn('apply', sensor_dict)
        self.assertNotIn('_reset_idx', vars(env))
        tap, bridge = self.tap(env)
        original_bridge_compute = bridge._termination_capture
        tap.close()
        self.assertIs(fake.feedback, original_feedback)
        self.assertEqual(vars(env._sensor_mild), sensor_dict)
        self.assertEqual(vars(env._feedback_delay_mild), delay_dict)
        self.assertNotIn('_reset_idx', vars(env))
        self.assertIs(env.termination_manager.compute.__self__, bridge)
        self.assertIs(env.termination_manager.compute.__func__, original_bridge_compute.__func__)
        tap.close()

    def test_foreign_env_passthrough_no_cross_env_capture(self):
        observed, other = fake.FakeEnv(2), fake.FakeEnv(2)
        tap, _ = self.tap(observed)
        raw = [[0.] * 3 for _ in range(2)]
        out = fake.feedback(other, 'base_ang_vel', raw)
        self.assertIs(out, other._feedback_delay_mild.last_return)
        self.assertEqual(tap.recorder.seen, 0)
        self.assertEqual(tap.calls['feedback'], 0)
        self.assertEqual(observed._sensor_mild.calls['apply'], 0)

    def test_fail_closed_native_preflight_on_fake_does_not_assign(self):
        env = fake.FakeEnv()
        bridge = fake.FakeBridge(env)
        manifest = json.loads((HERE / 'SOURCE_API_MANIFEST.json').read_text(encoding='utf-8'))
        feedback_before, sensor_before = fake.feedback, env._sensor_mild.apply
        with self.assertRaises((ValueError, AttributeError)):
            install_passive_capture(env, bridge, fake, manifest['roles']['E3'], manifest['bridge'])
        self.assertIs(fake.feedback, feedback_before)
        self.assertIs(env._sensor_mild.apply.__func__, sensor_before.__func__)
        self.assertNotIn('apply', vars(env._sensor_mild))
        self.assertNotIn('_reset_idx', vars(env))

    def test_code_pin_line_signature_and_live_bytecode_tamper(self):
        p = pin(HERE / 'fake_runtime.py', 'fake_runtime', 'feedback')
        receipt = verify_callable(fake.feedback, p)
        self.assertTrue(receipt['live_bytecode_matches_source'])
        self.assertIn('env, key, raw', receipt['signature'])
        old_code = fake.feedback.__code__
        try:
            fake.feedback.__code__ = old_code.replace(co_consts=old_code.co_consts + ('tampered fixture',))
            with self.assertRaisesRegex(ValueError, 'Live bytecode differs'):
                verify_callable(fake.feedback, p)
        finally:
            fake.feedback.__code__ = old_code
        wrong = dict(p, source_sha256='0' * 64)
        with self.assertRaisesRegex(ValueError, 'hash/line mismatch'):
            verify_callable(fake.feedback, wrong)

    def test_terminal_and_reset_original_return_identity_and_exception(self):
        env = fake.FakeEnv()
        bridge = fake.FakeBridge(env)
        token, error = object(), RuntimeError('original reset failure fixture')
        reset_calls = []
        def reset(*args, **kwargs):
            reset_calls.append((args, kwargs))
            if kwargs.get('fail'):
                raise error
            return token
        env._reset_idx = reset
        recorder = BoundedRecorder(first=8, last=8)
        tap = PassiveCapture(env, bridge, fake, recorder, stdlib_snapshot, {'fake': True}).attach()
        self.taps.append(tap)
        out = env.termination_manager.compute()
        self.assertIs(out, env.termination_manager.terminated)
        self.assertEqual(bridge.capture_calls, 1)
        self.assertIs(env._reset_idx([1]), token)
        with self.assertRaises(RuntimeError) as caught:
            env._reset_idx([1], fail=True)
        self.assertIs(caught.exception, error)
        self.assertEqual(len(reset_calls), 2)
        self.assertEqual(tap._reset_depth, 0)
        self.assertEqual(tap._phase, 'outside_scene_update')
        self.assertEqual(events(tap, 'reset_boundary')[-1]['exception']['message'], str(error))

    def test_default_argument_objects_on_original_callable_are_unchanged(self):
        env = fake.FakeEnv()
        bridge = fake.FakeBridge(env)
        marker = []
        calls = []
        def sensor(key, value, tick, retained_default=marker):
            calls.append(retained_default)
            return value
        env._sensor_mild.apply = sensor
        env._feedback_delay_mild.enabled = False
        before_defaults = sensor.__defaults__
        tap = PassiveCapture(env, bridge, fake, BoundedRecorder(), stdlib_snapshot, {'fake': True}).attach()
        self.taps.append(tap)
        raw = [[0.] * 3 for _ in range(3)]
        self.assertIs(fake.feedback(env, 'base_ang_vel', raw), raw)
        self.assertIs(calls[0], marker)
        self.assertIs(sensor.__defaults__, before_defaults)
        tap.close()
        self.assertIs(env._sensor_mild.apply, sensor)
        self.assertIs(env._sensor_mild.apply.__defaults__[0], marker)

    def test_source_manifest_eight_roles_and_closure_binding(self):
        manifest = build_manifest()
        self.assertEqual(set(manifest['roles']), set(('E0', 'E2', 'E3', 'W35', 'CURB_PROTECTED878', 'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50')))
        self.assertFalse(manifest['native_enabled'])
        self.assertFalse(manifest['exact'])
        for role in manifest['roles'].values():
            self.assertIn('feedback_delay_runtime', [r['module'] for r in role['env_mro_local']])
            self.assertEqual(role['pins']['feedback']['parameters'], ['env', 'key', 'raw'])
            self.assertIsNotNone(role['pins']['env_reset'])
        env = fake.FakeEnv()
        functions = list(closure_functions(env.scene.update))
        self.assertTrue(any('update' == f.__name__ for f in functions))
        sampling = functions[0]
        cells = dict(zip(sampling.__code__.co_freevars, sampling.__closure__))
        self.assertIs(cells['self'].cell_contents, env)

    def test_mutable_robot_default_and_explicit_asset_are_checked(self):
        from types import SimpleNamespace
        default = SimpleNamespace(name='robot')
        def root(env, asset_cfg=default):
            return None
        term = SimpleNamespace(func=root, params={})
        result = _root_asset_configuration(term)
        self.assertEqual(result['actual_asset_name'], 'robot')
        default.name = 'other_robot'
        with self.assertRaisesRegex(ValueError, 'default asset'):
            _root_asset_configuration(term)
        default.name = 'robot'
        term.params = {'asset_cfg': SimpleNamespace(name='other_robot')}
        with self.assertRaisesRegex(ValueError, 'Actual root'):
            _root_asset_configuration(term)
        term.params = {'asset_cfg': SimpleNamespace(name='robot')}
        self.assertTrue(_root_asset_configuration(term)['explicit_asset_override'])

    def test_provenance_paths_are_not_deployment_lookup_paths(self):
        expected = pin(HERE / 'fake_runtime.py', 'fake_runtime', 'feedback')
        expected['source_path'] = 'Z:/NONEXISTENT_SOURCE_PROVENANCE/feedback.py'
        receipt = verify_callable(fake.feedback, expected)
        self.assertEqual(Path(receipt['source_path']), HERE / 'fake_runtime.py')
        self.assertTrue(receipt['live_bytecode_matches_source'])
        expected_class = pin(HERE / 'fake_runtime.py', 'fake_runtime', 'FakeEnv')
        expected_class['source_path'] = '/NONEXISTENT_LINUX_PROVENANCE/fake.py'
        class_receipt = verify_class(fake.FakeEnv, expected_class)
        self.assertEqual(Path(class_receipt['source_path']), HERE / 'fake_runtime.py')
        tree = ast.parse((HERE / 'passive_capture.py').read_text(encoding='utf-8'))
        method = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'preflight')
        self.assertNotIn("['source_path']", ast.unparse(method))

    def test_production_imports_have_no_sdk_torch_process_or_signals(self):
        for name in ('passive_capture.py', 'source_api.py'):
            tree = ast.parse((HERE / name).read_text(encoding='utf-8'))
            imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
            imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
            self.assertFalse(any(x and x.split('.')[0] in ('torch', 'isaaclab', 'subprocess', 'signal', 'socket', 'paramiko', 'os') for x in imports))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CaptureContractTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = dict(kind='STDLIB_FAKE_PASSIVE_CAPTURE_TEST_RECEIPT_V1',
                   source_only=True, native_enabled=False, exact=False,
                   python=sys.version, tests_run=result.testsRun,
                   failures=[name.id() for name, _ in result.failures],
                   errors=[name.id() for name, _ in result.errors],
                   passed=result.wasSuccessful(),
                   native_SDK_execution=False, actual_tensor_parity_test=False,
                   real_PT_reads=0, canonical_ledger_access=0,
                   source_hashes={name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                       for name in ('passive_capture.py', 'source_api.py', 'fake_runtime.py', 'test_passive_capture.py')})
    # Re-run without a write when receipt already exists; never overwrite evidence.
    out = HERE / 'STDLIB_FAKE_TEST_RECEIPT_v3.json'
    if not out.exists():
        out.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)

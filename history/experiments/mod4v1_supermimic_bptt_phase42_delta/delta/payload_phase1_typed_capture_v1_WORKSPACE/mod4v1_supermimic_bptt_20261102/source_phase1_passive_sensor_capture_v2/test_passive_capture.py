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


class PublishedResetCompositionTests(unittest.TestCase):
    """Actual published wrapper CODE, explicitly fake instances, no SDK execution.

    Positive binding fixtures attach original constructor/reset descriptor code
    without running constructors. Flow fixtures use fake adapter reset behavior;
    their four wrapper functions are actual source code, NOT toy replacements.
    Flow fixtures explicitly bypass native preflight and claim no native binding.
    """
    PUBLISHED_E3 = {
        'explicit_pd_sdk_adapter': 'e9995ecd802f26cae1061a9540efdea1b34ae143bdfc9c8619508c560b438ae3',
        'chassis_com_pose_roundtrip_sdk_adapter': '32d554f4efa29a2cb7bc669d5067c03315d1cf55603269ea9a6041dc8244f6e1',
        'gas_damping_sdk_adapter': '3b318b827329e22038a2abb89ba97827355bf4ac5e6211ebce697def714e1ea5',
        'spring_pressure_index_runtime': '4ea0a70293f09dda4d7fe862068c1460ea6acbb8db2accb7ea0fa31d9ccedc58',
    }

    def setUp(self):
        import source_api as api
        import types
        self.api, self.types = api, types
        self.spec = json.loads((HERE / 'SOURCE_API_MANIFEST.json').read_text(encoding='utf-8'))['roles']['E3']['reset_chain']
        self.modules, self.old_modules, self.source_classes, self.taps = {}, {}, {}, []
        self.addCleanup(self.restore)

    def restore(self):
        for tap in reversed(self.taps):
            tap.close()
        for name, old in self.old_modules.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old

    def module(self, name, path):
        if name not in self.modules:
            m = self.types.ModuleType(name)
            m.__file__ = path
            self.old_modules[name] = sys.modules.get(name)
            self.modules[name] = m
            sys.modules[name] = m
        return self.modules[name]

    @staticmethod
    def cell(value):
        def borrow(): return value
        return borrow.__closure__[0]

    def function(self, p, bindings=None):
        path = Path(p['source_path'])
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), p['source_sha256'])
        if p['module'] in self.PUBLISHED_E3:
            self.assertEqual(p['source_sha256'], self.PUBLISHED_E3[p['module']])
        code = self.api._find_code(compile(raw.decode('utf-8'), str(path), 'exec', dont_inherit=True, optimize=sys.flags.optimize), p['qualname'])
        self.assertIsNotNone(code)
        closure = tuple(self.cell((bindings or {})[k]) for k in code.co_freevars)
        defaults = tuple(ast.literal_eval(x) for x in p['positional_default_expressions']) or None
        return self.types.FunctionType(code, self.module(p['module'], str(path)).__dict__, code.co_name, defaults, closure or None)

    def adapter_class(self, layer):
        base = object
        for p in reversed(layer['adapter_mro_local']):
            key = (p['module'], p['qualname'])
            if key in self.source_classes:
                base = self.source_classes[key]
                continue
            cls = type(p['qualname'], (base,), {'__module__': p['module']})
            self.module(p['module'], p['source_path']).__dict__[p['qualname']] = cls
            for method in layer['adapter_descriptors']:
                if method['owner'] == p['qualname'] and method['pin']['module'] == p['module']:
                    setattr(cls, method['name'], self.function(method['pin'], {'__class__': cls}))
            self.source_classes[key] = cls
            base = cls
        return base

    def fixture(self, *, flow=False):
        p = self.spec['endpoint']
        mod = self.module(p['module'], p['source_path'])
        cls = self.source_classes.get(('ENV', p['qualname']))
        if cls is None:
            name = p['qualname'].rsplit('.', 1)[0]
            cls = type(name, (fake.FakeEnv,), {'__module__': p['module']})
            mod.__dict__[name] = cls
            cls._reset_idx = self.function(p, {'__class__': cls})
            self.source_classes[('ENV', p['qualname'])] = cls
        env = cls(3)  # inherited FAKE initializer, not actual RecoveryEnv constructor
        env.recovery, env.e3_reset_enabled, env.device = None, False, 'FAKE_CPU_NO_TENSOR_OR_SDK'
        env.source_flow_trace, env.source_flow_queue = [], []
        env.source_flow_rngs, env.source_flow_draw_counts = {}, {}
        for i, layer in enumerate(reversed(self.spec['layers'])):
            adapter = object.__new__(self.adapter_class(layer))
            adapter.env, adapter.robot, adapter.component = env, object(), object()
            attr = layer['env_attribute']
            setattr(env, attr, adapter)
            if flow:
                rng = random.Random(731 + i)
                env.source_flow_rngs[attr] = rng
                env.source_flow_draw_counts[attr] = 0
                def reset(ids, attr=attr, rng=rng, env=env):
                    env.source_flow_trace.append((attr, tuple(ids)))
                    env.source_flow_queue.append((attr, rng.random()))
                    env.source_flow_draw_counts[attr] += 1
                adapter.reset = reset  # explicitly FAKE flow behavior, no native admission
        self.rebuild(env)
        return env

    def rebuild(self, env, order=None, *, original=None):
        chain = original or self.types.MethodType(type(env)._reset_idx, env)
        for layer in reversed(self.spec['layers'] if order is None else order):
            fn = self.function(layer['function'], {'adapter': vars(env)[layer['env_attribute']], 'original': chain})
            chain = self.types.MethodType(fn, env)
        env._reset_idx = chain
        return chain

    def replace_cells(self, env, **updates):
        old = env._reset_idx.__func__
        bindings = self.api._closure_values(old)
        bindings.update(updates)
        fn = self.types.FunctionType(old.__code__, old.__globals__, old.__name__, old.__defaults__,
                                     tuple(self.cell(bindings[k]) for k in old.__code__.co_freevars))
        env._reset_idx = self.types.MethodType(fn, env)
        return fn

    def rejected(self, env, spec=None):
        before, original_global = env.evidence(), random.getstate()
        with self.assertRaises(self.api.ResetBindingMismatch) as caught:
            self.api.verify_existing_reset_chain(env, spec or self.spec)
        self.assertEqual(before, env.evidence())
        self.assertEqual(original_global, random.getstate())
        self.assertIn('diagnostic=', str(caught.exception))
        self.assertIn('observed', caught.exception.diagnostic)
        self.assertFalse(caught.exception.diagnostic['native_enabled'])
        return caught.exception

    def test_published_function_code_strict_composition_positive_without_invocation(self):
        env = self.fixture()
        before, original_global = env.evidence(), random.getstate()
        r = self.api.verify_existing_reset_chain(env, self.spec)
        self.assertEqual(len(r['layers']), 4)
        self.assertEqual(r['terminal_descriptor']['qualname'], 'RecoveryEnv._reset_idx')
        self.assertTrue(r['no_original_function_called'])
        self.assertTrue(all(x['function']['raw_function_verified_without_unwrap'] for x in r['layers']))
        self.assertEqual(before, env.evidence())
        self.assertEqual(original_global, random.getstate())

    def test_eight_roles_own_constructor_source_evidence_live_stays_unknown(self):
        for role, r in self.api.build_manifest()['roles'].items():
            spec = r['reset_chain']
            self.assertEqual(spec['status'], 'SOURCE_CONFIRMED_LIVE_UNKNOWN', role)
            self.assertEqual(spec['live_binding'], 'UNKNOWN')
            self.assertEqual([x['env_attribute'] for x in spec['layers']], ['_explicit_pd', '_chassis_com', '_gas_damping', '_spring_pressure'])
            self.assertEqual(len(spec['constructor_order']), 3)
            self.assertTrue(all('/' + role + '/' in x['pin']['source_path'].replace('\\', '/') for x in spec['constructor_order']))
            self.assertEqual(spec['endpoint']['qualname'], r['pins']['env_reset']['qualname'])

    def test_published_wrapper_flow_once_order_private_rng_queue_and_none_identity(self):
        baseline, observed = self.fixture(flow=True), self.fixture(flow=True)
        original_global = random.getstate()
        left_bridge, bridge = fake.FakeBridge(baseline), fake.FakeBridge(observed)
        tap = PassiveCapture(observed, bridge, fake, BoundedRecorder(first=32, last=32), stdlib_snapshot,
            {'kind': 'PUBLISHED_WRAPPER_CODE_FAKE_ADAPTER_FLOW_ONLY', 'native_preflight_executed': False}).attach()
        self.taps.append(tap)
        self.assertIsNone(baseline._reset_idx([1]))
        self.assertIsNone(observed._reset_idx([1]))
        self.assertEqual(baseline.evidence(), observed.evidence())
        self.assertEqual([x[0] for x in observed.source_flow_trace], ['_spring_pressure', '_gas_damping', '_chassis_com', '_explicit_pd'])
        self.assertEqual(baseline.source_flow_queue, observed.source_flow_queue)
        self.assertEqual(baseline.source_flow_draw_counts, observed.source_flow_draw_counts)
        for name, rng in baseline.source_flow_rngs.items():
            self.assertEqual(rng.getstate(), observed.source_flow_rngs[name].getstate())
            self.assertEqual(observed.source_flow_draw_counts[name], 1)
        self.assertEqual(random.getstate(), original_global)
        self.assertEqual(tap.calls['reset_boundary'], 1)
        self.assertEqual(len(events(tap, 'reset_boundary')), 1)
        self.assertEqual(baseline.step([.25] * 6, [2]), observed.step([.25] * 6, [2]))
        self.assertEqual(baseline.evidence(), observed.evidence())
        self.assertEqual(left_bridge.pack_calls, bridge.pack_calls)
        self.assertEqual(sorted({x['clock']['physics_tick'] for x in events(tap) if x['clock']['is_original_100hz_slot']}), [4, 8])
        self.assertEqual(events(tap, 'terminal_pre_reset')[0]['episode'], [0, 1, 0])

    def test_published_wrapper_flow_exception_identity_no_retry_or_outer_side_effects(self):
        env, error = self.fixture(flow=True), RuntimeError('fake gas original exception')
        def fail(ids):
            env.source_flow_trace.append(('GAS_FAILURE', tuple(ids)))
            raise error
        env._gas_damping.reset = fail
        bridge = fake.FakeBridge(env)
        tap = PassiveCapture(env, bridge, fake, BoundedRecorder(), stdlib_snapshot,
                             {'native_preflight_executed': False, 'fake_adapters': True}).attach()
        self.taps.append(tap)
        with self.assertRaises(RuntimeError) as caught: env._reset_idx([1])
        self.assertIs(caught.exception, error)
        self.assertEqual(env.source_flow_trace, [('_spring_pressure', (1,)), ('GAS_FAILURE', (1,))])
        self.assertEqual(tap.calls['reset_boundary'], 1)
        self.assertEqual(tap._reset_depth, 0)
        self.assertEqual(tap.recorder.first[0]['payload']['exception']['message'], str(error))

    def test_composition_negative_cases_fail_closed_without_original_calls(self):
        def wrong_order(e): self.rebuild(e, [self.spec['layers'][1], self.spec['layers'][0]] + self.spec['layers'][2:])
        def duplicate(e): self.rebuild(e, [self.spec['layers'][0]] + self.spec['layers'])
        def unknown(e):
            original = e._reset_idx
            def foreign(this, ids): return original(ids)
            e._reset_idx = self.types.MethodType(foreign, e)
        def missing(e): e._reset_idx = self.api._closure_values(e._reset_idx.__func__)['original']
        def descriptor_only(e): del e._reset_idx
        def foreign_self(e): e._reset_idx = self.types.MethodType(e._reset_idx.__func__, self.fixture())
        def foreign_original(e): self.replace_cells(e, original=self.fixture()._reset_idx)
        def foreign_adapter(e): self.replace_cells(e, adapter=self.fixture()._explicit_pd)
        def adapter_env(e): e._explicit_pd.env = self.fixture()
        def slot(e): e._explicit_pd = object()
        def missing_fields(e): del e._explicit_pd.component
        def subclass(e): e._explicit_pd.__class__ = type('UnknownPD', (type(e._explicit_pd),), {})
        def extra_cell(e):
            old = e._reset_idx.__func__
            code = old.__code__.replace(co_freevars=old.__code__.co_freevars + ('polluted',))
            fn = self.types.FunctionType(code, old.__globals__, old.__name__, old.__defaults__, old.__closure__ + (self.cell(object()),))
            e._reset_idx = self.types.MethodType(fn, e)
        def bytecode(e):
            f = e._reset_idx.__func__
            f.__code__ = f.__code__.replace(co_consts=f.__code__.co_consts + ('foreign constant',))
        def globals_copy(e):
            f = e._reset_idx.__func__
            e._reset_idx = self.types.MethodType(self.types.FunctionType(f.__code__, dict(f.__globals__), f.__name__, f.__defaults__, f.__closure__), e)
        def defaults(e): e._reset_idx.__func__.__defaults__ = (object(),)
        def unwrap_skip(e): e._reset_idx.__func__.__wrapped__ = e._reset_idx.__func__
        def endpoint_clone(e):
            f = type(e)._reset_idx
            clone = self.types.FunctionType(f.__code__, f.__globals__, f.__name__, f.__defaults__, f.__closure__)
            self.rebuild(e, original=self.types.MethodType(clone, e))
        def endpoint_class(e):
            f = type(e)._reset_idx
            type(e)._reset_idx = self.types.FunctionType(f.__code__, f.__globals__, f.__name__, f.__defaults__, (self.cell(fake.FakeEnv),))
            self.rebuild(e)
        def ctor_code(e):
            f = vars(type(e._explicit_pd))['__init__']
            f.__code__ = f.__code__.replace(co_consts=f.__code__.co_consts + ('constructor pollution',))
        def reset_override(e): e._explicit_pd.reset = lambda ids: None
        cases = (wrong_order, duplicate, unknown, missing, descriptor_only, foreign_self, foreign_original,
                 foreign_adapter, adapter_env, slot, missing_fields, subclass, extra_cell, bytecode,
                 globals_copy, defaults, unwrap_skip, endpoint_clone, endpoint_class, ctor_code, reset_override)
        for mutate in cases:
            with self.subTest(case=mutate.__name__):
                self.source_classes.clear()
                env = self.fixture()
                mutate(env)
                self.rejected(env)

    def test_unknown_source_role_stays_unknown_and_fixed_sha_is_required(self):
        env = self.fixture()
        self.rejected(env, dict(self.spec, status='UNKNOWN'))
        changed = json.loads(json.dumps(self.spec))
        changed['layers'][0]['function']['source_sha256'] = '0' * 64
        self.rejected(env, changed)

    def test_diagnostic_expected_observed_bounded_no_getters_or_rng_calls(self):
        env = self.fixture()
        before, original_global = env.evidence(), random.getstate()
        r = self.api.diagnose_reset_chain(env, self.spec)
        self.assertEqual(len(r['observed']), 5)
        self.assertEqual(r['observed'][0]['module'], 'explicit_pd_sdk_adapter')
        self.assertEqual(r['observed'][0]['qualname'], 'ExplicitPDSDK.__init__.<locals>.reset_idx')
        self.assertTrue(all('co_filename' in x and 'source_sha256' in x and x['bound_self_is_env'] for x in r['observed']))
        self.assertTrue(r['no_task_function_called'] and r['no_SDK_getter_called'])
        self.assertEqual(before, env.evidence())
        self.assertEqual(random.getstate(), original_global)
        r = self.api.diagnose_preflight_bindings(env, fake.FakeBridge(env), fake,
            json.loads((HERE / 'SOURCE_API_MANIFEST.json').read_text(encoding='utf-8'))['roles']['E3'], {})
        self.assertIn('scene_update_closure_functions', r)
        self.assertLessEqual(len(r['scene_update_closure_functions']), 8)
        self.assertFalse(r['native_enabled'])


if __name__ == '__main__':
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(CaptureContractTests),
                                unittest.defaultTestLoader.loadTestsFromTestCase(PublishedResetCompositionTests)])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = dict(kind='STDLIB_FAKE_PASSIVE_CAPTURE_TEST_RECEIPT_V1',
                   source_revision=2, inherited_test_methods=21,
                   published_code_composition_test_methods=7,
                   composition_negative_subcases=21,
                   original_published_wrapper_code_compiled=True,
                   original_adapter_constructors_executed=False,
                   actual_native_preflight_executed=False,
                   actual_Torch_CPU_executed_by_this_child=False,
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

"""stdlib fake plumbing + AST/source tests. No SDK/native/plant execution."""
import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from capture_adapter import install_after_first_reset
from capture_contract import (CHANNELS, FINAL_KIND, INTEGRATION, PURPOSE,
                              validate_source_request, validate_waited_capture_evidence)
from source_preflight import audit_source

HERE = Path(__file__).resolve().parent


def request():
    return json.loads((HERE / 'SOURCE_REQUEST.json').read_text(encoding='utf-8'))


class Actor:
    shape = (80, 35)
    def __init__(self):
        self.values = [[0.0] * 35 for _ in range(80)]


class Recorder:
    def __init__(self, first, last, max_events):
        self.bounds = first, last, max_events
        self.events, self.capture_errors = [], 0
    def begin(self, kind):
        return (len(self.events) + 1, kind)
    def commit(self, ticket, payload):
        self.events.append(dict(sequence=ticket[0], kind=ticket[1], payload=payload))
    def capture_error(self, error):
        self.capture_errors += 1


class Tap:
    def __init__(self):
        self.closed, self.close_calls = False, 0
    def close(self):
        self.closed = True
        self.close_calls += 1
    def report(self):
        return dict(fake=True, capture_errors=0)


class FakeAPI:
    BoundedRecorder = Recorder
    def __init__(self):
        self.calls = []
        self.tap = Tap()
    def stdlib_snapshot(self, value):
        return copy.deepcopy(value.values if isinstance(value, Actor) else value)
    def install_passive_capture(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.tap


def plumbing():
    env = SimpleNamespace(_sensor_mild=object(), _feedback_delay_mild=object(),
                          _sim_step_counter=0, _feedback_100hz_tick=0)
    bridge = SimpleNamespace(real=env, initialized=True, state=object(), num_envs=80)
    api = FakeAPI()
    module, role_api, bridge_pin = object(), {'fake': True}, {'fake': True}
    session = install_after_first_reset(env, bridge, module, role_api, bridge_pin,
                                        request(), sensor_api=api)
    return env, bridge, api, module, role_api, bridge_pin, session


def fake_evidence():
    # Deliberately SYNTHETIC values: tests predicate strength, not authenticity.
    final = dict(kind=FINAL_KIND, purpose=PURPOSE, integration=INTEGRATION,
                 role='E3', num_envs=80, controls=64, bridge_controls=64, synthetic_actions=64,
                 physics_ticks_delta=512, fresh_100hz_samples_by_key={k: 128 for k in CHANNELS},
                 clean_input_dim=16, full_clean35_mid_end='UNKNOWN',
                 actor35_source='original_returned_policy_buffer', observer_extra_plant_calls=0,
                 observer_rng_calls=0, actual_binding_checked=True, original_return_identity_checked=True,
                 terminal_pre_reset_observed=True, partial_reset_observed=True, clock_mid_end_observed=True,
                 actor35_bitwise_untapped_comparison=True, model_pt_reads=0, optimizer_steps=0,
                 skill_evaluation=False, policy_quality_claim=False, action_observer_status='DEFERRED_UNSEALED')
    waited = dict(actual_popen_wait_returned=True, returncode=0, actual_parent_popen_wait_returned=True)
    closure = {k: True for k in ('tap_restored_before_bridge_close', 'original_bridge_close_once',
               'original_env_close_once', 'complete_AppV6_Base_chain', 'actual_app_close_binding_checked',
               'all_own_children_waited', 'original_private_GPU_EX_released', 'original_finite_EX_released')}
    closure.update(app_close_semantics='returned_original_once', canonical_writes=0, foreign_scope_actions=0)
    return final, waited, closure


class RequestTests(unittest.TestCase):
    def test_default_e3_64(self):
        self.assertEqual(validate_source_request(request())['requested_roles'], ['E3'])
    def test_explicit_two_member_128(self):
        value = request(); value.update(requested_roles=['E3', 'W35'], controls=128)
        self.assertEqual(validate_source_request(value)['controls'], 128)
    def test_reject_original_skill_denominators(self):
        for controls in (160, 1600, 0, True):
            with self.subTest(controls=controls), self.assertRaises(ValueError):
                value = request(); value['controls'] = controls; validate_source_request(value)
    def test_reject_other_members_or_order(self):
        for roles in (['W35'], ['E0'], ['W35', 'E3'], ['E3', 'E3']):
            with self.subTest(roles=roles), self.assertRaises(ValueError):
                value = request(); value['requested_roles'] = roles; validate_source_request(value)
    def test_reject_old_purpose(self):
        value = request(); value['purpose'] = 'FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1'
        with self.assertRaises(ValueError): validate_source_request(value)
    def test_reject_physics_change(self):
        value = request(); value['physics_dt'] = .005
        with self.assertRaises(ValueError): validate_source_request(value)
    def test_reject_clean35_claim(self):
        value = request(); value['clean_input_dim'] = 35
        with self.assertRaises(ValueError): validate_source_request(value)
    def test_reject_training_or_quality_claim(self):
        for field in ('training_enabled', 'skill_evaluation', 'policy_quality_claim', 'native_enabled'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                value = request(); value[field] = True; validate_source_request(value)
    def test_reject_action_auto_admission(self):
        value = request(); value['action_observer_status'] = 'PASS'
        with self.assertRaises(ValueError): validate_source_request(value)


class AdapterTests(unittest.TestCase):
    def test_forward_same_instances_and_known_arguments(self):
        env, bridge, api, module, role, pin, session = plumbing()
        args, kwargs = api.calls[0]
        self.assertEqual(args, (env, bridge, module, role, pin))
        self.assertIs(kwargs['recorder'], session.recorder)
        self.assertEqual(session.recorder.bounds, (32, 32, 100000))
    def test_no_added_reset_step_or_getter(self):
        # Fake env intentionally has no reset/step/compute/SDK getter at all.
        self.assertIsNotNone(plumbing()[-1])
    def test_requires_same_env(self):
        env, bridge, api, module, role, pin, _ = plumbing(); bridge.real = object()
        with self.assertRaises(ValueError):
            install_after_first_reset(env, bridge, module, role, pin, request(), sensor_api=api)
    def test_requires_first_reset_initialized(self):
        env, bridge, api, module, role, pin, _ = plumbing(); del env._sensor_mild
        with self.assertRaises(ValueError):
            install_after_first_reset(env, bridge, module, role, pin, request(), sensor_api=api)
    def test_requires_bridge_initial_state(self):
        env, bridge, api, module, role, pin, _ = plumbing(); bridge.initialized = False
        with self.assertRaises(ValueError):
            install_after_first_reset(env, bridge, module, role, pin, request(), sensor_api=api)
    def test_actor_origin_and_return_identity(self):
        session = plumbing()[-1]; actor = Actor()
        self.assertIs(session.observe_actor35(actor, original_policy_buffer=actor, control_index=0), actor)
        self.assertEqual(session.report()['actor35_observations'], 1)
    def test_actor_snapshot_is_copy(self):
        session = plumbing()[-1]; actor = Actor()
        session.observe_actor35(actor, original_policy_buffer=actor, control_index=0)
        actor.values[0][0] = 9
        self.assertEqual(session.recorder.events[0]['payload']['actor35'][0][0], 0)
    def test_reject_substituted_actor(self):
        session = plumbing()[-1]
        with self.assertRaises(ValueError):
            session.observe_actor35(Actor(), original_policy_buffer=Actor(), control_index=0)
    def test_reject_non35_actor(self):
        session = plumbing()[-1]; actor = Actor(); actor.shape = (80, 16)
        with self.assertRaises(ValueError):
            session.observe_actor35(actor, original_policy_buffer=actor, control_index=0)
    def test_reject_noncontiguous_controls(self):
        session = plumbing()[-1]; actor = Actor()
        with self.assertRaises(ValueError):
            session.observe_actor35(actor, original_policy_buffer=actor, control_index=1)
    def test_bounded64_observation_count(self):
        session = plumbing()[-1]; actor = Actor()
        for index in range(65): session.observe_actor35(actor, original_policy_buffer=actor, control_index=index)
        self.assertEqual(session.report()['observed_controls'], 64)
        with self.assertRaises(ValueError):
            session.observe_actor35(actor, original_policy_buffer=actor, control_index=65)
    def test_snapshot_error_preserves_actor(self):
        session = plumbing()[-1]; actor = Actor()
        def broken(value): raise RuntimeError('synthetic snapshot error')
        session.snapshot = broken
        self.assertIs(session.observe_actor35(actor, original_policy_buffer=actor, control_index=0), actor)
        self.assertEqual(session.recorder.capture_errors, 1)
    def test_close_tap_only_once(self):
        _, _, api, _, _, _, session = plumbing(); session.close(); session.close()
        self.assertEqual(api.tap.close_calls, 1)
        self.assertTrue(session.report()['tap_restored'])
    def test_restore_conflict_propagates_not_fake_closed(self):
        session = plumbing()[-1]
        def conflict(): raise RuntimeError('Restore conflict fixture')
        session.tap.close = conflict
        with self.assertRaises(RuntimeError): session.close()
        self.assertFalse(session.closed)
    def test_report_not_native_or_exact(self):
        report = plumbing()[-1].report()
        self.assertFalse(report['native_enabled']); self.assertFalse(report['exact'])
        self.assertFalse(report['capture_interface_passed']); self.assertEqual(report['gate1'], 'UNKNOWN')


class GateTests(unittest.TestCase):
    def evaluate(self, final, waited, closure):
        return validate_waited_capture_evidence(final, waited, closure, role='E3', controls=64)
    def test_fake_schema_does_not_admit_native(self):
        result = self.evaluate(*fake_evidence())
        self.assertTrue(result['schema_consistent']); self.assertFalse(result['capture_interface_passed'])
        self.assertFalse(result['actual_run_attested_here']); self.assertEqual(result['gate1'], 'UNKNOWN')
    def test_rc0_alone_fails(self):
        with self.assertRaises(ValueError): self.evaluate({}, {'returncode': 0}, {})
    def test_old_quality_final_fails(self):
        final, waited, close = fake_evidence(); final.update(kind='ACTUAL_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_PROBE_V1', qualQualityTrue=True)
        with self.assertRaises(ValueError): self.evaluate(final, waited, close)
    def test_missing_real_counts_fail(self):
        for field in ('bridge_controls', 'synthetic_actions', 'physics_ticks_delta', 'fresh_100hz_samples_by_key'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                final, waited, close = fake_evidence(); del final[field]; self.evaluate(final, waited, close)
    def test_missing_real_wait_or_release_fails(self):
        for field in ('actual_popen_wait_returned', 'actual_parent_popen_wait_returned'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                final, waited, close = fake_evidence(); waited[field] = False; self.evaluate(final, waited, close)
        for field in ('complete_AppV6_Base_chain', 'original_env_close_once', 'all_own_children_waited',
                      'original_private_GPU_EX_released', 'original_finite_EX_released'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                final, waited, close = fake_evidence(); close[field] = False; self.evaluate(final, waited, close)
    def test_missing_actual_boundary_or_actor_comparison_fails(self):
        for field in ('terminal_pre_reset_observed', 'partial_reset_observed', 'clock_mid_end_observed',
                      'actor35_bitwise_untapped_comparison', 'original_return_identity_checked'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                final, waited, close = fake_evidence(); final[field] = False; self.evaluate(final, waited, close)


class SourceTests(unittest.TestCase):
    def test_original_full17_source_pins_and_pending_dependencies(self):
        result = audit_source()
        self.assertEqual(len(result['original17_sources']), 17)
        self.assertEqual(result['action_observer_status'], 'DEFERRED_UNSEALED_NO_API_GUESSED')
        self.assertEqual(result['actual_PT_reads'], 0)
    def test_adapter_ast_no_plant_rng_or_native_import(self):
        tree = ast.parse((HERE / 'capture_adapter.py').read_text(encoding='utf-8'))
        forbidden = {'step', 'reset', '_reset_idx', 'compute', 'compute_obs', 'clean_policy',
                     'rand', 'randn', 'randint', 'seed', 'load', 'get_term', 'Popen'}
        calls = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
                 for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, (ast.Attribute, ast.Name))}
        self.assertFalse(calls & forbidden)
        imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imports, {'__future__', 'capture_contract'})
    def test_new_files_ast_parse_only(self):
        for path in HERE.glob('*.py'): ast.parse(path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=2)

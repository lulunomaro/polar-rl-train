"""Stdlib CPU fixtures + subprocess hard-exit simulation + bounded source AST.

No SDK/Torch/native import, checkpoint open, accounting, lock, GO, GPU, training,
or production process is performed. Fake source pins are PRIVATE test patches.
"""
from __future__ import annotations
import ast
from contextlib import contextmanager
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OLD = ROOT / 'source_resume_runtime_v2'
sys.path.insert(0, str(OLD))
sys.path.append(str(ROOT / 'source_app_close_semantics_v5'))
import app_close_semantics_v5 as close
import resume_runtime_contracts_v3 as base
import resume_runtime_app_close_v5 as shim
import _synthetic_app_fixture_v5 as fake
import build_app_close_candidates_v5 as builder

CASES = HERE / 'CPU_SYNTHETIC_CASES_V5'
CASES.mkdir(exist_ok=True)


def fake_pin():
    path = Path(fake.__file__).resolve()
    raw = path.read_bytes()
    return close._AppPin(fake.__name__, 'FakeApp', len(raw), hashlib.sha256(raw).hexdigest(),
                         fake.FakeApp.close.__code__.co_firstlineno)


@contextmanager
def private_fake_policy():
    with mock.patch.object(close, '_APP_PIN', fake_pin()):
        yield


def fixture():
    job = Path(tempfile.mkdtemp(prefix='case_', dir=CASES))
    out = job / 'production'; out.mkdir()
    entry = dict(role='E3', role_key='SYNTHETIC_E3_NO_NATIVE', run_id='CPU_FIXTURE_ONLY',
                 actor_view=base.BASELINE_ACTOR_VIEW, algorithm_variant='A0_FULLCTX_FRESH')
    counts = {key: 0 for key in base.COUNT_FIELDS}
    counts.update(policy_attempts=7, pi_optimizer_steps=5, pi_bptt_optimizer_steps=4,
                  wm_optimizer_steps=11, aux_optimizer_steps=13, critic_optimizer_steps=17)
    checkpoint = dict(path=str(out / 'checkpoints' / 'SYNTHETIC_RECEIPT_ONLY_NO_MODEL_FILE'),
                      bytes=12345, SHA='f' * 64, counts=dict(counts),
                      full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
    final = dict(kind=base.FINAL_KIND, role=entry['role'], role_key=entry['role_key'],
                 run_id=entry['run_id'], actor_view=entry['actor_view'],
                 algorithm_family='a0_fullctx_legacy_v1', passed_execution=True,
                 teacher_unchanged=True, actual_BPTT_policy_steps=4, counts=dict(counts),
                 checkpoint=checkpoint, target_reached=False, skill_graduated=False)
    emit = lambda name, value: write_json(out / name, value)
    emit('FINAL.json', final)
    write_json(job / 'FIXTURE_TASK_ONLY.json', entry)
    return job, out, entry, final, emit


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def hold_own_fixture_file(path):
    source=Path(path).resolve(strict=True)
    target=source.with_name('SYNTHETIC_HELD_' + source.name)
    assert source.is_relative_to(CASES.resolve()) and target.parent == source.parent and not target.exists()
    source.rename(target)
    return target


class Resource:
    def __init__(self, name, log, raises=False):
        self.name, self.log, self.raises, self.calls = name, log, raises, 0

    def close(self):
        self.calls += 1
        self.log.append(self.name)
        if self.raises:
            raise RuntimeError('synthetic ' + self.name + ' close raised')


def close_fixture(*, behavior='return', fast_shutdown=True, bridge_raises=False,
                  env_raises=False, primary_error=None, emit_override=None):
    job, out, entry, final, emit = fixture()
    log = []
    bridge, env = Resource('bridge', log, bridge_raises), Resource('env', log, env_raises)
    app = fake.FakeApp(behavior, fast_shutdown=fast_shutdown, log=log)
    with private_fake_policy():
        receipt = close.close_original_resources(bridge, env, {'app': app}, emit_override or emit,
                    job_root=job, task=entry, primary_error=primary_error)
    return job, out, entry, final, emit, bridge, env, app, log, receipt


def publish_lifecycle(out, entry, receipt):
    write_json(out / 'WORKER_LIFECYCLE_COMPLETE_V3.json', dict(kind=base.LIFECYCLE_KIND,
        role=entry['role'], run_id=entry['run_id'], passed_execution=not receipt['errors'], **receipt))


def evaluate(job, entry, rc=0):
    with private_fake_policy():
        return close.evaluate_waited_worker(job, rc, entry, entry['run_id'])


def child_case(behavior='exit_zero', *, primary_error=None, bridge_raises=False):
    job, out, entry, final, emit = fixture()
    write_json(job / 'FAKE_CHILD_INPUT.json', dict(behavior=behavior, primary_error=primary_error,
                                                bridge_raises=bridge_raises, task=entry))
    # Actual CPU child wait only. Inherit no SDK/harness program, capture no pipes.
    process = subprocess.run([sys.executable, '-S', '-B', str(Path(__file__).resolve()),
                              '--fake-close-child', str(job)],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, timeout=15, check=False)
    return job, out, entry, final, process.returncode


def run_fake_child(job):
    job = Path(job).resolve()
    spec = json.loads((job / 'FAKE_CHILD_INPUT.json').read_bytes())
    out = job / 'production'; task = spec['task']; log = []
    bridge = Resource('bridge', log, spec['bridge_raises'])
    env = Resource('env', log)
    app = fake.FakeApp(spec['behavior'], log=log)
    emit = lambda name, value: write_json(out / name, value)
    with private_fake_policy():
        closure = close.close_original_resources(bridge, env, {'app': app}, emit,
            job_root=job, task=task, primary_error=spec['primary_error'])
    publish_lifecycle(out, task, closure)
    write_json(out / 'AFTER_ORIGINAL_CLOSE_RETURNED_SYNTHETIC.json', {'returned': True})
    return 1 if closure['errors'] else 0


class PinTests(unittest.TestCase):
    def test_production_pin_rejects_fake_without_any_source_override(self):
        with self.assertRaises(close.AppCloseEvidenceError):
            close._pin_original_app_close(fake.FakeApp())

    def test_private_fake_positive_is_not_native(self):
        with private_fake_policy():
            receipt = close._pin_original_app_close(fake.FakeApp())
        self.assertEqual(receipt['actual_class'], '_synthetic_app_fixture_v5.FakeApp')
        self.assertNotEqual(receipt['source_SHA256'], close._APP_PIN.source_SHA256)
        self.assertTrue(receipt['method_self_is_application'])

    def test_subclass_is_not_assumed_same_actual_binding(self):
        class Child(fake.FakeApp):
            pass
        with private_fake_policy(), self.assertRaises(close.AppCloseEvidenceError):
            close._pin_original_app_close(Child())

    def test_config_is_actual_plain_config_not_private_config(self):
        app = fake.FakeApp(); app._config = {'fast_shutdown': False}
        with private_fake_policy():
            self.assertIs(close._pin_original_app_close(app)['fast_shutdown'], True)

    def test_config_descriptor_is_not_executed(self):
        app = fake.FakeApp()
        def bomb(_):
            self.fail('config descriptor executed')
        with private_fake_policy(), mock.patch.object(fake.FakeApp, 'config', property(bomb), create=True):
            with self.assertRaises(close.AppCloseEvidenceError):
                close._pin_original_app_close(app)

    def test_non_exact_config_dict_is_rejected(self):
        class DictSubclass(dict):
            pass
        app = fake.FakeApp(); app.config = DictSubclass(fast_shutdown=True)
        with private_fake_policy(), self.assertRaises(close.AppCloseEvidenceError):
            close._pin_original_app_close(app)

    def test_unknown_or_truthy_nonbool_mode_is_rejected(self):
        for value in (None, 1, 'true', [], {}):
            app = fake.FakeApp(); app.config['fast_shutdown'] = value
            with private_fake_policy(), self.assertRaises(close.AppCloseEvidenceError):
                close._pin_original_app_close(app)

    def test_instance_close_override_is_rejected(self):
        app = fake.FakeApp(); app.close = lambda: None
        with private_fake_policy(), self.assertRaises(close.AppCloseEvidenceError):
            close._pin_original_app_close(app)

    def test_source_sha_bytes_and_AST_line_are_pinned(self):
        for changes in ({'source_SHA256': '0' * 64}, {'source_bytes': 1}, {'close_firstlineno': 1}):
            with mock.patch.object(close, '_APP_PIN', replace(fake_pin(), **changes)):
                with self.assertRaises(close.AppCloseEvidenceError):
                    close._pin_original_app_close(fake.FakeApp())

    def test_missing_module_file_is_fail_closed(self):
        with private_fake_policy(), mock.patch.object(fake, '__file__', None):
            with self.assertRaises(close.AppCloseEvidenceError):
                close._pin_original_app_close(fake.FakeApp())

    def test_real_sdk_source_bytes_match_production_pin_not_imported(self):
        raw = (ROOT / 'discovery/sdk_warp_buffer_appclose_v3/app/exts_0_simulation_app.py').read_bytes()
        self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                         (close._APP_PIN.source_bytes, close._APP_PIN.source_SHA256))
        self.assertNotIn('isaacsim', sys.modules)

    def test_real_source_fast_default_zero_exit_and_immediate_shutdown_are_data_only(self):
        path = ROOT / 'discovery/sdk_warp_buffer_appclose_v3/app/exts_0_simulation_app.py'
        tree = ast.parse(path.read_bytes())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SimulationApp')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'close')
        self.assertEqual(method.lineno, 848)
        self.assertEqual([ast.literal_eval(n) for n in method.args.defaults], [True, False, 0])
        assignment = next(n for n in cls.body if isinstance(n, ast.Assign) and n.targets[0].id == 'DEFAULT_LAUNCHER_CONFIG')
        self.assertIs(ast.literal_eval(assignment.value)['fast_shutdown'], True)
        self.assertIn('quickReleaseFrameworkAndTerminate', path.read_text(encoding='utf-8'))


class CloseTests(unittest.TestCase):
    def test_original_calls_once_order_and_original_config_unchanged(self):
        *_, bridge, env, app, log, receipt = close_fixture()
        self.assertEqual(log, ['bridge', 'env', 'app'])
        self.assertEqual((bridge.calls, env.calls, app.calls), (1, 1, 1))
        self.assertEqual(app.config, {'fast_shutdown': True, 'unchanged_fixture_entry': 17})
        self.assertTrue(receipt['all_original_close_calls_returned'])

    def test_normal_return_keeps_original_post_marker_and_lifecycle_gate(self):
        job, out, entry, _, _, *_, receipt = close_fixture()
        self.assertTrue((out / 'APP_CLOSED.json').exists())
        publish_lifecycle(out, entry, receipt)
        result = evaluate(job, entry)
        self.assertTrue(result['passed_execution']);self.assertIs(result['app_close_returned'], True)
        self.assertFalse(result['accepted_missing_post_app_marker'])

    def test_pinned_fast_intent_has_only_metadata_and_original_counts(self):
        job, out, entry, final, *_ = close_fixture()
        intent = json.loads((out / close.INTENT_NAME).read_bytes())
        self.assertEqual(intent['counts'], final['counts'])
        self.assertEqual(intent['checkpoint']['SHA'], final['checkpoint']['SHA'])
        self.assertEqual(intent['checkpoint']['bytes'], 12345)
        self.assertEqual(intent['checkpoint_bytes_opened'], 0)
        self.assertIsNone(intent['app_close_returned'])
        self.assertFalse(Path(final['checkpoint']['path']).exists())

    def test_known_slow_mode_unchanged_needs_normal_return_marker_not_intent(self):
        job, out, entry, _, _, *_, receipt = close_fixture(fast_shutdown=False)
        self.assertFalse((out / close.INTENT_NAME).exists())
        publish_lifecycle(out, entry, receipt)
        self.assertTrue(evaluate(job, entry)['passed_execution'])

    def test_python_SystemExit_zero_is_error_not_fast_process_nonreturn(self):
        job, out, entry, _, _, *_, receipt = close_fixture(behavior='system_exit_zero')
        self.assertTrue(receipt['errors']);self.assertTrue((out / 'WORKER_ERROR.json').exists())
        self.assertFalse(evaluate(job, entry)['passed_execution'])

    def test_original_app_exception_is_preserved_before_any_success(self):
        job, out, entry, _, _, *_, receipt = close_fixture(behavior='raise')
        self.assertIn('synthetic original App.close raised', json.dumps(receipt))
        self.assertFalse(receipt['records'][-1]['returned'])
        self.assertFalse(evaluate(job, entry)['passed_execution'])

    def test_bridge_error_does_not_skip_env_or_app_and_blocks_intent(self):
        job, out, entry, _, _, bridge, env, app, log, receipt = close_fixture(bridge_raises=True)
        self.assertEqual(log, ['bridge', 'env', 'app'])
        self.assertFalse((out / close.INTENT_NAME).exists())
        self.assertTrue(receipt['errors']);self.assertFalse(evaluate(job, entry)['passed_execution'])

    def test_env_error_does_not_skip_app_and_blocks_intent(self):
        job, out, entry, _, _, *_, receipt = close_fixture(env_raises=True)
        self.assertFalse((out / close.INTENT_NAME).exists())
        self.assertFalse(receipt['records'][1]['returned'])
        self.assertEqual(receipt['records'][2], {'resource': 'app', 'returned': True})

    def test_prior_worker_error_never_becomes_fast_success(self):
        job, out, entry, _, _, *_, receipt = close_fixture(primary_error='PRIMARY_FIXTURE_FAILURE')
        self.assertFalse((out / close.INTENT_NAME).exists())
        self.assertTrue((out / 'WORKER_ERROR.json').exists())
        self.assertFalse(evaluate(job, entry)['passed_execution'])

    def test_unknown_actual_binding_is_durable_failure_before_original_call(self):
        job, out, entry, final, emit = fixture(); log = []
        app = fake.FakeApp(log=log)
        receipt = close.close_original_resources(Resource('bridge', log), Resource('env', log),
                    {'app': app}, emit, job_root=job, task=entry)
        self.assertEqual(app.calls, 1)
        self.assertTrue((out / 'WORKER_ERROR.json').exists())
        self.assertFalse((out / close.INTENT_NAME).exists())
        publish_lifecycle(out, entry, receipt)
        self.assertFalse(evaluate(job, entry)['passed_execution'])

    def test_emit_error_before_App_is_not_lost_to_fast_intent(self):
        def fail_emit(name, value):
            raise OSError('synthetic original emit failure')
        job, out, entry, _, _, *_, receipt = close_fixture(emit_override=fail_emit)
        self.assertFalse((out / close.INTENT_NAME).exists())
        self.assertTrue(receipt['errors']);self.assertFalse(evaluate(job, entry)['passed_execution'])

    def test_fsync_failure_does_not_publish_a_complete_looking_intent(self):
        job, out, entry, _, emit = fixture(); log=[]; app=fake.FakeApp(log=log)
        with private_fake_policy(), mock.patch.object(close.os, 'fsync', side_effect=OSError('fixture fsync failure')):
            receipt = close.close_original_resources(Resource('bridge',log), Resource('env',log), {'app':app},
                        emit, job_root=job, task=entry)
        self.assertFalse((out / close.INTENT_NAME).exists())
        self.assertTrue((out / (close.INTENT_NAME + '.unpublished')).exists())
        self.assertEqual(app.calls, 1)
        self.assertTrue(receipt['errors'])

    def test_fsynced_publication_happens_before_original_app_call(self):
        job, out, entry, _, emit = fixture(); events=[]; app=fake.FakeApp(log=events)
        original_fsync = close.os.fsync
        def observed_fsync(fd):
            events.append('file_fsync');return original_fsync(fd)
        original_replace = close.os.replace
        def observed_replace(src,dst):
            events.append('publish_intent');return original_replace(src,dst)
        with private_fake_policy(), mock.patch.object(close.os,'fsync',observed_fsync), mock.patch.object(close.os,'replace',observed_replace):
            close.close_original_resources(Resource('bridge',events),Resource('env',events),{'app':app},emit,job_root=job,task=entry)
        self.assertLess(events.index('file_fsync'), events.index('publish_intent'))
        self.assertLess(events.index('publish_intent'), events.index('app'))


class ActualCPUHardExitTests(unittest.TestCase):
    def test_fake_hard_exit_zero_has_intent_and_actual_wait_not_return(self):
        job, out, entry, _, rc = child_case('exit_zero')
        self.assertEqual(rc, 0)
        self.assertTrue((out / close.INTENT_NAME).exists())
        self.assertFalse((out / 'APP_CLOSED.json').exists())
        self.assertFalse((out / 'WORKER_LIFECYCLE_COMPLETE_V3.json').exists())
        self.assertFalse((out / 'AFTER_ORIGINAL_CLOSE_RETURNED_SYNTHETIC.json').exists())
        result = evaluate(job, entry, rc)
        self.assertTrue(result['passed_execution'])
        self.assertTrue(result['actual_wait_returned'])
        self.assertTrue(result['app_close_expected_nonreturn'])
        self.assertIsNone(result['app_close_returned'])
        with private_fake_policy():
            old = base.evaluate_waited_worker(job, rc, entry, entry['run_id'])
        self.assertEqual(old['reasons'], ['original_close_completion_missing'])

    def test_fake_hard_exit_nonzero_never_accepted(self):
        job, out, entry, _, rc = child_case('exit_seven')
        self.assertEqual(rc, 7)
        self.assertFalse(evaluate(job, entry, rc)['passed_execution'])

    def test_fake_hard_exit_does_not_hide_prior_worker_error(self):
        job, out, entry, _, rc = child_case('exit_zero', primary_error='FIRST_WORKER_FAILURE')
        self.assertEqual(rc, 0)
        self.assertFalse((out / close.INTENT_NAME).exists())
        self.assertTrue((out / 'WORKER_ERROR.json').exists())
        self.assertFalse(evaluate(job, entry, rc)['passed_execution'])

    def test_fake_hard_exit_does_not_hide_bridge_cleanup_error(self):
        job, out, entry, _, rc = child_case('exit_zero', bridge_raises=True)
        self.assertEqual(rc, 0)
        self.assertFalse((out / close.INTENT_NAME).exists())
        self.assertFalse(evaluate(job, entry, rc)['passed_execution'])

    def test_fake_return_child_keeps_post_marker(self):
        job, out, entry, _, rc = child_case('return')
        self.assertEqual(rc, 0);self.assertTrue((out / 'APP_CLOSED.json').exists())
        result = evaluate(job, entry, rc)
        self.assertTrue(result['passed_execution']);self.assertIs(result['app_close_returned'], True)

    def test_fake_raised_close_child_retains_error_and_nonzero(self):
        job, out, entry, _, rc = child_case('raise')
        self.assertEqual(rc, 1);self.assertTrue((out / 'WORKER_ERROR.json').exists())
        self.assertFalse(evaluate(job, entry, rc)['passed_execution'])


class OwnerGateTests(unittest.TestCase):
    def setUp(self):
        self.job, self.out, self.entry, self.final, self.emit, *_, self.receipt = close_fixture()
        # In these counterexamples we have a valid pre-call intent but deliberately
        # do not publish lifecycle: model only the strict missing-marker branch.
        hold_own_fixture_file(self.out / 'APP_CLOSED.json')

    def result(self, rc=0):
        return evaluate(self.job, self.entry, rc)

    def mutate_intent(self, mutate):
        path = self.out / close.INTENT_NAME
        value = json.loads(path.read_bytes());mutate(value);write_json(path,value)

    def mutate_final(self, mutate):
        value = json.loads((self.out / 'FINAL.json').read_bytes());mutate(value)
        write_json(self.out / 'FINAL.json',value)

    def test_strict_valid_intent_only_replaces_exact_missing_close_reason(self):
        result=self.result();self.assertTrue(result['passed_execution'])
        self.assertEqual(result['original_V4_reasons'],['original_close_completion_missing'])
        self.assertEqual(result['checkpoint_bytes_opened'],0)

    def test_production_pin_rejects_forged_fake_intent_even_with_RC0(self):
        result=close.evaluate_waited_worker(self.job,0,self.entry,self.entry['run_id'])
        self.assertFalse(result['passed_execution'])
        self.assertTrue(any('source_bytes' in r or 'actual_class' in r or 'unpublished actual module' in r for r in result['reasons']))

    def test_invalid_FINAL_is_never_removed(self):
        self.mutate_final(lambda f:f.update(passed_execution=False))
        result=self.result();self.assertFalse(result['passed_execution'])
        self.assertTrue(any(r.startswith('bad_success_FINAL:') for r in result['reasons']))

    def test_mismatched_FINAL_run_role_or_count_stays_failure(self):
        for key,value in [('role','E0'),('run_id','OTHER_RUN'),('actual_BPTT_policy_steps',999)]:
            with self.subTest(key=key):
                original=(self.out/'FINAL.json').read_bytes()
                self.mutate_final(lambda f:f.update({key:value}))
                self.assertFalse(self.result()['passed_execution'])
                (self.out/'FINAL.json').write_bytes(original)

    def test_fullsave_flag_and_checkpoint_receipt_remain_required(self):
        self.mutate_final(lambda f:f['checkpoint'].update(full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=False))
        self.assertFalse(self.result()['passed_execution'])

    def test_changed_FINAL_bytes_even_semantically_same_are_rejected(self):
        with (self.out/'FINAL.json').open('ab') as stream:stream.write(b'\n')
        self.assertFalse(self.result()['passed_execution'])

    def test_unknown_or_wrong_fast_mode_in_receipt_is_rejected(self):
        self.mutate_intent(lambda v:v['binding'].update(fast_shutdown=False))
        self.assertFalse(self.result()['passed_execution'])

    def test_wrong_close_class_SHA_code_line_and_owner_are_rejected(self):
        path=self.out/close.INTENT_NAME;original=path.read_bytes()
        for key,value in [('source_SHA256','0'*64),('source_bytes',1),('close_firstlineno',1),('close_owner','WRONG'),('method_self_is_application',False)]:
            with self.subTest(key=key):
                path.write_bytes(original)
                self.mutate_intent(lambda v:v['binding'].update({key:value}))
                self.assertFalse(self.result()['passed_execution'])
        path.write_bytes(original)

    def test_intent_role_key_run_and_job_are_bound(self):
        path=self.out/close.INTENT_NAME;original=path.read_bytes()
        for key,value in [('role','E0'),('role_key','OTHER'),('run_id','OTHER'),('job_root',str(HERE))]:
            with self.subTest(key=key):
                path.write_bytes(original);self.mutate_intent(lambda v:v.update({key:value}))
                self.assertFalse(self.result()['passed_execution'])
        path.write_bytes(original)

    def test_intent_checkpoint_bytes_SHA_counts_are_bound(self):
        self.mutate_intent(lambda v:v['checkpoint'].update(bytes=12346))
        self.assertFalse(self.result()['passed_execution'])

    def test_prior_two_closes_must_both_return(self):
        self.mutate_intent(lambda v:v['prior_original_closes'][1].update(returned=False))
        self.assertFalse(self.result()['passed_execution'])

    def test_truthy_integer_is_not_prior_close_return_boolean(self):
        self.mutate_intent(lambda v:v['prior_original_closes'][0].update(returned=1))
        self.assertFalse(self.result()['passed_execution'])

    def test_boolean_is_not_an_original_producer_count(self):
        self.mutate_intent(lambda v:v['counts'].update(pi_skipped_zero=False))
        self.assertFalse(self.result()['passed_execution'])

    def test_truthy_integer_is_not_checkpoint_fullsave_boolean(self):
        self.mutate_intent(lambda v:v['checkpoint'].update(full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=1))
        self.assertFalse(self.result()['passed_execution'])

    def test_actual_missing_intent_is_not_RC0_success(self):
        hold_own_fixture_file(self.out/close.INTENT_NAME)
        result=self.result();self.assertFalse(result['passed_execution'])
        self.assertIn('V5_fast_close_intent_missing',result['reasons'])

    def test_new_canonical_worker_error_after_intent_is_never_ignored(self):
        write_json(self.out/'WORKER_ERROR.json',{'error':'NEW_ERROR_AFTER_INTENT'})
        self.assertFalse(self.result()['passed_execution'])

    def test_secondary_error_after_intent_is_never_ignored(self):
        write_json(self.out/'WORKER_ERROR_SECONDARY_123.json',{'error':'NEW_SECONDARY'})
        self.assertFalse(self.result()['passed_execution'])

    def test_new_app_error_sidefile_is_never_ignored(self):
        write_json(self.out/'APP_CLOSE_RUNTIME_ERROR_V5.json',{'error':'NEW_APP_ERROR'})
        self.assertFalse(self.result()['passed_execution'])

    def test_missing_or_malformed_intent_stays_failure(self):
        path=self.out/close.INTENT_NAME
        path.write_bytes(b'{partial')
        self.assertFalse(self.result()['passed_execution'])

    def test_actual_APP_CLOSED_marker_with_missing_lifecycle_not_fast_nonreturn(self):
        write_json(self.out/'APP_CLOSED.json',{'closed':True})
        self.assertFalse(self.result()['passed_execution'])

    def test_malformed_lifecycle_never_replaced_by_intent(self):
        (self.out/'WORKER_LIFECYCLE_COMPLETE_V3.json').write_text('{bad',encoding='utf-8')
        result=self.result();self.assertFalse(result['passed_execution'])
        self.assertIn('original_close_completion_malformed_json',result['reasons'])

    def test_bad_lifecycle_false_return_never_replaced_by_intent(self):
        write_json(self.out/'WORKER_LIFECYCLE_COMPLETE_V3.json',{'kind':base.LIFECYCLE_KIND,'passed_execution':False})
        self.assertFalse(self.result()['passed_execution'])

    def test_missing_FINAL_no_proxy_and_finite_target_false_is_not_rewritten(self):
        self.assertFalse(self.final['target_reached'])
        self.assertTrue(self.result()['passed_execution'])
        hold_own_fixture_file(self.out/'FINAL.json')
        self.assertFalse(self.result()['passed_execution'])

    def test_nonzero_or_bool_returncode_never_accepted(self):
        for rc in (1,7,True,None):
            with self.subTest(rc=rc):self.assertFalse(self.result(rc)['passed_execution'])


class BoundedRecorderTests(unittest.TestCase):
    def test_first_three_last_and_counters_constant_memory(self):
        emitted=[];events=close.BoundedPoseCacheEventsV5(emitted.append,clock=lambda:0.0)
        for i in range(10000):events({'event':'write_returned_and_invalidated','call':i})
        value=events.snapshot()
        self.assertEqual(len(value['first_three']),3)
        self.assertEqual([e['call'] for e in value['first_three']],[0,1,2])
        self.assertEqual(value['last']['call'],9999)
        self.assertEqual(value['events_seen'],10000)
        self.assertEqual(value['event_counts']['write_returned_and_invalidated'],10000)
        self.assertLessEqual(value['retained_event_records'],4)
        self.assertLess(len(emitted),85)
        self.assertLess(max(len(json.dumps(e)) for e in emitted),1600)

    def test_every_128_events_or_20_seconds(self):
        now=[0.0];out=[];events=close.BoundedPoseCacheEventsV5(out.append,clock=lambda:now[0])
        for i in range(3):events({'event':'installed','i':i})
        count=len(out)
        for i in range(127):events({'event':'write_returned_and_invalidated','i':i})
        self.assertEqual(len(out),count)
        events({'event':'write_returned_and_invalidated','i':127})
        self.assertEqual(len(out),count+1)
        now[0]=20.0;events({'event':'write_returned_and_invalidated'})
        self.assertEqual(len(out),count+2)

    def test_error_event_forces_immediate_publication(self):
        out=[];events=close.BoundedPoseCacheEventsV5(out.append,clock=lambda:0.0)
        for _ in range(4):events({'event':'write_returned_and_invalidated'})
        count=len(out)
        events({'event':'adapter_rejected_before_write','error':'FIXTURE'})
        self.assertEqual(len(out),count+1)
        self.assertEqual(out[-1]['last']['event'],'adapter_rejected_before_write')

    def test_unknown_event_no_unbounded_counter_key(self):
        events=close.BoundedPoseCacheEventsV5(lambda v:None)
        with self.assertRaises(close.AppCloseEvidenceError):events({'event':'UNBOUNDED_ARBITRARY_KEY'})
        self.assertEqual(events.snapshot()['events_seen'],0)

    def test_external_event_mutation_does_not_rewrite_stored_first_or_last(self):
        events=close.BoundedPoseCacheEventsV5(lambda v:None)
        event={'event':'installed','nested':{'x':1}};events(event);event['nested']['x']=99
        self.assertEqual(events.snapshot()['last']['nested']['x'],1)

    def test_snapshot_and_emit_consumers_do_not_mutate_recorder_history(self):
        emitted=[];events=close.BoundedPoseCacheEventsV5(emitted.append)
        events({'event':'installed','nested':{'x':1}})
        emitted[-1]['last']['nested']['x']=99
        snapshot=events.snapshot();snapshot['first_three'][0]['nested']['x']=88
        self.assertEqual(events.snapshot()['last']['nested']['x'],1)
        self.assertEqual(events.snapshot()['first_three'][0]['nested']['x'],1)

    def test_nonfinite_metadata_or_clock_is_fail_closed(self):
        events=close.BoundedPoseCacheEventsV5(lambda v:None)
        with self.assertRaises(ValueError):events({'event':'installed','x':float('nan')})
        events=close.BoundedPoseCacheEventsV5(lambda v:None,clock=lambda:float('inf'))
        with self.assertRaises(close.AppCloseEvidenceError):events({'event':'installed'})

    def test_force_final_flush_and_error_persistence_not_mask_primary(self):
        job,out,entry,_,_=fixture()
        events=close.BoundedPoseCacheEventsV5(lambda v:(_ for _ in ()).throw(OSError('fixture emit error')))
        result=close.force_pose_cache_event_receipt_v5(events,out,role=entry['role'])
        self.assertIn('fixture emit error',result)
        self.assertTrue((out/'WORKER_ERROR.json').exists())

    def test_empty_recorder_final_flush_is_bounded(self):
        out=[];events=close.BoundedPoseCacheEventsV5(out.append)
        self.assertIsNone(close.force_pose_cache_event_receipt_v5(events,CASES,role='FIXTURE'))
        self.assertEqual(out[-1]['events_seen'],0)


class SourceASTTests(unittest.TestCase):
    def test_normalized_whole_worker_AST_matches_exact_V4(self):
        new=(HERE/builder.WORKER_NEW).read_text(encoding='utf-8')
        old=(OLD/builder.WORKER_OLD).read_text(encoding='utf-8')
        self.assertEqual(builder.normalized_source(new,undo_worker=True),ast.dump(ast.parse(old),include_attributes=False))

    def test_normalized_whole_both_owners_AST_equal_V4(self):
        for old,new in builder.OWNERS:
            self.assertEqual(builder.normalized_source((HERE/new).read_text(encoding='utf-8'),undo_owner=True),
                             ast.dump(ast.parse((OLD/old).read_text(encoding='utf-8')),include_attributes=False))

    def test_original_cfg_and_before_action_guard_identical(self):
        a=ast.parse((HERE/builder.WORKER_NEW).read_bytes());b=ast.parse((OLD/builder.WORKER_OLD).read_bytes())
        cfg=lambda tree:next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='SuperMimicConfig')
        guard=lambda tree:next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='before_action')
        self.assertEqual(ast.dump(cfg(a)),ast.dump(cfg(b)));self.assertEqual(ast.dump(guard(a)),ast.dump(guard(b)))

    def test_only_one_original_reset_and_original_install_command_bridge_order(self):
        text=(HERE/builder.WORKER_NEW).read_text(encoding='utf-8');tree=ast.parse(text)
        resets=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='env' and n.func.attr=='reset']
        self.assertEqual(len(resets),1)
        self.assertLess(text.index('install_optional_pose_cache_runtime_adapter(env,task,J'),text.index('reset=env.reset()'))
        self.assertLess(text.index('reset=env.reset()'),text.index('bind_original_command_after_fresh_reset(env,role,obs)'))
        self.assertLess(text.index('bind_original_command_after_fresh_reset(env,role,obs)'),text.index('bridge=BridgeClass('))

    def test_owner_actual_wait_precedes_semantic_gate_and_pending_block_preserved(self):
        for _,name in builder.OWNERS:
            text=(HERE/name).read_text(encoding='utf-8')
            self.assertIn('rc=p.wait()',text)
            self.assertLess(text.index('rc=p.wait()'),text.index('semantic=evaluate_waited_worker('))
            self.assertIn("original_error=semantic['original_error']",text)
            tree=ast.parse(text)
            fail_branch=[n for n in ast.walk(tree) if isinstance(n,ast.If)
                         and isinstance(n.test,ast.Subscript) and isinstance(n.test.value,ast.Name)
                         and n.test.value.id=='semantic' and isinstance(n.test.slice,ast.Constant)
                         and n.test.slice.value=='original_error']
            self.assertEqual(len(fail_branch),1)
            self.assertTrue(any(isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant)
                                and n.value.value is True and any(isinstance(t,ast.Name) and t.id=='blocked' for t in n.targets)
                                for statement in fail_branch[0].body for n in ast.walk(statement)))
            self.assertIn('while pending or slots:',text)

    def test_no_new_SDK_or_checkpoint_or_process_call_in_helper_import(self):
        self.assertNotIn('torch',sys.modules)
        self.assertFalse(any(key.startswith(('isaacsim','isaaclab','warp','omni.')) for key in sys.modules))
        tree=ast.parse((HERE/'app_close_semantics_v5.py').read_bytes())
        modules=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        modules += [a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
        self.assertFalse(set(modules)&{'torch','warp','isaacsim','subprocess'})

    def test_original_app_call_zero_args_and_no_config_or_exit_policy_assignment(self):
        tree=ast.parse((HERE/'app_close_semantics_v5.py').read_bytes())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='close_original_resources')
        app_calls=[n for n in ast.walk(function) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='application' and n.func.attr=='close']
        self.assertEqual(len(app_calls),1);self.assertEqual(app_calls[0].args,[]);self.assertEqual(app_calls[0].keywords,[])
        targets=[ast.dump(t) for n in ast.walk(function) if isinstance(n,ast.Assign) for t in n.targets]
        self.assertFalse(any('fast_shutdown' in target or "attr='config'" in target for target in targets))

    def test_shim_reuses_original_resume_installer_variant_and_error_APIs(self):
        import resume_runtime_install_hook_v4 as original
        for name in ('install_optional_pose_cache_runtime_adapter','bind_future_task_extensions','PinnedOwnFullCheckpoint',
                     'load_decoded_full_checkpoint_once','resolve_future_bridge_adapter','validate_worker_variant','preserve_worker_error'):
            self.assertIs(getattr(shim,name),getattr(original,name))
        self.assertIs(shim.evaluate_waited_worker,close.evaluate_waited_worker)

    def test_build_receipt_old_sources_remain_same_bytes(self):
        receipt=json.loads((HERE/'BUILD_APP_CLOSE_CANDIDATES_V5.json').read_bytes())
        for item in receipt['inputs']:
            raw=Path(item['path']).read_bytes()
            self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(item['bytes'],item['SHA256']))
        self.assertEqual(receipt['accounting_lock_deadline_admission_wait_save_learner_physics_changes'],0)


def main():
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(value) for value in list(vars(sys.modules[__name__]).values()) if isinstance(value,type) and issubclass(value,unittest.TestCase) and value.__module__==__name__ and value.__name__!='SourceASTTests')
    start=time.perf_counter();result=unittest.TextTestRunner(verbosity=2).run(suite)
    value=dict(kind='REUSED_V5_BEHAVIORAL_GATES_V6_NEW_SCRATCH_NOT_NATIVE',tests=result.testsRun,
               passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),
               duration_seconds=time.perf_counter()-start,
               actual_CPU_fake_hard_exit_child_tests=6,SDK_imports=0,Torch_imports=0,
               native_app_binding_verified=None,historical_fast_mode_or_exit_cause=None,
               production_checkpoint_bytes_opened=0,account_lock_deadline_GO_or_training_operations=0,
               fake_positive_uses_PRIVATE_OWN_SOURCE_pin_not_SDK_receipt=True)
    write_json(HERE/'CPU_TEST_RESULTS_V5.json',value)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--fake-close-child':
        raise SystemExit(run_fake_child(sys.argv[2]))
    raise SystemExit(main())

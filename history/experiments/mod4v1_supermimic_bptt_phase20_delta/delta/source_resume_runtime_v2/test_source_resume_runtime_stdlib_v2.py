"""Stdlib ONLY: synthetic sidefiles, injected bytes and AST-extracted full loader.
No SDK/Torch import, real checkpoint read, native process, lock or C operation.
Fake models exercise restore control flow, NOT Torch tensor/software restoration.
"""
import ast
import copy
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

from resume_runtime_contracts_v2 import (
    BASELINE_ACTOR_VIEW, FINAL_KIND, LIFECYCLE_KIND, COUNT_FIELDS,
    PinnedOwnFullCheckpoint, bind_future_task_extensions, close_original_resources,
    evaluate_waited_worker, load_decoded_full_checkpoint_once, preserve_worker_error,
    resolve_future_bridge_adapter, validate_full_resume_payload,
    validate_resume_descriptor, validate_bridge_adapter_descriptor,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = Path(tempfile.mkdtemp(prefix='STDLIB_SYNTHETIC_CASES_', dir=HERE))


def move_synthetic_fixture(source, destination):
    source, destination = source.resolve(), destination.resolve()
    assert source.is_relative_to(CASES.resolve()) and destination.is_relative_to(CASES.resolve())
    assert source.is_file() and not destination.exists()
    source.rename(destination)


def counts(n=2520):
    out = dict.fromkeys(COUNT_FIELDS, 0)
    out.update(policy_attempts=n, pi_optimizer_steps=n, pi_bptt_optimizer_steps=n,
               wm_optimizer_steps=10480, aux_optimizer_steps=10480, critic_optimizer_steps=10080)
    return out


def descriptor(raw=b'PURE_SYNTHETIC_BYTES_NOT_A_PT'):
    return dict(kind='OWN_NEW_BPTT_FULL_CHECKPOINT_V2', path='OWN_SYNTHETIC_INPUT_BYTES',
                SHA=hashlib.sha256(raw).hexdigest(), bytes=len(raw), actor_view=BASELINE_ACTOR_VIEW,
                allow_environment_reset=True, allow_partial_update=False, producer_run_id='old-own-run')


@dataclass
class Config:
    horizon: int = 16
    hist: int = 10
    iterations: int = 100000
    ckpt_every: int = 500
    log_every: int = 10
    log_backend: str = 'none'


def full_case():
    contract = dict(schema='mod4v1.ctx_task_reward.v1', num_joints=30, action_dim=6,
                    context_dim=40, obs_dim=119, num_envs=512, policy_dt_s=.02)
    layout = [('actor35_original', 35), ('model_only_synthetic_context', 5)]
    task = dict(role='E0', run_id='new-own-run', num_envs=512, actor_view=BASELINE_ACTOR_VIEW,
                teacher_path='ORIGINAL_DISTINCT_TEACHER_SOURCE', teacher_SHA='b' * 64,
                teacher_bytes=14035411, asset_SHA='c' * 64, contract_SHA='d' * 64,
                original_protocol={'policy_hz': 50, 'full_D0_D7': True}, resume_bptt=descriptor())
    ext = dict(contract=copy.deepcopy(contract), aux={'model': 'aux'}, opt_aux={'optimizer': 'aux'},
               counts=counts(), last_bptt_receipt={'verified_bptt_optimizer_step': True},
               context_predict_mask=[0.] * 40, full_resume=True,
               replay={'T': 128, 'N': 512, 'ptr': 2, 'size': 2,
                       'data': {'term': [False, True], 'trunc': [False, False],
                                'done': [False, True], 'stream_cut': [False, False]}},
               obs_hist=['saved_old_history_not_reused_after_physical_reset'],
               rng={'python': 'synthetic-python-rng', 'torch_cpu': 'synthetic-torch-rng', 'torch_cuda': []},
               collect_fraction=.375, pending_iteration={'phase': 'collect', 'collect_left': 2, 'wm_left': 4},
               environment={'exact': False, 'context_layout': copy.deepcopy(layout)},
               update_boundary_safe=True, resume_scope='learner_full_environment_reset_required')
    payload = dict(args=asdict(Config()), wm={'model': 'wm'}, pi={'model': 'pi'},
                   critic={'model': 'critic'}, opt_wm={'optimizer': 'wm'}, opt_pi={'optimizer': 'pi'},
                   opt_v={'optimizer': 'v'}, iteration=2620, sim_steps=90000, wall_time=3600.,
                   bootstrap_teacher={'source_path': task['teacher_path'], 'source_SHA': task['teacher_SHA'],
                                      'source_bytes': task['teacher_bytes']},
                   role='E0', original_task_protocol=copy.deepcopy(task['original_protocol']),
                   asset_SHA=task['asset_SHA'], contract_SHA=task['contract_SHA'],
                   new_algorithm_not_PPO_resume=True, context_reward_extension=ext)
    return task, contract, layout, payload


def ast_method(path, cls, name):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    return next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == name)


def fake_loader(contract):
    events = []
    source = HERE / 'ctx_reward_full_resume_candidate_v2.py'
    method = copy.deepcopy(ast_method(source, 'ContextRewardLearner', 'load_full_checkpoint'))
    loader_class = ast.ClassDef(name='ExtractedActualFullLoader', bases=[], keywords=[], body=[method], decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[loader_class], type_ignores=[]))
    namespace = dict(asdict=asdict, UpdateCounts=lambda **kw: SimpleNamespace(**kw),
                     restore_rng=lambda value: events.append(('restore_rng', value)))
    exec(compile(module, str(source), 'exec'), namespace)
    learner = namespace['ExtractedActualFullLoader']()
    learner.extension_contract = copy.deepcopy(contract)
    learner.cfg = Config()
    learner.env = SimpleNamespace()
    learner.device = 'synthetic-only'

    class Model:
        def __init__(self, name): self.name = name; self.loaded = None
        def load_state_dict(self, state): self.loaded = state; events.append(('model_or_optimizer', self.name))

    class Buffer:
        def import_state(self, state): self.state = copy.deepcopy(state); events.append(('replay_import', state))
        def seal_stream_boundary(self):
            self.state['data']['stream_cut'][self.state['ptr'] - 1] = True
            events.append(('seal_stream_boundary', None))

    class History:
        def zero_(self): self.zeroed = True; events.append(('fresh_history_zero', None))
        def copy_(self, value): raise AssertionError('saved history crossed declared physical reset')

    for name in ('wm', 'pi', 'critic', 'aux', 'opt_wm', 'opt_pi', 'opt_v', 'opt_aux'):
        setattr(learner, name, Model(name))
    learner.buffer = Buffer()
    learner.obs_hist = History()
    return learner, events


class TerminalGateTests(unittest.TestCase):
    def setUp(self):
        self.job = Path(tempfile.mkdtemp(prefix='job_', dir=CASES))
        self.out = self.job / 'production'; self.out.mkdir()
        self.entry = dict(role='E0', role_key='E0-new')
        self.final = dict(kind=FINAL_KIND, passed_execution=True, role='E0', role_key='E0-new',
                          run_id='new-run', actual_BPTT_policy_steps=10, counts=counts(10),
                          target_reached=False, parent_finite_saved_stop=True, teacher_unchanged=True,
                          checkpoint=dict(SHA='a' * 64, bytes=247000000,
                              path=str(self.out / 'checkpoints' / 'SYNTHETIC_UNOPENED_PATH'),
                              counts=counts(10), full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True))
        self.lifecycle = dict(kind=LIFECYCLE_KIND, passed_execution=True, role='E0', run_id='new-run',
                              all_original_close_calls_returned=True)
        self.write('FINAL.json', self.final)
        self.write('WORKER_LIFECYCLE_COMPLETE_V2.json', self.lifecycle)
    def write(self, name, value):
        (self.out / name).write_text(json.dumps(value), encoding='utf-8')
    def evaluate(self, rc=0): return evaluate_waited_worker(self.job, rc, self.entry, 'new-run')
    def test_finite_saved_success_not_target_or_skill_claim(self):
        result = self.evaluate(); self.assertFalse(result['original_error']); self.assertEqual(result['checkpoint_bytes_opened'], 0)
        self.assertFalse(result['final']['target_reached'])
    def test_rc0_with_worker_error_blocks(self):
        self.write('WORKER_ERROR.json', {'error': 'before learner'}); self.assertTrue(self.evaluate()['original_error'])
    def test_rc0_with_malformed_error_file_still_blocks(self):
        (self.out / 'WORKER_ERROR.json').write_text('{malformed', encoding='utf-8'); self.assertTrue(self.evaluate()['original_error'])
    def test_nonzero_rc_even_success_final_blocks(self): self.assertTrue(self.evaluate(1)['original_error'])
    def test_missing_final_blocks(self):
        # Rename fixture, never touch original source or a checkpoint.
        move_synthetic_fixture(self.out / 'FINAL.json', self.out / 'SYNTHETIC_IGNORED_FINAL.txt'); self.assertTrue(self.evaluate()['original_error'])
    def test_bad_json_final_blocks(self):
        (self.out / 'FINAL.json').write_text('null', encoding='utf-8'); self.assertTrue(self.evaluate()['original_error'])
    def test_execution_false_blocks(self):
        self.final['passed_execution'] = False; self.write('FINAL.json', self.final); self.assertTrue(self.evaluate()['original_error'])
    def test_stale_run_final_blocks(self):
        self.final['run_id'] = 'old-run'; self.write('FINAL.json', self.final); self.assertTrue(self.evaluate()['original_error'])
    def test_wrong_role_blocks(self):
        self.final['role'] = 'E2'; self.write('FINAL.json', self.final); self.assertTrue(self.evaluate()['original_error'])
    def test_null_counter_is_not_inferred_zero(self):
        self.final['counts'] = None; self.write('FINAL.json', self.final); self.assertTrue(self.evaluate()['original_error'])
    def test_count_receipt_mismatch_blocks(self):
        self.final['checkpoint']['counts'] = counts(11); self.write('FINAL.json', self.final); self.assertTrue(self.evaluate()['original_error'])
    def test_actor_only_checkpoint_receipt_blocks(self):
        self.final['checkpoint']['full_new_model_critic_aux_optimizers_replay_RNG_hist_saved'] = False
        self.write('FINAL.json', self.final); self.assertTrue(self.evaluate()['original_error'])
    def test_outside_checkpoint_path_blocks(self):
        self.final['checkpoint']['path'] = str(self.job / 'outside_synthetic_receipt'); self.write('FINAL.json', self.final)
        self.assertTrue(self.evaluate()['original_error'])
    def test_missing_close_receipt_blocks_hard_exit(self):
        move_synthetic_fixture(self.out / 'WORKER_LIFECYCLE_COMPLETE_V2.json', self.out / 'SYNTHETIC_IGNORED_CLOSE.txt')
        self.assertTrue(self.evaluate()['original_error'])
    def test_close_failure_receipt_blocks(self):
        self.lifecycle['all_original_close_calls_returned'] = False; self.write('WORKER_LIFECYCLE_COMPLETE_V2.json', self.lifecycle)
        self.assertTrue(self.evaluate()['original_error'])
    def test_root_fallback_error_blocks(self):
        (self.job / 'WORKER_ERROR_FALLBACK_V2.json').write_text('{}', encoding='utf-8'); self.assertTrue(self.evaluate()['original_error'])


class ByteAndResumeTests(unittest.TestCase):
    def setUp(self): self.task, self.contract, self.layout, self.payload = full_case()
    def test_exactly_one_synthetic_read_hash_decode_and_retention(self):
        calls = []; raw = b'PURE_SYNTHETIC_BYTES_NOT_A_PT'
        def reader(path): calls.append(('read', path)); return raw
        def decoder(stream): calls.append(('decode', stream.read())); return self.payload
        pinned = PinnedOwnFullCheckpoint(descriptor(raw), decoder, read_bytes=reader)
        self.assertIs(pinned.payload, self.payload); self.assertEqual(pinned.raw, raw)
        self.assertEqual([x[0] for x in calls], ['read', 'decode'])
        self.assertEqual([pinned.receipt()[x] for x in ('physical_byte_opens', 'SHA_calculations', 'decodes')], [1, 1, 1])
    def test_wrong_sha_fails_before_decode(self):
        value = descriptor(); value['SHA'] = '0' * 64; calls = []
        with self.assertRaises(ValueError): PinnedOwnFullCheckpoint(value, lambda stream: calls.append('decode'), read_bytes=lambda p: b'PURE_SYNTHETIC_BYTES_NOT_A_PT')
        self.assertEqual(calls, [])
    def test_wrong_size_fails_before_decode(self):
        value = descriptor(); value['bytes'] += 1
        with self.assertRaises(ValueError): PinnedOwnFullCheckpoint(value, lambda stream: self.fail('decode called'), read_bytes=lambda p: b'PURE_SYNTHETIC_BYTES_NOT_A_PT')
    def test_original_full_restore_body_fake_objects_four_models_four_opts(self):
        learner, events = fake_loader(self.contract)
        learner.load_full_checkpoint(self.payload, allow_environment_reset=True, allow_partial_update=False)
        self.assertEqual({value for tag, value in events if tag == 'model_or_optimizer'},
                         {'wm', 'pi', 'critic', 'aux', 'opt_wm', 'opt_pi', 'opt_v', 'opt_aux'})
        self.assertEqual(vars(learner.counts), counts())
        self.assertEqual((learner.iteration, learner.sim_steps, learner.wall_time), (2620, 90000, 3600.))
        self.assertEqual((learner.collect_fraction, learner.pending_iteration), (.375, self.payload['context_reward_extension']['pending_iteration']))
        self.assertTrue(learner.obs_hist.zeroed)
        self.assertEqual(events[-1][0], 'restore_rng')
    def test_reset_stream_cut_does_not_rewrite_original_done_term_timeout(self):
        learner, _ = fake_loader(self.contract); original = copy.deepcopy(self.payload['context_reward_extension']['replay']['data'])
        learner.load_full_checkpoint(self.payload, allow_environment_reset=True)
        for key in ('term', 'done', 'trunc'): self.assertEqual(learner.buffer.state['data'][key], original[key])
        self.assertEqual(learner.buffer.state['data']['stream_cut'], [False, True])
    def test_load_decoded_uses_full_api_no_second_byte_or_decode(self):
        calls = []; raw = b'PURE_SYNTHETIC_BYTES_NOT_A_PT'
        def reader(path): calls.append('read'); return raw
        def decoder(stream): calls.append('decode'); return self.payload
        pinned = PinnedOwnFullCheckpoint(descriptor(raw), decoder, read_bytes=reader)
        learner, _ = fake_loader(self.contract)
        result = load_decoded_full_checkpoint_once(learner, pinned, self.task, self.layout)
        self.assertEqual(calls, ['read', 'decode']); self.assertEqual(result['restored_counts']['pi_bptt_optimizer_steps'], 2520)
        self.assertTrue(result['no_counter_offset_or_fresh_count_splicing'])
    def test_explicit_reset_permission_required(self):
        learner, events = fake_loader(self.contract)
        with self.assertRaises(ValueError): learner.load_full_checkpoint(self.payload)
        self.assertFalse(events)
    def test_unsafe_partial_transaction_not_silently_restarted(self):
        self.payload['context_reward_extension']['update_boundary_safe'] = False
        with self.assertRaises(ValueError): validate_full_resume_payload(self.payload, self.task, self.contract, self.layout)
        learner, events = fake_loader(self.contract)
        with self.assertRaises(ValueError): learner.load_full_checkpoint(self.payload, allow_environment_reset=True)
        self.assertFalse(events)
    def test_algorithmic_config_mismatch_before_state_mutation(self):
        self.payload['args']['horizon'] = 8; learner, events = fake_loader(self.contract)
        with self.assertRaises(ValueError): learner.load_full_checkpoint(self.payload, allow_environment_reset=True)
        self.assertFalse(events)
    def test_missing_each_optimizer_and_model_is_rejected(self):
        for field in ('wm', 'pi', 'critic', 'opt_wm', 'opt_pi', 'opt_v'):
            with self.subTest(field=field):
                value = copy.deepcopy(self.payload); value.pop(field)
                with self.assertRaises(ValueError): validate_full_resume_payload(value, self.task, self.contract, self.layout)
        for field in ('aux', 'opt_aux', 'replay', 'rng', 'obs_hist', 'counts'):
            with self.subTest(field=field):
                value = copy.deepcopy(self.payload); value['context_reward_extension'].pop(field)
                with self.assertRaises(ValueError): validate_full_resume_payload(value, self.task, self.contract, self.layout)
    def test_context_layout_order_mismatch_rejected(self):
        with self.assertRaises(ValueError): validate_full_resume_payload(self.payload, self.task, self.contract, list(reversed(self.layout)))
    def test_raw35_schema_not_baseline_resume(self):
        value = copy.deepcopy(self.contract); value['obs_dim'] = 35
        self.payload['context_reward_extension']['contract'] = value
        with self.assertRaises(ValueError): validate_full_resume_payload(self.payload, self.task, value, self.layout)
    def test_raw35_descriptor_is_separate_fresh_zero_branch(self):
        value = descriptor(); value['actor_view'] = 'raw35'
        with self.assertRaises(ValueError): validate_resume_descriptor(value)
        with self.assertRaises(ValueError): bind_future_task_extensions({}, {'actor_view': 'raw35'})
    def test_different_teacher_or_old_ppo_checkpoint_rejected(self):
        value = copy.deepcopy(self.payload); value['bootstrap_teacher']['source_SHA'] = 'e' * 64
        with self.assertRaises(ValueError): validate_full_resume_payload(value, self.task, self.contract, self.layout)
        with self.assertRaises(ValueError): validate_full_resume_payload({'actor_state_dict': {}}, self.task, self.contract, self.layout)
    def test_same_teacher_and_bptt_source_path_rejected(self):
        self.task['resume_bptt']['path'] = self.task['teacher_path']
        with self.assertRaises(ValueError): validate_full_resume_payload(self.payload, self.task, self.contract, self.layout)
    def test_exact_physx_claim_is_not_accepted_by_fresh_environment_worker(self):
        self.payload['context_reward_extension']['resume_scope'] = 'exact_environment_and_learner'
        with self.assertRaises(ValueError): validate_full_resume_payload(self.payload, self.task, self.contract, self.layout)
    def test_pure_owner_extension_does_not_mutate_old_task_or_entry(self):
        task = {'run_id': 'new'}; entry = {'resume_bptt': descriptor()}
        result = bind_future_task_extensions(task, entry)
        self.assertEqual(task, {'run_id': 'new'}); self.assertIn('resume_bptt', result)
        self.assertIsNot(result['resume_bptt'], entry['resume_bptt'])
    def test_no_adapter_keeps_original_bridge(self):
        value = type('OriginalUnchangedBridge', (), {})
        resolved, receipt = resolve_future_bridge_adapter(value, {}, CASES)
        self.assertIs(resolved, value); self.assertFalse(receipt['adapter_requested'])
    def test_adapter_path_or_interface_escape_rejected(self):
        for bad in ({}, {'module': '../bad'}, {'module': 'owned', 'source_relative': '../owned.py'}):
            with self.assertRaises(ValueError): validate_bridge_adapter_descriptor(bad)


class CloseAndErrorTests(unittest.TestCase):
    def resources(self, bad=None):
        calls = []
        class Resource:
            def __init__(self, name): self.name = name
            def close(self):
                calls.append(self.name)
                if self.name == bad: raise SystemExit(0)
        return calls, Resource('bridge'), Resource('env'), {'app': Resource('app')}
    def test_original_close_once_each(self):
        calls, bridge, env, ns = self.resources(); emitted = []
        result = close_original_resources(bridge, env, ns, lambda name, value: emitted.append(name))
        self.assertEqual(calls, ['bridge', 'env', 'app']); self.assertTrue(result['all_original_close_calls_returned'])
        self.assertEqual(emitted, ['APP_CLOSING.json', 'ENV_CLOSED.json', 'APP_CLOSED.json'])
    def test_bridge_failure_still_closes_env_and_app(self):
        calls, bridge, env, ns = self.resources('bridge')
        result = close_original_resources(bridge, env, ns, lambda *args: None)
        self.assertEqual(calls, ['bridge', 'env', 'app']); self.assertFalse(result['all_original_close_calls_returned'])
    def test_app_systemexit_zero_is_preserved_as_failure(self):
        calls, bridge, env, ns = self.resources('app')
        result = close_original_resources(bridge, env, ns, lambda *args: None)
        self.assertFalse(result['all_original_close_calls_returned']); self.assertIn('SystemExit: 0', result['errors'][0]['error'])
    def test_sidefile_io_failure_never_skips_original_close(self):
        calls, bridge, env, ns = self.resources()
        def fail(*args): raise OSError('synthetic write failure')
        result = close_original_resources(bridge, env, ns, fail)
        self.assertEqual(calls, ['bridge', 'env', 'app']); self.assertFalse(result['all_original_close_calls_returned'])
    def test_primary_error_never_overwritten_by_close_error(self):
        out = Path(tempfile.mkdtemp(prefix='errors_', dir=CASES))
        first = preserve_worker_error(out, role='E3', error='ORIGINAL_GUARD_FAILURE', phase='startup')
        second = preserve_worker_error(out, role='E3', error='CLOSE_FAILURE', phase='close')
        self.assertNotEqual(first['path'], second['path'])
        self.assertEqual(json.loads((out / 'WORKER_ERROR.json').read_text())['error'], 'ORIGINAL_GUARD_FAILURE')
        self.assertEqual(json.loads(Path(second['path']).read_text())['error'], 'CLOSE_FAILURE')
    def test_prestart_output_absent_uses_root_fallback(self):
        root = Path(tempfile.mkdtemp(prefix='fallback_', dir=CASES))
        receipt = preserve_worker_error(root / 'production_absent', role='E3', error='PRESTART_FAILURE', phase='entry')
        self.assertTrue(receipt['persisted']); self.assertEqual(Path(receipt['path']), root / 'WORKER_ERROR_FALLBACK_V2.json')


class SourceProtectionTests(unittest.TestCase):
    def test_core_all_old_methods_except_load_ast_identical(self):
        old = ast.parse((ROOT / 'source_core_review/ctx_reward_learner.py').read_text(encoding='utf-8'))
        new = ast.parse((HERE / 'ctx_reward_full_resume_candidate_v2.py').read_text(encoding='utf-8'))
        def methods(tree):
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ContextRewardLearner')
            return {n.name: ast.dump(n, include_attributes=False) for n in cls.body if isinstance(n, ast.FunctionDef)}
        a, b = methods(old), methods(new)
        self.assertEqual([k for k in a if a[k] != b[k]], ['load'])
    def test_full_loader_body_is_original_load_body_without_decode(self):
        old = ast_method(ROOT / 'source_core_review/ctx_reward_learner.py', 'ContextRewardLearner', 'load')
        new = ast_method(HERE / 'ctx_reward_full_resume_candidate_v2.py', 'ContextRewardLearner', 'load_full_checkpoint')
        self.assertEqual([ast.dump(n, include_attributes=False) for n in old.body[1:]],
                         [ast.dump(n, include_attributes=False) for n in new.body])
    def test_original_owners_all_nonmain_functions_and_globals_identical(self):
        for oldname, newname in (
            ('supermimic_original_owner.py', 'supermimic_original_owner_resume_candidate_v2.py'),
            ('supermimic_original_owner_shared_v2.py', 'supermimic_original_owner_shared_resume_candidate_v2.py')):
            a = ast.parse((ROOT / 'source_runtime' / oldname).read_text(encoding='utf-8'))
            b = ast.parse((HERE / newname).read_text(encoding='utf-8'))
            for node in a.body:
                if isinstance(node, ast.FunctionDef) and node.name != 'main':
                    other = next(n for n in b.body if isinstance(n, ast.FunctionDef) and n.name == node.name)
                    self.assertEqual(ast.dump(node, include_attributes=False), ast.dump(other, include_attributes=False))
            self.assertEqual([ast.dump(n, include_attributes=False) for n in a.body if isinstance(n, ast.Assign)],
                             [ast.dump(n, include_attributes=False) for n in b.body if isinstance(n, ast.Assign)])
    def test_success_gate_runs_after_wait_before_pending_launch(self):
        text = (HERE / 'supermimic_original_owner_resume_candidate_v2.py').read_text(encoding='utf-8')
        main = text[text.index('def main():'):]
        self.assertLess(main.index('rc=p.wait()'), main.index('semantic=evaluate_waited_worker'))
        self.assertLess(main.index("if semantic['original_error']"), main.index('for u in UUIDS:'))
        self.assertIn('if u in slots or blocked or not pending:continue', main)
    def test_worker_one_original_reset_binder_before_bridge_and_first_action(self):
        tree = ast.parse((HERE / 'worker_supermimic_bptt_resume_candidate_v2.py').read_text(encoding='utf-8'))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        resets = [n for n in calls if ast.unparse(n.func) == 'env.reset']
        bind = next(n for n in calls if ast.unparse(n.func) == 'bind_original_command_after_fresh_reset')
        bridge = next(n for n in calls if ast.unparse(n.func) == 'bridge.init_state')
        train = next(n for n in calls if ast.unparse(n.func) == 'learner.train')
        self.assertEqual(len(resets), 1); self.assertLess(resets[0].lineno, bind.lineno)
        self.assertLess(bind.lineno, bridge.lineno); self.assertLess(bridge.lineno, train.lineno)
    def test_original_finite_beforeaction_condition_unchanged(self):
        def condition(path):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'before_action')
            return ast.dump(function.body[0].test, include_attributes=False)
        self.assertEqual(condition(ROOT / 'source_runtime/worker_supermimic_bptt.py'),
                         condition(HERE / 'worker_supermimic_bptt_resume_candidate_v2.py'))
    def test_teacher_actual_state_buffers_value_comparison_after_load(self):
        tree = ast.parse((HERE / 'worker_supermimic_bptt_resume_candidate_v2.py').read_text(encoding='utf-8'))
        method = copy.deepcopy(next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'assert_teacher_actor_unchanged'))
        current = {'weight': (1, 2), 'running_buffer': (3, 4)}
        actor = SimpleNamespace(state_dict=lambda: current, parameters=lambda: [SimpleNamespace(requires_grad=False)])
        namespace = dict(actor=actor, actor_snapshot=copy.deepcopy(current),
                         teacher=SimpleNamespace(assert_frozen=lambda: None), torch=SimpleNamespace(equal=lambda a, b: a == b))
        exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), '<EXTRACTED_ACTUAL_ACTOR_VALUE_GUARD>', 'exec'), namespace)
        namespace['assert_teacher_actor_unchanged']()
        current['running_buffer'] = (9, 9)
        with self.assertRaises(AssertionError): namespace['assert_teacher_actor_unchanged']()
    def test_no_path_load_called_by_candidate_worker(self):
        text = (HERE / 'worker_supermimic_bptt_resume_candidate_v2.py').read_text(encoding='utf-8')
        self.assertNotIn('learner.load(', text); self.assertNotIn('learner.train(resume=', text)
        self.assertIn('load_decoded_full_checkpoint_once', text)
    def test_no_torch_or_sdk_imported(self):
        self.assertNotIn('torch', sys.modules)
        self.assertFalse(any(name.startswith(('isaaclab', 'isaacsim', 'omni')) for name in sys.modules))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = dict(kind='STDLIB_AST_AND_SYNTHETIC_OBJECT_CONTRACT_TESTS_NOT_TORCH_OR_NATIVE',
                   tests_run=result.testsRun, passed=result.wasSuccessful(), failures=len(result.failures),
                   errors=len(result.errors), fixture_root=str(CASES), Torch_imported='torch' in sys.modules,
                   real_checkpoint_bytes_opened=0, SDK_imports=0, GPU_operations=0, native_runs=0,
                   training_updates=0, original_account_C_lock_operations=0,
                   interpretation='Actual source loader body with fake model/optimizer objects; not real Torch restore proof')
    with (HERE / 'TEST_RESULTS_STDLIB_RESUME_V2.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=2); stream.write('\n')
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)

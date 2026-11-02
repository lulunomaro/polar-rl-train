"""Only stdlib fake tensors/metadata and source AST. NOT Torch/SDK/frozen evaluation."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import ast
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import time
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

R = load('a1_frozen_eval_runtime_stdlib_fixture', HERE / 'a1_frozen_eval_runtime_v2.py')
B = load('a1_frozen_eval_builder_stdlib_fixture', HERE / 'build_frozen_eval_candidates_v2.py')
FIXTURES = Path(tempfile.mkdtemp(prefix='STDLIB_FAKE_EVAL_CASES_', dir=HERE))

def newdir(prefix='case_'):
    return Path(tempfile.mkdtemp(prefix=prefix, dir=FIXTURES))

def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, allow_nan=False)
    return path.read_bytes()

def shape(value):
    return (len(value),) + shape(value[0]) if isinstance(value, list) and value else ()

class FakeArray:
    def __init__(self, values, dtype='bool', device='FAKE_CPU'):
        self.values = copy.deepcopy(values); self.dtype = dtype; self.device = device
        self.shape = shape(values)
    def clone(self):
        return FakeArray(self.values, self.dtype, self.device)
    def __or__(self, other):
        return FakeArray([a or b for a, b in zip(self.values, other.values)], self.dtype, self.device)
    def __getitem__(self, index):
        if isinstance(index, tuple):
            rows, cols = index
            return FakeArray([row[cols] for row in self.values[rows]], self.dtype, self.device)
        result = self.values[index]
        return FakeArray(result, self.dtype, self.device) if isinstance(result, list) else result
    def __sub__(self, other):
        return FakeArray([[a-b for a, b in zip(x, y)] for x, y in zip(self.values, other.values)], self.dtype, self.device)
    def abs(self):
        return FakeArray([[abs(x) for x in row] for row in self.values], self.dtype, self.device)
    def max(self):
        return max(max(row) for row in self.values)

class FakeTorch:
    bool = 'bool'
    def ones(self, n, *, dtype, device):
        return FakeArray([True] * n, dtype, device)
    def is_tensor(self, value):
        return isinstance(value, FakeArray)
    def clamp(self, value, low, high):
        return FakeArray([[max(low, min(high, x)) for x in row] for row in value.values], value.dtype, value.device)

T = FakeTorch()

def flags(*indices, dtype='bool', device='FAKE_CPU', n=80):
    return FakeArray([i in indices for i in range(n)], dtype, device)

def matrix(n=35):
    return FakeArray([[0.] * n for _ in range(80)], 'float32')

class FakeMean:
    def __init__(self):
        self.t = T; self.device = 'FAKE_CPU'; self.pi = object(); self.calls = 0; self.observed = []
        self.source_bindings = {'rsl_rl.models.MLPModel': dict(R.APPROVED_RSL_MODEL_SOURCE)}
    def act(self, raw, *, episode_start):
        assert raw.shape == (80, 35)
        self.observed.append((raw, list(episode_start.values))); self.calls += 1
        return matrix(6)
    def assert_frozen(self):
        return True
    def receipt(self):
        return dict(actor_calls=self.calls, actor_frozen=True, normalization_updates=0, optimizer_updates=0)

class FakeFullCache:
    constructed = []
    def __init__(self, final, **kwargs):
        self.t = T; self.final = final; self.kwargs = kwargs; self.SHA = final['checkpoint']['SHA']
        self.built = 0; self.checked = 0; self.mean = FakeMean(); self.constructed.append(self)
    def build_mean_policy(self, device, num_envs=80):
        assert device == 'FAKE_CPU' and num_envs == 80
        self.built += 1; return self.mean
    def assert_unchanged(self):
        self.checked += 1; return True
    def receipt(self):
        cp = self.final['checkpoint']
        return dict(source_path=cp['path'], source_SHA=cp['SHA'], source_bytes=cp['bytes'],
                    physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1,
                    whole_root_CPU_unchanged=True, mother_checkpoint_opens=0,
                    replay_or_saved_history_sliced_or_restored=False,
                    live_optimizer_WM_critic_replay_created=False,
                    fixture_only_stub_receipt_not_actual_checkpoint_IO=True)

def paired():
    protocol = dict(pose_source_SHA=R.POSE_PIN[1], pose_source_bytes=R.POSE_PIN[0],
                    pose_source_version=R.POSE_VERSION, install_timing=R.POSE_TIMING,
                    seed=20260928, num_envs=80, explicit_original_reset_count=1,
                    physics_dt=.0025, control_dt=.02, feedback_hz=100,
                    actor_observation='original_noisy_delayed_policy35')
    return dict(kind='PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2', reference_planned_protocol=copy.deepcopy(protocol),
                candidate_planned_protocol=copy.deepcopy(protocol), historical_bug_baseline_reused=False,
                reference_actual_receipt=None)

def producer(role='E3'):
    job = newdir('SYNTHETIC_PRODUCER_METADATA_ONLY_'); (job / 'production').mkdir()
    c = dict.fromkeys(R.COUNT_FIELDS, 0)
    c.update(policy_attempts=3, pi_optimizer_steps=3, pi_bptt_optimizer_steps=3,
             wm_optimizer_steps=20, aux_optimizer_steps=20, critic_optimizer_steps=3)
    # No checkpoint file is created, opened, stat'ed or hashed. This is only JSON metadata.
    cp = dict(path=str(job / 'production' / 'checkpoints' / 'SYNTHETIC_NOT_A_MODEL_complete.pt'),
              SHA='b' * 64, bytes=1234, iteration=3, counts=dict(c), teacher_unchanged=True,
              full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
    final = dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', role=role, role_key='SYNTHETIC_' + role,
                 run_id='SYNTHETIC_PRODUCER_RUN', passed_execution=True, teacher_unchanged=True,
                 actor_view='raw35_legacy_held_aux_v1', algorithm_family='a1_raw35_legacy_v1',
                 algorithm_variant='A1_RAW35_FRESH', counts=c, actual_BPTT_policy_steps=3, checkpoint=cp)
    final_path = job / 'production' / 'FINAL.json'; raw = write_json(final_path, final)
    return dict(own_job_root=str(job), FINAL_path=str(final_path), FINAL=final, role_key=final['role_key'],
                run_id=final['run_id'], FINAL_bytes=len(raw), FINAL_SHA=hashlib.sha256(raw).hexdigest())

def task_fixture(role='E3'):
    group = newdir('SYNTHETIC_GROUP_'); case = group / role; case.mkdir()
    entry = dict(role=role, controls=R.CONTROLS[role], a1_producer=producer(role),
                 source_path='OLD_REFERENCE_METADATA_ONLY_NOT_OPENED.pt', source_SHA='c' * 64, source_bytes=999)
    plan = dict(group_id='SYNTHETIC_GROUP_ID', GPU_UUID='SYNTHETIC_GPU_UUID', asset_SHA=R.USD, contract_SHA=R.CONTRACT,
                paired_reset_protocol=paired(), approved_RSL_model_source=dict(R.APPROVED_RSL_MODEL_SOURCE))
    task = R.make_task(entry, plan, time.time() + 1000, [51, 52])
    return task, group, case, dict(entry, paired_reset_protocol=plan['paired_reset_protocol'])

APP_SOURCE = (HERE.parent / 'source_app_close_runtime_compat_v6' / 'app_close_semantics_v6.py').resolve()

def app_binding(fast=True, module='simulation_app.simulation_app'):
    name = module + '.SimulationApp'; source = str(FIXTURES / 'SYNTHETIC_NOT_SDK_simulation_app.py')
    return dict(kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5', actual_class=name, actual_MRO=[name, 'builtins.object'],
                close_owner=name, actual_module=module, actual_type_name='SimulationApp', close_module=module,
                close_qualname='SimulationApp.close', source_SHA256='6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903',
                source_bytes=48933, close_firstlineno=848, exact_class_verified=True, method_self_is_application=True,
                method_function_is_MRO_definition=True, fast_shutdown=fast, no_extra_SDK_getters=True,
                source_code_version='V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES', helper_source_file=str(APP_SOURCE),
                helper_source_bytes=R.APP_PIN[0], helper_source_SHA256=R.APP_PIN[1], source_file=source,
                module_file=source, code_filename=source, fixture_only_not_runtime_class_evidence=True)

def fake_app_helper():
    def validate(binding):
        assert binding['fast_shutdown'] is True
        other = dict(binding, fast_shutdown=False)
        R._validate_returned_app_binding(other, SimpleNamespace(__file__=str(APP_SOURCE)))
        return binding
    return SimpleNamespace(__file__=str(APP_SOURCE), _validate_binding_receipt=validate,
                           _pin_original_app_close=lambda app: app_binding(app.fast))

class FakeEnv:
    def __init__(self, fail=False):
        self.calls = 0; self.fail = fail
    def close(self):
        self.calls += 1
        if self.fail: raise RuntimeError('SYNTHETIC_ENV_CLOSE_ERROR')

class FakeApp:
    def __init__(self, *, fast=True, error=None):
        self.fast = fast; self.error = error; self.calls = 0
    def close(self):
        self.calls += 1
        if self.error is not None: raise self.error


def semantic_fixture(*, fast=True, returned=True):
    task, group, case, entry = task_fixture()
    cp = task['a1_producer']['FINAL']['checkpoint']
    source = dict(source_path=cp['path'], source_SHA=cp['SHA'], source_bytes=cp['bytes'],
                  admitted_producer_run_id=task['a1_producer']['run_id'], actual_BPTT_policy_steps=3,
                  approved_RSL_model_source=dict(R.APPROVED_RSL_MODEL_SOURCE),
                  approved_reference_provenance=dict(R.APPROVED_REFERENCE_PROVENANCE),
                  actual_eval_RSL_source_binding=dict(R.APPROVED_RSL_MODEL_SOURCE),
                  physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1, mother_checkpoint_opens=0,
                  whole_root_CPU_unchanged=True, replay_or_saved_history_sliced_or_restored=False,
                  live_optimizer_WM_critic_replay_created=False,
                  frozen_mean=dict(actor_frozen=True, actor_calls=task['controls'], normalization_updates=0, optimizer_updates=0,
                    paired_reset_protocol=dict(candidate_pose_installed=True, protocol=R.validate_paired_protocol(task['paired_reset_protocol'])),
                    original_episode_boundary=dict(actions=task['controls'], original_step_transitions=task['controls'], pending_original_step=False)))
    final = dict(kind='SYNTHETIC_EVAL_NOT_RUNTIME', integration=R.INTEGRATION, role=task['role'], group_id=task['group_id'],
                 passed_execution=True, num_envs=80, controls=task['controls'], source_cache=source)
    raw = write_json(case / 'FINAL.json', final)
    write_json(case / 'PRE_CLOSE.json', dict(fixture_only=True))
    write_json(case / 'ENV_CLOSE_RETURNED_A1_EVAL_V2.json', dict(closed=True))
    binding = app_binding(fast)
    if returned:
        write_json(case / 'APP_CLOSE_RETURNED_A1_EVAL_V2.json', dict(returned=True, binding=binding))
    else:
        write_json(case / 'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json', dict(kind='PINNED_A1_EVAL_FAST_CLOSE_INTENT_V2',
            role=task['role'], group_id=task['group_id'], final_SHA=hashlib.sha256(raw).hexdigest(), final_bytes=len(raw),
            original_env_close_returned=True, publication='FSYNC_ATOMIC_METADATA_BEFORE_ORIGINAL_APP_CLOSE', binding=binding))
    return task, case, entry, final

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        R.CONTEXT.clear(); FakeFullCache.constructed.clear()
    def gate(self, case, entry, rc=0):
        with mock.patch.object(R, '_pinned_module', return_value=fake_app_helper()):
            return R.evaluate_waited_eval_case(case, rc, entry, 'SYNTHETIC_GROUP_ID')
    def test_01_import_is_stdlib_only(self):
        self.assertNotIn('torch', sys.modules); self.assertNotIn('isaaclab', sys.modules)
    def test_02_four_actual_source_pins_and_compile(self):
        for key in B.PINS:
            source = B.read_pinned(key); ast.parse(source)
        for p in HERE.glob('*.py'):
            compile(p.read_text(encoding='utf-8'), str(p), 'exec')
    def test_03_three_sealed_dependencies_unchanged(self):
        sources = [(HERE.parent / 'source_eval_a1_raw35_v1' / 'frozen_a1_raw35_v1.py', R.HELPER_PIN),
                   (HERE.parent / 'source_native_v6_runtime_compat' / 'pose_cache_runtime_adapter_v4.py', R.POSE_PIN),
                   (APP_SOURCE, R.APP_PIN)]
        for path, pin in sources:
            raw = path.read_bytes(); self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), pin)
    def test_04_builder_replays_only_new_fixture_outputs_exact(self):
        directory = newdir('BUILDER_SOURCE_COPY_NOT_STAGE_')
        with mock.patch.object(B, 'HERE', directory), contextlib.redirect_stdout(io.StringIO()):
            B.main()
        for name in ('worker_formal_a1_frozen_candidate_v2.py', 'e1_parallel_worker_a1_frozen_candidate_v2.py',
                     'e1_fresh_bridge_a1_frozen_candidate_v2.py', 'single_gpu_eight_a1_frozen_parent_candidate_v2.py'):
            self.assertEqual((HERE / name).read_bytes(), (directory / name).read_bytes())
    def test_05_parent_original_admission_and_cleanup_unchanged(self):
        original = B.read_pinned('parent'); candidate = (HERE / 'single_gpu_eight_a1_frozen_parent_candidate_v2.py').read_text(encoding='utf-8')
        start = 'class BusyResource(Exception):pass\n'; end = 'deadline=time.time()+2400\n'
        self.assertEqual(original.split(start)[1].split(end)[0], candidate.split(start)[1].split(end)[0])
        for text in (original, candidate):
            outer = next(x for x in B.node(text, 'main').body if isinstance(x, ast.Try))
            if text is original: saved = B.body_source(text, outer.finalbody)
            else: self.assertEqual(saved, B.body_source(text, outer.finalbody))
    def test_06_parent_wait_then_semantic_and_eight_no_H1(self):
        source = (HERE / 'single_gpu_eight_a1_frozen_parent_candidate_v2.py').read_text(encoding='utf-8')
        self.assertLess(source.index('rc=p.wait();'), source.index('semantic=evaluate_waited_eval_case'))
        self.assertIn("{r['role']for r in roles}==set(ROLES)", source)
        self.assertEqual(len(R.ROLES), 8); self.assertNotIn('H1_normal', R.ROLES)
    def test_07_e1_original_full_control_loop_AST_identical(self):
        old = B.node(B.read_pinned('e1'), '_run_loop')
        new = B.node((HERE / 'e1_parallel_worker_a1_frozen_candidate_v2.py').read_text(encoding='utf-8'), '_run_loop')
        for a, b in zip([n for n in ast.walk(old) if isinstance(n, ast.With)], [n for n in ast.walk(new) if isinstance(n, ast.With)]):
            self.assertEqual(B.dump(a), B.dump(b))
        self.assertEqual(len([n for n in ast.walk(old) if isinstance(n, ast.With)]), 1)
    def test_08_e1_geometry_DR_and_fresh_audit_AST_identical(self):
        a = B.read_pinned('e1'); b = (HERE / 'e1_parallel_worker_a1_frozen_candidate_v2.py').read_text(encoding='utf-8')
        for name in ('_configure_environment', 'build_slope50_training_axis_factory'):
            self.assertEqual(B.dump(B.node(a, name)), B.dump(B.node(b, name)))
        a = B.read_pinned('bridge'); b = (HERE / 'e1_fresh_bridge_a1_frozen_candidate_v2.py').read_text(encoding='utf-8')
        self.assertEqual(B.dump(B.node(a, 'fresh_full_dr_audit')), B.dump(B.node(b, 'fresh_full_dr_audit')))
        new_attach = B.node(b, 'attach_fresh_guard'); old_attach = B.node(a, 'attach_fresh_guard')
        self.assertEqual([B.dump(x) for x in new_attach.body[1:]], [B.dump(x) for x in old_attach.body])
    def test_09_no_old_actor_loader_in_new_bridge(self):
        text = (HERE / 'e1_fresh_bridge_a1_frozen_candidate_v2.py').read_text(encoding='utf-8')
        for denied in ('MLPModel', 'load_state_dict(', 'class A0NoResetDecisionVec'):
            self.assertNotIn(denied, text)
        self.assertIn('return build_a1_original_vec', text)
    def test_10_formal_single_reset_then_original_step_true_flags(self):
        text = (HERE / 'worker_formal_a1_frozen_candidate_v2.py').read_text(encoding='utf-8')
        self.assertEqual(text.count('env.reset()'), 1)
        self.assertLess(text.index('install_paired_pose_before_original_reset(env);'), text.index('env.reset()'))
        self.assertIn('env.step(applied);actor.observe_transition(ter,tru);completed+=1;', text)
        self.assertIn('wholeOwnA1N1024CPUrootretained', text)
    def test_11_paired_protocol_exact_planned_match(self):
        self.assertEqual(R.validate_paired_protocol(paired())['num_envs'], 80)
        value = paired(); value['reference_planned_protocol']['pose_source_SHA'] = '0' * 64
        with self.assertRaises(R.IntegrationError): R.validate_paired_protocol(value)
    def test_12_old_bug_baseline_not_paired(self):
        value = paired(); value['historical_bug_baseline_reused'] = True
        with self.assertRaises(R.IntegrationError): R.validate_paired_protocol(value)
    def test_13_declared_reference_is_not_actual_pair_proof(self):
        task, group, case, _ = task_fixture(); task['paired_reset_protocol']['reference_actual_receipt'] = dict(
            protocol=R.validate_paired_protocol(paired()), passed_execution=True, eval_id='DECLARED_NOT_VERIFIED')
        R.configure_candidate_runtime(task, case); receipt = R.paired_protocol_receipt()
        self.assertTrue(receipt['declared_reference_protocol_matches'])
        for key in ('reference_receipt_verification', 'actual_reference_same_protocol', 'UID_alignment', 'raw_reference_cache_match', 'reward_effect_identification'):
            self.assertIsNone(receipt[key])
    def test_14_make_all_eight_original_scopes_observer_source_A1(self):
        for role in R.ROLES:
            task, group, case, _ = task_fixture(role); seen = []
            self.assertTrue(R.validate_group_task(task, role, group, case, environment={'CUDA_VISIBLE_DEVICES': 'SYNTHETIC_GPU_UUID'}, fd_check=seen.append))
            self.assertEqual(seen, [51, 52]); self.assertEqual(task['controls'], R.CONTROLS[role])
            self.assertEqual(task['source_SHA'], task['a1_producer']['FINAL']['checkpoint']['SHA'])
    def test_15_reject_scope_drift_without_touching_resources(self):
        task, group, case, _ = task_fixture()
        for key, value in [('num_envs', 1024), ('seed', 1), ('closure_m', .02), ('controls', 161), ('state_projection_or_slicing', True), ('source_SHA', 'c'*64)]:
            wrong = dict(task, **{key: value})
            with self.assertRaises(R.IntegrationError):
                R.validate_group_task(wrong, 'E3', group, case, environment={'CUDA_VISIBLE_DEVICES': 'SYNTHETIC_GPU_UUID'}, fd_check=lambda fd: None)
    def test_16_source_descriptor_requires_success_A1_whole_nine(self):
        base = producer()
        for field, value in [('passed_execution', False), ('actor_view', 'baseline_fullctx_v1'), ('actual_BPTT_policy_steps', 99)]:
            bad = copy.deepcopy(base); bad['FINAL'][field] = value
            with self.assertRaises(R.IntegrationError): R._producer_descriptor(bad, 'E3')
        bad = copy.deepcopy(base); bad['FINAL']['counts'].pop('wm_optimizer_steps')
        with self.assertRaises(R.IntegrationError): R._producer_descriptor(bad, 'E3')
    def test_17_actual_FINAL_bytes_required(self):
        task, _, _, _ = task_fixture(); self.assertEqual(R._read_actual_final(task), task['a1_producer']['FINAL'])
        task['a1_producer']['FINAL_SHA'] = '0' * 64
        with self.assertRaises(R.IntegrationError): R._read_actual_final(task)
    def test_18_boundary_first_true_then_previous_true_flags_not_cumulative(self):
        b = R.OriginalEpisodeBoundary(T, 'FAKE_CPU'); self.assertEqual(b.for_action().values, [True] * 80)
        b.after_original_step(flags(1), flags(3)); value = b.for_action()
        self.assertEqual([i for i, v in enumerate(value.values) if v], [1, 3])
        b.after_original_step(flags(), flags()); self.assertFalse(any(b.for_action().values))
    def test_19_boundary_rejects_missing_step_and_flag_layout(self):
        b = R.OriginalEpisodeBoundary(T, 'FAKE_CPU'); b.for_action()
        with self.assertRaises(R.IntegrationError): b.for_action()
        for bad in (flags(n=79), flags(dtype='float32'), flags(device='OTHER')):
            with self.assertRaises(R.IntegrationError): b.after_original_step(bad, flags())
    def test_20_policy_only_original_raw_no_privileged_input(self):
        mean = FakeMean(); caller = R.A1PolicyCaller(mean); raw = matrix()
        caller(dict(policy=raw, critic=object(), UID=object(), DR=object()))
        self.assertIs(mean.observed[0][0], raw); caller.observe_transition(flags(), flags())
        with self.assertRaises(R.IntegrationError): caller(dict(policy=raw), stochastic_output=True)
    def test_21_cache_adapter_delegates_once_no_real_checkpoint_open(self):
        task, _, _, _ = task_fixture(); fake = SimpleNamespace(FrozenA1CheckpointCache=FakeFullCache)
        with mock.patch.object(R, '_pinned_module', return_value=fake):
            cache = R.A1CheckpointAdapter(T, task)
        self.assertEqual(len(FakeFullCache.constructed), 1)
        caller = cache.actor('FAKE_CPU'); self.assertIs(caller.mean, cache.cache.mean)
        self.assertEqual(cache.cache.built, 1); self.assertTrue(cache.check_actor(caller.mean.pi))
        with self.assertRaises(R.IntegrationError): cache.actor('FAKE_CPU')
        with self.assertRaises(R.IntegrationError): cache.check_actor(object())
    def test_22_RSL_source_dependency_not_architecture_fallback(self):
        task, _, _, _ = task_fixture(); task['approved_RSL_model_source'] = None
        with mock.patch.object(R, '_pinned_module', return_value=SimpleNamespace(FrozenA1CheckpointCache=FakeFullCache)):
            cache = R.A1CheckpointAdapter(T, task)
        with self.assertRaises(R.IntegrationError): cache.actor('FAKE_CPU')
    def test_23_vec_original_compute_step_clamp_true_boundary(self):
        mean = FakeMean(); caller = R.A1PolicyCaller(mean); counts = dict(compute=0, step=0)
        raw, critic = matrix(), matrix(38)
        def compute(): counts['compute'] += 1; return dict(policy=raw, critic=critic)
        def step(action):
            counts['step'] += 1; self.assertEqual(action.values[0][:2], [6., -6.])
            return dict(), 0., flags(4), flags(5), dict()
        env = SimpleNamespace(num_envs=80, device='FAKE_CPU', observation_manager=SimpleNamespace(compute=compute),
              command_manager=SimpleNamespace(get_term=lambda name: SimpleNamespace(command=matrix(3))), step=step)
        cache = SimpleNamespace(actor=lambda device: caller)
        td = lambda values, batch_size: values
        vec = R.OriginalA1NoResetDecisionVec(env, cache, T, td, lambda x: x)
        observed = vec.get_observations(); self.assertEqual(list(observed), ['policy']); vec.policy(observed)
        action = FakeArray([[9., -9., 0., 0., 0., 0.]] * 80, 'float32')
        result = vec.step(action); self.assertEqual([i for i, x in enumerate(result[2].values) if x], [4, 5])
        self.assertEqual(counts, dict(compute=1, step=1)); self.assertEqual(vec.audit()['extra_explicit_env_resets'], 0)
    def test_24_pose_hook_once_bounded_events_no_getters(self):
        task, _, case, _ = task_fixture(); R.configure_candidate_runtime(task, case); robot = object(); calls = []
        def install(actual, *, receipt_callback):
            self.assertIs(actual, robot); calls.append(actual)
            for i in range(7): receipt_callback(dict(event='installed' if i == 0 else 'write_returned', synthetic_index=i))
            return object()
        with mock.patch.object(R, '_pinned_module', return_value=SimpleNamespace(install_pose_cache_runtime_adapter_v3=install)):
            R.install_paired_pose_before_original_reset(SimpleNamespace(scene={'robot': robot}))
            with self.assertRaises(R.IntegrationError): R.install_paired_pose_before_original_reset(SimpleNamespace(scene={'robot': robot}))
        saved, _ = R._metadata(case / 'PAIRED_POSE_CACHE_EVENTS_V2.json')
        self.assertEqual(len(saved['first']), 3); self.assertEqual(saved['counters']['write_returned'], 6); self.assertEqual(len(calls), 1)
    def test_25_primary_preserved_with_secondary_and_bad_cache_receipt(self):
        _, _, case, _ = task_fixture()
        bad = SimpleNamespace(receipt=lambda: (_ for _ in ()).throw(RuntimeError('SYNTHETIC_CACHE_RECEIPT')))
        R.record_primary_error(case, role='E3', phase='FIRST', error='PRIMARY', cache=bad)
        R.record_primary_error(case, role='E3', phase='SECOND', error='SECONDARY')
        first, _ = R._metadata(case / 'WORKER_ERROR.json')
        self.assertEqual(first['error'], 'PRIMARY'); self.assertIn('source_cache_error', first)
        self.assertEqual(len(list(case.glob('WORKER_ERROR_SECONDARY_*.json'))), 1)
    def test_26_original_close_env_and_App_once(self):
        task, _, case, _ = task_fixture(); write_json(case / 'FINAL.json', dict(passed_execution=True, integration=R.INTEGRATION))
        env, app = FakeEnv(), FakeApp()
        with mock.patch.object(R, '_pinned_module', return_value=fake_app_helper()):
            self.assertEqual(R.close_original_eval_resources(env, app, case, task), [])
        self.assertEqual((env.calls, app.calls), (1, 1)); self.assertTrue((case / 'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json').exists())
    def test_27_close_error_durable_and_still_calls_App(self):
        task, _, case, _ = task_fixture(); env, app = FakeEnv(fail=True), FakeApp()
        with mock.patch.object(R, '_pinned_module', return_value=fake_app_helper()):
            self.assertTrue(R.close_original_eval_resources(env, app, case, task))
        self.assertEqual((env.calls, app.calls), (1, 1)); self.assertTrue((case / 'WORKER_ERROR.json').exists())
    def test_28_SystemExit_zero_is_durable_error_not_hardexit_proof(self):
        task, _, case, _ = task_fixture(); app = FakeApp(error=SystemExit(0))
        with mock.patch.object(R, '_pinned_module', return_value=fake_app_helper()):
            self.assertTrue(R.close_original_eval_resources(FakeEnv(), app, case, task))
        self.assertTrue((case / 'WORKER_ERROR.json').exists()); self.assertEqual(app.calls, 1)
    def test_29_fast_intent_metadata_requires_actual_wait_caller(self):
        task, case, entry, final = semantic_fixture(returned=False)
        result = self.gate(case, entry)
        self.assertTrue(result['passed_execution']); self.assertTrue(result['original_fast_close_expected_nonreturn_accepted'])
        self.assertIn('CALLER_ORIGINAL_P_WAIT_REQUIRED', result['actual_resource_admission_or_parent_wait_proof'])
    def test_30_returned_nonfast_strict_same_source(self):
        task, case, entry, final = semantic_fixture(fast=False, returned=True)
        self.assertTrue(self.gate(case, entry)['passed_execution'])
        binding = app_binding(False); binding['actual_module'] = 'ARBITRARY.SUBCLASS'
        with self.assertRaises(R.IntegrationError): R._validate_returned_app_binding(binding, fake_app_helper())
    def test_31_nonfast_intent_alone_fails(self):
        task, case, entry, final = semantic_fixture(fast=False, returned=False)
        self.assertFalse(self.gate(case, entry)['passed_execution'])
    def test_32_RC_zero_error_presence_fails_even_bad_JSON(self):
        task, case, entry, final = semantic_fixture(); (case / 'WORKER_ERROR.json').write_text('MALFORMED_SYNTHETIC', encoding='utf-8')
        self.assertFalse(self.gate(case, entry)['passed_execution'])
    def test_33_nonzero_RC_never_success(self):
        task, case, entry, final = semantic_fixture(); self.assertFalse(self.gate(case, entry, rc=1)['passed_execution'])
    def test_34_stale_final_hash_fast_intent_fails(self):
        task, case, entry, final = semantic_fixture(returned=False)
        with (case / 'FINAL.json').open('a', encoding='utf-8') as stream: stream.write(' ')
        self.assertFalse(self.gate(case, entry)['passed_execution'])
    def test_35_semantic_cache_and_counter_corruption_fails(self):
        for key, value in [('physical_byte_opens', 2), ('CPU_decodes', True), ('mother_checkpoint_opens', 1),
                           ('whole_root_CPU_unchanged', False), ('source_SHA', '0'*64), ('replay_or_saved_history_sliced_or_restored', True)]:
            task, case, entry, final = semantic_fixture(); final['source_cache'][key] = value
            R.put_json(case / 'FINAL.json', final)
            self.assertFalse(self.gate(case, entry)['passed_execution'], key)
    def test_36_missing_N80_and_incomplete_actor_controls_fail(self):
        task, case, entry, final = semantic_fixture(); final.pop('num_envs'); R.put_json(case / 'FINAL.json', final)
        self.assertFalse(self.gate(case, entry)['passed_execution'])
        task, case, entry, final = semantic_fixture(); final['source_cache']['frozen_mean']['actor_calls'] -= 1
        R.put_json(case / 'FINAL.json', final); self.assertFalse(self.gate(case, entry)['passed_execution'])
    def test_37_no_actual_pair_improvement_in_semantic_result(self):
        task, case, entry, final = semantic_fixture(); result = self.gate(case, entry)
        for key in ('UID_alignment', 'reference_cache_match', 'paired_reward_effect'): self.assertIsNone(result[key])
    def test_38_pin_verified_before_source_import(self):
        text = (HERE / 'a1_frozen_eval_runtime_v2.py').read_text(encoding='utf-8'); func = ast.get_source_segment(text, B.node(text, '_pinned_module'))
        self.assertLess(func.index('hashlib.sha256(raw)'), func.index('module = importlib.import_module'))
    def test_39_frozen_helper_one_decode_and_no_live_restore_AST(self):
        text = (HERE.parent / 'source_eval_a1_raw35_v1' / 'frozen_a1_raw35_v1.py').read_text(encoding='utf-8')
        module = ast.parse(text); cls = next(x for x in module.body if isinstance(x, ast.ClassDef) and x.name == 'FrozenA1CheckpointCache')
        ctor = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == '__init__')
        src = ast.get_source_segment(text, ctor)
        self.assertEqual(src.count('self.path.read_bytes()'), 1); self.assertEqual(src.count('_decode_cpu('), 1)
        self.assertLess(text.index('pi = modules.Wrapper('), text.index('pi.load_state_dict(')); self.assertLess(text.index('pi.load_state_dict('), text.index('pi.to(device)'))
        self.assertNotIn('load_full_checkpoint(', text)
    def test_40_errors_before_optional_E1_partial_output_and_close(self):
        text = (HERE / 'e1_parallel_worker_a1_frozen_candidate_v2.py').read_text(encoding='utf-8')
        start = text.index('error=dict(kind=KIND')
        self.assertLess(text.index('record_primary_error(', start), text.index('np.savez_compressed(', start))
        self.assertLess(text.index('record_primary_error(', start), text.index('close_original_eval_resources(', start))

    def test_41_parent_CPU_reference_report_is_not_native_GPU_proof(self):
        path = HERE.parent / 'reports' / 'A1_FROZEN_MEAN_POLICY_CPU_V1.json'
        report, raw = R._metadata(path)
        self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (8696, R.APPROVED_REFERENCE_PROVENANCE['report_SHA256']))
        receipt = report['receipt']; binding = receipt['source_bindings']['rsl_rl.models.MLPModel']
        self.assertTrue(receipt['passed']); self.assertEqual(receipt['CPU_mean_controls'], 4)
        self.assertEqual(receipt['max_reference_error'], 0.0)
        for key, value in R.APPROVED_RSL_MODEL_SOURCE.items(): self.assertEqual(binding[key], value)
        self.assertIsNone(receipt['actual_frozen_evaluation'])
        self.assertIsNone(R.APPROVED_REFERENCE_PROVENANCE['original_native_GPU_source_binding_observed'])
    def test_42_actual_evaluator_class_diff_fails_before_any_action(self):
        task, _, _, _ = task_fixture()
        with mock.patch.object(R, '_pinned_module', return_value=SimpleNamespace(FrozenA1CheckpointCache=FakeFullCache)):
            cache = R.A1CheckpointAdapter(T, task)
        cache.cache.mean.source_bindings['rsl_rl.models.MLPModel']['module'] = 'SYNTHETIC_WRONG_CLASS'
        with self.assertRaises(R.IntegrationError): cache.actor('FAKE_CPU')
        self.assertEqual(cache.cache.mean.calls, 0); self.assertIsNone(cache.caller)
    def test_43_provenance_does_not_promote_CPU_to_native_or_human_approval(self):
        task, _, _, _ = task_fixture()
        self.assertIn('not_a_new_human_approval', task['approved_reference_provenance']['selected_by'])
        task['approved_reference_provenance'] = dict(task['approved_reference_provenance'], original_native_GPU_source_binding_observed=True)
        with self.assertRaises(R.IntegrationError): R._validate_approved_reference(task)
    def test_44_semantic_actual_source_diff_fails(self):
        task, case, entry, final = semantic_fixture()
        final['source_cache']['actual_eval_RSL_source_binding']['SHA256'] = '0' * 64
        R.put_json(case / 'FINAL.json', final); self.assertFalse(self.gate(case, entry)['passed_execution'])
    def test_45_absent_plan_selection_uses_explicit_parent_agent_selected_reference(self):
        task, _, _, entry = task_fixture()
        plan = dict(group_id=task['group_id'], GPU_UUID=task['GPU_UUID'], asset_SHA=R.USD,
                    contract_SHA=R.CONTRACT, paired_reset_protocol=paired())
        fresh = R.make_task(entry, plan, time.time()+1000, [51, 52])
        self.assertEqual(fresh['approved_RSL_model_source'], R.APPROVED_RSL_MODEL_SOURCE)
        self.assertEqual(fresh['approved_reference_provenance'], R.APPROVED_REFERENCE_PROVENANCE)


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    started = time.monotonic(); result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrationTests))
    receipt = dict(kind='STDLIB_FAKE_TENSOR_METADATA_AND_PINNED_SOURCE_AST_NOT_TORCH_OR_EVAL', passed=result.wasSuccessful(),
                   tests_run=result.testsRun, seconds=time.monotonic()-started,
                   failures=[dict(test=str(t), traceback=text) for t, text in result.failures],
                   errors=[dict(test=str(t), traceback=text) for t, text in result.errors], fixture_root=str(FIXTURES),
                   Torch_imported='torch' in sys.modules, original_model_PT_raw_JSONL_NPZ_C_SDK_GPU_SSH_Git_operations=0,
                   actual_frozen_evaluation_runs=0, actual_cache_IO_or_actor_math_verified=False,
                   actual_parent_wait_or_resource_admission_verified=False)
    with args.output.open('x', encoding='utf-8') as stream: json.dump(receipt, stream, indent=2, allow_nan=False)
    print(json.dumps(receipt, indent=2)); return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    raise SystemExit(main())

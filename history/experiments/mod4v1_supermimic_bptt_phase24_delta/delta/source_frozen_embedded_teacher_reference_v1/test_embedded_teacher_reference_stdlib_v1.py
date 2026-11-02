"""New SOURCE/fake tests only. No Torch/SDK/model/data imports or reads."""
import ast
import argparse
import contextlib
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import embedded_teacher_reference_v1 as h

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / 'source_a1_frozen_eval_integration_v2' / 'a1_frozen_eval_runtime_v2.py'
spec = importlib.util.spec_from_file_location('own_test_original_boundary_source', CORE)
core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)  # stdlib-only original module.


class Tensor:
    def __init__(self, shape, values=None, dtype='float32', device='cpu'):
        self.shape, self.dtype, self.device = tuple(shape), dtype, device
        n = 1
        for v in shape: n *= v
        self.values = list(values if values is not None else [0.] * n)
    def all(self): return all(self.values)
    def detach(self): return self
    def to(self, device):
        if device != self.device: raise AssertionError('fake tensors must stay CPU')
        return self
    def clone(self): return Tensor(self.shape, self.values, self.dtype, self.device)
    def clamp(self, lo, hi): return Tensor(self.shape, [x if x != x else max(lo, min(hi, x)) for x in self.values], self.dtype, self.device)
    def __or__(self, other): return Tensor(self.shape, [a or b for a, b in zip(self.values, other.values)], 'bool')


class Torch:
    float32, bool = 'float32', 'bool'
    @staticmethod
    def is_tensor(v): return isinstance(v, Tensor)
    @staticmethod
    def isfinite(v): return Tensor(v.shape, [abs(x) != float('inf') and x == x for x in v.values], 'bool')
    @staticmethod
    def equal(a, b): return a.shape == b.shape and a.dtype == b.dtype and a.values == b.values
    @staticmethod
    def inference_mode(): return contextlib.nullcontext()
    @staticmethod
    def ones(n, dtype, device): return Tensor((n,), [True] * n, dtype, device)


class TD(dict):
    def __init__(self, value, batch_size):
        super().__init__(value); self.batch_size = batch_size


class Teacher:
    def __init__(self):
        self.weights = {'linear.weight': Tensor((6, 35)), 'distribution.std_param': Tensor((), [1.])}
        self.buffers = {'obs_norm.mean': Tensor((35,)), 'obs_norm.var': Tensor((35,), [1.] * 35),
                        'obs_norm.count': Tensor((), [23.])}
        self.calls = 0; self.last_raw = None; self.last_stochastic = None
        self.output_shape = (80, 6); self.output_nan = False
    def state_dict(self): return dict(self.weights, **self.buffers)
    def named_parameters(self): return self.weights.items()
    def named_buffers(self): return self.buffers.items()
    def __call__(self, td, stochastic_output):
        self.calls += 1; self.last_raw = td['policy']; self.last_stochastic = stochastic_output
        values = [float('nan') if self.output_nan else (12. if j == 0 else -9. if j == 1 else .25) for _ in range(80) for j in range(6)]
        return Tensor(self.output_shape, values)


def snapshot_state(values): return {k: (v.shape, v.dtype, tuple(v.values)) for k, v in values.items()}


class Mean:
    def __init__(self):
        self.t, self.device, self.num_envs = Torch, 'cpu', 80
        self.calls = 0; self._history = None; self._failed = False; self.bad = False; self.guard_calls = 0
        self.pi = NS(teacher=Teacher(), residual=NS(forward_calls=0))
        teacher = dict(source_path='/OWN_FAKE_NOT_OPENED/teacher.pt', source_SHA='b' * 64, source_bytes=123, teacher_frozen=True)
        raw = b'OWN_FAKE_FULL_A1_NOT_A_MODEL_FILE'
        state = {'teacher.' + k: v.clone() for k, v in self.pi.teacher.state_dict().items()}
        state['residual.unused'] = Tensor((1,), [.7])
        root = dict(role='E3', role_key='OWN_FAKE_ROLE', run_id='OWN_FAKE_RUN', bootstrap_teacher=teacher, pi=state)
        self.cache = NS(root=root, raw=raw, SHA=hashlib.sha256(raw).hexdigest(),
                        expected={k: root[k] for k in ('role', 'role_key', 'run_id')})
        self.cache.receipt = lambda: dict(source_SHA=self.cache.SHA, source_bytes=len(raw),
            physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1, mother_checkpoint_opens=0,
            whole_root_CPU_unchanged=True)
        self.source_bindings = {h.RSL_BINDING_KEY: dict(h.APPROVED_RSL, path='/FAKE_CPU_SOURCE.py')}
        self.original_teacher = self.pi.teacher
        self.live = snapshot_state(self.pi.teacher.state_dict()); self.saved = snapshot_state(state)
        self.final = dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', passed_execution=True, teacher_unchanged=True,
            **self.cache.expected, teacher=copy.deepcopy(teacher),
            checkpoint=dict(SHA=self.cache.SHA, bytes=len(raw), teacher_unchanged=True, teacher_source=copy.deepcopy(teacher)))
    def assert_frozen(self):
        self.guard_calls += 1
        h.need(not self.bad and self.pi.teacher is self.original_teacher
               and snapshot_state(self.pi.teacher.state_dict()) == self.live
               and snapshot_state(self.cache.root['pi']) == self.saved, 'fake whole root/live snapshot changed')
        return True


def evidence(mean):
    value = dict(kind=h.FREEZE_EVIDENCE_KIND, **mean.cache.expected, source_A1_SHA=mean.cache.SHA,
                 actual_staged_worker_source=dict(path='/OWN_FAKE_WORKER.py', bytes=10, SHA256='c' * 64))
    value.update({k: True for k in ('parent_verified_actual_staged_source', 'state_dict_snapshot_all_parameters_and_buffers',
                 'torch_equal_before_each_complete_save', 'torch_equal_before_success_FINAL',
                 'producer_success_FINAL_and_checkpoint_teacher_unchanged')})
    return value


def raw(): return Tensor((80, 35))
def mask(fresh=True): return Tensor((80,), [fresh] * 80, 'bool')


class Tests(unittest.TestCase):
    def setUp(self):
        self.mean = Mean()
        self.binding = patch.object(h, '_actual_model_source', return_value=dict(h.APPROVED_RSL, path='/FAKE_CPU_SOURCE.py'))
        self.binding.start(); self.addCleanup(self.binding.stop)
    def build(self, **kw):
        opts = dict(tensor_dict_cls=TD, producer_final=self.mean.final, producer_freeze_evidence=evidence(self.mean))
        opts.update(kw)
        return h.EmbeddedTeacherMeanReference(self.mean, **opts)
    def run_one(self):
        ref = self.build(); boundary = core.OriginalEpisodeBoundary(Torch, 'cpu')
        caller = h.EmbeddedTeacherReferenceCaller(ref, boundary=boundary)
        caller({'policy': raw()}); caller.observe_transition(mask(False), mask(False))
        return ref, caller
    def validate(self, receipt, **kw):
        opts = dict(expected_role='E3', expected_source_sha=self.mean.cache.SHA, expected_bootstrap_teacher_sha='b' * 64, expected_actor_calls=1)
        opts.update(kw)
        return h.validate_reference_semantics(receipt, **opts)
    def test_direct_original_raw_teacher_clip(self):
        ref = self.build(); value = raw(); action = ref.act(value, episode_start=mask())
        self.assertIs(ref.teacher.last_raw, value); self.assertIs(ref.teacher.last_stochastic, False)
        self.assertEqual(action.values[:6], [6., -6., .25, .25, .25, .25])
        self.assertEqual(self.mean.calls, 0); self.assertEqual(self.mean.pi.residual.forward_calls, 0)
    def test_keeps_all_original_guards(self):
        ref = self.build(); before = self.mean.guard_calls; ref.act(raw(), episode_start=mask()); ref.receipt()
        self.assertGreaterEqual(self.mean.guard_calls - before, 3)
    def test_norm_std_and_all_buffers_manifest(self):
        receipt = self.build().receipt(); names = {x['name'] for x in receipt['full_teacher_state_manifest']}
        self.assertEqual(names, set(self.mean.pi.teacher.state_dict()))
        self.assertIn('distribution.std_param', names); self.assertIn('obs_norm.count', names)
    def test_no_evidence_stays_unknown_and_not_qualified(self):
        ref = self.build(producer_freeze_evidence=None)
        receipt = ref.receipt(); self.assertIsNone(receipt['producer_teacher_weights_buffers_guard_verified'])
        with self.assertRaises(ValueError): self.validate(receipt)
    def test_prior_candidate_call_rejected(self):
        self.mean.calls = 1
        with self.assertRaises(ValueError): self.build()
    def test_prior_candidate_history_rejected(self):
        self.mean._history = object()
        with self.assertRaises(ValueError): self.build()
    def test_n80_exact(self):
        self.mean.num_envs = 1024
        with self.assertRaises(ValueError): self.build()
    def test_false_first_mask_sticky(self):
        ref = self.build()
        with self.assertRaises(ValueError): ref.act(raw(), episode_start=mask(False))
        self.assertTrue(ref._failed)
        with self.assertRaises(ValueError): ref.act(raw(), episode_start=mask())
    def test_bad_input_shape(self):
        with self.assertRaises(ValueError): self.build().act(Tensor((80, 36)), episode_start=mask())
    def test_bad_input_dtype(self):
        value = raw(); value.dtype = 'float64'
        with self.assertRaises(ValueError): self.build().act(value, episode_start=mask())
    def test_bad_input_nan(self):
        value = raw(); value.values[0] = float('nan')
        with self.assertRaises(ValueError): self.build().act(value, episode_start=mask())
    def test_bad_mask_dtype(self):
        value = mask(); value.dtype = 'float32'
        with self.assertRaises(ValueError): self.build().act(raw(), episode_start=value)
    def test_bad_mask_shape(self):
        with self.assertRaises(ValueError): self.build().act(raw(), episode_start=Tensor((81,), dtype='bool'))
    def test_bad_action_shape(self):
        ref = self.build(); ref.teacher.output_shape = (80, 7)
        with self.assertRaises(ValueError): ref.act(raw(), episode_start=mask())
    def test_bad_action_nan(self):
        ref = self.build(); ref.teacher.output_nan = True
        with self.assertRaises(ValueError): ref.act(raw(), episode_start=mask())
    def test_actual_rsl_SHA_mismatch(self):
        with patch.object(h, '_actual_model_source', return_value=dict(h.APPROVED_RSL, SHA256='d' * 64)):
            with self.assertRaises(ValueError): self.build()
    def test_actual_rsl_class_mismatch(self):
        with patch.object(h, '_actual_model_source', return_value=dict(h.APPROVED_RSL, qualname='Different')):
            with self.assertRaises(ValueError): self.build()
    def test_declared_rsl_source_mismatch(self):
        self.mean.source_bindings[h.RSL_BINDING_KEY]['bytes'] += 1
        with self.assertRaises(ValueError): self.build()
    def test_expected_source_no_fallback(self):
        with self.assertRaises(ValueError): self.build(expected_rsl_source=dict(h.APPROVED_RSL, bytes=1))
    def test_live_teacher_norm_mutation(self):
        ref = self.build(); ref.teacher.buffers['obs_norm.mean'].values[0] += 1
        with self.assertRaises(ValueError): ref.act(raw(), episode_start=mask())
    def test_live_teacher_std_mutation(self):
        ref = self.build(); ref.teacher.weights['distribution.std_param'].values[0] += 1
        with self.assertRaises(ValueError): ref.act(raw(), episode_start=mask())
    def test_cached_root_mutation(self):
        ref = self.build(); self.mean.cache.root['pi']['residual.unused'].values[0] += 1
        with self.assertRaises(ValueError): ref.act(raw(), episode_start=mask())
    def test_teacher_rebound(self):
        ref = self.build(); self.mean.pi.teacher = Teacher()
        with self.assertRaises(ValueError): ref.act(raw(), episode_start=mask())
    def test_full_teacher_key_gap(self):
        del self.mean.cache.root['pi']['teacher.obs_norm.count']
        self.mean.saved = snapshot_state(self.mean.cache.root['pi'])
        with self.assertRaises(ValueError): self.build()
    def test_teacher_shape_gap(self):
        self.mean.cache.root['pi']['teacher.obs_norm.count'].shape = (1,)
        self.mean.saved = snapshot_state(self.mean.cache.root['pi'])
        with self.assertRaises(ValueError): self.build()
    def test_teacher_value_gap(self):
        self.mean.cache.root['pi']['teacher.obs_norm.count'].values[0] += 1
        self.mean.saved = snapshot_state(self.mean.cache.root['pi'])
        with self.assertRaises(ValueError): self.build()
    def test_producer_role_gap(self):
        self.mean.final['role'] = 'W35'
        with self.assertRaises(ValueError): self.build()
    def test_bootstrap_source_gap(self):
        self.mean.final['teacher']['source_SHA'] = 'e' * 64
        with self.assertRaises(ValueError): self.build()
    def test_freeze_evidence_false(self):
        value = evidence(self.mean); value['state_dict_snapshot_all_parameters_and_buffers'] = False
        with self.assertRaises(ValueError): self.build(producer_freeze_evidence=value)
    def test_freeze_evidence_different_A1(self):
        value = evidence(self.mean); value['source_A1_SHA'] = 'e' * 64
        with self.assertRaises(ValueError): self.build(producer_freeze_evidence=value)
    def test_source_and_bootstrap_hash_separate(self):
        receipt = self.build().receipt()
        self.assertNotEqual(receipt['source_A1_SHA'], receipt['original_bootstrap_teacher']['source_SHA'])
        self.assertIsNone(receipt['independent_original_mother_PT_equivalence'])
    def test_boundary_positive_and_semantics(self):
        _, caller = self.run_one(); result = self.validate(caller.receipt())
        self.assertTrue(result['passed_reference_policy_semantics']); self.assertIsNone(result['qualified_reference_execution'])
    def test_original_boundary_blocks_missing_step(self):
        ref = self.build(); caller = h.EmbeddedTeacherReferenceCaller(ref, boundary=core.OriginalEpisodeBoundary(Torch, 'cpu'))
        caller({'policy': raw()})
        with self.assertRaises(ValueError): caller({'policy': raw()})
        with self.assertRaises(ValueError): self.validate(caller.receipt())
    def test_original_boundary_true_tertrunc(self):
        ref = self.build(); caller = h.EmbeddedTeacherReferenceCaller(ref, boundary=core.OriginalEpisodeBoundary(Torch, 'cpu'))
        for _ in range(3):
            caller({'policy': raw()}); term, trunc = mask(False), mask(False)
            term.values[0] = True; trunc.values[1] = True; caller.observe_transition(term, trunc)
        self.assertEqual(caller.boundary.next_start.values[:3], [True, True, False])
        self.validate(caller.receipt(), expected_actor_calls=3)
    def test_stochastic_rejected(self):
        _, caller = self.run_one()
        with self.assertRaises(ValueError): caller({'policy': raw()}, stochastic_output=True)
    def test_candidate_variant_semantic_rejected(self):
        _, caller = self.run_one(); receipt = caller.receipt(); receipt['policy_variant'] = 'A1_RAW35_FRESH'
        with self.assertRaises(ValueError): self.validate(receipt)
    def test_wrong_control_count_rejected(self):
        _, caller = self.run_one()
        with self.assertRaises(ValueError): self.validate(caller.receipt(), expected_actor_calls=160)
    def test_bool_control_count_rejected(self):
        _, caller = self.run_one()
        with self.assertRaises(ValueError): self.validate(caller.receipt(), expected_actor_calls=True)
    def test_terminal_actual_rsl_pin_rejected(self):
        _, caller = self.run_one(); receipt = caller.receipt(); receipt['actual_eval_RSL_source_binding']['SHA256'] = 'f' * 64
        with self.assertRaises(ValueError): self.validate(receipt)
    def test_terminal_bool_boundary_count_rejected(self):
        _, caller = self.run_one(); receipt = caller.receipt(); receipt['original_episode_boundary']['actions'] = True
        with self.assertRaises(ValueError): self.validate(receipt)
    def test_terminal_guard_metadata_missing_rejected(self):
        _, caller = self.run_one(); receipt = caller.receipt(); receipt['producer_teacher_state_guard'] = None
        with self.assertRaises(ValueError): self.validate(receipt)
    def test_adapter_no_Torch_or_model_reader(self):
        source = (HERE / 'embedded_teacher_reference_v1.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        imports = {x.names[0].name.split('.')[0] for x in ast.walk(tree) if isinstance(x, ast.Import)}
        self.assertFalse({'torch', 'tensordict', 'isaacsim'} & imports)
        calls = [x.func.attr for x in ast.walk(tree) if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)]
        self.assertNotIn('load', calls); self.assertNotIn('load_state_dict', calls); self.assertNotIn('manual_seed', calls)
        self.assertNotIn('torch', sys.modules)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, default=HERE / 'CPU_TEST_RESULTS_FINAL_V1.json')
    args = parser.parse_args()
    start = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    value = dict(kind='STDLIB_FAKE_ONLY_EMBEDDED_TEACHER_REFERENCE_V1', tests_run=result.testsRun,
        failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(), seconds=time.perf_counter()-start,
        Torch_imported='torch' in sys.modules, SDK_native_GPU_actual_PT_operations=0,
        actual_Torch_reference_math=None, actual_frozen_reference_evaluation=None)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)

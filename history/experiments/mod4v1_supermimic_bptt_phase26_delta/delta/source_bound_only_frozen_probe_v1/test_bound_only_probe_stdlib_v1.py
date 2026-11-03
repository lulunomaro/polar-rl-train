"""SOURCE/fake/scalar tests only. No Torch, SDK or checkpoint/data decoding."""
import argparse
import ast
import contextlib
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import sys
import time
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'source_eval_a1_raw35_v1'
sys.path.insert(0, str(BASE))
import bound_only_frozen_probe_v1 as p
h = p.h
CORE = HERE.parent / 'source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py'
spec = importlib.util.spec_from_file_location('bound_probe_test_original_boundary', CORE)
core = importlib.util.module_from_spec(spec); sys.modules[spec.name] = core; spec.loader.exec_module(core)


class Scalar:
    def __init__(self, value): self.value = value
    def item(self): return self.value


class Vec:
    def __init__(self, values, *, dtype='float32', shape=None):
        self.values = list(values); self.shape = shape or (80, 6); self.dtype = dtype; self.device = 'cpu'
    def __add__(self, other): return Vec([a+b for a,b in zip(self.values, other.values)], shape=self.shape)
    def __sub__(self, other): return Vec([a-b for a,b in zip(self.values, other.values)], shape=self.shape)
    def __rmul__(self, scale): return Vec([scale*a for a in self.values], shape=self.shape)
    def __gt__(self, x): return Vec([a>x for a in self.values], dtype='bool', shape=self.shape)
    def __or__(self, other): return Vec([a or b for a,b in zip(self.values, other.values)], dtype='bool', shape=self.shape)
    def clone(self): return Vec(self.values, dtype=self.dtype, shape=self.shape)
    def abs(self): return Vec([abs(a) for a in self.values], shape=self.shape)
    def max(self): return Scalar(max(self.values))
    def sum(self): return Scalar(sum(self.values))
    def numel(self): return len(self.values)
    def clamp(self, lo, hi): return Vec([a if math.isnan(a) else max(lo, min(hi, a)) for a in self.values], shape=self.shape)


class FakeT:
    bool = 'bool'
    @staticmethod
    def tanh(x): return Vec([math.tanh(a) for a in x.values], shape=x.shape)
    @staticmethod
    def ones(n, dtype, device): return Vec([True]*n, dtype=dtype, shape=(n,))
    @staticmethod
    def is_tensor(x): return isinstance(x, Vec)


class TD(dict):
    def __init__(self, value, batch_size): super().__init__(value); self.batch_size = batch_size


class History:
    def __init__(self): self.raw = NS(shape=(80, 35)); self.last_key = None
    def __getitem__(self, key): self.last_key = key; return self.raw


class Teacher:
    def __init__(self, values): self.value = Vec(values*80); self.calls = 0
    def __call__(self, td, stochastic_output):
        assert stochastic_output is False
        self.calls += 1; self.last_td = td; return self.value


class Residual:
    def __init__(self, values): self.values = list(values)*80; self.calls = 0
    def __call__(self, history, goal): self.calls += 1; self.last = (history, goal); return Vec(self.values)


class Legacy:
    def __init__(self, residual, teacher, offset, scale=.05):
        self.residual, self.teacher, self.offset, self.scale = residual, teacher, offset, scale
        # Fake illustration of the REAL ctor hazard. Restore trained values AFTER.
        self.residual.values = [0.]*480


def wrapper(stats=False, base=None, delta=None):
    statistic = p.ReadOnlyActionStatistics(stats)
    cls = p.make_bound_only_wrapper(Legacy, TD, FakeT, statistic)
    teacher = Teacher(base or [0., 0., 0., 0., 0., 0.]); residual = Residual(delta or [-1000., -1., 0., .1, 1., 1000.])
    actor = cls(residual, teacher, 0, scale=.05)
    residual.values = list(delta or [-1000., -1., 0., .1, 1., 1000.])*80
    return actor, statistic


def fresh_cache(**kw):
    obj = object.__new__(h.FrozenA1CheckpointCache)
    obj.expected = dict(role='E3'); obj.SHA = p.QUALIFIED_CONTAINERS['E3']; obj._built = False
    obj.t = object(); obj.__dict__.update(kw)
    return obj


def valid_receipt():
    return dict(kind=p.KIND, purpose=p.PURPOSE, policy_variant=p.VARIANT, container_role='E3',
        source_SHA=p.QUALIFIED_CONTAINERS['E3'], container_checkpoint_SHA=p.QUALIFIED_CONTAINERS['E3'],
        actor_calls=1, probe_training_updates=0, probe_BPTT_policy_steps=0,
        probe_optimizer_updates=dict(pi=0, wm=0, aux=0, critic=0), actor_frozen=True,
        whole_root_CPU_unchanged=True, inference_failed=False, physical_byte_opens=1,
        SHA_calculations=1, CPU_decodes=1, mother_checkpoint_opens=0,
        actor_source_bindings={'rsl_rl.models.MLPModel': dict(p.APPROVED_RSL)},
        synthetic_only=False, container_algorithm_family=h.FAMILY, container_algorithm_variant='A1_RAW35_FRESH',
        container_algorithm_actor_view=h.VIEW, residual_scale=.05, action_clip=6., native_enabled=False,
        qualified_native_execution=None, eligible_for_promotion=False,
        effective_wrapper=dict(qualname='make_bound_only_wrapper.<locals>.BoundTeacherResidualPolicy', source=p._source_binding()),
        original_episode_boundary_source=dict(bytes=p.BOUNDARY_PIN[0], SHA256=p.BOUNDARY_PIN[1]),
        original_episode_boundary=dict(actions=1, original_step_transitions=1,
            pending_original_step=False, synthetic_episode_mask=False),
        bound_probe_action_statistics=dict(forward_calls=1))


class MathTests(unittest.TestCase):
    def test_scalar_component_bound(self):
        for x in (-1e100, -1000., -10., -1., -.001, 0., .001, 1., 10., 1000., 1e100):
            self.assertLessEqual(abs(.05*math.tanh(x)), .05)
    def test_not_bound_vs_old_unbounded(self):
        self.assertGreater(abs(.05*1000-.05*math.tanh(1000)), 49.)
        self.assertGreater(abs(6.-.05*math.tanh(1000)), 5.)
    def test_nonexpansive_total_clip_vs_teacher(self):
        rng = random.Random(703)
        for _ in range(2000):
            base, delta = rng.uniform(-20,20), rng.uniform(-1000,1000)
            clip = lambda x: max(-6., min(6., x))
            self.assertLessEqual(abs(clip(base+.05*math.tanh(delta))-clip(base)), .05+1e-14)
    def test_l2_is_not_component_bound(self): self.assertGreater(math.sqrt(6)*.05, .05)
    def test_tanh_is_not_hard_clip(self): self.assertNotEqual(math.tanh(.5), .5)
    def test_zero_residual_teacher_equivalence(self): self.assertEqual(.05*math.tanh(0), 0.)
    def test_changed_gradient_not_training_claim(self):
        self.assertLess(.05*(1-math.tanh(3)**2), .001)
        self.assertEqual(.05*(1-math.tanh(0)**2), .05)


class ForwardTests(unittest.TestCase):
    def test_exact_bound_formula_and_one_forward(self):
        actor, stats = wrapper(True); history, goal = History(), object(); value = actor.forward(history, goal)
        self.assertEqual(value.values[:6], [.05*math.tanh(x) for x in [-1000.,-1.,0.,.1,1.,1000.]])
        self.assertEqual(actor.teacher.calls, 1); self.assertEqual(actor.residual.calls, 1)
        self.assertIs(actor.teacher.last_td['policy'], history.raw); self.assertIs(actor.residual.last[1], goal)
        self.assertEqual(history.last_key, (Ellipsis, -1, slice(0,35,None)))
        self.assertEqual(stats.calls, 1); self.assertEqual(stats.components, 480)
    def test_original_constructor_is_inherited(self):
        actor, _ = wrapper(); self.assertIs(type(actor).__init__, Legacy.__init__)
    def test_stats_disabled_avoids_scalar_reductions(self):
        actor, stats = wrapper(False)
        with patch.object(Vec, 'max', side_effect=AssertionError('scalar reduction with stats disabled')):
            actor.forward(History(), object())
        receipt = stats.receipt(); self.assertFalse(receipt['enabled']); self.assertIsNone(receipt['action_components'])
        self.assertIsNone(receipt['maxima']['raw_delta_abs_max'])
    def test_same_forward_counterfactual_not_replay(self):
        actor, stats = wrapper(True); actor.forward(History(), object()); r = stats.receipt()
        self.assertGreater(r['maxima']['probe_vs_legacy_action_abs_max'], 5.)
        self.assertLessEqual(r['maxima']['probe_vs_clipped_teacher_abs_max'], .05)
        self.assertEqual(r['legacy_total_clip_hits'], 160); self.assertEqual(r['probe_total_clip_hits'], 0)
        self.assertEqual(r['extra_teacher_or_residual_forwards'], 0)
    def test_total_clip_and_base_outside_range(self):
        actor, _ = wrapper(base=[10.,-10.,6.,-6.,5.99,-5.99]); out = actor.forward(History(), object())
        self.assertTrue(all(-6 <= x <= 6 for x in out.values))
    def test_statistics_do_not_change_actions_or_rng(self):
        a, _ = wrapper(False); b, _ = wrapper(True); before = random.getstate()
        self.assertEqual(a.forward(History(), object()).values, b.forward(History(), object()).values)
        self.assertEqual(before, random.getstate())
    def test_no_added_constructor_or_state_submodule(self):
        actor, _ = wrapper(); self.assertEqual(set(vars(actor)), {'residual','teacher','offset','scale'})
    def test_stats_flag_type(self):
        with self.assertRaises(ValueError): p.ReadOnlyActionStatistics(1)


class FreshBuildTests(unittest.TestCase):
    def test_actual_old_helper_pin(self): self.assertEqual(p._verify_original_helper()['SHA256'], p.BASE_PIN[1])
    def test_existing_mean_or_other_object_not_cache(self):
        with self.assertRaises(ValueError): p.build_bound_only_mean_policy(object(), 'cpu')
    def test_already_built_cache_never_rearmed(self):
        cache = fresh_cache(_built=True)
        with self.assertRaises(ValueError): p.build_bound_only_mean_policy(cache, 'cpu')
        self.assertTrue(cache._built)
    def test_wrong_container_before_build(self):
        cache = fresh_cache(SHA='a'*64)
        with self.assertRaises(ValueError): p.build_bound_only_mean_policy(cache, 'cpu')
        self.assertFalse(cache._built)
    def test_wrong_explicit_container(self):
        with self.assertRaises(ValueError): p.build_bound_only_mean_policy(fresh_cache(), 'cpu', expected_container_sha='a'*64)
    def test_unrelated_role(self):
        with self.assertRaises(ValueError): p.build_bound_only_mean_policy(fresh_cache(expected=dict(role='E0')), 'cpu')
    def test_n80_exact_not_bool(self):
        for n in (True, 79, 1024):
            with self.assertRaises(ValueError): p.build_bound_only_mean_policy(fresh_cache(), 'cpu', n)
    def test_flags_actual_bool(self):
        for name in ('collect_action_statistics','synthetic_only'):
            with self.assertRaises(ValueError): p.build_bound_only_mean_policy(fresh_cache(), 'cpu', **{name:1})
    def test_synthetic_requires_explicit_sha(self):
        with self.assertRaises(ValueError): p.build_bound_only_mean_policy(fresh_cache(), 'cpu', synthetic_only=True)
    def test_build_claim_survives_failure_and_blocks_fallback(self):
        cache = fresh_cache()
        with patch.object(h, '_runtime_modules', side_effect=ValueError('own fake build failure')):
            with self.assertRaisesRegex(ValueError, 'own fake'): p.build_bound_only_mean_policy(cache, 'cpu')
        self.assertTrue(cache._built)
        with self.assertRaises(ValueError): p.build_bound_only_mean_policy(cache, 'cpu')
    def test_rsl_mismatch_consumes_failed_claim(self):
        cache = fresh_cache(); modules = NS(t=cache.t, source_bindings={'rsl_rl.models.MLPModel': {}})
        with patch.object(h, '_runtime_modules', return_value=modules):
            with self.assertRaisesRegex(ValueError, 'RSL6219'): p.build_bound_only_mean_policy(cache, 'cpu')
        self.assertTrue(cache._built)


class SourceTests(unittest.TestCase):
    def test_inherited_act_identity(self): self.assertIs(p.BoundOnlyFrozenMean.act, h.FrozenA1MeanPolicy.act)
    def test_original_construct_load_block_whole_ast_equal(self):
        old = ast.parse(Path(h.__file__).read_text(encoding='utf-8'))
        cls = next(n for n in old.body if isinstance(n, ast.ClassDef) and n.name == 'FrozenA1CheckpointCache')
        build = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'build_mean_policy')
        block = next(n for n in build.body if isinstance(n, ast.With))
        class N(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == 'self': node.id = 'cache'
                if node.id == 'need': return ast.Attribute(value=ast.Name(id='h',ctx=ast.Load()),attr='need',ctx=ast.Load())
                return node
            def visit_Attribute(self,node):
                node = self.generic_visit(node)
                if isinstance(node.value,ast.Name) and node.value.id == 'modules' and node.attr == 'Wrapper':
                    return ast.Name(id='wrapper',ctx=ast.Load())
                return node
        block = N().visit(block)
        new = ast.parse(Path(p.__file__).read_text(encoding='utf-8'))
        newfun = next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name == 'build_bound_only_mean_policy')
        newblock = next(n for n in newfun.body if isinstance(n,ast.With))
        self.assertEqual(ast.dump(block,include_attributes=False), ast.dump(newblock,include_attributes=False))
    def test_no_cache_rearm_assignment(self):
        for node in ast.walk(ast.parse(Path(p.__file__).read_text(encoding='utf-8'))):
            if isinstance(node,ast.Assign):
                for target in node.targets:
                    if isinstance(target,ast.Attribute) and target.attr == '_built':
                        self.assertIs(node.value.value, True)
    def test_no_native_or_training_entry(self):
        self.assertIs(p.NATIVE_ENABLED, False)
        text = Path(p.__file__).read_text(encoding='utf-8')
        for word in ('torch.load(', 'torch.save(', 'optimizer.step(', 'env.step(', 'env.reset(', 'register_forward_hook('):
            self.assertNotIn(word,text)
    def test_source_container_SHAs_equal_qualified_report(self):
        report = json.loads((HERE.parent/'reports/QUALIFIED_EMBEDDED_TEACHER_ORIGINAL_SKILL_BASELINE_V1.json').read_bytes())
        self.assertEqual({k:v['container_checkpoint_SHA'] for k,v in report['actor_container_and_teacher'].items()},p.QUALIFIED_CONTAINERS)
    def test_mean_guard_keeps_original_guard(self):
        obj = object.__new__(p.BoundOnlyFrozenMean); actor, stats = wrapper()
        obj.pi, obj._probe_statistics, obj.calls = actor, stats, 0
        obj._probe_class, obj._probe_forward, obj._probe_original_constructor = type(actor),type(actor).forward,Legacy.__init__
        with patch.object(h.FrozenA1MeanPolicy,'assert_frozen',return_value=True) as old:
            self.assertTrue(obj.assert_frozen()); old.assert_called_once()
        actor.forward = lambda *args: None
        with self.assertRaises(ValueError): obj.assert_frozen()


class ReceiptTests(unittest.TestCase):
    def validate(self,value=None): return p.validate_bound_probe_receipt(value or valid_receipt(), expected_role='E3',
        expected_source_sha=p.QUALIFIED_CONTAINERS['E3'], expected_actor_calls=1)
    def test_positive_component_not_native_qualification(self):
        result = self.validate(); self.assertTrue(result['passed_policy_component']); self.assertIsNone(result['actual_admission_wait_close_or_skill'])
    def test_old_unbounded_or_reference_kind(self):
        for key in ('kind','purpose','policy_variant'):
            row=valid_receipt(); row[key]='OLD'
            with self.assertRaises(ValueError): self.validate(row)
    def test_boolean_update_counter_not_zero(self):
        row=valid_receipt(); row['probe_training_updates']=False
        with self.assertRaises(ValueError): self.validate(row)
    def test_boolean_optimizer_counter_not_zero(self):
        row=valid_receipt(); row['probe_optimizer_updates']['pi']=False
        with self.assertRaises(ValueError): self.validate(row)
    def test_updates_nonzero(self):
        row=valid_receipt(); row['probe_BPTT_policy_steps']=1
        with self.assertRaises(ValueError): self.validate(row)
    def test_helper_SHA_binding(self):
        row=valid_receipt(); row['effective_wrapper']['source']['SHA256']='d'*64
        with self.assertRaises(ValueError): self.validate(row)
    def test_wrong_RSL(self):
        row=valid_receipt(); row['actor_source_bindings']['rsl_rl.models.MLPModel']['SHA256']='d'*64
        with self.assertRaises(ValueError): self.validate(row)
    def test_incomplete_original_step(self):
        row=valid_receipt(); row['original_episode_boundary']['pending_original_step']=True
        with self.assertRaises(ValueError): self.validate(row)
    def test_wrong_boundary_PIN(self):
        row=valid_receipt(); row['original_episode_boundary_source']['SHA256']='d'*64
        with self.assertRaises(ValueError): self.validate(row)
    def test_mother_reopen_or_duplicate_decode(self):
        for k in ('CPU_decodes','mother_checkpoint_opens'):
            row=valid_receipt(); row[k]=2
            with self.assertRaises(ValueError): self.validate(row)
    def test_no_promotion_or_native_relabel(self):
        for k in ('native_enabled','eligible_for_promotion'):
            row=valid_receipt(); row[k]=True
            with self.assertRaises(ValueError): self.validate(row)
    def test_boolean_forward_count_not_integer(self):
        row=valid_receipt(); row['bound_probe_action_statistics']['forward_calls']=True
        with self.assertRaises(ValueError): self.validate(row)


class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(CORE.parent))
        import bound_only_frozen_route_v1
        cls.route = bound_only_frozen_route_v1
    def task(self):
        return dict(role='E3', bound_only_probe=dict(purpose=p.PURPOSE, policy_variant=p.VARIANT,
            zero_update=True, native_enabled=False, collect_action_statistics=False))
    def test_explicit_new_source_task_required(self):
        self.assertFalse(self.route.validate_source_route_task(self.task())['collect_action_statistics'])
        for key in ('purpose','policy_variant','zero_update','native_enabled'):
            task=self.task(); task['bound_only_probe'].pop(key)
            with self.assertRaises(ValueError): self.route.validate_source_route_task(task)
    def test_constructor_delegates_unchanged_whole_cache(self):
        task=self.task()
        with patch.object(self.route.base.A1CheckpointAdapter,'__init__',return_value=None) as old:
            self.route.BoundOnlyCheckpointAdapter(FakeT,task)
            old.assert_called_once_with(FakeT,task)
    def test_original_cache_and_actor_guards_inherited(self):
        for name in ('check','assert_entire_root_unchanged','check_actor'):
            self.assertIs(getattr(self.route.BoundOnlyCheckpointAdapter,name),getattr(self.route.base.A1CheckpointAdapter,name))
    def test_historical_steps_not_new_probe_steps(self):
        obj=object.__new__(self.route.BoundOnlyCheckpointAdapter)
        obj.cache=NS(receipt=lambda:dict(source_SHA=p.QUALIFIED_CONTAINERS['E3']))
        obj.task=dict(a1_producer=dict(run_id='OWN_FAKE_SOURCE',FINAL=dict(actual_BPTT_policy_steps=2182,counts=dict(pi_bptt_optimizer_steps=2182))))
        obj.caller=None; row=obj.receipt()
        self.assertEqual(row['source_producer_actual_BPTT_policy_steps'],2182)
        self.assertEqual(row['probe_BPTT_policy_steps'],0); self.assertEqual(row['probe_training_updates'],0)
        self.assertFalse(row['native_enabled']); self.assertNotIn('actual_BPTT_policy_steps',row)
    def test_native_flag_and_no_source_task_relabel(self):
        self.assertFalse(self.route.NATIVE_ENABLED)
        task=self.task(); task['bound_only_probe']['native_enabled']=True
        with self.assertRaises(ValueError): self.route.validate_source_route_task(task)


class BoundaryTests(unittest.TestCase):
    def test_actual_original_boundary_true_term_trunc(self):
        boundary=core.OriginalEpisodeBoundary(FakeT,'cpu')
        self.assertTrue(all(boundary.for_action().values))
        term=Vec([i==0 for i in range(80)],dtype='bool',shape=(80,)); trunc=Vec([i==1 for i in range(80)],dtype='bool',shape=(80,))
        boundary.after_original_step(term,trunc); mask=boundary.for_action().values
        self.assertEqual(mask[:3],[True,True,False])
    def test_missing_step_blocks_action(self):
        boundary=core.OriginalEpisodeBoundary(FakeT,'cpu'); boundary.for_action()
        with self.assertRaises(ValueError): boundary.for_action()
    def test_source_only_caller_uses_original_raw_and_mask(self):
        mean=object.__new__(p.BoundOnlyFrozenMean); mean.t,mean.device=FakeT,'cpu'; mean.seen=[]
        mean.act=lambda raw,episode_start: mean.seen.append((raw,episode_start)) or 'OWN_FAKE_ACTION'
        boundary=core.OriginalEpisodeBoundary(FakeT,'cpu'); caller=p.BoundOnlyPolicyCaller(mean,boundary=boundary)
        raw=object(); self.assertEqual(caller({'policy':raw}), 'OWN_FAKE_ACTION'); self.assertIs(mean.seen[0][0],raw)
        self.assertTrue(all(mean.seen[0][1].values))
        with self.assertRaises(ValueError): caller({'policy':raw})


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',required=True); args=parser.parse_args()
    output=Path(args.output); assert not output.exists()
    start=time.perf_counter(); result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    receipt=dict(kind='SOURCE_SCALAR_AST_FAKE_ZERO_UPDATE_BOUND_PROBE_TESTS_V1', testsRun=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),seconds=time.perf_counter()-start,
        torch_imported='torch' in sys.modules, actual_Torch_fixture_executed=False,
        SDK_GPU_actual_PT_raw_C_locks_Git_or_native_operations=0)
    with output.open('x',encoding='utf-8') as f: json.dump(receipt,f,indent=2); f.write('\n')
    assert 'torch' not in sys.modules and 'isaacsim' not in sys.modules
    raise SystemExit(0 if result.wasSuccessful() else 1)

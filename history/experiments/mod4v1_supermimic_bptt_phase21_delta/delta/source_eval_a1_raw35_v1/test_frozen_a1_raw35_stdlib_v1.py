"""Stdlib-only synthetic cache/metadata/math/AST tests. No Torch/SDK import."""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid
import frozen_a1_raw35_v1 as h

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BRIDGE = ROOT / 'source_runtime/native_supermimic_bridge.py'
NETWORK = ROOT / 'source_core_review/evidence/networks.py'
COLLECT = ROOT / 'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py'


class FakeTensor:
    def __init__(self, shape, device='cpu'):
        self.shape = tuple(shape); self._version = 0; self.dtype = 'float32'; self.device = SimpleNamespace(type=device)


FAKE_TORCH = SimpleNamespace(is_tensor=lambda x: isinstance(x, FakeTensor))


def fixture():
    base = HERE / 'CPU_SYNTHETIC_CASES_V1' / uuid.uuid4().hex
    directory = base / 'production/checkpoints'; directory.mkdir(parents=True)
    path = directory / 'synthetic_000024_complete.pt'
    raw = b'{"OWN_STDLIB_JSON_FIXTURE_NOT_TORCH_OR_PRODUCTION_WEIGHTS":true}'
    path.write_bytes(raw)
    c = {k: 0 for k in h.COUNT_FIELDS}; c.update(policy_attempts=25, pi_optimizer_steps=24, pi_bptt_optimizer_steps=24, wm_optimizer_steps=30)
    teacher = dict(source_path='/SYNTHETIC_MOTHER_NEVER_OPEN.pt', source_SHA='a'*64, source_bytes=99, teacher_frozen=True)
    checkpoint = dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest(), iteration=24,
                      counts=c.copy(), teacher_source=teacher.copy(), teacher_unchanged=True,
                      full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
    final = dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', passed_execution=True, teacher_unchanged=True,
                 role='E3', role_key='EXPLICIT_ENTRY_KEY', run_id='OWN_SYNTHETIC_A1', actor_view=h.VIEW,
                 algorithm_family=h.FAMILY, algorithm_variant='A1_RAW35_FRESH', counts=c.copy(), actual_BPTT_policy_steps=24,
                 checkpoint=checkpoint, teacher=teacher.copy())
    pi = {'teacher.synthetic': FakeTensor((6,35)), 'residual.enc.synthetic': FakeTensor((32,3)), 'residual.dec.synthetic': FakeTensor((6,382))}
    for prefix, width in (('residual.obs_norm.',35), ('residual.goal_norm.',3)):
        for name, shape in (('mean',(width,)), ('var',(width,)), ('count',())):
            pi[prefix+name] = FakeTensor(shape)
    root = dict(wm={'unmoved':FakeTensor((2,))}, pi=pi, critic={}, opt_wm={}, opt_pi={}, opt_v={},
                args=dict(hist=10,z_dim=32,goal_frames=1,policy_hidden=[512,256,128],test_hidden_dims=None,amp='none',buffer_steps=128),
                iteration=24, asset_SHA='b'*64,contract_SHA='c'*64,new_algorithm_not_PPO_resume=True,bootstrap_teacher=teacher.copy(),
                context_reward_extension=dict(full_resume=True, counts=c.copy(), aux={'unused':FakeTensor((2,))}, opt_aux={}, replay=dict(T=128,N=1024,data={}),
                obs_hist=FakeTensor((1024,10,35)),rng={'python':('NOT_RESTORED',)},environment={'NOT_RESTORED':True},
                contract=dict(schema='mod4v1.ctx_task_reward.v1',obs_dim=35,action_dim=6,num_joints=30,goal_frame_dim=3,
                              context_dim=500,policy_dt_s=.02,num_envs=1024)))
    root.update({k:final[k] for k in ('role','role_key','run_id','actor_view','algorithm_family','algorithm_variant')})
    kwargs=dict(own_job_root=base,role='E3',role_key='EXPLICIT_ENTRY_KEY',run_id='OWN_SYNTHETIC_A1',asset_SHA='b'*64,contract_SHA='c'*64)
    return final, root, kwargs


def cache_fixture(final, root, kwargs):
    with patch.object(h, '_decode_cpu', return_value=(FAKE_TORCH, root)):
        return h.FrozenA1CheckpointCache(final, **kwargs)


def shape(x):
    return (len(x),)+shape(x[0]) if isinstance(x,list) and x else ()


def binary(a,b,fn):
    if isinstance(a,list):
        if isinstance(b,list) and len(shape(a)) == len(shape(b)):
            return [binary(x,y,fn) for x,y in zip(a,b)]
        return [binary(x,b,fn) for x in a]
    return fn(a,b)


class Array:
    def __init__(self, data): self.d=data; self.shape=shape(data)
    def __getitem__(self,key):
        if isinstance(key,tuple) and key[0] is Ellipsis:
            return Array([row[key[1]][key[2]] for row in self.d])
        return Array(self.d[key])
    def __add__(self,b): return Array(binary(self.d,b.d if isinstance(b,Array) else b,lambda x,y:x+y))
    def __sub__(self,b): return Array(binary(self.d,b.d if isinstance(b,Array) else b,lambda x,y:x-y))
    def __truediv__(self,b): return Array(binary(self.d,b.d if isinstance(b,Array) else b,lambda x,y:x/y))
    def __mul__(self,b): return Array(binary(self.d,b.d if isinstance(b,Array) else b,lambda x,y:x*y))
    __rmul__=__mul__
    def flatten(self,dim):
        assert dim == -2
        return Array([[v for row in batch for v in row] for batch in self.d])
    def clamp(self,low,high): return Array(binary(self.d,0,lambda x,_:min(high,max(low,x))))


def unary(a, fn): return Array(binary(a.d,0,lambda x,_:fn(x)))


FAKE_OPS=SimpleNamespace(sqrt=lambda x:unary(x,math.sqrt),tanh=lambda x:unary(x,math.tanh),
    cat=lambda xs,dim:Array([a+b for a,b in zip(xs[0].d,xs[1].d)]))


def extracted_forward(path, class_name, **globals_):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==class_name)
    fn=copy.deepcopy(next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='forward'))
    for arg in fn.args.args: arg.annotation=None
    fn.returns=None; fn.decorator_list=[]
    code=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])); scope=dict(globals_)
    exec(compile(code,'OWN_EXTRACTED_PURE_FORWARD_AST_NOT_SDK','exec'),scope)
    return scope['forward']


def sparse_mlp(rows, dims):
    result=rows
    for n,m in zip(dims,dims[1:]):
        next_rows=[]
        for row in result:
            values=[.15*row[j%n]-.07*row[(7*j+3)%n]+((j%11)-5)*.01 for j in range(m)]
            if m != dims[-1]: values=[v if v>=0 else math.expm1(v) for v in values]
            next_rows.append(values)
        result=next_rows
    return result


def vendor_history(history,obs,fresh):
    return [[list(row) for _ in range(10)] if first else old[1:]+[list(row)] for old,row,first in zip(history,obs,fresh)]


class CacheTests(unittest.TestCase):
    def test_one_whole_read_decode_hash_root_CPU_no_mother_open(self):
        final,root,kwargs=fixture(); original=Path.read_bytes; opened=[]
        def read(p): opened.append(str(p)); return original(p)
        with patch.object(Path,'read_bytes',read),patch.object(h,'_decode_cpu',return_value=(FAKE_TORCH,root)) as dec:
            cache=h.FrozenA1CheckpointCache(final,**kwargs); cache.assert_unchanged(); receipt=cache.receipt()
        self.assertEqual(opened,[final['checkpoint']['path']]); self.assertEqual(dec.call_count,1)
        self.assertEqual(receipt['physical_byte_opens'],1); self.assertEqual(receipt['CPU_decodes'],1)
        self.assertEqual(receipt['mother_checkpoint_opens'],0); self.assertIs(cache.root,root)
    def test_A0_and_B_family_fail_before_open(self):
        final,root,kw=fixture()
        for field,value in [('actor_view','strict_B'),('algorithm_family','ppo'),('algorithm_variant','A0')]:
            bad=copy.deepcopy(final);bad[field]=value
            with self.subTest(field=field),patch.object(Path,'read_bytes') as rd,self.assertRaises(ValueError):h.FrozenA1CheckpointCache(bad,**kw)
            rd.assert_not_called()
    def test_bad_counts_types_order_and_iteration(self):
        final,root,kw=fixture()
        for key,value in [('pi_unverified_steps',False),('pi_bptt_optimizer_steps',26)]:
            bad=copy.deepcopy(final);bad['counts'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):cache_fixture(bad,root,kw)
        final['checkpoint']['iteration']=True
        with self.assertRaises(ValueError):cache_fixture(final,root,kw)
    def test_role_key_run_asset_contract_provenance(self):
        for field in ('role_key','run_id','asset_SHA','contract_SHA'):
            final,root,kw=fixture();root[field]='DIFFERENT'
            with self.subTest(field=field),self.assertRaises(ValueError):cache_fixture(final,root,kw)
    def test_checkpoint_path_must_be_own_full_producer(self):
        final,root,kw=fixture();kw['own_job_root']=HERE/'UNRELATED_NEVER_OPEN'
        with patch.object(Path,'read_bytes') as rd,self.assertRaises(ValueError):cache_fixture(final,root,kw)
        rd.assert_not_called()
    def test_SHA_and_byte_mismatch_before_decode(self):
        for field,value in [('SHA','d'*64),('bytes',1)]:
            final,root,kw=fixture();final['checkpoint'][field]=value
            with patch.object(h,'_decode_cpu') as dec,self.subTest(field=field),self.assertRaises(ValueError):h.FrozenA1CheckpointCache(final,**kw)
            dec.assert_not_called()
    def test_N1024_not_sliced_or_restored(self):
        final,root,kw=fixture();cache=cache_fixture(final,root,kw)
        self.assertEqual(cache.root['context_reward_extension']['obs_hist'].shape,(1024,10,35))
        self.assertFalse(cache.receipt()['replay_or_saved_history_sliced_or_restored'])
    def test_source_N80_replay_not_accepted(self):
        final,root,kw=fixture();root['context_reward_extension']['replay']['N']=80
        with self.assertRaises(ValueError):cache_fixture(final,root,kw)
    def test_bad_policy_config_types_and_values(self):
        for key,value in [('hist',10.),('z_dim',31),('goal_frames',True),('policy_hidden',[512.,256,128]),('amp','bf16')]:
            final,root,kw=fixture();root['args'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):cache_fixture(final,root,kw)
    def test_missing_normalization_and_teacher_are_gaps_no_fallback(self):
        for key in ('residual.obs_norm.count','teacher.synthetic'):
            final,root,kw=fixture();del root['pi'][key]
            with self.subTest(key=key),self.assertRaises(ValueError):cache_fixture(final,root,kw)
    def test_full_root_required_not_actor_only(self):
        final,root,kw=fixture();del root['wm']
        with self.assertRaises(ValueError):cache_fixture(final,root,kw)
    def test_whole_root_version_guard_includes_unused_WM(self):
        final,root,kw=fixture();cache=cache_fixture(final,root,kw);root['wm']['unmoved']._version+=1
        with self.assertRaises(ValueError):cache.assert_unchanged()
    def test_whole_root_identity_and_metadata_guard(self):
        for mutation in ('tensor','metadata','schema'):
            final,root,kw=fixture();cache=cache_fixture(final,root,kw)
            if mutation=='tensor':root['wm']['unmoved']=FakeTensor((2,))
            elif mutation=='metadata':root['context_reward_extension']['rng']['python']=('CHANGED',)
            else:root['new_key']=1
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):cache.assert_unchanged()
    def test_decoded_GPU_leaf_fails(self):
        final,root,kw=fixture();root['wm']['unmoved'].device.type='cuda'
        with self.assertRaises(ValueError):cache_fixture(final,root,kw)
    def test_unchanged_NaN_nonactor_metadata_is_preserved_not_normalized(self):
        final,root,kw=fixture();root['unused_diagnostic']=float('nan');cache=cache_fixture(final,root,kw)
        self.assertTrue(cache.assert_unchanged());self.assertTrue(math.isnan(root['unused_diagnostic']))


class FormulaAndSourceTests(unittest.TestCase):
    def test_real_wrap_forward_AST_against_raw35_reference(self):
        norm=extracted_forward(NETWORK,'RunningNorm',torch=FAKE_OPS)
        policy=extracted_forward(NETWORK,'Policy',torch=FAKE_OPS,run_mlp=lambda net,x:net(x))
        wrapper=extracted_forward(BRIDGE,'TeacherResidualPolicy')
        def normalize(x,width):
            obj=SimpleNamespace(mean=Array([.02*(j-2) for j in range(width)]),var=Array([.5+.01*j for j in range(width)]),eps=.01)
            return norm(obj,x)
        hist=Array([[[.01*(i+j+k)-.3 for j in range(35)] for i in range(10)] for k in range(2)])
        goal=Array([x[-1][:3] for x in hist.d])
        enc=lambda x:Array(sparse_mlp(x.d,[3,512,256,128,32]))
        dec=lambda x:Array(sparse_mlp(x.d,[382,512,256,128,6]))
        residual=SimpleNamespace(enc=enc,dec=dec,goal_norm=lambda x:normalize(x,3),obs_norm=lambda x:normalize(x,35))
        def teacher(td,stochastic_output):
            self.assertIs(stochastic_output,False)
            return Array(sparse_mlp(td['policy'].d,[35,256,128,64,6]))
        wrapped=SimpleNamespace(offset=0,scale=.05,teacher=teacher,residual=lambda x,g:policy(residual,x,g))
        td_stub=SimpleNamespace(TensorDict=lambda data,batch_size:data)
        with patch.dict(sys.modules,{'tensordict':td_stub}): actual=wrapper(wrapped,hist,goal).d
        mean=teacher({'policy':Array([x[-1] for x in hist.d])},False).d
        zn=normalize(goal,3);latent=unary(enc(zn),math.tanh).d
        flat=normalize(hist,35).flatten(-2).d
        delta=dec(Array([z+x for z,x in zip(latent,flat)])).d
        expected=[[min(6.,max(-6.,a+.05*d)) for a,d in zip(aa,dd)] for aa,dd in zip(mean,delta)]
        self.assertEqual(actual,expected)
    def test_original_wrap_clips_total_not_delta(self):
        wrapper=extracted_forward(BRIDGE,'TeacherResidualPolicy')
        obj=SimpleNamespace(offset=0,scale=.05,teacher=lambda td,stochastic_output:Array([[5.9,-5.9,7.,-7.,1.,-1.]]),residual=lambda x,g:Array([[20.,-20.,-100.,100.,0.,0.]]))
        with patch.dict(sys.modules,{'tensordict':SimpleNamespace(TensorDict=lambda x,batch_size:x)}):
            got=wrapper(obj,Array([[[0.]*35]*10]),Array([[0.]*3])).d
        self.assertEqual(got,[[6.,-6.,2.,-2.,1.,-1.]])
    def test_first_and_reset_padding_repeat_current_not_zero(self):
        hist=[[[0.]*35 for _ in range(10)] for _ in range(2)];obs=[[1.]*35,[2.]*35]
        hist=vendor_history(hist,obs,[True,True]);self.assertEqual(hist[0],[[1.]*35]*10)
        hist=vendor_history(hist,[[3.]*35,[4.]*35],[False,True]);self.assertEqual(hist[0][-2:],[obs[0],[3.]*35]);self.assertEqual(hist[1],[[4.]*35]*10)
    def test_mixed_terminal_or_truncation_not_xi_valid_mask(self):
        term=[True,False,False];trunc=[False,True,False];fresh=[a or b for a,b in zip(term,trunc)]
        hist=vendor_history([[[0.]*35]*10 for _ in range(3)],[[j+1.]*35 for j in range(3)],fresh)
        self.assertEqual(fresh,[True,True,False]);self.assertEqual(hist[1],[[2.]*35]*10);self.assertEqual(hist[2][0],[0.]*35)
    def test_source_collect_and_helper_padding_goal(self):
        text=COLLECT.read_text(encoding='utf-8');helper=Path(h.__file__).read_text(encoding='utf-8')
        self.assertIn('self.obs_hist[:, 1:]',text);self.assertIn('self.obs_hist = torch.where',text)
        self.assertIn('raw35.unsqueeze(1).expand_as(self._history)',helper);self.assertIn('goal = raw35[:, :3]',helper)
    def test_strict_load_after_original_zeroing_constructor_and_no_norm_update(self):
        tree=ast.parse(Path(h.__file__).read_text(encoding='utf-8'))
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='FrozenA1CheckpointCache')
        build=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='build_mean_policy')
        calls=[(n.lineno,ast.unparse(n.func)) for n in ast.walk(build) if isinstance(n,ast.Call)]
        self.assertLess(next(l for l,f in calls if f=='modules.Wrapper'),next(l for l,f in calls if f=='pi.load_state_dict'))
        self.assertNotIn('.update(',ast.unparse(build));self.assertIn('assign=False',ast.unparse(build))
    def test_no_learn_restore_SDK_or_original_teacher_loader(self):
        tree=ast.parse(Path(h.__file__).read_text(encoding='utf-8'))
        forbidden={'learn','restore_rng','import_state','PinnedTeacher','SuperMimicLearner','ContextRewardLearner','Optimizer','Adam','randn_like'}
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):self.assertNotIn(ast.unparse(n.func).split('.')[-1],forbidden)
        imports=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
        self.assertFalse(any('torch' in s or 'isaac' in s for s in imports))
    def test_source_pins_match_only_two_bounded_files(self):
        for name,path in [('supermimic_vendor_v2.networks',NETWORK),('native_supermimic_bridge',BRIDGE)]:
            raw=path.read_bytes();self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),h._SOURCE_PINS[name])
    def test_frozen_wrapper_and_norm_hyperparameters_checked(self):
        def stub():
            norm=SimpleNamespace(eps=.01,max_count=2e8)
            pi=SimpleNamespace(offset=0,scale=.05,residual=SimpleNamespace(hist=10),obs_norm=norm,goal_norm=copy.copy(norm),
                               modules=lambda:[],parameters=lambda:[],named_parameters=lambda:[],named_buffers=lambda:[])
            return SimpleNamespace(cache=SimpleNamespace(assert_unchanged=lambda:True),pi=pi,_weights=[],t=FAKE_TORCH)
        self.assertTrue(h.FrozenA1MeanPolicy.assert_frozen(stub()))
        for target,key,value in [('pi','scale',1.),('pi','offset',1),('norm','eps',.1),('history','hist',9)]:
            obj=stub();item={'pi':obj.pi,'norm':obj.pi.obs_norm,'history':obj.pi.residual}[target];setattr(item,key,value)
            with self.subTest(key=key),self.assertRaises(ValueError):h.FrozenA1MeanPolicy.assert_frozen(obj)
    def test_E0_S50_binary_gaps_retained(self):
        c=json.loads((ROOT/'source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json').read_text(encoding='utf-8'))
        self.assertIsNone(c['experts']['E0']['original_atomic_predicate']);self.assertIsNone(c['experts']['SLOPE_INDEPENDENT50']['original_atomic_predicate'])
    def test_local_source_tests_imported_no_Torch_SDK(self):
        self.assertFalse(any(n=='torch' or n.startswith('isaac') for n in sys.modules))


if __name__=='__main__':
    started=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt=dict(kind='STDLIB_A1_CACHE_METADATA_EXTRACTED_FORWARD_AST_NOT_TORCH_OR_NATIVE',tests=result.testsRun,
                 failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),seconds=time.perf_counter()-started,
                 Torch_SDK_GPU_native_evaluation_or_production_checkpoint_reads=0,actual_frozen_eval=None)
    (HERE/'CPU_TEST_RESULTS_V1.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)

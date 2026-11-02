"""SYNTHETIC CPU-only full checkpoint roundtrip; native expert updates = 0.
No SDK, GPU, selected teacher checkpoint, canonical, GO, or active worker edits.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import ast,json,tempfile,random,torch,numpy as np
import native_supermimic_bridge
from ctx_reward_learner import ContextRewardLearner
from native_supermimic_bridge import TeacherResidualPolicy
from supermimic_vendor_v2.learner import SuperMimicConfig
# Reuse only the classes/imports of the prior fixture, not its already-run test.
fixture=Path(__file__).with_name('SYNTHETIC_CPU_SOFTWARE_CHECK_V1.py')
tree=ast.parse(fixture.read_text(encoding='utf-8'));prefix=[]
for node in tree.body:
    if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='e'for t in node.targets):break
    prefix.append(node)
scope={};exec(compile(ast.Module(body=prefix,type_ignores=[]),str(fixture),'exec'),scope)
Synthetic=scope['Synthetic'];FakeTeacher=scope['FakeTeacher'];torch.set_num_threads(2);torch.manual_seed(37);random.seed(37);np.random.seed(37)
e=Synthetic();e.init_state();teacher=FakeTeacher().requires_grad_(False)
e.export_supermimic_resume=lambda:dict(exact=False,reason='Synthetic new episode reset, not exact physical resume')
class L(ContextRewardLearner):
    def _make_policy(self):return TeacherResidualPolicy(super()._make_policy(),teacher,e.mdp.actor_context_offset)
config=SuperMimicConfig(iterations=40,buffer_steps=16,utd=1.,horizon=3,goal_frames=1,hist=2,z_dim=4,wm_hidden=(16,),policy_hidden=(16,),critic_hidden=(16,),wm_window=2,wm_batches=1,wm_batch=8,pi_batch=8,lr=.001,warmup_steps=8,wm_only_iters=2,critic_epochs=1,critic_minibatches=1,ckpt_every=10000,log_every=10000,log_backend='none',amp='none',compile=False,seed=37)
checks=[]
def same(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor)and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict)and set(a)==set(b)and all(same(v,b[k])for k,v in a.items())
    if isinstance(a,(list,tuple)):return isinstance(b,(list,tuple))and len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
    return a==b
with tempfile.TemporaryDirectory(prefix='declared_synthetic_fullresume_')as tmp:
    p=Path(tmp);l=L(e,config,p/'before',device='cpu',aux_hidden=(16,),aux_batch=8);l.train(target_bptt_steps=2)
    assert l.counts.pi_bptt_optimizer_steps==2;checks.append('natural_synthetic_train_two_verified_steps')
    dest=l.save(p/'synthetic_own_complete.pt',include_optimizers=True);payload=torch.load(dest,map_location='cpu',weights_only=True);ext=payload['context_reward_extension']
    assert ext['full_resume']and ext['update_boundary_safe']and ext['resume_scope']=='learner_full_environment_reset_required';checks.append('weights_only_full_payload_safe_load_with_numpy_rng')
    expected=(random.random(),np.random.random(3),torch.rand(3));e2=Synthetic();e2.init_state();n=L(e2,config,p/'after',device='cpu',aux_hidden=(16,),aux_batch=8)
    try:n.load(dest)
    except ValueError as error:assert 'allow_environment_reset' in str(error)
    else:raise AssertionError('Implicit physical continuation accepted')
    checks.append('undeclared_environment_reset_is_blocked')
    n.load(dest,allow_environment_reset=True)
    actual=(random.random(),np.random.random(3),torch.rand(3));assert expected[0]==actual[0]and np.array_equal(expected[1],actual[1])and torch.equal(expected[2],actual[2]);checks.append('Python_NumPy_TorchCPU_rng_restored')
    for name in ('wm','pi','critic','aux'):assert same(getattr(l,name).state_dict(),getattr(n,name).state_dict()),name
    checks.append('all_four_models_and_normalizers_identical')
    for name in ('wm','pi','v','aux'):assert same(getattr(l,'opt_'+name).state_dict(),getattr(n,'opt_'+name).state_dict()),name
    checks.append('all_four_optimizer_states_identical')
    assert vars(l.counts)==vars(n.counts)and l.iteration==n.iteration and l.sim_steps==n.sim_steps and l.collect_fraction==n.collect_fraction and l.pending_iteration==n.pending_iteration;checks.append('counters_iteration_collect_fraction_transaction_restored')
    assert l.buffer.ptr==n.buffer.ptr and l.buffer.size==n.buffer.size
    for key,data in l.buffer.data.items():
        if key!='stream_cut':assert torch.equal(data,n.buffer.data[key]),key
    assert n.buffer.data['stream_cut'][(n.buffer.ptr-1)%n.buffer.T].all()and not n.obs_hist.any();checks.append('replay_exact_except_declared_stream_cut_and_fresh_history')
    n.train(target_bptt_steps=3);assert n.counts.pi_bptt_optimizer_steps==3;checks.append('continues_from_two_to_three_not_restart_zero')
    assert not torch.cuda.is_initialized();checks.append('CUDA_never_initialized')
    print(json.dumps(dict(kind='SYNTHETIC_CPU_FULL_RESUME_ONLY_NOT_EXPERT_TRAINING',passed=True,checks=checks,synthetic_counts=vars(n.counts),native_expert_BPTT_updates_counted=0,source_teacher_PT_raw_SDK_GPU_C_GO_operations=0)))

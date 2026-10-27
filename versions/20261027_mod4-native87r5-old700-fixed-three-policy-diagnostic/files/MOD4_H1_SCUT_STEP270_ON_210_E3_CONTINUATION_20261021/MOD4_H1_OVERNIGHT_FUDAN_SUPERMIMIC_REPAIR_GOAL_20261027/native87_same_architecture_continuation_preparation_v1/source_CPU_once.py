"""One new synthetic restore fixture; no existing model file, SDK/GPU/physics."""
from pathlib import Path
from dataclasses import asdict,replace
from types import SimpleNamespace as S
from copy import deepcopy
import json,sys,torch,ast,hashlib
D=Path(__file__).resolve().parent;L=D.parent
sys.path[:0]=[str(D),str(L/'root_augmented_world_model_candidate/v5')]
from same_architecture_native_continuation_candidate_v1 import *
from supermimic_wheel_leg_v3.learner import SuperMimicConfig
from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel as WM
from supermimic_wheel_leg_v3.networks import Policy,Critic
torch.set_num_threads(2)
cfg=SuperMimicConfig(wm_hidden=(16,16,16),policy_hidden=(16,8),critic_hidden=(16,8),
                    wm_only_iters=64,wm_batch=1024,pi_batch=1024,amp='none',compile=False,seed=27)
checks=[]
def yes(v,name):
    assert v,name
    checks.append(name)
def exact(a,b):
    if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return type(a)==type(b) and a==b
def refuse(fn,name):
    try:fn()
    except (ValueError,KeyError,RuntimeError):checks.append(name);return
    raise AssertionError(name)
def learner():
    m=S(wm=WM(context_dim=31,hidden=cfg.wm_hidden,num_joints=30,auxiliary_dim=54,action_dim=6),
        pi=Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=cfg.policy_hidden),
        critic=Critic(1625,hidden=cfg.critic_hidden),cfg=cfg,env=S(num_envs=3),
        buffer=S(size=0),obs_hist=torch.full((3,10,86),-.125),iteration=0,wall_time=0.,sim_steps=0)
    m.opt_wm=torch.optim.Adam(m.wm.parameters(),lr=cfg.lr)
    m.opt_pi=torch.optim.Adam(m.pi.parameters(),lr=cfg.lr,betas=(.9,.95))
    m.opt_v=torch.optim.Adam(m.critic.parameters(),lr=cfg.lr)
    return m
source=learner()
# Populate real native module/normalizer and optimizer state synthetically.
for name,opt in [('wm','opt_wm'),('pi','opt_pi'),('critic','opt_v')]:
    module=getattr(source,name)
    for _,buf in module.named_buffers():
        if buf.is_floating_point():buf.fill_(.25)
    for p in module.parameters():p.grad=torch.full_like(p,.001)
    getattr(source,opt).step();getattr(source,opt).zero_grad(set_to_none=True)
native={k:deepcopy(getattr(source,k).state_dict()) for k in ('wm','pi','critic','opt_wm','opt_pi','opt_v')}
native.update(iteration=70,wall_time=123.5,sim_steps=983040,args=asdict(cfg),saved_at='SYNTHETIC')
contract=dict(DIMS,fresh4096_policy_only_bootstrap=True,original_physics_and_success_unchanged=True,
 original_RSL_core_frozen_bootstrap_only=True,not_production_expert_source=True,
 replay_not_saved_matching_upstream_resume_not_exact_PhysX_replay=True)
ref='a'*64
full=dict(UniSuperMimic_H1_test=native,UniSuperMimic_test_contract=contract,
 UniSuperMimic_publication=dict(native_iteration=70,world_updates=700,policy_updates=6,
 history_shape=[4096,10,86],episode_step_shape=[4096],
 producer=dict(reference_artifact_SHA=ref,method='MOD4_own_Fudan_native_v3',
 native_architecture_fresh=True,bootstrap_Adam=832460)),
 UniSuperMimic_obs_history='SYNTHETIC_SOURCE_HISTORY_MUST_NEVER_RESTORE',
 sensor_DR_state='SYNTHETIC_SOURCE_DR_MUST_NEVER_RESTORE')
progress=dict(updates=70,world_updates=700,policy_updates=6)
kw=dict(expected_source_contract=contract,expected_args=asdict(cfg),expected_progress=progress,expected_reference_SHA=ref,expected_num_envs=3)
target=learner();bridge=S(ep_step=torch.zeros(3,dtype=torch.long),wm_updates=0,pi_updates=0)
history=target.obs_hist;ep=bridge.ep_step;fresh_history=history.clone();rng=torch.random.get_rng_state().clone()
result=restore_same_architecture(target,bridge,full,**kw)
yes(all(exact(getattr(target,k).state_dict(),native[k]) for k in ('wm','pi','critic','opt_wm','opt_pi','opt_v')),'all_real_native_module_normalizer_and_3optimizer_states_exact')
yes(target.iteration==70 and bridge.wm_updates==700 and bridge.pi_updates==6 and target.wall_time==123.5 and target.sim_steps==983040,'global_counters_and_training_clock_preserved')
yes(target.obs_hist is history and bridge.ep_step is ep and torch.equal(history,fresh_history) and not ep.any(),'fresh_history_and_episode_state_not_replaced')
yes(torch.equal(torch.random.get_rng_state(),rng),'restore_no_RNG_draw')
# A subsequent target optimizer step must not mutate the source in-memory state.
before=deepcopy(native['opt_pi'])
for p in target.pi.parameters():p.grad=torch.full_like(p,.001)
target.opt_pi.step()
yes(exact(before,native['opt_pi']),'optimizer_state_not_aliased_into_source_checkpoint')
for label,edit in [
 ('missing_optimizer',lambda x:x['UniSuperMimic_H1_test'].pop('opt_v')),
 ('legacy_obs128',lambda x:x['UniSuperMimic_test_contract'].update(obs_dim=128)),
 ('wrong_config_seed',lambda x:x['UniSuperMimic_H1_test']['args'].update(seed=29)),
 ('source_counter_mismatch',lambda x:x['UniSuperMimic_publication'].update(policy_updates=7)),
 ('wrong_reference',lambda x:x['UniSuperMimic_publication']['producer'].update(reference_artifact_SHA='b'*64)),
 ('wrong_source_population',lambda x:x['UniSuperMimic_publication'].update(history_shape=[20000,10,86])),
 ('world_only_source',lambda x:x['UniSuperMimic_H1_test'].update(iteration=60)),
]:
    bad=deepcopy(full);edit(bad)
    refuse(lambda:validate_source(bad,contract,asdict(cfg),progress,ref),'reject_'+label)
# Use the actual vendor train condition; no fake training loop/optimizer call.
p=L/'root_augmented_world_model_candidate/v5/supermimic_wheel_leg_v3/learner.py';tree=ast.parse(p.read_bytes())
train=next(n for c in tree.body if isinstance(c,ast.ClassDef) and c.name=='SuperMimicLearner' for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='train')
condition=next(n.test for n in ast.walk(train) if isinstance(n,ast.If) and ast.unparse(n.test)=='iteration >= self.cfg.wm_only_iters')
expr=compile(ast.Expression(body=condition),'<actual_vendor_policy_phase_condition>','eval')
yes(eval(expr,{},dict(iteration=target.iteration,self=target)) is True,'restored_global_iteration_skips_repeated_world_only_phase_in_actual_train_condition')
yes(target.buffer.size==0,'no_source_replay_restore_claim')
report=dict(passed=True,count=len(checks),checks=checks,result=result,synthetic_only=True,
 actual_saved_model_read_or_hash=False,actual_SDK_or_GPU_or_physics_or_actor_forward=False,
 source_config_synthetic_hidden_only=[16,16,16],runtime_target_config_unchanged=True,
 actual_vendor_train_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),
 actual_qualified_R5_FINAL_binding=None,not_installed_or_admitted_or_next_GO=True)
with (D/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks),no_existing_model_read=True)))


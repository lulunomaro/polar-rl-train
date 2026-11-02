"""Necessary final466 one decode for full launch-to-landing actual return algorithm; CPU synthetic fixture, no physical data claim."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
from copy import deepcopy
import hashlib
import io
import json
import sys
import time
import traceback
import types

C=Path(__file__).resolve().parent;T=Path('F:\\RMPOLAR-RL\\mjcf_mod4_h1_archive_01a1967f_20261102\\workspace\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021');S=C/'source';A=Path('F:\\RMPOLAR-RL\\mjcf_mod4_h1_archive_01a1967f_20261102\\runs\\h1_wheel_height_20261103');R=C/'reports'
N=Path('F:\\RMPOLAR-RL\\mjcf_mod4_h1_archive_01a1967f_20261102\\workspace\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\RL_ACTUAL128_RETURN_PPO_PRODUCTION_V455_20261102')
sys.path[:0]=[str(S),str(A/'source'),str(N/'source'),str(N/'source/code'),str(N/'source/kernel')]
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())

def put(name,value):
    with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)

try:
    assert not(R/'CPU468_ONCE_CONSUMED_BEFORE_MODEL.json').exists()
    put('CPU468_ONCE_CONSUMED_BEFORE_MODEL.json',dict(epoch=time.time(),modelreads_max=1,
        purpose='Necessary final466 fullrestore and actual128step return temporalcredit fixture',SDK=0,physics=0,budget_writes=0))
    import torch
    torch.set_num_threads(8);torch.manual_seed(442)
    from actual_transition_learner468 import ActualTransitionLearner468,terminal_gae409
    from teacher_student292 import forward
    from tracking_wm389 import TrackingWM389
    from future_safe_wm_warm273 import FrozenTeacherContract273
    from measured_state224_v268 import MeasurementBinding268
    from tracking_reference389 import Reference389
    proofpath=A/'reports/ROOT466_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json';proof=read(proofpath)
    raw=Path(proof['path']).read_bytes()
    assert len(raw)==proof['bytes']and hashlib.sha256(raw).hexdigest()==proof['SHA']
    carrier=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
    assert carrier['kind']=='ACTUAL_RESIDUAL_PPO466_COMPLETE'and carrier['actual_new_PPO_updates']==43
    bb=carrier['world_model']['protocol']['binding']
    binding=MeasurementBinding268(tuple(bb['joint_names']),tuple(bb['body_names']),tuple(bb['motor_ids_reward_order']),bb['witness_kind'],bb['witness_SHA'])
    wm=TrackingWM389(str(N/'source/kernel'),torch.device('cpu'),teacher_contract=FrozenTeacherContract273(carrier['teacher_source_SHA'],'a'*64,True),binding=binding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512))
    wm.model.load_state_dict(carrier['world_model']['world_model'])
    wm.optimizer.load_state_dict(carrier['world_model']['world_optimizer']);wm.updates=carrier['total_WM_updates']
    original_wm_rng=carrier['world_model']['dedicated_sampling_rng'].clone()
    original_actor_rng=carrier['student']['residual_sampling_rng'].clone()
    assert original_wm_rng.numel()==original_actor_rng.numel()==16
    task=read(N/'TASK455_FROZEN.json')
    reference=Reference389(N/'reference389.npz',task['reference'],binding.joint_names,'cpu',torch.zeros(2,3))
    env=types.SimpleNamespace(scene={'robot':types.SimpleNamespace(joint_names=list(binding.joint_names),body_names=list(binding.body_names))},target389=torch.tensor([[.8,0.,.27,0.]]).repeat(80,1))
    fixturecarrier=dict(carrier,student=dict(carrier['student'],residual_sampling_rng=torch.Generator(device='cpu').manual_seed(442).get_state()))
    learner=ActualTransitionLearner468(wm,fixturecarrier,reference,env,binding,H(proofpath),put)
    saved=carrier['student']
    def same(a,b):
        if torch.is_tensor(a):return torch.equal(a,b)
        if isinstance(a,dict):return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
        if isinstance(a,(list,tuple)):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
        return a==b
    for key,net in(('actor',learner.actor),('critic',learner.critic),('target_critic',learner.target_critic),('residual_origin_actor',learner.residual_origin_actor)):
        assert same(net.state_dict(),saved[key+'_state_dict'])
    for key,opt in learner.optimizers.items():assert same(opt.state_dict()['state'],saved[key+'_optimizer']['state'])
    assert all(int(v['step'])==52554 for v in wm.optimizer.state.values())
    actual=saved['actual_RL_rollout'];assert 0<len(actual)<128
    # Saved observation/reward rows are fixture coordinates only. Generate new
    # latent/logprob/value explicitly, so this is never relabelled onpolicy data.
    generator=torch.Generator(device='cpu').manual_seed(442)
    learner.rollout=[]
    deterministic_delta=0.
    for i in range(128):
        row=deepcopy(actual[i%len(actual)])
        row['reward']=1./(1.-row['reward'].clamp(1e-30,1.).log())
        with torch.no_grad():
            mean=forward(learner.actor,row['x'])-forward(learner.residual_origin_actor,row['x'])
            row['latent_std']=learner.exploration_std(mean)
            row['latent']=mean+row['latent_std']*torch.randn(mean.shape,generator=generator)
            row['old_log_prob']=learner.log_prob(row['latent'],mean)
            row['old_value']=forward(learner.critic,row['cx']).squeeze(-1)
            expected=torch.tanh(mean)
            deterministic_delta=max(deterministic_delta,float((torch.tanh(mean)-expected).abs().max()))
        learner.rollout.append(row)
    x=torch.stack([row['x']for row in learner.rollout]).flatten(0,1)
    latent=torch.stack([row['latent']for row in learner.rollout]).flatten(0,1)
    oldlog=torch.stack([row['old_log_prob']for row in learner.rollout]).flatten()
    with torch.no_grad():
        mean=forward(learner.actor,x)-forward(learner.residual_origin_actor,x)
        sigma=learner.exploration_std(mean)
        ratio=torch.exp(learner.log_prob(latent,mean)-oldlog)
        analytic=torch.distributions.Normal(mean,sigma).log_prob(latent).sum(-1)
        logerror=float((analytic-learner.log_prob(latent,mean)).abs().max())
        shifted=mean+.03
        exactKL=torch.distributions.kl_divergence(torch.distributions.Normal(mean,sigma),torch.distributions.Normal(shifted,learner.exploration_std(shifted))).sum(-1).mean()
        KLerror=float((exactKL-learner.policy_KL(mean,shifted)).abs())
    assert torch.allclose(ratio,torch.ones_like(ratio),atol=1e-4,rtol=1e-4)
    assert logerror<5e-5 and KLerror<1e-5
    before={key:deepcopy(net.state_dict())for key,net in(('actor',learner.actor),('critic',learner.critic),('target_critic',learner.target_critic))}
    optbefore={key:deepcopy(opt.state_dict())for key,opt in learner.optimizers.items()}
    diagnostic=learner.update(apply_step=False)
    assert diagnostic['actor_grad_norm']>0 and diagnostic['critic_grad_norm']>0
    candidate=learner.update()
    trust=candidate['actor_trust_step']
    assert candidate['Pi_updates']==candidate['critic_updates']==candidate['PPO_updates']==1
    assert trust['applied']and trust['actual_KL']<=.01 and trust['actual_max_action_delta']<=.05
    assert all(int(learner.actor_optimizer.state[p]['step'])==(42940 if name=='distribution.std_param'else 56762)for name,p in learner.actor.named_parameters())
    assert all(int(slot['step'])==13822 for slot in learner.critic_optimizer.state.values())
    assert all(p.grad is None for p in wm.model.parameters())and all(p.grad is None for p in learner.residual_origin_actor.parameters())
    # Restore the CPU proposal; no optimized CPUweights become training source.
    learner.actor.load_state_dict(before['actor']);learner.critic.load_state_dict(before['critic']);learner.target_critic.load_state_dict(before['target_critic'])
    for key,opt in learner.optimizers.items():opt.load_state_dict(optbefore[key]);assert same(opt.state_dict(),optbefore[key])
    plain=torch.nn.Sequential(torch.nn.Linear(103,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,32),torch.nn.ELU(),torch.nn.Linear(32,6))
    plain.load_state_dict({k.removeprefix('mlp.'):v for k,v in saved['actor_state_dict'].items()if k.startswith('mlp.')})
    with torch.no_grad():interface_delta=float((plain(x)-forward(learner.actor,x)).abs().max())
    assert interface_delta<1e-6 and deterministic_delta==0.
    reward=torch.tensor([[.6],[100.]]);done=torch.ones(2,1,dtype=torch.bool)
    _,ret=terminal_gae409(reward,torch.tensor([[2.],[3.]]),torch.tensor([[123.],[999.]]),done)
    assert torch.allclose(ret,reward,atol=1e-5,rtol=0.)
    z=torch.linspace(-5,5,4001);weights=torch.softmax(-z.square()/2,dim=0)
    old=torch.tanh(3+.15*z);new=torch.tanh(3+learner.exploration_std(torch.tensor(3.))*z)
    std=lambda a:float(torch.sqrt((weights*(a-(weights*a).sum()).square()).sum()))
    assert std(new)>100*std(old)
    # A launch action before the old32boundary must see the later event, and
    # a reset prevents the next episode's large reward from entering it.
    rr=torch.zeros(128,1);rr[56]=1.;rr[100]=100.
    dd=torch.zeros(128,1,dtype=torch.bool);dd[56]=True;dd[-1]=True
    vv=torch.zeros_like(rr);nn=torch.zeros_like(rr)
    adv,returns=terminal_gae409(rr,vv,nn,dd,gamma=.99,lam=learner.gae_lambda)
    assert learner.rollout_controls==128 and learner.gae_lambda==1.
    assert abs(float(returns[0])-.99**56)<1e-5
    assert abs(float(returns[57])-100*.99**43)<1e-4
    truncated,_=terminal_gae409(rr[:32],vv[:32],nn[:32],dd[:32],gamma=.99,lam=.95)
    assert float(truncated[0])==0.
    delayed_event_fixture=dict(event_control57=1.,nextepisode_control101=100.,done_control57=True,
        candidate_return_control1=float(returns[0]),expected=.99**56,
        old32_return_control1=float(truncated[0]),next_episode_leak=False,lambda_value=learner.gae_lambda,
        total_controls=learner.rollout_controls,synthetic_no_physics=True)
    report=dict(epoch=time.time(),passed=True,sourceSHA=proof['SHA'],modelreads=1,SDK=0,physics=0,CUDA=torch.cuda.is_initialized(),
        source_offsets=[56761,13821,52554],delayed_event_fixture=delayed_event_fixture,full_source_networks_Adam_EMA_origin_restored=True,
        CUDA_samplingRNG_preserved_opaque_CPUfixture_explicit=True,old_learnedSTD17Adam42940_frozen=True,
        saved_coordinate_rows=len(actual),synthetic_fixture_controls=128,synthetic_new_latents_not_actual_onpolicy=True,
        logprob_vs_torch_Normal_maxerror=logerror,KL_vs_torch_Normal_error=KLerror,ratio_mean=float(ratio.mean()),
        diagnostic=diagnostic,candidate=candidate,CPUweights_and_Adam_restored=True,production_optimizer_steps=0,
        deterministic_eval_interface_delta=interface_delta,deterministic_action_delta=deterministic_delta,
        residual_std_at_mean3=dict(old=std(old),candidate=std(new)),terminalGAE_returns=ret.flatten().tolist(),
        learnerSHA=H(S/'actual_transition_learner468.py'),new_reward=True,productionGO=False,physicalskill_unproven=True)
    put('CPU468_LAUNCH_LANDING_RETURN_FULL_RESTORE_ADMISSION.json',report)
    print(json.dumps(report),flush=True)
except BaseException:
    put('CPU468_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True))
    raise

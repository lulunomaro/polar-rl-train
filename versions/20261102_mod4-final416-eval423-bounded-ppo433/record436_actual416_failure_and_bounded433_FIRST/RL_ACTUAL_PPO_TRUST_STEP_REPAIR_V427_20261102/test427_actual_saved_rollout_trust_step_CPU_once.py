"""Necessaryfinal416singledecode: actualsavedrollout candidateAdamstep, no physics."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
from pathlib import Path
from copy import deepcopy
import ast
import hashlib
import io
import json
import sys
import time
import traceback
import types

C = Path(__file__).resolve().parent
T = C.parent
S = C / 'source'
R = C / 'reports'
N = T / 'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
sys.path[:0] = [str(S),str(S / 'code'),str(S / 'kernel')]
read = lambda path: json.loads(path.read_bytes())
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def put(name,value):
    with (R / name).open('x',encoding='utf8') as stream:
        json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)

try:
    assert not (R / 'CPU427_ONCE_CONSUMED_BEFORE_MODEL.json').exists()
    put('CPU427_ONCE_CONSUMED_BEFORE_MODEL.json',dict(epoch=time.time(),modelreads_max=1,
        purpose='Necessarynewtruststepalgorithmfinal416fullrestore/actualsavedrollouttest',SDK=0,physics=0,training_budget_writes=0))
    import torch
    torch.set_num_threads(8)
    torch.manual_seed(427)
    from actual_transition_learner427 import ActualTransitionLearner427,terminal_gae409
    from teacher_student292 import forward
    from tracking_wm389 import TrackingWM389
    from future_safe_wm_warm273 import FrozenTeacherContract273
    from measured_state224_v268 import MeasurementBinding268
    from tracking_reference389 import Reference389
    proofpath = N / 'reports/ROOT416_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
    proof = read(proofpath)
    raw = Path(proof['path']).read_bytes()
    assert len(raw) == proof['bytes'] and hashlib.sha256(raw).hexdigest() == proof['SHA']
    carrier = torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False)
    del raw
    assert carrier['kind'] == 'ACTUAL_RESIDUAL_PPO416_COMPLETE' and carrier['actual_new_PPO_updates'] == 160
    bb = carrier['world_model']['protocol']['binding']
    binding = MeasurementBinding268(tuple(bb['joint_names']),tuple(bb['body_names']),tuple(bb['motor_ids_reward_order']),bb['witness_kind'],bb['witness_SHA'])
    wm = TrackingWM389(str(S / 'kernel'),torch.device('cpu'),
        teacher_contract=FrozenTeacherContract273(carrier['teacher_source_SHA'],'a'*64,True),binding=binding,
        seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512))
    wm.model.load_state_dict(carrier['world_model']['world_model'])
    wm.optimizer.load_state_dict(carrier['world_model']['world_optimizer'])
    wm.updates = carrier['total_WM_updates']
    preserved_WM_CUDA_RNG=carrier['world_model']['dedicated_sampling_rng'].clone()
    assert preserved_WM_CUDA_RNG.numel()==16
    # CPU fixture samples noWM transitions; CUDAstate is preserved opaque, notloadedintoCPUgenerator.
    task = read(N / 'TASK416_FROZEN.json')
    reference = Reference389(C / 'reference389.npz',task['reference'],binding.joint_names,'cpu',torch.zeros(2,3))
    env = types.SimpleNamespace(scene={'robot':types.SimpleNamespace(joint_names=list(binding.joint_names),body_names=list(binding.body_names))},
        target389=torch.tensor([[.8,0.,.27,0.]]).repeat(80,1))
    preserved_actor_CUDA_RNG=carrier['student']['residual_sampling_rng'].clone()
    assert preserved_actor_CUDA_RNG.numel()==16
    fixturecarrier=dict(carrier,student=dict(carrier['student'],residual_sampling_rng=torch.Generator(device='cpu').manual_seed(427).get_state()))
    learner = ActualTransitionLearner427(wm,fixturecarrier,reference,env,binding,H(proofpath),put)
    saved = carrier['student']
    for key,net in (('actor',learner.actor),('critic',learner.critic),('target_critic',learner.target_critic),('residual_origin_actor',learner.residual_origin_actor)):
        assert all(torch.equal(value,saved[key+'_state_dict'][name]) for name,value in net.state_dict().items())
    def same_tree(a,b):
        if torch.is_tensor(a):
            return torch.equal(a,b)
        if isinstance(a,dict):
            return a.keys()==b.keys() and all(same_tree(a[key],b[key]) for key in a)
        if isinstance(a,(list,tuple)):
            return len(a)==len(b) and all(same_tree(x,y) for x,y in zip(a,b))
        return a==b
    for name,opt in learner.optimizers.items():
        assert same_tree(opt.state_dict()['state'],saved[name+'_optimizer']['state'])
    actual = saved['actual_RL_rollout']
    assert 0 < len(actual) < 32
    # Repeat preserved actual rows only to fill a CPU algorithm fixture. This
    # does not create additional physical data or qualify as an onpolicyrollout.
    learner.rollout = [deepcopy(actual[i%len(actual)]) for i in range(32)]
    x = torch.stack([row['x'] for row in learner.rollout]).flatten(0,1)
    latent = torch.stack([row['latent'] for row in learner.rollout]).flatten(0,1)
    oldlog = torch.stack([row['old_log_prob'] for row in learner.rollout]).flatten()
    with torch.no_grad():
        mean = forward(learner.actor,x)-forward(learner.residual_origin_actor,x)
        ratio = torch.exp(learner.log_prob(latent,mean)-oldlog)
    assert torch.allclose(ratio,torch.ones_like(ratio),atol=1e-4,rtol=1e-4)
    before_weights = deepcopy(learner.actor.state_dict())
    before_opt = deepcopy(learner.actor_optimizer.state_dict())
    before_critic = deepcopy(learner.critic.state_dict())
    before_critic_opt = deepcopy(learner.critic_optimizer.state_dict())
    before_target = deepcopy(learner.target_critic.state_dict())
    diagnostic = learner.update(apply_step=False)
    assert diagnostic['actor_grad_norm']>0 and diagnostic['critic_grad_norm']>0
    actor_gradient = [None if p.grad is None else p.grad.detach().clone() for p in learner.actor.parameters()]
    learner.actor_optimizer.step()
    with torch.no_grad():
        unbounded = forward(learner.actor,x)-forward(learner.residual_origin_actor,x)
        unbounded_KL = float(.5*((unbounded-mean)/.15).square().sum(-1).mean())
        unbounded_delta = float((torch.tanh(unbounded)-torch.tanh(mean)).abs().max())
    learner.actor.load_state_dict(before_weights)
    learner.actor_optimizer.load_state_dict(deepcopy(before_opt))
    for p,grad in zip(learner.actor.parameters(),actor_gradient):
        p.grad = None if grad is None else grad.clone()
    assert same_tree(learner.actor_optimizer.state_dict(),before_opt)
    accepted = learner.update()
    assert accepted['PPO_updates']==accepted['Pi_updates']==accepted['critic_updates']==1
    trust = accepted['actor_trust_step']
    assert trust['applied'] and trust['actual_KL']<=.01 and trust['actual_max_action_delta']<=.05
    assert all(int(slot['step'])==56305 for slot in learner.actor_optimizer.state.values())
    assert all(int(slot['step'])==13365 for slot in learner.critic_optimizer.state.values())
    assert all(int(slot['step'])==25556 for slot in wm.optimizer.state.values())
    assert all(parameter.grad is None for parameter in wm.model.parameters())
    assert all(parameter.grad is None for parameter in learner.residual_origin_actor.parameters())
    # Restorethefixture; no candidate weights/Adamarepersisted or usedas source.
    learner.actor.load_state_dict(before_weights)
    learner.actor_optimizer.load_state_dict(before_opt)
    learner.critic.load_state_dict(before_critic)
    learner.critic_optimizer.load_state_dict(before_critic_opt)
    learner.target_critic.load_state_dict(before_target)
    reward=torch.tensor([[.6],[100.]])
    value=torch.tensor([[2.],[3.]])
    nxt=torch.tensor([[123.],[999.]])
    done=torch.ones(2,1,dtype=torch.bool)
    _,returns=terminal_gae409(reward,value,nxt,done)
    assert torch.allclose(returns,reward,atol=1e-5,rtol=0.)
    # SDK-free copiedactor path equals deterministic MLPModel onactualinputs.
    plain=torch.nn.Sequential(torch.nn.Linear(103,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,32),torch.nn.ELU(),torch.nn.Linear(32,6))
    plain.load_state_dict({k.removeprefix('mlp.'):v for k,v in before_weights.items() if k.startswith('mlp.')})
    with torch.no_grad():
        interface_delta=float((plain(x)-forward(learner.actor,x)).abs().max())
    assert interface_delta<1e-6
    report=dict(epoch=time.time(),passed=True,sourceSHA=proof['SHA'],modelreads=1,CUDA=torch.cuda.is_initialized(),SDK=0,physics=0,
        source_offsets=[56304,13364,25556],source_network_Adam_EMA_origin_restore_exact=True,
        CUDA_RNG_preserved_opaque_not_CPUloaded=True,CPU_fixture_rng_explicit=True,production_GPU_RNG_restore_code_unchanged=True,
        actualsavedrows=len(actual),repeatedCPUfixturecontrols=32,not_new_physical_onpolicy_samples=True,
        original_nominal_postAdam=dict(KL=unbounded_KL,max_normalized_residual_delta=unbounded_delta),
        candidate=accepted,allcandidateweightsAdam_restored_afterCPUfixture=True,
        committed_training_optimizersteps=0,CPU_candidate_Adamsteps_restored=True,
        terminalGAE_returns=returns.flatten().tolist(),deterministic_eval_actor_interface_max_delta=interface_delta,
        learnerSHA=H(S / 'actual_transition_learner427.py'),productionGO=False,
        physicalsuccess_not_demonstrated=True)
    put('CPU427_ACTUAL_SAVED_ROLLOUT_TRUST_STEP_ADMISSION.json',report)
    print(json.dumps(report),flush=True)
except BaseException:
    put('CPU427_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True))
    raise

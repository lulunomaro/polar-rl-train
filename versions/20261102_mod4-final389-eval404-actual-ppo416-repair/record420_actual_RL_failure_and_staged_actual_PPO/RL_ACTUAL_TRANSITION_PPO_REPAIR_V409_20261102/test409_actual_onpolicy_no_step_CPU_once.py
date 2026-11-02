"""One necessary final389 read for a new actual-transition-RL algorithm; no optimizer step."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib
import io
import json
import sys
import time
import traceback
import types

N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';R=N/'reports'
sys.path[:0]=[str(S),str(S/'code'),str(S/'kernel')]
def put(name,value):
 with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
try:
 assert not(R/'CPU409_ONCE_CONSUMED_BEFORE_MODEL.json').exists()
 put('CPU409_ONCE_CONSUMED_BEFORE_MODEL.json',dict(epoch=time.time(),modelreads_max=1,
    purpose='Necessary real389fullrestore and actualRL PPOgrad/terminalGAE no-step fixture',optimizersteps=0,SDK=0))
 import torch
 torch.set_num_threads(8);torch.manual_seed(409)
 from actual_transition_learner409 import ActualTransitionLearner409,terminal_gae409
 from tracking_reference389 import Reference389
 from tracking_wm389 import TrackingWM389
 from future_safe_wm_warm273 import FrozenTeacherContract273
 from measured_state224_v268 import MeasurementBinding268
 from teacher_student292 import forward
 proofpath=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102/reports/ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
 proof=json.loads(proofpath.read_bytes())
 raw=Path(proof['path']).read_bytes()
 assert len(raw)==proof['bytes']and hashlib.sha256(raw).hexdigest()==proof['SHA']
 carrier=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
 assert carrier['kind']=='REFERENCE_TRACKING_BPTT389_COMPLETE'
 bb=carrier['world_model']['protocol']['binding']
 binding=MeasurementBinding268(tuple(bb['joint_names']),tuple(bb['body_names']),tuple(bb['motor_ids_reward_order']),bb['witness_kind'],bb['witness_SHA'])
 wm=TrackingWM389(str(S/'kernel'),torch.device('cpu'),teacher_contract=FrozenTeacherContract273(carrier['teacher_source_SHA'],'a'*64,True),binding=binding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512))
 wm.model.load_state_dict(carrier['world_model']['world_model']);wm.optimizer.load_state_dict(carrier['world_model']['world_optimizer']);wm.updates=20419
 task=json.loads((T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102/TASK389_FROZEN.json').read_bytes())
 reference=Reference389(N/'reference389.npz',task['reference'],binding.joint_names,'cpu',torch.zeros(2,3))
 env=types.SimpleNamespace(scene={'robot':types.SimpleNamespace(joint_names=list(binding.joint_names),body_names=list(binding.body_names))},target389=torch.tensor([[.8,0.,.27,0.]]).repeat(80,1))
 learner=ActualTransitionLearner409(wm,carrier,reference,env,binding,hashlib.sha256(proofpath.read_bytes()).hexdigest(),put)
 saved=carrier['student']
 for key,net in(('actor',learner.actor),('critic',learner.critic),('target_critic',learner.target_critic),('residual_origin_actor',learner.residual_origin_actor)):
  assert all(torch.equal(value,saved[key+'_state_dict'][name])for name,value in net.state_dict().items())
 for key,optimizer in learner.optimizers.items():
  actual=optimizer.state_dict();source=saved[key+'_optimizer']
  for pid,slots in source['state'].items():
   for name,value in slots.items():
    assert torch.equal(value,actual['state'][pid][name])if torch.is_tensor(value)else value==actual['state'][pid][name]
 assert not any(parameter.requires_grad for parameter in learner.residual_origin_actor.parameters())
 before={key:{name:value.detach().clone()for name,value in net.state_dict().items()}for key,net in learner.networks.items()}
 for tick in range(32):
  x=torch.randn(80,103);cx=torch.randn(80,106)
  with torch.no_grad():
   mean=forward(learner.actor,x)-forward(learner.residual_origin_actor,x)
   latent=mean+.15*torch.randn_like(mean)
   value=forward(learner.critic,cx).squeeze(-1)
  reward=torch.linspace(.1,1.,80)+(tick%3)*.01
  done=torch.arange(80)%7==tick%7
  learner.rollout.append(dict(x=x,cx=cx,latent=latent,old_log_prob=learner.log_prob(latent,mean).detach(),old_value=value,
      reward=reward,done=done,next_value=value+1.))
 diag=learner.update(apply_step=False)
 assert diag['actor_grad_norm']>0 and diag['critic_grad_norm']>0
 assert diag['actual_onpolicy_samples']==2560 and diag['Pi_updates']==diag['critic_updates']==diag['PPO_updates']==0
 for key,net in learner.networks.items():
  assert all(torch.equal(value,before[key][name])for name,value in net.state_dict().items())
 # A terminal transition must not see a nextstate value or following episode reward.
 reward=torch.tensor([[.6],[100.]])
 old=torch.tensor([[2.],[3.]])
 nxt=torch.tensor([[123.],[999.]])
 done=torch.tensor([[True],[True]])
 advantage,returns=terminal_gae409(reward,old,nxt,done)
 assert torch.allclose(returns,reward,atol=1e-5,rtol=0.)
 assert all(parameter.grad is None for parameter in wm.model.parameters())
 assert all(parameter.grad is None for parameter in learner.residual_origin_actor.parameters())
 assert all(int(value['step'])==20419 for value in wm.optimizer.state.values())
 report=dict(epoch=time.time(),passed=True,modelreads=1,optimizersteps=0,SDK=0,physics=0,CUDA=torch.cuda.is_initialized(),
    sourceSHA=proof['SHA'],sourceOffsets=[56144,13204,20419],full_actorcriticEMA_origin_Adam_restore=True,
    teacherSTD_frozen=True,actualrewarddone_actor=True,WM_actorgradients=False,terminalGAE_returns=returns.flatten().tolist(),
    synthetic_fixture_only=True,actual_physics_skill_not_passed=True,diagnostic=diag,
    learnerSHA=hashlib.sha256((S/'actual_transition_learner409.py').read_bytes()).hexdigest(),
    production_integration_and_GO_pending=True)
 put('CPU409_REAL_TRANSITION_RL_NO_STEP_ADMISSION.json',report)
 print(json.dumps(report),flush=True)
except BaseException:
 put('CPU409_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True));raise

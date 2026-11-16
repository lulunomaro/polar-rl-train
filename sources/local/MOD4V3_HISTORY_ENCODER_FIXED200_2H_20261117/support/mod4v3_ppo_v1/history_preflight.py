"""Native PhysX full-DR preflight with zero optimizer/PPO updates."""
import json,torch,numpy as np,time
from pathlib import Path
from tensordict import TensorDict
from .history_common import HistoryQueue,LocalHistoryActor

def run(env,algorithm,pack,history,job,plan,current):
 started=time.monotonic();device=env.device;aux=algorithm._history_aux
 # Cross-runtime queue: independent NumPy assembly versus exact GPU assembly/reset.
 rng=np.random.default_rng(67);frames=rng.normal(size=(30,4,35)).astype(np.float32);gpu=HistoryQueue();npq=None;maxerr=0.
 for k,f in enumerate(frames):
  done=np.array([k%7==0,k%11==0,False,k==19]);t=torch.as_tensor(f,device=device)
  if npq is None:npq=np.repeat(f[:,None,:],12,1);got=gpu.reset(t)
  else:
   npq=np.concatenate((npq[:,1:],f[:,None]),1);npq[done]=np.repeat(f[done,None,:],12,1);got=gpu.append(t,torch.as_tensor(done,device=device))
  maxerr=max(maxerr,float(np.abs(got.cpu().numpy()-npq.reshape(4,-1)).max()))
 assert maxerr==0
 obs=TensorDict(current,batch_size=[env.num_envs]);algorithm.eval_mode();local=LocalHistoryActor().load_checkpoint(torch.load(plan['parent'],map_location='cpu',weights_only=False)).eval()
 with torch.no_grad():
  remote_action=algorithm.actor(obs);local_action=local(obs['policy'].cpu(),obs['obs_history'].cpu());action_error=float((remote_action.cpu()-local_action).abs().max())
 assert action_error<2e-5,action_error
 loss=aux.compute(algorithm,obs);algorithm.optimizer.zero_grad();loss.backward();encnorm=float(torch.sqrt(sum(p.grad.square().sum()for p in algorithm.actor.encoder.parameters()if p.grad is not None)));newnorm=float(algorithm.actor.mlp[0].weight.grad[:,35:].norm());allfinite=all(bool(torch.isfinite(p.grad).all())for p in list(algorithm.actor.parameters())+list(algorithm.critic.parameters())if p.grad is not None)
 assert allfinite and encnorm>0 and newnorm>0
 algorithm.optimizer.zero_grad();aux.steps=0;aux.counts.zero_();aux.window=[]
 resets=0;contact_targets=[];vel_targets=[]
 for k in range(16):
  with torch.inference_mode():raw,reward,term,timeout,extra=env.step(algorithm.actor(obs).clamp(-6,6))
  raw=pack(raw,term|timeout);obs=TensorDict(raw,batch_size=[env.num_envs]);b=raw['obs_history'].reshape(-1,12,35);assert torch.equal(b[:,-1],raw['policy']);done=term|timeout
  if bool(done.any()):assert torch.equal(b[done],raw['policy'][done,None,:].expand(-1,12,-1))
  resets+=int(done.sum());contact_targets.append(raw['critic'][:,69:71]);vel_targets.append(raw['critic'][:,28:31]);assert bool(torch.isfinite(reward).all())
 assert not env.enforce_closure_reset and env.num_envs==2048
 result=dict(passed=True,PPO_updates=0,optimizer_updates=0,history_H=12,history_dim=420,queue_numpy_gpu_max_error=maxerr,Isaac_MuJoCo_forward_max_error=action_error,finite_gradients=allfinite,encoder_supervision_grad_norm=encnorm,new_latent_columns_grad_norm=newnorm,physics_steps=16*8,simulated_policy_steps=16,autoresets_seen=resets,stair_envs=int(env.continuous_stair_mask.sum()),normal_keep_envs=int((~env.continuous_stair_mask).sum()),critic_velocity_slice=[28,31],critic_contact_slice=[69,71],contact_target_range=[float(torch.stack(contact_targets).min()),float(torch.stack(contact_targets).max())],physics_dt=float(env.cfg.sim.dt),leg_feedback_dt=.01,wheel_feedback_dt=.0025,policy_dt=.02,closure_2mm_only_diagnostic=True,full_DR=env.mild_dr.summary(),wall_seconds=time.monotonic()-started)
 (Path(job)/'HISTORY_NATIVE_PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n');print('HISTORY_NATIVE_PREFLIGHT',json.dumps(result),flush=True);return result

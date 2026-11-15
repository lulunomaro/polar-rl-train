"""Native PPO gradient diagnosis with optimizer.step replaced by a no-op."""
from pathlib import Path
import sys,json,types,time

def run_probe(env,algorithm):
 import torch
 from tensordict import TensorDict
 start=time.time();env.begin_training_counts();obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);policy=algorithm.get_policy()
 for _ in range(160):
  with torch.inference_mode():raw,reward,term,timeout,_=env.step(policy(obs,stochastic_output=False))
  obs=TensorDict(raw,batch_size=[env.num_envs])
 algorithm.train_mode()
 with torch.inference_mode():
  for _ in range(24):
   action=algorithm.act(obs);raw,reward,term,timeout,_=env.step(action)
   terminal=TensorDict(env.terminal_observations,batch_size=[env.num_envs]);reward=reward+algorithm.gamma*algorithm.critic(terminal).squeeze(-1)*timeout
   obs=TensorDict(raw,batch_size=[env.num_envs]);algorithm.process_env_step(obs,reward,term|timeout,{})
  algorithm.compute_returns(obs)
 actor=list(algorithm.actor.named_parameters());critic=list(algorithm.critic.named_parameters());before={('actor',n):p.detach().clone()for n,p in actor};before.update({('critic',n):p.detach().clone()for n,p in critic})
 state={'aux_capture':False,'grads':{},'aux':None,'records':[]};hooks=[]
 def hook(key):
  def capture(gradient):
   if not state['aux_capture']:state['grads'][key]=gradient.detach().clone()
   return gradient
  return capture
 for family,named in [('actor',actor),('critic',critic)]:
  for name,param in named:
   if param.requires_grad:hooks.append(param.register_hook(hook((family,name))))
 retention=algorithm._teacher_retention;original_compute=retention.compute;original_step=algorithm.optimizer.step
 def compute(self,alg,observations):
  value=original_compute(alg,observations);state['aux_capture']=True
  grads=torch.autograd.grad(value,[p for _,p in actor],retain_graph=True,allow_unused=True)
  state['aux']=[torch.zeros_like(p)if g is None else g.detach().clone()for (_,p),g in zip(actor,grads)]
  # Read the exact per-sample surrogate already computed by native PPO.
  native=sys._getframe(1).f_locals;mask=observations['teacher_keep'].reshape(-1)<.5
  per_sample=torch.max(native['surrogate'],native['surrogate_clipped']).reshape(-1)
  entropy=native['entropy'].reshape(-1)
  target_loss=per_sample[mask].sum()/len(mask)-alg.entropy_coef*entropy[mask].sum()/len(mask)
  target_grads=torch.autograd.grad(target_loss,[p for _,p in actor],retain_graph=True,allow_unused=True)
  state['target']=[torch.zeros_like(p)if g is None else g.detach().clone()for (_,p),g in zip(actor,target_grads)]
  state['target_fraction']=float(mask.float().mean())
  state['aux_capture']=False;state['grads'].clear();return value
 def noop_step(*args,**kwargs):
  total=[state['grads'].get(('actor',n),torch.zeros_like(p))for n,p in actor];aux=state['aux'];ppo=[x-y for x,y in zip(total,aux)];crit=[state['grads'].get(('critic',n),torch.zeros_like(p))for n,p in critic]
  def norm(values):return torch.sqrt(sum(v.square().sum()for v in values))
  a=norm(aux);b=norm(ppo);c=norm(total);v=norm(crit);target_norm=norm(state['target']);target_dot=sum(x.mul(y).sum()for x,y in zip(aux,state['target']));dot=sum(x.mul(y).sum()for x,y in zip(aux,ppo));post=norm([p.grad for _,p in actor+critic if p.grad is not None]);pre=torch.sqrt(c*c+v*v)
  state['records'].append(dict(teacher_actor_gradient_norm=float(a),PPO_plus_entropy_actor_gradient_norm=float(b),combined_actor_gradient_norm=float(c),value_critic_gradient_norm=float(v),teacher_to_PPO_norm_ratio=float(a/b.clamp_min(1e-12)),teacher_PPO_cosine=float(dot/(a*b).clamp_min(1e-12)),teacher_projection_fraction_on_PPO=float(dot/b.square().clamp_min(1e-12)),aggregate_postclip_to_preclip_norm=float(post/pre.clamp_min(1e-12)),actor_clip_scale=float(norm([p.grad for _,p in actor if p.grad is not None])/c.clamp_min(1e-12)),critic_clip_scale=float(norm([p.grad for _,p in critic if p.grad is not None])/v.clamp_min(1e-12)),weighted_specialist_PPO_gradient_norm=float(target_norm),teacher_to_weighted_specialist_ratio=float(a/target_norm.clamp_min(1e-12)),teacher_specialist_PPO_cosine=float(target_dot/(a*target_norm).clamp_min(1e-12)),specialist_sample_fraction=state['target_fraction']))
  return None
 retention.compute=types.MethodType(compute,retention);algorithm.optimizer.step=noop_step
 try:losses=algorithm.update()
 finally:
  algorithm.optimizer.step=original_step;retention.compute=original_compute
  for h in hooks:h.remove()
 unchanged=all(torch.equal(before[('actor',n)],p)for n,p in actor)and all(torch.equal(before[('critic',n)],p)for n,p in critic)
 assert unchanged,'Unexpected parameter mutation in zero-update gradient diagnosis'
 assert len(state['records'])==12,len(state['records'])
 keys=state['records'][0].keys();summary={k:sum(r[k]for r in state['records'])/len(state['records'])for k in keys}
 return dict(no_optimizer_updates=True,actual_optimizer_steps=0,optimizer_step_calls_intercepted=12,parameters_unchanged=unchanged,num_envs=env.num_envs,steps=184,warmup_steps=160,rollout_steps=24,records=state['records'],mean=summary,losses=losses,pitch=env.pitch_summary(),done_totals=dict(env.done_totals),wall_seconds=time.time()-start,scope='One native on-policy rollout near first hard stop,2048mixed/fullDR; actual PPO+entropy versus actual teacher loss gradients before separate actor/critic norm clipping; diagnostic gradients only. One batch is not whole-run causal ablation.')

if __name__=='__main__':
 plan_path=Path(sys.argv[sys.argv.index('--plan')+1]);plan=json.loads(plan_path.read_text());sys.path.insert(0,plan['support'])
 module=types.ModuleType('mod4v3_ppo_v1.pitch_stability_checks');module.run_probe=run_probe;sys.modules[module.__name__]=module
 from mod4v3_ppo_v1.continuous_stair_train import main
 main()

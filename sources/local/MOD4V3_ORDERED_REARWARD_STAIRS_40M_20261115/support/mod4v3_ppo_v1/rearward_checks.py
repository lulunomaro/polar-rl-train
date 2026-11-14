"""Functional probe for the new supported reset/reward; no PPO or new graduation gate."""
import time,torch
from tensordict import TensorDict

def run_probe(env,algorithm):
 env.begin_training_counts();obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);policy=algorithm.get_policy();peak=0.;samples=[];start=time.time()
 initial=env.rearward.summary()
 for k in range(600):
  with torch.inference_mode():action=policy(obs,stochastic_output=False);raw,reward,term,timeout,_=env.step(action)
  if not bool(torch.isfinite(reward).all()):raise RuntimeError('Nonfinite reward in supported-stair probe')
  obs=TensorDict(raw,batch_size=[env.num_envs]);peak=max(peak,float(env.closure_error.max()))
  if k%40==0:samples.append(dict(step=k,course=env.rearward.summary(),done_totals=dict(env.done_totals),finite_reward=True))
 return dict(no_optimizer_updates=True,steps=600,num_envs=env.num_envs,wall_seconds=time.time()-start,initial=initial,final=env.rearward.summary(),samples=samples,max_closure_m=peak,done_totals=env.done_totals,scope='Exact new supported resets and physical contact/reward routing; ordinary per-environment guard resets retained',original_physics_and_envelope=True)

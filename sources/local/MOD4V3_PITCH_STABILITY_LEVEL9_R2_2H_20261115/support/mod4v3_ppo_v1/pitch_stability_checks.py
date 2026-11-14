"""Zero-update transition probe; no policy learning claim."""
import time,torch
from tensordict import TensorDict

def run_probe(env,algorithm):
 env.begin_training_counts();obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);policy=algorithm.get_policy();peak=0.;samples=[];start=time.time()
 initial=env.pitch_summary()
 for k in range(200):
  with torch.inference_mode():
   action=policy(obs,stochastic_output=False);raw,reward,term,timeout,_=env.step(action)
  if not bool(torch.isfinite(reward).all()):raise RuntimeError('Nonfinite pitch probe reward')
  obs=TensorDict(raw,batch_size=[env.num_envs]);peak=max(peak,float(env.closure_error.max()))
  if k==2:
   mask=env.terrain_family==9;distance=(env.view.data.root_pos_w[mask,:2]-env._center()[mask,:2]).abs().amax(-1)
   assert bool((distance<4.).all()),'Random terrain spawn outside original tile boundary'
   initial['actual_random_spawn_abs_xy_max_m']=float(distance.max())
  if k%50==0:samples.append(dict(step=k,pitch=env.pitch_summary(),done_totals=dict(env.done_totals)))
 final=env.pitch_summary();assert final['random_uniform_levels']==[9]
 return dict(no_optimizer_updates=True,steps=200,num_envs=env.num_envs,wall_seconds=time.time()-start,initial=initial,final=final,samples=samples,max_closure_m=peak,done_totals=env.done_totals,scope='Actual level9 origin/grounded transition commands and body-pitch reward wiring; not learned-policy improvement',original_physics_and_envelope=True)

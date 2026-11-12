"""One short, full-population native functional probe; no PPO updates."""
import torch,time
from tensordict import TensorDict
from .scut_flat_env import tensor

def run_probe(env,algorithm):
 env.begin_training_counts();obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);policy=algorithm.get_policy();start=time.time();samples=[];max_closure=0.;pitch_reward_samples=0;geometry=env._center();stairs=env.continuous_stair_mask;retained=env.terrain.r1_retained_rough_mask
 assert bool((env.terrain.terrain_levels[stairs]==3).all())
 assert int(stairs.sum())==round(env.num_envs*.5)
 assert set(env.terrain_family[retained].tolist())==set(range(11))-{8}
 assert set(env.terrain.terrain_levels[retained].tolist())==set(range(10))
 assert bool(torch.allclose(geometry[stairs,2],torch.full_like(geometry[stairs,2],.4),atol=.0001))
 for k in range(600):
  with torch.inference_mode():action=policy(obs,stochastic_output=False);raw,reward,term,timeout,_=env.step(action)
  assert bool(torch.isfinite(reward).all()) and all(bool(torch.isfinite(v).all()) for v in raw.values())
  assert not bool(env.stair_up[~stairs].any()) and not bool(env.stair_extra[~stairs].any()), 'Special reset/reward leaked into retained courses'
  obs=TensorDict(raw,batch_size=[env.num_envs]);max_closure=max(max_closure,float(env.closure_error.max()))
  if k in [0,149,299,449,599]:samples.append(dict(step=k+1,done_totals=dict(env.done_totals),terrain=env.terrain_summary(),reward_extra_absmax=float(env.stair_extra.abs().max())))
 return dict(no_optimizer_update=True,num_envs=env.num_envs,steps=600,simulation_seconds=12.,wall_seconds=time.time()-start,max_closure_m=max_closure,done_totals=dict(env.done_totals),geometry_verified=True,samples=samples,policy35_critic78_actions6=[list(obs['policy'].shape),list(obs['critic'].shape),list(action.shape)],controller=env.physical_delay_summary())

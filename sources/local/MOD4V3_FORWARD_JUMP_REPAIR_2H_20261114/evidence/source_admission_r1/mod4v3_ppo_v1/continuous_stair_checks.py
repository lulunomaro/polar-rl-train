"""All-population native stair-specialist probe, frozen policy, no PPO updates."""
import torch,time,math
from tensordict import TensorDict

def run_probe(env,algorithm):
 env.begin_training_counts();obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);policy=algorithm.get_policy();start=time.time();samples=[]
 assert bool(env.continuous_stair_mask.all()) and not bool(env.flat_terrain_mask.any())
 assert not bool(env.terrain.r1_retained_rough_mask.any()) and bool(env.stair_up.all())
 assert bool((env.terrain.terrain_levels==3).all())
 assert float(env.stair_approach_yaw.abs().max())<=math.radians(30.)+1e-6
 assert bool((env.stair_approach_group==0).any()) and bool((env.stair_approach_group>0).any())
 assert not bool(env.r2_air_reset.any())
 assert env.reward.cfg.rewards['track_lin_vel_xy_square']==-1.5 and env.reward.cfg.lin_vel_xy_square_sigma==1.
 # The chosen paths meet both risers on their straight face and end inside the3m platform.
 center=env._center();delta=env.stair_approach_yaw;root_y=env.view.data.root_pos_w[:,1]-center[:,1]
 root_x=(env.view.data.root_pos_w[:,0]-center[:,0])*env.stair_side
 target_y=root_y-env.stair_side*(root_x-1.1)*torch.tan(delta)
 assert bool((target_y.abs()<.151).all()),'Oblique start missed intended platform corridor'
 max_closure=0.;height_ok=0
 for k in range(600):
  with torch.inference_mode():action=policy(obs,stochastic_output=False);raw,reward,term,timeout,_=env.step(action)
  assert bool(torch.isfinite(reward).all()) and all(bool(torch.isfinite(v).all()) for v in raw.values())
  assert raw['policy'].shape==(env.num_envs,35) and raw['critic'].shape==(env.num_envs,78) and action.shape==(env.num_envs,6)
  moving=env.stair_up&(env.episode_length_buf>=150)
  assert bool(((env.height[moving]-.42).abs()<1e-5).all()),'Highest target overwritten after command resampling'
  height_ok+=int(moving.sum());assert float(env.stair_reward_components[0])==0.
  obs=TensorDict(raw,batch_size=[env.num_envs]);max_closure=max(max_closure,float(env.closure_error.max()))
  if k in [0,149,299,449,599]:samples.append(dict(step=k+1,done_totals=dict(env.done_totals),terrain=env.terrain_summary()))
 return dict(no_optimizer_update=True,num_envs=env.num_envs,steps=600,simulation_seconds=12.,wall_seconds=time.time()-start,max_closure_m=max_closure,done_totals=dict(env.done_totals),all_stair_ascent=True,oblique_geometry_verified=True,post_warmup_height_endpoints=height_ok,policy35_critic78_actions6=True,samples=samples,controller=env.physical_delay_summary())

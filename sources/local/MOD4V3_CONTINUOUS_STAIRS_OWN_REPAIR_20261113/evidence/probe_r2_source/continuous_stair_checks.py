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
 fixed=env.flat_preservation_mask;task=env.flat_preservation_task[fixed]
 assert int(fixed.sum())==205 and not bool((fixed&~env.flat_terrain_mask).any())
 assert set(task.tolist())==set(range(6))
 assert int((fixed&env.full_dr.nominal_env_mask).sum())==41
 expected=env.command.new_tensor([[2.,0.,0.],[2.2,0.,0.],[-1.5,0.,0.],[0.,0.,4.5*3.141592653589793],[0.,0.,0.],[0.,0.,0.]])
 heights=env.height.new_tensor([.28,.28,.28,.28,.20,.40])
 assert env.reward.cfg.rewards['track_lin_vel_xy_square']==-1.5
 assert env.reward.cfg.lin_vel_xy_square_sigma==1.
 assert env.reward.cfg.rewards['track_lin_vel_xy']==1.2
 assert not bool(env.reward.get_terrain_name_mask('mod4_step270').any())
 settled_counts=torch.zeros(6,device=env.device,dtype=torch.long)
 for k in range(600):
  with torch.inference_mode():action=policy(obs,stochastic_output=False);raw,reward,term,timeout,_=env.step(action)
  assert bool(torch.isfinite(reward).all()) and all(bool(torch.isfinite(v).all()) for v in raw.values())
  settled=fixed&(env.episode_length_buf>=env._ground_command_until)
  settled_task=env.flat_preservation_task[settled]
  assert torch.allclose(env.command[settled],expected[settled_task]) and torch.allclose(env.height[fixed],heights[task]), 'Fixed six-task targets were overwritten after original reset warmup'
  settled_counts+=torch.bincount(settled_task,minlength=6)
  assert torch.allclose(env._ground_original_command[fixed],expected[task]), 'Reset warmup would restore a stale random command'
  assert not bool(env.r2_air_reset[fixed].any()), 'Preservation ground task became an airborne reset'
  assert not bool(env.stair_up[~stairs].any()) and not bool(env.stair_extra[~stairs].any()), 'Special reset/reward leaked into retained courses'
  obs=TensorDict(raw,batch_size=[env.num_envs]);max_closure=max(max_closure,float(env.closure_error.max()))
  if k in [0,149,299,449,599]:samples.append(dict(step=k+1,done_totals=dict(env.done_totals),terrain=env.terrain_summary(),reward_extra_absmax=float(env.stair_extra.abs().max())))
 assert bool((settled_counts>0).all()), "A retained flat task never reached its specified target"
 return dict(settled_flat_task_endpoint_counts=settled_counts.tolist(),no_optimizer_update=True,num_envs=env.num_envs,steps=600,simulation_seconds=12.,wall_seconds=time.time()-start,max_closure_m=max_closure,done_totals=dict(env.done_totals),geometry_verified=True,flat_six_tasks_verified=True,own_stair_shaping_enabled=True,terrain_name_filter_verified=True,samples=samples,policy35_critic78_actions6=[list(obs['policy'].shape),list(obs['critic'].shape),list(action.shape)],controller=env.physical_delay_summary())

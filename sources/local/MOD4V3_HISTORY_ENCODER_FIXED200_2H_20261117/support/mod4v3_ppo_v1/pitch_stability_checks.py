"""Observe the actual2048-env native task without optimizer updates."""
import time,torch
from tensordict import TensorDict
from .pitch_brake_math import wheel_brake_targets

def run_probe(env,algorithm):
 env.begin_training_counts();obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);policy=algorithm.get_policy();start=time.time();before={k:v.detach().clone()for k,v in algorithm.actor.state_dict().items()};brake_frames=valid_brake_frames=0
 for k in range(250):
  mask=obs['pitch_brake_hint'].reshape(-1)>.5;brake_frames+=int(mask.sum())
  if bool(mask.any()):
   _,valid=wheel_brake_targets(torch.zeros(len(obs['policy'][mask]),6,device=env.device),obs['policy'][mask]);valid_brake_frames+=int(valid.sum())
  with torch.inference_mode():action=policy(obs,stochastic_output=False);raw,reward,term,timeout,_=env.step(action)
  assert bool(torch.isfinite(reward).all())
  assert raw['policy'].shape==(env.num_envs,35)and raw['critic'].shape==(env.num_envs,78)
  obs=TensorDict(raw,batch_size=[env.num_envs])
 unchanged=all(torch.equal(before[k],v)for k,v in algorithm.actor.state_dict().items());pitch=env.pitch_summary()
 assert unchanged and env.enforce_closure_reset and env.cfg.decimation==8
 assert pitch['target_envs']==615 and pitch['rate_square_coefficient']==.05 and pitch['prediction_coefficient']==0.
 assert pitch['velocity_fix_samples']>0 and brake_frames>0 and valid_brake_frames>0
 cfg=env.reward.cfg
 assert float(cfg.rewards['track_lin_vel_xy_square'])==-1.5 and float(cfg.lin_vel_xy_square_sigma)==1.
 return dict(passed=True,no_optimizer_updates=True,actor_identical=unchanged,steps=250,num_envs=env.num_envs,wall_seconds=time.time()-start,brake_hint_frames=brake_frames,valid_observable_wheel_brake_frames=valid_brake_frames,pitch=pitch,done_totals=dict(env.done_totals),physics_dt_s=env.physics_dt,policy_dt_s=env.step_dt,actual_velocity_square_weight=float(cfg.rewards['track_lin_vel_xy_square']),actual_velocity_square_sigma=float(cfg.lin_vel_xy_square_sigma),pose_reward_weights={k:v for k,v in cfg.rewards.items()if'orientation'in k or k=='ang_vel_xy'})

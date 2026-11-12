"""Continuous 200mm ascent: actual wheel clearance/landing, no pitch/height reward veto."""
import math,torch
from .scut_rough_scut_v1_env import ScutUnifiedRoughV1Env
from .scut_flat_env import tensor
from isaaclab.utils.math import quat_from_euler_xyz

class ContinuousStairBase(ScutUnifiedRoughV1Env):
 def __init__(self,cfg,meta,bank):
  self._continuous_ready=False;self.leg_pd_decimation=4;self.wheel_pd_decimation=1
  super().__init__(cfg,meta,bank)
  n=self.num_envs;dev=self.device
  self.stair_completed=torch.zeros(n,device=dev,dtype=torch.bool)
  self.stair_up=torch.zeros(n,device=dev,dtype=torch.bool);self.stair_mid=self.stair_up.clone();self.stair_side=torch.ones(n,device=dev);self.stair_height=torch.full((n,),.38,device=dev);self.stair_speed=torch.full((n,),2.1,device=dev)
  self.stair_start=torch.zeros(n,device=dev);self.stair_progress=self.stair_start.clone();self.stair_stage=torch.zeros(n,device=dev,dtype=torch.long);self.stair_initial_stage=self.stair_stage.clone();self.stair_first_time=torch.full((n,),-1.,device=dev);self.stair_second_time=self.stair_first_time.clone();self.stair_goal_hold=self.stair_start.clone()
  self.lift_reference=torch.zeros(n,2,device=dev);self.lift_best=self.lift_reference.clone();self.lift_armed=torch.zeros(n,device=dev,dtype=torch.bool)
  self.stair_extra=torch.zeros(n,device=dev);self.stair_counts=torch.zeros(2,8,device=dev,dtype=torch.long);self.stair_time_sum=torch.zeros(2,device=dev);self.stair_time_count=torch.zeros(2,device=dev,dtype=torch.long);self.stair_reward_components=torch.zeros(5,device=dev)
  self.wheel_sensor_ids=[self.scene['contacts'].body_names.index(x) for x in ['left_wheel_link','right_wheel_link']]
  self.stair_wheel_idx=self.reward._wheel_link_idx
  self.continuous_stair_mask=self.terrain.r1_continuous_stair_mask
  self._continuous_ready=True
 def _center(self):return self.terrain.terrain_origins[self.terrain.terrain_levels,self.terrain.terrain_types]
 def _count(self,ids,column):
  if ids.numel():self.stair_counts[:,column].scatter_add_(0,self.full_dr.nominal_env_mask[ids].long(),torch.ones(len(ids),device=self.device,dtype=torch.long))
 def _sample_command(self,ids):
  super()._sample_command(ids)
  if not getattr(self,'_continuous_ready',False):return
  ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
  picked=ids[self.continuous_stair_mask[ids]];self.heading_env[picked]=False;self.standing_env[picked]=False
 def _reset_idx(self,ids):
  ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten();ready=getattr(self,'_continuous_ready',False)
  if ready:
   failed=ids[self.stair_up[ids]&self.reset_terminated[ids]];self._count(failed,6)
  super()._reset_idx(ids)
  if not ready or not ids.numel():return
  self.stair_completed[ids]=False
  self.stair_up[ids]=False;self.stair_mid[ids]=False;self.stair_progress[ids]=0.;self.stair_stage[ids]=0;self.stair_initial_stage[ids]=0;self.stair_first_time[ids]=-1.;self.stair_second_time[ids]=-1.;self.stair_goal_hold[ids]=0.;self.lift_best[ids]=0.;self.lift_armed[ids]=False;self.stair_extra[ids]=0.
  picked=ids[self.continuous_stair_mask[ids]]
  if not picked.numel():return
  n=len(picked);gen=self.reset_generator;center=self._center()[picked];up=torch.rand(n,device=self.device,generator=gen)<.9;mid=up&(torch.rand(n,device=self.device,generator=gen)<.15);side=torch.where(torch.rand(n,device=self.device,generator=gen)<.5,-1.,1.)
  options=((self._bank_h>=.24)&(self._bank_h<=.272)).nonzero().flatten();sample=options[torch.randint(len(options),(n,),device=self.device,generator=gen)];q=self._bank_q[sample][:,self._bank_ids].clone();root=tensor(self.robot.data.default_root_state)[picked].clone()
  distance=torch.where(up,torch.where(mid,torch.full_like(side,2.35),torch.empty(n,device=self.device).uniform_(3.55,4.,generator=gen)),torch.full_like(side,.25))
  ground=torch.where(up,torch.where(mid,.2,0.),.4);root[:,0]=center[:,0]+side*distance;root[:,1]=center[:,1]+torch.empty(n,device=self.device).uniform_(-.25,.25,generator=gen);root[:,2]=ground+self._bank_h[sample]+.01
  forward=torch.where(up,-side,side);yaw=torch.where(forward>0,0.,math.pi);root[:,3:7]=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw);root[:,7:]=0.
  self.robot.write_root_state_to_sim(root,env_ids=picked);self.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=picked)
  self.stair_up[picked]=up;self.stair_mid[picked]=mid;self.stair_side[picked]=side;self.stair_start[picked]=distance;self.stair_stage[picked]=mid.long();self.stair_initial_stage[picked]=mid.long()
  self.stair_height[picked]=torch.empty(n,device=self.device).uniform_(.365,.4,generator=gen);self.stair_speed[picked]=torch.empty(n,device=self.device).uniform_(1.8,2.2,generator=gen);self.stair_first_time[picked]=-1.
  self.height[picked]=.28;self.command[picked]=0.;self.heading_env[picked]=False;self.standing_env[picked]=False;self.actions[picked]=0.;self.torque[picked]=0.;self.zero_torque_remaining[picked]=0;self._ground_command_until[picked]=0;self.r2_air_reset[picked]=False
  self.reward.ground_z_est[picked]=ground;self.reward.command.copy_(self.command);self.reward.height_cmd.copy_(self.height);self.reward._invalidate_step_caches()
  self._count(picked[up&~mid],0);self._count(picked[mid],1);self._count(picked[~up],7)
 def _pre_physics_step(self,actions):
  super()._pre_physics_step(actions)
  if not self._continuous_ready:return
  picked=self.continuous_stair_mask.nonzero().flatten();self.height[picked]+=(self.stair_height[picked]-self.height[picked]).clamp(-.0012,.0012);move=self.episode_length_buf[picked]*self.step_dt>=3.
  self.command[picked,0]=torch.where(move,self.stair_speed[picked],0.);self.command[picked,1:]=0.;self.heading_env[picked]=False
 def _get_dones(self):
  term,timeout=super()._get_dones()
  if getattr(self,'_continuous_ready',False):timeout|=(self.stair_goal_hold>=.3)&(~term)
  return term,timeout
 def _get_rewards(self):
  base=super()._get_rewards()
  if not getattr(self,'_continuous_ready',False):return base
  active=self.stair_up&(~self.reset_terminated)&(self.episode_length_buf*self.step_dt>=3.);center=self._center();pos=self.view.data.root_pos_w;wheel=self.view.data.body_pos_w[:,self.stair_wheel_idx];forces=tensor(self.scene['contacts'].data.net_forces_w)[:,self.wheel_sensor_ids]
  local_x=(wheel[:,:,0]-center[:,None,0])*self.stair_side[:,None];dy=(wheel[:,:,1]-center[:,None,1]).abs();radius=.0625
  # Actual tread contact and wheel clearance, rather than root projection/world-z alone.
  support=forces[:,:,2]>5.;first=((local_x<2.88)&(local_x>1.42)&(dy<2.88)&((wheel[:,:,2]-(.2+radius)).abs()<.05)&support).all(1)
  second=((local_x<1.38)&(dy<1.38)&((wheel[:,:,2]-(.4+radius)).abs()<.05)&support).all(1)
  new_first=active&first&(self.stair_stage<1);new_second=active&second&(self.stair_stage<2)
  age=self.episode_length_buf*self.step_dt;self.stair_first_time[new_first]=age[new_first];self._count(new_first.nonzero().flatten(),2);self._count(new_second.nonzero().flatten(),3)
  self.stair_second_time[new_second]=age[new_second]
  dx=(pos[:,0]-center[:,0]).abs();progress=(self.stair_start-dx).clamp_min(0.);advance=(progress-self.stair_progress).clamp_min(0.).clamp_max(2.2*self.step_dt)*active
  self.stair_progress=torch.where(active,torch.maximum(self.stair_progress,progress),self.stair_progress)
  stage=self.stair_stage.clamp_max(1);edge=torch.where(stage==0,2.9,1.4);lower=stage*.2;near=(local_x-edge[:,None]).abs().amin(1)<.45
  armed=active&near&(~self.lift_armed);self.lift_reference[armed]=self.reward.length[armed];self.lift_armed|=armed
  lift=((wheel[:,:,2]-(lower[:,None]+radius))/.2).clamp(0,1);retract=((self.lift_reference-self.reward.length)/.08).clamp(0,1);score=lift*retract
  lift_gain=(score-self.lift_best).clamp_min(0.).mean(1)*(active&near&self.lift_armed);self.lift_best=torch.where((active&near)[:,None],torch.maximum(self.lift_best,score),self.lift_best)
  wait=active&(self.stair_stage>=1)&(self.stair_stage<2);time_cost=.15*self.step_dt*wait
  extra=.8*advance+.6*lift_gain+.5*new_first.float()+.5*new_second.float()-time_cost
  self.stair_stage=torch.where(new_second,2,torch.where(new_first,1,self.stair_stage));self.lift_best[new_first]=0.;self.lift_armed[new_first]=False
  on_top=(local_x<1.4).all(1)&(dy<1.4).all(1)&(wheel[:,:,2]>(.4+radius-.07)).all(1)
  prior_hold=self.stair_goal_hold.clone();self.stair_goal_hold=torch.where(active&(self.stair_stage==2)&on_top,self.stair_goal_hold+self.step_dt,torch.zeros_like(self.stair_goal_hold))
  completed=(prior_hold<.3)&(self.stair_goal_hold>=.3)&~self.stair_completed;self.stair_completed|=completed;full=completed&(self.stair_initial_stage==0);mid=completed&(self.stair_initial_stage==1);self._count(full.nonzero().flatten(),4);self._count(mid.nonzero().flatten(),5)
  timing=full&(self.stair_first_time>=0)
  if bool(timing.any()):
   g=self.full_dr.nominal_env_mask[timing].long();dt=self.stair_second_time[timing]-self.stair_first_time[timing];self.stair_time_sum.scatter_add_(0,g,dt);self.stair_time_count.scatter_add_(0,g,torch.ones_like(g))
  extra+=2.*completed.float()
  self.stair_extra=extra;self.stair_reward_components+=torch.stack((.8*advance.sum(),.6*lift_gain.sum(),.5*new_first.sum(),.5*new_second.sum()+2.*completed.sum(),-time_cost.sum()))
  return base+extra
 def terrain_summary(self):
  out=super().terrain_summary()
  if getattr(self,'_continuous_ready',False):
   out.update(stage='continuous200mm_with_Rough-v1-retention',max_level=9,level_sampling='special stairs fixed row3; retained original Rough-v1 all10 levels; no adaptive promotion')
   out['course_groups']=dict(continuous_stairs=int(self.continuous_stair_mask.sum()),retained_rough=int(self.terrain.r1_retained_rough_mask.sum()),flat=int(self.flat_terrain_mask.sum()),special_only_rewards=True,retained_original_commands_and_air_resets=True)
   out['continuous_stair']=dict(geometry=dict(source_level=3,riser_m=.2,tread_m=1.5,platform_height_m=.4,steps=2),counts_DR_then_nominal=self.stair_counts.tolist(),columns=['whole_ascent_starts','mid_ascent_starts','first_landed','second_landed','whole_two_step_success','mid_recovery_success','terminated','descent_starts'],mean_first_to_second_s=(self.stair_time_sum/self.stair_time_count.clamp_min(1)).tolist(),timed_successes=self.stair_time_count.tolist(),reward_sums=self.stair_reward_components.tolist(),reward_columns=['new_progress','clearance_with_retraction','first_landing','second_landing_plus_held_completion','between_step_time_cost'],active_up=int(self.stair_up.sum()),active_mid=int(self.stair_mid.sum()),pitch_reward_veto=False,height_reward_veto=False,scope='Cumulative stochastic training samples, not fixed evaluation success rate')
  return out
 def terrain_checkpoint_state(self):
  state=super().terrain_checkpoint_state();state['course']='continuous_stairs200_roughv1_retention';state['continuous_stair_counts']=self.stair_counts;state['continuous_stair_time_sum']=self.stair_time_sum;state['continuous_stair_time_count']=self.stair_time_count;return state
 def restore_terrain_curriculum(self,state):
  self.parent_terrain_state=state;self.snapshots=None
  same=state.get('course')=='continuous_stairs200_roughv1_retention'
  if same:
   self.stair_counts.copy_(state['continuous_stair_counts'].to(self.device));self.stair_time_sum.copy_(state['continuous_stair_time_sum'].to(self.device));self.stair_time_count.copy_(state['continuous_stair_time_count'].to(self.device))
  self.reset();return dict(new_continuous_stair_course=not same,parent_state_retained=True,counters_restored=same,fresh_physical_episodes=True,old_terrain_not_relabelled=True)

 def begin_training_counts(self):
  self.stair_counts.zero_();self.stair_time_sum.zero_();self.stair_time_count.zero_();self.stair_reward_components.zero_()
  self._count((self.stair_up&~self.stair_mid).nonzero().flatten(),0);self._count(self.stair_mid.nonzero().flatten(),1);self._count((self.continuous_stair_mask&~self.stair_up).nonzero().flatten(),7)


# The saved successful SCUT stair run uses ordinary ground rewards and no airborne manager.
# The other original Rough-v1/flat envs retain their current objectives, including landing.
from pathlib import Path
import json
from .scut_flat_rewards import configuration_rough_v0,make_reward_class
from rough_scut_v1_terrain import FAMILIES
REFERENCE=json.loads((Path(__file__).resolve().parents[1]/'scut_successful_stair_reward.json').read_text())
def successful_stair_configuration():
 cfg=configuration_rough_v0();cfg.rewards=dict(REFERENCE['weights'])
 for name,value in REFERENCE['helpers'].items():setattr(cfg,name,value)
 cfg.wrong_direction_penalty_enabled=False;cfg.speed_preserve_enabled=False;cfg.ctrl_mode_obs_enabled=False
 cfg.enable_state_machines=False
 for name in ('airborne_state_machine_cfg','jump_takeoff_state_machine_cfg','stair_state_machine_cfg','wheel_forward_scan_cfg'):getattr(cfg,name)['enabled']=False
 return cfg

class ContinuousStairEnv(ContinuousStairBase):
 def __init__(self,cfg,meta,bank):
  self.stair_reference_reward=None
  super().__init__(cfg,meta,bank)
  self.stair_reference_reward=make_reward_class(meta,cfg_factory=successful_stair_configuration)(self.view,self.num_envs,self.device)
  self.reward.get_terrain_name_mask=self._reference_terrain_mask
  self.stair_reference_reward.get_terrain_name_mask=self._reference_terrain_mask
  names=self.reward.cfg.airborne_state_machine_cfg.get('not_allowed_terrain_names',[])
  self.reward.cfg.airborne_state_machine_cfg['not_allowed_terrain_names']=list(dict.fromkeys([*names,FAMILIES[0],FAMILIES[4]]))
  self.command_resample=(5.,15.);self.standing_fraction=.1;self.heading_fraction=.5
  self.reward_profile_means={};self.stair_diagnostic_extra=torch.zeros(self.num_envs,device=self.device)
 def _reference_terrain_mask(self,names):
  if isinstance(names,str):names=(names,)
  if not names:return torch.ones(self.num_envs,device=self.device,dtype=torch.bool)
  mask=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
  for name in names:
   if name in FAMILIES:mask|=self.terrain_family==FAMILIES.index(name)
  return mask
 def prepare_endpoint(self):
  super().prepare_endpoint()
  ref=getattr(self,'stair_reference_reward',None)
  if ref is None:return
  main=self.reward
  ref.begin(self.actions,self.command,self.height,self.reset_terminated,self.numeric,self.episode_length_buf,main.contact_sensor.data.net_forces_w_history,main.ground_z_est,main.ground_wheels,main.forward_points,main.forward_hits,main.near_points,main.near_hits)
  for name in ('_previous_actions','_before_previous_actions','_previous_applied_torque','_before_previous_applied_torque','_numerical_safety_reset_buf'):
   target=getattr(ref,name,None);source=getattr(main,name,None)
   if torch.is_tensor(target) and torch.is_tensor(source):target.copy_(source)
 def _reset_idx(self,ids):
  super()._reset_idx(ids)
  ref=getattr(self,'stair_reference_reward',None)
  if ref is not None:ref.reset(ids)
 def _get_dones(self):
  # Original boundary/episode and safety termination; a diagnostic completion does not end the episode.
  return ScutUnifiedRoughV1Env._get_dones(self)
 def _get_rewards(self):
  original_with_diagnostic=super()._get_rewards()
  ref=getattr(self,'stair_reference_reward',None)
  if ref is None:return original_with_diagnostic
  diagnostic=self.stair_extra.clone();base=original_with_diagnostic-diagnostic;reference=ref.compute()
  result=torch.where(self.continuous_stair_mask,reference,base)
  self.stair_diagnostic_extra=diagnostic;self.stair_extra.zero_()
  self.reward_profile_means=dict(wide_SCUT=float(reference[self.continuous_stair_mask].mean()),retained_original=float(base[~self.continuous_stair_mask].mean()),custom_stair_shaping_applied=False)
  return result
 def terrain_summary(self):
  out=super().terrain_summary();out['stage']='SCUT-successful-stair-finetune-with-Rough-v1-retention'
  out['reward_profiles']=dict(wide_stair='saved rough_rotation_stair2026-07-23_16-23-21',other_envs='retained originalRough-v1/flat, including existing speed penalty and landing',custom_stair_shaping_to_PPO=False,wide_stair_airborne_manager=False,post_success_early_timeout=False,means=getattr(self,'reward_profile_means',{}))
  if 'continuous_stair' in out:
   row=out['continuous_stair'];row['diagnostic_score_sums']=row.pop('reward_sums');row['diagnostic_score_columns']=row.pop('reward_columns')
  return out

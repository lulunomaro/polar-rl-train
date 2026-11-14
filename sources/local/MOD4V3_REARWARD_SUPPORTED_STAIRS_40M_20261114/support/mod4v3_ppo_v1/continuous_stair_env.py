"""Continuous 200mm ascent: actual wheel clearance/landing, no pitch/height reward veto."""
import math,torch
from .scut_rough_scut_v1_env import ScutUnifiedRoughV1Env
from .scut_flat_env import tensor
from isaaclab.utils.math import quat_from_euler_xyz, quat_apply
from rough_scut_v1_terrain import FAMILIES

class _OriginalContinuousStairEnv(ScutUnifiedRoughV1Env):
 def __init__(self,cfg,meta,bank):
  self._continuous_ready=False;self.leg_pd_decimation=4;self.wheel_pd_decimation=1
  super().__init__(cfg,meta,bank)
  n=self.num_envs;dev=self.device
  self.stair_up=torch.zeros(n,device=dev,dtype=torch.bool);self.stair_mid=self.stair_up.clone();self.stair_side=torch.ones(n,device=dev);self.stair_height=torch.full((n,),.38,device=dev);self.stair_speed=torch.full((n,),2.1,device=dev)
  self.stair_start=torch.zeros(n,device=dev);self.stair_progress=self.stair_start.clone();self.stair_stage=torch.zeros(n,device=dev,dtype=torch.long);self.stair_initial_stage=self.stair_stage.clone();self.stair_first_time=torch.full((n,),-1.,device=dev);self.stair_second_time=self.stair_first_time.clone();self.stair_goal_hold=self.stair_start.clone()
  self.lift_reference=torch.zeros(n,2,device=dev);self.lift_best=self.lift_reference.clone();self.lift_armed=torch.zeros(n,device=dev,dtype=torch.bool)
  self.stair_landed_wheels=torch.zeros(n,2,2,device=dev,dtype=torch.bool);self.stair_extra=torch.zeros(n,device=dev);self.stair_counts=torch.zeros(2,8,device=dev,dtype=torch.long);self.stair_time_sum=torch.zeros(2,device=dev);self.stair_time_count=torch.zeros(2,device=dev,dtype=torch.long);self.stair_reward_components=torch.zeros(5,device=dev)
  self.wheel_sensor_ids=[self.scene['contacts'].body_names.index(x) for x in ['left_wheel_link','right_wheel_link']]
  self.stair_wheel_idx=self.reward._wheel_link_idx
  self.continuous_stair_mask=self.terrain.r1_continuous_stair_mask
  # Keep the original stair objective; repair only retained-task exposure and terrain lookup.
  self.flat_preservation_mask=torch.zeros(n,device=dev,dtype=torch.bool)
  self.flat_preservation_task=torch.full((n,),-1,device=dev,dtype=torch.long)
  task_offset=0
  for nominal in (False,True):
   ids=(self.flat_terrain_mask&(self.full_dr.nominal_env_mask==nominal)).nonzero().flatten()
   chosen=ids[::2]
   self.flat_preservation_mask[chosen]=True
   self.flat_preservation_task[chosen]=(torch.arange(len(chosen),device=dev)+task_offset)%6
   task_offset+=len(chosen)
  self.reward.get_terrain_name_mask=self._terrain_name_mask
  self.stair_approach_yaw=torch.zeros(n,device=dev)
  self.stair_approach_group=torch.zeros(n,device=dev,dtype=torch.long)
  self.stair_edge_contact_yaw=torch.zeros(n,device=dev)
  self.stair_edge_contact_seen=torch.zeros(n,device=dev,dtype=torch.bool)
  self.specialist_counts=torch.zeros(2,5,6,device=dev,dtype=torch.long)
  self.specialist_oblique_success=torch.zeros(2,5,device=dev,dtype=torch.long)
  self._continuous_ready=True
  from .rearward_support import RearwardSupport
  self.rearward=RearwardSupport(self)
 def _terrain_name_mask(self,names):
  if isinstance(names,str):names=(names,)
  if not names:return torch.ones(self.num_envs,device=self.device,dtype=torch.bool)
  mask=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
  for name in names:
   if name in FAMILIES:mask|=self.terrain_family==FAMILIES.index(name)
  return mask
 def _flat_preservation_commands(self,ids):
  if not getattr(self,'_continuous_ready',False):return
  picked=ids[self.flat_preservation_mask[ids]]
  if not picked.numel():return
  tasks=self.flat_preservation_task[picked]
  table=self.command.new_tensor([[2.,0.,.28],[2.2,0.,.28],[-1.5,0.,.28],[0.,4.5*math.pi,.28],[0.,0.,.20],[0.,0.,.40]])
  self.command[picked]=0.;self.command[picked,0]=table[tasks,0];self.command[picked,2]=table[tasks,1]
  self.height[picked]=table[tasks,2];self.command_timer[picked]=1e9
  self._ground_original_command[picked]=self.command[picked]
  self._ground_original_heading[picked]=False
  warming=self.episode_length_buf[picked]<self._ground_command_until[picked]
  self.command[picked]=torch.where(warming[:,None],self._ground_reset_command[picked],self.command[picked])
  self.heading_env[picked]=False;self.standing_env[picked]=tasks>=4
  self.reward.command[picked]=self.command[picked];self.reward.height_cmd[picked]=self.height[picked]
  self.reward._invalidate_step_caches()
 def _center(self):return self.terrain.terrain_origins[self.terrain.terrain_levels,self.terrain.terrain_types]
 def _count(self,ids,column):
  if ids.numel():
   nominal=self.full_dr.nominal_env_mask[ids].long()
   self.stair_counts[:,column].scatter_add_(0,nominal,torch.ones(len(ids),device=self.device,dtype=torch.long))
   if column<5 and hasattr(self,'specialist_counts'):
    flat_index=nominal*5+self.stair_approach_group[ids]
    self.specialist_counts[:,:,column].view(-1).scatter_add_(0,flat_index,torch.ones_like(flat_index))
 def _sample_command(self,ids):
  ready=getattr(self,'_continuous_ready',False)
  if ready:
   ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
   ascent_ids=ids[self.stair_up[ids]];ascent_height=self.height[ascent_ids].clone()
  super()._sample_command(ids)
  if not ready:return
  # Keep the ramped ascent height when the original command timer resamples.
  self.height[ascent_ids]=ascent_height
  picked=ids[self.continuous_stair_mask[ids]];self.heading_env[picked]=False;self.standing_env[picked]=False
  self._flat_preservation_commands(ids)
 def _reset_idx(self,ids):
  ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten();ready=getattr(self,'_continuous_ready',False)
  if ready:
   failed=ids[self.stair_up[ids]&self.reset_terminated[ids]];self._count(failed,6)
  super()._reset_idx(ids)
  if not ready or not ids.numel():return
  self.stair_landed_wheels[ids]=False;self.stair_up[ids]=False;self.stair_mid[ids]=False;self.stair_progress[ids]=0.;self.stair_stage[ids]=0;self.stair_initial_stage[ids]=0;self.stair_first_time[ids]=-1.;self.stair_second_time[ids]=-1.;self.stair_goal_hold[ids]=0.;self.lift_best[ids]=0.;self.lift_armed[ids]=False;self.stair_extra[ids]=0.
  self._flat_preservation_commands(ids)
  picked=ids[self.continuous_stair_mask[ids]]
  if not picked.numel():return
  n=len(picked);gen=self.reset_generator;center=self._center()[picked];up=torch.rand(n,device=self.device,generator=gen)<.9;mid=up&(torch.rand(n,device=self.device,generator=gen)<.15);side=torch.where(torch.rand(n,device=self.device,generator=gen)<.5,-1.,1.)
  options=((self._bank_h>=.24)&(self._bank_h<=.272)).nonzero().flatten();sample=options[torch.randint(len(options),(n,),device=self.device,generator=gen)];q=self._bank_q[sample][:,self._bank_ids].clone();root=tensor(self.robot.data.default_root_state)[picked].clone()
  distance=torch.where(up,torch.where(mid,torch.full_like(side,2.35),torch.empty(n,device=self.device).uniform_(3.55,4.,generator=gen)),torch.full_like(side,.25))
  ground=torch.where(up,torch.where(mid,.2,0.),.4);root[:,0]=center[:,0]+side*distance;root[:,1]=center[:,1]+torch.empty(n,device=self.device).uniform_(-.25,.25,generator=gen);root[:,2]=ground+self._bank_h[sample]+.01
  oblique=up&(torch.rand(n,device=self.device,generator=gen)<.5)
  angle=torch.empty(n,device=self.device).uniform_(math.radians(10.),math.radians(30.),generator=gen)
  sign=torch.where(torch.rand(n,device=self.device,generator=gen)<.5,-1.,1.)
  delta=torch.where(oblique,angle*sign,torch.zeros_like(angle))
  target_y=torch.empty(n,device=self.device).uniform_(-.15,.15,generator=gen)
  root[:,1]=center[:,1]+target_y+side*(distance-1.1)*torch.tan(delta)
  forward=torch.where(up,-side,side);yaw=torch.where(forward>0,0.,math.pi)+delta
  root[:,3:7]=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw);root[:,7:]=0.
  self.stair_approach_yaw[picked]=delta
  self.stair_approach_group[picked]=torch.where(oblique,1+(sign<0).long()+2*(angle>=math.radians(20.)).long(),0)
  self.stair_edge_contact_yaw[picked]=0.;self.stair_edge_contact_seen[picked]=False
  self.robot.write_root_state_to_sim(root,env_ids=picked);self.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=picked)
  self.stair_up[picked]=up;self.stair_mid[picked]=mid;self.stair_side[picked]=side;self.stair_start[picked]=distance;self.stair_stage[picked]=mid.long();self.stair_initial_stage[picked]=mid.long()
  sampled_stair_height=torch.empty(n,device=self.device).uniform_(.365,.4,generator=gen);self.stair_height[picked]=torch.where(up,torch.full_like(sampled_stair_height,.42),sampled_stair_height);self.stair_speed[picked]=torch.empty(n,device=self.device).uniform_(1.8,2.2,generator=gen);self.stair_first_time[picked]=-1.
  self.height[picked]=.28;self.command[picked]=0.;self.heading_env[picked]=False;self.standing_env[picked]=False;self.actions[picked]=0.;self.torque[picked]=0.;self.zero_torque_remaining[picked]=0;self._ground_command_until[picked]=0;self.r2_air_reset[picked]=False
  self.reward.ground_z_est[picked]=ground;self.reward.command.copy_(self.command);self.reward.height_cmd.copy_(self.height);self.reward._invalidate_step_caches()
  if hasattr(self,'rearward'):self.rearward.reset(picked)
  assisted=self.rearward.assisted[picked]
  self._count(picked[up&~mid&~assisted],0);self._count(picked[mid&~assisted],1);self._count(picked[~up],7)
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
  # Record real heading at near-first-edge horizontal wheel contact; diagnostic only.
  axis=torch.zeros(self.num_envs,3,device=self.device);axis[:,0]=1.
  forward_axis=quat_apply(self.view.data.root_quat_w[:,[1,2,3,0]],axis)
  edge_yaw=torch.atan2(-self.stair_side*forward_axis[:,1],-self.stair_side*forward_axis[:,0])
  near_first=(local_x-2.9).abs()<.12
  horizontal_contact=torch.linalg.vector_norm(forces[:,:,:2],dim=-1)>5.
  seen=active&(self.stair_stage==0)&(~self.stair_edge_contact_seen)&(near_first&horizontal_contact).any(1)
  self.stair_edge_contact_yaw[seen]=edge_yaw[seen];self.stair_edge_contact_seen[seen]=True
  # Actual tread contact and wheel clearance, rather than root projection/world-z alone.
  support=forces[:,:,2]>5.
  first_wheels=(local_x<2.88)&(local_x>1.42)&(dy<2.88)&((wheel[:,:,2]-(.2+radius)).abs()<.05)&support
  second_wheels=(local_x<1.38)&(dy<1.38)&((wheel[:,:,2]-(.4+radius)).abs()<.05)&support
  first=first_wheels.all(1);second=second_wheels.all(1)
  from .stair_landing_credit import landing_credit
  first_credit=landing_credit(first_wheels,self.stair_landed_wheels[:,0],active&(self.stair_stage<1))
  second_credit=landing_credit(second_wheels,self.stair_landed_wheels[:,1],active&(self.stair_stage<2))
  new_first=active&first&(self.stair_stage<1);new_second=active&second&(self.stair_stage<2)
  age=self.episode_length_buf*self.step_dt;self.stair_first_time[new_first]=age[new_first];self._count(new_first.nonzero().flatten(),2);self._count(new_second.nonzero().flatten(),3)
  self.stair_second_time[new_second]=age[new_second]
  dx=(pos[:,0]-center[:,0]).abs();progress=(self.stair_start-dx).clamp_min(0.);advance=(progress-self.stair_progress).clamp_min(0.).clamp_max(2.2*self.step_dt)*active
  self.stair_progress=torch.where(active,torch.maximum(self.stair_progress,progress),self.stair_progress)
  stage=self.stair_stage.clamp_max(1);edge=torch.where(stage==0,2.9,1.4);lower=stage*.2;near=(local_x-edge[:,None]).abs().amin(1)<.45
  armed=active&near&(~self.lift_armed);self.lift_reference[armed]=self.reward.length[armed];self.lift_armed|=armed
  lift=((wheel[:,:,2]-(lower[:,None]+radius))/.2).clamp(0,1);retract=((self.lift_reference-self.reward.length)/.08).clamp(0,1);score=lift*retract
  lift_gain=(score-self.lift_best).clamp_min(0.).mean(1)*(active&near&self.lift_armed);self.lift_best=torch.where((active&near)[:,None],torch.maximum(self.lift_best,score),self.lift_best)
  if hasattr(self,'rearward'):lift_gain=self.rearward.gain(active)
  wait=active&(self.stair_stage>=1)&(self.stair_stage<2);time_cost=.15*self.step_dt*wait
  extra=.6*lift_gain+first_credit+second_credit+.2*new_first.float()+.2*new_second.float()-time_cost
  self.stair_stage=torch.where(new_second,2,torch.where(new_first,1,self.stair_stage));self.lift_best[new_first]=0.;self.lift_armed[new_first]=False
  on_top=(local_x<1.4).all(1)&(dy<1.4).all(1)&(wheel[:,:,2]>(.4+radius-.07)).all(1)
  if hasattr(self,'rearward'):on_top&=(pos[:,2]-.4>=.32)&support.all(1)
  prior_hold=self.stair_goal_hold.clone();self.stair_goal_hold=torch.where(active&(self.stair_stage==2)&on_top,self.stair_goal_hold+self.step_dt,torch.zeros_like(self.stair_goal_hold))
  completed=(prior_hold<.3)&(self.stair_goal_hold>=.3);full=completed&(self.stair_initial_stage==0);mid=completed&(self.stair_initial_stage==1);self._count(full.nonzero().flatten(),4);self._count(mid.nonzero().flatten(),5)
  actual_oblique=full&self.stair_edge_contact_seen&(self.stair_edge_contact_yaw.abs()>=math.radians(10.))
  actual_ids=actual_oblique.nonzero().flatten()
  if actual_ids.numel():
   group=self.full_dr.nominal_env_mask[actual_ids].long()*5+self.stair_approach_group[actual_ids]
   self.specialist_oblique_success.view(-1).scatter_add_(0,group,torch.ones_like(group))
  timing=full&(self.stair_first_time>=0)
  if bool(timing.any()):
   g=self.full_dr.nominal_env_mask[timing].long();dt=self.stair_second_time[timing]-self.stair_first_time[timing];self.stair_time_sum.scatter_add_(0,g,dt);self.stair_time_count.scatter_add_(0,g,torch.ones_like(g))
  extra+=2.*completed.float()
  self.stair_extra=extra;self.stair_reward_components+=torch.stack((advance.new_zeros(()),.6*lift_gain.sum(),first_credit.sum()+.2*new_first.sum(),second_credit.sum()+.2*new_second.sum()+2.*completed.sum(),-time_cost.sum()))
  return base+extra
 def terrain_summary(self):
  out=super().terrain_summary()
  if hasattr(self,'rearward'):out['rearward_support']=self.rearward.summary()
  if getattr(self,'_continuous_ready',False):
   out.update(stage='continuous200mm_with_Rough-v1-retention',max_level=9,level_sampling='special stairs fixed row3; retained original Rough-v1 all10 levels; no adaptive promotion')
   out['course_groups']=dict(continuous_stairs=int(self.continuous_stair_mask.sum()),retained_rough=int(self.terrain.r1_retained_rough_mask.sum()),flat=int(self.flat_terrain_mask.sum()),special_only_rewards=True,retained_original_commands_and_air_resets=True)
   out['flat_preservation']=dict(envs=int(self.flat_preservation_mask.sum()),tasks=torch.bincount(self.flat_preservation_task[self.flat_preservation_mask],minlength=6).tolist(),ground_only=True,reward_unchanged=True,nominal=int((self.flat_preservation_mask&self.full_dr.nominal_env_mask).sum()))
   out['continuous_stair']=dict(ascent_height_target_m=.42,descent_height_target_m=[.365,.4],geometry=dict(source_level=3,riser_m=.2,tread_m=1.5,platform_height_m=.4,steps=2),counts_DR_then_nominal=self.stair_counts.tolist(),columns=['whole_ascent_starts','mid_ascent_starts','first_landed','second_landed','whole_two_step_success','mid_recovery_success','terminated','descent_starts'],mean_first_to_second_s=(self.stair_time_sum/self.stair_time_count.clamp_min(1)).tolist(),timed_successes=self.stair_time_count.tolist(),reward_sums=self.stair_reward_components.tolist(),reward_columns=['disabled_progress_zero','supported_rearward_upward_transfer','first_single_wheel_and_pair_landing','second_single_wheel_and_pair_landing_plus_held_completion','between_step_time_cost'],active_up=int(self.stair_up.sum()),active_mid=int(self.stair_mid.sum()),pitch_reward_veto=False,height_reward_veto="only while true supported mount before bilateral wheel landing",landing_credit='0.15 per real wheel first tread support once per stage plus0.2 bilateral landing; total0.5 unchanged per stair',scope='Cumulative stochastic training samples, not fixed evaluation success rate')
  if getattr(self,'_continuous_ready',False):
   out['stage']='mixed_comprehensive_student_with_specialist_guidance'
   out['specialist']=dict(counts_DR_then_nominal=self.specialist_counts.tolist(),groups=['straight','positive10to20','negative10to20','positive20to30','negative20to30'],columns=['whole_starts','mid_starts','first_landing','second_landing','whole_success','reserved'],actual_near_edge_oblique_success=self.specialist_oblique_success.tolist(),all_ascent=False,task_fraction=.4,mid_start_fraction=.15,oblique_fraction=.5,oblique_abs_yaw_deg=[10.,30.],edge_heading_diagnostic='first horizontal wheel force>5N within0.12m of first edge; exact contact geometry checked separately in MuJoCo')
  return out
 def terrain_checkpoint_state(self):
  state=super().terrain_checkpoint_state();state['course']='mixed_stair_specialist_student200';state['specialist_counts']=self.specialist_counts;state['specialist_oblique_success']=self.specialist_oblique_success;state['continuous_stair_counts']=self.stair_counts;state['continuous_stair_time_sum']=self.stair_time_sum;state['continuous_stair_time_count']=self.stair_time_count;return state
 def restore_terrain_curriculum(self,state):
  self.parent_terrain_state=state;self.snapshots=None
  same=state.get('course')=='mixed_stair_specialist_student200'
  if same:
   self.stair_counts.copy_(state['continuous_stair_counts'].to(self.device));self.stair_time_sum.copy_(state['continuous_stair_time_sum'].to(self.device));self.stair_time_count.copy_(state['continuous_stair_time_count'].to(self.device))
  if same:self.specialist_counts.copy_(state['specialist_counts'].to(self.device));self.specialist_oblique_success.copy_(state['specialist_oblique_success'].to(self.device))
  self.reset();return dict(new_continuous_stair_course=not same,parent_state_retained=True,counters_restored=same,fresh_physical_episodes=True,old_terrain_not_relabelled=True)

 def begin_training_counts(self):
  self.specialist_counts.zero_();self.specialist_oblique_success.zero_()
  self.stair_counts.zero_();self.stair_time_sum.zero_();self.stair_time_count.zero_();self.stair_reward_components.zero_()
  self.rearward.stats.zero_();self.rearward.stats[0]=self.rearward.assisted.sum()
  self._count((self.stair_up&~self.stair_mid&~self.rearward.assisted).nonzero().flatten(),0);self._count((self.stair_mid&~self.rearward.assisted).nonzero().flatten(),1);self._count((self.continuous_stair_mask&~self.stair_up).nonzero().flatten(),7)


from .stair_training_repair import ContinuousStairRepairMixin

class ContinuousStairEnv(ContinuousStairRepairMixin, _OriginalContinuousStairEnv):
    """Versioned correction; the completed parent run remains reproducible."""
    pass

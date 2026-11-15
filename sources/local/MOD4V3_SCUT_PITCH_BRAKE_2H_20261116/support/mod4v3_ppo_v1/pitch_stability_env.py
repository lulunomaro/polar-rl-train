"""Focused start/stop pitch repair with the comprehensive parent's stair source."""
import torch
from .continuous_stair_env import ContinuousStairEnv
from .scut_flat_env import tensor
from .pitch_brake_math import horizontal_reward_terms
from .pitch_stability_math import body_pitch,transition_command,stability_cost,stability_active_mask,stability_components,transition_window

class PitchStabilityEnv(ContinuousStairEnv):
 def __init__(self,cfg,meta,bank):
  self._pitch_ready=False
  super().__init__(cfg,meta,bank)
  self.pitch_target_mask=self.terrain.r1_pitch_target_mask
  self.pitch_rough_mask=self.terrain.r1_pitch_rough_mask
  self.pitch_speed=torch.ones(self.num_envs,device=self.device)
  self.pitch_height=torch.full_like(self.pitch_speed,.28)
  self.pitch_stats=torch.zeros(self.num_envs,4,device=self.device)
  self.pitch_transition_peaks=torch.zeros(self.num_envs,2,device=self.device)
  self.last_pitch_reward=torch.zeros(self.num_envs,device=self.device)
  self.pitch_support_seen=torch.zeros(self.num_envs,dtype=torch.bool,device=self.device)
  self.pitch_cost_sums=torch.zeros(self.num_envs,3,device=self.device)
  self.pitch_unloaded_samples=torch.zeros(self.num_envs,device=self.device)
  self.pitch_unloaded_rate2_dt=torch.zeros(self.num_envs,device=self.device)
  self.pitch_action_age=torch.zeros(self.num_envs,device=self.device)
  self.pitch_phase_disagreement_samples=0
  self._pitch_ready=True
  self.velocity_fix_samples=0
  self.velocity_fix_max_delta=0.
  original_postprocess=self.reward._postprocess_reward_terms
  def corrected_velocity_terms(terms):
   d=self.view.data
   changes=horizontal_reward_terms(d.root_lin_vel_b,d.projected_gravity_b,self.reward.command,self.reward.cfg)
   mask=self.pitch_target_mask
   for key,value in changes.items():
    if key in terms:
     delta=(terms[key]-value).abs()[mask]
     if delta.numel():self.velocity_fix_max_delta=max(self.velocity_fix_max_delta,float(delta.max()))
     terms[key]=torch.where(mask,value,terms[key])
   self.velocity_fix_samples+=int(mask.sum())
   return original_postprocess(terms)
  self.reward._postprocess_reward_terms=corrected_velocity_terms

 def _set_origins(self,ids):
  t=self.terrain;target=getattr(t,'r1_pitch_rough_mask',None)
  if target is not None:
   picked=ids[target[ids]]
   t.terrain_levels[picked]=9
   column=(t.r1_column_families==9).nonzero().flatten()[0]
   t.terrain_types[picked]=column
   if hasattr(self,'terrain_family'):self.terrain_family[picked]=9
  return super()._set_origins(ids)

 def _reset_idx(self,ids):
  super()._reset_idx(ids)
  if not getattr(self,'_pitch_ready',False):return
  ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
  self.pitch_support_seen[ids]=False
  self.pitch_action_age[ids]=0.
  picked=ids[self.pitch_target_mask[ids]]
  if not picked.numel():return
  gen=self.reset_generator
  choices=self.command.new_tensor([.6,1.2,2.,2.2]);heights=self.command.new_tensor([.28,.4,.42])
  self.pitch_speed[picked]=choices[torch.randint(4,(len(picked),),device=self.device,generator=gen)]
  self.pitch_speed[picked]*=torch.where(torch.rand(len(picked),device=self.device,generator=gen)<.5,-1.,1.)
  self.pitch_height[picked]=heights[torch.randint(3,(len(picked),),device=self.device,generator=gen)]
  self._ground_command_until[picked]=0;self.r2_air_reset[picked]=False
  self._pitch_commands()

 def _pitch_commands(self):
  if not getattr(self,'_pitch_ready',False):return
  picked=self.pitch_target_mask.nonzero().flatten();age=self.episode_length_buf[picked]*self.step_dt
  vx,moving,phase=transition_command(age,self.pitch_speed[picked])
  self.command[picked]=0.;self.command[picked,0]=vx
  self.height[picked]=self.pitch_height[picked];self.command_timer[picked]=1e9
  self.heading_env[picked]=False;self.standing_env[picked]=~moving
  self._ground_original_command[picked]=self.command[picked];self._ground_original_heading[picked]=False
  self.reward.command[picked]=self.command[picked];self.reward.height_cmd[picked]=self.height[picked]
  self.reward._invalidate_step_caches()

 def _pre_physics_step(self,actions):
  self._pitch_commands()
  # DirectRLEnv increments the counter after physics, before reward.
  self.pitch_action_age.copy_(self.episode_length_buf*self.step_dt)
  return super()._pre_physics_step(actions)

 def _get_observations(self):
  self._pitch_commands()
  return super()._get_observations()

 def _get_rewards(self):
  reward=super()._get_rewards()
  if not getattr(self,'_pitch_ready',False):return reward
  d=self.view.data;pitch=body_pitch(d.projected_gravity_b);rate=d.root_ang_vel_b[:,1]
  forces=tensor(self.scene['contacts'].data.net_forces_w)[:,self.wheel_sensor_ids,2]
  contact=(forces>5.).any(1)
  self.pitch_support_seen,active=stability_active_mask(self.pitch_target_mask,contact,self.pitch_support_seen,self.reset_terminated,self.pitch_action_age)
  # Ground-only specialist has no requested jump; loss of contact must not disable damping.
  unloaded=active&(~contact)
  self.pitch_unloaded_samples+=unloaded
  self.pitch_unloaded_rate2_dt+=rate.square()*self.step_dt*unloaded
  age=self.pitch_action_age
  issued_vx,moving,phase=transition_command(age,self.pitch_speed)
  transition=transition_window(age,self.pitch_speed)
  endpoint_window=transition_window(self.episode_length_buf*self.step_dt,self.pitch_speed)
  self.pitch_phase_disagreement_samples+=int(((transition!=endpoint_window)&active).sum())
  components=stability_components(pitch,rate,active,self.step_dt,transition,command_vx=issued_vx)
  self.pitch_cost_sums+=components
  extra=components.sum(-1);self.last_pitch_reward.copy_(extra)
  self.pitch_stats[:,0]+=active;self.pitch_stats[:,1]+=pitch.square()*active;self.pitch_stats[:,2]+=rate.square()*active
  self.pitch_stats[:,3]=torch.maximum(self.pitch_stats[:,3],pitch.abs()*active)
  issued_vx,moving,phase=transition_command(age,self.pitch_speed)
  startup=active&moving&(phase<.8);braking=active&(~moving)&(phase>=1.)&(phase<1.8)
  self.pitch_transition_peaks[:,0]=torch.maximum(self.pitch_transition_peaks[:,0],pitch.abs()*startup)
  self.pitch_transition_peaks[:,1]=torch.maximum(self.pitch_transition_peaks[:,1],pitch.abs()*braking)
  return reward+extra

 def pitch_summary(self):
  if not getattr(self,'_pitch_ready',False):return dict(ready=False)
  groups={}
  for name,mask in [('random_uniform_level9',self.pitch_rough_mask),('flat_start_stop',self.pitch_target_mask&~self.pitch_rough_mask)]:
   rows=self.pitch_stats[mask];count=rows[:,0].sum();peaks=self.pitch_transition_peaks[mask]
   groups[name]=dict(envs=int(mask.sum()),contact_samples=int(count),pitch_RMS_deg=float(torch.sqrt(rows[:,1].sum()/count.clamp_min(1))*180./torch.pi),pitch_rate_RMS_rad_s=float(torch.sqrt(rows[:,2].sum()/count.clamp_min(1))),pitch_abs_peak_deg=float(rows[:,3].max()*180./torch.pi)if rows.numel()else None,startup_peak_deg=float(peaks[:,0].max()*180./torch.pi)if peaks.numel()else None,braking_peak_deg=float(peaks[:,1].max()*180./torch.pi)if peaks.numel()else None)
  return dict(phase_age_source="action issuance counter captured before physics",phase_disagreement_samples=self.pitch_phase_disagreement_samples,rate_square_coefficient=.05,angle_square_coefficient=0.,prediction_horizon_s=0.,prediction_coefficient=0.,pitch_deadband_deg=0.,scut_gravity_gain_multiplier=.25,scut_upright_potential_weight=2.,scut_upright_sigma=.02,ground_contact_gate='per-episode latched first wheel contact>5N, charged through unintended unloading',reward_component_sums=dict(gravity_angle=float(self.pitch_cost_sums[:,0].sum()),pitch_rate=float(self.pitch_cost_sums[:,1].sum()),upright_potential=float(self.pitch_cost_sums[:,2].sum())),unloaded_samples_still_penalized=int(self.pitch_unloaded_samples.sum()),groups=groups,target_envs=int(self.pitch_target_mask.sum()),random_uniform_levels=self.terrain.terrain_levels[self.pitch_rough_mask].unique().tolist(),retained_tasks_exempt=True,original_speed_coefficients=True,velocity_projection='Exact gravity-orthogonal heading plane, target-only before source weighting',velocity_fix_samples=self.velocity_fix_samples,velocity_fix_max_raw_term_delta=self.velocity_fix_max_delta,scope='Cumulative full-DR on-policy metrics, not fixed model evaluation')

 def terrain_summary(self):
  result=super().terrain_summary()
  if getattr(self,'_pitch_ready',False):result['pitch_stability']=self.pitch_summary()
  return result

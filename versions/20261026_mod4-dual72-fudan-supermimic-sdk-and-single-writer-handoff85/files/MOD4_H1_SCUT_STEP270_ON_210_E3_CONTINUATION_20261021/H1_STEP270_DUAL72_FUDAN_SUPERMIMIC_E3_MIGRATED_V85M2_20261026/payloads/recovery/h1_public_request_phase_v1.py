"""Declared H1 training evidence; external request clock is independent of contact truth.

No actions, observation dimensions, DR RNG, physics setters or added forces.
"""
import torch
PROFILE=dict(version=1,normal_controls=100,jump_controls=80,request_once_per_episode=True,physics_dt=.0025,control_dt=.01,ground_ticks=80,air_ticks=16,landing_ticks=12,recovery_ticks=200,target_wheel_apex_m=.03,ground_support_N=1.,ground_geometric_skin_m=.001,preparation_speed_m_s=.2,preparation_vz_m_s=.2,preparation_tilt_rad=.2617993877991494,recovery_speed_m_s=.03,recovery_tilt_rad=.17453292519943295,recovery_yaw_rad=.2)
class H1PublicRequestPhase:
 def __init__(self,n,device):
  self.n=n;self.device=device
  for k in ('age_control','stable_ticks','air_ticks','land_ticks','recover_ticks','takeoff_count','landing_count','recovery_count'):setattr(self,k,torch.zeros(n,device=device,dtype=torch.long))
  for k in ('ready','anchor_valid','request_for_action','previous_request','attempt','positive_vz','launched','landed','recovered'):setattr(self,k,torch.zeros(n,device=device,dtype=torch.bool))
  for k in ('yaw_reference','peak','paid_peak','event_control'):setattr(self,k,torch.zeros(n,device=device))
 def public_request(self):return (self.age_control>=PROFILE['normal_controls'])&(self.age_control<PROFILE['normal_controls']+PROFILE['jump_controls'])
 def public_mode(self):return torch.where(self.public_request(),4,0)
 def begin_control(self):
  self.event_control.zero_();self.request_for_action.copy_(self.public_request());edge=self.request_for_action&~self.previous_request;self.attempt|=edge&self.ready;self.previous_request.copy_(self.request_for_action)
 def finish_control_before_selected_reset(self):self.age_control.add_(1)
 def reset(self,ids):
  for v in self.tensors().values():v[ids]=0
 def tensors(self):return {k:v for k,v in vars(self).items() if torch.is_tensor(v)}
 def state_dict(self):return dict(profile=PROFILE,num_envs=self.n,tensors={k:v.clone() for k,v in self.tensors().items()},new_rng='none; deterministic external request clock, original command RNG retained separately')
 def load_state_dict(self,state):
  assert state['profile']==PROFILE and state['num_envs']==self.n and state['tensors'].keys()==self.tensors().keys()
  for k,a in self.tensors().items():
   b=state['tensors'][k];assert a.dtype==b.dtype and a.shape==b.shape
   if b.is_floating_point():assert torch.isfinite(b).all()
   a.copy_(b.to(a.device))
 def physical(self,*,wheel_N,wheel_clear_m,all_min_clear_m,nonwheel_max_N,root_vz,root_planar_speed,roll,pitch,yaw):
  # Only reward/evidence receives contact/geometry; none can alter public_mode().
  fresh=~self.anchor_valid;self.yaw_reference.copy_(torch.where(fresh,yaw,self.yaw_reference));self.anchor_valid.fill_(True)
  support=(wheel_N>1).all(-1);clean=nonwheel_max_N<=1;ground=support&clean&(all_min_clear_m>=-.001)
  prepared=ground&~self.request_for_action&~self.attempt&(root_vz.abs()<=.2)&(root_planar_speed<=.2)&(roll.abs()<PROFILE['preparation_tilt_rad'])&(pitch.abs()<PROFILE['preparation_tilt_rad'])
  self.stable_ticks.copy_(torch.where(prepared,self.stable_ticks+1,0));self.ready.copy_(self.stable_ticks>=80)
  self.positive_vz|=self.attempt&(root_vz>.05)
  air=self.attempt&self.positive_vz&(wheel_N<=1).all(-1)&(wheel_clear_m>.005).all(-1)&(all_min_clear_m>0)&clean
  self.air_ticks.copy_(torch.where(air,self.air_ticks+1,0));take=(self.air_ticks>=16)&~self.launched;self.launched|=take
  peak=torch.where(air,(wheel_clear_m.amin(-1)/.03).clamp(0,1),0.);self.peak.copy_(torch.maximum(self.peak,peak));dense=torch.where(self.launched,(self.peak-self.paid_peak).clamp_min(0),0.);self.paid_peak.add_(dense)
  land=ground&self.launched;self.land_ticks.copy_(torch.where(land,self.land_ticks+1,0));landing=(self.land_ticks>=12)&~self.landed;self.landed|=landing
  dyaw=torch.atan2(torch.sin(yaw-self.yaw_reference),torch.cos(yaw-self.yaw_reference))
  stable=ground&self.landed&(root_vz.abs()<=.03)&(root_planar_speed<=.03)&(roll.abs()<PROFILE['recovery_tilt_rad'])&(pitch.abs()<PROFILE['recovery_tilt_rad'])&(dyaw.abs()<.2)
  self.recover_ticks.copy_(torch.where(stable,self.recover_ticks+1,0));recovery=(self.recover_ticks>=200)&~self.recovered;self.recovered|=recovery
  self.takeoff_count.add_(take.long());self.landing_count.add_(landing.long());self.recovery_count.add_(recovery.long());delta=dense+take.float()+2*landing.float()+3*recovery.float();self.event_control.add_(delta)
  return dict(takeoff=take,landing=landing,recovery=recovery,event_delta=delta,air=air,prepared=prepared)

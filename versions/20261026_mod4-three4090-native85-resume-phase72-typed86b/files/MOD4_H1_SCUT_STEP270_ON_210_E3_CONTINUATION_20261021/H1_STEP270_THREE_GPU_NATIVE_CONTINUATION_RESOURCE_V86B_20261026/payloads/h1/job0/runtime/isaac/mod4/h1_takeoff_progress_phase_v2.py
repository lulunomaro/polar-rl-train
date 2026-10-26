"""Isolated training-only prelaunch proxy; original H1 flight/event truth is unchanged.

This is bounded upward root kinetic progress, not measured COM energy, flight,
success or a controller. No actor mode/action/force/reset/RNG is selected here.
"""
import torch
from h1_public_request_phase_v1 import H1PublicRequestPhase,PROFILE as V1_PROFILE
PROFILE=dict(version=2,base_profile=V1_PROFILE,additional_reward='bounded_prelaunch_upward_root_kinetic_proxy',reference_g_m_s2=9.81,reference_rise_m=.03,min_upward_speed_m_s=.05,max_prelaunch_credit=.5,ground_reset_and_public_schedule_unchanged=True,not_flight_or_COM_or_hardware_energy=True)
EXTRA=('progress_peak','progress_paid','progress_control')
class H1TakeoffProgressPhaseV2(H1PublicRequestPhase):
 def __init__(self,n,device):
  super().__init__(n,device)
  for k in EXTRA:setattr(self,k,torch.zeros(n,device=device))
  self.source_migration_history=[]
 def begin_control(self):super().begin_control();self.progress_control.zero_()
 def state_dict(self):return dict(profile=PROFILE,num_envs=self.n,tensors={k:v.clone() for k,v in self.tensors().items()},new_rng='none; public schedule and original private command RNG unchanged')
 def load_state_dict(self,s):
  assert s['num_envs']==self.n;old=s['profile']==V1_PROFILE;assert old or s['profile']==PROFILE;keys=set(self.tensors())-set(EXTRA) if old else set(self.tensors());assert set(s['tensors'])==keys
  for k,v in self.tensors().items():
   if k not in s['tensors']:v.zero_();continue
   x=s['tensors'][k];assert x.shape==v.shape and x.dtype==v.dtype
   if x.is_floating_point():assert torch.isfinite(x).all()
   v.copy_(x.to(v.device))
  self.source_migration_history.append(dict(source_phase_version=1 if old else 2,all_existing_typed_phase_fields_restored=True,new_three_proxy_fields_declared_zero_only_for_V1=old,new_episode_reset_required_by_original_fullrestore=True,no_new_RNG_or_physics_state=True))
 def physical(self,**kw):
  out=super().physical(**kw)
  supported=(kw['wheel_N']>1.).any(-1);clean=kw['nonwheel_max_N']<=1.;upright=(kw['roll'].abs()<V1_PROFILE['preparation_tilt_rad'])&(kw['pitch'].abs()<V1_PROFILE['preparation_tilt_rad']);gate=self.request_for_action&self.attempt&~self.launched&supported&clean&upright&(kw['all_min_clear_m']>=-.001)&(kw['root_planar_speed']<=V1_PROFILE['preparation_speed_m_s'])
  upward=(kw['root_vz']-PROFILE['min_upward_speed_m_s']).clamp_min(0.);potential=(upward.square()/(2*PROFILE['reference_g_m_s2']*PROFILE['reference_rise_m'])).clamp(0.,1.);eligible=torch.where(gate,potential,0.);self.progress_peak.copy_(torch.maximum(self.progress_peak,eligible));delta=(self.progress_peak-self.progress_paid).clamp_min(0.);self.progress_paid.add_(delta);credit=PROFILE['max_prelaunch_credit']*delta;self.progress_control.add_(credit)
  return {**out,'prelaunch_proxy_delta':credit,'prelaunch_proxy_gate':gate}

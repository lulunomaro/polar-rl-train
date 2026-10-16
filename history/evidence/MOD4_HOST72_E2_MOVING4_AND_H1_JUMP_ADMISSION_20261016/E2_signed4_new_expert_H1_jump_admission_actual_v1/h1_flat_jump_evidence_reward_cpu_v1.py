"""Candidate H1 evidence/reward only; never emits actions or mutates physics."""
import numpy as np
DT=.0025
class H1Evidence:
 def __init__(self,n):
  self.n=n;self.support_ticks=np.zeros(n,np.int64);self.air_ticks=np.zeros(n,np.int64);self.land_ticks=np.zeros(n,np.int64);self.recover_ticks=np.zeros(n,np.int64);self.ready=np.zeros(n,bool);self.launched=np.zeros(n,bool);self.landed=np.zeros(n,bool);self.recovered=np.zeros(n,bool);self.positive_vz=np.zeros(n,bool);self.peak=np.zeros(n);self.paid_peak=np.zeros(n)
 def reset(self,ids):
  ids=np.asarray(ids)
  for value in vars(self).values():
   if isinstance(value,np.ndarray):value[ids]=0
 def update(self,*,wheel_force_N,wheel_clearance_m,all_collider_min_clearance_m,nonwheel_force_N,root_vz_m_s,roll_rad,pitch_rad,yaw_error_rad,speed_error_m_s,done,operator_jump):
  force=np.asarray(wheel_force_N);clear=np.asarray(wheel_clearance_m);contact=np.asarray(nonwheel_force_N);minimum=np.asarray(all_collider_min_clearance_m);vz=np.asarray(root_vz_m_s);roll=np.asarray(roll_rad);pitch=np.asarray(pitch_rad);yaw=np.asarray(yaw_error_rad);speed=np.asarray(speed_error_m_s);done=np.asarray(done,dtype=bool);request=np.asarray(operator_jump,dtype=bool)
  if force.shape!=(self.n,2) or clear.shape!=(self.n,2) or contact.ndim!=2 or contact.shape[0]!=self.n:raise ValueError('Actual wheel/all-body contact shape')
  for x in (force,clear,contact,minimum,vz,roll,pitch,yaw,speed):
   if not np.isfinite(x).all():raise ValueError('Incomplete/nonfinite actual collider/contact evidence')
  valid=request&~done;support=(force>1).all(1);self.support_ticks=np.where(support&valid,self.support_ticks+1,0);self.ready|=self.support_ticks>=12;self.positive_vz|=self.ready&valid&(vz>0.05)
  air=valid&self.ready&self.positive_vz&(force<=1).all(1)&(clear>.005).all(1)&(minimum>0)&(contact<=1).all(1);self.air_ticks=np.where(air,self.air_ticks+1,0);takeoff=(self.air_ticks>=16)&~self.launched;self.launched|=takeoff
  self.peak=np.maximum(self.peak,np.where(air,np.minimum(clear.min(1),.03)/.03,0));dense=np.where(self.launched,np.maximum(self.peak-self.paid_peak,0),0);self.paid_peak+=dense
  landed=valid&self.launched&support&(contact<=1).all(1);self.land_ticks=np.where(landed,self.land_ticks+1,0);landing=(self.land_ticks>=12)&~self.landed;self.landed|=landing
  stable=valid&self.landed&support&(contact<=1).all(1)&(abs(roll)<np.deg2rad(10))&(abs(pitch)<np.deg2rad(10))&(abs(yaw)<.2)&(abs(speed)<=.03);self.recover_ticks=np.where(stable,self.recover_ticks+1,0);recovery=(self.recover_ticks>=200)&~self.recovered;self.recovered|=recovery
  reward=dense+takeoff.astype(float)+2*landing.astype(float)+3*recovery.astype(float)
  reward[done]=0;self.reset(np.flatnonzero(done));return dict(control_event_reward=reward,takeoff=takeoff,landing=landing,recovery=recovery,phase_or_support_truth_for_actor=False)

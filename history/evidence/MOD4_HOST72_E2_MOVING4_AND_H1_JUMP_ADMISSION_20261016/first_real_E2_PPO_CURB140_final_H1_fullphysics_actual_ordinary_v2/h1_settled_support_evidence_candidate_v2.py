"""Independent candidate: distinguish reset/position-controller rebound from commanded hop.

CPU evidence only; not installed in a live environment, never produces actions.
"""
import numpy as np
from h1_flat_jump_evidence_reward_cpu_v1 import H1Evidence
class SettledH1Evidence:
 def __init__(self,n):
  self.n=n;self.base=H1Evidence(n);self.settle=np.zeros(n,np.int64);self.armed=np.zeros(n,bool)
 def update(self,**v):
  force=np.asarray(v['wheel_force_N']);non=np.asarray(v['nonwheel_force_N']);done=np.asarray(v['done'],bool);request=np.asarray(v['operator_jump'],bool)
  finite=all(np.isfinite(np.asarray(v[k])).all() for k in ('wheel_force_N','wheel_clearance_m','all_collider_min_clearance_m','nonwheel_force_N','root_vz_m_s','roll_rad','pitch_rad','yaw_error_rad','speed_error_m_s'))
  if not finite:raise ValueError('UNKNOWN/nonfinite physical evidence')
  grounded=(force>1).all(1)&(non<=1).all(1)&(np.asarray(v['all_collider_min_clearance_m'])>=-.001)
  stable=grounded&(abs(v['root_vz_m_s'])<=.03)&(abs(v['speed_error_m_s'])<=.03)&(abs(v['roll_rad'])<np.deg2rad(10))&(abs(v['pitch_rad'])<np.deg2rad(10))&(abs(v['yaw_error_rad'])<.2)&~done
  self.settle=np.where(stable,self.settle+1,0);self.armed|=(self.settle>=200)&request;self.armed[done]=False;self.settle[done]=0
  v=dict(v);v['operator_jump']=request&self.armed
  # V1 did not require whole authored collider clearance at landing. Preserve V1;
  # withhold this candidate's landing/recovery whenever that reference is penetrated.
  invalid_landing=(np.asarray(v['all_collider_min_clearance_m'])<-.001)&self.base.launched
  vv=np.array(v['nonwheel_force_N'],copy=True);vv[invalid_landing]=np.maximum(vv[invalid_landing],2.);v['nonwheel_force_N']=vv
  result=self.base.update(**v);result['settled_ground_armed']=self.armed.copy();return result

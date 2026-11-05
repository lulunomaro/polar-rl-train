"""Existing sensor/PD-D4-DC and 2kHz private audit on P0 v2 robot.
Only target-domain and initialization geometry are adapted; no truth controller.
"""
from pathlib import Path
import sys,json,math
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parent
V1=ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'
sys.path.insert(0,str(V1))
import physics_bridge as oldbridge
from physics_bridge_v3 import BufferedImuPlant as V3Buffered
from RM_ROBUSTNESS_V1.t01_contact_audit import AuditedPlant
from sensor_core import LinkageGeometry
from v2_linearization import V2LinearPlant
from model_builder_v2 import PACKAGE
BOUNDS=(-1.0863195404360622,.49192233306644084)

def geometry():
 pins=json.loads((PACKAGE/'reports/model_manifest.json').read_text(encoding='utf-8'))['neutral_skeleton_xz_m']
 return LinkageGeometry(pins,radius=.0625)

class CylinderSupport:
 """Exact authored finite cylinder support; not a faceted-mesh approximation."""
 def __init__(self,m):
  self.m=m;self.ids=[int(m.geom(s+'_tire').id)for s in ('left','right')]
  if any(int(m.geom_type[i])!=int(mujoco.mjtGeom.mjGEOM_CYLINDER)for i in self.ids):raise ValueError('This P0 support helper requires authored cylinder tires')
 def root_z_translation(self,d,plane_z_m=0.,clearance_m=0.):
  low=[]
  for i in self.ids:
   axis=d.geom_xmat[i].reshape(3,3)[:,2];r,h=self.m.geom_size[i,:2]
   low.append(float(d.geom_xpos[i,2]-r*np.sqrt(max(0.,1.-axis[2]**2))-h*abs(axis[2])))
  return dict(root_dz_m=float(plane_z_m+clearance_m-min(low)),representation='P0 finite cylinder analytic support; initialization only')

class V2Plant(AuditedPlant):
 q_from=V2LinearPlant.q_from
 q_from_full=V2LinearPlant.q_from_full
 def __init__(self,model,imu_offset=(.03,0.,.04)):
  factory=oldbridge.model_factory
  try:
   oldbridge.model_factory=lambda *a,**kw:model
   oldbridge.RobustPlant.__init__(self,False,imu_offset)
  finally:oldbridge.model_factory=factory
  self.radius=float(model.geom_size[self.tires[0],0]);self.nominal_spec_radius=.0625
  self.imu_omega_sum=np.zeros(3);self.imu_acc_sum=np.zeros(3);self.imu_window_count=0
  self.total_highrate_IMU_samples=0;self.rate_sum=np.zeros(6);self.exact_support=CylinderSupport(model)
  self._env=(np.asarray(model.geom_bodyid)==0)&((np.asarray(model.geom_contype)|np.asarray(model.geom_conaffinity))!=0)
  self._main=tuple(map(int,self.tires))
  self._guides={i for i in np.flatnonzero(np.asarray(model.geom_bodyid)>0)if(model.geom(int(i)).name or '').startswith('guide_wheel_')}
  if len(self._guides)!=8:raise ValueError('Expected all 8 P0 guide rollers')
  self.target_projection_calls=0;self._reset_audit()
 def reset(self,*a,**kw):
  V3Buffered.reset(self,*a,**kw);self._reset_audit();self.target_projection_calls=0
 def apply_torque_request(self,tau,packet,dt=.01,mechanical_power_limit=None):
  self._window=__import__('RM_ROBUSTNESS_V1.t01_contact_audit',fromlist=['_bucket'])._bucket();self.audit_samples=[]
  self.last_control_wheel_impulse=np.zeros(2);self.last_control_nonwheel_ticks=0
  tau=np.asarray(tau,float)
  if tau.shape!=(6,)or not np.isfinite(tau).all()or dt!=.01:raise ValueError('Finite six requested Nm / 100Hz required')
  q=np.zeros(6);qd=np.zeros(6);leg=[0,1,3,4]
  q[leg]=packet.joint_pos4;qd[leg]=packet.joint_vel4;qd[[2,5]]=packet.wheel_vel2
  target=q+(tau+self.KD*qd)/self.KP
  target[[2,5]]=qd[[2,5]]+tau[[2,5]]/self.wKD
  # Same nearest-relative-lift then common lift as P0 runtime_adapter_v2:184-192.
  # Current values here are the delivered encoder packet, never root/DR truth.
  for i in (0,3):
   raw_delta=target[i+1]-target[i];current_delta=q[i+1]-q[i]
   delta=np.clip(raw_delta+np.rint((current_delta-raw_delta)/(2*math.pi))*2*math.pi,*BOUNDS)
   hip=target[i]+np.rint((q[i]-target[i])/(2*math.pi))*2*math.pi
   self.target_projection_calls+=int(delta!=raw_delta)
   target[i],target[i+1]=hip,hip+delta
  target[[2,5]]=np.clip(target[[2,5]],-60,60);self.last_request=tau.copy()
  for _ in range(round(dt/self.dt)):
   applied=self.dr.process_targets(target,self.tick_phys)if self.dr else target
   actual_q=self.d.qpos[self.qids];actual_dq=self.d.qvel[self.vids]
   kp=self.dr.KP6 if self.dr else np.array([60.,60.,0.,60.,60.,0.])
   kd=self.dr.KD6 if self.dr else np.array([2.,2.,.6,2.,2.,.6])
   raw=kp*(applied-actual_q)-kd*actual_dq
   raw[[2,5]]=kd[[2,5]]*(applied[[2,5]]-actual_dq[[2,5]])
   bounded=self.clip(self.clip(raw)*(self.dr.motor_gain6 if self.dr else 1.))
   power=float(np.maximum(bounded*actual_dq,0).sum())
   if mechanical_power_limit is not None and power>mechanical_power_limit:bounded*=mechanical_power_limit/power
   self.d.ctrl[:]=bounded
   self.max_mechanical_power=max(self.max_mechanical_power,float(np.maximum(bounded*actual_dq,0).sum()))
   self.max_applied_tau=np.maximum(self.max_applied_tau,np.abs(bounded));self.rate_sum+=self.d.qvel[self.vids]
   mujoco.mj_step(self.m,self.d);self.tick_phys+=1
   self.imu_omega_sum+=self.d.sensor('base_gyro').data;self.imu_acc_sum+=self.d.sensor('base_acceleration').data
   self.imu_window_count+=1;self.total_highrate_IMU_samples+=1;self._grade_contact_sample()

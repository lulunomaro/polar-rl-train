"""R01: actualmeshsupportinit + physics-rate IMUboxcar front-end.
No newcontrollertruthaccess. Averaging approximatesreal high-rateIMUanti-alias;
profile difference vsinstantaneousR00 is explicit, not an originalDRbitidentity.
"""
from pathlib import Path
import sys
import numpy as np,mujoco
from physics_bridge import RobustPlant,ROOT,G,SensorPacket
sys.path.insert(0,str(ROOT/'MODEL_AUDIT/mesh_support_helper_v1'))
from mesh_support import TireMeshSupport
class BufferedImuPlant(RobustPlant):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.imu_omega_sum=np.zeros(3);self.imu_acc_sum=np.zeros(3);self.imu_window_count=0;self.total_highrate_IMU_samples=0;self.exact_support=TireMeshSupport(self.m)
 def reset(self,g,x=0.):
  super().reset(g,x);placement=self.exact_support.root_z_translation(self.d,plane_z_m=0.,clearance_m=0.);self.d.qpos[2]+=placement['root_dz_m'];mujoco.mj_forward(self.m,self.d);self.initial_mesh_support={k:v for k,v in placement.items()if isinstance(v,(str,float,int,bool))};self.imu_omega_sum[:]=0.;self.imu_acc_sum[:]=0.;self.imu_window_count=0;self.total_highrate_IMU_samples=0
 def sensor_packet(self):
  omega=self.imu_omega_sum/self.imu_window_count if self.imu_window_count else self.d.sensor('base_gyro').data.copy();acc=self.imu_acc_sum/self.imu_window_count if self.imu_window_count else self.d.sensor('base_acceleration').data.copy();idx=[1,0,4,3];clean={'omega3':omega.copy(),'gravity3':-acc.copy()/G,'legq4':self.d.qpos[self.qids[idx]].copy(),'legqd4':self.d.qvel[self.vids[idx]].copy(),'wheelqd2':self.d.qvel[self.vids[[2,5]]].copy()};obs=self.dr.observe(clean)if self.dr else clean;age=self.dr.last_feedback_age_us*1e-6 if self.dr else 0.;torque=self.previous_torque.copy()if age>0 and self.previous_torque is not None else self.d.ctrl.copy();self.previous_torque=self.d.ctrl.copy();self.observed=obs;packet=SensorPacket(float(self.d.time)-age,float(self.d.time),obs['omega3'].copy(),-G*obs['gravity3'].copy(),obs['legq4'][[1,0,3,2]].copy(),obs['legqd4'][[1,0,3,2]].copy(),obs['wheelqd2'].copy(),torque);self.last_packet=packet;self.imu_window_count=0;self.imu_omega_sum[:]=0.;self.imu_acc_sum[:]=0.;return packet
 def apply_torque_request(self,tau,packet,dt=.01,mechanical_power_limit=None):
  self.last_control_wheel_impulse=np.zeros(2);self.last_control_nonwheel_ticks=0;ground=self.m.geom('ground').id
  tau=np.asarray(tau,float);assert tau.shape==(6,)and np.isfinite(tau).all();q=np.zeros(6);qd=np.zeros(6);leg=[0,1,3,4];q[leg]=packet.joint_pos4;qd[leg]=packet.joint_vel4;qd[[2,5]]=packet.wheel_vel2;target=q+(tau+self.KD*qd)/self.KP;target[[2,5]]=qd[[2,5]]+tau[[2,5]]/self.wKD;target[leg]=np.clip(target[leg],-3,3)
  for i in(0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
  target[[2,5]]=np.clip(target[[2,5]],-60,60);self.last_request=tau.copy()
  for _ in range(round(dt/self.dt)):
   applied=self.dr.process_targets(target,self.tick_phys)if self.dr else target;actual_q=self.d.qpos[self.qids];actual_dq=self.d.qvel[self.vids];kp=self.dr.KP6 if self.dr else np.array([60.,60.,0.,60.,60.,0.]);kd=self.dr.KD6 if self.dr else np.array([2.,2.,.6,2.,2.,.6]);raw=kp*(applied-actual_q)-kd*actual_dq;raw[[2,5]]=kd[[2,5]]*(applied[[2,5]]-actual_dq[[2,5]]);bounded=self.clip(self.clip(raw)*(self.dr.motor_gain6 if self.dr else 1.));power=float(np.maximum(bounded*actual_dq,0).sum())
   if mechanical_power_limit is not None and power>mechanical_power_limit:bounded*=mechanical_power_limit/power
   self.d.ctrl[:]=bounded;self.max_mechanical_power=max(self.max_mechanical_power,float(np.maximum(bounded*actual_dq,0).sum()));self.max_applied_tau=np.maximum(self.max_applied_tau,np.abs(bounded));mujoco.mj_step(self.m,self.d);self.tick_phys+=1;self.imu_omega_sum+=self.d.sensor('base_gyro').data;self.imu_acc_sum+=self.d.sensor('base_acceleration').data;self.imu_window_count+=1;self.total_highrate_IMU_samples+=1
   hit=False
   for ci,ct in enumerate(self.d.contact):
    a,b=int(ct.geom1),int(ct.geom2)
    if ground not in(a,b):continue
    force=np.zeros(6);mujoco.mj_contactForce(self.m,self.d,ci,force);other=b if a==ground else a
    if other in self.tires:self.last_control_wheel_impulse[self.tires.index(other)]+=max(0.,float(force[0]))*self.dt
    elif force[0]>1:hit=True
   self.last_control_nonwheel_ticks+=int(hit)

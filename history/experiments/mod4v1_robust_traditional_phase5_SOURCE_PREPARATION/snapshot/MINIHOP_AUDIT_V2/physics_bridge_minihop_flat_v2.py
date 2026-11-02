"""Private v2 observer hooks; actuator method byte-identical to v1."""
import numpy as np,mujoco
from physics_bridge_v4_grade import BufferedImuPlant as Base
from MINIHOP_AUDIT_V2.contact_grade_v2 import ReadOnlyGrade
class MiniHopAuditPlant(ReadOnlyGrade,Base):
 def apply_torque_request(self,tau,packet,dt=.01,mechanical_power_limit=None):
  self.last_control_wheel_impulse=np.zeros(2);self.last_control_nonwheel_ticks=0;ground=self.m.geom('ground').id
  tau=np.asarray(tau,float);assert tau.shape==(6,)and np.isfinite(tau).all();q=np.zeros(6);qd=np.zeros(6);leg=[0,1,3,4];q[leg]=packet.joint_pos4;qd[leg]=packet.joint_vel4;qd[[2,5]]=packet.wheel_vel2;target=q+(tau+self.KD*qd)/self.KP;target[[2,5]]=qd[[2,5]]+tau[[2,5]]/self.wKD;target[leg]=np.clip(target[leg],-3,3)
  for i in(0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
  target[[2,5]]=np.clip(target[[2,5]],-60,60);self.last_request=tau.copy()
  for _ in range(round(dt/self.dt)):
   applied=self.dr.process_targets(target,self.tick_phys)if self.dr else target;actual_q=self.d.qpos[self.qids];actual_dq=self.d.qvel[self.vids];kp=self.dr.KP6 if self.dr else np.array([60.,60.,0.,60.,60.,0.]);kd=self.dr.KD6 if self.dr else np.array([2.,2.,.6,2.,2.,.6]);raw=kp*(applied-actual_q)-kd*actual_dq;raw[[2,5]]=kd[[2,5]]*(applied[[2,5]]-actual_dq[[2,5]]);bounded=self.clip(self.clip(raw)*(self.dr.motor_gain6 if self.dr else 1.));power=float(np.maximum(bounded*actual_dq,0).sum())
   if mechanical_power_limit is not None and power>mechanical_power_limit:bounded*=mechanical_power_limit/power
   self._capture_drivepoint(actual_dq,bounded)
   self.d.ctrl[:]=bounded;self.max_mechanical_power=max(self.max_mechanical_power,float(np.maximum(bounded*actual_dq,0).sum()));self.max_applied_tau=np.maximum(self.max_applied_tau,np.abs(bounded));self.rate_sum+=self.d.qvel[self.vids];mujoco.mj_step(self.m,self.d);self.tick_phys+=1;self.imu_omega_sum+=self.d.sensor('base_gyro').data;self.imu_acc_sum+=self.d.sensor('base_acceleration').data;self.imu_window_count+=1;self.total_highrate_IMU_samples+=1
   self._grade_minihop_sample()
   hit=False
   for ci,ct in enumerate(self.d.contact):
    a,b=int(ct.geom1),int(ct.geom2)
    if ground not in(a,b):continue
    force=np.zeros(6);mujoco.mj_contactForce(self.m,self.d,ci,force);other=b if a==ground else a
    if other in self.tires:self.last_control_wheel_impulse[self.tires.index(other)]+=max(0.,float(force[0]))*self.dt
    elif force[0]>1:hit=True
   self.last_control_nonwheel_ticks+=int(hit)

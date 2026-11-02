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
from RAW2K_SHADOW_V1.publisher import ShadowPublisher
class BufferedImuPlant(RobustPlant):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.imu_omega_sum=np.zeros(3);self.imu_acc_sum=np.zeros(3);self.imu_window_count=0;self.total_highrate_IMU_samples=0;self.exact_support=TireMeshSupport(self.m);self.rate_sum=np.zeros(6);self.raw2k_publisher=ShadowPublisher();self.raw2k_records=[];self.raw2k_shadow_frame=None
 def reset(self,g,x=0.):
  super().reset(g,x);placement=self.exact_support.root_z_translation(self.d,plane_z_m=0.,clearance_m=0.);self.d.qpos[2]+=placement['root_dz_m'];mujoco.mj_forward(self.m,self.d);self.initial_mesh_support={k:v for k,v in placement.items()if isinstance(v,(str,float,int,bool))};self.imu_omega_sum[:]=0.;self.imu_acc_sum[:]=0.;self.imu_window_count=0;self.total_highrate_IMU_samples=0;self.rate_sum[:]=0.;self.raw2k_publisher=ShadowPublisher();self.raw2k_records=[];self.raw2k_shadow_frame=None
 def sensor_packet(self):
  self._raw2k_register_source()
  omega=self.imu_omega_sum/self.imu_window_count if self.imu_window_count else self.d.sensor('base_gyro').data.copy();acc=self.imu_acc_sum/self.imu_window_count if self.imu_window_count else self.d.sensor('base_acceleration').data.copy();idx=[1,0,4,3];rates=self.rate_sum/self.imu_window_count if self.imu_window_count else self.d.qvel[self.vids].copy();clean={'omega3':omega.copy(),'gravity3':-acc.copy()/G,'legq4':self.d.qpos[self.qids[idx]].copy(),'legqd4':rates[idx].copy(),'wheelqd2':rates[[2,5]].copy()};obs=self.dr.observe(clean)if self.dr else clean;age=self.dr.last_feedback_age_us*1e-6 if self.dr else 0.;torque=self.previous_torque.copy()if age>0 and self.previous_torque is not None else self.d.ctrl.copy();self.previous_torque=self.d.ctrl.copy();self.observed=obs;packet=SensorPacket(float(self.d.time)-age,float(self.d.time),obs['omega3'].copy(),-G*obs['gravity3'].copy(),obs['legq4'][[1,0,3,2]].copy(),obs['legqd4'][[1,0,3,2]].copy(),obs['wheelqd2'].copy(),torque);self.last_packet=packet;self.raw2k_shadow_frame=self.raw2k_publisher.publish(packet);self.raw2k_records=[];self.imu_window_count=0;self.imu_omega_sum[:]=0.;self.imu_acc_sum[:]=0.;self.rate_sum[:]=0.;return packet
 def apply_torque_request(self,tau,packet,dt=.01,mechanical_power_limit=None):
  self.last_control_wheel_impulse=np.zeros(2);self.last_control_nonwheel_ticks=0;ground=self.m.geom('ground').id
  tau=np.asarray(tau,float);assert tau.shape==(6,)and np.isfinite(tau).all();q=np.zeros(6);qd=np.zeros(6);leg=[0,1,3,4];q[leg]=packet.joint_pos4;qd[leg]=packet.joint_vel4;qd[[2,5]]=packet.wheel_vel2;target=q+(tau+self.KD*qd)/self.KP;target[[2,5]]=qd[[2,5]]+tau[[2,5]]/self.wKD;target[leg]=np.clip(target[leg],-3,3)
  for i in(0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
  target[[2,5]]=np.clip(target[[2,5]],-60,60);self.last_request=tau.copy()
  for _ in range(round(dt/self.dt)):
   applied=self.dr.process_targets(target,self.tick_phys)if self.dr else target;actual_q=self.d.qpos[self.qids];actual_dq=self.d.qvel[self.vids];kp=self.dr.KP6 if self.dr else np.array([60.,60.,0.,60.,60.,0.]);kd=self.dr.KD6 if self.dr else np.array([2.,2.,.6,2.,2.,.6]);raw=kp*(applied-actual_q)-kd*actual_dq;raw[[2,5]]=kd[[2,5]]*(applied[[2,5]]-actual_dq[[2,5]]);bounded=self.clip(self.clip(raw)*(self.dr.motor_gain6 if self.dr else 1.));power=float(np.maximum(bounded*actual_dq,0).sum())
   if mechanical_power_limit is not None and power>mechanical_power_limit:bounded*=mechanical_power_limit/power
   self.d.ctrl[:]=bounded;self.max_mechanical_power=max(self.max_mechanical_power,float(np.maximum(bounded*actual_dq,0).sum()));self.max_applied_tau=np.maximum(self.max_applied_tau,np.abs(bounded));private_raw=self._raw2k_before_step();self.rate_sum+=self.d.qvel[self.vids];mujoco.mj_step(self.m,self.d);self.tick_phys+=1;self.imu_omega_sum+=self.d.sensor('base_gyro').data;self.imu_acc_sum+=self.d.sensor('base_acceleration').data;self.imu_window_count+=1;self.total_highrate_IMU_samples+=1;self._raw2k_after_step(private_raw)
   hit=False
   for ci,ct in enumerate(self.d.contact):
    a,b=int(ct.geom1),int(ct.geom2)
    if ground not in(a,b):continue
    force=np.zeros(6);mujoco.mj_contactForce(self.m,self.d,ci,force);other=b if a==ground else a
    if other in self.tires:self.last_control_wheel_impulse[self.tires.index(other)]+=max(0.,float(force[0]))*self.dt
    elif force[0]>1:hit=True
   self.last_control_nonwheel_ticks+=int(hit)

 def _raw2k_before_step(self):
  stamp=int(round(float(self.d.time)*1e6));q=self.d.qpos[self.qids].copy();qd=self.d.qvel[self.vids].copy()
  return dict(sampled_us=stamp,encoder_pos_sampled_us=stamp,encoder_rate_sampled_us=stamp,joint_pos4=q[[0,1,3,4]].copy(),joint_vel4=qd[[0,1,3,4]].copy(),wheel_vel2=qd[[2,5]].copy())
 def _raw2k_after_step(self,record):
  # mj_step reports dynamics-stage IMU at the PRE-step epoch, same as saved q/qd.
  record.update(gyro_body=self.d.sensor('base_gyro').data.copy(),accel_proper_body=self.d.sensor('base_acceleration').data.copy());self.raw2k_records.append(record)
 def _raw2k_register_source(self):
  epoch=int(round(float(self.d.time)*1e6));count=int(self.imu_window_count);endpoint=self.d.qpos[self.qids[[0,1,3,4]]].copy()
  if count:
   assert count==20 and len(self.raw2k_records)==20
   rates=self.rate_sum/count;clean_mean=dict(gyro_body=self.imu_omega_sum/count,accel_proper_body=self.imu_acc_sum/count,joint_vel4=rates[[0,1,3,4]],wheel_vel2=rates[[2,5]])
   self.raw2k_publisher.register(epoch,epoch-10000,self.raw2k_records,clean_mean,endpoint)
  else:
   record=self._raw2k_before_step();record.update(gyro_body=self.d.sensor('base_gyro').data.copy(),accel_proper_body=self.d.sensor('base_acceleration').data.copy());clean_mean={k:record[k]for k in('gyro_body','accel_proper_body','joint_vel4','wheel_vel2')};self.raw2k_publisher.register(epoch,epoch,[record],clean_mean,endpoint,instant=True)

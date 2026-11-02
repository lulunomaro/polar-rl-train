"""Instrumentation-onlybridge. Cachesensors/actuationidenticaltoV3; read-onlycontactgrading."""
import numpy as np,mujoco
from physics_bridge_v4_grade import BufferedImuPlant
class ContactAuditPlant(BufferedImuPlant):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.audit_armed=False;self.audit_samples=[];self.air_run=0.;self.max_full_air=0.;self.full_air_confirmed=False;self.first_full_air=None;self.first_landing=None;self.guide_contact_ticks=0;self.hard_contact_ticks=0
 def _grade_contact_sample(self):
  if not self.audit_armed:return
  contacts=[];main=np.zeros(2);guide=0.;hard=0.;world={self.m.geom('ground').id,self.m.geom('step270').id}
  for ci,ct in enumerate(self.d.contact):
   a,b=int(ct.geom1),int(ct.geom2)
   if a not in world and b not in world:continue
   robot=b if a in world else a;env=a if a in world else b;force=np.zeros(6);mujoco.mj_contactForce(self.m,self.d,ci,force);fn=max(0.,float(force[0]))
   if fn<=1.:continue
   name=self.m.geom(robot).name;kind='main_wheel'if robot in self.tires else'guide_roller'if name.startswith('guide_wheel_')else'hard_other'
   if kind=='main_wheel':main[self.tires.index(robot)]+=fn
   elif kind=='guide_roller':guide+=fn
   else:hard+=fn
   contacts.append(dict(robot_geom=name,robot_body=self.m.body(int(self.m.geom_bodyid[robot])).name,environment_geom=self.m.geom(env).name,normal_N=fn,kind=kind))
  stage=max(0.,float(self.d.time)-self.dt);total=float(main.sum())+guide+hard
  self.air_run=self.air_run+self.dt if total<=1. else 0.;self.max_full_air=max(self.max_full_air,self.air_run)
  if not self.full_air_confirmed and self.air_run>=.02:self.full_air_confirmed=True;self.first_full_air=stage-self.air_run+self.dt
  if self.full_air_confirmed and self.first_landing is None and total>1.:self.first_landing=dict(time_s=stage,contacts=contacts)
  self.guide_contact_ticks+=guide>1.;self.hard_contact_ticks+=hard>1.;self.audit_samples.append(dict(time_s=stage,main_normal_N2=main.tolist(),guide_normal_N=guide,hard_other_normal_N=hard,all_ground_force_N=total,fullair_run_s=self.air_run,contacts=contacts))
 def apply_torque_request(self,tau,packet,dt=.01,mechanical_power_limit=None):
  self.last_control_wheel_impulse=np.zeros(2);self.last_control_nonwheel_ticks=0;ground=self.m.geom('ground').id
  tau=np.asarray(tau,float);assert tau.shape==(6,)and np.isfinite(tau).all();q=np.zeros(6);qd=np.zeros(6);leg=[0,1,3,4];q[leg]=packet.joint_pos4;qd[leg]=packet.joint_vel4;qd[[2,5]]=packet.wheel_vel2;target=q+(tau+self.KD*qd)/self.KP;target[[2,5]]=qd[[2,5]]+tau[[2,5]]/self.wKD;target[leg]=np.clip(target[leg],-3,3)
  for i in(0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
  target[[2,5]]=np.clip(target[[2,5]],-60,60);self.last_request=tau.copy()
  for _ in range(round(dt/self.dt)):
   applied=self.dr.process_targets(target,self.tick_phys)if self.dr else target;actual_q=self.d.qpos[self.qids];actual_dq=self.d.qvel[self.vids];kp=self.dr.KP6 if self.dr else np.array([60.,60.,0.,60.,60.,0.]);kd=self.dr.KD6 if self.dr else np.array([2.,2.,.6,2.,2.,.6]);raw=kp*(applied-actual_q)-kd*actual_dq;raw[[2,5]]=kd[[2,5]]*(applied[[2,5]]-actual_dq[[2,5]]);bounded=self.clip(self.clip(raw)*(self.dr.motor_gain6 if self.dr else 1.));power=float(np.maximum(bounded*actual_dq,0).sum())
   if mechanical_power_limit is not None and power>mechanical_power_limit:bounded*=mechanical_power_limit/power
   self.d.ctrl[:]=bounded;self.max_mechanical_power=max(self.max_mechanical_power,float(np.maximum(bounded*actual_dq,0).sum()));self.max_applied_tau=np.maximum(self.max_applied_tau,np.abs(bounded));self.rate_sum+=self.d.qvel[self.vids];mujoco.mj_step(self.m,self.d);self.tick_phys+=1;self.imu_omega_sum+=self.d.sensor('base_gyro').data;self.imu_acc_sum+=self.d.sensor('base_acceleration').data;self.imu_window_count+=1;self.total_highrate_IMU_samples+=1
   self._grade_contact_sample()
   hit=False
   for ci,ct in enumerate(self.d.contact):
    a,b=int(ct.geom1),int(ct.geom2)
    if ground not in(a,b):continue
    force=np.zeros(6);mujoco.mj_contactForce(self.m,self.d,ci,force);other=b if a==ground else a
    if other in self.tires:self.last_control_wheel_impulse[self.tires.index(other)]+=max(0.,float(force[0]))*self.dt
    elif force[0]>1:hit=True
   self.last_control_nonwheel_ticks+=int(hit)

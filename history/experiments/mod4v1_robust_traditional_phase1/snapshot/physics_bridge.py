"""NewMOD4v1 MuJoCo bridge. Oldsources imported read-only; oldonce/main notrun.
Sensors and grading are separate interfaces. No controller method reads roottruth.
"""
from pathlib import Path
import sys,json,math,hashlib,xml.etree.ElementTree as ET
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'traditional_control_20261101';sys.path.insert(0,str(OLD))
import control_core as oldcore
from full_lqr import AsymmetricPlant
from dr_components import FullDR
from sensor_core import SensorPacket,LinkageGeometry,G
MODEL_SHA='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'
MODEL_FILE='mod4v1_usd_source_aligned.xml'
MODEL_WHEEL_RADIUS=.06369999796152115 # authoredUSDcollisioncircumradius; notmeasuredrollingcalibration

def model_factory(step=False,imu_offset=(.03,0.,.04),physics_dt=.0005):
 path=ROOT/'MODEL_AUDIT'/MODEL_FILE;raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==MODEL_SHA;xml=ET.fromstring(raw);xml.find('compiler').set('meshdir',str(path.parent));xml.find('option').set('timestep',str(physics_dt));imu=xml.find(".//site[@name='imu']");imu.set('pos',' '.join(map(str,imu_offset)))
 if step:ET.SubElement(xml.find('worldbody'),'geom',name='step270',type='box',pos='1.5 0 .135',size='1.5 1 .135',contype='1',conaffinity='2',friction='.9 .003 .0001',rgba='.3 .5 .7 1')
 return mujoco.MjModel.from_xml_string(ET.tostring(xml,encoding='unicode'))

class RobustPlant(AsymmetricPlant):
 def __init__(self,step=False,imu_offset=(.03,0.,.04)):
  self.m=model_factory(step,imu_offset);self.d=mujoco.MjData(self.m);self.tmp=mujoco.MjData(self.m);self.qids=np.array([self.m.joint(n).qposadr[0]for n in oldcore.ORDER]);self.vids=np.array([self.m.joint(n).dofadr[0]for n in oldcore.ORDER]);self.chassis=self.m.body('chassis').id;self.wheels=[self.m.body(s+'_wheel').id for s in('left','right')];self.tires=[self.m.geom(s+'_tire').id for s in('left','right')];self.pairs=[(self.m.site(a).id,self.m.site(b).id)for a,b in oldcore.PAIRS];self.mass=float(self.m.body_mass.sum());self.radius=MODEL_WHEEL_RADIUS;self.nominal_spec_radius=.0625;self.KP=60.;self.KD=2.;self.wKD=.6;self.dt=float(self.m.opt.timestep);self.substeps=20;self.max_tau=np.array([40,40,5.775909774436091]*2);self.stall=np.array([53.3333333333333,53.3333333333333,28.18532894736838]*2);self.no_load=np.array([16.755160819145562,16.755160819145562,55.3557]*2);self.history=[];self.applied=[];self.dr=None;self.observed=None;self.tick_phys=0;self.use_full_lqr=True;self.imu_offset=np.asarray(imu_offset);self.previous_torque=None;self.last_packet=None;self.last_request=np.zeros(6);self.max_mechanical_power=0.;self.max_applied_tau=np.zeros(6)
 def sensor_packet(self):
  # Sensorarrayvalues are simulator equivalents of IMU and encoder registers.
  # gravity3 in legacyDR is deliberately RAW -properaccel/g here, not truthgravity.
  idx=[1,0,4,3];clean={'omega3':self.d.sensor('base_gyro').data.copy(),'gravity3':-self.d.sensor('base_acceleration').data.copy()/G,'legq4':self.d.qpos[self.qids[idx]].copy(),'legqd4':self.d.qvel[self.vids[idx]].copy(),'wheelqd2':self.d.qvel[self.vids[[2,5]]].copy()};obs=self.dr.observe(clean)if self.dr else clean;age=(self.dr.last_feedback_age_us*1e-6)if self.dr else 0.;torque=self.previous_torque.copy()if age>0 and self.previous_torque is not None else self.d.ctrl.copy();self.previous_torque=self.d.ctrl.copy();self.observed=obs;packet=SensorPacket(float(self.d.time)-age,float(self.d.time),obs['omega3'].copy(),-G*obs['gravity3'].copy(),obs['legq4'][[1,0,3,2]].copy(),obs['legqd4'][[1,0,3,2]].copy(),obs['wheelqd2'].copy(),torque);self.last_packet=packet;return packet
 def apply_torque_request(self,tau,packet,dt=.01,mechanical_power_limit=None):
  # Original inversePD processed-target interface preservedasdiagnostic baseline.
  # ItisnotyetconfirmedDM3519/C-boardelectricaldeploymentmapping.
  tau=np.asarray(tau,float);assert tau.shape==(6,)and np.isfinite(tau).all();q=np.zeros(6);qd=np.zeros(6);leg=[0,1,3,4];q[leg]=packet.joint_pos4;qd[leg]=packet.joint_vel4;qd[[2,5]]=packet.wheel_vel2;target=q+(tau+self.KD*qd)/self.KP;target[[2,5]]=qd[[2,5]]+tau[[2,5]]/self.wKD;target[leg]=np.clip(target[leg],-3,3)
  for i in(0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
  target[[2,5]]=np.clip(target[[2,5]],-60,60);self.last_request=tau.copy()
  for _ in range(round(dt/self.dt)):
   applied=self.dr.process_targets(target,self.tick_phys)if self.dr else target;actual_q=self.d.qpos[self.qids];actual_dq=self.d.qvel[self.vids];kp=self.dr.KP6 if self.dr else np.array([60.,60.,0.,60.,60.,0.]);kd=self.dr.KD6 if self.dr else np.array([2.,2.,.6,2.,2.,.6]);raw=kp*(applied-actual_q)-kd*actual_dq;raw[[2,5]]=kd[[2,5]]*(applied[[2,5]]-actual_dq[[2,5]]);bounded=self.clip(self.clip(raw)*(self.dr.motor_gain6 if self.dr else 1.));power=float(np.maximum(bounded*actual_dq,0).sum())
   if mechanical_power_limit is not None and power>mechanical_power_limit:bounded*=mechanical_power_limit/power
   self.d.ctrl[:]=bounded;self.max_mechanical_power=max(self.max_mechanical_power,float(np.maximum(bounded*actual_dq,0).sum()));self.max_applied_tau=np.maximum(self.max_applied_tau,np.abs(bounded));mujoco.mj_step(self.m,self.d);self.tick_phys+=1
  return self.d.ctrl.copy()
 def grade(self):
  # Groundtruth neverpassedtoStateEstimator/controller; gradinghasitsowninterface.
  h=self.health();R=self.d.xmat[self.chassis].reshape(3,3);vb=R.T@self.d.qvel[:3];omega=self.d.sensor('base_gyro').data.copy();return dict(**h,body_velocity=vb.tolist(),gyro_true=omega.tolist(),yaw_true=math.atan2(R[1,0],R[0,0]),pitch_true=math.atan2(-R[2,0],math.hypot(R[0,0],R[1,0])),roll_true=math.atan2(R[2,1],R[2,2]))

def geometry():
 pins=json.loads((OLD/'reports/model_manifest.json').read_bytes())['neutral_skeleton_xz_m'];return LinkageGeometry(pins,radius=MODEL_WHEEL_RADIUS)

def serialize_gain(g):
 def cv(v):
  if isinstance(v,dict):return{k:cv(a)for k,a in v.items()}
  if isinstance(v,np.ndarray):
   if np.iscomplexobj(v):return[[float(z.real),float(z.imag)]for z in v]
   return v.tolist()
  if isinstance(v,np.generic):return v.item()
  return v
 return cv(g)
def load_gain(path):
 g=json.loads(Path(path).read_bytes())['gain']
 return{k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in g.items()}

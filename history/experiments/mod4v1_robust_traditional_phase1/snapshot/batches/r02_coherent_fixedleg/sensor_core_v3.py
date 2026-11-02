"""Platform-independent sensor mathematics prototype; no MuJoCo/plant imports.

Controller inputs are timestamped IMU/encoder packets. Simulator truth is NOT
accepted by this module. Geometry constants come from an explicitly supplied
neutral linkage model. Python prototype precedes a separately tested C port.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

G=9.81

def wrap(a):return math.atan2(math.sin(a),math.cos(a))
def quat_mul(a,b):
 w,x,y,z=a;v,i,j,k=b
 return np.array([w*v-x*i-y*j-z*k,w*i+x*v+y*k-z*j,w*j-x*k+y*v+z*i,w*k+x*j-y*i+z*v])
def quat_step(q,omega,dt):
 a=np.asarray(omega,float)*dt;n=float(np.linalg.norm(a));r=np.r_[math.cos(n/2),a*(math.sin(n/2)/n if n>1e-12 else .5)]
 o=quat_mul(q,r);return o/np.linalg.norm(o)
def quat_from_rpy(roll,pitch,yaw):
 cr,sr=math.cos(roll/2),math.sin(roll/2);cp,sp=math.cos(pitch/2),math.sin(pitch/2);cy,sy=math.cos(yaw/2),math.sin(yaw/2)
 return np.array([cr*cp*cy+sr*sp*sy,sr*cp*cy-cr*sp*sy,cr*sp*cy+sr*cp*sy,cr*cp*sy-sr*sp*cy])
def rotation(q):
 w,x,y,z=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
def rpy(q):
 R=rotation(q);return np.array([math.atan2(R[2,1],R[2,2]),math.atan2(-R[2,0],math.hypot(R[0,0],R[1,0])),math.atan2(R[1,0],R[0,0])])
def compensate_lever_arm(accel_at_imu,omega,alpha,imu_from_origin_body):
 """All arguments BODY frame. Offset is origin->IMU; return origin properaccel."""
 r=np.asarray(imu_from_origin_body,float)
 return np.asarray(accel_at_imu,float)-np.cross(alpha,r)-np.cross(omega,np.cross(omega,r))

class LinkageGeometry:
 """Closed CAD planar loop; all output coordinates remain chassis-frame meters."""
 def __init__(self,pins,track=.4376,radius=.0625):
  self.pins={s:{k:np.asarray(v,float)for k,v in p.items()}for s,p in pins.items()};self.track=track;self.radius=radius
 @staticmethod
 def rotate(v,q):
  c,s=math.cos(q),math.sin(q);return np.array([c*v[0]+s*v[1],-s*v[0]+c*v[1]])
 @staticmethod
 def angle(v,w):return wrap(-(math.atan2(w[1],w[0])-math.atan2(v[1],v[0])))
 @staticmethod
 def intersect(a,ra,b,rb,sign):
  d=b-a;length=float(np.linalg.norm(d))
  if not abs(ra-rb)+1e-7<length<ra+rb-1e-7:raise ValueError('Linkage unreachable or singular')
  t=(ra*ra-rb*rb+length*length)/(2*length);h=math.sqrt(max(0.,ra*ra-t*t));x=d/length;y=np.array([-x[1],x[0]]);return a+t*x+sign*h*y
 def pose(self,hip,crank,side):
  p=self.pins[side];L=lambda a,b:float(np.linalg.norm(p[a]-p[b]));cross=lambda a,b:a[0]*b[1]-a[1]*b[0]
  q={k:self.rotate(v,hip)for k,v in p.items()};q['A']=self.rotate(p['A'],crank);q['B']=self.intersect(q['A'],L('A','B'),q['P'],L('B','P'),math.copysign(1.,cross(p['P']-p['A'],p['B']-p['A'])))
  rocker=self.angle(p['B']-p['P'],q['B']-q['P']);q['C']=q['P']+self.rotate(p['C']-p['P'],rocker);q['D']=self.intersect(q['K'],L('K','D'),q['C'],L('C','D'),math.copysign(1.,cross(p['C']-p['K'],p['D']-p['K'])))
  shin=self.angle(p['D']-p['K'],q['D']-q['K']);w=q['K']+self.rotate(p['W']-p['K'],shin);return np.array([w[0],self.track/2 if side=='left'else-self.track/2,w[1]]),wrap(shin-hip)
 def wheel_kinematics(self,hip,crank,hipdot,crankdot,spin,omega,side):
  r,knee=self.pose(hip,crank,side);eps=1e-5;der=[]
  for dh,dc in((eps,0.),(0.,eps)):
   a,ka=self.pose(hip+dh,crank+dc,side);b,kb=self.pose(hip-dh,crank-dc,side);der.append((a-b)/(2*eps));der[-1]=np.r_[der[-1],wrap(ka-kb)/(2*eps)]
  dq=np.array([hipdot,crankdot]);J=np.array(der).T;relative=J[:3]@dq;kneedot=float(J[3]@dq)
  omega_wheel_y=float(omega[1]+hipdot+kneedot+spin)
  root_v_forward=self.radius*omega_wheel_y-float(relative[0])-float(np.cross(omega,r)[0]);return root_v_forward,r,J[:3],knee

@dataclass(frozen=True)
class SensorPacket:
 time_s:float
 arrival_s:float
 gyro_body:np.ndarray
 accel_proper_body:np.ndarray
 joint_pos4:np.ndarray # Lhip,Lcrank,Rhip,Rcrank, not RL order
 joint_vel4:np.ndarray
 wheel_vel2:np.ndarray
 motor_torque6:np.ndarray|None=None
 validity:bool=True
 def validate(self):
  arrays=[(self.gyro_body,3),(self.accel_proper_body,3),(self.joint_pos4,4),(self.joint_vel4,4),(self.wheel_vel2,2)]
  if not self.validity or not math.isfinite(self.time_s)or not math.isfinite(self.arrival_s)or self.arrival_s+1e-9<self.time_s:raise ValueError('Invalid sensor timestamps/validity')
  for a,n in arrays:
   if np.shape(a)!=(n,)or not np.isfinite(a).all():raise ValueError('Invalid sensor vector')

@dataclass
class Estimate:
 state14:np.ndarray
 roll:float
 omega_body:np.ndarray
 proper_acc_origin:np.ndarray
 velocity_variance:float
 measured_wheel_forward2:np.ndarray
 sensor_age_s:float
 estimated_time_s:float
 slip_innovation:float
 contact_confidence:float

class StateEstimator:
 """Gyro/acc complementary attitude +2-state velocity/bias Kalman prototype.

 No ground truth/collision read. Contact confidence here is a measurement
 consistency proxy, NOT independently validated wheel force or landing truth.
 Sensor acquisition age comes from a packet timestamp, not DR coefficients.
 """
 def __init__(self,geometry,imu_offset=(0.,0.,0.),accel_correction=1.5,wheel_std=.065,accel_std=.5,accel_reference="chassis",innovation_limit=1.):
  self.geom=geometry;self.offset=np.asarray(imu_offset,float);self.innovation_limit=innovation_limit;self.accel_reference=accel_reference;self.accel_correction=accel_correction;self.wheel_std=wheel_std;self.accel_std=accel_std;self.reset()
 def reset(self):
  self.q=None;self.prev_stamp=None;self.prev_omega=None;self.alpha=np.zeros(3);self.last_yaw_wrapped=0.;self.yaw=0.;self.distance=0.;self.vb=np.zeros(2);self.P=np.diag([.05,.1]);self.prev_wheel=0.;self.wheel_acc=0.;self.last=None
 def update(self,p:SensorPacket):
  p.validate();stamp=float(p.time_s)
  if self.prev_stamp is not None and stamp<=self.prev_stamp+1e-10:
   if abs(stamp-self.prev_stamp)<1e-9 and self.last is not None:return self._predict_view(self.last,p.arrival_s)
   raise ValueError('Out-of-order sensor packet')
  first=self.prev_stamp is None;dt=0. if first else stamp-self.prev_stamp
  if not first and not 0.<dt<=.1:raise ValueError('Sensor timeout')
  omega=np.asarray(p.gyro_body,float)
  if self.prev_omega is not None:self.alpha+=dt/(.06+dt)*((omega-self.prev_omega)/dt-self.alpha)
  proper=compensate_lever_arm(p.accel_proper_body,omega,self.alpha,self.offset)
  if self.q is None:
   unit=proper/max(float(np.linalg.norm(proper)),1e-9);roll=math.atan2(unit[1],unit[2]);pitch=math.atan2(-unit[0],math.hypot(unit[1],unit[2]));
   if abs(float(np.linalg.norm(proper))-G)>.3*G:roll=pitch=0. # declareduprightarmingpriorforunsettledfirstIMUsample, nottruth
   self.q=quat_from_rpy(roll,pitch,0.);self.last_yaw_wrapped=0.
  wheel=[];positions=[]
  for j,side in enumerate(('left','right')):
   v,position,_,_=self.geom.wheel_kinematics(p.joint_pos4[2*j],p.joint_pos4[2*j+1],p.joint_vel4[2*j],p.joint_vel4[2*j+1],p.wheel_vel2[j],omega,side);wheel.append(v);positions.append(position)
  wheel=np.asarray(wheel);wheel_mean=float(np.mean(wheel));raw_acc=0. if first else (wheel_mean-self.prev_wheel)/dt;self.wheel_acc+=dt/(.12+dt)*(np.clip(raw_acc,-8,8)-self.wheel_acc)
  pivot=np.mean(positions,axis=0);pivot_rotation=np.cross(self.alpha,pivot)+np.cross(omega,np.cross(omega,pivot)) if self.accel_reference=="wheel_midpoint"else np.zeros(3)
  expected=np.array([self.wheel_acc,omega[2]*self.vb[0],0.]);gravity_candidate=proper+pivot_rotation-expected;norm=float(np.linalg.norm(gravity_candidate));confidence=max(0.,1.-abs(norm-G)/(G*.35));predicted_up=rotation(self.q).T[:,2];innovation=float(np.linalg.norm(gravity_candidate-G*predicted_up));confidence*=max(0.,1.-innovation/self.innovation_limit) if self.innovation_limit>0 else 1.;error=np.cross(gravity_candidate/max(norm,1e-9),predicted_up)
  self.q=quat_step(self.q,omega+self.accel_correction*confidence*np.clip(error,-.3,.3),dt);angles=rpy(self.q);self.yaw+=wrap(float(angles[2])-self.last_yaw_wrapped);self.last_yaw_wrapped=float(angles[2]);gravity_body=rotation(self.q).T@np.array([0.,0.,-G]);linear=proper+gravity_body
  if self.accel_reference=="wheel_midpoint":
   origin_v_transverse=-np.cross(omega,pivot);linear[0]+=omega[2]*origin_v_transverse[1]-omega[1]*origin_v_transverse[2]
  F=np.array([[1.,-dt],[0.,1.]]);self.vb=F@self.vb+np.array([dt*linear[0],0.]);self.P=F@self.P@F.T+np.diag([(self.accel_std*dt)**2,(.015*dt)**2]);innovation=wheel_mean-self.vb[0];disagreement=float(abs(wheel[0]-wheel[1]));R=self.wheel_std**2*(1.+min(30.,(disagreement/.15)**2));S=float(self.P[0,0]+R);K=self.P[:,0]/S;self.vb+=K*innovation;I=np.eye(2);H=np.array([[1.,0.]]);A=I-K[:,None]@H;self.P=A@self.P@A.T+R*np.outer(K,K);self.distance+=self.vb[0]*dt
  roll,pitch=float(angles[0]),float(angles[1]);pitchdot=omega[1]*math.cos(roll)-omega[2]*math.sin(roll);yawdot=(omega[1]*math.sin(roll)+omega[2]*math.cos(roll))/max(math.cos(pitch),.15);lq=p.joint_pos4;lv=p.joint_vel4
  x=np.array([self.distance,self.yaw,pitch,lq[0],lq[1]-lq[0],lq[2],lq[3]-lq[2],self.vb[0],yawdot,pitchdot,lv[0],lv[1]-lv[0],lv[2],lv[3]-lv[2]])
  contact=float(np.clip(confidence*(1.-min(1.,disagreement/.7)),0,1));e=Estimate(x,roll,omega.copy(),proper.copy(),float(self.P[0,0]),wheel.copy(),max(0.,p.arrival_s-stamp),stamp,float(innovation),contact);self.prev_stamp=stamp;self.prev_omega=omega.copy();self.prev_wheel=wheel_mean;self.last=e;return self._predict_view(e,p.arrival_s)
 def _predict_view(self,e,now):
  # First-order propagation uses only gyro/encoder/estimatedvelocity, neveroracleD4.
  age=max(0.,float(now)-e.estimated_time_s)
  if age>.05:raise ValueError('Stale feedback')
  x=e.state14.copy();x[:7]+=age*x[7:14];return Estimate(x,e.roll,e.omega_body.copy(),e.proper_acc_origin.copy(),e.velocity_variance,e.measured_wheel_forward2.copy(),age,float(now),e.slip_innovation,e.contact_confidence)

class CommandShaper:
 def __init__(self,accel=2.,yaw_accel=8.,jerk=10.):self.v=0.;self.w=0.;self.a=0.;self.accel=accel;self.yaw_accel=yaw_accel;self.jerk=jerk
 def update(self,v,w,dt):
  if not math.isfinite(dt)or dt<=0:raise ValueError('Positive finite controlperiod required')
  olda=self.a;j=float(np.clip(16.*(v-self.v)-8.*self.a,-self.jerk,self.jerk));self.a=float(np.clip(self.a+j*dt,-self.accel,self.accel));self.v+=.5*(olda+self.a)*dt
  if abs(v-self.v)<1e-5 and abs(self.a)<self.jerk*dt:self.v=float(v);self.a=0.
  self.w+=float(np.clip(w-self.w,-self.yaw_accel*dt,self.yaw_accel*dt));return self.v,self.w

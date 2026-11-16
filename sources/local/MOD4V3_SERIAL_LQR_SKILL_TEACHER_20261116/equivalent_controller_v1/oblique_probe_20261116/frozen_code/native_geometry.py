"""MOD4 native closed-chain FK, Jacobians and inertial/passive force projection.
The source controller's virtual theta is -atan2(x,-z), despite MOD4 native +Y axes.
No policy/checkpoint or source trajectory is used by this module.
"""
from pathlib import Path
import sys,importlib.util,json,functools,math
import numpy as np,mujoco as mj
ROOT=Path(__file__).resolve().parent;T=ROOT.parent;R=T.parents[2]
PLANT=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/plant/MOD4v3_HW300N60_R3'
sys.path.insert(0,str(PLANT))
spec=importlib.util.spec_from_file_location('mod4_exact_native_kinematics',PLANT/'kinematics.py');KIN=importlib.util.module_from_spec(spec);spec.loader.exec_module(KIN)
API=KIN.Semantics(PLANT)
sys.path.remove(str(PLANT))
class NativeGeometry:
 def __init__(self):
  self.m=mj.MjModel.from_xml_path(str(PLANT/'mjcf/scene.xml'));self.d=mj.MjData(self.m);self.d.qpos[:3]=0.;self.d.qpos[3:7]=[1,0,0,0];mj.mj_kinematics(self.m,self.d)
  self.base=self.m.body('base_link').id;self.names=API.native_names;self.qadr=np.array([self.m.jnt_qposadr[self.m.joint(n).id]for n in self.names]);self.dadr=np.array([self.m.jnt_dofadr[self.m.joint(n).id]for n in self.names]);self.context=None
  self.side_indices=[np.array([i for i,n in enumerate(self.names)if n.startswith(side+'_')and '_guide_joint'not in n])for side in ['left','right']]
  self.wheel_ids=[self.m.body(side+'_wheel_link').id for side in ['left','right']];self.hips=[];self.bodies=[];self.wheel_parent_index=[]
  for i,side in enumerate(['left','right']):
   self.hips.append(self.d.xanchor[self.m.joint(side+'_rear1_joint').id].copy())
   bodies=[b for b in range(1,self.m.nbody)if self.m.body(b).name.startswith(side+'_')and '_guide_'not in self.m.body(b).name and b!=self.wheel_ids[i]]+[self.wheel_ids[i]]
   self.bodies.append(bodies);self.wheel_parent_index.append(bodies.index(int(self.m.body_parentid[self.wheel_ids[i]])))
  used=set(self.bodies[0]+self.bodies[1]);self.chassis=[i for i in range(1,self.m.nbody)if i not in used];self.dy=np.array([self.d.xanchor[self.m.joint(s+'_wheel_joint').id,1]for s in ['left','right']]);self.cache={}
 def set_context(self,m,d):self.context=(m,d)
 @functools.lru_cache(maxsize=16384)
 def configuration(self,side,front,back):
  values,_=KIN.leg_configuration(front,back,side=side,check_limits=False);semantic=np.zeros(len(API.names))
  for j,n in enumerate(API.names):
   if n in values:semantic[j]=values[n]
  return API.native_positions(semantic)
 @functools.lru_cache(maxsize=4096)
 def fk(self,side,front,back):
  i=['left','right'].index(side);q=self.configuration(side,float(front),float(back));self.d.qpos[self.qadr[self.side_indices[i]]]=q[self.side_indices[i]];mj.mj_kinematics(self.m,self.d)
  ids=self.bodies[i];p=self.d.xipos[ids][:,[0,2]].copy();R=self.d.xmat[ids].reshape(-1,3,3);angles=-np.arctan2(R[:,0,2],R[:,0,0]);wheel=self.d.xpos[self.wheel_ids[i]][[0,2]].copy();return p,angles,wheel
 def q_jacobian(self,side,front,back):
  eps=1e-6;return np.stack([(self.configuration(side,front+eps,back)-self.configuration(side,front-eps,back))/(2*eps),(self.configuration(side,front,back+eps)-self.configuration(side,front,back-eps))/(2*eps)],axis=1)
 def projected(self,side,front,back,field):
  if self.context is None:return np.zeros(2)
  m,d=self.context;J=self.q_jacobian(side,front,back);return J.T@np.asarray(getattr(d,field))[self.dadr]
 def static_gravity(self,side,front,back,R3):
  i=['left','right'].index(side);mass=self.m.body_mass[self.bodies[i]];eps=1e-5;out=[]
  for delta in [(eps,0.),(0.,eps)]:
   a=self.fk(side,front+delta[0],back+delta[1])[0];b=self.fk(side,front-delta[0],back-delta[1])[0];out.append(9.81*np.sum(mass*((a-b)/(2*eps)@R3[2,[0,2]])))
  return np.asarray(out)
G=NativeGeometry();SIDE_BODY_COUNT=len(G.bodies[0]);assert SIDE_BODY_COUNT==len(G.bodies[1])

class Mod4ClosedChainLeg:
 def __init__(self,side,link_lengths,dt):
  from kinematics import DiscreteDerivative,SecondDerivative
  self.side=side;self.dt=dt;self.length=0.;self.theta=0.;self.theta_body=0.;self.theta_world=0.;self.shank_rate=0.;self._shank_last=None;self.force=0.;self.front_torque=0.;self.back_torque=0.
  self.length_dot=DiscreteDerivative(dt);self.theta_dot=DiscreteDerivative(dt);self.length_ddot=SecondDerivative(dt);self.theta_ddot=SecondDerivative(dt)
 def wheel_position(self,front,back):return G.fk(self.side,float(front),float(back))[2].copy()
 def _forward_raw(self,front,back):
  x,z=self.wheel_position(front,back);return np.array([np.hypot(x,z),-math.atan2(x,-z)])
 def jacobian(self,front,back):
  eps=1e-6;return np.column_stack([(self._forward_raw(front+eps,back)-self._forward_raw(front-eps,back))/(2*eps),(self._forward_raw(front,back+eps)-self._forward_raw(front,back-eps))/(2*eps)])
 def forward(self,front,back,body_pitch):
  self.length,self.theta_body=self._forward_raw(front,back);self.theta=self.theta_world=self.theta_body+body_pitch
  side=['left','right'].index(self.side);angles=G.fk(self.side,float(front),float(back))[1];shank=body_pitch-angles[G.wheel_parent_index[side]]
  if self._shank_last is not None:self.shank_rate=((shank-self._shank_last+np.pi)%(2*np.pi)-np.pi)/self.dt
  self._shank_last=shank;self.length_dot.update(self.length);self.theta_dot.update(self.theta);self.length_ddot.update(self.length);self.theta_ddot.update(self.theta);return self.length,self.theta
 def vmc(self,force,torque,front,back):
  self.force=force;motor=self.jacobian(front,back).T@np.array([force,torque])+G.projected(self.side,front,back,'qfrc_bias');self.front_torque,self.back_torque=motor;return tuple(motor)
 def gas_spring_torque(self,front,back,stiffness,reference_force):return tuple(G.projected(self.side,front,back,'qfrc_passive'))
 def reset_dynamic_state(self):
  self.length_dot.reset();self.theta_dot.reset();self.length_ddot.reset();self.theta_ddot.reset();self._shank_last=None;self.shank_rate=0.;self.front_torque=self.back_torque=self.force=0.

class Mod4MomentumModel:
 def __init__(self,left_leg,right_leg):
  self.free_workspace=json.loads((ROOT/'FREE_WORKSPACE.json').read_text()) if (ROOT/'FREE_WORKSPACE.json').exists() else None;self.minimum_length=.11537519977075085;self.recovery_calibration=getattr(G,'calibration',None);self.legs=(left_leg,right_leg);m=G.m;ids=G.chassis;d=G.d;mj.mj_kinematics(m,d);mass=m.body_mass[ids];self.body_mass=float(mass.sum());self.body_com=np.average(d.xipos[ids],axis=0,weights=mass)
  inertia=0.
  for b in ids:
   Rb=d.ximat[b].reshape(3,3);r=d.xipos[b]-self.body_com;inertia+=(Rb@np.diag(m.body_inertia[b])@Rb.T)[1,1]+m.body_mass[b]*(r[0]**2+r[2]**2)
  self.side_mass=[m.body_mass[x].copy()for x in G.bodies];self.side_inertia=[]
  for bids in G.bodies:
   self.side_inertia.append(np.array([(d.ximat[b].reshape(3,3)@np.diag(m.body_inertia[b])@d.ximat[b].reshape(3,3).T)[1,1]for b in bids]))
  self.mass=np.r_[self.body_mass,*self.side_mass];self.inertia=np.r_[inertia,*self.side_inertia];self.com=np.zeros((len(self.mass),2));self.com[0]=self.body_com[[0,2]];self.wheel_indices=np.array([SIDE_BODY_COUNT,2*SIDE_BODY_COUNT]);self.wheel_parent_index=G.wheel_parent_index;self.slices=[slice(1,1+SIDE_BODY_COUNT),slice(1+SIDE_BODY_COUNT,1+2*SIDE_BODY_COUNT)];self._kinematics_cache=[None,None]
 def minimum_static_length(self,theta,pitch):
  if self.free_workspace is None:return self.minimum_length
  w=self.free_workspace;values=[np.interp(theta,w['body_theta_rad'],row)for row in w['minimum_static_free_length_m']]
  return float(np.interp(pitch,w['pitch_rad'],values))
 def pose(self,side,front,back):return tuple(x.copy()for x in G.fk(['left','right'][side],float(front),float(back)))
 def leg_kinematics(self,side,q):
  key=tuple(q);cached=self._kinematics_cache[side]
  if cached is not None and cached[0]==key:return cached[1]
  p,angles,wheel=self.pose(side,*q);Jp=[];Ja=[]
  for delta in [np.array([1e-5,0.]),np.array([0.,1e-5])]:
   a,aa,_=self.pose(side,*(q+delta));b,ab,_=self.pose(side,*(q-delta));Jp.append((a-b)/2e-5);Ja.append(((aa-ab+np.pi)%(2*np.pi)-np.pi)/2e-5)
  result=(p,wheel,np.asarray(Jp),np.asarray(Ja));self._kinematics_cache[side]=(key,result);return result
 def evaluate(self,state):
  phi=state['euler'][1];rate=state['gyro'][1];co,si=np.cos(phi),np.sin(phi);R2=np.array([[co,si],[-si,co]])
  positions=[R2@self.com[0]];velocities=[np.array([positions[0][1],-positions[0][0]])*rate];angular=[rate];wheels=[]
  for i,side in enumerate(['left','right']):
   q=np.array([state[side+'_front_pos'],state[side+'_back_pos']]);qd=np.array([state[side+'_front_vel'],state[side+'_back_vel']]);p,w,Jp,Ja=self.leg_kinematics(i,q)
   v=np.einsum('i,ijk->jk',qd,Jp);ad=qd@Ja;p=p@R2.T;v=v@R2.T+np.column_stack((p[:,1],-p[:,0]))*rate;omega=rate-ad;omega[-1]=rate-ad[self.wheel_parent_index[i]]+state[side+'_wheel_vel'];positions.extend(p);velocities.extend(v);angular.extend(omega);wheels.append(R2@w)
  positions=np.asarray(positions);velocities=np.asarray(velocities);center=np.average(positions,axis=0,weights=self.mass);speed=np.average(velocities,axis=0,weights=self.mass);self.last_com_velocity=speed.copy();r=positions-center;v=velocities-speed
  H=np.sum(self.inertia*np.asarray(angular)+self.mass*(r[:,1]*v[:,0]-r[:,0]*v[:,1]));return float(H),center,np.mean(wheels,axis=0)

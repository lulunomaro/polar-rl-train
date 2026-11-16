"""Local matched MOD4 teacher/student experiments. No remote PPO or default adoption."""
from pathlib import Path
import sys,json,math,time,hashlib,xml.etree.ElementTree as ET
import numpy as np,torch,mujoco as mj
from mod4_retarget import Mod4Retarget,PLANT,PIN,T,R,PPO_ORDER
D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';E=T/'distill_r1'
sys.path.insert(0,str(D/'runtime/core'))
from args_for import args_for
from play_ppo_flatv1_control import Simulation
from play_ppo_flatv1 import ActorMLP
BASE=R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt'
BASE_SHA='c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA
torch.set_num_threads(1)

def actor_from(path):
 ck=torch.load(path,map_location='cpu',weights_only=False);p=ActorMLP();p.load_state_dict(ck['actor_state_dict'],strict=False);p.eval();return p

class Env:
 def __init__(self,height,output,start_x=0.):
  self.height=height;original=PLANT/'mjcf/scene.xml';assert hashlib.sha256(original.read_bytes()).hexdigest()==PIN
  tree=ET.parse(original);root=tree.getroot();root.find('compiler').set('meshdir',str(original.parent/'assets'))
  if height:ET.SubElement(root.find('worldbody'),'geom',name='skill_platform',type='box',pos=f'2.1 0 {height/2}',size=f'.9 1.1 {height/2}',contype='1',conaffinity='2',friction='.9 .005 .0001')
  output.mkdir(parents=True,exist_ok=True);self.xml=output/'scene.xml';tree.write(self.xml,encoding='utf8',xml_declaration=True)
  args=args_for(str(BASE));args.xml=str(self.xml);self.sim=Simulation(args);self.e=self.sim.env;self.m=self.e.m;self.d=self.e.d
  self.m.opt.timestep=.0025;self.d.qpos[0]+=start_x;mj.mj_forward(self.m,self.d)
  self.tire=[self.m.geom(n).id for n in ['left_tire','right_tire']];self.wb=[int(self.m.geom_bodyid[g])for g in self.tire]
  self.hips=[self.m.joint(s+'_rear1_joint').id for s in ['left','right']]
  self.platform=mj.mj_name2id(self.m,mj.mjtObj.mjOBJ_GEOM,'skill_platform')
  self.pairs=[(self.m.site(x.get('site1')).id,self.m.site(x.get('site2')).id)for x in root.findall('equality/connect')]
  self.maxclosure=0.;self.tau_peak=np.zeros(6);self.last=np.zeros(6,np.float32);self.teacher_calls=0
  self.qa=np.array([self.m.jnt_qposadr[self.m.joint(n).id]for n in PPO_ORDER]);self.va=np.array([self.m.jnt_dofadr[self.m.joint(n).id]for n in PPO_ORDER])
  self.default=self.sim.default_active.numpy()
 def obs(self,v,height,kind='normal',target=0.,clock=0.,wz=0.):
  q=self.d.qpos[self.qa]-self.default;q=q.copy();q[4:]=0.;qd=self.d.qvel[self.va];rot=self.d.xmat[self.e.base_id].reshape(3,3)
  mode=np.zeros(7);mode[{'normal':0,'stair':1,'jump':4}[kind]]=1.
  if kind in ['stair','jump']:mode[5:]=[target*5.,min(clock,1.5)if kind=='jump'else 0.]
  return np.r_[[v,0.,wz,height*5.],self.d.qvel[3:6]*.5,rot.T@np.array([0.,0.,-1.]),q,qd*.1,self.last,mode].astype(np.float32)
 def infer(self,actor,obs):
  with torch.no_grad():return actor(torch.from_numpy(obs).reshape(1,35))[0].clamp(-6.,6.).numpy().copy()
 def step(self,action):
  action=np.clip(action,-6.,6.).astype(np.float32);a=torch.from_numpy(action).reshape(1,6)[:,self.sim.ppo_to_env]
  for j in range(8):
   tau=self.e._torque(a).numpy().reshape(-1)
   if j%4==0:self.d.ctrl[self.e.act_ids[:4]]=tau[:4]
   self.d.ctrl[self.e.act_ids[4:]]=tau[4:];mj.mj_step(self.m,self.d)
   self.tau_peak=np.maximum(self.tau_peak,np.abs(self.d.ctrl[self.e.act_ids]))
   if not np.isfinite(self.d.qpos).all()or not np.isfinite(self.d.qvel).all():raise RuntimeError('nonfinite')
   closure=max(np.linalg.norm(self.d.site_xpos[u]-self.d.site_xpos[v])for u,v in self.pairs);self.maxclosure=max(self.maxclosure,float(closure))
   if closure>1.:raise RuntimeError('catastrophic separation>1m')
  self.last=action.copy();self.sim.a_prev=torch.from_numpy(action).reshape(1,6)
 def task(self):
  rot=self.d.xmat[self.e.base_id].reshape(3,3);v=(self.d.xpos[self.wb]-np.stack([self.d.xanchor[j]for j in self.hips]))@rot
  return np.r_[np.linalg.norm(v,axis=1),np.arctan2(v[:,0],-v[:,2])]
 def contacts(self):
  ground=np.zeros(2,bool);top=np.zeros(2,bool);edge=np.zeros(2,bool);guide_force=0.
  for ci,c in enumerate(self.d.contact):
   g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(self.m.geom_bodyid[g1]),int(self.m.geom_bodyid[g2]);f=np.zeros(6);mj.mj_contactForce(self.m,self.d,ci,f)
   for side,body in enumerate(self.wb):
    other=g1 if b2==body and b1==0 else g2 if b1==body and b2==0 else -1
    if other<0:continue
    normal=(1 if b2==body else -1)*np.asarray(c.frame).reshape(3,3)[0]
    if f[0]>5 and normal[2]>.7:
     ground[side]=True
     if other==self.platform and abs(float(c.pos[2])-self.height)<.012:top[side]=True
    if other==self.platform and f[0]>5:edge[side]=True
   if self.platform in [g1,g2]:
    other=g2 if g1==self.platform else g1
    if 'guide' in self.m.geom(other).name:guide_force+=f[0]
  return ground,top,edge,guide_force
 def pose(self):
  rot=self.d.xmat[self.e.base_id].reshape(3,3);return np.array([math.asin(float(np.clip(-rot[2,0],-1,1))),math.atan2(rot[2,1],rot[2,2]),math.atan2(rot[1,0],rot[0,0])])
 def close(self):self.sim.close()

class SourceReference:
 def __init__(self,case):
  if case['kind']=='jump':
   root=T/'source_demonstrations';key='flat_jump'
  else:
   root=E/'source_bank';key=f"step{round(case['height']*100):02d}_v{round(case['speed']*100):02d}"
  meta=json.loads((root/'RESULT.json').read_text());data=np.load(root/'trajectories.npz');self.col={n:i for i,n in enumerate(meta['columns'])}
  info=next(x for x in meta['rows']if x['case']==key)
  if not info['success']:
   candidates=[x for x in meta['rows']if x['success']and abs(x['height_m']-case['height'])<1e-8]
   assert candidates,f'no qualified source for {key}'
   info=min(candidates,key=lambda x:abs(x['command_speed']-case['speed']));key=info['case']
  self.source_key=key
  source=data[key];phases=info['phases'];self.phases=phases
  if case['kind']=='jump':t0=float(source[np.isin(source[:,-1],[v for k,v in phases.items()if k!='idle|idle']),0].min())-.10
  else:t0=float(source[source[:,self.col['wheel_xyz_0']]>=1.125,0].min())
  mask=source[:,0]>=t0;self.rows=source[mask];self.time=self.rows[:,0]-self.rows[0,0];self.duration=float(self.time[-1])
  self.generalized=data[key+'_task_force'][mask].copy()if key+'_task_force'in data else None
  if self.generalized is not None:self.generalized[:,:,1]*=-1
  source_path=Path(json.loads((T/'PLAN.json').read_text())['teacher_repository'])/'mjcf/bigeye_flat.xml'
  sm=mj.MjModel.from_xml_path(str(source_path));sd=mj.MjData(sm);mj.mj_forward(sm,sd);base=sm.body('base').id
  anchor=np.stack([sd.xanchor[sm.joint(s+'_rear_hip_joint').id]-sd.xpos[base]for s in ['left','right']]);self.mass=float(sm.body_mass.sum());tasks=[]
  for row in self.rows:
   rot=np.zeros(9);mj.mju_quat2Mat(rot,row[4:8]);rot=rot.reshape(3,3);wheel=row[[self.col[f'wheel_xyz_{j}']for j in range(6)]].reshape(2,3)
   v=(wheel-row[1:4])@rot-anchor;tasks.append(np.r_[np.linalg.norm(v,axis=1),np.arctan2(v[:,0],-v[:,2])])
  self.task=np.asarray(tasks)

class SkillTeacher:
 def __init__(self,env,case,variant):
  self.env=env;self.case=case;self.variant=variant;self.ref=SourceReference(case);self.started=None;self.phase=0.;self.elapsed=0.;self.eq=None;self.last_script=None;self.end_age=None
 def start(self,age,action):
  e=self.env;r=self.ref;ik=Mod4Retarget();ik.d.qpos[ik.qadr]=e.d.qpos[ik.qadr];ik.q=e.d.qpos[ik.qadr].copy();base=e.task();mass=float(e.m.body_mass.sum())/r.mass
  self.started=age;self.eq=action[:4].copy();qs=[];forces=[];dtheta=[];baseline=None;self.maxfit=0.
  baseline_ground=np.median(r.rows[:4,[r.col['left_force_z'],r.col['right_force_z']]],axis=0)
  for i,target in enumerate(r.task):
   length=np.clip(base[:2]+target[:2]-r.task[0,:2],.13,.38);theta=base[2:]+target[2:]-r.task[0,2:]
   q0=ik.fit(length,theta);q=q0['active_q'];self.maxfit=max(self.maxfit,q0['target_error_m']);qs.append(q)
   qL=ik.fit(length+.0005,theta)['active_q'];qT=ik.fit(length,theta+.0005)['active_q'];ik.fit(length,theta);dtheta.append((qT-q)/.0005)
   force=np.zeros(4)
   for side in range(2):
    ids=slice(2*side,2*side+2);dq=np.column_stack(((qL[ids]-q[ids])/.0005,(qT[ids]-q[ids])/.0005));J=np.linalg.pinv(dq)
    if r.generalized is not None:force[ids]=J.T@(r.generalized[i,side]*mass)
    else:
     phase_name=next(k for k,v in r.phases.items()if v==int(r.rows[i,-1]));F=max(0,r.rows[i,r.col[['left_force_z','right_force_z'][side]]]-baseline_ground[side])*mass
     if 'thrust'in phase_name:force[ids]=J[0]*F*(self.case.get('target',.10)/.10)
   if r.generalized is not None:
    if baseline is None:baseline=force.copy()
    force-=baseline
   forces.append(force/30.)
  self.q=np.asarray(qs);self.ff=np.asarray(forces);self.dtheta=np.asarray(dtheta)
 def act(self,age,public_height,normal_actor):
  e=self.env;ground,top,edge,guide=e.contacts();r=self.ref;v=self.case['speed']if age>=2 else 0.
  yaw=e.pose()[2];wz=np.clip(-self.variant.get('yaw',0.)*yaw-.3*self.variant.get('yaw',0.)*e.d.qvel[5],-1.5,1.5)
  internal_v=np.clip(v+self.variant.get('speed_feedback',0.)*(v-e.e.vx),-.3,.8) if age>=2 else 0.
  base_action=e.infer(normal_actor,e.obs(internal_v,public_height,wz=wz))
  trigger=age>=2 and (self.case['kind']=='jump'or(edge.all()if self.variant.get('paired')else edge.any()))
  if self.started is None and trigger:self.start(age,base_action)
  if self.started is None:return base_action,False,0.,public_height
  elapsed=age-self.started;phase=self.phase if self.variant.get('warp')else elapsed
  blend=self.variant.get('blend',0.);capture=.24 if self.case['kind']=='stair' else public_height
  if phase>r.duration:
   if self.variant.get('warp'):self.phase+=.02
   f=min(1.,(phase-r.duration)/max(.0001,blend)) if blend else 1.
   h=public_height+(capture-public_height)*f
   action=e.infer(normal_actor,e.obs(internal_v,h,wz=wz))
   if blend and elapsed-self.end_age<blend and self.last_script is not None:
    weight=np.clip((elapsed-self.end_age)/blend,0,1);action[:4]=(1-weight)*self.last_script[:4]+weight*action[:4]
  else:
   h=public_height;action=base_action.copy();q=np.array([np.interp(phase,r.time,self.q[:,j])for j in range(4)]);ff=np.array([np.interp(phase,r.time,self.ff[:,j])for j in range(4)])
   if self.variant.get('feedback'):
    pitch=e.pose()[0];corr=np.clip(self.variant['feedback']*pitch+.025*e.d.qvel[4],-.18,.18);dq=np.array([np.interp(phase,r.time,self.dtheta[:,j])for j in range(4)]);q+=dq*corr
   action[:4]=self.eq+(q-self.q[0])/.5+ff;self.last_script=action.copy();self.end_age=elapsed
   if self.variant.get('warp'):
    err=np.max(abs(e.d.qpos[e.qa[:4]]-q));rate=np.clip(1.-.5*max(0,err-.15),.35,1.15);self.phase+=.02*rate
  e.teacher_calls+=1
  return np.clip(action,-6,6),phase<=r.duration,phase,h


class CartesianTeacher(SkillTeacher):
 """Source preload followed by actual wheel/guide contact driven Cartesian VMC."""
 def __init__(self,env,case,variant):
  super().__init__(env,case,variant);self.stage='preload';self.stage_age=None;self.cart_ik=None;self.capture_age=None;self.capture_action=None;self.land_hold=0.
 def geometry(self):
  e=self.env;R=e.d.xmat[e.e.base_id].reshape(3,3);forward=R[:2,0];forward=forward/np.linalg.norm(forward);W=np.array([[*forward,0.],[0.,0.,1.]])
  hip=np.stack([e.d.xanchor[j]for j in e.hips]);p=(e.d.xpos[e.wb]-hip)@W.T
  ik=self.cart_ik;ik.q=e.d.qpos[ik.qadr].copy();ik.d.qpos[ik.qadr]=ik.q;task=e.task();L=task[:2];theta=task[2:]
  f0=ik.fit(L,theta);fL=ik.fit(L+.0005,theta);fT=ik.fit(L,theta+.0005);ik.fit(L,theta)
  q=f0['active_q'];qL=fL['active_q'];qT=fT['active_q'];fullL=(fL['qpos'][ik.qadr]-f0['qpos'][ik.qadr])/.0005;fullT=(fT['qpos'][ik.qadr]-f0['qpos'][ik.qadr])/.0005
  jdofs=ik.m.jnt_dofadr[ik.joints];matrices=[];bias=[];passive=[]
  for i,side in enumerate(['left','right']):
   ids=slice(2*i,2*i+2);J=np.linalg.pinv(np.column_stack(((qL[ids]-q[ids])/.0005,(qT[ids]-q[ids])/.0005)))
   a=theta[i];radial=np.sqrt(max(1e-6,L[i]**2-ik.lateral_offset[i]**2));polar=np.array([[np.sin(a)*L[i]/radial,radial*np.cos(a)],[-np.cos(a)*L[i]/radial,radial*np.sin(a)]])
   planar=W@R[:,[0,2]]@polar;C=planar@J;mask=np.array([ik.m.joint(j).name.startswith(side+'_')for j in ik.joints]);Q=np.stack([fullL[mask],fullT[mask]])
   matrices.append((J,planar,C));bias.append(Q@e.d.qfrc_bias[jdofs[mask]]);passive.append(Q@e.d.qfrc_passive[jdofs[mask]])
  return p,matrices,np.asarray(bias),np.asarray(passive)
 def act(self,age,public_height,normal_actor):
  e=self.env;ground,top,edge,guide=e.contacts();r=self.ref;v=self.case['speed']if age>=2 else 0.
  if self.stage=='preload':
   action,active,phase,h=super().act(age,public_height,normal_actor)
   lift_indices=np.where(r.rows[:,-1]!=0)[0];lift_time=float(r.time[lift_indices[0]]) if len(lift_indices) else .38
   if self.started is not None and age-self.started>=lift_time and (guide>self.variant.get('guide_min',10.) or age-self.started>lift_time+.16):
    self.stage='lift';self.stage_age=age;self.cart_ik=Mod4Retarget();R=e.d.xmat[e.e.base_id].reshape(3,3);forward=R[:2,0]/np.linalg.norm(R[:2,0]);hip=np.stack([e.d.xanchor[j]for j in e.hips]);self.lift_x=(e.d.xpos[e.wb]-hip)@np.r_[forward,0.];self.prev_p=None
   else:return action,active,phase,h
  if self.stage=='capture':
   alpha=np.clip((age-self.capture_age)/self.variant.get('blend',.3),0,1);h=public_height+(.24-public_height)*alpha
   action=e.infer(normal_actor,e.obs(v,h));action[:4]=(1-alpha)*self.capture_action[:4]+alpha*action[:4];e.teacher_calls+=1
   return action,False,age-self.started,h
  p,geometry,bias,passive=self.geometry();velocity=np.zeros((2,2))if self.prev_p is None else (p-self.prev_p)/.02;self.prev_p=p.copy()
  wheel=e.d.geom_xpos[e.tire];elapsed=age-self.stage_age
  if self.stage=='lift'and min(wheel[:,2]-.0625-self.case['height'])>.01:self.stage='swing';self.stage_age=age
  if self.stage=='swing'and min(wheel[:,0])>1.265 and max(abs(p[:,0]+.025))<.12:self.stage='plant';self.stage_age=age
  pose=e.pose();R=e.d.xmat[e.e.base_id].reshape(3,3);action=e.infer(normal_actor,e.obs(v,public_height));taus=np.zeros(4)
  for i in range(2):
   hipz=e.d.xanchor[e.hips[i],2];goalx=self.lift_x[i]-.6*max(0,e.e.vx)*min(elapsed,.4) if self.stage=='lift'else -.025
   clearance=.053 if self.stage in ['lift','swing']else -.025;goalz=self.case['height']+.0625+clearance-hipz
   desired_rate=np.clip(18*(np.array([goalx,goalz])-p[i]),[-2.2,-.45],[2.2,self.variant.get('lift_rate',2.8)]);force=np.array([135.,140.])*self.variant.get('cart_gain',1.)*(desired_rate-velocity[i])
   if pose[0]<-.04:force[0]-=30.*e.d.qvel[4]
   J,P,C=geometry[i];taus[2*i:2*i+2]=J.T@(P.T@force+bias[i]-passive[i])
  q=e.d.qpos[e.qa[:4]];qd=e.d.qvel[e.va[:4]];action[:4]=(q-e.default[:4]+taus/60.)/.5
  if self.variant.get('zero_air_wheels')and self.stage in ['lift','swing']:
   action[4:]=e.d.qvel[e.va[4:]]/10.
  self.land_hold=self.land_hold+.02 if top.all()and abs(pose[0])<.30 and abs(e.d.qvel[4])<2. else 0.
  if self.stage=='plant'and self.land_hold>=.04:
   self.stage='capture';self.capture_age=age;self.capture_action=action.copy()
  e.teacher_calls+=1;return np.clip(action,-6,6),True,age-self.started,public_height


def run_case(case,out,policy=None,variant=None):
 start=time.perf_counter();out=Path(out);assert not (out/'RESULT.json').exists();e=Env(case['height'],out,case['x']);normal=e.sim.actor
 teacher=(CartesianTeacher if (variant or {}).get('cartesian')and case['kind']=='stair' else SkillTeacher)(e,case,variant or {})if policy is None and case['kind']!='normal'else None
 xs=[];ys=[];states=[];vels=[];trace=[];phases=[];hold=0.;maxhold=0.;air=False;air_time=0.;bad=0;reason='timeout';first_top=None;entry=None;peak=0.;jump_base=None;maxfit=0.;error=None
 try:
  for k in range(round(case.get('seconds',12)/.02)):
   age=k*.02;v=case['speed']if age>=2 else 0.;H=case.get('stance',.4 if case['kind']=='stair' else .32)
   public_h=.28+(H-.28)*min(age/2,1.) if (variant or {}).get('ramp')else H
   mode=case['kind']if case['kind']!='jump'or age>=2 else 'normal';clock=max(0,age-2);target=case.get('target',case['height']if case['kind']=='stair'else 0.)
   x=e.obs(v,public_h,mode,target,clock)
   if case['kind']=='jump'and jump_base is None and age>=2:jump_base=float(e.d.qpos[2])
   if teacher is not None:action,active,phase,internal_h=teacher.act(age,public_h,normal)
   else:action=e.infer(policy or normal,x);active=False;phase=0.;internal_h=public_h
   xs.append(x);ys.append(action.copy());phases.append([active,phase,internal_h,public_h]);e.step(action)
   pose=e.pose();ground,top,edge,guide=e.contacts();wheel=e.d.geom_xpos[e.tire];speed=float(np.linalg.norm(e.d.qvel[:2]));peak=max(peak,float(e.d.qpos[2]))
   if entry is None and edge.any():entry=speed
   airborne=not ground.any()and np.all(wheel[:,2]>.0825);air|=bool(airborne);air_time+=.02 if airborne else 0.
   physical=bool(top.all()and 1.32<e.d.qpos[0]<2.85)
   if physical and first_top is None:first_top=age
   ready=physical if case['kind']=='stair'else(air and ground.all()and age>2.7)if case['kind']=='jump'else age>5.
   stable=ready and max(abs(pose[:2]))<math.radians(25)and np.linalg.norm(e.d.qvel[3:5])<1.5 and abs(e.d.qvel[2])<.25
   hold=hold+.02 if stable else 0.;maxhold=max(maxhold,hold);bad=bad+1 if max(abs(pose[:2]))>math.radians(40)else 0
   trace.append([age,*e.d.qpos[:3],*pose,*wheel.reshape(-1),*ground,*top,hold,guide,e.maxclosure,speed]);states.append(e.d.qpos.copy());vels.append(e.d.qvel.copy())
   if hold>=.4-1e-8:reason='qualified_stable_landing';break
   if bad>=10:reason='orientation>40deg_0.2s';break
   if np.abs(e.d.qpos[:2]).max()>4.1:reason='boundary';break
 except Exception as ex:reason='error';error=repr(ex)
 finally:
  result=dict(case=case,success=reason=='qualified_stable_landing',reason=reason,error=error,teacher_assisted=teacher is not None,teacher_calls=e.teacher_calls,policy_is_pure_mlp=teacher is None,actor_dim=35,critic_dim=78,actions=6,reference_start_s=teacher.started if teacher else None,source_reference=teacher.ref.source_key if teacher else None,first_top_s=first_top,hold_s=hold,max_hold_s=maxhold,airborne=air,air_time_s=air_time,root_peak_z=peak,jump_root_rise_m=peak-jump_base if jump_base else None,entry_horizontal_speed_m_s=entry,frames=len(trace),wall_seconds=time.perf_counter()-start,max_closure_m=e.maxclosure,max_IK_error_m=getattr(teacher,'maxfit',0.),torque_abs_peak=e.tau_peak.tolist(),variant=variant,optimizer_steps=0,obs_height_matches_public_command=bool(np.allclose(np.asarray(xs)[:,3],np.asarray(phases)[:,3]*5.)))
  np.savez_compressed(out/'rollout.npz',obs=np.asarray(xs),actions=np.asarray(ys),trace=np.asarray(trace),qpos=np.asarray(states),qvel=np.asarray(vels),teacher_phase=np.asarray(phases))
  (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');e.close()
 return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--student');args=p.parse_args()
 plan=json.loads(Path(args.plan).read_text());out=Path(args.out);out.mkdir(parents=True,exist_ok=True);actor=actor_from(args.student)if args.student else None;results=[]
 for i,case in enumerate(plan['cases']):
  folder=out/f'case_{i:03d}'
  if (folder/'RESULT.json').exists():r=json.loads((folder/'RESULT.json').read_text())
  else:r=run_case(case,folder,actor,plan.get('variant',{}))
  results.append(r);(out/'PROGRESS.json').write_text(json.dumps(dict(completed=len(results),passed=sum(x['success']for x in results),rows=results),indent=2)+'\n');print(json.dumps(dict(index=i,success=r['success'],case=case,reason=r['reason'],first_top=r['first_top_s'],hold=r['max_hold_s'],entry=r['entry_horizontal_speed_m_s'],wall=r['wall_seconds'])),flush=True)
 (out/'RESULT.json').write_text(json.dumps(dict(rows=results,passed=sum(x['success']for x in results),requested=len(results),teacher_assisted=not bool(args.student),student_checkpoint=args.student),indent=2)+'\n')

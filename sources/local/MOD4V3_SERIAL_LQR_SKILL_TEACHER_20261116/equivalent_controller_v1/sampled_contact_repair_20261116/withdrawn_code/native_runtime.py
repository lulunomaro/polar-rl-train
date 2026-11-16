"""Actor-free MOD4 physics bridge, instrumented sensors and exact native PD inverse."""
from pathlib import Path
import sys,json,math,hashlib,ast,argparse,itertools
import xml.etree.ElementTree as ET
import numpy as np,torch,mujoco as mj,yaml
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'sim'),str(ROOT.parent)]
from native_geometry import G,PLANT,R
D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
sys.path.insert(0,str(D/'runtime/core'))
from play_mod4v3 import Mod4v3Mujoco,RobotSpec,_q_from_runtime,_q_from_bank
from mod4_retarget import Mod4Retarget
from controller import StandController
from native_actuation import feasible, inverse
from native_contacts import NativeContacts
# Import order matters: runtime vendor modules must not shadow the source geometry.
PPO_TO_NATIVE=np.array([0,2,1,3,4,5])
NAMES=['left_front1_joint','right_front1_joint','left_rear1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint']
PIN='77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f'
torch.set_num_threads(1)

def source_args():
 tree=ast.parse((ROOT/'sim/main.py').read_text(encoding='utf8'))
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='parse_args')
 fn.body[-1].value.args.append(ast.List(elts=[],ctx=ast.Load()))
 ns={'argparse':argparse};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'source_cli_defaults','exec'),ns)
 args=ns['parse_args']();args.push_body='base_link';args.joint_torque_limit=40.;args.wheel_torque_limit=5.775909774436091
 return args

def model_xml(output,height=0.,edge=1.2):
 original=PLANT/'mjcf/scene.xml';assert hashlib.sha256(original.read_bytes()).hexdigest()==PIN
 tree=ET.parse(original);root=tree.getroot();root.find('compiler').set('meshdir',str(original.parent/'assets'))
 base=root.find(".//body[@name='base_link']");ET.SubElement(base,'site',name='native_teacher_imu',pos='0 0 0',size='.001')
 sensor=root.find('sensor')
 if sensor is None:sensor=ET.SubElement(root,'sensor')
 sensors={}
 for key,tag in [('quat','framequat'),('gyro','gyro'),('accel','accelerometer')]:
  name='native_teacher_'+key;sensors[key]=name
  attrs={'name':name,'objtype':'site','objname':'native_teacher_imu'}if tag=='framequat'else {'name':name,'site':'native_teacher_imu'}
  ET.SubElement(sensor,tag,**attrs)
 for side in ['left','right']:
  for role,joint in [('front','front1_joint'),('back','rear1_joint'),('wheel','wheel_joint')]:
   for suffix,tag in [('pos','jointpos'),('vel','jointvel')]:
    key=side+'_'+role+'_'+suffix;name='native_teacher_'+key;sensors[key]=name
    ET.SubElement(sensor,tag,name=name,joint=side+'_'+joint)
 for side in ['left','right']:
  for role,joint in [('front','front1_joint'),('rear','rear1_joint')]:
   ET.SubElement(sensor,'actuatorfrc',name=side+'_'+role+'_hip_torque',actuator=side+'_'+joint+'_motor')
 if height>0:
  ET.SubElement(root.find('worldbody'),'geom',name='native_teacher_platform',type='box',pos=f'{edge+.9} 0 {height/2}',size=f'.9 1.1 {height/2}',contype='1',conaffinity='2',friction='.9 .005 .0001')
 output.mkdir(parents=True,exist_ok=True);xml=output/'scene.xml';tree.write(xml,encoding='utf8',xml_declaration=True)
 return xml,root,sensors

class NativeTeacher:
 def __init__(self,output,height=0.,start_x=0.,yaw=0.,length=.25,reset_pitch=0.,actuation='native_action'):
  self.output=Path(output);self.height=height;self.actuation=actuation
  xml,root,sensors=model_xml(self.output,height)
  template=json.loads((D/'runtime/core/template_spec.json').read_text(encoding='utf8'));spec=RobotSpec(**template['spec'])
  runtime=json.loads((PLANT/'runtime_config.json').read_text(encoding='utf8'));default=_q_from_runtime(runtime,spec.joint_names)
  bank=json.loads((D/'plant/reset_bank.json').read_text());sem=json.loads((PLANT/'semantics.json').read_text());bq,bz=_q_from_bank(bank,sem,spec.joint_names)
  self.env=Mod4v3Mujoco(str(xml),spec,default,bq,bz,action_clip=6.)
  self.m,self.d=self.env.m,self.env.d;self.m.opt.timestep=.0025
  # Static exact closed-chain initial pose, never an executed source trajectory.
  ik=Mod4Retarget();fit=ik.fit(np.sqrt(length**2+ik.lateral_offset**2),0.)
  self.d.qpos[:]=fit['qpos'];self.d.qpos[:3]=[start_x,0.,length+.0625+.001]
  self.d.qpos[3:7]=[math.cos(yaw/2)*math.cos(reset_pitch/2),-math.sin(yaw/2)*math.sin(reset_pitch/2),math.cos(yaw/2)*math.sin(reset_pitch/2),math.sin(yaw/2)*math.cos(reset_pitch/2)]
  self.d.qvel[:]=0.;mj.mj_forward(self.m,self.d);G.set_context(self.m,self.d)
  self.qa=np.array([self.m.jnt_qposadr[self.m.joint(n).id]for n in NAMES]);self.va=np.array([self.m.jnt_dofadr[self.m.joint(n).id]for n in NAMES]);self.default=self.env.default_q[self.env.leg_ids].numpy().copy()
  self.tire=np.array([self.m.geom(s+'_tire').id for s in ['left','right']]);self.wheels=np.array([self.m.geom_bodyid[g]for g in self.tire]);self.platform=mj.mj_name2id(self.m,mj.mjtObj.mjOBJ_GEOM,'native_teacher_platform')
  self.pairs=[(self.m.site(x.get('site1')).id,self.m.site(x.get('site2')).id)for x in root.findall('equality/connect')]
  self.closure_peak=0.;self.bad=False
  cfg=yaml.safe_load((ROOT/'config/robot_params.yaml').read_text());cfg['mujoco']['sensors']=sensors
  # Recovery geometry is also used by the source StepClimb observer.
  points=[]
  for g in range(self.m.ngeom):
   if self.m.geom_bodyid[g] not in G.chassis or not self.m.geom_contype[g]:continue
   base_R=self.d.xmat[self.env.base_id].reshape(3,3);center=base_R.T@(self.d.geom_xpos[g]-self.d.xpos[self.env.base_id]);mat=base_R.T@self.d.geom_xmat[g].reshape(3,3)
   if self.m.geom_type[g]==mj.mjtGeom.mjGEOM_BOX:ext=self.m.geom_size[g]
   elif self.m.geom_type[g]==mj.mjtGeom.mjGEOM_CYLINDER:ext=self.m.geom_size[g][[0,0,1]]
   else:ext=np.repeat(self.m.geom_rbound[g],3)
   points.extend(center+np.asarray(list(itertools.product([-1,1],repeat=3)))*ext@mat.T)
  calibration=dict(base_support_points_m=np.asarray(points).tolist(),hip_positions_m=np.asarray(G.hips).tolist(),wheel_lateral_offsets_m=G.dy.tolist(),source='native compiled collision bounds; no source dimensions')
  G.calibration=calibration
  (self.output/'RECOVERY_GEOMETRY.json').write_text(json.dumps(calibration,indent=2)+chr(10))
  args=source_args();args.target_leg_length=length;self.controller=StandController(self.m,self.d,cfg,args);self.controller.native_managed=True
  self.surface_observer=NativeContacts(self.m,self.d,self.env.base_id,self.wheels,[i for i in range(self.m.ngeom)if (self.m.geom(i).name or "").startswith("guide_wheel_")],.0625)
  self.controller.native_contact_observer=self.surface_observer.sample
  # Verify sensor-only instrumentation preserves all physical coefficients.
  fields=['body_mass','body_inertia','body_ipos','body_iquat','body_pos','body_quat','jnt_axis','jnt_pos','jnt_range','jnt_stiffness','dof_damping','dof_armature','eq_data','eq_solref','eq_solimp','actuator_gear','actuator_ctrlrange']
  checks={k:bool(np.array_equal(getattr(self.m,k),getattr(G.m,k)))for k in fields};assert all(checks.values()),checks
  (self.output/'MODEL_CHECK.json').write_text(json.dumps(dict(plant_sha256=PIN,mass_kg=float(self.m.body_mass.sum()),physical_coefficients_unchanged=checks,physics_dt=.0025,leg_hz=100,wheel_hz=400,policy_hz=50,actor_loaded=False,actuation=actuation),indent=2))
 def inverse(self,tau):
  q=self.d.qpos[self.qa];v=self.d.qvel[self.va]
  action=np.r_[(q[:4]-self.default+(tau[:4]+2.*v[:4])/60.)/.5,(v[4:]+tau[4:]/.6)/10.]
  return action
 def contacts(self):
  ground=np.zeros(2,bool);top=np.zeros(2,bool);edge=np.zeros(2,bool);guide=0.
  for i,c in enumerate(self.d.contact):
   g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(self.m.geom_bodyid[g1]),int(self.m.geom_bodyid[g2]);f=np.zeros(6);mj.mj_contactForce(self.m,self.d,i,f)
   for s,b in enumerate(self.wheels):
    other=g1 if b2==b and b1==0 else g2 if b1==b and b2==0 else -1
    if other<0:continue
    normal=(1 if b2==b else -1)*np.asarray(c.frame).reshape(3,3)[0]
    if f[0]>5. and normal[2]>.7:
     ground[s]=True
     if other==self.platform and abs(c.pos[2]-self.height)<.012:top[s]=True
    if other==self.platform and f[0]>5.:edge[s]=True
   if self.platform in (g1,g2):
    other=g2 if g1==self.platform else g1
    if 'guide' in self.m.geom(other).name:guide+=f[0]
  return ground,top,edge,guide
 def step(self,axes):
  G.set_context(self.m,self.d);self.controller.step(axes);desired=self.controller.desired_motor_ctrl.copy();projected,empty=feasible(desired,self.d.qpos[self.qa],self.d.qvel[self.va],self.default);a_raw=self.inverse(projected);a=np.clip(a_raw,-6.,6.).astype(np.float32);a_t=torch.from_numpy(a).reshape(1,6)
  if getattr(self, 'sampled_inverse', None) is not None and self.controller.step_climb.phase in ('lift','swing','plant'):
   a=self.sampled_inverse.solve(a).astype(np.float32);a_t=torch.from_numpy(a).reshape(1,6)
  elif getattr(self, 'sampled_inverse', None) is not None and getattr(self, 'wheel_hold_inverse', False) and any(self.controller.last_state.get('_native_contacts',{}).get('wheel_wall_interval',(False,False))):
   a=self.sampled_inverse.solve_wheels(a,desired).astype(np.float32);a_t=torch.from_numpy(a).reshape(1,6)
  applied=[];first=None
  for j in range(8):
   tau=self.env._torque(a_t).numpy().reshape(-1)
   if self.actuation=='direct_torque':
    # Diagnostic only, retaining original voltage/velocity envelope.
    v=self.d.qvel[self.va];peak=np.r_[[40.]*4,[5.775909774436091]*2];stall=np.r_[[53.333333333333336]*4,[28.18525375641699]*2];nl=np.r_[[16.755160819145562]*4,[55.35573187814664]*2]
    tau=np.clip(desired,np.maximum(-peak,np.minimum(0.,-stall*(1+v/nl))),np.minimum(peak,np.maximum(0.,stall*(1-v/nl))))
   if j%4==0:self.d.ctrl[self.env.act_ids[:4]]=tau[:4]
   self.d.ctrl[self.env.act_ids[4:]]=tau[4:]
   if first is None:first=self.d.ctrl[self.env.act_ids].copy()
   applied.append(self.d.ctrl[self.env.act_ids].copy());mj.mj_step(self.m,self.d);self.surface_observer.observe_substep()
   closure=max(np.linalg.norm(self.d.site_xpos[u]-self.d.site_xpos[v])for u,v in self.pairs);self.closure_peak=max(self.closure_peak,float(closure))
   if not np.isfinite(self.d.qpos).all()or not np.isfinite(self.d.qvel).all():raise RuntimeError('nonfinite')
   if closure>1.:raise RuntimeError('catastrophic separation >1m')
  # Source load/state estimates see actual motor output on the previous interval.
  actual=np.asarray(applied);self.controller.previous_motor_ctrl[:]=actual[-1]
  return dict(requested=desired,feasible_requested=projected,projection_error=projected-desired,empty_feasible_set=empty,action_raw=a_raw,action=a,actual=actual,first_error=first-desired,feasible_first_error=first-projected,interval_error=actual-desired)
 def euler(self):
  mat=self.d.xmat[self.env.base_id].reshape(3,3);return np.array([math.atan2(mat[2,1],mat[2,2]),math.asin(float(np.clip(-mat[2,0],-1,1))),math.atan2(mat[1,0],mat[0,0])])

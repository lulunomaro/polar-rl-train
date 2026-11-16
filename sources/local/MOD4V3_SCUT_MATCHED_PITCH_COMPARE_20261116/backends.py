"""Isolated adapters for frozen native SCUT and MOD4v3 comparison."""
from pathlib import Path
import importlib.util,sys,types,hashlib,json,math,gc
import numpy as np
import torch,mujoco
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent
D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';T=R/'sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116'
MOD4=R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt'
PIN={'mod4':'c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617','scut':'d19492be858ffd431a67e5aa40afb4a4c51dc9a1c914c5c92022ed46d5868db7'}
FAMILIES={'flat':'plane_for_rm','rough':'random_uniform_for_rm'}
torch.set_num_threads(1)
class Adapter:
 def __init__(self,kind,out,materials='native',mu=1.,contact='hard'):
  self.kind=kind;self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True);self.materials=materials;self.mu=float(mu);self.contact=contact
  if kind=='scut':
   sys.path.insert(0,str(R/'sources/local/SCUT_ORIGINAL_MUJOCO_ROUGH_20261115'));import scut_backend
   self.module=scut_backend;self.module.RUNTIME=self.out/'scenes';self.module.RUNTIME.mkdir(exist_ok=True);self.checkpoint=scut_backend.CHECKPOINT
  else:
   spec=importlib.util.spec_from_file_location('matched_pitch_show',D/'viewer/showcase.py');self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
   B=self.out/'scenes';(B/'tiles').mkdir(parents=True,exist_ok=True)
   for level,family in [(9,FAMILIES['rough']),(0,FAMILIES['flat'])]:
    tile=f'r{level:02d}_c{self.module.COLS[family]:02d}'
    (B/'tiles'/(tile+'.npz')).write_bytes((D/'viewer/tiles'/(tile+'.npz')).read_bytes())
    cache=D/'viewer'/(tile+'_hf_v2.npz')
    if cache.exists():(B/cache.name).write_bytes(cache.read_bytes())
   self.module.B=B;self.module.CKPT=MOD4;self.module.EXPECTED=PIN[kind];self.checkpoint=MOD4
   sys.path.insert(0,str(T/'manual_replay'));from replay_supported_guards import replay_step
   self.module.Replay.step=replay_step(self.module.Simulation,self.module.SafetyStop,duration_steps=10,event_dir=self.out/'reset_events')
  assert hashlib.sha256(self.checkpoint.read_bytes()).hexdigest()==PIN[kind]
 def create(self,family,height,direction=1,y0=-.1):
  level=9 if family=='rough'else 0
  self.s=self.module.SCUTReplay(level=level,family=FAMILIES[family],direction='up')if self.kind=='scut'else self.module.Replay(level=level,family=FAMILIES[family],direction='up')
  s=self.s;self.e=s.env;self.m=self.e.m;self.d=self.e.d;self.height=height;self.max_closure=0.;self.failed='';self.steps=0
  self.base=s.base if self.kind=='scut'else self.e.base_id
  if self.kind=='mod4':
   owner=self
   def physics(env,act):
    act=act.clamp(-env.action_clip,env.action_clip)
    for j in range(env.decim):
     tau=env._torque(act).detach().numpy().reshape(-1)
     if j%4==0:env.d.ctrl[env.act_ids[:4]]=tau[:4]
     env.d.ctrl[env.act_ids[4:]]=tau[4:];mujoco.mj_step(env.m,env.d)
     if not np.isfinite(env.d.qpos).all()or not np.isfinite(env.d.qvel).all():raise owner.module.SafetyStop('nonfinite')
     cl=max(float(np.linalg.norm(env.d.site_xpos[u]-env.d.site_xpos[v]))for u,v in s.pairs);s.closure=cl;owner.max_closure=max(owner.max_closure,cl)
     if cl>.002:raise owner.module.SafetyStop('closure>2mm')
    env.a_prev=act.detach().to(env.device);return env.state()
   self.e.step=types.MethodType(physics,self.e)
  original_friction=self.m.geom_friction.copy()
  if self.materials=='uniform1':
   active=(self.m.geom_contype!=0)|(self.m.geom_conaffinity!=0);self.m.geom_friction[active]=[self.mu,.01,.01];self.m.geom_solref[active]=[.02 if self.contact=='soft'else .0012,1.];self.m.geom_solimp[active]=[.9,.95,.001,.5,2.]if self.contact=='soft'else[.99,.999,.0001,.5,2.];self.m.geom_condim[active]=3
  x0=-.8;z0=s.ground(x0,y0)+(0.18483 if self.kind=='scut'else self.e.bank_z)
  self.d.qpos[:3]=[x0,y0,z0];self.d.qpos[3:7]=[1.,0.,0.,0.];self.d.qvel[:]=0.;self.d.time=0.;mujoco.mj_forward(self.m,self.d)
  if self.kind=='scut':s._update_state()
  else:self.e.state()
  s.set_height(height);s.paused=False;s.reason='';self.reset_before=s.reset_count
  ground=self.m.geom('ground').id
  self.control=dict(kind=self.kind,checkpoint_sha256=PIN[self.kind],physics_dt=float(self.m.opt.timestep),policy_dt=.02,leg_feedback_s=.001 if self.kind=='scut'else .01,wheel_feedback_s=.001 if self.kind=='scut'else .0025,geom_count=self.m.ngeom,total_mass_kg=float(self.m.body_mass.sum()),ground_friction=self.m.geom_friction[ground].tolist(),ground_solref=self.m.geom_solref[ground].tolist(),ground_solimp=self.m.geom_solimp[ground].tolist(),ground_condim=int(self.m.geom_condim[ground]),ground_priority=int(self.m.geom_priority[ground]),hfield_sha256=hashlib.sha256(self.m.hfield_data.tobytes()).hexdigest(),hfield_size=self.m.hfield_size.tolist(),hfield_shape=[self.m.hfield_nrow.tolist(),self.m.hfield_ncol.tolist()],hfield_ground_pos=self.m.geom_pos[ground].tolist(),original_friction_unique=np.unique(original_friction,axis=0).tolist(),active_friction_unique=np.unique(self.m.geom_friction[(self.m.geom_contype!=0)|(self.m.geom_conaffinity!=0)],axis=0).tolist(),environment_material_mode=self.materials,contact_profile=self.contact,closure_guard_m=.002,solver=int(self.m.opt.solver),solver_iterations=int(self.m.opt.iterations))
  return self.control
 def measure(self,issued_time,command,stage):
  rotation=np.asarray(self.d.xmat[self.base]).reshape(3,3);g=rotation.T@np.array([0.,0.,-1.]);pitch=math.atan2(g[0],np.linalg.norm(g[1:]));velocity=np.zeros(6);mujoco.mj_objectVelocity(self.m,self.d,mujoco.mjtObj.mjOBJ_BODY,self.base,velocity,1)
  closure=float(self.s.closure);self.max_closure=max(self.max_closure,closure)
  h=float(self.d.qpos[2]-self.s.ground(*self.d.qpos[:2]));friction=[]
  for contact in self.d.contact:
   b1,b2=self.m.geom_bodyid[int(contact.geom1)],self.m.geom_bodyid[int(contact.geom2)]
   if (b1==0)!=(b2==0):friction.append(float(contact.friction[0]))
  return [float(self.d.time),issued_time,command,float(self.d.qpos[0]),float(self.d.qpos[1]),float(self.d.qvel[0]),float(self.d.qvel[1]),pitch,float(velocity[1]),h,closure,float(self.s.reset_count-self.reset_before),float(stage),float(len(friction)),min(friction)if friction else math.nan,max(friction)if friction else math.nan]
 def step(self,command,stage):
  issued=self.steps*.02;self.s.args.vx=abs(command);self.s.cmd_vx=command;self.s.cmd_vy=0.;self.s.cmd_wz=0.;self.s.set_height(self.height)
  self.s.step({'w'}if command>0 else{'s'}if command<0 else set());self.steps+=1
  row=self.measure(issued,command,stage)
  if self.s.reset_count!=self.reset_before:self.failed=self.s.reason or'reset'
  if not np.isfinite(self.d.qpos).all()or not np.isfinite(self.d.qvel).all():self.failed='nonfinite'
  return row
 def close(self):
  self.s.close();self.s=None;self.e=None;self.m=None;self.d=None;gc.collect()
COLUMNS=['actual_time_s','issued_time_s','command_vx','world_root_x','world_root_y','world_root_vx','world_root_vy','body_pitch_rad','body_pitch_rate_rad_s','height_above_ground_m','closure_m','resets','stage_0rest_1drive_2brake','external_contact_count','external_friction_min','external_friction_max']

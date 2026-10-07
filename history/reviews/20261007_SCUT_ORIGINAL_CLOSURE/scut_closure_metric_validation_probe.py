"""Frozen original SCUT V14_2 policy and saved parameters, with read-only closure capture."""
from pathlib import Path
import argparse,sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;O=Path('D:/MOD4_async_eval/scut_closure_review_20261007/original')
for folder in ['source/agent_world','source/agent_tasks','source/agent_rl','']:
 sys.path.insert(0,str(O/folder))
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--steps',type=int,default=1500);p.add_argument('--num_envs',type=int,default=32)
AppLauncher.add_app_launcher_args(p);args=p.parse_args();app=AppLauncher(args).app
try:
 import torch,numpy as np,yaml,importlib,types,copy
 from pxr import Usd,UsdPhysics,UsdGeom
 from isaaclab.utils.math import quat_apply
 from isaaclab_physx.physics import PhysxCfg
 from isaaclab.managers import EventTermCfg,SceneEntityCfg
 import agent_tasks.manager.mdp.isaaclab as scut_mdp
 import isaaclab.envs.mdp.events as native_events
 for name in dir(native_events):
  if not name.startswith('_') and not hasattr(scut_mdp,name):setattr(scut_mdp,name,getattr(native_events,name))
 import agent_tasks.manager.mdp.isaaclab.events as scut_events
 from isaaclab_physx.assets import Articulation as PhysxArticulation
 scut_events.Articulation=PhysxArticulation
 from agent_tasks.direct.wheelbipe.wheelbipe_V14.env_cfg import WheelbipeV14FlatEnvCfg
 from agent_tasks.direct.wheelbipe.wheelbipe_V14.env import WheelbipeV14Env
 from agent_tasks.manager.mdp.isaaclab.commands import SpecialModeEntryCfg
 class SavedLoader(yaml.SafeLoader):pass
 SavedLoader.add_constructor('tag:yaml.org,2002:python/tuple',lambda l,n:tuple(l.construct_sequence(n,deep=True)))
 SavedLoader.add_constructor('tag:yaml.org,2002:python/object/apply:builtins.slice',lambda l,n:slice(*l.construct_sequence(n,deep=True)))
 prefix=O/'pretrained/26_infantry/flat_and_rotation/2026-07-29_23-20-03'
 saved=yaml.load((prefix/'params/env.yaml').read_text(encoding='utf8'),Loader=SavedLoader)
 cfg=WheelbipeV14FlatEnvCfg();adapters=[]
 def resolve(s):
  module,name=s.split(':',1)
  assert module.startswith(('isaaclab.','agent_tasks.','agent_world.')),(module,name)
  obj=importlib.import_module(module)
  for part in name.split('.'):obj=getattr(obj,part)
  return obj
 from dataclasses import MISSING
 def merge(old,value,path):
  if isinstance(old,type(MISSING)):old=None
  if isinstance(value,dict):
   if old is None:
    if path.endswith('/ranges') and set(value)=={'lin_vel_x','lin_vel_y','ang_vel_z'}:old=SpecialModeEntryCfg.Ranges(**value)
    elif 'func' in value and 'mode' in value:old=EventTermCfg(func=resolve(value['func']),mode=value['mode'])
    elif 'name' in value and 'body_ids' in value:old=SceneEntityCfg(value['name'])
    else:return {k:merge(None,v,path+'/'+k) for k,v in value.items()}
   if isinstance(old,dict):return {k:merge(old.get(k),v,path+'/'+k) for k,v in value.items()}
   for k,v in value.items():
    if path=='/sim' and k=='physx':
     old.physics=merge(PhysxCfg(),v,path+'/physics');adapters.append({'path':path+'/physx','mapped_to':'/sim/physics'});continue
    prior=getattr(old,k,None)
    if not hasattr(old,k):adapters.append({'path':path+'/'+k,'added_attribute':True})
    setattr(old,k,merge(prior,v,path+'/'+k))
   return old
  if isinstance(value,(list,tuple)):
   if path in ['/robot_cfg/init_state/rot','/dot_scanner/offset/rot']:
    assert len(value)==4
    adapters.append({'path':path,'wxyz_to_xyzw':True})
    return tuple(value[1:])+tuple(value[:1])
   if path=='/commands/special_modes':return tuple(merge(SpecialModeEntryCfg(),v,path+'/'+str(i)) for i,v in enumerate(value))
   return type(value)(merge(None,v,path+'/'+str(i)) for i,v in enumerate(value))
  if isinstance(value,str) and ':' in value and (callable(old) or path.endswith(('/func','/class_type'))):return resolve(value)
  return value
 cfg=merge(cfg,saved,'')
 asset=O/'source/agent_world/agent_world/assets/usd_files/wheelbipeV14_2_1/wheelbipeV14_2.usd'
 cfg.robot_cfg.spawn.usd_path=str(asset);cfg.scene.num_envs=args.num_envs;cfg.terrain.num_envs=args.num_envs;cfg.sim.device='cuda:0';cfg.seed=66
 assert cfg.sim.dt==.005 and cfg.decimation==4
 assert cfg.robot_cfg.spawn.articulation_props.solver_position_iteration_count==12 and cfg.robot_cfg.spawn.articulation_props.solver_velocity_iteration_count==6
 # Visualization-only switches do not change the original plant, task, DR, noise, or delays.
 def hide(x):
  if isinstance(x,dict):
   for k,v in x.items():
    if k=='debug_vis':x[k]=False
    else:hide(v)
  elif hasattr(x,'__dict__'):
   for k,v in vars(x).items():
    if k=='debug_vis':setattr(x,k,False)
    elif k!='class_type' and not callable(v):hide(v)
 hide(cfg)
 source=json.loads((O/'SOURCE_MANIFEST.json').read_text())
 for name,row in source['files'].items():assert hashlib.sha256((O/name).read_bytes()).hexdigest()==row['sha256'],name
 output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
 pre={'phase':'creating_original_environment','commit':source['commit'],'checkpoint':str(prefix/'model_15000.pt'),'config_adapters':adapters,'physics_dt_s':cfg.sim.dt,'decimation':cfg.decimation,'num_envs':args.num_envs,'new_learning':False}
 (output.parent/'READBACK_STARTED.json').write_text(json.dumps(pre,indent=2),encoding='utf8')
 # Use the byte-identical official Isaac 5.1 grid asset locally, avoiding Kit's failed cloud fetch.
 import isaaclab.terrains.terrain_importer as terrain_module
 original_ground_cfg=terrain_module.sim_utils.GroundPlaneCfg
 ground_path=Path('D:/MOD4_async_eval/scut_closure_review_20261007/ground/default_environment.usd')
 assert hashlib.sha256(ground_path.read_bytes()).hexdigest()=='8a21c317d638d33a4e6c20c958a7ed8f4d8c5195efd7e20f1b85178b4a15638a'
 def local_original_ground(**kwargs):return original_ground_cfg(usd_path=str(ground_path),**kwargs)
 terrain_module.sim_utils.GroundPlaneCfg=local_original_ground
 adapters.append({'path':'ground_asset','official_version':'5.1','local_byte_identical':True})
 assert tuple(cfg.robot_cfg.init_state.rot)==(0.,0.,0.,1.)
 from isaaclab.sim import SimulationContext
 from isaacsim.core.version import get_version
 SimulationContext.get_version=staticmethod(lambda: tuple(get_version()[0].split('.')))
 original_asset_initialize=PhysxArticulation._initialize_impl
 def initialize_with_saved_defaults(asset):
  original_asset_initialize(asset)
  asset.data.default_joint_dynamic_friction_coeff=asset.data.joint_dynamic_friction_coeff.torch.clone()
  if not hasattr(asset.data,'default_joint_viscous_friction_coeff'):asset.data.default_joint_viscous_friction_coeff=asset.data.joint_viscous_friction_coeff.torch.clone()
 PhysxArticulation._initialize_impl=initialize_with_saved_defaults
 # TorchScript cannot dispatch ProxyArray. Convert only SCUT call arguments to zero-copy Torch views.
 import isaaclab.utils.math as native_math
 def torch_view(x):
  if hasattr(x,'torch') and type(x).__name__=='ProxyArray':return x.torch
  if type(x).__module__.startswith('warp.') and hasattr(x,'device'):
   import warp as wp
   if isinstance(x,wp.array):return wp.to_torch(x)
  if isinstance(x,tuple):return tuple(torch_view(v) for v in x)
  if isinstance(x,list):return [torch_view(v) for v in x]
  if isinstance(x,dict):return {k:torch_view(v) for k,v in x.items()}
  return x
 def math_adapter(f):
  def adapted(*a,**kw):return torch_view(f(*torch_view(a),**torch_view(kw)))
  return adapted
 adapted_math=types.SimpleNamespace(**{n:math_adapter(v) if callable(v) and not isinstance(v,type) else v for n,v in vars(native_math).items() if not n.startswith('_')})
 for module_name,module in tuple(sys.modules.items()):
  if module_name.startswith('agent_tasks.') and module is not None:
   for name,value in tuple(vars(module).items()):
    if value is native_math:setattr(module,name,adapted_math)
    elif callable(value) and vars(native_math).get(name) is value and not isinstance(value,type):setattr(module,name,getattr(adapted_math,name))
 # Original task code uses Torch operators; route Proxy/Warp inputs through the same native Torch operator.
 adapted_torch=types.SimpleNamespace(**{n:math_adapter(v) if callable(v) and not isinstance(v,type) else v for n,v in vars(torch).items() if not n.startswith('__')})
 for module_name,module in tuple(sys.modules.items()):
  if module_name.startswith('agent_tasks.') and module is not None and getattr(module,'torch',None) is torch:module.torch=adapted_torch
 from agent_tasks.direct.wheelbipe.wheelbipe25_v3.env import Wheelbipe25V3Env
 original_priv=Wheelbipe25V3Env.get_privilaged_obs
 def privileged_as_torch(self):return torch_view(original_priv(self))
 Wheelbipe25V3Env.get_privilaged_obs=privileged_as_torch
 original_base_reset=Wheelbipe25V3Env._reset_idx
 def base_reset_as_torch(self,ids):
  all_ids=self.robot._ALL_INDICES
  self.robot._ALL_INDICES=torch_view(all_ids)
  try:return original_base_reset(self,torch_view(ids))
  finally:self.robot._ALL_INDICES=all_ids
 Wheelbipe25V3Env._reset_idx=base_reset_as_torch
 original_env_ids=Wheelbipe25V3Env._as_env_ids_tensor
 def env_ids_as_torch(self,ids):return torch_view(original_env_ids(self,ids))
 Wheelbipe25V3Env._as_env_ids_tensor=env_ids_as_torch
 env=WheelbipeV14Env(cfg=cfg)
 # Audit class/module identity, and adapt the original instance method result explicitly.
 original_instance_priv=env.get_privilaged_obs
 def instance_priv(self):
  value=original_instance_priv();converted=torch_view(value)
  assert isinstance(converted,torch.Tensor),(type(value),type(converted))
  return converted
 env.get_privilaged_obs=types.MethodType(instance_priv,env)
 (output.parent/'BRIDGE_READBACK.json').write_text(json.dumps({'mro':[str(c) for c in type(env).__mro__],
  'patched_base_is_actual_base':Wheelbipe25V3Env in type(env).__mro__,
  'original_priv_repr':str(original_instance_priv),'original_priv_module':getattr(original_instance_priv,'__module__',None),
  'original_priv_globals_torch_type':str(type(getattr(original_instance_priv,'__globals__',{}).get('torch')))},indent=2),encoding='utf8')
 actual={'body_count':env.robot.num_bodies,'joint_count':env.robot.num_joints,'body_names':env.robot.body_names,'joint_names':env.robot.joint_names,'physics_dt':env.physics_dt,'policy_dt':env.step_dt,
  'use_obs_noise':env.use_self_obs_noise,'use_act_noise':env.use_self_act_noise,'use_obs_delay':env.use_obs_delay,'use_act_delay':env.use_act_delay,
  'cfg_after_platform_adapters':cfg.to_dict()}
 (output.parent/'ACTUAL_PLANT_CONFIG.json').write_text(json.dumps(actual,indent=2,default=str),encoding='utf8')
 state=torch.load(prefix/'model_15000.pt',map_location='cpu',weights_only=False)['model_state_dict']
 model=torch.nn.Sequential(torch.nn.Linear(35,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,32),torch.nn.ELU(),torch.nn.Linear(32,6)).to(env.device)
 model.load_state_dict({k.removeprefix('actor.'):v for k,v in state.items() if k.startswith('actor.')},strict=True);model.eval()
 assert all(torch.isfinite(v).all() for v in model.state_dict().values())
 env.set_training_progress(iteration=15000)
 obs,_=env.reset();obs=torch_view(obs);assert obs['policy'].shape==(args.num_envs,35),obs['policy'].shape
 stage=env.sim.stage;unit=UsdGeom.GetStageMetersPerUnit(stage);assert unit==1.,unit
 roots='/World/envs/env_0/Robot'
 loops=[]
 for prim in Usd.PrimRange(stage.GetPrimAtPath(roots)):
  if not prim.IsA(UsdPhysics.Joint):continue
  joint=UsdPhysics.Joint(prim)
  if not joint.GetExcludeFromArticulationAttr().Get() or not joint.GetJointEnabledAttr().Get():continue
  b0=joint.GetBody0Rel().GetTargets()[0];b1=joint.GetBody1Rel().GetTargets()[0]
  loops.append({'path':str(prim.GetPath()),'type':prim.GetTypeName(),'body0':b0.name,'body1':b1.name,'pos0':list(joint.GetLocalPos0Attr().Get()),'pos1':list(joint.GetLocalPos1Attr().Get())})
 assert len(loops)==6,loops
 from pxr import PhysxSchema
 solver=[];all_loops=[]
 for ei in range(args.num_envs):
  for prim in Usd.PrimRange(stage.GetPrimAtPath('/World/envs/env_'+str(ei)+'/Robot')):
   if prim.HasAPI(PhysxSchema.PhysxArticulationAPI):
    api=PhysxSchema.PhysxArticulationAPI(prim);solver.append({'env':ei,'prim':str(prim.GetPath()),'position':api.GetSolverPositionIterationCountAttr().Get(),'velocity':api.GetSolverVelocityIterationCountAttr().Get()})
   if prim.IsA(UsdPhysics.Joint):
    j=UsdPhysics.Joint(prim)
    if j.GetExcludeFromArticulationAttr().Get() and j.GetJointEnabledAttr().Get():all_loops.append(str(prim.GetPath()))
 assert len(solver)==args.num_envs and all(v['position']==12 and v['velocity']==6 for v in solver),solver
 assert len(all_loops)==args.num_envs*6,len(all_loops)
 (output.parent/'STAGE_CONSTRAINT_READBACK.json').write_text(json.dumps({'solver':solver,'enabled_external_loop_paths':all_loops},indent=2),encoding='utf8')
 names=env.robot.body_names;i0=[names.index(l['body0']) for l in loops];i1=[names.index(l['body1']) for l in loops]
 pos0=torch.tensor([l['pos0'] for l in loops],device=env.device).repeat(args.num_envs,1,1)
 pos1=torch.tensor([l['pos1'] for l in loops],device=env.device).repeat(args.num_envs,1,1)
 validation=[];frames=[];commands=[];actions=[];velocities=[];done_events=[];resets=[];control=0
 original_update=env.scene.update
 def capture(dt):
  original_update(dt)
  assert abs(dt-.005)<1e-9,dt
  pos=env.robot.data.body_link_pos_w;quat=env.robot.data.body_link_quat_w
  a0=pos[:,i0]+quat_apply(quat[:,i0].reshape(-1,4),pos0.reshape(-1,3)).reshape(args.num_envs,6,3)
  a1=pos[:,i1]+quat_apply(quat[:,i1].reshape(-1,4),pos1.reshape(-1,3)).reshape(args.num_envs,6,3)
  error=torch.linalg.vector_norm(a0-a1,dim=-1)
  assert torch.isfinite(error).all()
  # Independent raw PhysX link poses and float64 NumPy quaternion rotation.
  raw_pose=torch_view(env.robot.root_view.get_link_transforms()).detach().cpu().numpy().astype(np.float64)
  dp=pos.detach().cpu().numpy().astype(np.float64);dq=quat.detach().cpu().numpy().astype(np.float64)
  assert raw_pose.shape==(args.num_envs,len(names),7),raw_pose.shape
  pose_diff=float(np.max(np.abs(raw_pose[...,:3]-dp)))
  quat_diff=float(np.max(np.abs(raw_pose[...,3:]-dq)))
  assert pose_diff<1e-6 and quat_diff<1e-6,(pose_diff,quat_diff)
  def anchor(indices,local):
   q=raw_pose[:,indices,3:];v=np.broadcast_to(np.asarray(local,dtype=np.float64),(args.num_envs,6,3));t=2*np.cross(q[...,:3],v)
   return raw_pose[:,indices,:3]+v+q[...,3:4]*t+np.cross(q[...,:3],t)
  reference=np.linalg.norm(anchor(i0,[l['pos0'] for l in loops])-anchor(i1,[l['pos1'] for l in loops]),axis=-1)
  actual=error.detach().cpu().numpy()
  formula_diff=float(np.max(np.abs(reference-actual)))
  assert formula_diff<1e-5,formula_diff
  validation.append([pose_diff,quat_diff,formula_diff])
  frames.append(actual)
 env.scene.update=capture
 original_reset=env._reset_idx
 def record_reset(ids):
  if ids is not None and len(ids):resets.append({'control':control,'physics_frames_before_reset':len(frames),'envs':ids.detach().cpu().tolist()})
  return original_reset(ids)
 env._reset_idx=record_reset
 start=time.time()
 for control in range(args.steps):
  with torch.inference_mode():action=model(obs['policy'])
  actions.append(action.detach().cpu().numpy());commands.append(env.command.detach().cpu().numpy());velocities.append(env.robot.data.root_ang_vel_b.detach().cpu().numpy())
  obs,reward,terminated,truncated,extras=env.step(action)
  obs=torch_view(obs);terminated=torch_view(terminated);truncated=torch_view(truncated)
  if terminated.any() or truncated.any():done_events.append({'control':control,'terminated':terminated.nonzero().flatten().cpu().tolist(),'timeout':truncated.nonzero().flatten().cpu().tolist()})
  if control%100==0:
   (output.parent/'PROGRESS.json').write_text(json.dumps({'control_steps_completed':control+1,'physics_frames':len(frames),'max_closure_mm':float(np.max(frames))*1000,'wall_seconds':time.time()-start}),encoding='utf8')
 e=np.stack(frames);assert e.shape==(args.steps*4,args.num_envs,6)
 above=e>.002;longest=0
 # Reset boundaries break persistence: count separately per episode and loop.
 reset_at={}
 for r in resets:reset_at.setdefault(r['physics_frames_before_reset'],[]).extend(r['envs'])
 run=np.zeros((args.num_envs,6),dtype=np.int64)
 for tick,b in enumerate(above):
  for row in reset_at.get(tick,[]):run[row]=0
  run=np.where(b,run+1,0);longest=max(longest,int(run.max()))
 raw=output.with_suffix('.npz');np.savez_compressed(raw,closure_m=e,commands=np.stack(commands),actions=np.stack(actions),root_omega_body=np.stack(velocities))
 result={**pre,'phase':'completed','measurement_validation':{'method':'Raw PhysX link transforms plus independent float64 NumPy quaternion rotation','physics_frames':len(validation),'max_pose_difference_m':max(v[0] for v in validation),'max_quaternion_component_difference':max(v[1] for v in validation),'max_anchor_distance_difference_m':max(v[2] for v in validation)},'policy_sha256':hashlib.sha256((prefix/'model_15000.pt').read_bytes()).hexdigest(),'saved_env_sha256':hashlib.sha256((prefix/'params/env.yaml').read_bytes()).hexdigest(),'USD_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
  'engine_scope':'Original SCUT source/model/parameters on current Isaac Sim 6.0.1 and Isaac Lab 6.1.14; not an exact reproduction of their original engine build.',
  'actual_steps':args.steps,'physics_frames':len(frames),'simulated_seconds':args.steps*.02,'wall_seconds':time.time()-start,'loop_joints':loops,
  'max_closure_mm':float(e.max())*1000,'rms_closure_mm':float(np.sqrt(np.mean(e**2)))*1000,'percentile_mm':{str(q):float(np.percentile(e,q))*1000 for q in [50,95,99,99.9]},
  'per_joint_max_mm':(e.max(axis=(0,1))*1000).tolist(),'samples_over_2mm':int(above.sum()),'total_samples':int(e.size),'longest_contiguous_over_2mm_seconds':longest*.005,
  'termination_events':done_events,'resets':resets,'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'closure_termination_added':False,
  'observed_command_min':np.stack(commands).min(axis=(0,1)).tolist(),'observed_command_max':np.stack(commands).max(axis=(0,1)).tolist(),'max_abs_action':float(np.abs(np.stack(actions)).max()),'original_loop_joints_enabled':True}
 output.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
 env.close()
except Exception:
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.with_suffix('.error.txt').write_text(traceback.format_exc(),encoding='utf8');raise
finally:app.close()

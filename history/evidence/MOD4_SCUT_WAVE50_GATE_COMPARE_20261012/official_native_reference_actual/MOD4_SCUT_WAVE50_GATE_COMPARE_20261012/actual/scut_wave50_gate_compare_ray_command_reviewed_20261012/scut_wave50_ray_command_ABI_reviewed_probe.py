"""Frozen original SCUT V14_2 policy and saved parameters, with read-only closure capture."""
from pathlib import Path
import argparse,sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;O=Path('D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012/original')
for folder in ['source/agent_world','source/agent_tasks','source/agent_rl','']:
 sys.path.insert(0,str(O/folder))
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--model_name',required=True,choices=['2026-07-23_16-23-21','2026-07-30_09-16-27']);p.add_argument('--steps',type=int,default=750);p.add_argument('--num_envs',type=int,default=80)
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
 from agent_tasks.direct.wheelbipe.wheelbipe_V14.env_cfg import WheelbipeV14RoughEnvCfg
 from agent_tasks.direct.wheelbipe.wheelbipe_V14.env import WheelbipeV14Env
 from agent_tasks.manager.mdp.isaaclab.commands import SpecialModeEntryCfg
 class SavedLoader(yaml.SafeLoader):pass
 SavedLoader.add_constructor('tag:yaml.org,2002:python/tuple',lambda l,n:tuple(l.construct_sequence(n,deep=True)))
 SavedLoader.add_constructor('tag:yaml.org,2002:python/object/apply:builtins.slice',lambda l,n:slice(*l.construct_sequence(n,deep=True)))
 prefix=O/'pretrained/26_infantry/rough_rotation_stair'/args.model_name
 saved=yaml.load((prefix/'params/env.yaml').read_text(encoding='utf8'),Loader=SavedLoader)
 cfg=WheelbipeV14RoughEnvCfg();adapters=[]
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
   if path=='/robot_cfg/init_state/rot' or path.endswith('/offset/rot'):
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
 pre={'phase':'creating_original_environment','commit':source['commit'],'checkpoint':str(prefix/'model_1000.pt'),'config_adapters':adapters,'physics_dt_s':cfg.sim.dt,'decimation':cfg.decimation,'num_envs':args.num_envs,'new_learning':False}
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
 # Original native SCUT plant/DR/observation/actor; only the frozen test terrain,
 # start pose and manual velocity command are fixtures matching MOD4's route test.
 from isaaclab.terrains import TerrainImporterCfg
 fixture=json.loads((D/'FIXTURE.json').read_bytes());assert args.num_envs==80 and args.steps==750
 cfg.terrain=TerrainImporterCfg(prim_path='/World/ground',terrain_type='usd',usd_path=str(D/fixture['mesh_file']),num_envs=80,env_spacing=9.,collision_group=-1,physics_material=cfg.terrain.physics_material,debug_vis=False)
 cfg.seed=fixture['seed'];cfg.scene.env_spacing=9.
 centers=torch.tensor(fixture['centers'],device='cuda:0',dtype=torch.float32)
 starts=torch.tensor(fixture['starts'],device='cuda:0',dtype=torch.float32)
 groups=torch.arange(80,device='cuda:0')%3
 targets=torch.tensor([.3,-.3,0.],device='cuda:0')[groups]
 env=WheelbipeV14Env(cfg=cfg)
 original_instance_priv=env.get_privilaged_obs
 def instance_priv(self):return torch_view(original_instance_priv())
 env.get_privilaged_obs=types.MethodType(instance_priv,env)
 assert abs(env.physics_dt-.005)<1e-10 and abs(env.step_dt-.02)<1e-10
 env.terrain.env_origins[:,:2]=starts
 with np.load(Path('D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012/actual_mod4_wave50_query.npz'),allow_pickle=False) as z:initial_ground=z['expected_actual_ground'][:,17].copy()
 env.terrain.env_origins[:,2]=torch.tensor(initial_ground,device=env.device)* (groups==2)
 original_compute=env.command_generator.compute
 def manual():
  if hasattr(env.command_generator,'special_mode_id'):env.command_generator.special_mode_id[:]=-1
  env.command_generator.command[:]=0.;env.command_generator.command[:,0]=targets
  env.command[:]=env.command_generator.command
  for name,value in (('is_standing_env',groups==2),('is_heading_env',torch.zeros(80,device=env.device,dtype=torch.bool))):
   if hasattr(env.command_generator,name):getattr(env.command_generator,name)[:]=value
 def manual_compute(dt):original_compute(dt);manual()
 env.command_generator.compute=manual_compute
 original_reset=env._reset_idx;episodes=np.zeros(80,dtype=np.int64);resets=[];control=-1
 def fixture_reset(ids):
  ids=env.robot._ALL_INDICES if ids is None else ids;ids=torch_view(ids)
  original_reset(ids)
  state=torch_view(env.robot.data.root_state_w)[ids].clone();state[:,:2]=starts[ids];state[:,3:7]=torch.tensor([0.,0.,0.,1.],device=env.device);state[:,7:13]=0.
  env.robot.write_root_pose_to_sim(state[:,:7],env_ids=ids);env.robot.write_root_velocity_to_sim(state[:,7:13],env_ids=ids)
  env._record_reset_heading_target(ids);env._sync_heading_command_target_to_reset_heading(ids)
  manual();resets.append(dict(control=int(control),envs=ids.cpu().tolist()))
 env._reset_idx=fixture_reset
 agent=yaml.safe_load((prefix/'params/agent.yaml').read_text(encoding='utf8'));assert agent['policy']['activation']=='elu' and not agent['empirical_normalization']
 state=torch.load(prefix/'model_1000.pt',map_location='cpu',weights_only=False);weights=state['model_state_dict'];layers=[];dims=[35,*agent['policy']['actor_hidden_dims'],6]
 for i,(a,b) in enumerate(zip(dims,dims[1:])):
  layers.append(torch.nn.Linear(a,b))
  if i<len(dims)-2:layers.append(torch.nn.ELU())
 model=torch.nn.Sequential(*layers).to(env.device);model.load_state_dict({k.removeprefix('actor.'):v for k,v in weights.items() if k.startswith('actor.')},strict=True);model.eval()
 model_sha=hashlib.sha256((prefix/'model_1000.pt').read_bytes()).hexdigest();actor_initial={k:v.clone() for k,v in model.state_dict().items()}
 env.set_training_progress(iteration=int(state['iter']));obs,_=env.reset();obs=torch_view(obs)
 assert obs['policy'].shape==(80,35) and torch.allclose(torch_view(env.robot.data.root_pos_w)[:,:2],starts,atol=1e-6,rtol=0)
 # This new scope requires the actual original height sensor to point down.
 scanner_receipts={}
 for name in ('height_scanner','right_wheel_height_scanner','left_wheel_height_scanner'):
  sensor=getattr(env,name,None)
  if sensor is None:continue
  dirs=torch_view(sensor.ray_directions);hit=torch_view(sensor.data.ray_hits_w)
  assert torch.all(dirs[...,2]<-.999999) and torch.isfinite(hit).all(), ('original_SCUT_sensor_direction_hit',name)
  scanner_receipts[name]=dict(local_direction=dirs.cpu().tolist(),initial_hit=hit.cpu().tolist(),config_offset=list(sensor.cfg.offset.rot),all_downward_and_all_hits_finite=True)
 (output.parent/'ORIGINAL_HEIGHT_SENSOR_GPU_ABI_VERIFIED.json').write_text(json.dumps(scanner_receipts,indent=2),encoding='utf8')
 # Verify the collider's actual authored triangles, then query it independently.
 import warp as wp
 stage=env.sim.stage;assert UsdGeom.GetStageMetersPerUnit(stage)==1.
 meshes=[UsdGeom.Mesh(p) for p in Usd.PrimRange(stage.GetPrimAtPath('/World/ground')) if p.IsA(UsdGeom.Mesh)]
 assert len(meshes)==1
 m=meshes[0];vertices=np.array(m.GetPointsAttr().Get(),dtype=np.float32);face=np.array(m.GetFaceVertexIndicesAttr().Get(),dtype=np.int32).reshape(-1,3)
 xform=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(m.GetPrim()),dtype=np.float64)
 world=(np.c_[vertices,np.ones(len(vertices))]@xform)[:,:3].astype(np.float32)
 with np.load(Path('D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012/actual_mod4_wave50_query.npz'),allow_pickle=False) as z:expected_tri=z['world_triangles'];ray_starts=z['actual_world_ray_origins'];expected_height=z['expected_actual_ground']
 actual_tri=world[face].reshape(expected_tri.shape);assert np.array_equal(actual_tri,expected_tri)
 mesh_wp=wp.Mesh(points=wp.array(world,dtype=wp.vec3,device=env.device),indices=wp.array(face.reshape(-1),dtype=wp.int32,device=env.device))
 from isaaclab.utils.warp import raycast_mesh
 rays=torch.tensor(ray_starts.reshape(-1,3),device=env.device);directions=torch.zeros_like(rays);directions[:,2]=-1.
 hits=raycast_mesh(rays,directions,max_dist=10.,mesh=mesh_wp)[0]
 height=torch_view(hits).cpu().numpy()[:,2].reshape(80,35);assert np.isfinite(height).all()
 query_error=float(np.max(abs(height-expected_height)));assert query_error<=1e-6
 np.savez_compressed(output.parent/'query_actual.npz',actual_triangles=actual_tri,ray_starts=ray_starts,expected_height=expected_height,actual_height=height)
 names=list(env.robot.body_names);sensor_names=list(env.contact_sensor.body_names)
 wheel_names=[x for x in names if x.endswith('_wheel_link')];assert len(wheel_names)==2
 wheel_body=[names.index(x) for x in wheel_names];wheel_sensor=[sensor_names.index(x) for x in wheel_names]
 loops=[]
 for p0 in Usd.PrimRange(stage.GetPrimAtPath('/World/envs/env_0/Robot')):
  if not p0.IsA(UsdPhysics.Joint):continue
  j=UsdPhysics.Joint(p0)
  if not j.GetExcludeFromArticulationAttr().Get() or not j.GetJointEnabledAttr().Get():continue
  loops.append(dict(path=str(p0.GetPath()),body0=j.GetBody0Rel().GetTargets()[0].name,body1=j.GetBody1Rel().GetTargets()[0].name,pos0=list(j.GetLocalPos0Attr().Get()),pos1=list(j.GetLocalPos1Attr().Get())))
 assert len(loops)==6
 i0=[names.index(x['body0']) for x in loops];i1=[names.index(x['body1']) for x in loops]
 a0=torch.tensor([x['pos0'] for x in loops],device=env.device).repeat(80,1,1);a1=torch.tensor([x['pos1'] for x in loops],device=env.device).repeat(80,1,1)
 initial=dict(root=torch_view(env.robot.data.root_state_w).cpu().tolist(),q=torch_view(env.robot.data.joint_pos).cpu().tolist(),body_names=names,wheel_names=wheel_names,wheel_indices=wheel_body,contact_body_names=sensor_names,physics_dt=env.physics_dt,policy_dt=env.step_dt,source_saved_parameters_SHA=hashlib.sha256((prefix/'params/env.yaml').read_bytes()).hexdigest(),original_DR_config=cfg.to_dict(),seed=cfg.seed)
 (output.parent/'ACTUAL_INITIAL.json').write_text(json.dumps(initial,indent=2,default=str),encoding='utf8')
 physical_force=[];closure=[];callback_body=[];current={};rows={k:[] for k in ('before_root','root','q','body_link_pos','command','action','episode','terminated','truncated','original_terminated','original_truncated','route_boundary','joint_vel','applied_torque','obs_policy','special_mode_ids')}
 original_update=env.scene.update
 from isaaclab.utils.math import quat_apply as native_quat_apply
 def capture(dt):
  original_update(dt);assert abs(dt-.005)<1e-10
  pos=torch_view(env.robot.data.body_link_pos_w);quat=torch_view(env.robot.data.body_link_quat_w)
  b0=pos[:,i0]+torch_view(native_quat_apply(quat[:,i0].reshape(-1,4),a0.reshape(-1,3))).reshape(80,6,3)
  b1=pos[:,i1]+torch_view(native_quat_apply(quat[:,i1].reshape(-1,4),a1.reshape(-1,3))).reshape(80,6,3)
  closure.append(torch.linalg.vector_norm(b0-b1,dim=-1).cpu().numpy().copy())
  physical_force.append(torch_view(env.contact_sensor.data.net_forces_w)[:,wheel_sensor].cpu().numpy().copy())
  callback_body.append(pos[:,wheel_body].cpu().numpy().copy())
 env.scene.update=capture
 original_done=env._get_dones
 def before_reset_done():
  terminated,truncated=original_done();terminated=torch_view(terminated);truncated=torch_view(truncated)
  root=torch_view(env.robot.data.root_state_w).clone();xy=root[:,:2]-centers;boundary=(xy[:,0].abs()>3.5)|(xy[:,1].abs()>3.)
  current.update(root=root.cpu().numpy().copy(),q=torch_view(env.robot.data.joint_pos).cpu().numpy().copy(),body_link_pos=torch_view(env.robot.data.body_link_pos_w).cpu().numpy().copy(),joint_vel=torch_view(env.robot.data.joint_vel).cpu().numpy().copy(),applied_torque=torch_view(env.robot.data.applied_torque).cpu().numpy().copy(),original_terminated=terminated.cpu().numpy().copy(),original_truncated=truncated.cpu().numpy().copy(),route_boundary=boundary.cpu().numpy().copy(),terminated=terminated.cpu().numpy().copy(),truncated=(truncated|boundary).cpu().numpy().copy())
  return terminated,truncated|boundary
 env._get_dones=before_reset_done
 start=time.time()
 for control in range(750):
  manual();before=torch_view(env.robot.data.root_state_w).cpu().numpy().copy()
  expected_command=env._scale_obs_component('command',env._clip_obs_component('command',env.command))
  assert torch.allclose(obs['policy'][:,:3],expected_command,atol=1e-6,rtol=0), 'Original actor must receive requested scaled BODY command'
  actual_obs=obs['policy'].cpu().numpy().copy();mode_ids=env.command_generator.special_mode_id.cpu().numpy().copy();assert np.all(mode_ids==-1)
  with torch.inference_mode():action=model(obs['policy'])
  requested=env.command.cpu().numpy().copy();assert np.max(abs(requested[:,0]-targets.cpu().numpy()))==0 and np.max(abs(requested[:,1:]))==0
  obs,reward,terminated,truncated,extras=env.step(action);obs=torch_view(obs)
  values=dict(before_root=before,command=requested,action=action.cpu().numpy(),episode=episodes.copy(),obs_policy=actual_obs,special_mode_ids=mode_ids,**current)
  assert all(np.isfinite(x).all() for x in values.values()) and torch.isfinite(torch_view(reward)).all()
  for key,v in values.items():rows[key].append(v)
  episodes+=current['terminated']|current['truncated']
  assert len(physical_force)==(control+1)*4
  if control%50==0:(output.parent/'PROGRESS.json').write_text(json.dumps(dict(control_steps=control+1,simulated_seconds=(control+1)*.02,wall_seconds=time.time()-start,callbacks=len(physical_force))),encoding='utf8')
 data={k:np.stack(v) for k,v in rows.items()};data.update(physical_wheel_force_N=np.stack(physical_force),closure_per_physics_m=np.stack(closure),physical_wheel_link_pos=np.stack(callback_body),group_ids=groups.cpu().numpy(),targets_m_s=targets.cpu().numpy())
 assert data['root'].shape==(750,80,13) and data['physical_wheel_force_N'].shape==(3000,80,2,3)
 for k,v in model.state_dict().items():assert torch.equal(v,actor_initial[k])
 raw=output.parent/'route_raw.npz';np.savez_compressed(raw,**data)
 support=np.maximum(data['physical_wheel_force_N'].reshape(750,4,80,2,3)[...,2],0).sum(1)*.005/.02>1.
 first_failure=np.where(data['terminated'],np.arange(750)[:,None],750).min(0);shadow_closure=data['closure_per_physics_m'].reshape(750,4,80,6).max((1,3))>.002
 first_shadow=np.where(shadow_closure|data['terminated'],np.arange(750)[:,None],750).min(0)
 half=fixture['halfspan'];cent=np.array(fixture['centers']);route_rows=[];counts={};shadow_counts={}
 for group,label in ((0,'forward'),(1,'reverse'),(2,'stand')):
  complete=0;shadow_complete=0
  for i in np.flatnonzero(data['group_ids']==group):
   direction=1 if group==0 else -1;local=direction*(data['body_link_pos'][:,i,wheel_body,0]-cent[i,0]);eps=[];shadoweps=[];prefixes=[]
   for ep in np.unique(data['episode'][:,i]):
    ids=np.flatnonzero((data['episode'][:,i]==ep)&(np.arange(750)<first_failure[i]));sids=ids[ids<first_shadow[i]]
    if not len(ids):continue
    def crossed(ix):
     front=np.flatnonzero((local[ix].max(1)<-half-.2)&support[ix,i].all(1));after=np.flatnonzero((local[ix].min(1)>half+.2)&support[ix,i].all(1))
     return group!=2 and len(front)>0 and len(after)>0 and front.min()<after.max()
    ok=crossed(ids);sok=crossed(sids) if len(sids) else False
    if ok:eps.append(int(ep))
    if sok:shadoweps.append(int(ep))
    prefixes.append(dict(episode=int(ep),controls=int(len(ids)),seconds=float(len(ids)*.02),wheel_signed_x_range=[float(local[ids].min()),float(local[ids].max())],complete_before_ordinary_failure=bool(ok),complete_before_shadow_closure2mm=bool(sok),same_control_prereset_x_m=float((data['root'][ids,i,0]-data['before_root'][ids,i,0]).sum())))
   complete+=bool(eps);shadow_complete+=bool(shadoweps);route_rows.append(dict(env=int(i),group=label,complete_episodes=eps,shadow_closure_complete_episodes=shadoweps,first_ordinary_failure_control=int(first_failure[i]),first_shadow_closure_or_ordinary_control=int(first_shadow[i]),all_valid_prefixes=prefixes))
  counts[label]=dict(complete=int(complete),count=int(sum(data['group_ids']==group)),standing_no_cross_required=group==2);shadow_counts[label]=int(shadow_complete)
 result=dict(phase='completed',model=args.model_name,public_pin=source['commit'],policy_SHA=model_sha,actor_hidden_dims=agent['policy']['actor_hidden_dims'],saved_env_SHA=hashlib.sha256((prefix/'params/env.yaml').read_bytes()).hexdigest(),USD_SHA=hashlib.sha256(asset.read_bytes()).hexdigest(),mesh_SHA=fixture['mesh_SHA'],actual_world_triangles_byteexact=True,actual_query_error_m=query_error,ground_tolerance_m=1e-6,num_envs=80,policy_controls=750,physics_callbacks=3000,physics_dt_s=.005,policy_dt_s=.02,seconds=15.,wall_seconds=time.time()-start,route_scope=fixture,behavior_completion=counts,shadow_MOD4_closure2mm_completion=shadow_counts,route_rows=route_rows,ordinary_events=int(data['terminated'].sum()),route_boundary_events=int(data['route_boundary'].sum()),original_timeout_events=int(data['original_truncated'].sum()),max_closure_mm=float(data['closure_per_physics_m'].max()*1000),closure_physics_samples_over2mm=int((data['closure_per_physics_m']>.002).sum()),closure_shadow_never_changed_original_SCUT_dones=True,original_SCUT_termination_duration_and_plant_DR_kept=True,original_height_sensor_GPU_ABI_verified=scanner_receipts,actual_actor_command_obs_and_no_special_modes_verified=True,old_first_scope_ineligible_due_unconverted_rough_sensor_quaternion=True,legacy_any_substep_shadow_is_diagnostic_not_exact_control_gate=True,raw=dict(path=str(raw),bytes=raw.stat().st_size,sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),shapes={k:list(v.shape) for k,v in data.items()}),query=dict(path=str(output.parent/'query_actual.npz'),bytes=(output.parent/'query_actual.npz').stat().st_size,sha256=hashlib.sha256((output.parent/'query_actual.npz').read_bytes()).hexdigest()),resets=resets,loops=loops,contact_force_source='actual ContactSensor net_forces_w read after every original5ms scene.update; integrated positive vertical force over original4 callbacks',initial=initial,API_adapters=adapters,engine_scope='Public original robot/model/parameters with explicit previously validated API conversion on current IsaacSim6.0.1/Lab6.1.14, not original engine or MOD4 plant equivalence',no_learning=True,optimizer_updates=0,actor_byteexact_unchanged=True,MOD4_health_shadow_not_full_joint_mimic_or_hardware_equivalence=True)
 output.write_text(json.dumps(result,indent=2,default=str),encoding='utf8');print(json.dumps(dict(model=args.model_name,behavior=result['behavior_completion'],shadow_closure=result['shadow_MOD4_closure2mm_completion'],max_closure_mm=result['max_closure_mm'],ordinary=result['ordinary_events'],wall_seconds=result['wall_seconds'])),flush=True);env.close()
except Exception:
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.with_suffix('.error.txt').write_text(traceback.format_exc(),encoding='utf8');raise
finally:app.close()

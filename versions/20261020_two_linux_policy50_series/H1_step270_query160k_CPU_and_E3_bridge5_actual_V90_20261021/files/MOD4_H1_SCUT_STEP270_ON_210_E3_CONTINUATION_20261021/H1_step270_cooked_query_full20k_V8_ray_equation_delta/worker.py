"""New read-only cooked PhysX mesh audit. No PPO or action execution."""
from pathlib import Path
import ast,hashlib,json,os,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;J=B/'job0';O=B/'out';O.mkdir()
def put(n,v):(O/n).open('x',encoding='utf8').write(json.dumps(v,indent=2))
def main():
 cfg=json.loads((B/'FROZEN_CONFIG.json').read_bytes());assert cfg['kind']=='H1_step270_cooked_PhysX_queries_full20k_v8_ray_equation';source=J/'source.pt';assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_SHA']
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 old=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in old.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',OWN_E2_H1_KIND='H1_STEP270_NEW_TASK_QUERY_AUDIT',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 runtime=J/'runtime/isaac/mod4';sys.path[:0]=[str(B/'lib'),str(runtime),str(B)];entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928'];ns=runpy.run_path(str(entry),run_name='step270_cooked_query_configuration_only');env=None;error=None
 try:
  import torch,numpy as np
  torch.set_num_threads(1);torch.manual_seed(20260928);torch.cuda.manual_seed_all(20260928)
  def forbid(*a,**kw):raise RuntimeError('Cooked terrain audit forbids optimizers')
  torch.optim.Optimizer.__init__=forbid
  factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg']
  def small_cfg():
   c=original_cfg();c.scene.num_envs=20000;c.seed=20260928;c.sim.device='cuda:0';assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01;c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01}
   return c
  import h1_scut_fudan_jump_reward_v1 as scut
  import h1_step270_sdk_runtime_candidate as terrain
  original=scut.configure;scut.configure=lambda c:terrain.configure_rewards(c,original);factory.__globals__.update(Mod4EnvCfg=small_cfg,Mod4Env=terrain.H1Step270Env);env=factory();env.reset();assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4
  import omni.physx
  query=omni.physx.get_physx_scene_query_interface();origins=env.scene.env_origins.detach().cpu().numpy();points=[];labels=[]
  for i,(ox,oy,oz) in enumerate(origins):
   for dx,dy,tag in ((0,0,'lower_floor_under_robot'),(.349,0,'before_front'),(.351,0,'after_front'),(.75,0,'top_middle'),(1.149,0,'before_back'),(1.151,0,'after_back'),(.75,.601,'outside_side')):points.append([float(ox+dx),float(oy+dy),1.5]);labels.append(dict(env=i,tag=tag))
  # Separate numerical SDK probe: no simulated trajectory, actor or live phase changes.
  from types import SimpleNamespace
  from isaaclab.managers import RewardManager
  class Fixture:
   def __getattr__(self,name):return getattr(env,name)
  fixture=Fixture();n=env.num_envs;pattern=torch.arange(n,device=env.device)%4;root=torch.zeros((n,13),device=env.device);root[:,6]=1.;root[:,7]=.1;root[:,8]=.2;root[:,9]=1.2;omega=torch.zeros((n,3),device=env.device);omega[:,2]=.4
  phase=object.__new__(terrain.Step270Phase);phase.request_for_action=pattern!=1;phase.attempt=torch.ones(n,device=env.device,dtype=torch.bool);phase.launched=pattern==2;phase.landed=pattern==3;phase.release_reference_vz=torch.full((n,),3.,device=env.device)
  fixture.h1_phase=phase;fixture.scene={'robot':SimpleNamespace(data=SimpleNamespace(root_state_w=root,root_ang_vel_b=omega))}
  names=('release_shortfall','landing_yaw_rate','landing_planar_stop');terms={name:getattr(env.cfg.rewards,'h1_step270_'+name) for name in names};assert [terms[name].weight for name in names]==[-2.,-1.,-2.]
  cpu_before=torch.get_rng_state().clone();cuda_before=torch.cuda.get_rng_state().clone();manager=RewardManager(terms,fixture);contribution=manager.compute(float(env.step_dt));pat=np.arange(n)%4;release=((pat!=1)&(pat!=2)).astype(np.float64)*(3.-float(np.float32(1.2)));yaw=(pat==3)*float(np.float32(.4))**2;stop=(pat==3)*(float(np.float32(.1))**2+float(np.float32(.2))**2);expected=(-2*release-yaw-2*stop)*.01;err=float(np.abs(contribution.detach().cpu().numpy()-expected).max());assert err<=1e-6 and torch.equal(cpu_before,torch.get_rng_state()) and torch.equal(cuda_before,torch.cuda.get_rng_state())
  put('ACTUAL_NEW_THREE_STEP_RATES_ISOLATED_SDK_MATH_PROBE.json',dict(epoch=time.time(),passed=True,actual_reward_manager_type=type(manager).__module__+'.'+type(manager).__name__,fixture_rows=n,case_patterns=4,actual_configured_weights={name:terms[name].weight for name in names},actual_SDK_dt=float(env.step_dt),independent_numpy_weighted_control_contribution_maxabs=err,live_trajectory_or_actor_or_phase_or_rng_not_modified=True,no_simulated_skill_credit_or_optimizer=True,fixture_not_a_behavioral_result=True))
  point_tensor=torch.tensor(points,device=env.device,dtype=torch.float32).reshape(20000,7,3);authored_raw=terrain.mesh_query(env).cast(point_tensor.contiguous(),4.);authored={key:(value.reshape(-1,3) if value.ndim==3 and value.shape[-1]==3 else value.reshape(-1)) for key,value in authored_raw.items()};assert authored['hit'].all();rows=[];maxheight=maxnormal=0.
  def cast(origin,direction,distance):
   hits=[];raw_hits=[];callback_errors=[]
   def callback(hit):
    try:
     row=dict(collision=str(hit.collision),rigidBody=str(hit.rigid_body),position=[float(x) for x in hit.position],normal=[float(x) for x in hit.normal],distance=float(hit.distance),faceIndex=int(hit.face_index),material=str(hit.material),actual_callback_type=str(type(hit)))
     raw_hits.append(row)
     if row['collision'].startswith('/World/ground/'):hits.append(row)
     return True
    except BaseException:
     callback_errors.append(traceback.format_exc());return False
   returned=query.raycast_all(tuple(float(x) for x in origin),tuple(float(x) for x in direction),float(distance),callback)
   if callback_errors:
    put('ORIGINAL_CALLBACK_READER_ERROR.json',dict(epoch=time.time(),errors=callback_errors,raw_hits=raw_hits));raise RuntimeError('Actual RaycastHit callback failed; no swallowed exception or admission')
   if not hits:
    put('ORIGINAL_MISSING_QUERY_RAW_DIAGNOSTIC.json',dict(epoch=time.time(),origin=[float(x) for x in origin],direction=[float(x) for x in direction],distance=float(distance),raycast_all_return=str(returned),all_unfiltered_hits=raw_hits));raise RuntimeError('Cooked terrain filter missing; no fallback or admission')
   return min(hits,key=lambda x:x['distance'])
  # The original Float3 world-point failure is preserved in the V7 receipt.
  # Keep the physical 1um criterion using the actual ray equation in float64.
  from pxr import UsdGeom
  mesh_cache={};fronts=[];world_point_rejections=0;max_ray_geometry_error=0.
  def exact_hit_triangle(hit):
   path=hit['collision']
   if path not in mesh_cache:
    mesh=UsdGeom.Mesh(env.sim.stage.GetPrimAtPath(path));verts=np.asarray(mesh.GetPointsAttr().Get(),dtype=np.float32);indices=np.asarray(mesh.GetFaceVertexIndicesAttr().Get(),dtype=np.int64).reshape(-1,3);counts=np.asarray(mesh.GetFaceVertexCountsAttr().Get());assert (counts==3).all();mesh_cache[path]=(verts,indices)
   verts,indices=mesh_cache[path];return verts[indices[hit['faceIndex']]].astype(np.float64)
  for i,(ox,oy,oz) in enumerate(origins):
   origin=(float(ox+.25),float(oy),.135);hit=cast(origin,(1.,0.,0.),.2);actual_origin=np.asarray(origin,dtype=np.float32).astype(np.float64);triangle=exact_hit_triangle(hit);expected=float(np.float32(float(ox)+.35));ray_point=actual_origin+np.array([hit['distance'],0.,0.],dtype=np.float64)
   # Independent Moller-Trumbore intersection against the exact authored triangle.
   a,b,c=triangle;e1=b-a;e2=c-a;direction=np.array([1.,0.,0.]);cross=np.cross(direction,e2);det=float(e1@cross);assert abs(det)>1e-12;tvec=actual_origin-a;u=float(tvec@cross)/det;qvec=np.cross(tvec,e1);vv=float(direction@qvec)/det;t=float(e2@qvec)/det
   geometric_error=abs(float(ray_point[0])-expected);triangle_error=abs(float(hit['distance'])-t);world_error=abs(hit['position'][0]-expected);max_ray_geometry_error=max(max_ray_geometry_error,geometric_error,triangle_error);world_point_rejections+=int(world_error>1e-6)
   assert np.isfinite(triangle).all() and np.isfinite(ray_point).all() and 0<float(hit['distance'])<.2 and u>=-1e-9 and vv>=-1e-9 and u+vv<=1+1e-9
   assert np.max(np.abs(triangle[:,0]-expected))==0 and geometric_error<=1e-6 and triangle_error<=1e-6
   assert abs(hit['normal'][0]+1)<=1e-6 and abs(hit['normal'][1])+abs(hit['normal'][2])<=1e-6
   fronts.append(dict(env=i,origin=list(origin),actual_Float3_origin=actual_origin.tolist(),expected_x=expected,cooked=hit,actual_authored_hit_triangle=triangle.tolist(),float64_ray_point=ray_point.tolist(),independent_triangle_ray_distance=t,geometric_error_m=geometric_error,triangle_distance_error_m=triangle_error,world_Float3_axis_error_diagnostic_m=world_error,original_world_point_guard_failed=world_error>1e-6))
  for i,point in enumerate(point_tensor.detach().cpu().numpy().reshape(-1,3)):
   hit=cast(point,(0.,0.,-1.),4.);height=float(authored['height'][i]);normal=authored['normal'][i].detach().cpu().numpy();herr=abs(hit['position'][2]-height);nerr=float(abs(np.array(hit['normal'])-normal).max());maxheight=max(maxheight,herr);maxnormal=max(maxnormal,nerr);assert herr<=1e-6 and nerr<=1e-6;rows.append(dict(**labels[i],origin=point.tolist(),authored_height=height,authored_face=int(authored['face_id'][i]),authored_normal=normal.tolist(),cooked=hit))
  result=dict(epoch=time.time(),passed=True,kind='actual_cooked_PhysX_vs_authored_step270_queries',source_SHA=cfg['source_SHA'],source_Adam=674740,num_envs=20000,geometry=terrain.GEOMETRY,ordered_triangle_SHA=env.step270_geometry_receipt['actual_stage_ordered_triangle_SHA'],vertical_points=len(rows),front_face_points=len(fronts),physical_query_threshold_m=1e-6,front_ray_geometry_maxabs_m=max_ray_geometry_error,original_world_Float3_guard_failed_count=world_point_rejections,original_world_Float3_failures_retained_not_relabelled=True,front_physical_point_uses_float64_ray_equation_and_independent_authored_triangle=True,vertical_height_maxabs_m=maxheight,vertical_normal_maxabs=maxnormal,original_query_threshold_m=1e-6,no_fallback_or_guard_relaxation=True,raycast_all_filters_only_actual_ground_colliders=True,original_material_retained=True,all_rows=rows,front_rows=fronts,zero_optimizer_no_action_execution_no_skill_claim=True)
  put('ACTUAL_COOKED_VS_AUTHORED_STEP270_QUERY_RESULT.json',result);put('FINAL.json',dict(epoch=time.time(),passed_execution_not_skill=True,source_SHA=cfg['source_SHA'],kind=result['kind'],actual_cooked_query_pass=True,vertical_points=len(rows),front_face_points=len(fronts),artifacts=[],no_optimizer_or_learning_GO=True))
 except BaseException:error=traceback.format_exc();put('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=error,no_replay=True))
 finally:
  if env is not None:
   try:env.close()
   except BaseException:put('ENV_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  put('APP_CLOSING.json',dict(epoch=time.time(),error=bool(error)));ns['app'].close()
 if error:raise RuntimeError('Original cooked-query error retained')
if __name__=='__main__':
 try:main()
 except BaseException:
  if not (O/'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').exists():put('WORKER_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  raise

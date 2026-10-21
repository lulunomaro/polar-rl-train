"""New read-only cooked PhysX mesh audit. No PPO or action execution."""
from pathlib import Path
import ast,hashlib,json,os,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;J=B/'job0';O=B/'out';O.mkdir()
def put(n,v):(O/n).open('x',encoding='utf8').write(json.dumps(v,indent=2))
def main():
 cfg=json.loads((B/'FROZEN_CONFIG.json').read_bytes());assert cfg['kind']=='H1_step270_cooked_PhysX_queries_v3_diagnostic';source=J/'source.pt';assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_SHA']
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 old=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in old.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',OWN_E2_H1_KIND='H1_STEP270_NEW_TASK_QUERY_AUDIT',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 runtime=J/'runtime/isaac/mod4';sys.path[:0]=[str(B/'lib'),str(runtime),str(B)];entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','32','--seed','20260928'];ns=runpy.run_path(str(entry),run_name='step270_cooked_query_configuration_only');env=None;error=None
 try:
  import torch,numpy as np
  torch.set_num_threads(1);torch.manual_seed(20260928);torch.cuda.manual_seed_all(20260928)
  def forbid(*a,**kw):raise RuntimeError('Cooked terrain audit forbids optimizers')
  torch.optim.Optimizer.__init__=forbid
  factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg']
  def small_cfg():
   c=original_cfg();c.scene.num_envs=32;c.seed=20260928;c.sim.device='cuda:0';assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01;c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01}
   for k,v in dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20).items():setattr(c.sim.physics,k,v)
   return c
  import h1_scut_fudan_jump_reward_v1 as scut
  import h1_step270_sdk_runtime_candidate as terrain
  original=scut.configure;scut.configure=lambda c:terrain.configure_rewards(c,original);factory.__globals__.update(Mod4EnvCfg=small_cfg,Mod4Env=terrain.H1Step270Env);env=factory();env.reset();assert env.num_envs==32 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4
  import omni.physx
  query=omni.physx.get_physx_scene_query_interface();origins=env.scene.env_origins.detach().cpu().numpy();points=[];labels=[]
  for i,(ox,oy,oz) in enumerate(origins):
   for dx,dy,tag in ((0,0,'lower_floor_under_robot'),(.349,0,'before_front'),(.351,0,'after_front'),(.75,0,'top_middle'),(1.149,0,'before_back'),(1.151,0,'after_back'),(.75,.601,'outside_side')):points.append([float(ox+dx),float(oy+dy),1.5]);labels.append(dict(env=i,tag=tag))
  point_tensor=torch.tensor(points,device=env.device,dtype=torch.float32).reshape(32,7,3);authored_raw=terrain.mesh_query(env).cast(point_tensor.contiguous(),4.);authored={key:(value.reshape(-1,3) if value.ndim==3 and value.shape[-1]==3 else value.reshape(-1)) for key,value in authored_raw.items()};assert authored['hit'].all();rows=[];maxheight=maxnormal=0.
  def cast(origin,direction,distance):
   hits=[];raw_hits=[]
   def callback(hit):
    raw_hits.append({str(key):(value if isinstance(value,(str,int,float,bool,type(None))) else [float(x) for x in value] if hasattr(value,'__len__') else str(value)) for key,value in hit.items()})
    path=str(hit.get('collision',''))
    if path.startswith('/World/ground/'):
     hits.append(dict(collision=path,position=[float(x) for x in hit['position']],normal=[float(x) for x in hit['normal']],distance=float(hit['distance']),faceIndex=int(hit.get('faceIndex',-1))))
    return True
   returned=query.raycast_all(tuple(float(x) for x in origin),tuple(direction),float(distance),callback)
   if not hits:
    import carb
    put('ORIGINAL_MISSING_QUERY_RAW_DIAGNOSTIC.json',dict(epoch=time.time(),origin=list(origin),direction=list(direction),distance=distance,raycast_all_return=str(returned),all_unfiltered_hits=raw_hits,closest_unfiltered=str(query.raycast_closest(tuple(float(x) for x in origin),tuple(direction),float(distance))),enable_scene_query_setting=carb.settings.get_settings().get('/physics/enableSceneQuerySupport'),query_type=str(type(query)),cooked_missing_not_bypassed=True));raise RuntimeError('Cooked terrain filter missing; raw diagnostic retained, no fallback or admission')
   return min(hits,key=lambda x:x['distance'])
  for i,point in enumerate(point_tensor.detach().cpu().numpy().reshape(-1,3)):
   hit=cast(point,(0.,0.,-1.),4.);height=float(authored['height'][i]);normal=authored['normal'][i].detach().cpu().numpy();herr=abs(hit['position'][2]-height);nerr=float(abs(np.array(hit['normal'])-normal).max());maxheight=max(maxheight,herr);maxnormal=max(maxnormal,nerr);assert herr<=1e-6 and nerr<=1e-6;rows.append(dict(**labels[i],origin=point.tolist(),authored_height=height,authored_face=int(authored['face_id'][i]),authored_normal=normal.tolist(),cooked=hit))
  fronts=[]
  for i,(ox,oy,oz) in enumerate(origins):
   origin=(float(ox+.25),float(oy),.135);hit=cast(origin,(1.,0.,0.),.2);error=abs(hit['position'][0]-float(ox+.35));assert error<=1e-6 and abs(hit['normal'][0]+1)<=1e-6 and abs(hit['normal'][1])+abs(hit['normal'][2])<=1e-6;fronts.append(dict(env=i,origin=list(origin),expected_x=float(ox+.35),cooked=hit))
  result=dict(epoch=time.time(),passed=True,kind='actual_cooked_PhysX_vs_authored_step270_queries',source_SHA=cfg['source_SHA'],source_Adam=674740,num_envs=32,geometry=terrain.GEOMETRY,ordered_triangle_SHA=env.step270_geometry_receipt['actual_stage_ordered_triangle_SHA'],vertical_points=len(rows),front_face_points=len(fronts),vertical_height_maxabs_m=maxheight,vertical_normal_maxabs=maxnormal,original_query_threshold_m=1e-6,no_fallback_or_guard_relaxation=True,raycast_all_filters_only_actual_ground_colliders=True,original_material_retained=True,all_rows=rows,front_rows=fronts,zero_optimizer_no_action_execution_no_skill_claim=True)
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

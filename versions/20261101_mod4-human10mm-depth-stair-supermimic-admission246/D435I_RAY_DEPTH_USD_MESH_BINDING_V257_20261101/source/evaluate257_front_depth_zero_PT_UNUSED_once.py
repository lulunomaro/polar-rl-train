"""OwnMOD4 forward Z-depth sensor admission,12controls; no policy/checkpoint."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract257 import validate_task
p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)
assert TASK['actual_parent_private_EX_and_authority_admitted']and os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
assert hashlib.sha257(Path(__file__).read_bytes()).hexdigest()==TASK['worker_SHA']
ROOT=Path(TASK['qualified240_package_root']);payload=ROOT/'payload';OUT=P/'actual_capture';OUT.mkdir(exist_ok=False)
def put(n,x):
 with(OUT/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
real=ns=None;deadline=time.time()+TASK['worker_seconds']
try:
 original=json.loads((ROOT/'E0_original_run_manifest_frozen_v1.json').read_bytes())['env']
 for k in list(os.environ):
  if k.startswith('RM_')or k in('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v)for k,v in original.items()if k not in('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
 os.environ.update(ENABLE_CAMERAS='0',RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='0',RM_HEADING_CMD='0',RM_HEIGHT_MIN='.25',RM_HEIGHT_MAX='.25',RM_EPISODE_S='20',RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'UNREQUESTED_STOP.json'),MOD4_RESUME_QUEUE_CONTROL_US='20000')
 kit=OUT/'kit_isolation';kit.mkdir();(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}');os.environ['MOD4_188_OWN_KIT_ROOT']=str(kit);os.environ['MOD4_188_JOB_ROOT']=str(P)
 runtime=payload/'job0/runtime/isaac/mod4';sys.path[:0]=[str(P),str(ROOT),str(payload/'lib'),str(runtime),str(payload/'job0/runtime')]
 entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','27','--log_root',str(OUT/'unused_learning_logs')];ns=runpy.run_path(str(entry),run_name='capture257_camera_config_no_old_main')
 import math,numpy as np,torch
 import isaaclab.sim as sim_utils
 from isaaclab.assets import AssetBaseCfg
 from isaaclab.sensors import RayCasterCameraCfg
 from isaaclab.sensors.ray_caster.patterns import PinholeCameraPatternCfg
 from spring_nominal_sdk_readback import tensor
 sys.modules.pop('directional_spin_runtime',None)
 import mixed240_sdk as sdk
 from depth_stair247 import target_from_depth
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=1;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg);cfg.terminations.closure.params['threshold']=.01;cfg.sim.render_interval=8
 # Source-provisional mount, not measured hardware calibration: front chassis+.15m,10deg down.
 ground_file=OUT/'FORWARD_RAY257_GROUND_AND_270MM.usda'
 points=[(-10.,-10.,0.),(10.,-10.,0.),(10.,10.,0.),(-10.,10.,0.)]+[(x,y,z)for z in(0.,.27)for x,y in[(1.25,-.75),(2.75,-.75),(2.75,.75),(1.25,.75)]]
 cube=[(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,4,7),(0,7,3),(1,2,6),(1,6,5),(0,1,5),(0,5,4),(3,7,6),(3,6,2)]
 faces=[(0,1,2),(0,2,3)]+[tuple(i+4 for i in f)for f in cube]
 from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,Gf
 stage=Usd.Stage.CreateNew(str(ground_file));UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.z);UsdGeom.SetStageMetersPerUnit(stage,1.)
 root_prim=UsdGeom.Xform.Define(stage,'/Ground').GetPrim();stage.SetDefaultPrim(root_prim)
 mesh=UsdGeom.Mesh.Define(stage,'/Ground/mesh');mesh.CreatePointsAttr([Gf.Vec3f(*p)for p in points]);mesh.CreateFaceVertexCountsAttr([3]*len(faces));mesh.CreateFaceVertexIndicesAttr([i for f in faces for i in f]);mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True)
 UsdPhysics.CollisionAPI.Apply(mesh.GetPrim());mat=UsdShade.Material.Define(stage,'/Ground/Material');pm=UsdPhysics.MaterialAPI.Apply(mat.GetPrim());pm.CreateStaticFrictionAttr(.5);pm.CreateDynamicFrictionAttr(.5);pm.CreateRestitutionAttr(.5);UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat,materialPurpose='physics')
 stage.GetRootLayer().Save();del stage
 raw=ground_file.read_bytes();check=Usd.Stage.Open(str(ground_file));assert check.GetPrimAtPath('/Ground/mesh').IsA(UsdGeom.Mesh);del check
 put('ACTUAL257_GENERATED_TERRAIN_METADATA.json',dict(path=str(ground_file),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),producer_readback=1,physical_and_ray_mesh_same_USD=True,plane0_and270mm_box=True,not_privileged_heightmap=True,source_repair='Explicit UsdGeom mesh child and its exact ray target path; previous256 false retained.'))
 cfg.scene.ground=AssetBaseCfg(prim_path='/World/ground',spawn=sim_utils.UsdFileCfg(usd_path=str(ground_file)),init_state=AssetBaseCfg.InitialStateCfg(pos=(0.,0.,0.)))
 cfg.scene.d435i=RayCasterCameraCfg(prim_path=cfg.scene.robot.prim_path+'/links/chassis',update_period=0.,mesh_prim_paths=['/World/ground/mesh'],max_distance=4.,data_types=['distance_to_image_plane'],
  pattern_cfg=PinholeCameraPatternCfg(focal_length=24.,horizontal_aperture=48.*math.tan(math.radians(87./2)),vertical_aperture=48.*math.tan(math.radians(58./2)),width=84,height=48),
  offset=RayCasterCameraCfg.OffsetCfg(pos=(.15,0.,.15),rot=(0.,math.sin(math.radians(5)),0.,math.cos(math.radians(5))),convention='world'))
 real=sdk.Mixed209Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000;camera=real.scene['d435i'];robot=real.scene['robot'];vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)
 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real.cfg.terminations.closure.params['threshold']==.01 and real.cfg.terminations.mimic.params['threshold']==.01
 put('ACTUAL257_CAMERA_AND_PLANT_CONFIG.json',dict(passed=True,closure_m=.01,mimic_rad=.01,physics_dt=.0025,policy_dt=.02,camera='actual installed6.1.14 RayCasterCameraCfg; geometric environment depth',camera_parent=cfg.scene.robot.prim_path+'/links/chassis',source_provisional_mount_pos=[.15,0.,.15],source_provisional_pitch_down_deg=10.,not_measured_D435i_hardware_calibration=True,depth_type='distance_to_image_plane',resolution=[84,48],camera_ray_read_hz=50,actual_D435i_stream_fps_not_yet_bound=True,original_reward_functions_unchanged=True,stair_fixture_size_m=[1.5,1.5,.27],stair_fixture_pos_relative_env=[2.,0.,.135],not_original_Fudan_terrain_course=True,model_PT_ONNX_NN_or_optimizer=0))
 def rotation(q):
  x,y,z,w=q;return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],dtype=np.float32)
 actions=torch.zeros((1,6),device=real.device);tick=int(real._integrated_contact.tick);fb=int(real._feedback_100hz_tick);rows=[];images=[];matrices=[];transforms=[]
 for i in range(12):
  assert time.time()<deadline
  vec.step(actions);camera.update(real.step_dt,force_recompute=True)
  image=tensor(camera.data.output['distance_to_image_plane'])[0].detach().cpu().numpy().copy().reshape(48,84)
  K=tensor(camera.data.intrinsic_matrices)[0].detach().cpu().numpy().copy();pos=tensor(camera.data.pos_w)[0].cpu().numpy().copy();quat=tensor(camera.data.quat_w_ros)[0].cpu().numpy().copy()
  root=tensor(robot.data.root_state_w)[0].cpu().numpy().copy();q=root[3:7];yaw=float(np.arctan2(2*(q[3]*q[2]+q[0]*q[1]),1-2*(q[1]*q[1]+q[2]*q[2])));c,s=np.cos(yaw),np.sin(yaw);R_level_world=np.array([[c,s,0.],[-s,c,0.],[0.,0.,1.]],dtype=np.float32)
  T=np.eye(4,dtype=np.float32);T[:3,:3]=R_level_world@rotation(quat);T[:3,3]=R_level_world@(pos-np.array([root[0],root[1],0.],dtype=np.float32))
  result=target_from_depth(image,K,T,sensor_time=(i+1)*.02,control_time=(i+1)*.02)
  valid=np.isfinite(image)&(image>0);assert image.dtype==np.float32 and valid.any()and K.shape==(3,3)
  rows.append(dict(control=i+1,render_frame_available=True,finite_positive_pixels=int(valid.sum()),minimum_positive_depth_m=float(image[valid].min()),maximum_finite_depth_m=float(image[valid].max()),depth_target={k:(v.tolist()if isinstance(v,np.ndarray)else v)for k,v in result.items()},current_closure_m=float(real._mod4_closure_now[0])))
  if i in(0,11):images.append(image);matrices.append(K);transforms.append(T)
 assert int(real._integrated_contact.tick)-tick==96 and int(real._feedback_100hz_tick)-fb==24
 path=OUT/'D435I_SIM_SENSOR257_DEPTH_K_POSE.npz';np.savez_compressed(path,depth_image_plane_m=np.stack(images),K=np.stack(matrices),T_heading_optical=np.stack(transforms))
 with path.open('rb')as f:sha=hashlib.file_digest(f,'sha257').hexdigest()
 put('CAPTURE257_ACTUAL_RESULT.json',dict(passed=True,controls=12,physics_callbacks=96,feedback_samples=24,model_byte_reads=0,model_decodes=0,optimizer_steps=0,account_writes=0,rows=rows,real_sim_depth_frames=True,ray_depth_not_RTX_or_real_D435i_stereo=True,self_occlusion_and_stereo_noise_not_modelled=True,not_real_hardware_or_learned_perception_or_SuperMimic=True,producer=dict(path=str(path),bytes=path.stat().st_size,SHA=sha,transfer='METADATA_ONLY')))
except BaseException:
 put('ORIGINAL257_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV257_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV257_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:put('APP257_CLOSE_REQUESTED.json',dict(close_call_next=True,post_return_marker_optional=True));ns['app'].close()

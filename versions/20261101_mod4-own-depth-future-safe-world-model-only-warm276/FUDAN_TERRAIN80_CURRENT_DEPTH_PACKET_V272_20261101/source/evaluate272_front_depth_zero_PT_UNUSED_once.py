"""OwnMOD4 forward Z-depth sensor admission,12controls; no policy/checkpoint."""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract272 import validate_task
p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)
assert TASK['actual_parent_private_EX_and_authority_admitted']and os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==TASK['worker_SHA']
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
 entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','27','--log_root',str(OUT/'unused_learning_logs')];ns=runpy.run_path(str(entry),run_name='capture272_camera_config_no_old_main')
 import math,numpy as np,torch
 import isaaclab.sim as sim_utils
 from isaaclab.assets import AssetBaseCfg
 from isaaclab.sensors import RayCasterCameraCfg
 from isaaclab.sensors.ray_caster.patterns import PinholeCameraPatternCfg
 from spring_nominal_sdk_readback import tensor
 sys.modules.pop('directional_spin_runtime',None)
 import terrain_only272 as sdk
 from depth_stair263 import target_from_depth
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=80;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg);cfg.terminations.closure.params['threshold']=.01;cfg.sim.render_interval=8
 # Source-provisional mount, not measured hardware calibration: front chassis+.15m,10deg down.
 cfg.scene.d435i=RayCasterCameraCfg(prim_path=cfg.scene.robot.prim_path+'/links/chassis',update_period=0.,mesh_prim_paths=['/World/ground/original_Fudan_STAIRS3'],max_distance=4.,data_types=['distance_to_image_plane'],
  pattern_cfg=PinholeCameraPatternCfg(focal_length=24.,horizontal_aperture=48.*math.tan(math.radians(87./2)),vertical_aperture=48.*math.tan(math.radians(58./2)),width=84,height=48),offset=RayCasterCameraCfg.OffsetCfg(pos=(.15,0.,.15),rot=(0.,math.sin(math.radians(5)),0.,math.cos(math.radians(5))),convention='world'))
 real=sdk.TerrainMixed272Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000;camera=real.scene['d435i'];robot=real.scene['robot'];vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)
 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real.cfg.terminations.closure.params['threshold']==.01 and real.cfg.terminations.mimic.params['threshold']==.01
 put('ACTUAL272_CAMERA_AND_PLANT_CONFIG.json',dict(passed=True,closure_m=.01,mimic_rad=.01,physics_dt=.0025,policy_dt=.02,camera='actual installed6.1.14 RayCasterCameraCfg; geometric environment depth',camera_parent=cfg.scene.robot.prim_path+'/links/chassis',source_provisional_mount_pos=[.15,0.,.15],source_provisional_pitch_down_deg=10.,not_measured_D435i_hardware_calibration=True,depth_type='distance_to_image_plane',resolution=[84,48],camera_ray_read_hz=50,actual_D435i_stream_fps_not_yet_bound=True,original_reward_functions_unchanged=True,original_Fudan_geometry=sdk.DATA['metadata'],fixed_warm_level_sampling_0_to5_not_original_dynamic_curriculum=True,model_free_sensor_only=False,source_model_byte_read_admission=1,optimizer_steps=0))
 def rotation(q):
  x,y,z,w=q;return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],dtype=np.float32)
 from actual_DR_memory_getter272 import ActualDRMemoryGetter,RuntimeOrderBinding,read_old_processed_applied
 from compact_episode_static31_v1 import compact_static_snapshot
 from measured224_schema272 import pack224,validate_transition,LAYOUT
 from mod4_literal_math184_v2 import rotation_xyzw,own_virtual_legs
 with Path(TASK['model_path']).open('rb')as f:raw=f.read()
 assert len(raw)==TASK['model_bytes']and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
 ck=torch.load(io.BytesIO(raw),map_location=real.device,weights_only=False);del raw
 assert ck['iter']==2135 and ck['typed_MODEL2050_MIX240_task']['source_SHA']==TASK['source_parent_SHA']
 steps=[float(x['step'])for x in ck['optimizer_state_dict']['state'].values()];assert len(steps)==17 and min(steps)==max(steps)==42940
 actor=torch.nn.Sequential(torch.nn.Linear(35,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,32),torch.nn.ELU(),torch.nn.Linear(32,6)).to(real.device)
 weights={k.removeprefix('mlp.'):v for k,v in ck['actor_state_dict'].items()if k.startswith('mlp.')};actor.load_state_dict(weights,strict=True);actor.eval()
 for p in actor.parameters():p.requires_grad_(False)
 put('ACTUAL272_FROZEN2135_ACTOR_ONE_READ.json',dict(passed=True,source_SHA=TASK['model_SHA'],bytes=TASK['model_bytes'],physical_byte_reads=1,GPU_decodes=1,actor_exact=all(torch.equal(v,actor.state_dict()[k])for k,v in weights.items()),STD=ck['actor_state_dict']['distribution.std_param'].cpu().tolist(),optimizer_constructs=0,critic_WM_forwards=0))
 del ck
 body_names=list(robot.body_names);joint_names=list(robot.joint_names);assert len(body_names)==31 and len(joint_names)==30
 def names_of(actuator):
  ids=robot.actuators[actuator].joint_indices
  if isinstance(ids,slice):ids=list(range(30))[ids]
  elif hasattr(ids,'torch'):ids=ids.torch.tolist()
  elif torch.is_tensor(ids):ids=ids.tolist()
  return tuple(joint_names[i]for i in ids)
 binding=RuntimeOrderBinding(tuple(body_names),tuple(joint_names),names_of('legs'),names_of('wheels'),names_of('gas_springs'),real._mild_dr.materials.shape[1])
 dr=ActualDRMemoryGetter(real,binding);dr.capture_initial()
 def static31():
  e=real;p=e._explicit_pd
  return compact_static_snapshot(dr.snapshot(),nominal_mass=e._mild_dr.mass,nominal_inertia=e._mild_dr.inertia,original_body_com=e._chassis_com.original_pose[...,:3],body_id=e._chassis_com.body_id,leg_ids=p.leg_ids,wheel_ids=p.wheel_ids,gas_ids=e._spring_pressure.ids,wheel_shape_ids=e._mild_dr.wheel_shapes,nominal_gas_stiffness=e._spring_pressure.nominal)
 def copied(x):
  if torch.is_tensor(x):return x.detach().cpu().clone()
  if hasattr(x,'torch'):return x.torch.detach().cpu().clone()
  if isinstance(x,dict):return{k:copied(v)for k,v in x.items()}
  if isinstance(x,(list,tuple)):return type(x)(copied(v)for v in x)
  return x
 def complete_component_memory():
  return dict(sensor=copied(real._sensor_mild.state_dict()),feedback=copied(real._feedback_delay_mild.state_dict()),physics_action_queue=copied(real._physics_action_delay.state_dict()),spring=copied(real._spring_pressure.component.state_dict()),damping=copied(real._gas_damping.state_dict()),COM=copied(real._chassis_com.state_dict()),PD=copied(real._explicit_pd.state_dict()))
 from observed_support_context271 import Producer271,CurrentDepthPacket271,make_anchor,FRAME
 import native_geometry272 as geometry
 camera_reads=0;anchor_validated=0
 def depth_now(control_time):
  global camera_reads,anchor_validated
  camera.update(real.step_dt,force_recompute=True);camera_reads+=1
  images=tensor(camera.data.output['distance_to_image_plane']).detach().cpu().numpy().copy().reshape(80,48,84)
  Ks=tensor(camera.data.intrinsic_matrices).detach().cpu().numpy().copy();positions=tensor(camera.data.pos_w).cpu().numpy().copy();quats=tensor(camera.data.quat_w_ros).cpu().numpy().copy();roots=tensor(robot.data.root_state_w).detach().clone();root=roots.cpu().numpy().copy()
  Ts=[];worldTs=[];features=[];floors=[];found=[]
  for j in range(80):
   q=root[j,3:7];yaw=float(np.arctan2(2*(q[3]*q[2]+q[0]*q[1]),1-2*(q[1]*q[1]+q[2]*q[2])));c,s=np.cos(yaw),np.sin(yaw);R_heading=np.array([[c,s,0.],[-s,c,0.],[0.,0.,1.]],dtype=np.float32)
   T=np.eye(4,dtype=np.float32);T[:3,:3]=R_heading@rotation(quats[j]);T[:3,3]=R_heading@(positions[j]-np.array([root[j,0],root[j,1],0.],dtype=np.float32))
   W=np.eye(4,dtype=np.float32);W[:3,:3]=R_heading.T;W[:3,3]=[root[j,0],root[j,1],0.]
   target=target_from_depth(images[j],Ks[j],T,sensor_time=control_time,control_time=control_time,pixel_center_offset=.5)
   Ts.append(T);worldTs.append(W);features.append(target['features']);found.append(bool(target['found']));floors.append(target.get('visible_floor_z_m',float('nan')))
  features=torch.tensor(np.stack(features),device=real.device);found=torch.tensor(found,device=real.device,dtype=torch.bool);floors=torch.tensor(floors,device=real.device,dtype=torch.float32);W=torch.tensor(np.stack(worldTs),device=real.device)
  roots[:,:3]-=real.scene.env_origins;roots[:,3:7]=roots[:,[6,3,4,5]]
  ids=torch.where(found)[0]
  if len(ids):
   index=ids.cpu().tolist();producer=Producer271('ACTUAL_OWN_MOD4_CURRENT_DEPTH263_PACKET','own_MOD4_live_USD',TASK['run_id'],TASK['generation'],TASK['actual_resource_admission_SHA'],'D435i_front_fixed',tuple(index),tuple(int(x)for x in episodes[ids].cpu().tolist()))
   times=torch.full((len(ids),),control_time,device=real.device,dtype=torch.float32)
   packet=CurrentDepthPacket271(producer,f"{TASK['run_id']}:t{control_time:.6f}",found[ids],features[ids],floors[ids],times,times.clone(),times.clone(),roots[ids],real.scene.env_origins[ids].clone(),W[ids],FRAME,'native_wxyz')
   anchor=make_anchor(packet,static31_raw=xi[ids],geometry=geometry);state=state_now();subset=tuple(v[ids]for v in geometry_state272(state));ctx=anchor.context40(subset,producer=producer,imagination_step=0,geometry=geometry)
   assert torch.isfinite(ctx['context40_raw']).all()and ctx['context40_raw'].shape==(len(ids),40);anchor_validated+=len(ids)
  return dict(image=images,K=Ks,T=np.stack(Ts),T_world_heading=W,visible_floor_z_m=floors,sensor_pose_native13=roots,features=features,found=found,sensor_time=control_time)
 def geometry_state272(packed):
  return(packed[:,:3],geometry.quat_to_mat(packed[:,3:7]),packed[:,7:10],packed[:,10:13],packed[:,13:43],packed[:,43:73],packed[:,73:])
 def state_now(frame=None):
  root=tensor(robot.data.root_state_w).detach().clone();R=rotation_xyzw(root[:,3:7])
  L,theta=own_virtual_legs(tensor(robot.data.body_pos_w),R,body_names,real.hip_anchors194)if frame is None else(frame['L0'],frame['theta0'])
  contact=tensor(real.contacts194.data.net_forces_w)[:,real.contact_order194]if frame is None else frame['contact_forces']
  body_contact=torch.einsum('bij,bnj->bni',R.transpose(1,2),contact)
  root[:,:3]-=real.scene.env_origins;root[:,3:7]=root[:,[6,3,4,5]]
  return pack224(root,tensor(robot.data.joint_pos),tensor(robot.data.joint_vel),real._integrated_contact.history,tensor(robot.data.applied_torque),read_old_processed_applied(real,int(real._sim_step_counter)),L,theta,body_contact)
 arrays={};dynamic_memory=[];static_snapshots=[copied(dr.snapshot())];xi=static31();episodes=torch.zeros(80,device=real.device,dtype=torch.int64)
 def append(k,v):
  if torch.is_tensor(v):v=v.detach().cpu().numpy().copy()
  arrays.setdefault(k,[]).append(np.asarray(v).copy())
 put('ACTUAL272_FULL_MEASURED_SCHEMA_BINDING.json',dict(passed=True,num_envs=80,actual_environment_origins=real.scene.env_origins.cpu().tolist(),actual_resource_admission_SHA=TASK['actual_resource_admission_SHA'],terrain=sdk.DATA['metadata'],body_names=body_names,joint_names=joint_names,motor_ids=real.motor_ids194,contact_order=real.contact_order194,state224_LAYOUT=LAYOUT,static31_source='existing source-pinned parameter projection; adapted queue control clock20ms',new_WM_measurements='ownL0/theta4+BODYcontact31x3/400, torque30 already in127',full_sensor_queue_component_memory_separate=True,not_all_sensor_Markov_memory_claimed_in224=True,original_reward_text_unchanged=True,old_frozen_policy_and_STD_unchanged=True))
 original=real.literal.measured_step;pending={};control=0
 def measured(frame,tick):
  assert not pending
  before=dict(base_air_time=real.literal.base_air_time.clone(),last_contacts=real.literal.last_contacts.clone(),last_actions=frame['last_actions'].clone())
  pending.update(s1=state_now(frame),depth=depth_now(control*.02),frame={k:v.detach().clone()for k,v in frame.items()},memory_before=before,terminated=real.termination_manager.terminated.clone(),truncated=real.termination_manager.time_outs.clone(),components=complete_component_memory())
  value=original(frame,tick)
  pending['literal_reward']=value.detach().clone();pending['memory_after']=dict(base_air_time=real.literal.base_air_time.clone(),last_contacts=real.literal.last_contacts.clone())
  return value
 real.literal.measured_step=measured
 obs=vec.get_observations();tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls;depth=depth_now(0.);previous_tick=None
 for control in range(1,65):
  assert time.time()<deadline
  start_state=state_now();start_depth=depth;start_episode=episodes.clone();sxi=xi.clone();start_obs=obs['policy'].clone();start_critic=obs['critic'].clone();pending.clear()
  with torch.inference_mode():actions=actor(obs['policy'])
  obs,physical_reward,done,extra=vec.step(actions);assert pending and torch.isfinite(obs['policy']).all()and torch.isfinite(physical_reward).all()
  current_tick=int(real._integrated_contact.tick)-tick0;union=pending['terminated']|pending['truncated'];assert torch.equal(union,done.bool())
  row=dict(producer_kind='ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER',plant='own_MOD4_live_USD',run_id=TASK['run_id'],generation=TASK['generation'],source_admission_SHA=TASK['actual_resource_admission_SHA'],physics_us=2500,physics_callbacks=8,feedback_samples=2,policy_us=20000,physics_end_tick=current_tick,depth_age_seconds=(control-1)*.02-start_depth['sensor_time'],s=start_state,s1=pending['s1'],xi31=sxi,depth9=start_depth['features'],a=actions.clamp(-6.,6.))
  validate_transition(row,previous_tick=previous_tick);previous_tick=current_tick
  for k in('s','s1','xi31','depth9','a'):append(k,row[k])
  for k,v in pending['frame'].items():append('literal_'+k,v)
  for k,v in pending['memory_before'].items():append('memory_before_'+k,v)
  for k,v in pending['memory_after'].items():append('memory_after_'+k,v)
  for k,v in dict(policy_obs35=start_obs,critic_obs38=start_critic,post_policy_obs35=obs['policy'],done=done.bool(),terminated=pending['terminated'],truncated=pending['truncated'],episode_id=start_episode,original_literal_reward=pending['literal_reward'],physical_reward=physical_reward,physics_end_tick=np.array(current_tick),depth_image=start_depth['image'],K=start_depth['K'],T_heading_optical=start_depth['T'],T_world_heading=start_depth['T_world_heading'],visible_floor_z_m=start_depth['visible_floor_z_m'],sensor_pose_native13=start_depth['sensor_pose_native13'],environment_origins_world=real.scene.env_origins,depth_found=start_depth['found'],depth_time=np.array(start_depth['sensor_time']),control_time=np.array((control-1)*.02)).items():append(k,v)
  dynamic_memory.append(pending['components'])
  if bool(done.any()):
   dr.refresh_after_resets(torch.where(done)[0]);xi=static31();episodes+=done.long();static_snapshots.append(copied(dr.snapshot()));depth=depth_now(control*.02)
  else:depth=pending['depth']
 assert anchor_validated>0
 assert int(real._integrated_contact.tick)-tick0==512 and int(real._feedback_100hz_tick)-fb0==128 and real.literal.calls-calls0==64
 assert all(torch.equal(v,actor.state_dict()[k])for k,v in weights.items())
 packed={k:np.stack(v)for k,v in arrays.items()};path=OUT/'OWN272_FULLSTATE_DEPTH_PRE_RESET_TRANSITIONS.npz';np.savez_compressed(path,**packed)
 with path.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 extra_path=OUT/'OWN272_MEASURED_COMPONENT_AND_STATIC_SNAPSHOTS.pt';torch.save(dict(component_memory=dynamic_memory,static_snapshots=static_snapshots,source_model_SHA=TASK['model_SHA'],scope='measured data only; no learned model/optimizer'),extra_path)
 with extra_path.open('rb')as f:extra_sha=hashlib.file_digest(f,'sha256').hexdigest()
 counts=dict(controls=64,own_transitions=5120,physics_callbacks=512,feedback_samples=128,camera_reads=camera_reads,terminated=int(packed['terminated'].sum()),truncated=int(packed['truncated'].sum()),depth_valid_input_environment_controls=int(packed['depth_found'].sum()))
 put('CAPTURE272_ACTUAL_RESULT.json',dict(passed=True,kind=TASK['kind'],model_SHA=TASK['model_SHA'],model_byte_reads=1,model_decodes=1,optimizer_steps=0,account_writes=0,**counts,field_shapes={k:list(v.shape)for k,v in packed.items()},pre_reset_terminal_state_not_reset_pose=True,literal_reward_inputs_and_memory_recorded=True,full_sensor_queue_component_memory_separate=True,state224_not_all_sensor_Markov_memory_claim=True,actor_frozen_exact=True,new_dataset_not_complete_WM_population_or_skill=True,complete_current_depth_packet_recorded=True,actual_anchor_packets_validated=anchor_validated,terrain_metadata=sdk.DATA['metadata'],real_SuperMimic_Pi_or_WM_updates=0,producer=dict(path=str(path),bytes=path.stat().st_size,SHA=sha,transfer='METADATA_ONLY'),component_producer=dict(path=str(extra_path),bytes=extra_path.stat().st_size,SHA=extra_sha,transfer='METADATA_ONLY')))

except BaseException:
 put('ORIGINAL272_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV272_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV272_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:put('APP272_CLOSE_REQUESTED.json',dict(close_call_next=True,post_return_marker_optional=True));ns['app'].close()

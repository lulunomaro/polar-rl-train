"""Live ownMOD4 WM-only warm: frozen2135 teacher, one fresh WM Adam, original finite owner."""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,shutil,sys,time,traceback
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parent/'code'),str(Path(__file__).resolve().parent/'kernel')]
from wm_task275 import validate_task,validate_go
p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)
go=json.loads((P/'GO_PRODUCTION.json').read_bytes());validate_go(go,go['run_id'],TASK,time.time());assert os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
TASK=dict(TASK,run_id=go['run_id'],generation='OWN_LIVE_WM_WARM276_FRESH_EPISODES',actual_resource_admission_SHA=hashlib.sha256((P/'control276/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json').read_bytes()).hexdigest())
assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==TASK['worker_SHA']
ROOT=Path(TASK['qualified240_package_root']);payload=ROOT/'payload';OUT=P/'production';OUT.mkdir(exist_ok=False)
def put(n,x):
 q=OUT/(n+'.partial');q.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf8');os.replace(q,OUT/n)
real=ns=None;deadline=go['save_deadline']
try:
 original=json.loads((ROOT/'E0_original_run_manifest_frozen_v1.json').read_bytes())['env']
 for k in list(os.environ):
  if k.startswith('RM_')or k in('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v)for k,v in original.items()if k not in('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
 os.environ.update(ENABLE_CAMERAS='0',RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='0',RM_HEADING_CMD='0',RM_HEIGHT_MIN='.25',RM_HEIGHT_MAX='.25',RM_EPISODE_S='20',RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'),MOD4_RESUME_QUEUE_CONTROL_US='20000')
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
 # Complete original actor/Critic/STD/17Adam remains frozen in ck; no old DR restored into fresh physical episodes.
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
 xi=static31();episodes=torch.zeros(80,device=real.device,dtype=torch.int64)
 binding_path=OUT/'ACTUAL276_FRESH_MEASURED_SCHEMA_BINDING.json'
 put(binding_path.name,dict(passed=True,body_names=body_names,joint_names=joint_names,motor_ids=real.motor_ids194,contact_order=real.contact_order194,terrain=sdk.DATA['metadata'],state224_LAYOUT=LAYOUT,actual_resource_admission_SHA=TASK['actual_resource_admission_SHA']))
 from future_safe_wm_warm273 import FutureSafeWarmWM273,FrozenTeacherContract273
 from measured_state224_v268 import MeasurementBinding268,SCHEMA_ID
 wmbinding=MeasurementBinding268(tuple(joint_names),tuple(body_names),tuple(real.motor_ids194),'ACTUAL_OWN_MOD4_ROBOT_NAME_AND_MOTOR_ID_BINDING',hashlib.sha256(binding_path.read_bytes()).hexdigest());wmbinding.validate()
 wm=FutureSafeWarmWM273(str(Path(__file__).resolve().parent/'kernel'),torch.device(real.device),teacher_contract=FrozenTeacherContract273(TASK['model_SHA'],TASK['teacher_whole_CPU_receipt_SHA'],True),binding=wmbinding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512),synthetic_CPU_test=False)
 def finite(v):
  if torch.is_tensor(v):
   if v.is_floating_point()or v.is_complex():assert torch.isfinite(v).all()
  elif isinstance(v,dict):
   for x in v.values():finite(x)
  elif isinstance(v,(list,tuple)):
   for x in v:finite(x)
 finite(ck)
 assert float(ck['optimizer_state_dict']['param_groups'][0]['lr'])==.0019461950683593758
 put('ACTUAL276_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json',dict(passed=True,source_SHA=TASK['model_SHA'],source_byte_reads=1,source_GPU_decodes=1,source_iteration=2135,source_Adam17=steps,source_LR=float(ck['optimizer_state_dict']['param_groups'][0]['lr']),actor8_tensors_exact=True,Critic_STD_full17Adam_retained_frozen=True,teacher_optimizer_constructed=False,new_optimizer_count=1,new_optimizer_scope='WM only',new_WM_seed=27,WM_input=273,WM_output=223,state224=224,H32=32,batch=1024,hidden=[512,512,512],fresh_physics_DR_queues_and_WM_not_exact_PhysX_resume=True,original_reward_text_unchanged=True,closure_m=.01,mimic_rad=.01))
 controls=0;last_saved=0.;first=None;terminated_count=0;truncated_count=0;valid_input=0;previous_tick=None
 previous_action=torch.zeros(80,6,device=real.device);epstep=torch.zeros(80,dtype=torch.int32,device=real.device)
 def reward_memory():
  return dict(episode_sums=copied(real.literal.episode_sums),base_air_time=copied(real.literal.base_air_time),last_contacts=copied(real.literal.last_contacts),contact_filt=copied(real.literal.contact_filt),was_in_flight=copied(real.literal.was_in_flight),last_actions=copied(real.last_actions),last_root=copied(real.last_root))
 def command_memory():
  cmd=real.command_manager.get_term('twist');names=('vel_command_b','time_left','command_counter','is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed','command_uid209')
  trackers={}
  for name in real.reward_manager.active_terms:
   inner=getattr(real.reward_manager.get_term_cfg(name).func,'original',None);tracker=getattr(inner,'tracker',None)
   if tracker is not None:trackers[name]={k:copied(v)for k,v in vars(tracker).items()}
  return dict(fields={k:copied(getattr(cmd,k))for k in names if hasattr(cmd,k)},generators={k:v.get_state().cpu()for k,v in vars(cmd).items()if isinstance(v,torch.Generator)},flat_mask=copied(real._mixed209_flat),mode=copied(real._mod4_mode_bit),height=copied(real._mod4_height_cmd),ground_episode_sums=copied(real.reward_manager._episode_sums),stateful_ground_rewards=trackers)
 def full_DR():
  mild=real._mild_dr
  return dict(components=complete_component_memory(),physical_snapshot=copied(dr.snapshot()),mild=dict(factor=copied(mild.factor),nominal=copied(mild.nominal),mu=copied(mild.mu),reset_count=copied(mild.reset_count),private_GPU_rng=mild.generator.get_state().cpu(),private_CPU_rng=mild.cpu_generator.get_state(),motor_output=copied(mild.output)),global_CPU_rng=torch.random.get_rng_state(),global_CUDA_rng=torch.cuda.get_rng_state_all())
 def save(label):
  global last_saved
  assert wm.updates>0 and all(torch.equal(v,actor.state_dict()[k])for k,v in weights.items())
  assert all(float(x['step'])==42940 for x in ck['optimizer_state_dict']['state'].values())
  state=dict(kind='OWN_DEPTH_WM_ONLY_WARM276_COMPLETE',typed_WM_WARM276_task=TASK,original_finite_owner_GO=go,teacher_full_PPO_state=ck,teacher_source_SHA=TASK['model_SHA'],teacher_saved_iteration=2135,teacher_Adam17_step=42940,actual_new_WM_updates=wm.updates,actual_new_PPO_updates=0,actual_Pi_Critic_STD_updates=0,world_model=wm.checkpoint(),target_DR_state=full_DR(),mixed_ground_JUMP_state=command_memory(),original_jump_reward_memory=reward_memory(),current_measured_state224=copied(state_now()),current_static31=copied(xi),current_episodes=copied(episodes),current_episode_steps=copied(epstep),previous_clipped_action=copied(previous_action),controls=controls,own_transitions=controls*80,physics_callbacks=controls*8,feedback_samples=controls*2,full_physics_resume_claimed=False,complete_three_optimizer_conversion=False,actual_Pi_runtime_qualified=False,replay_dataset_scope='original64-control WM ring, fresh replay on resume; no full population dataset saved')
  finite(state);dest=OUT/(label+'.pt');temp=dest.with_suffix('.pt.partial');torch.save(state,temp);os.replace(temp,dest)
  with dest.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
  wmsteps=[int(v['step'])for v in wm.optimizer.state.values()];assert wmsteps and min(wmsteps)==max(wmsteps)==wm.updates
  epoch=time.time()
  row=dict(epoch=epoch,save_epoch=epoch,path=str(dest),bytes=dest.stat().st_size,SHA=sha,actual_new_WM_updates=wm.updates,saved_WM_updates=wm.updates,WM_Adam_step_min=min(wmsteps),WM_Adam_step_max=max(wmsteps),actual_new_PPO_updates=0,controls=controls,own_transitions=controls*80,teacher_source_SHA=TASK['model_SHA'],teacher_saved_iteration=2135,teacher_iteration=2135,teacher_Adam_step=42940,teacher_LR=.0019461950683593758,teacher_Adam_min=42940,teacher_Adam_max=42940,typed_WM_only_task_present=True,full_WM_tree_finite=True,frozen_teacher_fullstate_preserved=True,replay_saved=False,complete_three_optimizer_conversion=False,full_teacher_WM_Adam_norm_RNG_DR_reward_memory_saved=True)
  put('latest_complete.json',row);last_saved=time.time();return row
 original=real.literal.measured_step;pending={}
 def measured(frame,tick):
  assert not pending
  pending.update(s1=state_now(frame),depth=depth_now(controls*.02),terminated=real.termination_manager.terminated.clone(),truncated=real.termination_manager.time_outs.clone())
  return original(frame,tick)
 real.literal.measured_step=measured
 obs=vec.get_observations();tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls;depth=depth_now(0.)
 while time.time()<deadline and not(OUT/'STOP_AFTER_SAVE.json').exists()and shutil.disk_usage(P).free>=8*1024**3:
  controls+=1;start_state=state_now();start_depth=depth;start_episode=episodes.clone();sxi=xi.clone();pending.clear()
  with torch.inference_mode():actions=actor(obs['policy'])
  obs,physical_reward,done,extra=vec.step(actions);assert pending and torch.isfinite(obs['policy']).all()and torch.isfinite(physical_reward).all()
  tick=int(real._integrated_contact.tick)-tick0;union=pending['terminated']|pending['truncated'];assert torch.equal(union,done.bool())and tick==controls*8
  assert int(real._feedback_100hz_tick)-fb0==controls*2 and real.literal.calls-calls0==controls
  row=dict(producer_kind='ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER',plant='own_MOD4_live_USD',run_id=TASK['run_id'],generation=TASK['generation'],source_admission_SHA=TASK['actual_resource_admission_SHA'],physics_us=2500,physics_callbacks=8,feedback_samples=2,policy_us=20000,physics_end_tick=tick,depth_age_seconds=(controls-1)*.02-start_depth['sensor_time'],s=start_state,s1=pending['s1'],xi31=sxi,depth9=start_depth['features'],a=actions.clamp(-6.,6.))
  validate_transition(row,previous_tick=previous_tick);previous_tick=tick
  times=torch.full((80,),start_depth['sensor_time'],device=real.device,dtype=torch.float32);ct=torch.full((80,),(controls-1)*.02,device=real.device,dtype=torch.float32)
  producer=Producer271('ACTUAL_OWN_MOD4_CURRENT_DEPTH263_PACKET','own_MOD4_live_USD',TASK['run_id'],TASK['generation'],TASK['actual_resource_admission_SHA'],'D435i_front_fixed',tuple(range(80)),tuple(int(x)for x in start_episode.cpu().tolist()))
  packet=CurrentDepthPacket271(producer,f"{TASK['run_id']}:start{tick-8}",start_depth['found'],start_depth['features'],start_depth['visible_floor_z_m'],times,ct,times.clone(),start_depth['sensor_pose_native13'],real.scene.env_origins.clone(),start_depth['T_world_heading'],FRAME,'native_wxyz')
  fields=dict(s=start_state,s1=pending['s1'],a=row['a'],a_prev=previous_action,xi=torch.cat((sxi,start_depth['features']),-1),r=physical_reward,f=torch.full((80,),controls-1,device=real.device,dtype=torch.int64),ep_step=epstep,done=done.bool())
  witness=dict(kind='ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER',plant='own_MOD4_live_USD',state_schema=SCHEMA_ID,binding_witness_SHA=wmbinding.witness_SHA,measured_fields=['own_L0_theta4','contact_forces_BODY31x3'],s_physics_end_tick=tick-8,s1_physics_end_tick=tick,run_id=TASK['run_id'],generation=TASK['generation'],source_admission_SHA=TASK['actual_resource_admission_SHA'],max_depth_age_seconds=float((ct-times).max()))
  ingress=wm.add(fields,actual_anchor=packet,physics_end_tick=tick,physics_us=2500,feedback_samples=2,producer=witness)
  terminated_count+=int(pending['terminated'].sum());truncated_count+=int(pending['truncated'].sum());valid_input+=int(start_depth['found'].sum())
  previous_action=row['a'].clone();previous_action[done.bool()]=0;epstep=torch.where(done.bool(),0,epstep+1).to(torch.int32)
  if bool(done.any()):
   dr.refresh_after_resets(torch.where(done)[0]);xi=static31();episodes+=done.long();depth=depth_now(controls*.02)
  else:depth=pending['depth']
  if controls==24:put('NATIVE24_WM_WARM276_ACTUAL.json',dict(passed=True,controls=24,physics_callbacks=192,feedback_samples=48,fullstate_depth_ingress=24*80,WM_updates=0,teacher_updates=0,original_literal_calls=24,closure_m=.01,mimic_rad=.01))
  if wm.ready_for_update():
   diagnostic=wm.update()
   if first is None:
    first=save('model_first_complete');assert wm.updates==1
    from wm_task275 import FIRST_KIND,validate_first
    receipt=dict(epoch=time.time(),kind=FIRST_KIND,passed=True,source_SHA=TASK['model_SHA'],run_id=TASK['run_id'],actual_new_WM_updates=1,actual_new_PPO_updates=0,actual_new_Pi_updates=0,actual_new_critic_updates=0,actual_new_STD_updates=0,actual_Pi_Critic_teacher_updates=0,actual_Pi_Critic_STD_updates=0,num_envs=80,controls=controls,new_completed_controls=controls,new_environment_transitions=controls*80,physics_callbacks=controls*8,feedback_samples=controls*2,teacher_iteration=2135,teacher_saved_iteration=2135,teacher_Adam_step=42940,teacher_LR=.0019461950683593758,teacher_Adam17_step=42940,teacher_source_byte_reads=1,teacher_source_decodes=1,WM_optimizer_count=1,new_WM_optimizer_count=1,teacher_actor_critic_STD_full17Adam_unchanged=True,finite_WM_loss_grad_params_optimizer=True,convert_actor44_critic47=False,complete_three_optimizer_conversion=False,diagnostic=diagnostic,first_complete=first,first_current_anchor_only=True,original_JUMP_reward_unchanged=True,not_navigation_jump270_or_fullSuperMimic=True)
    receipt['actual_resource_admission_SHA']=TASK['actual_resource_admission_SHA']
    native_proof=json.loads((OUT/'NATIVE24_WM_WARM276_ACTUAL.json').read_bytes())
    receipt['native24_before_first_WM_step_passed']=bool(native_proof['passed']and native_proof['controls']==24 and native_proof['physics_callbacks']==192 and native_proof['feedback_samples']==48 and native_proof['WM_updates']==0 and native_proof['teacher_updates']==0)
    validate_first(receipt,TASK,go);put('FIRST_ACTUAL_NEW_WM_UPDATE.json',receipt)
   elif time.time()-last_saved>=120:save('model_latest_complete')
   put('LATEST_PROGRESS.json',dict(epoch=time.time(),actual_new_WM_updates=wm.updates,actual_new_PPO_updates=0,controls=controls,own_transitions=controls*80,depth_valid_input_environment_controls=valid_input,terminated=terminated_count,truncated=truncated_count,diagnostic=diagnostic,teacher_frozen=True,original_JUMP_diagnostic=real.stats194))
 assert wm.updates>0 and first is not None
 final=save('model_final_complete')
 from wm_task275 import FINAL_KIND
 receipt=dict(receipt,epoch=time.time(),kind=FINAL_KIND,actual_new_WM_updates=wm.updates,controls=controls,new_completed_controls=controls,new_environment_transitions=controls*80,physics_callbacks=controls*8,feedback_samples=controls*2,final=final,original_finite_owner_GO=go,stop_file_seen=(OUT/'STOP_AFTER_SAVE.json').exists(),disk_guard_triggered=shutil.disk_usage(P).free<8*1024**3,no_navigation_or_270skill_claim=True)
 receipt.pop('first_complete');receipt.pop('diagnostic');put('FINAL.json',receipt)
except BaseException:
 put('ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV276_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV276_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:put('APP276_CLOSING.json',dict(close_call_next=True,post_return_marker_optional=True));ns['app'].close()

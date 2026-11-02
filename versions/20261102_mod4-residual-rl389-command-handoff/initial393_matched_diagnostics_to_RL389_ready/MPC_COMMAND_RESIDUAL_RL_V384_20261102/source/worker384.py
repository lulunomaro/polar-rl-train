"""Teacher-assisted depth SuperMimic; restored WM, migrated actor/critic, original finite owner."""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,shutil,sys,time,traceback
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parent/'code'),str(Path(__file__).resolve().parent/'kernel')]
from teacher_task384 import validate_task,validate_go
p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)
go=json.loads((P/'GO_PRODUCTION.json').read_bytes());validate_go(go,go['run_id'],TASK,time.time());assert os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
TASK=dict(TASK,run_id=go['run_id'],generation='OWN_TEACHER_DEPTH_STUDENT384_FRESH_EPISODES',actual_resource_admission_SHA=hashlib.sha256((P/'control384/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json').read_bytes()).hexdigest())
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
 import terrain384 as sdk
 from depth_stair263 import target_from_depth
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=80;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg);cfg.terminations.closure.params['threshold']=.01;cfg.sim.render_interval=8
 # Source-provisional mount, not measured hardware calibration: front chassis+.15m,10deg down.
 cfg.scene.d435i=RayCasterCameraCfg(prim_path=cfg.scene.robot.prim_path+'/links/chassis',update_period=0.,mesh_prim_paths=['/World/ground/teacher_step270'],max_distance=4.,data_types=['distance_to_image_plane'],
  pattern_cfg=PinholeCameraPatternCfg(focal_length=24.,horizontal_aperture=48.*math.tan(math.radians(87./2)),vertical_aperture=48.*math.tan(math.radians(58./2)),width=84,height=48),offset=RayCasterCameraCfg.OffsetCfg(pos=(.15,0.,.15),rot=(0.,math.sin(math.radians(5)),0.,math.cos(math.radians(5))),convention='world'))
 real=sdk.Teacher384Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000;camera=real.scene['d435i'];robot=real.scene['robot'];vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)
 from residual_reset384 import install_planned_reset384
 reset384=install_planned_reset384(real,P/'feedforward384.json')
 real.reset()
 put('ACTUAL384_RL_PLANNED_RESET_AND_IMU_CACHE_REPAIR.json',reset384.receipt())
 assert torch.isfinite(tensor(robot.data.joint_pos)).all()and torch.isfinite(tensor(robot.data.joint_vel)).all()
 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real.cfg.terminations.closure.params['threshold']==.01 and real.cfg.terminations.mimic.params['threshold']==.01
 put('ACTUAL272_CAMERA_AND_PLANT_CONFIG.json',dict(passed=True,closure_m=.01,mimic_rad=.01,physics_dt=.0025,policy_dt=.02,camera='actual installed6.1.14 RayCasterCameraCfg; geometric environment depth',camera_parent=cfg.scene.robot.prim_path+'/links/chassis',source_provisional_mount_pos=[.15,0.,.15],source_provisional_pitch_down_deg=10.,not_measured_D435i_hardware_calibration=True,depth_type='distance_to_image_plane',resolution=[84,48],camera_ray_read_hz=50,actual_D435i_stream_fps_not_yet_bound=True,original_reward_functions_unchanged=False,tracking_reward_only=True,original_Fudan_geometry=sdk.DATA['metadata'],fixed_warm_level_sampling_0_to5_not_original_dynamic_curriculum=True,model_free_sensor_only=False,source_model_byte_read_admission=1,optimizer_steps=0))
 def rotation(q):
  x,y,z,w=q;return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],dtype=np.float32)
 from actual_DR_memory_getter272 import ActualDRMemoryGetter,RuntimeOrderBinding,read_old_processed_applied
 from compact_episode_static31_v1 import compact_static_snapshot
 from measured224_schema272 import pack224,validate_transition,LAYOUT
 from mod4_literal_math184_v2 import rotation_xyzw,own_virtual_legs
 with Path(TASK['model_path']).open('rb')as f:raw=f.read()
 assert len(raw)==TASK['model_bytes']and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
 ck=torch.load(io.BytesIO(raw),map_location=real.device,weights_only=False);del raw
 carrier=ck
 assert ck['kind']=='REFERENCE_TRACKING_BPTT324_COMPLETE' and ck['total_WM_updates']==16879 and ck['actual_new_Pi_updates']==4379
 ck=carrier['teacher_full_PPO_state']
 assert ck['iter']==2135
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
 from future_safe_wm_warm273 import FrozenTeacherContract273
 from tracking_wm384 import TrackingWM384
 from measured_state224_v268 import MeasurementBinding268,SCHEMA_ID
 wmbinding=MeasurementBinding268(tuple(joint_names),tuple(body_names),tuple(real.motor_ids194),'ACTUAL_OWN_MOD4_ROBOT_NAME_AND_MOTOR_ID_BINDING',hashlib.sha256(binding_path.read_bytes()).hexdigest());wmbinding.validate()
 wm=TrackingWM384(str(Path(__file__).resolve().parent/'kernel'),torch.device(real.device),teacher_contract=FrozenTeacherContract273(TASK['teacher_SHA'],TASK['teacher_whole_CPU_receipt_SHA'],True),binding=wmbinding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512),synthetic_CPU_test=False)
 wm.model.load_state_dict(carrier['world_model']['world_model'],strict=True)
 wm.optimizer.load_state_dict(carrier['world_model']['world_optimizer'])
 wm.updates=carrier['world_model']['world_updates'];wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'].cpu())
 initial_WM_updates=wm.updates
 assert wm.updates==16879 and all(int(v['step'])==16879 for v in wm.optimizer.state.values())
 from tracking_reference384 import Reference384,tracking_cost384
 from tracking_learner384 import TrackingLearner384
 reference=Reference384(P/'reference384.npz',TASK['reference'],joint_names,real.device,real.hip_anchors194)
 reference.path=P/'reference384.npz'
 learner=TrackingLearner384(wm,carrier,reference,real,wmbinding,TASK['carrier_CPU_receipt_SHA'],put)
 def finite(v):
  if torch.is_tensor(v):
   if v.is_floating_point()or v.is_complex():assert torch.isfinite(v).all()
  elif isinstance(v,dict):
   for x in v.values():finite(x)
  elif isinstance(v,(list,tuple)):
   for x in v:finite(x)
 finite(ck)
 assert float(ck['optimizer_state_dict']['param_groups'][0]['lr'])==.0019461950683593758
 put('ACTUAL276_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json',dict(passed=True,source_SHA=TASK['model_SHA'],source_byte_reads=1,source_GPU_decodes=1,source_iteration=2135,source_Adam17=steps,source_LR=float(ck['optimizer_state_dict']['param_groups'][0]['lr']),actor8_tensors_exact=True,Critic_STD_full17Adam_retained_frozen=True,source_optimizer_identity_restored_for_migration=True,new_optimizer_count=3,new_optimizer_scope='restored WM + migrated actor and critic',new_WM_seed=27,WM_input=273,WM_output=223,state224=224,H32=32,batch=1024,hidden=[512,512,512],inherited_WM_updates=16879,fresh_physics_DR_queues_replay_not_exact_PhysX_resume=True,original_reward_text_unchanged=False,tracking_reward_only=True,closure_m=.01,mimic_rad=.01))
 controls=0;last_saved=0.;first=None;student=None;terminated_count=0;truncated_count=0;valid_input=0;previous_tick=None
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
  state=dict(kind='REFERENCE_TRACKING_BPTT384_COMPLETE',source_carrier_SHA=TASK['model_SHA'],
   teacher_full_PPO_state=ck,teacher_source_SHA=TASK['teacher_SHA'],teacher_saved_iteration=2135,teacher_Adam17_step=42940,
   typed_TEACHER384_task=TASK,original_finite_owner_GO=go,student=learner.checkpoint(),world_model=wm.checkpoint(),
   actual_new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,
   actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,
   actual_new_PPO_updates=0,actual_new_STD_updates=0,learning_scope='reference_conditioned_tracking_BPTT',
   target_DR_state=full_DR(),mixed_ground_JUMP_state=command_memory(),original_jump_reward_memory=reward_memory(),
   current_measured_state224=copied(state_now()),current_static31=copied(xi),current_episodes=copied(episodes),
   current_episode_steps=copied(epstep),previous_clipped_action=copied(previous_action),reference=TASK['reference'],residual_RL=True,feedforward_protocol=learner.residual_policy.protocol,planned_reset_protocol=reset384.receipt(),
   teacher_target_layout=copied(real.target384),controls=controls,own_transitions=controls*80,
   physics_callbacks=controls*8,feedback_samples=controls*2,full_physics_resume_claimed=False,
   complete_three_optimizer_conversion=True,actual_Pi_runtime_qualified=learner.Pi_updates>0,
   reference_phase_steps=copied(epstep),replay_saved=False,actor_policy_H=8,WM_training_H=32,actor_terminal_bootstrap=False,policy_rollback_source='restoreexactfinal324/allAdamEMA_STD_WM16879;actorH8directcost_noalive_mask_noexp_noactorvalue;freshphysicalepisodes',failed_student_source_SHA=TASK['model_SHA'],inherited_world_updates=16879,replay_resume_scope='fresh physical and64-control own replay on resume; full optimizer/norm/RNG/DR/reward state retained')
  finite(state);dest=OUT/(label+'.pt');temp=dest.with_suffix('.pt.partial');torch.save(state,temp);os.replace(temp,dest)
  with dest.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
  wmsteps=[int(v['step'])for v in wm.optimizer.state.values()];assert min(wmsteps)==max(wmsteps)==wm.updates
  pi_steps=[int(v['step'])for p,v in learner.optimizers['actor'].state.items() if p.requires_grad]
  from complete_save384 import complete_adam_steps384
  critic_meta=complete_adam_steps384(learner.optimizers['critic'],learner.critic_offset+learner.critic_updates)
  assert min(pi_steps)==max(pi_steps)==learner.actor_offset+learner.Pi_updates
  epoch=time.time()
  row=dict(epoch=epoch,save_epoch=epoch,path=str(dest),bytes=dest.stat().st_size,SHA=sha,
   Pi_updates=learner.Pi_updates,critic_updates=learner.critic_updates,actual_new_WM_updates=wm.updates-initial_WM_updates,
   total_WM_updates=wm.updates,WM_Adam_step_min=min(wmsteps),WM_Adam_step_max=max(wmsteps),
   actor_Adam_step_min=min(pi_steps),actor_Adam_step_max=max(pi_steps),critic_Adam_step_min=critic_meta['step_min'],critic_Adam_step_max=critic_meta['step_max'],critic_Adam_state_slots=critic_meta['state_slots'],critic_fresh_zero_step=critic_meta['fresh_zero_step'],
   controls=controls,own_transitions=controls*80,teacher_source_SHA=TASK['teacher_SHA'],teacher_iteration=2135,
   teacher_Adam_step=42940,full_student_WM_tree_finite=True,complete_student_WM_three_optimizers=True,
   frozen_teacher_fullstate_preserved=True,full_Adam_norm_RNG_DR_reward_memory_saved=True,replay_saved=False)
  put('latest_complete.json',row);last_saved=time.time();return row
 actual_tracking_costs=[]
 original=real.literal.measured_step;pending={}
 def measured(frame,tick):
  assert not pending
  pending.update(s1=state_now(frame),depth=depth_now(controls*.02),terminated=real.termination_manager.terminated.clone(),truncated=real.termination_manager.time_outs.clone())
  real.literal.calls+=1;real.literal.last_tick=tick
  real.literal.base_air_time.zero_();real.literal.last_contacts=frame['contact_forces'][:,learner.wheelbodies,2]>1.
  label=reference.labels(epstep.long(),torch.arange(80,device=real.device),real.target384)
  cost,terms=tracking_cost384(wm.measured_layout.unpack(pending['s1']),label,learner.legs,learner.wheelbodies,previous_action,frame['actions'][:,[0,1,3,4,2,5]])
  actual_tracking_costs.append(float(cost.mean().detach()))
  return torch.exp(-cost/5.)
 real.literal.measured_step=measured
 real._mixed209_flat[:]=False
 obs=vec.get_observations();tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls;depth=depth_now(0.)
 while time.time()<deadline and not(OUT/'STOP_AFTER_SAVE.json').exists()and shutil.disk_usage(P).free>=8*1024**3:
  controls+=1;start_state=state_now();start_depth=depth;start_episode=episodes.clone();sxi=xi.clone();pending.clear()
  start_obs=obs['policy'].detach().clone();start_critic=obs['critic'].detach().clone();start_phase=epstep.long().clone()
  cmd=real.command_manager.get_command('twist');start_commands=torch.stack((cmd[:,0],cmd[:,2],real._mod4_height_cmd[:,0],torch.zeros(80,device=real.device)),-1)
  with torch.inference_mode():actions=learner.action(obs['policy'],start_depth['features'],start_state,start_phase)
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
  learner.add_metadata((wm.buffer.ptr-1)%64,start_obs,start_critic,start_phase,obs['critic'],pending['depth']['features'])
  terminated_count+=int(pending['terminated'].sum());truncated_count+=int(pending['truncated'].sum());valid_input+=int(start_depth['found'].sum())
  previous_action=row['a'].clone();previous_action[done.bool()]=0;epstep=torch.where(done.bool(),0,epstep+1).to(torch.int32)
  if bool(done.any()):
   dr.refresh_after_resets(torch.where(done)[0]);xi=static31();episodes+=done.long();depth=depth_now(controls*.02)
  else:depth=pending['depth']
  if controls==24:put('NATIVE24_TEACHER384_ACTUAL.json',dict(passed=True,controls=24,physics_callbacks=192,feedback_samples=48,fullstate_depth_ingress=24*80,new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,Pi_updates=learner.Pi_updates,critic_updates=learner.critic_updates,original_literal_calls=24,closure_m=.01,mimic_rad=.01))
  if wm.ready_for_update():
   if controls==64:
    with torch.no_grad():
     batch=wm.sample();before_rng=wm.generator.get_state().clone()
     loss,predicted,_=wm.rollout_loss(batch)
     actual=wm.measured_layout.unpack(batch['s1']);mask=batch['mask'].bool()
     poserr=torch.linalg.vector_norm(predicted[0]-actual[0],dim=-1)
     tilt_error=(predicted[1][...,2,2]-actual[1][...,2,2]).abs()
     put('ACTUAL384_H32_PAIRED_REAL_WM_METRICS_BEFORE_PI.json',dict(epoch=time.time(),passed=True,source='actual own contiguous transitions, fixed startobservedanchor; mask before episode reset',sample_count=int(mask.sum()),H32_position_RMSE_m=float(torch.sqrt(poserr[mask].square().mean())),H32_Rzz_MAE=float(tilt_error[mask].mean()),one_step_position_RMSE_m=float(torch.sqrt(poserr[:,0].square().mean())),one_step_Rzz_MAE=float(tilt_error[:,0].mean()),prediction_uses_no_future_real_depth=True,source_WM_updates=wm.updates,loss=float(loss)))
   diagnostic=wm.update()
   if controls>=64 and first is None:
    before=wm.generator.get_state().clone()
    admission=learner.update(apply_step=False)
    wm.generator.set_state(before)
    if admission is not None:
     assert admission['Pi_updates']==admission['critic_updates']==0 and not admission['optimizer_steps_applied']
     put('ACTUAL384_LIVE_H32_REWARD_TERMINAL_TEACHER_GRADIENT_BEFORE_STEP.json',dict(epoch=time.time(),passed=True,source='actual own plant fresh replay',diagnostic=admission,WM_loss=diagnostic,optimizer_steps=0))
   student=learner.update() if controls>=64 else None
   if student is not None:put('LATEST_STUDENT384.json',dict(epoch=time.time(),**student))
   if first is None and student is not None:
    first=save('model_first_complete');assert learner.Pi_updates==1
    from teacher_task384 import FIRST_KIND,validate_first
    native=json.loads((OUT/'NATIVE24_TEACHER384_ACTUAL.json').read_bytes())
    receipt=dict(epoch=time.time(),kind=FIRST_KIND,passed=True,source_SHA=TASK['model_SHA'],run_id=TASK['run_id'],
     actual_new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,
     actual_new_PPO_updates=0,actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,
     actual_new_STD_updates=0,actual_frozen_teacher_updates=0,num_envs=80,controls=controls,
     new_completed_controls=controls,new_environment_transitions=controls*80,physics_callbacks=controls*8,feedback_samples=controls*2,
     student=student,first_complete=first,diagnostic=diagnostic,original_JUMP_reward_unchanged=False,reference_tracking_objective=True,Fudan_rewards_used=False,
     complete_three_optimizer_conversion=True,teacher_frozen=True,student_skill_not_yet_evaluated=True,tracker_scope='planned reference conditioned, not autonomous depth student',
     actual_resource_admission_SHA=TASK['actual_resource_admission_SHA'],
     native24_before_first_WM_step_passed=bool(native['passed'] and native['controls']==24 and native['physics_callbacks']==192
      and native['feedback_samples']==48 and native['new_WM_updates']==native['Pi_updates']==native['critic_updates']==0))
    validate_first(receipt,TASK,go);put('FIRST_ACTUAL_TEACHER_DEPTH_STUDENT384_UPDATE.json',receipt)
   elif first is not None and time.time()-last_saved>=120:save('model_latest_complete')
   put('LATEST_PROGRESS.json',dict(epoch=time.time(),actual_new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,actual_new_PPO_updates=0,controls=controls,own_transitions=controls*80,depth_valid_input_environment_controls=valid_input,terminated=terminated_count,truncated=truncated_count,diagnostic=diagnostic,teacher_frozen=True,tracking_cost_mean_last32=sum(actual_tracking_costs[-32:])/max(1,len(actual_tracking_costs[-32:])),inherited_measurement_diagnostic=real.stats194))
 assert wm.updates>16879 and learner.Pi_updates>0 and first is not None
 final=save('model_final_complete')
 from teacher_task384 import FINAL_KIND,validate_final
 receipt=dict(receipt,epoch=time.time(),kind=FINAL_KIND,actual_new_WM_updates=wm.updates-initial_WM_updates,total_WM_updates=wm.updates,controls=controls,new_completed_controls=controls,new_environment_transitions=controls*80,physics_callbacks=controls*8,feedback_samples=controls*2,final=final,original_finite_owner_GO=go,stop_file_seen=(OUT/'STOP_AFTER_SAVE.json').exists(),disk_guard_triggered=shutil.disk_usage(P).free<8*1024**3,no_navigation_or_270skill_claim=True)
 receipt.pop('first_complete');receipt.pop('diagnostic');receipt.update(actual_new_Pi_updates=learner.Pi_updates,actual_new_critic_updates=learner.critic_updates,student=student);validate_final(receipt,TASK,go);put('FINAL.json',receipt)
except BaseException:
 if 'learner' in globals() and 'save' in globals():
  try:save('model_error_complete')
  except BaseException:put('ERROR_SAVE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 put('ORIGINAL_ERROR.json' ,dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV276_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV276_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:put('APP276_CLOSING.json',dict(close_call_next=True,post_return_marker_optional=True));ns['app'].close()

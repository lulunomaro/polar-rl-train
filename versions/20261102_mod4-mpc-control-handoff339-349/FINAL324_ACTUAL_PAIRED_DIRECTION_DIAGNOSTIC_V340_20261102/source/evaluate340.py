"""Teacher-assisted depth SuperMimic; restored WM, migrated actor/critic, original finite owner."""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,shutil,sys,time,traceback
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parent/'code'),str(Path(__file__).resolve().parent/'kernel')]
from contract340 import validate_task
p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)
assert TASK['actual_parent_private_EX_and_authority_admitted']and os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
TASK=dict(TASK,run_id='FINAL324_PAIRED_WM_DIAGNOSTIC340',generation='FROZEN_FINAL324_ACTUAL_DIAGNOSTIC340',actual_resource_admission_SHA=hashlib.sha256((P/'ACTUAL340_CURRENT_AUTHORITY_AND_N1_RESOURCE_ADMISSION.json').read_bytes()).hexdigest())
assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==TASK['worker_SHA']
ROOT=Path(TASK['qualified240_package_root']);payload=ROOT/'payload';OUT=P/'actual_capture';OUT.mkdir(exist_ok=False)
def put(n,x):
 q=OUT/(n+'.partial');q.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf8');os.replace(q,OUT/n)
real=ns=None;deadline=time.time()+TASK['worker_seconds']
try:
 original=json.loads((ROOT/'E0_original_run_manifest_frozen_v1.json').read_bytes())['env']
 for k in list(os.environ):
  if k.startswith('RM_')or k in('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v)for k,v in original.items()if k not in('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
 os.environ.update(ENABLE_CAMERAS='0',RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='0',RM_HEADING_CMD='0',RM_HEIGHT_MIN='.25',RM_HEIGHT_MAX='.25',RM_EPISODE_S='20',RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'),MOD4_RESUME_QUEUE_CONTROL_US='20000')
 kit=OUT/'kit_isolation';kit.mkdir();(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}');os.environ['MOD4_188_OWN_KIT_ROOT']=str(kit);os.environ['MOD4_188_JOB_ROOT']=str(P)
 runtime=payload/'job0/runtime/isaac/mod4';sys.path[:0]=[str(P),str(ROOT),str(payload/'lib'),str(runtime),str(payload/'job0/runtime')]
 entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','9137','--log_root',str(OUT/'unused_learning_logs')];ns=runpy.run_path(str(entry),run_name='capture272_camera_config_no_old_main')
 import math,numpy as np,torch
 import isaaclab.sim as sim_utils
 from isaaclab.assets import AssetBaseCfg
 from isaaclab.sensors import RayCasterCameraCfg
 from isaaclab.sensors.ray_caster.patterns import PinholeCameraPatternCfg
 from spring_nominal_sdk_readback import tensor
 sys.modules.pop('directional_spin_runtime',None)
 import terrain324 as sdk
 from depth_stair263 import target_from_depth
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=80;cfg.seed=9137;cfg.sim.device='cuda:0';sdk.configure(cfg);cfg.terminations.closure.params['threshold']=.01;cfg.sim.render_interval=8
 # Source-provisional mount, not measured hardware calibration: front chassis+.15m,10deg down.
 cfg.scene.d435i=RayCasterCameraCfg(prim_path=cfg.scene.robot.prim_path+'/links/chassis',update_period=0.,mesh_prim_paths=['/World/ground/teacher_step270'],max_distance=4.,data_types=['distance_to_image_plane'],
  pattern_cfg=PinholeCameraPatternCfg(focal_length=24.,horizontal_aperture=48.*math.tan(math.radians(87./2)),vertical_aperture=48.*math.tan(math.radians(58./2)),width=84,height=48),offset=RayCasterCameraCfg.OffsetCfg(pos=(.15,0.,.15),rot=(0.,math.sin(math.radians(5)),0.,math.cos(math.radians(5))),convention='world'))
 real=sdk.Teacher324Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000;camera=real.scene['d435i'];robot=real.scene['robot'];vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)
 assert int(torch.count_nonzero(tensor(robot.data.default_joint_pos)))==int(torch.count_nonzero(tensor(robot.data.default_joint_vel)))==0
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
 put('ACTUAL340_FINAL324_SINGLE_COMPLETE_READ.json',dict(passed=True,SHA=TASK['model_SHA'],bytes=TASK['model_bytes'],model_byte_reads=1,model_decodes=1,source_Pi=carrier['actual_new_Pi_updates'],source_WM=carrier['total_WM_updates'],all_three_optimizer_states_retained_in_source=True,no_optimizer_step=True))
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
 from tracking_wm324 import TrackingWM324
 from measured_state224_v268 import MeasurementBinding268,SCHEMA_ID
 wmbinding=MeasurementBinding268(tuple(joint_names),tuple(body_names),tuple(real.motor_ids194),'ACTUAL_OWN_MOD4_ROBOT_NAME_AND_MOTOR_ID_BINDING',hashlib.sha256(binding_path.read_bytes()).hexdigest());wmbinding.validate()
 wm=TrackingWM324(str(Path(__file__).resolve().parent/'kernel'),torch.device(real.device),teacher_contract=FrozenTeacherContract273(TASK['teacher_SHA'],TASK['teacher_whole_CPU_receipt_SHA'],True),binding=wmbinding,seed=27,envs=80,batch=1024,window=32,hidden=(512,512,512),synthetic_CPU_test=False)
 wm.model.load_state_dict(carrier['world_model']['world_model'],strict=True)
 wm.optimizer.load_state_dict(carrier['world_model']['world_optimizer'])
 wm.updates=carrier['world_model']['world_updates'];wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'].cpu())
 initial_WM_updates=wm.updates
 assert wm.updates==16879 and all(int(v['step'])==16879 for v in wm.optimizer.state.values())
 from tracking_reference324 import Reference324,tracking_cost324
 from teacher_student292 import model,forward,DEPTH_SCALE
 reference=Reference324(P/'reference324.npz',TASK['reference'],joint_names,real.device,real.hip_anchors194)
 class Frozen340:
  def __init__(self):
   self.actor=model(103,True,real.device);self.actor.load_state_dict(carrier['student']['actor_state_dict'],strict=True);self.actor.eval()
   for parameter in self.actor.parameters():parameter.requires_grad_(False)
   self.legs=[joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')]
   self.wheelbodies=[body_names.index(n)for n in('left_wheel','right_wheel')]
  def action(self,policy,depth,packed,phase):
   state=wm.measured_layout.unpack(packed);goal=reference.goals(state,phase,torch.arange(80,device=real.device),real.target324)
   x=torch.cat((policy,depth/depth.new_tensor(DEPTH_SCALE),goal),-1)
   return forward(self.actor,x).clamp(-6,6)
 learner=Frozen340()
 for parameter in wm.model.parameters():parameter.requires_grad_(False)
 # WM ingress keeps its schema/anchor validation and records actual pairs, but
 # the final324 model's normalizers are frozen for an honest prediction test.
 wm.model.in_norm.update=lambda value:None
 wm.model.out_norm.update=lambda value:None
 actual_endpoint_rows=[]
 sampling_rng_before=wm.generator.get_state().clone()
 frozen_wm={key:value.detach().clone()for key,value in wm.model.state_dict().items()}
 controls=0;terminated_count=0;truncated_count=0;valid_input=0;previous_tick=None
 previous_action=torch.zeros(80,6,device=real.device);epstep=torch.zeros(80,dtype=torch.int32,device=real.device)
 actual_phase=[]
 actual_tracking_costs=[]
 original=real.literal.measured_step;pending={}
 def measured(frame,tick):
  assert not pending
  pending.update(s1=state_now(frame),depth=depth_now(controls*.02),terminated=real.termination_manager.terminated.clone(),truncated=real.termination_manager.time_outs.clone())
  real.literal.calls+=1;real.literal.last_tick=tick
  real.literal.base_air_time.zero_();real.literal.last_contacts=frame['contact_forces'][:,learner.wheelbodies,2]>1.
  label=reference.labels(epstep.long(),torch.arange(80,device=real.device),real.target324)
  cost,terms=tracking_cost324(wm.measured_layout.unpack(pending['s1']),label,learner.legs,learner.wheelbodies,previous_action,frame['actions'][:,[0,1,3,4,2,5]])
  actual_tracking_costs.append(float(cost.mean().detach()))
  return torch.exp(-cost/5.)
 real.literal.measured_step=measured
 real._mixed209_flat[:]=False
 obs=vec.get_observations();tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls;depth=depth_now(0.)
 for finite_control in range(TASK['max_controls']):
  assert time.time()<deadline
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
  actual_phase.append(start_phase.detach().clone())
  actual_endpoint_rows.append(dict(p=start_state[:,:3].detach().cpu().tolist(),Rzz=wm.measured_layout.unpack(start_state)[1][:,2,2].detach().cpu().tolist(),phase=start_phase.detach().cpu().tolist(),actions=actions.detach().cpu().tolist(),done=done.bool().detach().cpu().tolist()))
  terminated_count+=int(pending['terminated'].sum());truncated_count+=int(pending['truncated'].sum());valid_input+=int(start_depth['found'].sum())
  previous_action=row['a'].clone();previous_action[done.bool()]=0;epstep=torch.where(done.bool(),0,epstep+1).to(torch.int32)
  if bool(done.any()):
   dr.refresh_after_resets(torch.where(done)[0]);xi=static31();episodes+=done.long();depth=depth_now(controls*.02)
  else:depth=pending['depth']
  if controls%16==0:put('PROGRESS340.json',dict(epoch=time.time(),controls=controls,model_reads=1,optimizer_steps=0,terminated=terminated_count))
 assert controls==64 and wm.ready_for_update()
 with torch.no_grad():
  batch=wm.sample();loss,predicted,_=wm.rollout_loss(batch);actual=wm.measured_layout.unpack(batch['s1']);mask=batch['mask'].bool()
  position_error=torch.linalg.vector_norm(predicted[0]-actual[0],dim=-1)
  rzz_error=(predicted[1][...,2,2]-actual[1][...,2,2]).abs()
  joint_error=(predicted[4][...,learner.legs]-actual[4][...,learner.legs]).square().mean(-1).sqrt()
  report=dict(epoch=time.time(),passed=True,source_final_SHA=TASK['model_SHA'],source_WM_updates=wm.updates,source_Pi_updates=4379,controls=controls,own_pairs=controls*80,physics_callbacks=controls*8,feedback_samples=controls*2,optimizer_steps=0,normalizer_updates=0,model_byte_reads=1,model_decodes=1,paired_source='Actual own final324 actor controls, measured contiguous s224/s1 before reset, first observed sameepisode anchor only',samples=int(mask.sum()),one_step_position_RMSE_m=float(position_error[:,0].square().mean().sqrt()),one_step_Rzz_MAE=float(rzz_error[:,0].mean()),H32_masked_position_RMSE_m=float(position_error[mask].square().mean().sqrt()),H32_masked_Rzz_MAE=float(rzz_error[mask].mean()),H32_masked_motor_q_RMSE_rad=float(joint_error[mask].square().mean().sqrt()),horizons=[dict(step=i+1,valid=int(mask[:,i].sum()),position_RMSE_m=float(position_error[:,i][mask[:,i]].square().mean().sqrt())if bool(mask[:,i].any())else None,Rzz_MAE=float(rzz_error[:,i][mask[:,i]].mean())if bool(mask[:,i].any())else None)for i in(0,3,7,15,31)],training_loss_diagnostic=float(loss),actual_termination_events=terminated_count,truncated=truncated_count,loss_not_skill=True,independent_skill_test=False,future_depth_in_prediction=False,causal_scope='actual prediction error, not proof of gradient fidelity or only failure cause')
 # Measure predicted signed movement/yaw against real contiguous endpoints.
 def yaw_from_R(rot):return torch.atan2(rot[...,1,0],rot[...,0,0])
 def wrapped(x):return torch.atan2(torch.sin(x),torch.cos(x))
 actual0=wm.measured_layout.unpack(batch['s'][:,0]);p0=actual0[0];yaw0=yaw_from_R(actual0[1])
 horizons=[]
 for i in(0,3,7,15,31):
  valid=mask[:,i]
  pred_delta=predicted[0][:,i]-p0;real_delta=actual[0][:,i]-p0
  pyaw=wrapped(yaw_from_R(predicted[1][:,i])-yaw0);ryaw=wrapped(yaw_from_R(actual[1][:,i])-yaw0)
  horizons.append(dict(step=i+1,valid=int(valid.sum()),predicted_dx_mean=float(pred_delta[valid,0].mean()),actual_dx_mean=float(real_delta[valid,0].mean()),dx_MAE=float((pred_delta[valid,0]-real_delta[valid,0]).abs().mean()),predicted_dy_mean=float(pred_delta[valid,1].mean()),actual_dy_mean=float(real_delta[valid,1].mean()),predicted_dyaw_mean=float(pyaw[valid].mean()),actual_dyaw_mean=float(ryaw[valid].mean()),dyaw_MAE=float(wrapped(pyaw[valid]-ryaw[valid]).abs().mean()),wrong_dx_sign_fraction=float(((pred_delta[valid,0]*real_delta[valid,0]<0)&(real_delta[valid,0].abs()>.001)).float().mean())))
 # H4 action-gradient diagnostic with all actual labels/actions and frozen WM.
 # This is local model sensitivity, not a measured physical derivative.
 from future_safe_wm_warm273 import context_from_start_anchor273
 from native_depth_world_model50_v255 import normalize_context40
 phase_all=torch.stack(actual_phase)
 b=wm.buffer;slots=b._row(torch.arange(b.size,device=wm.device));candidates=wm.anchors.data['valid_anchor'][slots].nonzero()
 selected=candidates[:min(256,len(candidates))];rows,envs=slots[selected[:,0]],selected[:,1]
 anchor=wm.anchors.gather(rows,envs);initial=wm.measured_layout.unpack(b.data['s'][rows,envs].detach().clone());phase=phase_all[rows,envs]
 action=b.data['a'][rows,envs].detach().clone().requires_grad_(True);previous=b.data['a_prev'][rows,envs].detach().clone()
 state=initial;costs=[];component_means={}
 for i in range(4):
  context=context_from_start_anchor273(anchor,state,i,wm.native_geometry)
  state=wm.model.step(state,action,normalize_context40(context))
  label=reference.labels(phase+i,envs,real.target324)
  cost,terms=tracking_cost324(state,label,learner.legs,learner.wheelbodies,previous,action)
  costs.append(cost)
  for key,value in terms.items():component_means[key]=component_means.get(key,0.)+float(value.detach().mean())/4
  previous=action
 coststack=torch.stack(costs,1)
 exp_loss=-torch.exp(-coststack/5.).sum(1).mean()
 direct_loss=coststack.sum(1).mean()/5.
 exp_grad=torch.autograd.grad(exp_loss,action,retain_graph=True)[0]
 direct_grad=torch.autograd.grad(direct_loss,action)[0]
 assert torch.isfinite(exp_grad).all()and torch.isfinite(direct_grad).all()
 sensitivity=dict(scope='frozenWM H4 actionheldconstant sensitivity atactualobservedstarts;NOTactualphysicalfiniteDifference',sample_count=len(envs),source_phase_min=int(phase.min()),source_phase_max=int(phase.max()),cost_mean=float(coststack.detach().mean()),cost_max=float(coststack.detach().max()),exp_negative_return=float(exp_loss.detach()),direct_scaled_cost=float(direct_loss.detach()),exp_gradient_L2=float(exp_grad.norm()),direct_gradient_L2=float(direct_grad.norm()),exp_gradient_per_action_mean=exp_grad.mean(0).cpu().tolist(),direct_gradient_per_action_mean=direct_grad.mean(0).cpu().tolist(),tracking_components=component_means,optimizer_steps=0)
 report.update(direction_horizons=horizons,model_local_action_sensitivity=sensitivity)
 put('ACTUAL340_FINAL324_PAIRED_WM_PREDICTION_METRICS.json',report)
 put('ACTUAL340_REAL_ENDPOINT_DIRECTION_ROWS.json',dict(epoch=time.time(),schema='64controlsx80environments startp_Rzz_phase_action_done',rows=actual_endpoint_rows,model_reads=0,source='new340actualownphysicalmeasurement'))

 assert all(torch.equal(value,wm.model.state_dict()[key])for key,value in frozen_wm.items())
 assert wm.updates==16879 and all(int(value['step'])==16879 for value in wm.optimizer.state.values())
 summary=dict(report,kind=TASK['kind'],model_SHA=TASK['model_SHA'],replay=[],strict_successes=0,crossed_cases=0,ground_complete=0,terminations=real.stats194['terminations'],account_writes=0,no_new_training=True,prediction_only_not_skill=True)
 put('RESULT340.json',summary);print(json.dumps(report),flush=True)
except BaseException:
 put('ORIGINAL340_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV340_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV340_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:put('APP340_CLOSE_REQUESTED.json',dict(close_call_next=True));ns['app'].close()

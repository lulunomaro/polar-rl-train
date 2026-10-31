"""ROOT-only NEW220 N1 first-episode mean-policy regression in207 PhysX path.

Current ROOT parent owns authority/resources/locks/wait. No optimizer or GUI.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent/'source'))
from contract220 import validate_task,E0_PARENT,KIND
parser=argparse.ArgumentParser();parser.add_argument('--task',type=Path,required=True);args=parser.parse_args()
P=args.task.resolve().parent;TASK=json.loads(args.task.read_bytes());validate_task(TASK)
assert os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
assert TASK['actual_parent_private_EX_and_authority_admitted'] is True
assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==TASK['worker_SHA']
ROOT=Path(TASK['qualified197_package_root']);payload=ROOT/'payload'
OUT=P/'actual_capture';OUT.mkdir(exist_ok=False)


def put(n,v):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


deadline=time.time()+840;real=ns=None
try:
 original=json.loads((payload/'job0/original_run_manifest.json').read_bytes())['env']
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SPIN_STAGE','RM_SLOPE_INITIAL_ADMISSION')})
 os.environ.update(RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',
  RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='1',RM_HEADING_CMD='0',
  RM_HEIGHT_MIN='.23',RM_HEIGHT_MAX='.33',RM_EPISODE_S='20',RM_HIDDEN_DIMS='256,128,64',
  RM_VALUE_LOSS_COEF='2.0',RM_SCHEDULE='adaptive',RM_ENTROPY_COEF='.005',RM_DESIRED_KL='.01',
  RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'UNREQUESTED_STOP.json'))
 os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
 kit=OUT/'kit_isolation';kit.mkdir();(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}')
 os.environ['MOD4_188_OWN_KIT_ROOT']=str(kit);os.environ['MOD4_188_JOB_ROOT']=str(P)
 runtime=payload/'job0/runtime/isaac/mod4'
 sys.path[:0]=[str(P),str(ROOT),str(payload/'lib'),str(runtime),str(payload/'job0/runtime')]
 entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','27','--log_root',str(OUT/'unused_learning_logs')]
 ns=runpy.run_path(str(entry),run_name='capture220_config_only_no_old_main')
 import numpy as np
 import torch
 from spring_nominal_sdk_readback import tensor
 import jump194_sdk as sdk
 from wheel_geometry220 import load_own_wheels,authored_bottom,unknown
 from flight_evidence220 import summarize
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=1;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg)
 cfg.commands.twist.ranges.ang_vel_z=(0.,0.)  #207 controlled eval-only factor;reward unchanged.
 real=sdk.JumpMod4Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000
 vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.);obs=vec.get_observations();robot=real.scene['robot']
 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8
 assert obs['policy'].shape==(1,35) and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
 assert real.cfg.terminations.closure.params['threshold']==.002 and real.cfg.terminations.mimic.params['threshold']==.01
 assert tuple(cfg.commands.twist.ranges.lin_vel_x)==(-2.1,2.1)
 names=list(robot.body_names);wheels=[names.index('left_wheel'),names.index('right_wheel')]
 assert real.literal.feet_indices.detach().cpu().tolist()==wheels
 ground_spawn_name=getattr(cfg.scene.ground.spawn.func,'__name__','UNKNOWN')
 if ground_spawn_name=='spawn_local_native_plane':
  plane_z=float(cfg.scene.ground.init_state.pos[2])
 else:
  plane_z=float(cfg.scene.ground.init_state.pos[2])+.5*float(cfg.scene.ground.spawn.size[2])
 assert plane_z==0.,dict(spawn_function=ground_spawn_name,actual_top=plane_z)
 put('ACTUAL220_LITERAL_JUMP_PLANE_BEFORE_MODEL.json',dict(passed=True,
  original_JUMP19_methods_config16_scales_no_edits=True,literal_reward_names=real.literal.reward_names,
  original_weights_per_second={k:v/.02 for k,v in real.literal.reward_scales.items()},
  original_clip_single=2.5,original_total_positive_clip=False,original_plane_mu_restitution=[.5,.5],
  binding_original_training_scope=real.binding_receipt(),actual_eval_yaw_range=[0.,0.],
  actual_vx_range=[-2.1,2.1],actual_height_range=[.12,.15],plane_top_z_m=plane_z,
  actor35_critic38_action6=True,physics_us=2500,policy_us=20000,TGS=[32,4],nominal_gas_k=2000,
  nominal_gas_N=400,DR='Original D0white_v3 and D1-D7 fresh N1 engineering recipe',
  fresh_N1_physics_not_20k_DR_slice=True,eval_original_JUMP_mode_only=True))
 try:
  import omni.usd
  stage=omni.usd.get_context().get_stage()  #Existing stage only;no USD open.
  robot_path=cfg.scene.robot.prim_path.replace('{ENV_REGEX_NS}','/World/envs/env_0').replace('env_.*','env_0')
  geometry,support=load_own_wheels(stage,robot_path)
 except Exception as exc:
  geometry=[unknown(name,'STAGE_ACCESS_UNAVAILABLE',error=type(exc).__name__+': '+str(exc))[0] for name in ('left_wheel','right_wheel')]
  support=[None,None]
 put('ACTUAL220_OWN_LOADED_STAGE_WHEEL_GEOMETRY.json',dict(wheels=geometry,
  wheel_metadata_queries=2,max_prim_visits_each=10000,max_meshes_each=64,max_points_each=65536,
  extra_PhysX_getter_calls=0,stage_open_calls=0,plane_top_z_m=plane_z,
  geometry_unknown_is_reported_not_a_physics_or_training_gate=True,cooked_contact_depth=False))
 source=Path(TASK['model_path'])
 with source.open('rb') as f:raw=f.read()
 assert len(raw)==TASK['model_bytes'] and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
 ck=torch.load(io.BytesIO(raw),map_location='cuda:0',weights_only=False);del raw
 assert ck['iter']==TASK['model_iteration'] and ck['source_parent_branch_SHA']==E0_PARENT
 typed=ck['typed_MIX210_task'];assert typed['source_SHA']==E0_PARENT and typed['reward_weights_and_functions_no_edits']
 assert typed['learning_seconds']==10800 and typed['ground_envs']==2000 and typed['jump_envs']==18000
 assert ck['actual_new_PPO_updates']==TASK['actual_training_new_PPO_updates']
 actor=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6)).to(real.device)
 weights={k.removeprefix('mlp.'):v for k,v in ck['actor_state_dict'].items() if k.startswith('mlp.')}
 actor.load_state_dict(weights,strict=True);actor.eval()
 assert all(torch.equal(v,actor.state_dict()[k]) for k,v in weights.items())
 put('ACTUAL220_ONE_NEW_GPU_MODEL_MEAN_RESTORE.json',dict(passed=True,model_SHA=TASK['model_SHA'],model_iteration=TASK['model_iteration'],
  source_parent_branch_SHA=E0_PARENT,new_GPU_file_reads=1,new_GPU_decodes=1,model_copies=0,
  actor35_6_literal=True,optimizer_constructed=False,learned_STD_in_source_but_deterministic_mean=True,
  fresh_N1_physical_DR_no_20k_restore=True,no_state_or_force_injection=True))
 del ck,weights
 frames=[];pending={};old_compute=real.termination_manager.compute;old_reward=real.original_jump_once
 term_names=list(real.termination_manager.active_terms)
 def capture_terminal(*a,**kw):
  value=old_compute(*a,**kw)
  pending['position']=tensor(robot.data.body_pos_w)[0].detach().cpu().numpy().copy()
  pending['quat_xyzw']=tensor(robot.data.body_quat_w)[0].detach().cpu().numpy().copy()
  pending['root13']=tensor(robot.data.root_state_w)[0].detach().cpu().numpy().copy()
  pending['q30']=tensor(robot.data.joint_pos)[0].detach().cpu().numpy().copy()
  pending['flags']={n:bool(real.termination_manager.get_term(n)[0]) for n in term_names}
  return value
 def capture_reward(*a,**kw):
  value=old_reward(*a,**kw)
  #Reuse already-read original reward tensor;no contact sensor/view call here.
  pending['wheel_force_xyz']=real.literal.contact_forces[0,real.literal.feet_indices,:].detach().cpu().numpy().copy()
  pending['original_flight_flag']=bool(real.literal.was_in_flight[0])
  pending['nonwheel_force_norm_max']=float(torch.linalg.vector_norm(real.literal.contact_forces[0,real.literal.penalised_contact_indices,:],dim=-1).max())
  pending['original_reward_command4']=real.literal.commands[0].detach().cpu().numpy().copy()
  pending['original_reward_motor_actions6']=real.literal.actions[0].detach().cpu().numpy().copy()
  return value
 real.termination_manager.compute=capture_terminal;real.original_jump_once=capture_reward
 old_manager=real.reward_manager.compute;reward_dt=[]
 def counted_reward(*a,**kw):
  dt=kw.get('dt',a[0] if a else None);assert dt==.02;reward_dt.append(dt);return old_manager(*a,**kw)
 real.reward_manager.compute=counted_reward
 tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls
 queue0=dict(real._physics_action_delay.calls);endflags={};reward_sum=0.;completed=0;ended=False
 with torch.inference_mode():
  for control in range(1000):
   assert time.time()<deadline,'Original finite capture bound reached'
   pending.clear();action=actor(obs['policy'])
   command=real.command_manager.get_command('twist')[0].detach().cpu().numpy().copy()
   raw_action=action[0].detach().cpu().numpy().copy()
   obs,reward,done,extra=vec.step(action)
   assert set(pending)=={'position','quat_xyzw','root13','q30','flags','wheel_force_xyz','original_flight_flag','nonwheel_force_norm_max','original_reward_command4','original_reward_motor_actions6'}
   assert pending['position'].shape==(31,3) and pending['quat_xyzw'].shape==(31,4)
   assert all(np.isfinite(pending[k]).all() for k in ('position','quat_xyzw','root13','q30','wheel_force_xyz','nonwheel_force_norm_max','original_reward_command4','original_reward_motor_actions6'))
   bottoms=[authored_bottom(support[j],pending['position'][idx],pending['quat_xyzw'][idx],plane_z) for j,idx in enumerate(wheels)]
   frames.append(dict(pending,command=command,raw_action=raw_action,
    authored_bottom=np.asarray([np.nan if b is None else b for b in bottoms],dtype=np.float32)))
   completed+=1;reward_sum+=float(reward[0])
   if bool(done[0]):endflags=pending['flags'];ended=True;break
 assert completed>0 and int(real._integrated_contact.tick)-tick0==8*completed
 assert int(real._feedback_100hz_tick)-fb0==2*completed and real.literal.calls-calls0==completed
 assert {k:real._physics_action_delay.calls[k]-queue0[k] for k in ('legs','wheels')}=={'legs':8*completed,'wheels':8*completed}
 assert reward_dt==[.02]*completed
 pos=np.stack([x['position'] for x in frames]).astype(np.float32);root=np.stack([x['root13'] for x in frames]).astype(np.float32)
 quat=np.stack([x['quat_xyzw'] for x in frames]);contact=np.stack([x['wheel_force_xyz'] for x in frames])
 bottoms=np.stack([x['authored_bottom'] for x in frames]);cmds=np.stack([x['command'] for x in frames])
 raw_actions=np.stack([x['raw_action'] for x in frames]);flagrows=[x['flags'] for x in frames]
 nonwheel_force=np.asarray([x['nonwheel_force_norm_max'] for x in frames],dtype=np.float32)
 evidence=summarize(contact,bottoms,flagrows,root,raw_actions,nonwheel_force)
 assert float(np.max(np.abs(cmds[:,2])))==0.
 qx,qy,qz,qw=(root[:,i] for i in (3,4,5,6))
 yaw=np.unwrap(np.arctan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz)));dyaw=yaw-yaw[0]
 reward_commands=np.stack([x['original_reward_command4'] for x in frames])
 metrics=dict(command_yaw_max_abs=float(np.max(np.abs(cmds[:,2]))),observed_vx_range=[float(cmds[:,0].min()),float(cmds[:,0].max())],
  observed_height_range=[float(reward_commands[:,2].min()),float(reward_commands[:,2].max())],
  final_heading_delta_rad=float(dyaw[-1]),max_abs_heading_excursion_rad=float(np.max(np.abs(dyaw))),
  mean_abs_root_world_angular_z=float(np.mean(np.abs(root[:,12]))),max_abs_root_world_angular_z=float(np.max(np.abs(root[:,12]))),
  maximum_common_wheel_center_z=float(pos[:,wheels,2].min(1).max()),wheel_center_not_clearance=True)
 artifact=OUT/'ACTUAL220_NEW210_E0_BODY_POSES_AND_FLIGHT.npz'
 vertices=np.asarray([[-20,-20,plane_z],[20,-20,plane_z],[20,20,plane_z],[-20,20,plane_z]],dtype=np.float32)
 np.savez_compressed(artifact,body_position_w=pos,body_quat_xyzw=quat,root13=root,
  q30=np.stack([x['q30'] for x in frames]),commands=cmds,original_reward_command4=reward_commands,
  raw_action6=raw_actions,original_reward_motor_actions6=np.stack([x['original_reward_motor_actions6'] for x in frames]),
  wheel_contact_xyz=contact,wheel_contact_z=contact[:,:,2],authored_wheel_bottom_above_plane_m=bottoms,
  nonwheel_force_norm_max=nonwheel_force,
  authored_left_bodylocal_points=np.empty((0,3),dtype=np.float32) if support[0] is None else support[0],
  authored_right_bodylocal_points=np.empty((0,3),dtype=np.float32) if support[1] is None else support[1],
  geometry_known=np.isfinite(bottoms),original_flight_flag=np.asarray([x['original_flight_flag'] for x in frames],dtype=np.bool_),
  terminal_flags=np.asarray([[x[n] for n in term_names] for x in flagrows],dtype=np.bool_),termination_names=np.asarray(term_names),
  terrain_vertices=vertices,terrain_faces=np.asarray([[0,1,2],[0,2,3]],dtype=np.int32),control=np.arange(1,completed+1,dtype=np.int32),
  body_names=np.asarray(names),joint_names=np.asarray(list(robot.joint_names)))
 with artifact.open('rb') as f:artifact_sha=hashlib.file_digest(f,'sha256').hexdigest()
 result=dict(passed=True,kind=KIND,epoch=time.time(),model_SHA=TASK['model_SHA'],model_iteration=TASK['model_iteration'],
  controls=completed,physics_callbacks=completed*8,feedback_samples=completed*2,seconds=completed*.02,
  requested_controls_max=1000,requested_seconds_max=20.,first_episode_only=True,original_done=ended,
  terminal_flags=endflags,all_termination_counts={n:sum(int(x[n]) for x in flagrows) for n in term_names},
  recording='Actual207 path;50Hz endpoint body poses and original flags BEFORE automatic reset',
  reward_sum=reward_sum,original_JUMP_reward_no_edits=True,eval_yaw0_only=True,metrics=metrics,
  plane_flight_evidence=evidence,geometry=geometry,
  original_filtered_flight_flag_rows=sum(int(x['original_flight_flag']) for x in frames),
  artifact=dict(path=str(artifact),bytes=artifact.stat().st_size,SHA=artifact_sha,
   producer_worker_SHA=TASK['worker_SHA'],producer_model_SHA=TASK['model_SHA'],producer_controls=completed,
   producer_only_no_transfer_or_GUI=True,unknown_geometry_values_are_explicit_NaN_masked_by_geometry_known=True),
  body_names=names,joint_names=list(robot.joint_names),body_quaternion='actual SDK xyzw',
  model_byte_reads=1,model_decodes=1,model_copies=0,optimizer_steps=0,critic_WM_forward=False,
  account_writes=0,artifact_transfers=0,actual_270_skill=False,population_success_rate=False,stable_landing_certified=False)
 put('CAPTURE220_ACTUAL_RESULT.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ('body_names','joint_names','geometry')}),flush=True)
except BaseException:
 put('ORIGINAL220_CAPTURE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_automatic_retry=True));raise
finally:
 if real is not None:real.close()
 if ns is not None:ns['app'].close()
 put('APP220_CLOSED.json',dict(epoch=time.time(),closed=True))

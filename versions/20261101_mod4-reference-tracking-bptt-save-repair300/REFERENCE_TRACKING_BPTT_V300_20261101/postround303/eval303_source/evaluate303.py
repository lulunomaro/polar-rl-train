"""Teacher-assisted depth SuperMimic; restored WM, migrated actor/critic, original finite owner."""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,shutil,sys,time,traceback
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parent/'code'),str(Path(__file__).resolve().parent/'kernel')]
from contract303 import validate_task
p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)
assert TASK['actual_parent_private_EX_and_authority_admitted'] and os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
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
 import terrain300 as sdk
 from depth_stair263 import target_from_depth
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=80;cfg.seed=9137;cfg.sim.device='cuda:0';sdk.configure(cfg);cfg.terminations.closure.params['threshold']=.01;cfg.sim.render_interval=8
 # Source-provisional mount, not measured hardware calibration: front chassis+.15m,10deg down.
 cfg.scene.d435i=RayCasterCameraCfg(prim_path=cfg.scene.robot.prim_path+'/links/chassis',update_period=0.,mesh_prim_paths=['/World/ground/teacher_step270'],max_distance=4.,data_types=['distance_to_image_plane'],
  pattern_cfg=PinholeCameraPatternCfg(focal_length=24.,horizontal_aperture=48.*math.tan(math.radians(87./2)),vertical_aperture=48.*math.tan(math.radians(58./2)),width=84,height=48),offset=RayCasterCameraCfg.OffsetCfg(pos=(.15,0.,.15),rot=(0.,math.sin(math.radians(5)),0.,math.cos(math.radians(5))),convention='world'))
 real=sdk.Teacher300Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000;camera=real.scene['d435i'];robot=real.scene['robot'];vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)
 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real.cfg.terminations.closure.params['threshold']==.01 and real.cfg.terminations.mimic.params['threshold']==.01
 put('ACTUAL272_CAMERA_AND_PLANT_CONFIG.json',dict(passed=True,closure_m=.01,mimic_rad=.01,physics_dt=.0025,policy_dt=.02,camera='actual installed6.1.14 RayCasterCameraCfg; geometric environment depth',camera_parent=cfg.scene.robot.prim_path+'/links/chassis',source_provisional_mount_pos=[.15,0.,.15],source_provisional_pitch_down_deg=10.,not_measured_D435i_hardware_calibration=True,depth_type='distance_to_image_plane',resolution=[84,48],camera_ray_read_hz=50,actual_D435i_stream_fps_not_yet_bound=True,original_reward_functions_unchanged=False,tracking_reward_only=True,original_Fudan_geometry=sdk.DATA['metadata'],fixed_warm_level_sampling_0_to5_not_original_dynamic_curriculum=True,model_free_sensor_only=False,source_model_byte_read_admission=1,optimizer_steps=0))
 def rotation(q):
  x,y,z,w=q;return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],dtype=np.float32)
 from wheel_geometry220 import load_own_wheels
 import omni.usd
 stage=omni.usd.get_context().get_stage()
 rp=cfg.scene.robot.prim_path.replace('{ENV_REGEX_NS}','/World/envs/env_0').replace('env_.*','env_0')
 metadata,points=load_own_wheels(stage,rp)
 assert all(p is not None for p in points),metadata
 put('ACTUAL303_OWN_WHEEL_SUPPORT_GEOMETRY.json',dict(wheels=metadata,queries=2))
 raw=Path(TASK['model_path']).read_bytes()
 assert len(raw)==TASK['model_bytes'] and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
 ck=torch.load(io.BytesIO(raw),map_location=real.device,weights_only=False);del raw
 assert ck['kind']=='REFERENCE_TRACKING_BPTT300_COMPLETE' and ck['actual_new_Pi_updates']==TASK['expected_Pi_updates']
 weights={k.removeprefix('mlp.'):v for k,v in ck['student']['actor_state_dict'].items()if k.startswith('mlp.')}
 actor=torch.nn.Sequential(torch.nn.Linear(103,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,32),torch.nn.ELU(),torch.nn.Linear(32,6)).to(real.device)
 actor.load_state_dict(weights,strict=True);actor.eval()
 for parameter in actor.parameters():parameter.requires_grad_(False)
 del ck
 put('ACTUAL303_FINAL300_ACTOR_ONE_READ.json',dict(passed=True,SHA=TASK['model_SHA'],model_byte_reads=1,model_decodes=1,optimizer_constructs=0))
 body_names=list(robot.body_names);wheel_ids=[body_names.index(n) for n in('left_wheel','right_wheel')]
 nonwheel=[i for i,n in enumerate(body_names)if n not in('left_wheel','right_wheel')]
 support=[torch.tensor(p,device=real.device)for p in points]
 origin=real.scene.env_origins.clone();target=real.target300.clone();ct,st=target[:,3].cos(),target[:,3].sin()
 def bounds():
  allpos=tensor(robot.data.body_pos_w);allq=tensor(robot.data.body_quat_w);lo=[];hi=[]
  for i,wid in enumerate(wheel_ids):
   q=allq[:,wid];x,y,z,w=q.unbind(-1)
   R=torch.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(80,3,3)
   v=torch.einsum('nij,pj->npi',R,support[i])+allpos[:,wid,None]-origin[:,None]
   delta=v[:,:,:2]-target[:,None,:2]
   local=torch.stack((ct[:,None]*delta[:,:,0]+st[:,None]*delta[:,:,1],-st[:,None]*delta[:,:,0]+ct[:,None]*delta[:,:,1],v[:,:,2]),-1)
   lo.append(local.amin(1));hi.append(local.amax(1))
  return torch.stack(lo,1),torch.stack(hi,1)
 def depth_features():
  camera.update(real.step_dt,force_recompute=True)
  image=tensor(camera.data.output['distance_to_image_plane']).detach().cpu().numpy().reshape(80,48,84)
  K=tensor(camera.data.intrinsic_matrices).detach().cpu().numpy();pos=tensor(camera.data.pos_w).detach().cpu().numpy()
  quat=tensor(camera.data.quat_w_ros).detach().cpu().numpy();root=tensor(robot.data.root_state_w).detach().cpu().numpy()
  feats=[]
  for j in range(80):
   x,y,z,w=root[j,3:7];yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z));c,s=np.cos(yaw),np.sin(yaw)
   heading=np.array([[c,s,0.],[-s,c,0.],[0.,0.,1.]],dtype=np.float32)
   transform=np.eye(4,dtype=np.float32);transform[:3,:3]=heading@rotation(quat[j]);transform[:3,3]=heading@(pos[j]-[root[j,0],root[j,1],0.])
   feats.append(target_from_depth(image[j],K[j],transform,sensor_time=0.,control_time=0.,pixel_center_offset=.5)['features'])
  return torch.tensor(np.stack(feats),device=real.device)
 from tracking_reference300 import Reference300,tracking_cost300
 reference=Reference300(P/'reference300.npz',TASK['reference'],list(robot.joint_names),real.device,real.hip_anchors194)
 def goal_state():
  root=tensor(robot.data.root_state_w);q=root[:,3:7];x,y,z,w=q.unbind(-1)
  R=torch.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(80,3,3)
  return(root[:,:3]-real.scene.env_origins,R,root[:,7:10],root[:,10:13],tensor(robot.data.joint_pos),tensor(robot.data.joint_vel),torch.zeros(80,151,device=real.device))
 real.reset();obs=vec.get_observations();active=torch.ones(80,dtype=torch.bool,device=real.device)
 flight=torch.zeros(80,dtype=torch.long,device=real.device);first_air=torch.zeros_like(flight);up=torch.zeros_like(active)
 cross=torch.zeros(80,2,dtype=torch.bool,device=real.device);land=torch.zeros_like(flight);stable=torch.zeros_like(flight);stable_peak=torch.zeros_like(flight)
 success=torch.zeros_like(active);cross_ever=torch.zeros_like(active);flight_ever=torch.zeros_like(active)
 counts=torch.zeros_like(flight);reward_sum=torch.zeros(80,device=real.device);vx_sum=torch.zeros_like(reward_sum);vx_mae=torch.zeros_like(reward_sum)
 overflow=torch.zeros(80,6,dtype=torch.long,device=real.device);depth_valid=torch.zeros_like(flight)
 low,high=bounds();previous=high[:,:,0].clone();tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick)
 previous_air=torch.zeros_like(active);support_seen=torch.zeros_like(active);physics_counts=torch.zeros_like(flight);current_control=0;terminal_rows={};frames=[];captured={};phys_calls=0
 selected=[1,0,10,20];old_scene_update=real.scene.update
 def measure_physics(dt):
  global flight,first_air,up,cross,land,stable,stable_peak,success,cross_ever,flight_ever,previous,previous_air,support_seen,phys_calls
  old_scene_update(dt)
  if abs(float(dt)-.0025)>1e-9:return
  phys_calls+=1;low,high=bounds();root=tensor(robot.data.root_state_w)
  f=tensor(real.contacts194.data.net_forces_w)[:,real.contact_order194];wf=f[:,wheel_ids];nw=torch.linalg.vector_norm(f[:,nonwheel],dim=-1).amax(-1)
  airborne=(torch.linalg.vector_norm(wf,dim=-1)<=1).all(-1)&(low[:,:,2]>.005).all(-1)&(nw<=1)&active
  support_seen|=(torch.linalg.vector_norm(wf,dim=-1)>1).all(-1)&active
  first_air+=(airborne&~previous_air&active&support_seen).long();first=(first_air==1)&support_seen
  flight=torch.where(airborne,flight+1,torch.zeros_like(flight));up|=airborne&first&(root[:,9]>.05)
  crossing=(previous<0)&(high[:,:,0]>=0)&(low[:,:,2]>=.27)
  cross|=crossing&airborne[:,None]&first[:,None]
  crossed=cross.all(-1)&up&first;cross_ever|=crossed;flight_ever|=airborne
  inside=(low[:,:,0]>=0)&(high[:,:,0]<=3)&(low[:,:,1]>=-1)&(high[:,:,1]<=1)
  ontop=inside.all(-1)&(low[:,:,2]>=.269).all(-1)&(low[:,:,2]<=.28).all(-1)&(wf[:,:,2]>1).all(-1)&(nw<=1)&active
  land=torch.where(ontop&cross_ever&first,land+1,torch.zeros_like(land))
  x,y,z,w=root[:,3:7].unbind(-1)
  roll=torch.atan2(2*(w*x+y*z),1-2*(x*x+y*y));pitch=torch.asin((2*(w*y-z*x)).clamp(-1,1));yaw=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z))
  heading=torch.atan2(torch.sin(yaw-target[:,3]),torch.cos(yaw-target[:,3]))
  steady=ontop&(land>=12)&(root[:,9].abs()<=.03)&(torch.linalg.vector_norm(root[:,7:9],dim=-1)<=.03)&(roll.abs()<.174533)&(pitch.abs()<.174533)&(heading.abs()<.2)
  stable=torch.where(steady,stable+1,torch.zeros_like(stable));stable_peak=torch.maximum(stable_peak,stable);success|=(stable>=200)&(~real._mixed209_flat)&active
  physics_counts.add_(active.long());previous=high[:,:,0].clone();previous_air=airborne
 real.scene.update=measure_physics
 # Same measured endpoint tracking objective as training300. No legacy reward.
 leg_ids=[robot.joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')]
 previous_action=torch.zeros(80,6,device=real.device);endpoint={}
 tracking_cost_sum=torch.zeros(80,device=real.device);tracking_reward_sum=torch.zeros_like(tracking_cost_sum)
 tracking_term_sum={}
 def tracking_measured(frame,tick):
  root=tensor(robot.data.root_state_w);q=root[:,3:7];x,y,z,w=q.unbind(-1)
  rot=torch.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(80,3,3)
  aux=torch.zeros(80,151,device=real.device);aux[:,54:56]=frame['L0'];aux[:,56:58]=frame['theta0']
  aux[:,58:]=torch.einsum('bij,bnj->bni',rot.transpose(1,2),frame['contact_forces']).flatten(1)/400.
  state=(root[:,:3]-origin,rot,root[:,7:10],root[:,10:13],tensor(robot.data.joint_pos),tensor(robot.data.joint_vel),aux)
  label=reference.labels(torch.full((80,),current_control-1,device=real.device,dtype=torch.long),torch.arange(80,device=real.device),target)
  cost,terms=tracking_cost300(state,label,leg_ids,wheel_ids,previous_action,frame['actions'][:,[0,1,3,4,2,5]])
  endpoint.update(cost=cost.detach().clone(),reward=torch.exp(-cost/5.).detach().clone(),terms={k:v.detach().clone()for k,v in terms.items()})
  real.literal.calls+=1;real.literal.last_tick=tick;real.literal.base_air_time.zero_();real.literal.last_contacts=frame['contact_forces'][:,wheel_ids,2]>1.
  return torch.exp(-cost/5.)
 real.literal.measured_step=tracking_measured
 original_compute=real.termination_manager.compute
 def compute(*args,**kwargs):
  value=original_compute(*args,**kwargs);done=real.termination_manager.terminated|real.termination_manager.time_outs
  root=tensor(robot.data.root_state_w)
  captured.update(root=root.detach().clone(),pos=tensor(robot.data.body_pos_w).detach().clone(),quat=tensor(robot.data.body_quat_w).detach().clone(),
   closure=real._mod4_closure_now.detach().clone(),wheel_forces=tensor(real.contacts194.data.net_forces_w)[:,real.contact_order194][:,wheel_ids].detach().clone())
  for i in torch.where(done&active)[0].cpu().tolist():
   terminal_rows[str(i)]=dict(control=current_control,seconds=int(counts[i])*.02,flags={n:bool(real.termination_manager.get_term(n)[i])for n in real.termination_manager.active_terms},root13=root[i].cpu().tolist())
  return value
 real.termination_manager.compute=compute
 for current_control in range(1,TASK['max_controls']+1):
  assert time.time()<deadline
  d=depth_features();x=torch.cat((obs['policy'],d/d.new_tensor([4.,.4,2.,np.pi,2.,4.,1.,.2,1.])),-1)
  goal=reference.goals(goal_state(),torch.full((80,),current_control-1,device=real.device,dtype=torch.long),torch.arange(80,device=real.device),real.target300)
  with torch.inference_mode():raw_action=actor(torch.cat((x,goal),-1));action=raw_action.clamp(-6,6)
  assert torch.isfinite(action).all();before=active.clone();counts.add_(before.long());overflow.add_((raw_action.abs()>6)&before[:,None]);depth_valid.add_((d[:,8]==1)&before)
  obs,reward,done,extra=vec.step(action)
  tracking_cost_sum.add_(torch.where(before,endpoint['cost'],0.));tracking_reward_sum.add_(torch.where(before,endpoint['reward'],0.))
  for name,value in endpoint['terms'].items():
   if name not in tracking_term_sum:tracking_term_sum[name]=torch.zeros_like(value)
   tracking_term_sum[name].add_(torch.where(before,value,0.))
  previous_action=action.detach().clone();previous_action[done.bool()]=0.
  reward_sum.add_(torch.where(before,reward,0.));r=captured['root'];q=r[:,3:7];v=r[:,7:10]
  u=-q[:,:3];tv=2*torch.cross(u,v,dim=-1);bodyv=v+q[:,3,None]*tv+torch.cross(u,tv,dim=-1)
  vx_sum.add_(torch.where(before,bodyv[:,0],0.));labels=reference.labels(torch.full((80,),current_control-1,device=real.device,dtype=torch.long),torch.arange(80,device=real.device),real.target300);expected=(labels['state'][:,12:15]*torch.stack((target[:,3].cos(),target[:,3].sin(),torch.zeros_like(target[:,3])),-1)).sum(-1)
  vx_mae.add_(torch.where(before,(bodyv[:,0]-expected).abs(),0.))
  frames.append(dict(pos=captured['pos'][selected].cpu().numpy(),quat=captured['quat'][selected].cpu().numpy(),root=r[selected].cpu().numpy(),
   force=captured['wheel_forces'][selected].cpu().numpy(),action=action[selected].cpu().numpy(),depth=d[selected].cpu().numpy()))
  active&=~done.bool()
  if current_control%50==0:put('PROGRESS303.json',dict(control=current_control,active_first_episodes=int(active.sum()),successes=int(success.sum())))
  if not active.any():break
 assert phys_calls==current_control*8 and int(real._integrated_contact.tick)-tick0==current_control*8 and int(real._feedback_100hz_tick)-fb0==current_control*2
 assert all(torch.equal(value,actor.state_dict()[key])for key,value in weights.items())
 results=[]
 for i in range(80):
  isflat=bool(real._mixed209_flat[i]);controls=int(counts[i]);term=terminal_rows.get(str(i))
  results.append(dict(env=i,kind='reference270',controls=controls,seconds=controls*.02,full_window=controls==400,
   reference_vx_last=float(expected[i]),tracking_cost_mean=float(tracking_cost_sum[i]/max(1,controls)),tracking_reward_mean=float(tracking_reward_sum[i]/max(1,controls)),tracking_components={k:float(v[i]/max(1,controls))for k,v in tracking_term_sum.items()},body_vx_mean=float(vx_sum[i]/max(1,controls)),body_vx_MAE=float(vx_mae[i]/max(1,controls)),target=target[i].cpu().tolist(),
   episode_terminal=term,first_air_events=int(first_air[i]),airborne_ever=bool(flight_ever[i]),first_flight_both_cross=bool(cross_ever[i]),
   longest_stable_seconds=float(stable_peak[i])*.0025,strict270_stable=bool(success[i]),depth_valid_controls=int(depth_valid[i]),action_overflow=overflow[i].cpu().tolist()))
 replay=[]
 for j,env_id in enumerate(selected):
  count=int(counts[env_id]);packet=dict(body_position_w=np.stack([f['pos'][j]for f in frames[:count]]),body_quat_xyzw=np.stack([f['quat'][j]for f in frames[:count]]),
   root13=np.stack([f['root'][j]for f in frames[:count]]),wheel_contact_xyz=np.stack([f['force'][j]for f in frames[:count]]),
   action6=np.stack([f['action'][j]for f in frames[:count]]),depth9=np.stack([f['depth'][j]for f in frames[:count]]))
  path=OUT/('REPLAY303_env'+str(env_id)+'.npz');np.savez_compressed(path,**packet)
  replay.append(dict(env=env_id,path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest(),controls=count,
   seconds=count*.02,result=results[env_id],origin=origin[env_id].cpu().tolist(),body_names=body_names))
 jumps=[r for r in results if r['kind']=='reference270'];ground=[r for r in results if r['kind']=='ground']
 summary=dict(passed=True,kind=TASK['kind'],model_SHA=TASK['model_SHA'],seed=9137,independent_fresh_DR_episodes=True,same_fixed_reference_course=True,heldout_terrain_layout=False,Fudan_objective_used=False,planned_reference_conditioned=True,autonomous_depth_student=False,controls=current_control,physics_callbacks=phys_calls,
  feedback_samples=current_control*2,first_episodes=80,jump_cases=80,strict_successes=sum(r['strict270_stable']for r in jumps),crossed_cases=sum(r['first_flight_both_cross']for r in jumps),
  ground_complete=sum(r['full_window']for r in ground),ground_cases=ground,
  terminations={name:sum(bool((r['episode_terminal']or{}).get('flags',{}).get(name))for r in results)for name in real.termination_manager.active_terms},
  results=results,replay=replay,optimizer_steps=0,model_byte_reads=1,model_decodes=1,account_writes=0,
  support_measurement='400Hz full authored collision wheel bounds+net wheel load over top; no contact manifold normal identity',
  no_new_training=True,readiness='failure valid; success requires corresponding top manifold confirmation before graduation')
 put('RESULT303.json',summary);print(json.dumps({k:summary[k]for k in('passed','controls','strict_successes','crossed_cases','ground_complete','terminations')}),flush=True)
except BaseException:
 put('ORIGINAL303_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV303_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV303_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:put('APP303_CLOSE_REQUESTED.json',dict(close_call_next=True));ns['app'].close()

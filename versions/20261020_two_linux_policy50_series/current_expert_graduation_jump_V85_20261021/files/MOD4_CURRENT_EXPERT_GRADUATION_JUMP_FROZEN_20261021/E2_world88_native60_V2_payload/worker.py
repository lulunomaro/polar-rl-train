"""Original signed4 world/stand/straight bank on the closed50 source and 50Hz runtime."""
from pathlib import Path
import hashlib,json,os,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;J=B/'job0';O=B/'out';O.mkdir()
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 cfg=json.loads((B/'FROZEN_CONFIG.json').read_bytes());steps=cfg['steps'];assert steps in (60,750);src=J/'source.pt';assert H(src)==cfg['source_SHA'];put('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),source_SHA=cfg['source_SHA'],steps=steps,no_optimizer=True))
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 old=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in old.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_SPAWN_GRACE_STEPS='5',MOD4_RESUME_QUEUE_CONTROL_US='20000',OWN_E2_H1_KIND='E2_WORLD_MOVING_SIGNED4',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 runtime=J/'runtime/isaac/mod4';sys.path[:0]=[str(B/'lib'),str(runtime),str(B)];entry=runtime/'train_E2_full_resume_v1.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','88','--seed','20260928'];ns=runpy.run_path(str(entry),run_name='frozen_E2_configuration_only');env=None;error=None;controls=[];physics=[];artifacts=[];total=0;physical_pending=[]
 try:
  import torch,numpy as np,math
  import torch.nn.functional as F
  torch.set_num_threads(1);torch.manual_seed(20260928);torch.cuda.manual_seed_all(20260928);torch.set_float32_matmul_precision('highest')
  def forbid(*a,**k):raise RuntimeError('Frozen evaluation forbids optimizer construction')
  torch.optim.Optimizer.__init__=forbid;factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg']
  def small_cfg():
   c=original_cfg();c.scene.num_envs=88;c.seed=20260928;c.sim.device='cuda:0';assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01;c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01}
   from isaaclab.sensors import ContactSensorCfg
   c.scene.full_robot_contact=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/.*',update_period=0.0,history_length=1,track_air_time=False)
   for k,v in dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20).items():setattr(c.sim.physics,k,v)
   return c
  factory.__globals__['Mod4EnvCfg']=small_cfg;env=factory();assert env.num_envs==88 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8;env._physics_action_delay.queue.control_us=20000
  from h1_fullstate_environment_v1 import tensor
  from h1_authored_full_collider_plane_reference_v1 import extract,evaluate
  cpu=lambda x:tensor(x).detach().cpu().numpy().copy();robot=env.scene['robot'];names=list(robot.body_names);sensor=env.scene.sensors['full_robot_contact'];contact=list(sensor.body_names);assert len(contact)==31;shapes=extract(env.sim.stage,'/World/envs/env_0/Robot',names);assert len(shapes)==34;wheel=[contact.index(x) for x in ('left_wheel','right_wheel')];wheel_shapes=[[i for i,x in enumerate(shapes) if x['body']==name] for name in ('left_wheel','right_wheel')];stepping=False;frame=None
  old_update=env.scene.update
  def update(dt):
   old_update(dt)
   if not stepping:return
   pos=tensor(robot.data.body_pos_w);quat=tensor(robot.data.body_quat_w);clear=evaluate(pos,quat,shapes);force=tensor(sensor.contact_view.get_net_contact_forces(dt=float(dt))).reshape(88,31,3);raw=tensor(env._integrated_contact.sensor.contact_view.get_net_contact_forces(dt=float(dt))).reshape(88,2,3);assert float(abs(force[:,wheel]-raw).max())<=.1;physical_pending.append(dict(root13=cpu(robot.data.root_state_w),q30=cpu(robot.data.joint_pos),all34_clearance=cpu(clear),all31_contact_force=cpu(force),wheel_raw=cpu(raw),wheel_5ms_mean=cpu(env._integrated_contact.history[:,0]),wheel_clearance=cpu(torch.stack([clear[:,ids].amin(-1) for ids in wheel_shapes],-1)),body_pos=cpu(pos),body_quat_xyzw=cpu(quat),episode=cpu(env._sensor_mild.episode)))
  env.scene.update=update;old_term=env.termination_manager.compute
  def termination(*a,**k):
   nonlocal frame
   result=old_term(*a,**k)
   if stepping:
    import mod4_task as task
    frame=dict(root13=cpu(robot.data.root_state_w),q30=cpu(robot.data.joint_pos),executed6=cpu(env.action_manager.action),impulse=cpu(env._integrated_contact.impulse),history=cpu(env._integrated_contact.history),closure=cpu(torch.stack(list(task.closure_errors(env).values())).amax(0)),mimic=cpu(torch.stack(list(task.mimic_errors(env).values())).amax(0)),ground=cpu(task.ground_height(env)),command=cpu(env.command_manager.get_term('twist').command),episode=cpu(env._sensor_mild.episode),heading=cpu(robot.data.heading_w))
   return result
  env.termination_manager.compute=termination
  from clock_training_health import ClockTrainingHealth,learning_health_pass
  health=ClockTrainingHealth(env,O)
  from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
  vec=RslRlVecEnvWrapper(env,clip_actions=6.);state=torch.load(src,map_location='cpu',weights_only=False);assert state['policy_clock']['policy_hz']==50 and {int(v['step']) for v in state['optimizer_state_dict']['state'].values()}=={cfg['source_Adam']} and len(state['actor_state_dict'])==9;original={k:v.clone() for k,v in state['actor_state_dict'].items()};w={k:v.to(env.device) for k,v in original.items()};env.reset();obs=vec.get_observations();cmd=env.command_manager.get_term('twist');cmd.set_manual_evaluation_mode();gid=torch.arange(88,device=env.device)%11;moving=gid>=3;angles=torch.tensor([0.,0.,0.,0.,0.,math.pi/2,math.pi/2,math.pi/3,math.pi/3,math.pi,math.pi],device=env.device)[gid];yaw=torch.tensor([0.,0.,0.,4.,-4.,4.,-4.,4.,-4.,4.,-4.],device=env.device)[gid];straight=torch.tensor([0.,.3,1.,0.,0.,0.,0.,0.,0.,0.,0.],device=env.device)[gid]
  np.savez_compressed(O/'INITIAL_ACTUAL.npz',root13=cpu(robot.data.root_state_w),q30=cpu(robot.data.joint_pos),group=cpu(gid),world_direction=cpu(angles),signed_yaw=cpu(yaw));put('GEOMETRY_AND_CLOCK_ACTUAL.json',dict(source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],shapes=shapes,body_names=names,contact_names=contact,policy_hz=50,physics_dt=.0025,decimation=8,feedback_hz=100,seed=20260928,original11_groups_times8=True,world_goal_m_s=.5,signed_yaw_rad_s=4.,original_body_command_rule='2*.5*cos(heading-direction),vy0,cap1.5',public_command_refresh_only_no_extra_observation_noise_draw=True,no_other_actor_input_changed=True,no_position_teacher_or_assist_force=True))
  from nominal_parameter_audit import parameter_audit
  audit=parameter_audit(env);assert audit['profile']=='white_v3' and audit['actual_parameters_pass'];put('INITIAL_PARAMETER_READBACK.json',audit)
  import subprocess
  gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);own=[x for x in gpu.splitlines() if x.split(',')[1].strip()==str(os.getpid())];assert own and all(cfg['GPU_UUID'] in x for x in own);put('ACTUAL_OWN_GPU.json',dict(epoch=time.time(),own=own))
  def persist():
   for values,prefix in ((controls,'CONTROL'),(physics,'PHYSICS')):
    if not values:continue
    p=O/(prefix+'_'+str(sum(x.get('kind')==prefix for x in artifacts)).zfill(4)+'.npz');np.savez_compressed(p,**{k:np.stack([r[k] for r in values]) for k in values[0]});artifacts.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p),kind=prefix,rows=len(values)));values.clear()
   tmp=O/'VALID_PREFIX_INDEX.tmp';tmp.write_text(json.dumps(dict(epoch=time.time(),controls=total,artifacts=artifacts),indent=2));tmp.replace(O/'VALID_PREFIX_INDEX.json')
  tick=env._integrated_contact.tick;fb=env._feedback_100hz_tick;start=time.monotonic()
  try:
   with torch.inference_mode():
    for i in range(steps):
     cmd.set_manual_evaluation_mode();cmd.time_left.fill_(1e9);cmd.is_standing_env[:]=False;cmd.is_heading_env[:]=False;cmd.is_moving_spin[:]=moving;cmd.world_direction[:]=angles;cmd.signed_yaw[:]=yaw;vx=torch.where(moving,torch.cos(tensor(robot.data.heading_w)-angles),straight);cmd.vel_command_b.zero_();cmd.vel_command_b[:,0]=vx;cmd.vel_command_b[:,2]=yaw;env._mod4_mode_bit=torch.zeros(88,device=env.device,dtype=torch.long);x=obs['policy'].clone();x[:,:3]=cmd.command;assert x.shape==(88,35) and torch.isfinite(x).all() and torch.equal(x[:,:3],cmd.command) and (x[:,28]==1).all() and not x[:,29:35].any();raw=x
     for n in (0,2,4,6):
      raw=F.linear(raw,w[f'mlp.{n}.weight'],w[f'mlp.{n}.bias'])
      if n!=6:raw=F.elu(raw)
     policy=cpu(x);action=cpu(raw);heading_input=cpu(robot.data.heading_w);root_input=cpu(robot.data.root_state_w);physical_pending=[];frame=None;before=env._integrated_contact.tick;before_fb=env._feedback_100hz_tick;stepping=True
     try:obs,reward,done,info=vec.step(raw)
     finally:stepping=False
     assert env._integrated_contact.tick-before==8 and env._feedback_100hz_tick-before_fb==2 and len(physical_pending)==8 and frame is not None and torch.isfinite(reward).all();controls.append(dict(policy=policy,raw_action=action,reward=cpu(reward),done=cpu(done),heading_for_command=heading_input,root_before_policy=root_input,**frame));physics.extend(physical_pending);physical_pending=[];total=i+1
     if total%24==0:persist()
     assert not (O/'STOP_AFTER_SAVE').exists() and time.monotonic()-start<cfg['wall_seconds']-120
   persist();assert all(torch.equal(v.detach().cpu(),original[k]) for k,v in w.items()) and env._integrated_contact.tick-tick==8*steps and env._feedback_100hz_tick-fb==2*steps;h=health.write();assert learning_health_pass(h);put('FINAL.json',dict(epoch=time.time(),passed_execution_not_skill=True,source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],steps=steps,callbacks=8*steps,num_envs=88,actor9_STD_literal_exact=True,zero_optimizer=True,health=h,artifacts=artifacts,no_graduation_claim_before_CPU=True))
  finally:persist()
 except BaseException:
  error=traceback.format_exc()
  if physical_pending:np.savez_compressed(O/'FAILED_CURRENT_CONTROL_PHYSICS.npz',**{k:np.stack([r[k] for r in physical_pending]) for k in physical_pending[0]})
  put('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=error,completed_controls=total,no_replay=True))
 finally:
  if env is not None:
   try:env.close()
   except BaseException:put('ENV_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  put('APP_CLOSING.json',dict(epoch=time.time(),original_error=bool(error)));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  if not (O/'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').exists():put('WORKER_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  raise

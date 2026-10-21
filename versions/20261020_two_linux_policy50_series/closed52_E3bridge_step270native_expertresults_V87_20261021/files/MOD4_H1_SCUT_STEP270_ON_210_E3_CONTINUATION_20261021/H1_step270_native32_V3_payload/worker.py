"""Frozen source16 public0/4 jump evaluation; no PPO, scripted jump or added force."""
from pathlib import Path
import hashlib,json,os,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;J=B/'job0';O=B/'out';O.mkdir()
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 cfg=json.loads((B/'FROZEN_CONFIG.json').read_bytes());steps=cfg['steps'];assert steps==480;src=J/'source.pt';assert H(src)==cfg['source_SHA'];put('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),source_SHA=cfg['source_SHA'],steps=steps,no_optimizer=True))
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 old=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in old.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',OWN_E2_H1_KIND='H1_FLAT_PUBLIC_REQUEST',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 runtime=J/'runtime/isaac/mod4';sys.path[:0]=[str(B/'lib'),str(runtime),str(B)];entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','32','--seed','20260928'];ns=runpy.run_path(str(entry),run_name='frozen_H1_configuration_only');env=None;error=None;controls=[];physics=[];artifacts=[];total=0
 try:
  import torch,numpy as np
  import torch.nn.functional as F
  torch.set_num_threads(1);torch.manual_seed(20260928);torch.cuda.manual_seed_all(20260928);torch.set_float32_matmul_precision('highest')
  def forbid(*a,**k):raise RuntimeError('Frozen evaluation forbids optimizer construction')
  torch.optim.Optimizer.__init__=forbid;factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg']
  def small_cfg():
   c=original_cfg();c.scene.num_envs=32;c.seed=20260928;c.sim.device='cuda:0';assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01;c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01}
   for k,v in dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20).items():setattr(c.sim.physics,k,v)
   return c
  import h1_scut_fudan_jump_reward_v1 as scut
  import h1_step270_sdk_runtime_candidate as terrain
  original_reward_configure=scut.configure
  scut.configure=lambda cfg:terrain.configure_rewards(cfg,original_reward_configure)
  factory.__globals__['Mod4Env']=terrain.H1Step270Env
  factory.__globals__['Mod4EnvCfg']=small_cfg;env=factory();assert env.num_envs==32 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4;env._physics_action_delay.queue.control_us=10000
  from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
  probe=isolated_actual_SDK_dt_probe(env);put('ACTUAL_STEP270_TERRAIN_AND_REWARD_TASK.json',dict(**env.step270_geometry_receipt,new_task_terrain_reward_phase_migration=True,original_actor35_critic38_action6=True,no_original_H1_scope_claim=True));put('ISOLATED_ORIGINAL_SDK_REWARD_READBACK_ACTUAL.json',probe)
  from h1_takeoff_progress_environment_v2 import tensor
  cpu=lambda x:tensor(x).detach().cpu().numpy().copy();robot=env.scene['robot'];env.h1_witness_ids=torch.arange(32,device=env.device);env.h1_capture=True
  from clock_training_health import ClockTrainingHealth,learning_health_pass
  health=ClockTrainingHealth(env,O)
  # Read-only COM observations, evaluated after the original physical callback.
  old_update=env.scene.update
  def update(dt):
   old_update(dt)
   if env.h1_stepping and env.h1_physical_rows:
    row=env.h1_physical_rows[-1];mass=tensor(robot.root_view.get_masses()).to(env.device);local=tensor(robot.data.body_com_pos_b);world=tensor(robot.data.body_com_pose_w)[...,:3];assert world.shape==(32,31,3) and mass.shape==(32,31);row.update(actual_body_COM_world=world.clone(),actual_body_COM_local=local.clone(),actual_mass=mass.clone(),whole_robot_COM=(world*mass[...,None]).sum(1)/mass.sum(1,keepdim=True),chassis_COM=world[:,env.h1_body_names.index('chassis')].clone())
  env.scene.update=update;old_term=env.termination_manager.compute
  def term(*a,**k):
   result=old_term(*a,**k)
   if env.h1_stepping and env.h1_control_frame is not None:
    phase=env.h1_phase;env.h1_control_frame.update(age_after=phase.age_control.clone(),ready_before_reset=phase.ready.clone(),attempt_before_reset=phase.attempt.clone(),launched_before_reset=phase.launched.clone(),landed_before_reset=phase.landed.clone(),recovered_before_reset=phase.recovered.clone(),takeoff_count=phase.takeoff_count.clone(),landing_count=phase.landing_count.clone(),recovery_count=phase.recovery_count.clone(),episode=env._sensor_mild.episode.clone())
   return result
  env.termination_manager.compute=term
  from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
  vec=RslRlVecEnvWrapper(env,clip_actions=6.);state=torch.load(src,map_location='cpu',weights_only=False);assert {int(v['step']) for v in state['optimizer_state_dict']['state'].values()}=={cfg['source_Adam']} and len(state['actor_state_dict'])==9;original={k:v.clone() for k,v in state['actor_state_dict'].items()};w={k:v.to(env.device) for k,v in original.items()};assert all(torch.isfinite(v).all() for v in w.values());env.reset();env._h1_publish_external_request();assert not env.h1_phase.age_control.any();obs=vec.get_observations()
  np.savez_compressed(O/'INITIAL_ACTUAL.npz',root13=cpu(robot.data.root_state_w),q30=cpu(robot.data.joint_pos),mass=cpu(robot.root_view.get_masses()),COM_local=cpu(robot.data.body_com_pos_b));put('GEOMETRY_AND_CLOCK_ACTUAL.json',dict(source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],shapes=env.h1_shapes,body_names=env.h1_body_names,contact_names=env.h1_contact_names,witness_ids=list(range(32)),quaternion='XYZW',policy_hz=100,physics_dt=.0025,decimation=4,normal100_request4_next80=True,actual_270mm_vertical_platform=True,new_public4_forward_command_m_s=.8,feedback_hz=100,contact_bin_s=.005,fresh32_seed=20260928,source20k_DR_not_restored=True,no_script_assist_or_added_force=True))
  from nominal_parameter_audit import parameter_audit
  audit=parameter_audit(env);assert audit['profile']=='white_v3' and audit['actual_parameters_pass'];put('INITIAL_PARAMETER_READBACK.json',audit)
  import subprocess
  gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);own=[x for x in gpu.splitlines() if x.split(',')[1].strip()==str(os.getpid())];assert own and all(cfg['GPU_UUID'] in x for x in own);put('ACTUAL_OWN_GPU.json',dict(epoch=time.time(),own=own))
  def persist():
   for values,prefix in ((controls,'CONTROL'),(physics,'PHYSICS')):
    if not values:continue
    p=O/(prefix+'_'+str(sum(x.get('kind')==prefix for x in artifacts)).zfill(4)+'.npz');np.savez_compressed(p,**{k:np.stack([r[k] for r in values]) for k in values[0]});artifacts.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p),kind=prefix,rows=len(values)));values.clear()
   q=O/'VALID_PREFIX_INDEX.json';tmp=q.with_suffix('.tmp');tmp.write_text(json.dumps(dict(epoch=time.time(),controls=total,artifacts=artifacts),indent=2));tmp.replace(q)
  tick=env._integrated_contact.tick;start=time.monotonic()
  try:
   with torch.inference_mode():
    for i in range(steps):
     x=obs['policy'];assert x.shape==(32,35) and torch.isfinite(x).all() and torch.equal(x[:,0],env.h1_phase.public_request().float()*.8) and not x[:,1:3].any();assert torch.equal(x[:,28:35],F.one_hot(env.h1_phase.public_mode(),7).to(x.dtype));raw=x
     for n in (0,2,4,6):
      raw=F.linear(raw,w[f'mlp.{n}.weight'],w[f'mlp.{n}.bias'])
      if n!=6:raw=F.elu(raw)
     policy=cpu(x);action=cpu(raw);env.h1_physical_rows=[];before=env._integrated_contact.tick;obs,reward,done,info=vec.step(raw);assert env._integrated_contact.tick-before==4 and len(env.h1_physical_rows)==4 and torch.isfinite(reward).all();frame=env.h1_control_frame;assert frame is not None
     controls.append(dict(policy=policy,raw_action=action,reward=cpu(reward),done=cpu(done),**{k:cpu(v) for k,v in frame.items()}));physics.extend({k:cpu(v) for k,v in row.items()} for row in env.h1_physical_rows);env.h1_physical_rows=[];total=i+1
     if total%24==0:persist()
     assert not (O/'STOP_AFTER_SAVE').exists() and time.monotonic()-start<cfg['wall_seconds']-120
   persist();assert all(torch.equal(v.detach().cpu(),original[k]) for k,v in w.items()) and env._integrated_contact.tick-tick==4*steps;h=health.write();assert learning_health_pass(h);put('FINAL.json',dict(epoch=time.time(),passed_execution_not_skill=True,source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],steps=steps,callbacks=4*steps,num_envs=32,actor9_STD_literal_exact=True,zero_optimizer=True,health=h,artifacts=artifacts,all_body_COM_and_all34_geometry_saved=True,no_jump_height_or_graduation_claim_before_CPU=True,new_task_native_only_not_learning=True))
  finally:persist()
 except BaseException:
  error=traceback.format_exc()
  if env is not None and env.h1_physical_rows:
   try:np.savez_compressed(O/'FAILED_CURRENT_CONTROL_PHYSICS.npz',**{k:np.stack([cpu(r[k]) for r in env.h1_physical_rows]) for k in env.h1_physical_rows[0]})
   except BaseException:put('FAILED_CURRENT_PHYSICS_SAVE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  put('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=error,completed_controls=total,no_replay=True))
 finally:
  if env is not None:
   try:env.close()
   except BaseException:put('ENV_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  put('APP_CLOSING.json',dict(epoch=time.time(),original_error=bool(error)));ns['app'].close()
 if error:raise RuntimeError('Original frozen H1 evaluation error retained')
if __name__=='__main__':
 try:main()
 except BaseException:
  if not (O/'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').exists():put('WORKER_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  raise

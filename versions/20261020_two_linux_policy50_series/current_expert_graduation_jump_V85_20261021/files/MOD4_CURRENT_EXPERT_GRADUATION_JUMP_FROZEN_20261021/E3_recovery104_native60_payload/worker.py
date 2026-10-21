"""Fresh13 recovery diagnostics on the user-authorized shared GPU; never constructs PPO."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;O=B/'out';O.mkdir();J=B/'job0'
def put(name,v):
 with (O/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 cfg=json.loads((B/'FROZEN_CONFIG.json').read_bytes());a=argparse.Namespace(steps=cfg['steps']);assert a.steps in (60,750);src=J/'source.pt';assert H(src)==cfg['source_SHA'];put('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,steps=a.steps,num_envs=104,source_SHA=cfg['source_SHA'],optimizer_constructed=False,shared_GPU_explicit_human_authority=True))
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 old=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in old.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_SPAWN_GRACE_STEPS='5',MOD4_RESUME_QUEUE_CONTROL_US='20000',OWN_E2_H1_KIND='E3_PUBLIC_RECOVERY',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 runtime=J/'runtime/isaac/mod4';sys.path[:0]=[str(B/'lib'),str(runtime)];entry=runtime/'train_E3_fullstate_v1.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','104','--seed','20260928'];ns=runpy.run_path(str(entry),run_name='frozen_configuration_only');env=None;failed=None
 try:
  import torch,numpy as np
  import torch.nn.functional as F
  torch.set_num_threads(1);torch.manual_seed(20260928);torch.cuda.manual_seed_all(20260928)
  # Only the environment factory is used. The training main/runner/optimizer are never constructed.
  def forbid(*args,**kwargs):raise RuntimeError('Frozen scope forbids optimizer construction or updates')
  torch.optim.Optimizer.__init__=forbid
  original_factory=ns['build_env'];original_class=ns['Mod4EnvCfg']
  def small_cfg():
   c=original_class();c.scene.num_envs=104;c.seed=20260928;c.sim.device='cuda:0'
   caps=dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20)
   for k,v in caps.items():setattr(c.sim.physics,k,v)
   assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01
   c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01}
   return c
  # runpy function globals are kept separately from the returned namespace.
  original_factory.__globals__['Mod4EnvCfg']=small_cfg
  env=original_factory();assert env.num_envs==104 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8
  assert float(env.termination_manager.get_term_cfg('mimic').params['threshold'])==.01 and float(env.termination_manager.get_term_cfg('closure').params['threshold'])==.002
  env._physics_action_delay.queue.control_us=20000
  import subprocess
  compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
  own=[line for line in compute.splitlines() if len(line.split(','))>=2 and line.split(',')[1].strip()==str(os.getpid())]
  assert own and all('GPU-16828f91-2b45-b646-8dc0-9481138e2842' in line for line in own)
  put('ACTUAL_SHARED_GPU_COMPUTE.json',dict(epoch=time.time(),own_compute_rows=own,explicit_shared_GPU=True))
  original_term=env.termination_manager.compute
  def observed_term(*args,**kwargs):
   value=original_term(*args,**kwargs)
   if env.e3_frame is not None:
    env.e3_frame['credited_before_reset']=env.recovery.credited.clone()
    env.e3_frame['stable_units_before_reset']=env.recovery.stable.clone()
   return value
  env.termination_manager.compute=observed_term
  from clock_training_health import ClockTrainingHealth,learning_health_pass
  health=ClockTrainingHealth(env,O)
  from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
  vec=RslRlVecEnvWrapper(env,clip_actions=6.0);s=torch.load(src,map_location='cpu',weights_only=False);assert s['policy_clock']['policy_hz']==50 and {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={cfg['source_Adam']};cpu={k:x.clone() for k,x in s['actor_state_dict'].items()};w={k:x.to(env.device) for k,x in cpu.items()};assert len(w)==9
  def exact():return all(torch.equal(x.detach().cpu(),cpu[k]) for k,x in w.items())
  env.reset();env.e3_reset_enabled=True;env.place_declared_fall(torch.arange(104,device=env.device));env.publish();env.e3_witness=torch.arange(104,device=env.device);env.e3_capture=True
  from h1_fullstate_environment_v1 import tensor as source_tensor
  def cpu_value(x):return source_tensor(x).detach().cpu().numpy().copy()
  robot=env.scene['robot'];initial=dict(root13=cpu_value(robot.data.root_state_w),q30=cpu_value(robot.data.joint_pos),recipe=cpu_value(env.recovery.recipe),mode=cpu_value(env.recovery.mode()))
  np.savez_compressed(O/'INITIAL_ACTUAL.npz',**initial);put('ACTUAL_CONFIG.json',dict(policy_hz=50,physics_dt=.0025,decimation=8,feedback_hz=100,recovery_counter_units_10ms=True,recovery_counter_increment=2,request_seconds=3,stable_seconds=.5,spawn_grace_seconds=.1,fresh104_original13recipes_times8_not_source20k_restore=True,reset=env.e3_reset_receipt,source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],actor9_STD_exact=exact(),no_optimizer=True))
  put('GEOMETRY_ACTUAL.json',dict(shapes=env.e3_shapes,body_names=env.e3_body_names,contact_names=env.e3_contact_names,witness_ids=list(range(104)),quaternion='XYZW',original13poses_per8=True))
  rows=[];physical=[];start=time.monotonic();obs=vec.get_observations();tick0=env._integrated_contact.tick;fb0=env._feedback_100hz_tick
  with torch.inference_mode():
   for i in range(a.steps):
    x=obs['policy'];assert x.shape==(104,35) and torch.isfinite(x).all();raw=x
    for n in (0,2,4,6):
     raw=F.linear(raw,w[f'mlp.{n}.weight'],w[f'mlp.{n}.bias'])
     if n!=6:raw=F.elu(raw)
    policy_read=cpu_value(x);action_read=cpu_value(raw);before=env._integrated_contact.tick;fb=env._feedback_100hz_tick;env.e3_physical.clear();obs,reward,done,info=vec.step(raw);assert env._integrated_contact.tick-before==8 and env._feedback_100hz_tick-fb==2 and len(env.e3_physical)==8 and torch.isfinite(reward).all();frame=env.e3_frame;assert frame is not None
    for f in env.e3_physical:
     physical.append({k:cpu_value(v) for k,v in f.items()});assert all(np.isfinite(z).all() for z in physical[-1].values() if isinstance(z,np.ndarray) and z.dtype.kind in 'fc')
    rows.append(dict(policy=policy_read,raw_action=action_read,reward=cpu_value(reward),done=cpu_value(done),**{k:cpu_value(v) for k,v in frame.items()}));env.e3_frame=None
    if (O/'STOP_AFTER_SAVE').exists():raise RuntimeError('Original source integrity health requested own stop')
    assert time.monotonic()-start<cfg['wall_seconds']-120,'Bounded shared-GPU diagnostic duration exceeded'
  assert exact() and env._integrated_contact.tick-tick0==8*a.steps and env._feedback_100hz_tick-fb0==2*a.steps
  h=health.write();assert learning_health_pass(h)
  np.savez_compressed(O/'CONTROL_ACTUAL.npz',**{k:np.stack([r[k] for r in rows]) for k in rows[0]});np.savez_compressed(O/'PHYSICAL_CALLBACK_ACTUAL.npz',**{k:np.stack([r[k] for r in physical]) for k in physical[0]})
  put('FINAL.json',dict(epoch=time.time(),passed_execution_not_skill=True,source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],controls=a.steps,callbacks=8*a.steps,feedback_samples=2*a.steps,envs=104,zero_optimizer=True,actor9_STD_initial_final_literal_exact=True,physical_and_control_all_rows_saved=True,source_health=h,not_full104_frozen_or_skill_qualification=True,artifacts=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in O.glob('*.npz')]))
 except BaseException:
  failed=traceback.format_exc();put('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=failed,no_optimizer=True,no_qualification_claim=True))
  if 'rows' in locals() and rows:
   np.savez_compressed(O/'FAILED_CONTROL_PREFIX.npz',**{k:np.stack([r[k] for r in rows]) for k in rows[0]})
  if 'physical' in locals() and physical:
   np.savez_compressed(O/'FAILED_PHYSICAL_PREFIX.npz',**{k:np.stack([r[k] for r in physical]) for k in physical[0]})
 finally:
  if env is not None:
   try:env.close()
   except BaseException:put('ENV_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
  put('APP_CLOSING.json',dict(epoch=time.time(),original_error=failed is not None));ns['app'].close()
 if failed:raise RuntimeError('Frozen diagnostic original error preserved')
if __name__=='__main__':
 try:main()
 except BaseException:
  if not (O/'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').exists():put('WORKER_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_replay=True))
  raise

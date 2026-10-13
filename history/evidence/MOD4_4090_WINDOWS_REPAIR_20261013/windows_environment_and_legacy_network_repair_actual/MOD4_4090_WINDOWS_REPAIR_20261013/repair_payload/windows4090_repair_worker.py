"""New Windows4090 scope entrypoint. Parent lease/OSlock required before Kit.

Torch and TensorDict preload occurs before every Isaac import. No installed SDK
file is edited.20k capacities are the frozen original cfg values.
"""
from pathlib import Path
import os,sys,json,time,argparse,traceback,hashlib
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
for name in ('runtime-root','manifest','source-checkpoint','source-sha','output','stop-after-save'):parser.add_argument('--'+name,required=True)
parser.add_argument('--mode',choices=['sdk','native','fullrestore','train'],required=True)
parser.add_argument('--train-seconds',type=int,default=3600);parser.add_argument('--probe-controls',type=int,default=120)
pre,_=parser.parse_known_args();R=Path(pre.runtime_root);C=R/'isaac/mod4';manifest=json.loads(Path(pre.manifest).read_bytes())
assert os.name=='nt' and int(os.environ['MOD4_WINDOWS_GPU_LOCK_PARENT_PID'])==os.getppid(),'leased parent ownership required'
assert manifest['approved_for_new_Windows4090_scope'] and manifest['num_envs']==20000
assert pre.source_sha==manifest['source']['sha256'] and hashlib.sha256(Path(pre.source_checkpoint).read_bytes()).hexdigest()==pre.source_sha
sys.path[:0]=[str(C),str(P),str(R)]
for k,v in manifest['source_environment'].items():
 if k.startswith('RM_'):os.environ[k]=str(v)
os.environ['RM_MOD4_USD']=str(R/'assets/robot.usd');os.environ.pop('RM_RESCUE_DEADLINE',None)
os.environ['ISAACSIM_ACCEPT_EULA']='Y';os.environ['OMNI_KIT_ACCEPT_EULA']='YES'
# Import order is a measured Windows native-crash repair, not an SDK hotpatch.
import torch,tensordict
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(parser);args=parser.parse_args();O=Path(args.output);assert O.is_dir()
def write(name,v):
 p=O/name;b=json.dumps(v,ensure_ascii=False,indent=2).encode();q=p.with_suffix(p.suffix+'.partial')
 with q.open('wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(q,p)
write('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,mode=args.mode,source_SHA=args.source_sha,num_envs=10 if args.mode=='sdk' else 20000,no_PPO_yet=True,new_Windows_backend_scope=True,PhysX_exact_resume=False))
app=None;env=None
try:
 app=AppLauncher(args).app;torch.set_num_threads(1)
 from local_physx_api import install
 install()
 import mod4_task as task
 from retention_learning_env import RetentionLearningEnv
 from wave50_lifetime_runtime import configure_retention
 from e1_terrain_training_health import E1TerrainTrainingHealth,learning_health_pass
 cfg=task.Mod4EnvCfg();cfg.scene.num_envs=10 if args.mode=='sdk' else 20000;cfg.seed=20260928;cfg.sim.device=args.device;configure_retention(cfg)
 capacity_names=('gpu_max_rigid_contact_count','gpu_max_rigid_patch_count','gpu_found_lost_pairs_capacity','gpu_found_lost_aggregate_pairs_capacity','gpu_total_aggregate_pairs_capacity')
 capacities={k:getattr(cfg.sim.physx,k) for k in capacity_names};assert capacities==manifest['admitted_Windows20k_GPU_buffer_capacities'],'reviewed new backend buffer identity'
 write('WINDOWS4090_ORIGINAL_CAPACITY_IDENTITY.json',dict(epoch=time.time(),actual_new_Windows20k_cfg=capacities,original20k_task_constructor_no_capacity_overrides_retained=True,capacity_overrides_applied=False,small128_caps_not_used=True,Linux_old_SDK_capacity_numerical_equivalence_not_claimed=True))
 env=RetentionLearningEnv(cfg=cfg);env.reset();placement=None
 if args.mode=='sdk':
  from wave50_entry_sdk_placement_v2 import prepare,verify
  placement=prepare(env);env.reset();placement=verify(env,placement)
  cmd=env.command_manager.get_term('twist');cmd.set_manual_evaluation_mode()
 else:cmd=env.command_manager.get_term('twist')
 write('INITIALIZED.json',dict(epoch=time.time(),pid=os.getpid(),num_envs=env.num_envs,physics_dt=env.physics_dt,control_dt=env.step_dt,decimation=env.cfg.decimation,obs_dimensions=env.observation_manager.group_obs_dim,assignment_SHA=env.scene.terrain.retention_assignment_sha,backend='Windows-IsaacSim5.1-PhysX2API',physical_engine_equivalence_claimed=False,placement=placement))
 assert env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4
 if args.mode in ('sdk','native'):
  import numpy as np
  health=E1TerrainTrainingHealth(env,O);N=env.num_envs;rows=[];warm=0 if args.mode=='sdk' else 24;timed=300 if args.mode=='sdk' else 120;started=time.time()
  for i in range(warm+timed):
   if args.mode=='sdk':
    cmd.time_left[:]=1e9;cmd.command[:]=0.;cmd.command[:,0]=torch.tensor([.3,-.3,.3,-.3,.3,-.3,.3,-.3,0.,0.],device=env.device);cmd.is_standing_env[:]=False;cmd.is_standing_env[8:]=True
    if hasattr(cmd,'is_heading_env'):cmd.is_heading_env[:]=False
    cmd.is_pure_spin[:]=False;cmd.is_moving_spin[:]=False;cmd.is_transition_spin[:]=False
   command=cmd.command.detach().cpu().numpy().copy();env.step(torch.zeros((N,6),device=env.device));rows.append(command)
   if (i+1)%24==0:write('PROBE_PROGRESS.json',dict(epoch=time.time(),controls=i+1,callbacks=(i+1)*4,no_PPO=True))
  report=health.write();assert learning_health_pass(report)
  if args.mode=='sdk':
   from wave50_entry_sdk_placement_v2 import verify
   # Selected reset is part of this diagnostic scope; physical footprint verified
   # immediately after reset, never treated as route completion.
   selected=torch.tensor([0,3,9],device=env.device);before_episode=env._e1_episode.clone();env._reset_idx(selected);env.scene.write_data_to_sim();env.sim.forward();env.scene.update(env.physics_dt)
   actualq=env.scene['robot'].data.joint_pos[selected];actualq=actualq.torch if hasattr(actualq,'torch') else actualq
   expectedq=env._rough_probe_expected_q[selected];qerror=float((actualq-expectedq).abs().max());assert qerror<=1e-6
   write('SDK_SELECTED_RESET_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),passed=True,env_ids=selected.cpu().tolist(),all30q_requested_and_actual_max_error_rad=qerror,fullpose_reset_receipt=env._rough_probe_reset_receipt,new_RNG_not_claimed_zero_for_this_diagnostic_reset=True,not_route_progress=True))
  raw=O/'PROBE_COMMAND_TRACE.npz';np.savez_compressed(raw,command=np.asarray(rows),warm_controls=warm,timed_controls=timed)
  write('PROBE_COMPLETE.json',dict(epoch=time.time(),pid=os.getpid(),passed=True,mode=args.mode,actual_controls=warm+timed,timed_controls=timed,warm_controls=warm,actual_callbacks=(warm+timed)*4,elapsed_seconds=time.time()-started,health=report,placement=placement,command_trace=dict(path=str(raw),sha256=hashlib.sha256(raw.read_bytes()).hexdigest()),diagnostic_fixture_commands_only=args.mode=='sdk',no_PPO=True,backend_scope_admission_not_fullroute_or_training=True))
 else:
  from windows4090_training_runtime import restore_and_run
  restore_and_run(env,args,O,write)
 env.close();app.close()
 write('WORKER_RETURNED_NATURALLY.json',dict(epoch=time.time(),pid=os.getpid(),no_PPO=args.mode!='train'))
except BaseException:
 write('ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),prePPO=not (O/'WINDOWS4090_PPO_PROGRESS.json').exists(),progress=json.loads((O/'WINDOWS4090_PPO_PROGRESS.json').read_bytes()) if (O/'WINDOWS4090_PPO_PROGRESS.json').exists() else None))
 print(traceback.format_exc(),flush=True)
 # An own failed prelearn scene is never reused. Preserve before failedKit teardown.
 os._exit(1)

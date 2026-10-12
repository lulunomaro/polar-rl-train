from pathlib import Path
import os,sys,json,time,argparse,traceback,hashlib
D=Path(__file__).resolve().parent;C=D/'runtime/isaac/mod4';sys.path[:0]=[str(C),str(D)]
RUN=D.parent/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'
parser=argparse.ArgumentParser();parser.add_argument('--num_envs',type=int,default=128);parser.add_argument('--output',required=True);parser.add_argument('--probe-controls',type=int,default=120);parser.add_argument('--mode',choices=['probe','fullrestore','train'],default='probe');parser.add_argument('--train-seconds',type=int,default=1800)
envvars=json.loads((RUN/'run_manifest.json').read_bytes())['env']
for k,v in envvars.items():
 if k.startswith('RM_'):os.environ[k]=str(v)
os.environ['RM_MOD4_USD']=str(D/'runtime/assets/robot.usd');os.environ.pop('RM_RESCUE_DEADLINE',None)
os.environ['ISAACSIM_ACCEPT_EULA']='Y';os.environ['OMNI_KIT_ACCEPT_EULA']='YES'
import torch,tensordict
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(parser);args=parser.parse_args();O=Path(args.output);O.mkdir(parents=True,exist_ok=True)
def write(name,v):
 p=O/name;b=json.dumps(v,ensure_ascii=False,indent=2).encode();q=p.with_suffix(p.suffix+'.partial')
 with q.open('wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(q,p)
write('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,num_envs=args.num_envs,source_SHA='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a',no_PPO=True))
app=None;env=None
try:
 app=AppLauncher(args).app
 import torch
 torch.set_num_threads(1)
 from local_physx_api import install
 install()
 import mod4_task as task
 from retention_learning_env import RetentionLearningEnv
 from wave50_lifetime_runtime import configure_retention
 cfg=task.Mod4EnvCfg();cfg.scene.num_envs=args.num_envs;cfg.seed=20260928;cfg.sim.device=args.device
 configure_retention(cfg)
 capacities=dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20)
 original_capacities={k:getattr(cfg.sim.physx,k) for k in capacities}
 for k,v in capacities.items():setattr(cfg.sim.physx,k,v)
 write('LOCAL_SMALL_BATCH_CAPACITY_ADMISSION.json',dict(epoch=time.time(),num_envs=args.num_envs,original=original_capacities,local=capacities,solver_clock_geometry_DR_thresholds_unchanged=True,overflow_is_strict_failure=True,performance_gain_not_yet_measured=True))
 # Original solver32/4/2.5ms are defined by frozen task and USD actuator configuration.
 env=RetentionLearningEnv(cfg=cfg)
 env.reset()
 write('INITIALIZED.json',dict(epoch=time.time(),pid=os.getpid(),step_dt=env.step_dt,physics_dt=env.physics_dt,physics_handles_decimation=env._physics_handles_decimation,obs_dimensions=env.observation_manager.group_obs_dim,geometry_assignment_SHA=env.scene.terrain.retention_assignment_sha,device=str(env.device),source_projection_pending=True))
 if args.mode=='probe':
  for i in range(args.probe_controls):
   env.step(torch.zeros((args.num_envs,6),device=env.device))
   if (i+1)%20==0:write('PROBE_PROGRESS.json',dict(epoch=time.time(),controls=i+1,callbacks=env._integrated_contact.tick))
  write('PROBE_COMPLETE.json',dict(epoch=time.time(),passed=True,pid=os.getpid(),actual_controls=args.probe_controls,closed_loop_max_m=getattr(env,'_mod4_max_closure',None),mimic_max_rad=getattr(env,'_mod4_max_mimic',None),not_PPO_or_formal_source_fullrestore=True))
 else:
  from local_training_runtime import restore_and_run
  restore_and_run(env,args,O,write)
 env.close();app.close()
except BaseException:
 write('ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),pid=os.getpid(),prePPO=True))
 print(traceback.format_exc(),flush=True)
 # A failed initialization is never learned from. Preserve errors before failedKit teardown.
 os._exit(1)

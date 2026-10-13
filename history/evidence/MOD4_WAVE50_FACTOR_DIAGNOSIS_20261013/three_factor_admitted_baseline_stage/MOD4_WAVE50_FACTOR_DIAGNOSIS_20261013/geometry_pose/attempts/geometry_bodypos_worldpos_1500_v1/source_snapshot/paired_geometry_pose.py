"""Frozen-only matched factor worker, one root-issued lease and native GPU lock.

Each invocation creates an independent scene at identical seed/environment count.
Actual DR readback/assignments must be CPU compared across invocations before
calling the results paired. No optimizer, saved-source restoration, or learning.
"""
from pathlib import Path
import argparse, os, sys, json, time, hashlib, traceback, msvcrt
D=Path(__file__).resolve().parent
W=D.parents[1]
L=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
C=L/'runtime/isaac/mod4'
LOCK=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock'
RUN=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'
p=argparse.ArgumentParser()
p.add_argument('--checkpoint',required=True);p.add_argument('--checkpoint-sha',required=True)
p.add_argument('--output',required=True);p.add_argument('--lease',required=True)
p.add_argument('--case-id',required=True);p.add_argument('--steps',type=int,default=1500)
p.add_argument('--num-envs',type=int,default=8);p.add_argument('--seed',type=int,default=20260928)
p.add_argument('--body-sign',type=int,choices=(-1,1),default=1)
p.add_argument('--world-sign',type=int,choices=(-1,1),default=1)
p.add_argument('--pitch-deg',type=float,default=0.);p.add_argument('--roll-deg',type=float,default=0.)
p.add_argument('--height-m',type=float,default=.25)
p.add_argument('--entry-margin',type=float,default=.4)
p.add_argument('--sensor-clean',action='store_true')
p.add_argument('--feedback-current',action='store_true');p.add_argument('--policy-factor',action='store_true')
p.add_argument('--speed',type=float,default=.3)
p.add_argument('--headless',action='store_true');p.add_argument('--device',default='cuda:0')
args=p.parse_args();O=Path(args.output);ck=Path(args.checkpoint)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert args.steps in (120,300,600,1500) and 2<=args.num_envs<=40
assert args.seed==20260928 and abs(args.pitch_deg)<=5 and abs(args.roll_deg)<=5
assert args.height_m in (.23,.25,.27) and .4<=args.entry_margin<=.85 and 0<args.speed<=.3
assert sum((bool(args.sensor_clean),bool(args.feedback_current),bool(args.policy_factor)))<=1,'One diagnostic factor at a time'
assert sha(ck)==args.checkpoint_sha
lease=json.loads(Path(args.lease).read_bytes())
assert lease['case_id']==args.case_id and lease['checkpoint_sha256']==args.checkpoint_sha
assert lease['GPU_lease_granted_by_root'] is True and lease['owned_training_actual_exit_and_shared_lock_free_verified'] is True
assert lease['worker_sha256']==sha(__file__)
assert lease['factor_runtime_sha256']==sha(D/'factor_runtime.py')
case_parameters={k:getattr(args,k) for k in ('steps','num_envs','seed','body_sign','world_sign','pitch_deg','roll_deg','height_m','entry_margin','sensor_clean','feedback_current','policy_factor','speed','headless','device')}
assert lease['case_parameters']==case_parameters,'Every diagnostic factor must match the root lease'
assert not O.exists(),'Output directory is immutable and once-only'
guard=LOCK.open('r+b');guard.seek(0);msvcrt.locking(guard.fileno(),msvcrt.LK_NBLCK,1)
O.mkdir(parents=True)
def save(name,v):
 q=O/name;assert not q.exists();q.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
save('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,lease=lease,source_sha256=args.checkpoint_sha,worker_sha256=sha(__file__),runtime_sha256=sha(D/'factor_runtime.py'),case_parameters=case_parameters,no_PPO=True,native_shared_OSlock_acquired=True))
for k,v in json.loads((RUN/'run_manifest.json').read_bytes())['env'].items():
 if k.startswith('RM_'):os.environ[k]=str(v)
os.environ['RM_MOD4_USD']=str(L/'runtime/assets/robot.usd')
os.environ['RM_MILD_DR_PROFILE']='white_v3'
os.environ.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
sys.path[:0]=[str(C),str(L),str(D)]
# This import order is required by the actual successful local v7/v10 branch.
import torch,tensordict,numpy as np
from isaaclab.app import AppLauncher
app=None;env=None
try:
 app=AppLauncher(headless=args.headless,device=args.device).app
 torch.set_num_threads(1)
 from local_physx_api import install
 install()
 from factor_runtime import run_factor
 run_factor(args,O,L,save)
 app.close()
 save('EXIT_NATURAL.json',dict(epoch=time.time(),pid=os.getpid(),exit_code=0,app_close_returned=True,no_PPO=True))
except BaseException:
 save('ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),no_PPO=True))
 print(traceback.format_exc(),flush=True)
 os._exit(1)
finally:
 guard.seek(0);msvcrt.locking(guard.fileno(),msvcrt.LK_UNLCK,1);guard.close()

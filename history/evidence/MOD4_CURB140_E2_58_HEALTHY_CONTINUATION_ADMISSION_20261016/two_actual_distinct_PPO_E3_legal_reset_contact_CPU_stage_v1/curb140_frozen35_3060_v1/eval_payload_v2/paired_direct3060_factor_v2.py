"""3060 direct-local frozen-policy factor; explicit new native modular backend."""
from pathlib import Path
import argparse,os,sys,json,time,hashlib,traceback,msvcrt,importlib.metadata as metadata
D=Path(__file__).resolve().parent;L=D/'runtime';C=L/'isaac/mod4'
LOCK=Path('D:/MOD4_async_eval/worker.lock')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser()
for key in ('checkpoint','checkpoint-sha','output','lease','case-id'):p.add_argument('--'+key,required=True)
p.add_argument('--steps',type=int,default=1500);p.add_argument('--num-envs',type=int,default=8);p.add_argument('--seed',type=int,default=20260928)
p.add_argument('--body-sign',type=int,choices=(-1,1),default=1);p.add_argument('--world-sign',type=int,choices=(-1,1),default=1)
p.add_argument('--feedback-current',action='store_true');p.add_argument('--headless',action='store_true');p.add_argument('--device',default='cuda:0')
a=p.parse_args();O=Path(a.output);ck=Path(a.checkpoint)
assert a.steps in (120,1500) and a.num_envs==8 and a.seed==20260928
assert a.checkpoint_sha=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4' and H(ck)==a.checkpoint_sha
lease=json.loads(Path(a.lease).read_bytes())
assert lease['target_host']=='10.24.4.249' and lease['namespace']=='MOD4_3060_DIRECT_FACTOR_20261013'
assert lease['GPU_lease_granted_by_root'] is True and lease['actual_shared_slot_idle_verified'] is True
assert lease['case_id']==a.case_id and lease['checkpoint_sha256']==a.checkpoint_sha
assert lease['worker_sha256']==H(__file__) and lease['factor_runtime_sha256']==H(D/'factor_runtime_3060_native_v2.py')
case={k:getattr(a,k) for k in ('steps','num_envs','seed','body_sign','world_sign','feedback_current','headless','device')}
assert lease['case_parameters']==case
manifest=json.loads((D/'SOURCE_BUNDLE_V2_MANIFEST.json').read_bytes())
assert lease['source_bundle_manifest_sha256']==H(D/'SOURCE_BUNDLE_V2_MANIFEST.json')
for row in manifest['file_rows']:assert H(D/row['relative'])==row['sha256']
sdk=json.loads((D/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for row in sdk['files']:assert H(row['path'])==row['sha256']
assert not O.exists() and LOCK.exists()
f=LOCK.open('r+b');f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
O.mkdir(parents=True)
def save(name,value):
 q=O/name;assert not q.exists()
 with q.open('wb') as out:out.write(json.dumps(value,ensure_ascii=False,indent=2).encode());out.flush();os.fsync(out.fileno())
save('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,case=case,lease=lease,no_PPO=True,
 frozen_fixture_original_white3_initialization=True,not_training_fullstate_resume=True,shared_original_OS_lock_acquired=True))
for k,v in json.loads((D/'provenance/original459_run_manifest.json').read_bytes())['env'].items():
 if k.startswith('RM_'):os.environ[k]=str(v)
os.environ['RM_MOD4_USD']=str(L/'assets/robot.usd');os.environ['RM_MILD_DR_PROFILE']='white_v3'
os.environ.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
sys.path[:0]=[str(C),str(D)]
# TD before Isaac is deliberate; native3060 arrays are xyzw and ProxyArray.
import torch,tensordict,numpy as np
from isaaclab.app import AppLauncher
app=None
try:
 app=AppLauncher(headless=a.headless,device=a.device).app;torch.set_num_threads(1)
 from factor_runtime_3060_native_v2 import run_factor
 a.pitch_deg=0.;a.roll_deg=0.;a.height_m=.25;a.entry_margin=.4;a.speed=.3;a.sensor_clean=False;a.policy_factor=False
 run_factor(a,O,D,save);app.close()
 save('EXIT_NATURAL.json',dict(epoch=time.time(),pid=os.getpid(),exit_code=0,app_close_returned=True,no_PPO=True))
except BaseException:
 save('ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),no_PPO=True))
 print(traceback.format_exc(),flush=True);os._exit(1)
finally:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1);f.close()

"""Prepared isolated3060 frozen E2 case. Actual root lease required; never trains."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback,msvcrt,importlib.metadata as metadata
D=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();p=argparse.ArgumentParser()
for name in ('checkpoint','checkpoint-sha','output','lease','case-id','shared-payload'):p.add_argument('--'+name,required=True)
p.add_argument('--router-mode',choices=['single_eval'],required=True);p.add_argument('--kind',choices=['world'],required=True);p.add_argument('--steps',type=int,choices=[120,1500],required=True);p.add_argument('--num-envs',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--headless',action='store_true');p.add_argument('--device',default='cuda:0');a=p.parse_args();O=Path(a.output);lease=json.loads(Path(a.lease).read_bytes());manifest_path=D/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V6.json';m=json.loads(manifest_path.read_bytes());assert a.steps in (120,1500) and a.num_envs==88 and a.seed==20260928 and a.headless and a.device=='cuda:0';assert a.checkpoint_sha==m['source']['SHA']==H(a.checkpoint)
assert lease['target_host']=='10.24.4.249' and lease['namespace']=='E2_CLOSED109_SIGNED4_FROZEN_V6_20261017' and lease['GPU_lease_granted_by_root'] is True and lease['actual_shared_slot_idle_verified'] is True;assert lease['case_id']==a.case_id and lease['checkpoint_sha256']==a.checkpoint_sha and lease['worker_sha256']==H(__file__) and lease['source_manifest_sha256']==H(manifest_path)
case=dict(router_mode=a.router_mode,kind=a.kind,steps=a.steps,num_envs=a.num_envs,seed=a.seed,headless=a.headless,device=a.device);assert lease['case_parameters']==case
if a.steps==1500:assert lease['actual_same_source_native120_independent_CPU_passed'] is True and lease['native120_actual_exit_childrenout_lockfree'] is True
for row in m['files']:q=D/row['relative'];assert q.resolve().is_relative_to(D.resolve()) and q.stat().st_size==row['bytes'] and H(q)==row['SHA'],row['relative']
sdk=json.loads((D/'frozen_shared/EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for row in sdk['files']:assert H(row['path'])==row['sha256']
lock=Path('D:/MOD4_async_eval/worker.lock');assert lock.exists() and not O.exists();f=lock.open('r+b');f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);O.mkdir(parents=True)
def save(name,value):
 q=O/name;assert not q.exists()
 with q.open('xb') as out:out.write(json.dumps(value,indent=2).encode('utf8'));out.flush();os.fsync(out.fileno())
save('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,case=case,lease=lease,no_PPO=True,source_actor9_GPU_only_no_gate_or_full20k_DRrestore=True))
for key,value in m['env'].items():os.environ[key]=str(value)
L=D/'frozen_shared/runtime';C=L/'isaac/mod4';os.environ.update(RM_MOD4_USD=str(L/'assets/robot.usd'),RM_MILD_DR_PROFILE='white_v3',RM_SPIN_MAX_RAD_S='4.0',RM_SPIN_WORLD_PROGRESS_M_S='0.5',ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES');sys.path[:0]=[str(D),str(C),str(L),str(D/'frozen_shared')];app=None;context={};failed=None
try:
 import torch,tensordict,numpy as np
 torch.set_num_threads(1)
 from e2_closed109_source_guard_v1 import validate_E2_source
 source=torch.load(a.checkpoint,map_location='cpu',weights_only=False);validate_E2_source(source);assert not torch.cuda.is_initialized();del source
 from isaaclab.app import AppLauncher
 app=AppLauncher(headless=True,device=a.device).app
 from retention_native_witness_v8 import CONTEXT
 context=CONTEXT;context.update(save=save,output_dir=str(O),router_mode='single_eval');a.dr_profile='white_v3';a.speed_limit=1.5;a.ramp_suite=False;a.reset_smoke=False;a.max_rate=4.;a.contact_readback=True;a.manual_reference=False;a.output=str(O/'probe.json')
 from retention_world_native_v8 import run_world
 run_world(a);app.close();app=None;save('EXIT_NATURAL.json',dict(epoch=time.time(),pid=os.getpid(),exit_code=0,no_PPO=True))
except BaseException:
 failed=traceback.format_exc();save('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=failed,no_PPO=True,no_qualification_claim=True))
 try:
  from e2_frozen_prefix_guard_v4 import save_failed_prefix
  save_failed_prefix(context,O,save)
 except BaseException:save('FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_failure_preserved=True))
finally:
 if app is not None:
  try:app.close()
  except BaseException:save('APP_CLOSE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()))
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1);f.close()
if failed:raise RuntimeError('Original frozen-evaluation failure saved before SDK close')

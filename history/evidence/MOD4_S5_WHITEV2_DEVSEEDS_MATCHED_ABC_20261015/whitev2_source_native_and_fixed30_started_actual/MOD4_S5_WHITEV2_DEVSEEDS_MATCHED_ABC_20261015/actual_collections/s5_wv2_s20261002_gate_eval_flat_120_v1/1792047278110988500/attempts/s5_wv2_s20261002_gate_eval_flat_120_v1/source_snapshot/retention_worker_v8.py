"""New single-case native3060 frozen evaluation; root lease is required."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback,msvcrt,importlib.metadata as metadata
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser()
for k in ('checkpoint','checkpoint-sha','output','lease','case-id','shared-payload'):p.add_argument('--'+k,required=True)
p.add_argument('--router-mode',required=True,choices=('single_eval','rule_eval','gate_eval'));p.add_argument('--kind',required=True,choices=('flat','spin','world'));p.add_argument('--steps',type=int,choices=(120,1500),default=1500)
p.add_argument('--num-envs',type=int,required=True);p.add_argument('--seed',type=int,default=20261002)
p.add_argument('--headless',action='store_true');p.add_argument('--device',default='cuda:0');a=p.parse_args()
O=Path(a.output);S=Path(a.shared_payload);L=S/'runtime';C=L/'isaac/mod4';lease=json.loads(Path(a.lease).read_bytes());manifest=json.loads((D/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())
assert a.seed in (20261002,20261003) and a.num_envs=={'flat':80,'spin':88,'world':88}[a.kind]
assert a.checkpoint_sha in {x['sha256'] for x in manifest['sources'].values()} and H(a.checkpoint)==a.checkpoint_sha
assert lease['target_host']=='10.24.4.249' and lease['namespace']=='MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015'
assert lease['GPU_lease_granted_by_root'] is True and lease['actual_shared_slot_idle_verified'] is True
assert lease['worker_sha256']==H(__file__) and lease['case_id']==a.case_id and lease['checkpoint_sha256']==a.checkpoint_sha
case=dict(router_mode=a.router_mode,kind=a.kind,steps=a.steps,num_envs=a.num_envs,seed=a.seed,headless=a.headless,device=a.device)
assert lease['case_parameters']==case
for name in ('retention_native_witness_v8.py','retention_'+a.kind+'_native_v8.py','raycast_hit_serializer_v5.py'):assert H(D/name)==lease['port_sources_sha256'][name]
for row in manifest['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
assert H(manifest['v5_sdk_primary_stub']['actual_installed_stub_path'])==manifest['v5_sdk_primary_stub']['actual_sha256']
assert H(manifest['V7_actual_native_binding']['path'])==manifest['V7_actual_native_binding']['sha256']
for row in manifest['package_files_v8']:assert H(D/row['relative'])==row['sha256'],row['relative']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for row in sdk['files']:assert H(row['path'])==row['sha256']
lock=Path('D:/MOD4_async_eval/worker.lock');assert lock.exists() and not O.exists()
f=lock.open('r+b');f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);O.mkdir(parents=True)
def save(name,value):
 q=O/name;assert not q.exists()
 with q.open('xb') as out:out.write(json.dumps(value,ensure_ascii=False,indent=2).encode('utf8'));out.flush();os.fsync(out.fileno())
save('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,case=case,lease=lease,no_PPO=True,only_actor_loaded=a.router_mode=='single_eval',declared_eval_mode=a.router_mode,trained_gate_source148_pair_modes_only=True,new_fixture_no_training_DR_restore=True,OS_shared_lock_acquired=True))
for key,value in json.loads((S/'provenance/original459_run_manifest.json').read_bytes())['env'].items():
 if key.startswith('RM_'):os.environ[key]=str(value)
os.environ['RM_MOD4_USD']=str(L/'assets/robot.usd');os.environ['RM_MILD_DR_PROFILE']='white_v2'
os.environ.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
sys.path[:0]=[str(C),str(L),str(S),str(D)]
import torch,tensordict,numpy as np
from isaaclab.app import AppLauncher
app=None
try:
 app=AppLauncher(headless=a.headless,device=a.device).app;torch.set_num_threads(1)
 from retention_native_witness_v8 import CONTEXT
 CONTEXT['save']=save;CONTEXT['output_dir']=str(O);CONTEXT['router_mode']=a.router_mode
 a.dr_profile='white_v2';a.speed_limit=1.5;a.ramp_suite=True;a.reset_smoke=False;a.max_rate=4*np.pi;a.contact_readback=True;a.manual_reference=False
 a.output=str(O/'probe.json')
 module=__import__('retention_'+a.kind+'_native_v8');getattr(module,'run_'+a.kind)(a)
 app.close();save('EXIT_NATURAL.json',dict(epoch=time.time(),pid=os.getpid(),exit_code=0,app_close_returned=True,no_PPO=True))
except BaseException:
 save('ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),no_PPO=True));print(traceback.format_exc(),flush=True);os._exit(1)
finally:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1);f.close()

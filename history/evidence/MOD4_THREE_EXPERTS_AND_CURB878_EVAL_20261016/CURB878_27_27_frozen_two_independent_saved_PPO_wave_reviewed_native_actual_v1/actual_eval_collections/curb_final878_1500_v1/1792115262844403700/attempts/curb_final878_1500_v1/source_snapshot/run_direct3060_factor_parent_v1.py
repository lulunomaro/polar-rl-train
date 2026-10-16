"""Per-case isolated parent records exact launch, guardian and full exit cost."""
from pathlib import Path
import argparse,json,sys,subprocess,time,os,hashlib,psutil,shutil
D=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--lease',required=True);p.add_argument('--attempt',required=True);args=p.parse_args()
A=Path(args.attempt);assert not A.exists(),'Case parent is once-only';lease_path=Path(args.lease);lease=json.loads(lease_path.read_bytes())
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert lease['worker_sha256']==H(D/'paired_direct3060_factor_v1.py') and lease['factor_runtime_sha256']==H(D/'factor_runtime_3060_native_v1.py')
assert lease['GPU_lease_granted_by_root'] is True and lease['actual_shared_slot_idle_verified'] is True
A.mkdir(parents=True);O=A/'output';snap=A/'source_snapshot';snap.mkdir()
files=[]
for src in list(D.glob('*.py'))+[D/'SOURCE_BUNDLE_MANIFEST.json',D/'EXPECTED_INSTALLED_3060_BACKEND.json',lease_path]:
 dest=snap/src.name;shutil.copy2(src,dest);assert H(src)==H(dest);files.append(dict(source=str(src),path=str(dest),bytes=dest.stat().st_size,sha256=H(dest)))
def write(name,value):
 q=A/name;b=json.dumps(value,ensure_ascii=False,indent=2).encode('utf8');tmp=q.with_suffix(q.suffix+'.partial')
 with tmp.open('wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(tmp,q)
write('SOURCE_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),files=files,prelaunch=True,source_bundle_manifest_SHA=H(D/'SOURCE_BUNDLE_MANIFEST.json'),installed_backend_source_SHA_verified_by_worker=True))
params=lease['case_parameters'];argv=[sys.executable,str(D/'paired_direct3060_factor_v1.py'),'--checkpoint',lease['checkpoint_path'],'--checkpoint-sha',lease['checkpoint_sha256'],'--output',str(O),'--lease',str(lease_path),'--case-id',lease['case_id']]
for key,value in params.items():
 flag='--'+key.replace('_','-')
 if isinstance(value,bool):
  if value:argv.append(flag)
 else:argv.extend((flag,str(value)))
started=time.time();log=(A/'worker.log').open('wb');child=subprocess.Popen(argv,cwd=str(D),stdout=log,stderr=subprocess.STDOUT)
creation=psutil.Process(child.pid).create_time()
write('DISPATCH_RECEIPT.json',dict(epoch=started,parent_pid=os.getpid(),parent_creation=psutil.Process().create_time(),child_pid=child.pid,child_creation=creation,argv=argv,cwd=str(D),lease=str(lease_path),checkpoint_sha256=lease['checkpoint_sha256'],frozen_only=True,no_PPO=True))
while child.poll() is None:
 try:process=psutil.Process(child.pid);actual=dict(pid=child.pid,creation=process.create_time(),argv=process.cmdline(),cwd=process.cwd())
 except psutil.Error:actual=None
 write('GUARDIAN_CURRENT.json',dict(epoch=time.time(),parent_pid=os.getpid(),child_actual=actual,no_signals_sent=True))
 time.sleep(15)
log.close();ended=time.time()
write('PARENT_EXIT_RECEIPT.json',dict(epoch=ended,parent_pid=os.getpid(),child_pid=child.pid,child_creation=creation,exit_code=child.returncode,started_epoch=started,unique_actual_parent_load_run_save_exit_seconds=ended-started,
 no_PPO=True,canonical_budget_written=False,original_error_present=(O/'ORIGINAL_ERROR.json').exists(),complete_data_contract_present=(O/'COMPLETE_ACTUAL.json').exists(),natural_app_close_present=(O/'EXIT_NATURAL.json').exists()))
print(json.dumps(json.loads((A/'PARENT_EXIT_RECEIPT.json').read_bytes())),flush=True)
sys.exit(child.returncode)

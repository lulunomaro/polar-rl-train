"""Single new metadata attempt, full source snapshot, no canonical accounting."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,subprocess,shutil,psutil
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--lease',required=True);p.add_argument('--attempt',required=True);a=p.parse_args()
lease_path=Path(a.lease);lease=json.loads(lease_path.read_bytes())
manifest_path=D/'RETENTION_PLANE_METADATA_CPU_MANIFEST_V7.json';manifest=json.loads(manifest_path.read_bytes())
A=Path(a.attempt);assert not A.exists()
assert lease['worker_sha256']==H(D/'retention_plane_metadata_worker_v7.py') and lease['GPU_lease_granted_by_root'] is True
assert lease['namespace']==manifest['target_namespace'] and lease['case_parameters']['requested_controls']==0
A.mkdir(parents=True);snap=A/'source_snapshot';snap.mkdir();sources=[]
for source,relative in [(D/row['relative'],row['relative']) for row in manifest['package_files']]+[(manifest_path,manifest_path.name),(lease_path,'LEASE_ACTUAL.json')]:
 dst=snap/relative;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dst);assert H(dst)==H(source)
 sources.append(dict(source=str(source),path=str(dst),sha256=H(dst),bytes=dst.stat().st_size))
def save(name,value):
 q=A/name;tmp=q.with_suffix(q.suffix+'.partial')
 with tmp.open('wb') as f:f.write(json.dumps(value,indent=2).encode('utf8'));f.flush();os.fsync(f.fileno())
 os.replace(tmp,q)
save('SOURCE_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),files=sources,prelaunch=True))
argv=[sys.executable,str(D/'retention_plane_metadata_worker_v7.py'),'--output',str(A/'output'),
      '--lease',str(lease_path),'--case-id',lease['case_id'],'--shared-payload',lease['shared_payload_target'],
      '--xy-input',lease['source_positions_path']]
for key,value in lease['case_parameters'].items():
 flag='--'+key.replace('_','-')
 if isinstance(value,bool):
  if value:argv.append(flag)
 else:argv.extend((flag,str(value)))
started=time.time();log=(A/'worker.log').open('xb')
child=subprocess.Popen(argv,cwd=str(D),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
creation=psutil.Process(child.pid).create_time()
save('DISPATCH_RECEIPT.json',dict(epoch=started,parent_pid=os.getpid(),parent_creation=psutil.Process().create_time(),
     child_pid=child.pid,child_creation=creation,argv=argv,cwd=str(D),lease=str(lease_path),no_PPO=True,
     requested_evaluation_controls=0))
while child.poll() is None:
 try:
  proc=psutil.Process(child.pid);identity=dict(pid=child.pid,creation=proc.create_time(),argv=proc.cmdline(),cwd=proc.cwd())
 except psutil.Error:identity=None
 save('GUARDIAN_CURRENT.json',dict(epoch=time.time(),child_actual=identity,no_signal_sent=True));time.sleep(15)
log.close();ended=time.time();O=A/'output'
save('PARENT_EXIT_RECEIPT.json',dict(epoch=ended,started_epoch=started,parent_pid=os.getpid(),child_pid=child.pid,
     child_creation=creation,exit_code=child.returncode,unique_actual_parent_load_run_save_exit_seconds=ended-started,
     no_PPO=True,canonical_budget_written=False,requested_evaluation_controls=0,
     original_error_present=(O/'ORIGINAL_ERROR.json').exists(),complete_data_contract_present=(O/'COMPLETE_ACTUAL.json').exists(),
     natural_app_close_present=(O/'EXIT_NATURAL.json').exists(),old_V6_fullcase_grade_changed=False))
sys.exit(child.returncode)

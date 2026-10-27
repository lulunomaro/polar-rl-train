"""Actual unused E0 source/SDK CPU installation; no Task, GO or account writer."""
from pathlib import Path
import hashlib,importlib.util,json,shlex,sys,tarfile,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent
A=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/night_frozen_experts_PPO50_gas400_adaptation_20261027'
N=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89B_20261027';R=N/'reports'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89b/e0'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,x):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
PRE='''from pathlib import Path
import psutil,fcntl,json,hashlib,shutil,subprocess
B=Path(v['root']);assert not B.exists() and B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve())
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['remaining_training_seconds']>86412.86069250107
for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (C.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert shutil.disk_usage(Path('/home/lc01/Zonglin Li/zonglin2/tasks')).free>25*1024**3 and psutil.virtual_memory().available>32*1024**3
g=v['gpu'];line=subprocess.check_output(['nvidia-smi','-i',g,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',g,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==g and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and g not in apps
B.mkdir(parents=True);assert C.read_bytes()==raw
print(json.dumps(dict(epoch=__import__('time').time(),newroot=str(B),canonical_None=True,remaining_snapshot=c['remaining_training_seconds'],C_SHA=hashlib.sha256(raw).hexdigest(),owner_locks_free=True,selected_GPU_UUID=g,free_MiB=int(line[2]),selected_compute_UUID_rows=0,no_unknown_PID_identity=True,no_Task_GO_or_budget_write=True)))
'''
VERIFY='''from pathlib import Path
import json,tarfile,hashlib,shutil
B=Path(v['root']);archive=B/'SOURCE_PAYLOAD.tar';assert hashlib.sha256(archive.read_bytes()).hexdigest()==v['archive_SHA']
with tarfile.open(archive,'r') as tf:
 for member in tf.getmembers():assert member.isfile() and (B/member.name).resolve().is_relative_to(B.resolve())
 tf.extractall(B,filter='data')
for r in v['rows']:
 p=B/r['relative'];assert p.is_file() and p.stat().st_size==r['bytes']
 with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 assert h==r['SHA'],r['relative']
assert shutil.disk_usage(B).free>25*1024**3
print(json.dumps(dict(all_payload_files_fullSHA_verified=True,files=len(v['rows']),payload_postcopy_free_bytes=shutil.disk_usage(B).free,no_Task_or_GO=True)))
'''
def main():
 assert not N.exists();N.mkdir();R.mkdir()
 put('E0_V89B_SOURCE_INSTALL_CONSUMED_ACTUAL.json',dict(epoch=time.time(),new_purpose='Actual E0 PPO50 gas400 source/SDK admission on remote4090 host, CPU only',worker_v1_original16GiB_refusal_preserved=True,worker_V2_only_disk8_literal=True,no_Task_GO_or_budget_write=True))
 index_path=A/'E0_FROZEN_MINIMUM_ADMISSION_INDEX_v1.json';assert H(index_path)=='e093760087e2aafaac3f973bb8aed725529dd90d2732c1586beec705d5fd5574'
 index=json.loads(index_path.read_bytes());rows=[]
 def add(p,rel,expected=None,size=None):
  p=Path(p);assert p.is_file() and not p.is_symlink();assert '..' not in Path(rel).parts
  if size is not None:assert p.stat().st_size==size
  digest=expected or H(p)
  if p.suffix.lower() not in ('.pt','.usd','.npz'):assert H(p)==digest
  rows.append(dict(local_path=str(p),relative=rel,bytes=p.stat().st_size,SHA=digest))
 for r in index['runtime']:add(r['path'],'runtime/'+r['relative'],r['SHA'],r['bytes'])
 for r in index['binary_dependencies']:
  if r['required_for_E0']:add(r['local_path'],r['installed_relative'],r['SHA'],r['bytes'])
 r=index['typed_source_model'];add(r['path'],'source/E0_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt',r['SHA'],r['bytes'])
 r=index['original_run_manifest'];add(r['path'],'original_run_manifest.json',r['SHA'],r['bytes'])
 add(A/'E0_PPO50_gas400_finite_worker_v3_original_resource_exact.py','E0_PPO50_gas400_finite_worker_v1.py','1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152')
 r=index['SDK_CPU_admission'];add(r['path'],'E0_target_source_SDK_CPU_admission_v1.py',r['SHA'],r['bytes'])
 archive=N/'SOURCE_PAYLOAD.tar'
 with tarfile.open(archive,'w') as tf:
  for r in rows:tf.add(r['local_path'],arcname=r['relative'],recursive=False)
 manifest=dict(epoch=time.time(),root=ROOT,rows=rows,archive=dict(path=str(archive),bytes=archive.stat().st_size,SHA=H(archive)),source_only=True,worker_content_V2_installed_at_fixed_entry_name=True)
 put('E0_V89B_ACTUAL_INSTALL_PAYLOAD_MANIFEST.json',manifest)
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('E0_sourceSDK_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  put('E0_V89B_ACTUAL_PREINSTALL_RESOURCE_AND_SOLE72_ACCOUNT.json',d.code(c,d.PY72,PRE,dict(root=ROOT,gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'),timeout=60))
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:sf.put(str(archive),ROOT+'/SOURCE_PAYLOAD.tar')
  finally:sf.close()
  put('E0_V89B_ACTUAL_POSTCOPY_FULLSOURCE_SHA_ADMISSION.json',d.code(c,d.PY72,VERIFY,dict(root=ROOT,rows=rows,archive_SHA=manifest['archive']['SHA']),timeout=90))
  command="CUDA_VISIBLE_DEVICES='' "+shlex.quote(d.PY72)+' -u -B '+shlex.quote(ROOT+'/E0_target_source_SDK_CPU_admission_v1.py')+' --job-root '+shlex.quote(ROOT)
  i,o,e=c.exec_command(command,timeout=240);i.channel.shutdown_write();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status()
  put('E0_V89B_ACTUAL_SOURCE_SDK_CPU_PROCESS_RETURNED.json',dict(epoch=time.time(),returncode=rc,stdout=stdout,stderr=stderr,command=command,no_GO=True))
  # Always preserve original small error files before interpreting rc.
  sf=c.open_sftp()
  try:
   errors=[]
   for name in sf.listdir(ROOT):
    if name.startswith('E0_SOURCE_SDK_CPU_') and name.endswith('.json'):
     with sf.open(ROOT+'/'+name,'rb') as f:raw=f.read()
     assert len(raw)<4000000
     with (R/name).open('xb') as f:f.write(raw)
     errors.append(dict(path=ROOT+'/'+name,local_path=str(R/name),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
  finally:sf.close()
  put('E0_V89B_ACTUAL_SOURCE_CPU_ERRORS_OR_REPORTS_TRANSFERRED.json',dict(files=errors,actual_process_returned=True))
  assert rc==0,(stdout,stderr)
  proof=json.loads((R/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json').read_bytes());assert proof['passed'] and proof['worker_SHA']=='1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152'
  result=dict(actual_finite_returned=True,actual_target_source_SDK_CPU_passed=True,actual_GPU_PPO_GO_still_pending=True,source_CPU_SHA=H(R/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json'),root=ROOT,source_SHA=proof['source_SHA'],worker_V2_SHA=proof['worker_SHA'],no_Task_GO_or_account_write=True)
  put('E0_V89B_REMOTE4090_HOST_ACTUAL_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('E0_V89B_SOURCE_SDK_CPU_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_GO_no_budget_write_no_retry=True));raise

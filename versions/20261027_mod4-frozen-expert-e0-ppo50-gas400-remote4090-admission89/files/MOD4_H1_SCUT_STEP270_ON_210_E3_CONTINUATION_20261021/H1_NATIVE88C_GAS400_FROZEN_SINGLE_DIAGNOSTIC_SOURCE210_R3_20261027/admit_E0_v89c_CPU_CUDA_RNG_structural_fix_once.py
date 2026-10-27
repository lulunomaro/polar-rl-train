"""New CPU admission purpose; reuse verified89B source, preserve its false/error."""
from pathlib import Path
import importlib.util,json,hashlib,shlex,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent
A=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/night_frozen_experts_PPO50_gas400_adaptation_20261027'
N=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027';R=N/'reports'
OLD='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89b/e0'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/e0'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,x):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
COPY='''from pathlib import Path
import hashlib,shutil,json,psutil,fcntl,subprocess
B=Path(v['root']);old=Path(v['old']);owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks')
assert not B.exists() and B.resolve().is_relative_to(owned.resolve()) and old.is_dir()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None and c['remaining_training_seconds']>86412.86069250107
for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (C.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert shutil.disk_usage(owned).free>25*1024**3 and psutil.virtual_memory().available>32*1024**3
g='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',g,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',g,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==g and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and g not in apps
B.mkdir(parents=True);copies=[]
for r in v['rows']:
 if r['relative']=='E0_target_source_SDK_CPU_admission_v1.py':continue
 p=old/r['relative'];dest=B/r['relative'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==r['bytes'] and dest.resolve().is_relative_to(B.resolve())
 a=p.stat();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);b=p.stat()
 assert (a.st_size,a.st_mtime_ns,a.st_ino)==(b.st_size,b.st_mtime_ns,b.st_ino)
 with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 assert digest==r['SHA'],r['relative'];copies.append(r['relative'])
assert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw
print(json.dumps(dict(epoch=__import__('time').time(),all_verified89B_source_copies_fullSHA_passed=True,copied=len(copies),canonical_unchanged=True,canonical_None=True,remaining_snapshot=c['remaining_training_seconds'],selected_GPU_UUID=g,free_MiB=int(line[2]),selected_compute_UUID_rows=0,no_unknown_PID_identity=True,postcopy_free_bytes=shutil.disk_usage(B).free,no_Task_GO_or_writer=True)))
'''
def main():
 assert not N.exists();N.mkdir();R.mkdir()
 put('E0_V89C_CPU_ADMISSION_NEW_PURPOSE_CONSUMED_ACTUAL.json',dict(epoch=time.time(),prior89B_newtyped_initial_CPU_load_count=1,prior89B_generator_device_reader_error_retained=True,newpurpose='Exact CPU CUDA-generator structural admission fix; actual GPU restoration still required',newtyped_model_one_necessary_reload_after_old_process_exit=True,no_original_frozen_model_reread_or_GPU=True))
 old_local=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89B_20261027/reports'
 prior=json.loads((old_local/'E0_V89B_ACTUAL_SOURCE_SDK_CPU_PROCESS_RETURNED.json').read_bytes());assert prior['returncode']!=0
 rows=json.loads((old_local/'E0_V89B_ACTUAL_INSTALL_PAYLOAD_MANIFEST.json').read_bytes())['rows']
 admission=A/'E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py';assert H(admission)=='d0522290c92cb6a0506dd5269b7f40f2a6052d6d84200c4a0f11fda91ba31663'
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('E0_89c_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  put('E0_V89C_ACTUAL_COPY_RESOURCE_SOURCE_SHA_RECEIPT.json',d.code(c,d.PY72,COPY,dict(root=ROOT,old=OLD,rows=rows),timeout=90))
  sf=c.open_sftp()
  try:sf.put(str(admission),ROOT+'/E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py')
  finally:sf.close()
  verify=d.code(c,d.PY72,"from pathlib import Path;import hashlib,json;p=Path(v['p']);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==v['SHA'];print(json.dumps(dict(installed_CPU_source_SHA=h)))",dict(p=ROOT+'/E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py',SHA=H(admission)),timeout=30)
  put('E0_V89C_INSTALLED_NEW_CPU_SOURCE_SHA_ACTUAL.json',verify)
  cmd="CUDA_VISIBLE_DEVICES='' "+shlex.quote(d.PY72)+' -u -B '+shlex.quote(ROOT+'/E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py')+' --job-root '+shlex.quote(ROOT)
  i,o,e=c.exec_command(cmd,timeout=240);i.channel.shutdown_write();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status()
  put('E0_V89C_ACTUAL_SOURCE_SDK_CPU_PROCESS_RETURNED.json',dict(epoch=time.time(),returncode=rc,stdout=stdout,stderr=stderr,command=cmd,no_Task_GO=True))
  sf=c.open_sftp();transferred=[]
  try:
   for name in sf.listdir(ROOT):
    if name.startswith('E0_SOURCE_SDK_CPU_') and name.endswith('.json'):
     with sf.open(ROOT+'/'+name,'rb') as f:b=f.read()
     assert len(b)<4000000
     with (R/name).open('xb') as f:f.write(b)
     transferred.append(dict(path=ROOT+'/'+name,local_path=str(R/name),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
  finally:sf.close()
  put('E0_V89C_CPU_REPORTS_AND_ORIGINAL_ERRORS_TRANSFERRED_ACTUAL.json',dict(files=transferred,actual_process_returned=True))
  assert rc==0,(stdout,stderr)
  proof=json.loads((R/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json').read_bytes());assert proof['passed'] and proof['worker_SHA']=='1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152'
  result=dict(actual_finite_returned=True,actual_source_SDK_CPU_passed=True,source_CPU_SHA=H(R/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json'),source_SHA=proof['source_SHA'],worker_V3_SHA=proof['worker_SHA'],root=ROOT,actual_CUDA_restore_PPO_signed_GO_pending=True,no_GPU_Task_GO_or_budget_writer=True)
  put('E0_V89C_ACTUAL_REMOTE4090_SOURCE_SDK_CPU_ADMITTED_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E0_V89C_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_automatic_retry_or_GO=True));raise

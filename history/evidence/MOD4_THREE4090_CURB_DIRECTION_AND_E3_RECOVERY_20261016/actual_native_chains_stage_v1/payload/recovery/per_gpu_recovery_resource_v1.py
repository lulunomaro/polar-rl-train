"""Actual GPU1 lock and one explicitly known GPU0 owner; never bypass unknown locks."""
from pathlib import Path
import os,json,time,hashlib,fcntl,subprocess
def owners(st,raw):
 out=[]
 for line in raw.splitlines():
  b=line.split()
  if len(b)<6 or '->' in b:continue
  try:d=b[5].split(':');same=int(d[0],16)==os.major(st.st_dev) and int(d[1],16)==os.minor(st.st_dev) and int(d[2])==st.st_ino
  except (ValueError,IndexError):continue
  if same:out.append(int(b[4]))
 return out
def acquire(B):
 import psutil
 root=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(root.resolve());lock=(root/'state/e3_public_recovery_gpu1_v1.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);globalfile=(root/'state/finite_environment_validation.lock').open('rb+');proof={}
 try:
  try:fcntl.flock(globalfile,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:
   actual=owners(os.fstat(globalfile.fileno()),Path('/proc/locks').read_text());assert actual==[3122980],actual;p=psutil.Process(actual[0]);old=root/'tasks/MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016/e2_from58_plus75_same4_continuation_v2';manifest=old/'CONTINUATION_COMPLETE_MANIFEST_V2.json';assert abs(p.create_time()-1792148612.54)<.1 and str(old/'e2_single_original_canonical_owner_node_v2.py') in p.cmdline() and hashlib.sha256(manifest.read_bytes()).hexdigest()=='c933f3cfa0d5ca3d780eab930738e37dde66ca728c702d6933e4acc5e2a3ed6c';task=json.loads((old/'job0/TASK.json').read_bytes());assert task['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842';proof=dict(known_existing_GPU0_owner=actual[0],creation=p.create_time(),argv=p.cmdline(),manifest_SHA=hashlib.sha256(manifest.read_bytes()).hexdigest(),actual_proc_fcntl_device_inode_verified=True)
  else:fcntl.flock(globalfile,fcntl.LOCK_UN);proof=dict(original_global_actual_fcntl_free=True,new_explicit_per_GPU_lock_contract=True)
 finally:globalfile.close()
 proof.update(epoch=time.time(),own_GPU1_fcntl_actual_held=True,own_pid=os.getpid(),own_creation=psutil.Process().create_time(),own_root=str(B),no_other_job_signal_or_global_lock_change=True,compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode());(B/'GPU1_ACTUAL_RESOURCE_COSCHEDULING_CONTRACT.json').write_text(json.dumps(proof,indent=2));return lock

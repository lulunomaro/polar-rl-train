"""Original selected private/shared locks and4090 resource floors, UUID only."""
from pathlib import Path
import fcntl,json,psutil,shutil,subprocess,time
from E0_single72_protocol_v1 import validate_spec,PRIVATE_LOCK,GPU,require
def acquire(spec,B):
 validate_spec(spec);B=Path(B).resolve();owned=Path('/home/lc01/Zonglin Li/zonglin2')
 require(B.is_relative_to(owned),'owned controller namespace')
 lock=Path(PRIVATE_LOCK).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  with (owned/'state/finite_environment_validation.lock').open('rb+') as shared:
   fcntl.flock(shared,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(shared,fcntl.LOCK_UN)
  apps=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
  require(GPU not in apps,'selected GPU has another compute task; untouched')
  line=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();v=[x.strip() for x in line.split(',')]
  require(v[0]==GPU and v[1]=='NVIDIA GeForce RTX 4090' and int(v[2])>15669,'original4090 floor')
  ram=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free;require(ram>8*1024**3 and disk>25*1024**3,'original normalPPO resource floors')
  p=B/'E0_ACTUAL_PRIVATE_SHARED_RESOURCE_ACQUIRED.json'
  with p.open('x') as f:json.dump(dict(epoch=time.time(),GPU_UUID=GPU,private_lock=PRIVATE_LOCK,actual_private_GPU_fcntl_acquired=True,shared_validation_brief_only=True,selected_compute_UUID_rows=0,GPU_line=line,RAM_available=ram,durable_free=disk,no_unknown_PID_inspection=True,no_account_write=True),f,indent=2)
  return lock
 except BaseException:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();raise

from pathlib import Path
import os,json,time,fcntl,subprocess,psutil
def acquire(spec,B):
 key=spec['key'];old=Path(spec['previous_runtime_root']);source=key=='h1';owned=Path('/mnt/mod4_linux_durable_20261013') if source else Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and old.resolve().is_relative_to(owned.resolve())
 exitrow=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());assert exitrow['actual_all_own_children_waited'] and exitrow['validation_fcntl_released_if_acquired'];terminal=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert terminal['returncode']==0 and terminal['final']['passed']
 path=Path(json.loads((old/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').read_bytes())['path']) if source else owned/'state'/('three_expert_v2_'+spec['GPU_UUID']+'.lock');assert path.resolve().is_relative_to(owned.resolve())
 alive=[]
 for p in psutil.process_iter(['pid','create_time','cmdline']):
  try:
   if p.pid!=os.getpid() and any(s.startswith(str(old)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
  except psutil.Error:pass
 assert not alive,alive;lock=path.open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  if not source:
   with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode()
  if source:assert not compute.strip(),compute
  (B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),previous_root=str(old),actual_previous_scope_all_children_out=True,actual_private_GPU_fcntl_acquired=True,path=str(path),original_validation_global_free_if72=True,compute_snapshot=compute,other_process_untouched=True),indent=2));return lock
 except BaseException:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();raise

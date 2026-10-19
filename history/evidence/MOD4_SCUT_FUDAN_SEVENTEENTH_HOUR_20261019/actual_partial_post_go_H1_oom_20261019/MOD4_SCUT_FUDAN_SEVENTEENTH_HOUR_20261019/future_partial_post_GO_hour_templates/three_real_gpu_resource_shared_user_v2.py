"""Same real private-GPU locks, brief shared admission, original memory and durable guards."""
from pathlib import Path
import os,json,time,fcntl,subprocess,psutil,shutil
def acquire(spec,B):
 owned=Path('/mnt/mod4_linux_durable_20261013' if spec['execution_backend']=='source210' else '/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve());old=Path(spec['previous_runtime_root']);assert old.resolve().is_relative_to(owned.resolve());kind=spec['previous_exit_kind']
 if kind=='node':
  e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['returncode']==0 and r['final']['passed'] and not r['errors']
 elif kind=='native_only':
  e=json.loads((old/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json').read_bytes());assert e['all_actual_own_GPU_children_waited'] and e['private_GPU_fcntl_released_if_acquired'] and e['passed_native_CPU'] and not e['original_error']
 elif kind=='observation':
  e=json.loads((old/'OBSERVATION_PARENT_EXIT_ACTUAL.json').read_bytes());assert e['actual_child_waited'] and e['returncode']==0 and not (old/'full1500_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').exists()
 else:raise AssertionError(kind)
 own=[]
 for p in psutil.process_iter(['pid','cmdline','create_time']):
  try:
   if p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
  except psutil.Error:pass
 failed=spec.get('previous_failed_preGO_runtime_root')
 if failed:
  q=Path(failed);assert q.resolve().is_relative_to(owned.resolve());fe=json.loads((q/'NODE_EXIT_ACTUAL.json').read_bytes());fr=json.loads((q/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert fe['actual_all_own_children_waited'] and fe['validation_fcntl_released_if_acquired'] and fr['phase']=='admission' and fr['original_error'] and fr['worker'] is None and not (q/'job0/GO_PRODUCTION.json').exists() and not (q/'GO_PRODUCTION.json').exists() and not (q/'job0/production').exists()
  for p in psutil.process_iter(['pid','cmdline']):
   try:
    if p.pid!=os.getpid() and any(x.startswith(str(q)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
   except psutil.Error:pass
 failed_post=spec.get('previous_failed_postGO_runtime_root')
 if failed_post:
  q=Path(failed_post);assert q.resolve().is_relative_to(owned.resolve());fe=json.loads((q/'NODE_EXIT_ACTUAL.json').read_bytes());fr=json.loads((q/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert fe['actual_all_own_children_waited'] and fe['validation_fcntl_released_if_acquired'] and fr['phase']=='production' and fr['original_error'] and fr['worker'] is None and fr['final'] is None and fr['latest_save'] is None and not (q/'job0/production/PPO_POSITIVE_CURRENT.json').exists() and (q/'job0/GO_PRODUCTION.json').exists()
  for p in psutil.process_iter(['pid','cmdline']):
   try:
    if p.pid!=os.getpid() and any(x.startswith(str(q)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
   except psutil.Error:pass
 assert not own,own;lock=Path(spec['private_lock']).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  if spec['execution_backend']!='source210':
   with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  else:assert owned.is_mount()
  compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert (spec['key']=='h1' and spec.get('human_explicit_GPU_sharing') is True) or not any(spec['GPU_UUID'] in x for x in compute.splitlines());line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if spec['GPU_UUID'] in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3
  assert (spec['key']!='h1') or int(line.split(',')[-1])>=15669
  (B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').write_text(json.dumps(dict(epoch=time.time(),path=spec['private_lock'],actual_private_GPU_fcntl_acquired=True,previous_root=str(old),actual_previous_scope_all_children_out=True,shared_validation_brief_only=True,compute_snapshot=compute,human_explicit_GPU_sharing=bool(spec.get('human_explicit_GPU_sharing')),other_processes_untouched=True,GPU_line=line,durable_free=shutil.disk_usage(B).free),indent=2));return lock
 except BaseException:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();raise

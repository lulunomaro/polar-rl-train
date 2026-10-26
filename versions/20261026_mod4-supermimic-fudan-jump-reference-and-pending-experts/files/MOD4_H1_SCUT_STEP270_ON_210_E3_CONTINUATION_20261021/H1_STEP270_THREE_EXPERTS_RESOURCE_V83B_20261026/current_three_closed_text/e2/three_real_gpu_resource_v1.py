"""Same real private-GPU locks, brief shared admission, original memory and durable guards."""
from pathlib import Path
import os,json,time,fcntl,subprocess,psutil,shutil
def acquire(spec,B):
 if spec.get('cross_host_qualified_source'):
  import hashlib
  assert spec['key']=='e2' and spec['execution_backend']=='target72' and spec['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
  owned=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve())
  proof=json.loads((B/'SOURCE_ORIGIN_210_C52/CLOSED_MODELS_COST_CPU_ACTUAL.json').read_bytes());model=proof['models']['e2'];terminal=json.loads((B/'SOURCE_ORIGIN_210_C52/NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];exit=json.loads((B/'SOURCE_ORIGIN_210_C52/NODE_EXIT_ACTUAL.json').read_bytes());auth=json.loads((B/'CROSS_HOST_QUALIFIED_SOURCE_AUTH_ACTUAL.json').read_bytes())
  assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
  assert model['final']['twohost_complete_SHA'] and model['final']['SHA']==spec['source_SHA'] and model['Adam']==spec['source_Adamstep'] and model['actual_cost']['duration_bound_passed']
  assert terminal['terminal_all_own_children_waited'] and terminal['returncode']==0 and terminal['final']['passed'] and not terminal['errors'] and terminal['final']['final']['SHA']==spec['source_SHA']
  assert exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired']
  assert auth['approved'] and auth['kind']=='human_three_GPU_existing_E2_cross_host_continuation' and auth['origin_runtime_root']==spec['previous_runtime_root'] and auth['source_SHA']==spec['source_SHA']
  lock=Path(spec['private_lock']).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
   compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(spec['GPU_UUID'] in x for x in compute.splitlines())
   line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if spec['GPU_UUID'] in x)
   assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3
   (B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').write_text(json.dumps(dict(epoch=time.time(),path=spec['private_lock'],actual_private_GPU_fcntl_acquired=True,source_origin_runtime_root=spec['previous_runtime_root'],actual_previous_source_all_children_out=True,source_origin_host='original210',target_host='72',explicit_cross_host_source_proof=True,shared_validation_brief_only=True,GPU_line=line,no_unknown_peer_identity_query=True),indent=2));return lock
  except BaseException:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();raise

 owned=Path('/mnt/mod4_linux_durable_20261013' if spec['execution_backend']=='source210' else '/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve());old=Path(spec['previous_runtime_root']);assert old.resolve().is_relative_to(owned.resolve());kind=spec['previous_exit_kind']
 if kind=='node':
  e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['returncode']==0 and r['final']['passed'] and not r['errors']
 elif kind=='native_only':
  e=json.loads((old/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json').read_bytes());assert e['all_actual_own_GPU_children_waited'] and e['private_GPU_fcntl_released_if_acquired'] and e['passed_native_CPU'] and not e['original_error']
 elif kind=='step270_completed':
  e=json.loads((old/'PARENT_EXIT_ACTUAL.json').read_bytes());p=json.loads((old/'PARENT_COMPLETE_ACTUAL.json').read_bytes());assert e['all_own_children_waited'] and e['own_eval_lease_released'] and p['actual_child_waited'] and p['returncode']==0 and not p['own_timeout'] and p['passed'] and not p['errors']
 elif kind=='observation':
  e=json.loads((old/'OBSERVATION_PARENT_EXIT_ACTUAL.json').read_bytes());assert e['actual_child_waited'] and e['returncode']==0 and not (old/'full1500_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').exists()
 else:raise AssertionError(kind)
 own=[]
 for p in psutil.process_iter(['pid','cmdline','create_time']):
  try:
   if p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
  except psutil.Error:pass
 assert not own,own;lock=Path(spec['private_lock']).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  if spec['execution_backend']!='source210':
   with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  else:assert owned.is_mount()
  compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(spec['GPU_UUID'] in x for x in compute.splitlines());line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if spec['GPU_UUID'] in x);assert int(line.split(',')[-1])>(15669 if spec['key']=='h1' else 7000) and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3
  (B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').write_text(json.dumps(dict(epoch=time.time(),path=spec['private_lock'],actual_private_GPU_fcntl_acquired=True,previous_root=str(old),actual_previous_scope_all_children_out=True,shared_validation_brief_only=True,compute_snapshot=compute,GPU_line=line,durable_free=shutil.disk_usage(B).free),indent=2));return lock
 except BaseException:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();raise

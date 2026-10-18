"""Finish the installed unused target after fixing editable-package SDK discovery only."""
import dispatch_new_fe778_frozen210_native120_after_E2_full_out_once as m
from inventory_current_owned210_storage_readonly_once import *
def main():
 save('H1_FE778_FROZEN210_V1_EDITABLE_LOOKUP_FAILURE_V2_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,first_failure='PathFinder excludes editable meta path finders; found no isaaclab spec',inline_followup_failure='NoneType submodule_search_locations from same wrong lookup',no_prior_parent_worker_native_GO_or_GPU_dispatched=True,original_errors_retained=True,only_lookup_fixed_no_package_or_GPU_replay=True))
 c=None
 try:
  c=a.t.connect();proof=a.code(c,a.t.PY,r'''
from pathlib import Path
import psutil,os,json,time,fcntl,subprocess,shutil
B=Path('/mnt/mod4_linux_durable_20261013/H1f7_1810ev1');assert B.is_dir() and not (B/'native120').exists() and not (B/'frozen_eval_only_CONSOLE.log').exists();alive=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive
with Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
gpu='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e';compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(gpu in s for s in compute.splitlines());assert shutil.disk_usage(B).free>25*1024**3;print(json.dumps(dict(epoch=time.time(),actual_no_previous_worker_or_native=True,real_private_fcntl_free=True,D_free=shutil.disk_usage(B).free,compute=compute)))
''',timeout=60);save('H1_FE778_FROZEN210_V2_ACTUAL_NO_WORKER_NATIVE_LOCK_HANDOFF.json',proof)
  code=m.CPU.replace('from importlib.machinery import PathFinder','from importlib.util import find_spec').replace("PathFinder.find_spec('isaaclab')","find_spec('isaaclab')");cpu=a.code(c,a.t.PY,code,m.TARGET,timeout=180);save('H1_FE778_FROZEN210_V2_ACTUAL_TARGET_SOURCE_INSTALLED_RSL_SDK_CPU.json',cpu)
  manifest=json.loads((m.Q/'H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json').read_bytes());case=dict(router_mode='single_eval',kind='jump',steps=120,num_envs=80,seed=20260928,headless=True,device='cuda:0');lease=dict(target_host='10.24.4.210',execution_backend='linux210_GPU0_frozen_only',GPU_UUID=m.GPU,namespace='H1_HOUR1_FINAL_LINUX210_V1_20261018',GPU_lease_granted_by_root=True,actual_selected_GPU_idle_private_lock_free=True,human_authorized_4090_eval_parallel_training_not_interrupted=True,checkpoint_sha256=manifest['source']['SHA'],checkpoint_path=m.TARGET+'/'+manifest['source_relative'],worker_sha256=m.H(m.Q/'h1_linux4090_frozen_worker_v1.py'),source_manifest_sha256=m.H(m.Q/'H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json'),actual_Linux_backend_SHA=cpu['backend_file_SHA'],case_id='H1_FE778_LINUX210_NATIVE120_1810V1',case_parameters=case)
  parent=m.old.d.launch(a.code,c,a.t.PY,m.TARGET,'h1_linux4090_frozen_parent_v1.py',dict(role='frozen_eval_only',attempt=m.TARGET+'/native120',lease=lease));save('H1_FE778_FROZEN210_V2_NATIVE120_DETACHED_ACTUAL.json',dict(epoch=time.time(),parent=parent,root=m.TARGET,lease=lease,actual_target_CPU_passed=True,no_PPO_or_canonical_charge=True,training_not_stopped_or_signalled=True,native_result_not_yet=True));print(json.dumps(dict(reclaimed210_new_H1_frozen_native_dispatched=True,parent=parent,training_untouched=True)),flush=True)
 finally:
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('H1_FE778_FROZEN210_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_before_new_attempt=True));raise

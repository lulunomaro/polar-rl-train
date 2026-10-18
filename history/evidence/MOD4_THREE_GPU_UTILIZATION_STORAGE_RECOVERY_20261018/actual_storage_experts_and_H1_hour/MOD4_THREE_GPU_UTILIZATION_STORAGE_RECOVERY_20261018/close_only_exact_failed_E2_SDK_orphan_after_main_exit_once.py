"""Reap only a proven orphan of this newly failed diagnostic, never an existing training job."""
from inventory_current_owned210_storage_readonly_once import *
CODE=r'''
from pathlib import Path
import json,time,psutil,os,subprocess,fcntl
B=Path('/mnt/mod4_linux_durable_20261013/E2rf_1810d1');v=json.loads((B/'OBSERVATION_PARENT_CHILD_ACTUAL.json').read_bytes());end=json.loads((B/'OBSERVATION_PARENT_EXIT_ACTUAL.json').read_bytes());assert end['actual_child_waited'] and (B/'native120_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').is_file() and not (B/'native120_observation/COMPLETE_ACTUAL.json').exists()
try:
 main=psutil.Process(v['worker_pid']);assert abs(main.create_time()-v['worker_creation'])>.01 or main.status()==psutil.STATUS_ZOMBIE
except psutil.NoSuchProcess:pass
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();rows=[]
try:
 p=psutil.Process(117732);before=dict(pid=p.pid,creation=p.create_time(),ppid=p.ppid(),status=p.status(),argv=p.cmdline(),cwd=p.cwd());assert abs(before['creation']-1792314420.57)<.01 and before['ppid']==1 and before['cwd']==str(B) and str(B/'linux_expert_frozen_reward_diagnostic_worker_v1.py') in before['argv'] and str(B/'LINUX_EXPERT_OBSERVATION_CONFIG.json') in before['argv'];assert not any(', 117732,' in line for line in compute.splitlines());p.terminate();gone,alive=psutil.wait_procs([p],timeout=8);status=None
 try:status=p.status()
 except psutil.NoSuchProcess:pass
 assert status is None or status==psutil.STATUS_ZOMBIE;rows.append(dict(before=before,exact_own_failed_orphan_SIGTERM_only=True,after_status=status,no_GPU_context_before=True,no_other_process_signalled=True))
except psutil.NoSuchProcess:rows.append(dict(pid=117732,already_actual_out_no_signal=True))
L=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')
with L.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(epoch=time.time(),rows=rows,private_fcntl_actual_free=True,original_failed_main_and_parent_receipts_kept=True,no_H1_writer_GPU_or_budget_mutation=True)))
'''
if __name__=='__main__':
 c=None
 try:
  save('EXACT_FAILED_E2_OWN_ORPHAN_CLOSURE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_transport_owner=True));c=a.t.connect();v=a.code(c,a.t.PY,CODE,timeout=45);save('EXACT_FAILED_E2_OWN_SDK_ORPHAN_CLOSURE_ACTUAL.json',v);print(json.dumps(v),flush=True)
 except BaseException:save('EXACT_FAILED_E2_ORPHAN_CLOSURE_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_other_job_signal_or_budget_change=True));raise
 finally:a.t.close(c)

"""Original210 private finite frozen eval; no owner/GO/account/optimizer."""
from pathlib import Path
import argparse,fcntl,json,os,psutil,shutil,subprocess,time,traceback
from source210_project_launch_helpers_v1 import PY,GPU,own_identity,environment
JOB=Path('/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_Q34_INITIAL24_DEVICE_ROUTE_20261029v2/e3')
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);a=p.parse_args();J=a.job_root.resolve();assert J==JOB
 def put(n,v):
  with (J/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 task=json.loads((J/'FROZEN_CASE_TASK_TEMPLATE.json').read_bytes());assert task['num_envs']==20000 and task['controls']==24 and task['maximum_worker_seconds']==1680 and task['no_optimizer_steps'];me=own_identity(os.getpid());put('OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json',me)
 lock=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+');child=None;worker=None;rc=None;timed=False;error=None
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put('OWN_PRIVATE210_EX_ACQUIRED_FOR_FROZEN_EVAL.json',dict(epoch=time.time(),supervisor=me,no_owner_or_Canonical_lock=True))
  apps=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True,timeout=15);line=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=15).strip();row=[x.strip() for x in line.split(',')]
  assert row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669 and int(row[3])<=30 and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(J).free>25*1024**3
  task['actual_private_GPU_EX_held_by_parent']=True;task['actual_private_parent_identity']=me;put('FROZEN_CASE_TASK.json',task);put('FRESH_PRIVATE_HELD_UUID_ONLY_BEFORE_FROZEN_WORKER.json',dict(epoch=time.time(),GPU_line=line,selected_compute_UUID_rows=apps.splitlines(),user_light_util_le30=True,no_unknown_PID_read=True))
  with (J/'FROZEN_E3_WORKER_COMPLETE_STDOUT_STDERR.log').open('xb') as log:
   child=subprocess.Popen([PY,'-u','-B',str(J/'evaluate_E3_adapted97_source210_initial24_original_queries_once_v1.py'),'--job-root',str(J)],cwd=J,env=environment(J,True),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);worker=own_identity(child.pid);put('OWN_E3_FROZEN_WORKER_EXACT_IDENTITY.json',worker)
   try:rc=child.wait(timeout=1800)
   except subprocess.TimeoutExpired:
    timed=True;assert psutil.Process(child.pid).create_time()==worker['creation'];child.terminate()
    try:rc=child.wait(timeout=30)
    except subprocess.TimeoutExpired:assert psutil.Process(child.pid).create_time()==worker['creation'];child.kill();rc=child.wait(timeout=15)
 except BaseException:error=traceback.format_exc();put('OWN_E3_SUPERVISOR_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error,no_other_process_or_account_write=True))
 finally:
  if child is not None and child.poll() is None:
   child.terminate()
   try:rc=child.wait(timeout=30)
   except subprocess.TimeoutExpired:child.kill();rc=child.wait(timeout=15)
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();out=J/'frozen_regression';result=out/'BOUNDED_FROZEN_E3_N20K_PROFILES_ACTUAL.json';errors=(list(out.glob('*ORIGINAL_ERROR*.json'))+list(out.glob('*EXCEPTION_BEFORE_APP_CLOSE*.json'))) if out.exists() else []
  value=dict(epoch=time.time(),actual_worker_waited=child is not None and child.poll() is not None,returncode=rc,deadline_terminated=timed,supervisor=me,worker=worker,passed_frozen_execution=rc==0 and not timed and error is None and result.exists() and (out/'ACTUAL_NATIVE24_E3_40050_CLOCK_QUEUE.json').exists() and not errors and (out/'E3_INITIAL24_ORIGINAL_QUERY_FINALIZATION_ACTUAL.json').exists() and json.loads((out/'E3_INITIAL24_ORIGINAL_QUERY_FINALIZATION_ACTUAL.json').read_bytes())['diagnostic_valid'],result=json.loads(result.read_bytes()) if result.exists() else None,original_error=error,original_worker_errors=[dict(path=str(q),value=json.loads(q.read_bytes())) for q in errors],private_EX_released=True,no_optimizer_or_authority_write=True,skill_graduation=False,complete_WM_dataset=False)
  put('FROZEN_E3_ORIGINAL_WAITED_TERMINAL_ACTUAL.json',value);put('FROZEN_E3_SUPERVISOR_EXIT_ACTUAL.json',dict(epoch=time.time(),private_EX_released=True,no_account_or_GO=True))
if __name__=='__main__':main()

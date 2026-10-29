"""Own finite evaluation supervisor; source210 private lock, no budget writes."""
from pathlib import Path
import argparse,fcntl,json,os,psutil,shutil,subprocess,time,traceback
GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',required=True,type=Path);a=p.parse_args();J=a.job_root.resolve()
 def put(n,v):
  with (J/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 def ident(pid):
  q=psutil.Process(pid);return dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd())
 task=json.loads((J/'FROZEN_CASE_TASK_TEMPLATE.json').read_bytes());assert task['num_envs']==20000 and task['no_optimizer_steps'];me=ident(os.getpid());put('OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json',me);lock=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+');child=None;own=None;rc=None;timed=False;error=None
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put('OWN_PRIVATE210_EX_ACQUIRED_FOR_FROZEN_EVAL.json',dict(epoch=time.time(),supervisor=me,no_owner_or_shared_Canonical_lock=True))
  apps=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True,timeout=15);line=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=15).strip();row=[x.strip() for x in line.split(',')];assert row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669 and int(row[3])<=30 and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(J).free>25*1024**3
  task['actual_private_GPU_EX_held_by_parent']=True;task['actual_private_parent_identity']=me;put('FROZEN_CASE_TASK.json',task)
  put('FRESH_PRIVATE_HELD_UUID_ONLY_BEFORE_FROZEN_WORKER.json',dict(epoch=time.time(),GPU_line=line,selected_compute_UUID_rows=apps.splitlines(),user_light_util_le30=True,no_unknown_PID_read=True));env=dict(os.environ,CUDA_VISIBLE_DEVICES=GPU,PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  for k,n in {'HOME':'home','TMPDIR':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda'}.items():
   d=J/n;d.mkdir(parents=True,exist_ok=True);env[k]=str(d)
  argv=[task['actual_source210_python'],'-u','-B',str(J/'evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v2_queue_receipt.py'),'--job-root',str(J)]
  with (J/'FROZEN_W35_WORKER_COMPLETE_STDOUT_STDERR.log').open('xb') as log:
   child=subprocess.Popen(argv,env=env,cwd=J,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);own=ident(child.pid);put('OWN_W35_FROZEN_WORKER_EXACT_IDENTITY.json',own)
   try:rc=child.wait(timeout=1800)
   except subprocess.TimeoutExpired:
    timed=True;assert psutil.Process(child.pid).create_time()==own['creation'];child.terminate()
    try:rc=child.wait(timeout=30)
    except subprocess.TimeoutExpired:assert psutil.Process(child.pid).create_time()==own['creation'];child.kill();rc=child.wait(timeout=15)
 except BaseException:error=traceback.format_exc();put('OWN_W35_SUPERVISOR_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error,no_other_process_signal_or_budget_write=True))
 finally:
  if child is not None and child.poll() is None:
   child.terminate()
   try:rc=child.wait(timeout=30)
   except subprocess.TimeoutExpired:child.kill();rc=child.wait(timeout=15)
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();result=J/'frozen_regression/BOUNDED_FROZEN_W35_N20K_PROFILES_ACTUAL.json';original_errors=list((J/'frozen_regression').glob('*ORIGINAL_ERROR*.json')) if (J/'frozen_regression').exists() else []
  value=dict(epoch=time.time(),actual_worker_waited=child is not None and child.poll() is not None,returncode=rc,deadline_terminated=timed,supervisor=me,worker=own if child else None,passed_frozen_execution=rc==0 and not timed and error is None and result.exists() and not original_errors,result=json.loads(result.read_bytes()) if result.exists() else None,original_error=error,original_worker_errors=[dict(path=str(q),value=json.loads(q.read_bytes())) for q in original_errors],private_EX_released=True,no_optimizer_or_authority_write=True,skill_graduation=False,complete_WM_dataset=False)
  put('FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json',value);put('FROZEN_W35_SUPERVISOR_EXIT_ACTUAL.json',dict(epoch=time.time(),private_EX_released=True,no_account_or_GO=True))
if __name__=='__main__':main()

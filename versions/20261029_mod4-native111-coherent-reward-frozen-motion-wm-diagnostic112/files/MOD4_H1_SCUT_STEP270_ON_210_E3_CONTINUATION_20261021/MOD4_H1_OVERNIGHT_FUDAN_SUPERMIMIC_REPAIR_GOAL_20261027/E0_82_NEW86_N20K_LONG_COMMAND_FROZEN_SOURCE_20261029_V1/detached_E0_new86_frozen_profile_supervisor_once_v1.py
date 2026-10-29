"""Own finite profile regression, real original72 authority witness, no learning."""
from pathlib import Path
import argparse,fcntl,json,os,shutil,subprocess,time,traceback
from project_clone_launch_helpers_v1 import environment,argv,own_identity,H
ROOT=Path('/data/robemo/polar-rl-train');GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3'
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--clone-root',type=Path,required=True);a=p.parse_args();J=a.job_root.resolve();D=a.clone_root.resolve();assert J.is_relative_to(ROOT/'evaluation_runs') and D.is_relative_to(ROOT/'runtime_migrations')
 def put(n,v):
  with (J/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 task=json.loads((J/'FROZEN_CASE_TASK_TEMPLATE.json').read_bytes());assert task['num_envs']==20000 and task['controls']==1000 and task['no_optimizer_steps'] and task['target_backend']=='new86';me=own_identity(os.getpid());put('OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json',me)
 locks=ROOT/'state/hardware';assert json.loads((locks/'OWN_NEW86_GPU_LOCK_SCOPE.json').read_bytes())==dict(root=str(ROOT),GPU_UUID=GPU);lock=(locks/(GPU+'.private.lock')).open('rb+');child=None;worker=None;rc=None;timed=False;error=None
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put('OWN_PRIVATE86_EX_ACQUIRED_FOR_FROZEN_EVAL.json',dict(epoch=time.time(),supervisor=me,no_owner_lock_or_ledger_write=True))
  line=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=15).strip();apps=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True,timeout=15);row=[x.strip() for x in line.split(',')]
  available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
  assert available>32*1024**3 and shutil.disk_usage(ROOT).free>25*1024**3
  assert row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669 and int(row[3])<=30
  put('FRESH_PRIVATE_HELD_UUID_ONLY_BEFORE_FROZEN_WORKER.json',dict(epoch=time.time(),GPU_line=line,selected_compute_UUID_rows=apps.splitlines(),user_light_util_at_most30=True,no_unknown_PID_read=True))
  task['actual_private_GPU_EX_held_by_parent']=True;task['actual_private_parent_identity']=me;put('FROZEN_CASE_TASK.json',task)
  command=argv(D,J/'evaluate_E0_adapted82_new86_frozen1000_once_v1.py',['--job-root',str(J)])
  with (J/'FROZEN_E0_WORKER_COMPLETE_STDOUT_STDERR.log').open('xb') as f:
   child=subprocess.Popen(command,cwd=J,env=environment(J,D,True),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);worker=own_identity(child.pid);put('OWN_E0_FROZEN_WORKER_EXACT_IDENTITY.json',worker)
   try:rc=child.wait(timeout=1800)
   except subprocess.TimeoutExpired:
    timed=True
    if child.poll() is None:child.terminate()
    try:rc=child.wait(timeout=30)
    except subprocess.TimeoutExpired:
     if child.poll() is None:child.kill()
     rc=child.wait(timeout=15)
 except BaseException:error=traceback.format_exc();put('OWN_E0_SUPERVISOR_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error,no_unknown_process_or_ledger_IO=True))
 finally:
  if child is not None and child.poll() is None:
   child.terminate()
   try:rc=child.wait(timeout=30)
   except subprocess.TimeoutExpired:child.kill();rc=child.wait(timeout=15)
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();result=J/'frozen_regression/BOUNDED_FROZEN_E0_N20K_PROFILES_ACTUAL.json';out=J/'frozen_regression';errs=list(out.glob('*ORIGINAL_ERROR*.json'))+list(out.glob('*EXCEPTION_BEFORE_APP_CLOSE*.json')) if out.exists() else []
  value=dict(epoch=time.time(),actual_worker_waited=child is not None and child.poll() is not None,returncode=rc,deadline_terminated=timed,supervisor=me,worker=worker,passed_frozen_execution=rc==0 and not timed and error is None and result.exists() and (out/'ACTUAL_NATIVE24_E0_40050_CLOCK_QUEUE.json').exists() and not errs,result=json.loads(result.read_bytes()) if result.exists() else None,original_error=error,original_worker_errors=[dict(path=str(q),value=json.loads(q.read_bytes())) for q in errs],private_EX_released=True,no_optimizer_or_authority_write=True,skill_graduation=False,complete_WM_dataset=False)
  put('FROZEN_E0_ORIGINAL_WAITED_TERMINAL_ACTUAL.json',value);put('FROZEN_E0_SUPERVISOR_EXIT_ACTUAL.json',dict(epoch=time.time(),private_EX_released=True,no_account_or_GO=True))
if __name__=='__main__':main()

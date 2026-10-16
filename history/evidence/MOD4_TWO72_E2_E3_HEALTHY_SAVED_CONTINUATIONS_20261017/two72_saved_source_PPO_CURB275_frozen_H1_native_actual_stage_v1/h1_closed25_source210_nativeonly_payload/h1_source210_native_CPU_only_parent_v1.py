"""Owned native and then independent CPU audit, no learner or canonical permissions."""
from pathlib import Path
import os,time,json,subprocess,traceback,fcntl
B=Path(__file__).resolve().parent;PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def put(p,v):
 p=Path(p);q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def ident(pid):
 import psutil
 p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
def native_and_CPU():
 put(B/'PARENT_IDENTITY.json',ident(os.getpid()));e=dict(os.environ)
 for n in ('home','tmp','cache','config','data'):(B/n).mkdir()
 e.update(HOME=str(B/'home'),TMPDIR=str(B/'tmp'),XDG_CACHE_HOME=str(B/'cache'),XDG_CONFIG_HOME=str(B/'config'),XDG_DATA_HOME=str(B/'data'),CUDA_VISIBLE_DEVICES='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):e.pop(k,None)
 p=subprocess.Popen([PY,'-u','-B',str(B/'h1_ground_prelaunch_v2_native_worker_v1.py')],cwd=B,env=e,stdout=(B/'worker.log').open('xb'),stderr=subprocess.STDOUT,close_fds=True,start_new_session=True);put(B/'WORKER_STARTED_ACTUAL.json',ident(p.pid));rc=p.wait();put(B/'WORKER_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=p.pid,returncode=rc,actual_waited=True));passed=rc==0 and (B/'job0/native/FINAL.json').exists() and not list((B/'job0/native').glob('*ORIGINAL_ERROR*.json'))
 if passed:
  r=subprocess.run([PY,'-B',str(B/'review_H1_prelaunch_v2_native_allrows_CPU_v1.py')],cwd=B,env={**e,'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True);put(B/'NATIVE_CPU_COMMAND_ACTUAL.json',dict(epoch=time.time(),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));passed=r.returncode==0
 put(B/'PARENT_FINAL.json',dict(epoch=time.time(),passed=passed,native_and_CPU_only=True,optimizer_updates=0,canonical_write=False));put(B/'PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),own_child_actual_waited_out=True,no_auto_PPO=True))
def main():
 path=B/'OWN_SOURCE_GPU_NATIVE_ONLY.lock'
 with path.open('xb+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put(B/'OWN_VALIDATION_FCNTL_HELD_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),path=str(path),actual_lock_acquired=True))
  try:native_and_CPU()
  finally:fcntl.flock(lock,fcntl.LOCK_UN);put(B/'OWN_VALIDATION_FCNTL_RELEASED_ACTUAL.json',dict(epoch=time.time(),path=str(path),actual_unlock=True))
if __name__=='__main__':
 assert not (B/'PARENT_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),native_CPU_only=True)),flush=True)
 else:
  os.setsid();fd=os.open(str(B/'parent.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd)
  try:main()
  except BaseException:put(B/'PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_PPO=True));raise

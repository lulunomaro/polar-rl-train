from pathlib import Path
import os,json,time,subprocess,fcntl,traceback
import psutil
B=Path(__file__).resolve().parent;ROOT=Path('/home/lc01/Zonglin Li/zonglin2');PY=ROOT/'run-python.sh'
def put(p,v):
 q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 lock=(ROOT/'state/recovery_schema_v3_gpu1.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put(B/'PARENT_IDENTITY.json',dict(pid=os.getpid(),creation=psutil.Process().create_time(),argv=psutil.Process().cmdline()));e=dict(os.environ)
 for n in ('home','tmp','cache','config','data'):(B/n).mkdir()
 e.update(CUDA_VISIBLE_DEVICES='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',HOME=str(B/'home'),TMPDIR=str(B/'tmp'),XDG_CACHE_HOME=str(B/'cache'),XDG_CONFIG_HOME=str(B/'config'),XDG_DATA_HOME=str(B/'data'),PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');child=None
 try:
  child=subprocess.Popen([str(PY),'-u','-B',str(B/'recovery_worker.py'),'--job','0','--phase','native'],cwd=B,env=e,stdout=(B/'worker.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(B/'WORKER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=child.pid,creation=psutil.Process(child.pid).create_time(),argv=psutil.Process(child.pid).cmdline()));rc=child.wait();put(B/'WORKER_EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=rc,pid=child.pid,actual_waited=True));good=rc==0 and (B/'job0/native/FINAL.json').exists() and not list((B/'job0/native').glob('*ORIGINAL_ERROR*.json'))
  if good:
   v=subprocess.run([str(PY),'-B',str(B/'native_CPU.py'),'--job','0'],cwd=B,env={**e,'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True);put(B/'CPU_ACTUAL_EXIT.json',dict(epoch=time.time(),returncode=v.returncode,stdout=v.stdout,stderr=v.stderr));good=v.returncode==0
  put(B/'PARENT_FINAL.json',dict(epoch=time.time(),passed_native_CPU=good,canonical_write=False,PPO_updates=0,old_other_experts_not_stopped=True))
 finally:
  if child:child.wait()
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();put(B/'PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),own_child_waited_out=True,own_gpu1_fcntl_released=True))
if __name__=='__main__':
 assert not (B/'PARENT_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),native_only=True)),flush=True)
 else:
  os.setsid();f=os.open(str(B/'parent.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
  try:main()
  except BaseException:put(B/'PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise

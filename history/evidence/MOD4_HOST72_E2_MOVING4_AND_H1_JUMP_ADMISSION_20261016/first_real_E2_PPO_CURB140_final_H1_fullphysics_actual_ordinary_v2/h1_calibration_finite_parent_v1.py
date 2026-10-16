"""Own calibration child wait/exit receipt, no learner/canonical write authority."""
from pathlib import Path
import os,sys,json,time,subprocess,traceback
B=Path(__file__).resolve().parent;PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def ident(pid):
 import psutil
 p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
def main():
 put(B/'PARENT_IDENTITY.json',ident(os.getpid()));e=dict(os.environ)
 for n in ('home','tmp','cache','config','data'):(B/n).mkdir()
 e.update(CUDA_VISIBLE_DEVICES='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(B/'home'),TMPDIR=str(B/'tmp'),XDG_CACHE_HOME=str(B/'cache'),XDG_CONFIG_HOME=str(B/'config'),XDG_DATA_HOME=str(B/'data'))
 p=subprocess.Popen([PY,'-u','-B',str(B/'h1_fullphysics_calibration_worker_v1.py')],cwd=B,env=e,stdout=(B/'worker.log').open('xb'),stderr=subprocess.STDOUT,close_fds=True,start_new_session=True);put(B/'WORKER_STARTED_ACTUAL.json',ident(p.pid));rc=p.wait();put(B/'WORKER_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=p.pid,returncode=rc,actual_waited=True));success=rc==0 and (B/'output/COMPLETE_ACTUAL.json').exists() and not list((B/'output').glob('ORIGINAL_ERROR*.json'));put(B/'PARENT_FINAL.json',dict(epoch=time.time(),passed=success,original_failure_preserved=not success,calibration_only_no_PPO_or_canonical_write=True));put(B/'PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),own_child_actual_out=True,returncode=rc))
if __name__=='__main__':
 assert not (B/'PARENT_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),no_learning=True)),flush=True)
 else:
  os.setsid();f=os.open(str(B/'parent.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
  try:main()
  except BaseException:put(B/'PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_learning=True));raise

from pathlib import Path
import sys,json,time,os,subprocess
B=Path(__file__).resolve().parent
def put(n,v):
 p=B/n;t=p.with_suffix('.json.partial');t.write_text(json.dumps(v,indent=2));t.replace(p)
def main():
 import psutil
 put('CPU_PARENT_IDENTITY.json',dict(pid=os.getpid(),creation=psutil.Process().create_time(),argv=psutil.Process().cmdline()))
 e=dict(os.environ);e.update(CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',HOME=str(B.parent/'job0/home'),TMPDIR=str(B.parent/'job0/tmp'),XDG_CACHE_HOME=str(B.parent/'job0/cache'))
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'review_H1_closed_production_all_control_rows_CPU_v1.py')],cwd=B,env=e,stdout=(B/'CPU_STDOUT_STDERR.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 put('CPU_CHILD_IDENTITY.json',dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=psutil.Process(p.pid).cmdline()));rc=p.wait();put('CPU_PARENT_FINAL.json',dict(epoch=time.time(),returncode=rc,child_actual_waited_out=True,passed=rc==0 and (B/'ALL_PRODUCTION_240_CONTROL_ROWS_CPU_ACTUAL.json').exists(),no_GPU_optimizer_budget_or_runtime_mutation=True));put('CPU_PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),child_actual_waited_out=True))
if __name__=='__main__':
 assert not (B/'CPU_PARENT_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_parent_pid=pid,root=str(B))),flush=True)
 else:
  os.setsid();f=os.open(str(B/'CPU_PARENT_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);main()

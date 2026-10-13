from pathlib import Path
import sys,os,json,time,base64,traceback,hashlib
W=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
from reuse_authorized_session_transport import recover
secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
from eval_remote_io import connect_eval
code=r'''
from pathlib import Path
import json,time,os,psutil,msvcrt,hashlib,subprocess,platform
root=Path('D:/MOD4_async_eval');lock=root/'worker.lock'
owned=[]
for p in psutil.process_iter(['name','cmdline','create_time']):
 try:
  argv=p.info['cmdline'] or []
  if any('MOD4_async_eval' in x for x in argv) and p.pid!=os.getpid():
   owned.append(dict(pid=p.pid,name=p.info['name'],creation=p.info['create_time'],argv=argv,cwd=p.cwd(),children=[dict(pid=c.pid,creation=c.create_time(),argv=c.cmdline()) for c in p.children(recursive=True)]))
 except psutil.Error:pass
held=None
if lock.exists():
 try:
  with lock.open('r+b') as f:
   f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
  held=False
 except PermissionError:held=True
 elif_error=None
gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True)
base=root/'closure_episode_clock2500_v15';states=[]
for pat in ('*e1_wave50*state*.json','*E1_WAVE50*json','*ATTENTION*json'):
 for p in list(base.glob(pat))[:12]:
  states.append(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
print(json.dumps(dict(epoch=time.time(),hostname=platform.node(),python=os.sys.executable,SDK_runtime_python_exists=Path('D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe').exists(),actual_owned_processes=owned,shared_worker_lock_path=str(lock),shared_worker_lock_actual_held=held,gpu=dict(returncode=gpu.returncode,stdout=gpu.stdout.strip(),stderr=gpu.stderr.strip()),RAM_available_bytes=psutil.virtual_memory().available,durable_free_bytes=psutil.disk_usage('D:/').free,namespace_state_files=states,no_GPU_launch=True,no_4090_connection=True,no_task_or_worker_mutation=True)))
'''
def main():
 c=connect_eval()
 try:
  enc=base64.b64encode(code.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
  _,o,e=c.exec_command(cmd,timeout=45);raw=o.read();err=e.read();rc=o.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace')
  result=json.loads(raw);result['human_3060_compute_reauthorized']=True;result['local_GPU_train_eval_paused']=True
  p=D/'reports'/('REMOTE3060_COMPUTE_ACTUAL_'+str(time.time_ns())+'.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
 finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('REMOTE3060_CONNECTION_OR_READER_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_remote4090_launch=True)),encoding='utf8');raise

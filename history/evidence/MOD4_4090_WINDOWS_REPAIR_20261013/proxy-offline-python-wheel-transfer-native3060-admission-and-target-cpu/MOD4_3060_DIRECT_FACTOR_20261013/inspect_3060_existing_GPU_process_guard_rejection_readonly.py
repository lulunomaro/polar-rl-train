"""Independent readonly audit of initial compute-process guard rejection."""
from pathlib import Path
import sys,os,json,time,base64,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
CODE=r'''
import json,time,subprocess,psutil
from pathlib import Path
raw=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,timeout=20)
rows=[]
for line in raw.stdout.splitlines():
 if not line.strip():continue
 try:
  pid=int(line.split(',')[0].strip());p=psutil.Process(pid);argv=p.cmdline()
  safe=[];hide=False
  for a in argv:
   if hide:safe.append('[REDACTED]');hide=False;continue
   if any(w in a.lower() for w in ['password','passwd','token=','secret','private key']):safe.append('[REDACTED_ARGUMENT]');hide=True
   else:safe.append(a)
  rows.append(dict(nvidia_line=line,pid=pid,creation=p.create_time(),exe=p.exe(),argv=safe,parent=p.ppid(),cwd=p.cwd()))
 except Exception as e:rows.append(dict(nvidia_line=line,error=type(e).__name__))
gpu=subprocess.run(['nvidia-smi','--query-gpu=index,name,memory.total,memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=20)
ram=psutil.virtual_memory();disk=psutil.disk_usage('D:/')
print(json.dumps(dict(epoch=time.time(),actual_gpu_compute_query_stdout=raw.stdout,returncode=raw.returncode,actual_gpu_processes=rows,
 actual_gpu_memory_query=gpu.stdout,RAM_available=ram.available,durable_D_free=disk.free,newroot_exists=Path('D:/MOD4_async_eval/MOD4_DIRECT_FACTOR_20261013').exists(),
 read_only=True,no_GPU_import_launch_or_signals=True)))
'''
def main():
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
 c=connect_eval()
 try:
  enc=base64.b64encode(CODE.encode()).decode();command='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
  _,o,e=c.exec_command(command,timeout=45);raw=o.read();err=e.read();rc=o.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace')
  a=json.loads(raw);q=R/'DIRECT3060_COMPUTE_GUARD_REJECTION_ACTUAL_PROCESS_REVIEW.json';assert not q.exists();q.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
  print(json.dumps(a,ensure_ascii=False),flush=True)
 finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()

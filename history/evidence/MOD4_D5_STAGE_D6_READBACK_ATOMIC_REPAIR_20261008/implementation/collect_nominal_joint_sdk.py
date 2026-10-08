"""Read the already-published nominal SDK job; no publication, restart or setters."""
from pathlib import Path
import sys,json,hashlib,time,base64
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();job='clk2500-closure-episode-d3-71-d6-nominal-joint-sdk';root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 code="$rows=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});$rows|ConvertTo-Json -Compress -Depth 6"
 _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(code.encode('utf-16le')).decode(),timeout=20)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 rows=json.loads(raw) if raw.strip() else []
 v=dict(epoch=time.time(),job_id=job,process_rows=rows,no_GPU_PPO_publication_budget_or_parameter_write=True)
 with n.open_sftp() as nf,w.open_sftp() as wf:
  for name in ('SPRING_AUDIT_WORKER_STARTED.json','SPRING_AUDIT_WORKER_STATE.json','SPRING_AUDIT_WORKER_ATTENTION.json'):
   try:v[name]=json.loads(wf.open(root+'/'+name).read())
   except FileNotFoundError:v[name]=None
  wp=root+'/jobs/'+job;np='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results/'+job
  try:wf.stat(wp+'/complete.json');nf.stat(np+'/probe.json');nf.stat(np+'/result.json')
  except FileNotFoundError:v['pending']=True
  else:
   dest=R/'windows'/job;dest.mkdir(parents=True,exist_ok=True);files={}
   for name in ('manifest.json','complete.json','probe.json','result.json'):
    b=wf.open(wp+'/'+name).read()
    if name in ('probe.json','result.json'):assert b==nf.open(np+'/'+name).read()
    (dest/name).write_bytes(b);files[name]=dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),automatic_bridge_return_bytes_exact=name in ('probe.json','result.json'))
   v.update(pending=False,files=files,result=json.loads((dest/'result.json').read_text(encoding='utf8')))
  kpath='D:/claude2/fangzhen/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab_physx/isaaclab_physx/assets/articulation/kernels.py'
  b=wf.open(kpath).read();(D/'reviewed_sources/installed_articulation_kernels.py').write_bytes(b)
  v['actual_installed_kernel_source']=dict(path=kpath,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 (R/'D6_NOMINAL_JOINT_SDK_CURRENT.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(v))
finally:w.close();n.close()

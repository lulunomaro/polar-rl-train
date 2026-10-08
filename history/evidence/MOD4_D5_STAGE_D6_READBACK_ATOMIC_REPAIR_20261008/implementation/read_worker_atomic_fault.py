"""Capture actual exited evaluator authority and preserved transient file error."""
from pathlib import Path
import sys,json,time,base64,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 code="$rows=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});$t=Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_spring_audit_review';[pscustomobject]@{rows=$rows;taskState=$t.State.ToString()}|ConvertTo-Json -Compress -Depth 6"
 _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(code.encode('utf-16le')).decode(),timeout=20)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);v['epoch']=time.time()
 with c.open_sftp() as f:
  for name in ('SPRING_AUDIT_WORKER_STARTED.json','SPRING_AUDIT_WORKER_STATE.json','SPRING_AUDIT_WORKER_ATTENTION.json'):
   with f.open(root+'/'+name) as inp:b=inp.read()
   v[name]=json.loads(b)
  for name in ('eval_worker_closure2500.py','eval_worker_spring_audit_review.py'):
   with f.open(root+'/'+name) as inp:b=inp.read()
   (D/'reviewed_sources'/name).write_bytes(b);v[name]=dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 (R/'EVALUATOR_ATOMIC_WRITE_ACTUAL_FAULT.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()

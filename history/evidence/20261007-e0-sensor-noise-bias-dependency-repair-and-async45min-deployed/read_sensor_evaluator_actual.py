"""Read new evaluator identities by creation and path; retain absent probe failures."""
from pathlib import Path
import sys,json,base64
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/sensor_clock1000_v15'
try:
 code=r'''
from pathlib import Path
import json,subprocess,base64,time
D=Path('D:/MOD4_async_eval/sensor_clock1000_v15')
def read(p):return json.loads(p.read_text(encoding='utf8')) if p.is_file() else None
started=read(D/'WORKER_STARTED.json');pid=started['pid']
ps="$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"';$c=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(pid)+"');[pscustomobject]@{process=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=$c|Select-Object ProcessId,CommandLine;newTask=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_sensor').State.ToString();oldTask=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_clock1000').State.ToString()}|ConvertTo-Json -Depth 5 -Compress"
enc=base64.b64encode(ps.encode('utf-16le')).decode();p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert p.returncode==0,p.stderr
jobs=[]
for d in sorted((D/'jobs').glob('*')):
 jobs.append(dict(job_id=d.name,active=read(d/'ACTIVE.json'),complete=read(d/'complete.json'),result=read(d/'result.json'),probe_present=(d/'probe.json').is_file(),
  last_log=(d/'probe.log').read_text(errors='replace').splitlines()[-5:] if (d/'probe.log').exists() else []))
print(json.dumps(dict(epoch=time.time(),worker_started=started,worker_state=read(D/'WORKER_STATE.json'),attention=read(D/'WORKER_ATTENTION.json'),identity=json.loads(p.stdout),jobs=jobs)))
'''
 enc=base64.b64encode(code.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
 _,o,e=c.exec_command(cmd,timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode(errors='replace');v=json.loads(raw)
 (R/'SENSOR_EVALUATOR_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2))
 with c.open_sftp() as s:
  for j in v['jobs']:
   if j['complete']:
    dest=R/'sensor_windows'/j['job_id'];dest.mkdir(parents=True,exist_ok=True)
    for n in ('complete.json','result.json','probe.json','manifest.json','probe.json.error.txt','probe.log'):
     try:s.get(root+'/jobs/'+j['job_id']+'/'+n,str(dest/n))
     except FileNotFoundError:pass
 print(json.dumps(dict(epoch=v['epoch'],identity=v['identity'],attention=v['attention'],jobs=[dict(job_id=j['job_id'],complete=bool(j['complete']),result=j['result'],log_tail=[l[:220] for l in j['last_log']]) for j in v['jobs']])))
finally:c.close()

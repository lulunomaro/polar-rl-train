from pathlib import Path
import sys,json,base64
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/sensor_recovery_clock1000_v15'
try:
 code=r'''
from pathlib import Path
import json,time,base64,subprocess
D=Path('D:/MOD4_async_eval/sensor_recovery_clock1000_v15')
read=lambda p:json.loads(p.read_text(encoding='utf8')) if p.is_file() else None
started=read(D/'WORKER_STARTED.json');pid=started['pid']
ps="$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"';$c=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(pid)+"');[pscustomobject]@{process=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=$c|Select-Object ProcessId,CommandLine;taskState=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_recovery1000').State.ToString()}|ConvertTo-Json -Depth 6 -Compress"
enc=base64.b64encode(ps.encode('utf-16le')).decode();p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert p.returncode==0,p.stderr
jobs=[]
for d in sorted((D/'jobs').glob('*')):
 jobs.append(dict(id=d.name,complete=read(d/'complete.json'),result=read(d/'result.json'),active=read(d/'ACTIVE.json'),probe=read(d/'probe.json') if (d/'complete.json').exists() else None,log_tail=(d/'probe.log').read_text(errors='replace')[-1300:] if (d/'probe.log').exists() else ''))
print(json.dumps(dict(epoch=time.time(),worker=started,identity=json.loads(p.stdout),state=read(D/'WORKER_STATE.json'),attention=read(D/'WORKER_ATTENTION.json'),jobs=jobs)))
'''
 enc=base64.b64encode(code.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
 _,o,e=c.exec_command(cmd,timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'RECOVERY_EVALUATOR_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as ftp:
  for j in v['jobs']:
   if j['complete']:
    target=R/'windows'/j['id'];target.mkdir(parents=True,exist_ok=True)
    for n in ('probe.json','result.json','complete.json','probe.log','manifest.json'):
     try:ftp.get(root+'/jobs/'+j['id']+'/'+n,str(target/n))
     except FileNotFoundError:pass
 print(json.dumps({'epoch':v['epoch'],'identity':v['identity'],'state':v['state'],'attention':v['attention'],'jobs':[{'id':j['id'],'complete':bool(j['complete']),'result':j['result'],'solver_readback':(j['probe'] or {}).get('clock2500_actual_solver'),'log_tail':j['log_tail'] if not j['complete'] else ''} for j in v['jobs']]}))
finally:c.close()

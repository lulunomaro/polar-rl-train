"""Retire only completed idle evaluator task, then start isolated new scope."""
from pathlib import Path
import json,subprocess,base64,time,msvcrt,hashlib
D=Path(__file__).resolve().parent;OLD=D.parent/'sensor_clock1000_v15'
assert D==Path('D:/MOD4_async_eval/sensor_clock2500_solver32_v15')
assert not (D/'HANDOVER.json').exists()
def ps(code):
 enc=base64.b64encode(code.encode('utf-16le')).decode()
 p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
 assert p.returncode==0,p.stdout+p.stderr
 return json.loads(p.stdout) if p.stdout.strip() else None
started=json.loads((OLD/'WORKER_STARTED.json').read_text());state=json.loads((OLD/'WORKER_STATE.json').read_text())
assert state['phase']=='polling' and state['pid']==started['pid'] and time.time()-state['epoch']<90
assert len(state['jobs'])==16 and all((OLD/'jobs'/j/'complete.json').exists() for j in state['jobs'])
code=r"$p=@(Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -like '*sensor_clock1000_v15*'});$rows=@($p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{processes=$rows;taskState=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_sensor').State.ToString()}|ConvertTo-Json -Depth 6 -Compress"
before=ps(code);rows=before['processes'];assert len(rows)==2 and before['taskState']=='Running',before
assert all('eval_worker_sensor.py' in r['CommandLine'] for r in rows)
own=[r for r in rows if r['ProcessId']==started['pid']];assert len(own)==1 and abs(own[0]['creation_epoch']-started['epoch'])<2
children=ps("@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(started['pid'])+"' | Select-Object ProcessId,CommandLine)|ConvertTo-Json -Compress")
assert not children,'Idle handover refuses any live evaluation child'
retained=ps("$xml=Export-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_sensor';[pscustomobject]@{xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count}|ConvertTo-Json -Compress")
assert retained['triggerCount']==0;(D/'OLD_TASK_RETAINED.xml').write_text(retained['xml'],encoding='utf8')
ps("$ErrorActionPreference='Stop';Disable-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_sensor'|Out-Null;Stop-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_sensor'|Out-Null")
for _ in range(60):
 after=ps(code)
 if not after['processes']:break
 time.sleep(.25)
assert not after['processes'],after
with (D.parent/'worker.lock').open('a+b') as f:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
task=ps(r'''
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_v15_clock2500_solver32'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'New task already exists; inspect instead of restart'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\sensor_clock2500_solver32_v15\eval_worker_clock2500.py' -WorkingDirectory 'D:\MOD4_async_eval\sensor_clock2500_solver32_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'Approved immutable2.5ms solver32 frozen scope; no triggers/PPO/budget/4090 authority. Shared singleGPU lock.'|Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()}|ConvertTo-Json -Compress
''');assert task['triggerCount']==0
for _ in range(80):
 if (D/'WORKER_STARTED.json').exists():break
 time.sleep(.1)
new=json.loads((D/'WORKER_STARTED.json').read_text());assert not (D/'WORKER_ATTENTION.json').exists()
v=dict(epoch=time.time(),old16complete_idle_verified=True,old_actual_identity=before,old_task_xml_retained=True,old_task_disabled=True,old_actual_processes_exited=True,no_live_GPU_child_signalled=True,new_worker=new,new_task=task,worker_sha256=hashlib.sha256((D/'eval_worker_clock2500.py').read_bytes()).hexdigest(),namespace='clk2500-solver32-',shared_single_GPU_lock=True,canonical_write_authority=False,training_launch_authority=False,new_scope_pending=True)
(D/'HANDOVER.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))

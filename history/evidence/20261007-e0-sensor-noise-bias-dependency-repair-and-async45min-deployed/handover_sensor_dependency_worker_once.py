"""Start one complete-scope worker after the failed worker actually exited."""
from pathlib import Path
import json,subprocess,base64,time,msvcrt,hashlib
D=Path(__file__).resolve().parent;OLD=D.parent/'history_clock1000_v15'
assert D==Path('D:/MOD4_async_eval/sensor_clock1000_v15') and not (D/'HANDOVER.json').exists()
def ps(code):
 enc=base64.b64encode(code.encode('utf-16le')).decode()
 p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
 assert p.returncode==0,p.stdout+p.stderr
 return json.loads(p.stdout) if p.stdout.strip() else None
assert (OLD/'WORKER_ATTENTION.json').is_file()
assert len([x for x in (OLD/'jobs').glob('clk1000-*') if '-s2' not in x.name and (x/'complete.json').is_file()])==14
failed=json.loads((OLD/'jobs/clk1000-s2sensor-flat/result.json').read_text());assert failed['phase']=='retained_failed' and not failed['result_present']
assert "No module named 'history_actor_label_ppo'" in (OLD/'jobs/clk1000-s2sensor-flat/probe.log').read_text(errors='replace')
identity=ps("$p=@(Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -like '*history_clock1000_v15*'});[pscustomobject]@{actualOldProcesses=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};oldTaskState=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_clock1000').State.ToString()}|ConvertTo-Json -Depth 5 -Compress")
assert not identity['actualOldProcesses'] and identity['oldTaskState']=='Ready',identity
with (D.parent/'worker.lock').open('a+b') as f:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
retained=ps("$xml=Export-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_clock1000';[pscustomobject]@{xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count}|ConvertTo-Json -Compress")
assert retained['triggerCount']==0;(D/'OLD_TASK_RETAINED.xml').write_text(retained['xml'],encoding='utf8')
ps("$ErrorActionPreference='Stop';Disable-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_clock1000'|Out-Null")
task=ps(r'''
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_v15_sensor'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'New task already exists; inspect instead of restarting'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\sensor_clock1000_v15\eval_worker_sensor.py' -WorkingDirectory 'D:\MOD4_async_eval\sensor_clock1000_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'Approvedv1.5 complete sensor frozen scope only; no triggers/PPO/budget/4090authority. One shared GPUlock.'|Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()}|ConvertTo-Json -Compress
''');assert task['triggerCount']==0
for _ in range(60):
 if (D/'WORKER_STARTED.json').exists():break
 time.sleep(.1)
new=json.loads((D/'WORKER_STARTED.json').read_text());assert not (D/'WORKER_ATTENTION.json').exists()
receipt=dict(epoch=time.time(),old_actual_identity=identity,old_actual_worker_exited=True,old_PID_not_assumed_or_signaled=True,old_task_disabled=True,old14completed_and_failed_sensor_files_retained=True,new_worker=new,new_task=task,worker_sha256=hashlib.sha256((D/'eval_worker_sensor.py').read_bytes()).hexdigest(),namespace='clk1000-s2complete-',single_shared_GPU_lock=True,canonical_write_authority=False,training_launch_authority=False)
(D/'HANDOVER.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))

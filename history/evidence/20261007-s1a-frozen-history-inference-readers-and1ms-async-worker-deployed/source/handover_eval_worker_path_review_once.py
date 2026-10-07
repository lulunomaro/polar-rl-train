"""Retire only the completed idle old evaluator and demand-start one new frozen worker."""
from pathlib import Path
import json,subprocess,base64,time,os,msvcrt
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent
assert ROOT==Path('D:/MOD4_async_eval/history_clock1000_v15')
RECEIPT=ROOT/'WORKER_HANDOVER.json';assert not RECEIPT.exists()
def ps(code):
 enc=base64.b64encode(code.encode('utf-16le')).decode()
 p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
 assert p.returncode==0,p.stdout+p.stderr
 return json.loads(p.stdout) if p.stdout.strip() else None
old=json.loads((OLD/'WORKER_STARTED.json').read_text());pid=int(old['pid'])
jobs=list((OLD/'jobs').iterdir());assert len(jobs)==7 and all((p/'complete.json').exists() for p in jobs)
identity=ps("$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"'; $children=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(pid)+"'); [pscustomobject]@{process=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=$children|Select-Object ProcessId,CommandLine} | ConvertTo-Json -Depth 5 -Compress")
assert identity['process'] and identity['process']['ProcessId']==pid
assert 'D:/MOD4_async_eval/eval_worker.py' in identity['process']['CommandLine'].replace(chr(92),'/') and not identity['children']
assert not (OLD/'WORKER_ATTENTION.json').exists()
assert abs(identity['process']['creation_epoch']-1791308481.929)<1
xml=ps("$xml=Export-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v12'; [pscustomobject]@{xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count} | ConvertTo-Json -Compress")
assert xml['triggerCount']==0
(ROOT/'OLD_TASK_RETAINED.xml').write_text(xml['xml'],encoding='utf8')
(ROOT/'WORKER_HANDOVER_PRECHECK.json').write_text(json.dumps(dict(epoch=time.time(),old_identity=identity,old_jobs_completed=7,old_task_trigger_count=0,new_worker_sha256=__import__('hashlib').sha256((ROOT/'eval_worker_clock1000.py').read_bytes()).hexdigest(),no_learning=True),indent=2))
ps("$ErrorActionPreference='Stop'; Stop-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v12'; Disable-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v12' | Out-Null")
for _ in range(50):
 live=ps("[bool](Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"') | ConvertTo-Json -Compress")
 if not live:break
 time.sleep(.1)
assert not live,'Old worker has not actually exited; no new task starts'
with (OLD/'worker.lock').open('a+b') as f:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
task=ps(r'''
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_v15_clock1000'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'New task already exists; inspect actual instead of replacing'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\history_clock1000_v15\eval_worker_clock1000.py' -WorkingDirectory 'D:\MOD4_async_eval\history_clock1000_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'ApprovedMOD4 v1.5 immutable1ms/history frozen evaluation only; demand-start, no triggers, no PPO/budget/4090 launch authority.' | Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()} | ConvertTo-Json -Compress
''')
assert task['triggerCount']==0
for _ in range(50):
 if (ROOT/'WORKER_STARTED.json').exists():break
 time.sleep(.1)
new=json.loads((ROOT/'WORKER_STARTED.json').read_text());assert new['pid']!=pid
assert not (ROOT/'WORKER_ATTENTION.json').exists()
proof=dict(epoch=time.time(),old_worker=identity,old_worker_actual_exited=True,old_task_disabled=True,old_completed_jobs_and_files_preserved=True,new_worker=new,new_task=task,single_shared_GPU_lock=True,new_learning=False,canonical_write_authority=False,queue_published=False)
RECEIPT.write_text(json.dumps(proof,indent=2));print(json.dumps(proof))

"""Make the worker independent of SSH session lifetime; one demand-start task, no trigger."""
from pathlib import Path
import json,time,subprocess,base64
ROOT=Path(__file__).resolve().parent
receipt=ROOT/'WORKER_TASK_REVIEWED.json';assert not receipt.exists()
old=json.loads((ROOT/'WORKER_STARTED.json').read_text(encoding='utf8'))
query='Get-Process -Id '+str(old['pid'])+' -ErrorAction SilentlyContinue | Select-Object Id | ConvertTo-Json -Compress'
r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',query],capture_output=True,text=True,creationflags=0x08000000)
assert not r.stdout.strip(),'Existing worker still alive; preserve it'
for folder in (ROOT/'jobs').glob('*'):
 assert not (folder/'ACTIVE.json').exists(),'Prior GPU launch needs explicit audit before restarting'
(ROOT/'SSH_PARENT_EXIT_RETAINED.json').write_text(json.dumps({'epoch':time.time(),'old_worker':old,'gpu_ever_launched':False,'snapshot_download_retained':True}))
pyw=Path('D:/claude2/fangzhen/.venv-isaaclab/Scripts/pythonw.exe');assert pyw.is_file()
code=r'''
$ErrorActionPreference='Stop'
$taskName='MOD4_AsyncFrozenEvaluation_v12'
if(Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue){throw 'Dedicated task already exists; inspect instead of replacing'}
$taskAction=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\eval_worker.py' -WorkingDirectory 'D:\MOD4_async_eval'
$taskPrincipal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$taskSettings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $taskAction -Principal $taskPrincipal -Settings $taskSettings -Description 'ApprovedMOD4 v1.2 frozen evaluation only; demand-start, no periodic trigger, no canonical or production launch authority.' | Out-Null
Start-ScheduledTask -TaskName $taskName
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName,State,@{n='TriggerCount';e={@($_.Triggers).Count}} | ConvertTo-Json -Compress
'''
encoded=base64.b64encode(code.encode('utf-16le')).decode()
r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',encoded],capture_output=True,text=True,creationflags=0x08000000)
assert r.returncode==0,r.stdout+r.stderr
proof={'epoch':time.time(),'task':json.loads(r.stdout),'no_periodic_trigger':True,'no_boot_trigger':True,'old_SSH_parented_worker_exited_before_GPU':True,'all_artifacts_preserved':True,'no_new_learning':True}
receipt.write_text(json.dumps(proof));print(json.dumps(proof))

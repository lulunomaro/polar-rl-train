"""CPU-only wait for all previous immutable jobs, then replace the idle worker."""
from pathlib import Path
import sys,json,time,subprocess,base64,traceback
D=Path(__file__).resolve().parent;OLD=D.parent/'sensor_recovery_clock1000_v15';sys.path.insert(0,str(OLD));import eval_worker_recovery1000 as previous
def ps(code):
 enc=base64.b64encode(code.encode('utf-16le')).decode();p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert p.returncode==0,p.stdout+p.stderr
 return json.loads(p.stdout) if p.stdout.strip() else None
def read(p):return json.loads(p.read_text(encoding='utf8'))
def main():
 assert D==Path('D:/MOD4_async_eval/closure_episode_clock2500_v15') and (D/'HANDOVER_ATTENTION.json').exists() and not (D/'HANDOVER_COMPLETE.json').exists() and not (D/'HANDOVER_PERMISSION_REVIEW_STARTED.json').exists()
 previous.atomic(D/'HANDOVER_PERMISSION_REVIEW_STARTED.json',dict(epoch=time.time(),pid=__import__('os').getpid(),CPU_only=True,previous_GPU_jobs_not_interrupted=True))
 while True:
  jobs=[j for j in previous.rpc({'op':'list_jobs'})['jobs'] if j.startswith('clk1000-recovery-')]
  state=read(OLD/'WORKER_STATE.json');started=read(OLD/'WORKER_STARTED.json');pid=started['pid']
  row=ps("$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"';$c=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(pid)+"');[pscustomobject]@{process=$p|Select-Object ProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=$c|Select-Object ProcessId,CommandLine}|ConvertTo-Json -Depth 6 -Compress")
  assert row['process'] and 'sensor_recovery_clock1000_v15\\eval_worker_recovery1000.py' in row['process']['CommandLine'] and abs(row['process']['creation_epoch']-started['epoch'])<2
  if not row['children'] and state['phase']=='polling' and time.time()-state['epoch']<90 and all((OLD/'jobs'/j/'complete.json').exists() for j in jobs):break
  previous.atomic(D/'HANDOVER_STATE.json',dict(epoch=time.time(),phase='waiting_previous_jobs_complete',job_count=len(jobs),old_identity=row,training_not_blocked=True));time.sleep(30)
 # No new1ms publication is allowed after the4090 saved-boundary owner retirement.
 again=[j for j in previous.rpc({'op':'list_jobs'})['jobs'] if j.startswith('clk1000-recovery-')];assert again==jobs
 oldname='MOD4_AsyncFrozenEvaluation_v15_recovery1000';xml=ps("$xml=Export-ScheduledTask -TaskName '"+oldname+"';[pscustomobject]@{xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count}|ConvertTo-Json -Compress");assert xml['triggerCount']==0;(D/'OLD_TASK_RETAINED.xml').write_text(xml['xml'],encoding='utf8')
 ps("$ErrorActionPreference='Stop';Disable-ScheduledTask -TaskName '"+oldname+"'|Out-Null;Stop-ScheduledTask -TaskName '"+oldname+"'|Out-Null")
 for _ in range(60):
  gone=ps("Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"'|Select-Object ProcessId|ConvertTo-Json -Compress")
  if not gone:break
  time.sleep(.25)
 assert not gone
 task=ps(r'''
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_v15_closure2500'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Existing task: do not repeat'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\closure_episode_clock2500_v15\eval_worker_closure2500.py' -WorkingDirectory 'D:\MOD4_async_eval\closure_episode_clock2500_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'Immutable2.5ms32-4 D3 frozen evaluation; shared GPU lock; no triggers or production launch/canonical write.'|Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()}|ConvertTo-Json -Compress
''');assert task['triggerCount']==0
 for _ in range(100):
  if (D/'WORKER_STARTED.json').exists():break
  time.sleep(.1)
 new=read(D/'WORKER_STARTED.json');assert not (D/'WORKER_ATTENTION.json').exists()
 bootstrap='MOD4_AsyncFrozenEvaluation_closure2500_saved_handover_once'
 saved=ps("$ErrorActionPreference='Stop';$xml=Export-ScheduledTask -TaskName '"+bootstrap+"';[pscustomobject]@{xml=$xml;state=(Get-ScheduledTask -TaskName '"+bootstrap+"').State.ToString()}|ConvertTo-Json -Compress");assert saved['state']!='Running';(D/'BOOTSTRAP_TASK_RETAINED.xml').write_text(saved['xml'],encoding='utf8')
 ps("$ErrorActionPreference='Stop';Unregister-ScheduledTask -TaskName '"+bootstrap+"' -Confirm:$false")
 previous.atomic(D/'HANDOVER_COMPLETE.json',dict(epoch=time.time(),old_completed_jobs=jobs,old_identity=row,old_task_disabled=True,new_worker=new,new_task=task,shared_GPU_lock=True,no_training_or_budget_authority=True,new_behavior_scope_pending=True))
if __name__=='__main__':
 try:main()
 except BaseException:previous.atomic(D/'HANDOVER_PERMISSION_REVIEW_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_retry=True));raise

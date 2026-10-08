"""New CPU-only worker replacement after actual exited previous worker/child."""
from pathlib import Path
import json,time,subprocess,base64,msvcrt,hashlib
D=Path(__file__).resolve().parent
def ps(code):
    encoded=base64.b64encode(code.encode('utf-16le')).decode()
    p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',encoded],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
    assert p.returncode==0,p.stdout+p.stderr
    return json.loads(p.stdout) if p.stdout.strip() else None
def main():
    assert D==Path('D:/MOD4_async_eval/closure_episode_clock2500_v15') and not (D/'SPRING_AUDIT_WORKER_ADMISSION.json').exists()
    read=lambda p:json.loads(p.read_text(encoding='utf8'))
    original=read(D/'PRESSURE_DEPENDENCY_WORKER_STARTED.json');pid=original['pid']
    assert pid==24444 and (D/'PRESSURE_DEPENDENCY_WORKER_ATTENTION.json').exists()
    result=read(D/'jobs/clk2500-closure-episode-d3-67-d5-stiffness-index-sdk-01-on/result.json')
    assert result['phase']=='retained_failed' and result['errors'] and not result['result_present']
    error=(D/'jobs/clk2500-closure-episode-d3-67-d5-stiffness-index-sdk-01-on/probe.json.error.txt').read_text(encoding='utf8')
    assert "gas_springs_stiffness_error" in error
    pending=D/'jobs/clk2500-closure-episode-d3-66-d5-stiffness-sdk-01-on'
    assert not (pending/'ACTIVE.json').exists() and not (pending/'complete.json').exists()
    actual=ps("$rows=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{rows=$rows}|ConvertTo-Json -Compress -Depth 6")
    this=[x for x in actual['rows'] if x['ProcessId']==__import__('os').getpid()]
    assert len(this)==1
    allowed_CPU_reader_ids={this[0]['ProcessId'],this[0]['ParentProcessId']}
    assert all('admit_spring_audit_worker_once.py' in x['CommandLine'] for x in actual['rows'] if x['ProcessId'] in allowed_CPU_reader_ids)
    assert not [x for x in actual['rows'] if x['ProcessId'] not in allowed_CPU_reader_ids],'Old worker/GPU child is still active; do not interrupt it'
    lock=(D.parent/'worker.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
    old='MOD4_AsyncFrozenEvaluation_v15_pressure_dependency_review'
    task=ps("$ErrorActionPreference='Stop';$xml=Export-ScheduledTask -TaskName '"+old+"';[pscustomobject]@{xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName '"+old+"').State.ToString()}|ConvertTo-Json -Compress")
    assert task['triggerCount']==0 and task['state']!='Running'
    (D/'OLD_TASK_BEFORE_SPRING_AUDIT_REVIEW.xml').write_text(task['xml'],encoding='utf8')
    ps("$ErrorActionPreference='Stop';Disable-ScheduledTask -TaskName '"+old+"'|Out-Null")
    admission=dict(epoch=time.time(),old_worker_locator=original,old_worker_and_children_exited=True,actual_processes=actual,
        old_demand_task_disabled=True,old_failed_and_unexecuted_packages_preserved=True,shared_GPU_lock_was_free=True,
        excluded_failed_source='67-d5-stiffness-index-sdk-01-on',reason='D0 observer used fixed3500 reference for intended D5 spring stiffness; new observer verifies actual drive/buffer/model against independentD5 state with all other D0 checks intact',
        old_worker_original_errors_preserved=True,no_4090_PPO_or_canonical_or_live_asset_mutation=True)
    (D/'SPRING_AUDIT_WORKER_ADMISSION.json').write_text(json.dumps(admission,indent=2),encoding='utf8')
    new=ps(r'''
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_v15_spring_audit_review'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Existing new task; do not repeat'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\closure_episode_clock2500_v15\eval_worker_spring_audit_review.py' -WorkingDirectory 'D:\MOD4_async_eval\closure_episode_clock2500_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'Explicit frozen SDK dependency recovery; same single GPU lock; skip only retained invalid immutable pressure66 packages; no triggers/production launch/canonical write.'|Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()}|ConvertTo-Json -Compress
''')
    assert new['triggerCount']==0
    for _ in range(100):
        if (D/'SPRING_AUDIT_WORKER_STARTED.json').exists():break
        time.sleep(.1)
    started=read(D/'SPRING_AUDIT_WORKER_STARTED.json')
    assert not (D/'SPRING_AUDIT_WORKER_ATTENTION.json').exists()
    (D/'SPRING_AUDIT_TASK.xml').write_text(new.pop('xml'),encoding='utf8')
    done=dict(epoch=time.time(),admission=admission,new_worker=started,new_task=new,no_replay_of_completed_jobs=True,old_files_results_error_taskXML_preserved=True)
    (D/'SPRING_AUDIT_WORKER_ADMITTED.json').write_text(json.dumps(done,indent=2),encoding='utf8');print(json.dumps(done))
if __name__=='__main__':main()

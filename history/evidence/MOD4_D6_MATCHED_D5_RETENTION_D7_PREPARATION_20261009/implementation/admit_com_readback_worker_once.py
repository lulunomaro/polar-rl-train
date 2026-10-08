"""CPU-only transfer after real failed SDK worker exit; no signals or GPU launch."""
from pathlib import Path
import os,json,time,hashlib,subprocess,base64,msvcrt
from resilient_json_atomic import atomic
D=Path(__file__).resolve().parent
def ps(code):
    p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
    assert p.returncode==0,p.stdout+p.stderr
    return json.loads(p.stdout) if p.stdout.strip() else None
def main():
    assert D==Path('D:/MOD4_async_eval/closure_episode_clock2500_v15') and not (D/'COM_READBACK_REVIEW_WORKER_ADMISSION.json').exists()
    read=lambda p:json.loads(p.read_text(encoding='utf8'))
    assert hashlib.sha256((D/'eval_worker_closure2500.py').read_bytes()).hexdigest()=='0b7e7a700a952dda0a08edc7587406f39880d10843ee4ef49132fe979e6268f1'
    fault=read(D/'JOB_IDENTIFIER_REVIEW_WORKER_ATTENTION.json');assert 'Frozen evaluation failed' in fault['error']
    job=D/'jobs/clk2500-closure-episode-d3-88-d7-chassis-pd-nominal-sdk'
    failed=read(job/'result.json');assert failed['phase']=='retained_failed' and failed['checkpoint']['iteration_stored']==31416
    error=(job/'probe.json.error.txt').read_text(encoding='utf8');assert "assert result['D7_nominal_chassis_PD_initial']['static']" in error
    actual=ps("$rows=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{rows=$rows}|ConvertTo-Json -Compress -Depth 6")
    this=[p for p in actual['rows'] if p['ProcessId']==os.getpid()];assert len(this)==1
    allowed={os.getpid(),this[0]['ParentProcessId']}
    assert all(p['ProcessId'] in allowed and 'admit_com_readback_worker_once.py' in p['CommandLine'] for p in actual['rows']),'Real worker/child still active; wait without signals'
    lock=(D.parent/'worker.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
    old='MOD4_AsyncFrozenEvaluation_v15_job_identifier_review'
    task=ps("$ErrorActionPreference='Stop';$xml=Export-ScheduledTask -TaskName '"+old+"';[pscustomobject]@{xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName '"+old+"').State.ToString()}|ConvertTo-Json -Compress")
    assert task['triggerCount']==0 and task['state']!='Running'
    (D/'OLD_TASK_BEFORE_COM_READBACK_REVIEW.xml').write_text(task['xml'],encoding='utf8')
    ps("$ErrorActionPreference='Stop';Disable-ScheduledTask -TaskName '"+old+"'|Out-Null")
    admission=dict(epoch=time.time(),old_worker_and_children_exited=True,actual_processes=actual,old_demand_task_disabled=True,shared_GPU_lock_was_free=True,
                   old_attention_retained=fault,old_failed_result_retained=failed,old_sources_XML_errors_results_preserved=True,
                   only_reviewed_D7_readonly_failure_retired=True,no_4090_PPO_canonical_or_live_asset_mutation=True)
    atomic(D/'COM_READBACK_REVIEW_WORKER_ADMISSION.json',admission)
    new=ps(r'''
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_v15_com_readback_review'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Existing new task; do not repeat'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\closure_episode_clock2500_v15\eval_worker_com_readback_review.py' -WorkingDirectory 'D:\MOD4_async_eval\closure_episode_clock2500_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'Immutable D7 read-only correction; prior failure retained; valid completed cases reused; no trainer or budget authority.'|Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()}|ConvertTo-Json -Compress
''')
    assert new['triggerCount']==0
    for _ in range(100):
        if (D/'COM_READBACK_REVIEW_WORKER_STARTED.json').exists():break
        time.sleep(.1)
    started=read(D/'COM_READBACK_REVIEW_WORKER_STARTED.json');assert not (D/'COM_READBACK_REVIEW_WORKER_ATTENTION.json').exists()
    (D/'COM_READBACK_REVIEW_TASK.xml').write_text(new.pop('xml'),encoding='utf8')
    done=dict(epoch=time.time(),admission=admission,new_worker=started,new_task=new,no_replay_of_valid_completed_jobs=True,no_4090_PPO_canonical_or_live_asset_mutation=True)
    atomic(D/'COM_READBACK_REVIEW_WORKER_ADMITTED.json',done);print(json.dumps(done))
if __name__=='__main__':main()

"""New frozen-only authority after actual previous worker/children exit and free lock."""
from pathlib import Path
import os,json,time,hashlib,subprocess,base64,msvcrt
from resilient_json_atomic import atomic
D=Path(__file__).resolve().parent
def ps(code):
 p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
 assert p.returncode==0,p.stdout+p.stderr
 return json.loads(p.stdout) if p.stdout.strip() else None
def main():
 assert D==Path('D:/MOD4_async_eval/closure_episode_clock2500_v15') and not (D/'E1_FULL_ROUTE_REVIEW_WORKER_ADMISSION.json').exists()
 read=lambda p:json.loads(p.read_text(encoding='utf8'))
 assert hashlib.sha256((D/'eval_worker_closure2500.py').read_bytes()).hexdigest()=='0b7e7a700a952dda0a08edc7587406f39880d10843ee4ef49132fe979e6268f1'
 assert hashlib.sha256((D/'eval_worker_e1_curriculum_interface_review.py').read_bytes()).hexdigest()=='39965b7a0e55a8469535c6c4d97f950432fa0c7a7de7e76478935066e7840f7d'
 expected=read(D/'E1_FULL_ROUTE_WORKER_EXPECTED.json')
 assert hashlib.sha256((D/'eval_worker_e1_full_route_review.py').read_bytes()).hexdigest()==expected['new_source_sha256']
 fault=read(D/'E1_CURRICULUM_INTERFACE_WORKER_ATTENTION.json');assert 'Frozen evaluation failed' in fault['error']
 jid='clk2500-closure-episode-d3-119-e1-g1-fullroute-anchor32053-flat';folder=D/'jobs'/jid
 failed=read(folder/'result.json');assert failed['phase']=='retained_failed' and failed['error_files']==['probe.json.error.txt']
 assert hashlib.sha256((folder/'probe.json.error.txt').read_bytes()).hexdigest()=='36430e1c04ec7f71ce2ac0ec66289af52076d0d5c9d93176380509a1222ce86b'
 assert not (D/'jobs/clk2500-closure-episode-d3-119-e1-g1-fullroute-candidate32098-flat').exists()
 actual=ps("$rows=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{rows=$rows}|ConvertTo-Json -Compress -Depth 6")
 this=[p for p in actual['rows'] if p['ProcessId']==os.getpid()];assert len(this)==1
 allowed={os.getpid(),this[0]['ParentProcessId']}
 assert all(p['ProcessId'] in allowed and 'admit_e1_full_route_review_once.py' in p['CommandLine'] for p in actual['rows']),'Actual worker or GPU child active; wait without signals'
 lock=(D.parent/'worker.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
 old='MOD4_AsyncFrozenEvaluation_v15_e1_curriculum_interface_review'
 task=ps("$ErrorActionPreference='Stop';$xml=Export-ScheduledTask -TaskName '"+old+"';[pscustomobject]@{xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName '"+old+"').State.ToString()}|ConvertTo-Json -Compress")
 assert task['triggerCount']==0 and task['state']!='Running'
 (D/'OLD_E1_CURRICULUM_TASK_BEFORE_FULL_ROUTE.xml').write_text(task['xml'],encoding='utf8')
 ps("$ErrorActionPreference='Stop';Disable-ScheduledTask -TaskName '"+old+"'|Out-Null")
 admission=dict(epoch=time.time(),old_worker_and_children_exited=True,actual_processes=actual,old_demand_task_disabled=True,shared_GPU_lock_was_free=True,old_attention_retained=fault,original_failed_result=failed,source_SHA_exact=True,no_4090_PPO_canonical_or_live_asset_mutation=True,exclusion_of119_is_failure_and_neverrun_not_pass=True)
 atomic(D/'E1_FULL_ROUTE_REVIEW_WORKER_ADMISSION.json',admission)
 new=ps(r'''
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_v15_e1_full_route_review'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Existing new task; do not repeat'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\closure_episode_clock2500_v15\eval_worker_e1_full_route_review.py' -WorkingDirectory 'D:\MOD4_async_eval\closure_episode_clock2500_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'Retain failed119 proxy dtype proof and neverrun candidate; new frozen complete-wave route review; original bridge/lock; no trainer/budget authority.'|Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()}|ConvertTo-Json -Compress
''')
 assert new['triggerCount']==0
 for _ in range(100):
  if (D/'E1_FULL_ROUTE_REVIEW_WORKER_STARTED.json').exists():break
  time.sleep(.1)
 started=read(D/'E1_FULL_ROUTE_REVIEW_WORKER_STARTED.json');assert not (D/'E1_FULL_ROUTE_REVIEW_WORKER_ATTENTION.json').exists()
 (D/'E1_FULL_ROUTE_REVIEW_TASK.xml').write_text(new.pop('xml'),encoding='utf8')
 done=dict(epoch=time.time(),admission=admission,new_worker=started,new_task=new,no_replay_of_valid_completed_jobs=True,no_4090_PPO_canonical_or_live_asset_mutation=True)
 atomic(D/'E1_FULL_ROUTE_REVIEW_WORKER_ADMITTED.json',done);print(json.dumps(dict(pid=started['pid'],epoch=started['epoch'],task=new)))
if __name__=='__main__':main()

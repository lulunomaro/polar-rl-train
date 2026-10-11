"""New frozen worker after136 precontrol failure and actual oldworker/children exit."""
from pathlib import Path
import os,json,time,hashlib,subprocess,base64,msvcrt
from resilient_json_atomic import atomic
D=Path(__file__).resolve().parent

def ps(code):
 p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
 assert p.returncode==0,p.stdout+p.stderr
 return json.loads(p.stdout) if p.stdout.strip() else None

def main():
 assert D==Path('D:/MOD4_async_eval/closure_episode_clock2500_v15') and not (D/'E1_SLOPE8_QUERY_REVIEW_WORKER_ADMISSION.json').exists()
 read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 expected=read(D/'SLOPE8_QUERY_WORKER_EXPECTED.json')
 assert H(D/'eval_worker_closure2500.py')=='0b7e7a700a952dda0a08edc7587406f39880d10843ee4ef49132fe979e6268f1'
 assert H(D/'eval_worker_e1_g3_package_review.py')==expected['old_worker_SHA'] and H(D/'eval_worker_e1_slope8_query_review.py')==expected['new_worker_SHA']
 fault=read(D/'E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json');assert 'Frozen evaluation failed; retained and returned evidence' in fault['error']
 jid='clk2500-closure-episode-d3-136-e1-slope8-source404-mirrored-fullroute-flat';folder=D/'jobs'/jid;m=read(folder/'manifest.json');r=read(folder/'result.json')
 assert m['no_learning'] and not m['canonical_write_authority'] and r['phase']=='retained_failed' and not r['new_learning']
 assert r['error_files']==['probe.json.error.txt'] and not (folder/'probe.json').exists()
 assert H(folder/'result.json')==expected['result136_SHA'] and H(folder/'probe.json.error.txt')==expected['error136_SHA']
 assert r['runtime_archive_sha256']=='050ef42a3909b13292f0caf29c3a82a05c030d38a35a16312bdc6790c2a5b0c9' and r['checkpoint']['sha256']=='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411'
 error=(folder/'probe.json.error.txt').read_text(encoding='utf8');assert 'line 94, in main' in error and 'sampled-expected[None,:]' in error
 actual=ps("$rows=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{rows=$rows}|ConvertTo-Json -Compress -Depth 6")
 this=[p for p in actual['rows'] if p['ProcessId']==os.getpid()];assert len(this)==1;allowed={os.getpid(),this[0]['ParentProcessId']}
 assert all(p['ProcessId'] in allowed and 'admit_slope8_query_worker_once.py' in p['CommandLine'] for p in actual['rows']),'Actual previous worker or GPU child active; wait without signals'
 lock=(D.parent/'worker.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
 old='MOD4_AsyncFrozenEvaluation_v15_e1_g3_package_review'
 task=ps("$ErrorActionPreference='Stop';$xml=Export-ScheduledTask -TaskName '"+old+"';[pscustomobject]@{xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName '"+old+"').State.ToString()}|ConvertTo-Json -Compress")
 assert task['triggerCount']==0 and task['state']!='Running'
 ps("$ErrorActionPreference='Stop';Disable-ScheduledTask -TaskName '"+old+"'|Out-Null")
 admission=dict(epoch=time.time(),old_worker_and_children_exited=True,actual_processes=actual,old_demand_task_disabled=True,old_task_before_disable=task,
  shared_GPU_lock_was_free=True,old_attention_retained=fault,original_failed136_result=r,expected=expected,
  exclusion136_before_control_not_physical_pass=True,baseguard_bridge_JSON_retry_singleGPUlock_unchanged=True,no_4090_PPO_canonical_or_live_asset_mutation=True)
 atomic(D/'E1_SLOPE8_QUERY_REVIEW_WORKER_ADMISSION.json',admission)
 new=ps(r'''
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_v15_e1_slope8_query_review'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Existing new task; do not repeat'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\closure_episode_clock2500_v15\eval_worker_e1_slope8_query_review.py' -WorkingDirectory 'D:\MOD4_async_eval\closure_episode_clock2500_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'Retain136 precontrol nominal-versus-actual rayinput mismatch; exact new137 input-identity scope; original bridge/guard/lock; frozen only.'|Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;xml=$xml;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()}|ConvertTo-Json -Compress
''')
 assert new['triggerCount']==0
 for _ in range(100):
  if (D/'E1_SLOPE8_QUERY_REVIEW_WORKER_STARTED.json').exists():break
  time.sleep(.1)
 started=read(D/'E1_SLOPE8_QUERY_REVIEW_WORKER_STARTED.json');assert not (D/'E1_SLOPE8_QUERY_REVIEW_WORKER_ATTENTION.json').exists()
 done=dict(epoch=time.time(),admission=admission,new_worker=started,new_task=new,no_replay_of_valid_completed_jobs=True,no_4090_PPO_canonical_or_live_asset_mutation=True)
 atomic(D/'E1_SLOPE8_QUERY_REVIEW_WORKER_ADMITTED.json',done);print(json.dumps(dict(pid=started['pid'],epoch=started['epoch'],task={k:v for k,v in new.items() if k!='xml'})))

if __name__=='__main__':main()

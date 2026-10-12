"""Retain the orphan coordinator; only a new immutable oneoff TaskService scope starts."""
from scut_wave_detached_io import *
OLD='D:/MOD4_async_eval/scut_wave50_gate_compare_20261012'

def main():
    assert not (R/'DETACHED_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json').exists()
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,time,hashlib,subprocess,base64,shutil,torch
OLD=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);TASK=TASK_TOKEN;W=Path('D:/MOD4_async_eval/closure_episode_clock2500_v15');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ps(code):
 r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert r.returncode==0,r.stderr;return json.loads(r.stdout) if r.stdout.strip() else None
old=json.loads((OLD/'REFERENCE_DISPATCH_ACTUAL_RECEIPT.json').read_bytes());pid=old['coordinator']['ProcessId']
actual=ps("@(Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"')|Select-Object ProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}}|ConvertTo-Json -Compress")
assert not actual or abs(actual['creation_epoch']-old['coordinator']['creation_epoch'])>2
assert not (OLD/'IDLE_WORKER_BORROW_ACTUAL.json').exists() and not (OLD/'SHARED_GPU_LOCK_ACTUAL_ACQUIRED.json').exists() and not (OLD/'runs').exists()
assert not (W/'E1_WAVE50_QUERY_REVIEW_WORKER_ATTENTION.json').exists()
preserved=dict(epoch=time.time(),orphan_actual_PID_exit_before_worker_borrow_or_GPU=True,original_started=json.loads((OLD/'REFERENCE_COORDINATOR_STARTED.json').read_bytes()),original_dispatch=old,original_log=dict(path=str(OLD/'coordinator.log'),bytes=(OLD/'coordinator.log').stat().st_size,sha256=h(OLD/'coordinator.log')),classification='Windows SSH-session child lifetime failure before GPU, not SCUT physics or policy failure',new_TaskService_oneoff_continuation_not_old_dispatch_replay=True)
q=OLD/'ORPHAN_DISPATCH_ACTUAL_REVIEW.json';assert not q.exists();q.write_text(json.dumps(preserved,indent=2))
assert not D.exists();D.mkdir();assert shutil.disk_usage(D).free>2*sum(p.stat().st_size for p in OLD.rglob('*') if p.is_file())+2*1024**3
for name in ('original','reference_original.zip','exact_wave50_test.usda','actual_mod4_wave50_query.npz','FIXTURE.json','scut_wave50_placement_reviewed_probe.py','reference_coordinator_once.py'):
 a=OLD/name;b=D/name
 if a.is_dir():shutil.copytree(a,b)
 else:shutil.copyfile(a,b)
original=(D/'reference_coordinator_once.py').read_bytes()
header="from pathlib import Path\nimport sys\nD=Path(__file__).resolve().parent\nsys.stdout=sys.stderr=(D/'coordinator.log').open('x',encoding='utf8')\n"
body=header+original.decode('utf8');compile(body,'reference_coordinator_detached_reviewed_once.py','exec');(D/'reference_coordinator_detached_reviewed_once.py').write_text(body,encoding='utf8')
proof=json.loads((OLD/'TARGET_CPU_ADMITTED.json').read_bytes());assert proof['passed'];proof.update(epoch=time.time(),remote_root=str(D),original_CPU_reference=str(OLD/'TARGET_CPU_ADMITTED.json'),original_CPU_reference_SHA=h(OLD/'TARGET_CPU_ADMITTED.json'),all_original_policy_USD_probe_fixture_bytes_exact=True,new_detached_coordinator_SHA=h(D/'reference_coordinator_detached_reviewed_once.py'),orphan_diagnostic=preserved,no_original_coordinator_or_GPU_replay=True)
for name,row in proof['stage_files'].items():assert h(D/name)==row['sha256']
assert not torch.cuda.is_initialized();(D/'TARGET_CPU_ADMITTED.json').write_text(json.dumps(proof,indent=2))
principalTask='MOD4_AsyncFrozenEvaluation_v15_e1_wave50_query_review'
script="$old=Get-ScheduledTask -TaskName '"+principalTask+"';if(Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue){throw 'Independent reference task already exists'};$a=New-ScheduledTaskAction -Execute 'PY_TOKEN_TEXT' -Argument '-X utf8 \""+str(D/'reference_coordinator_detached_reviewed_once.py')+"\"' -WorkingDirectory '"+str(D)+"';$s=New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 2) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries;$t=Register-ScheduledTask -TaskName '"+TASK+"' -Action $a -Principal $old.Principal -Settings $s;Start-ScheduledTask -TaskName '"+TASK+"';$t=Get-ScheduledTask -TaskName '"+TASK+"';[pscustomobject]@{name=$t.TaskName;state=$t.State.ToString();triggers=@($t.Triggers).Count;action=$t.Actions|Select-Object Execute,Arguments,WorkingDirectory;principal=$t.Principal|Select-Object UserId,LogonType,RunLevel;new_oneoff_no_periodic_no_boot=$true}|ConvertTo-Json -Depth 6 -Compress"
task=ps(script.replace('PY_TOKEN_TEXT',PY_TOKEN));assert task['triggers']==0 and str(D/'reference_coordinator_detached_reviewed_once.py') in task['action']['Arguments']
v=dict(epoch=time.time(),passed=True,new_root=str(D),oneoff_task=task,targetCPU=proof,orphan_old_dispatch_retained=preserved,actual_TaskService_dispatch=True,actual_GPU_probe_pending_owned_idle_slot=True,no_4090_PPO_or_budget_mutation=True)
(D/'DETACHED_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(REMOTE)).replace('TASK_TOKEN',repr(TASK)).replace('PY_TOKEN',repr(PY)))
        save('ORPHAN_DISPATCH_ACTUAL_REVIEW.json',v['orphan_old_dispatch_retained']);save('DETACHED_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json',v)
        print(json.dumps(dict(dispatched=True,oneoff_task=v['oneoff_task'],new_root=REMOTE,no_GPU_pass_inferred=True)))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('DETACHED_REFERENCE_DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),original_partial_retained=True,no_repeat_record_task_or_GPU=True));raise

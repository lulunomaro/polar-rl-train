"""Verify actual unchanged worker restoration after all reference children exit."""
from scut_wave_command_io import *

def main():
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,time,hashlib,subprocess,base64,msvcrt
D=Path(ROOT_TOKEN);W=Path('D:/MOD4_async_eval/closure_episode_clock2500_v15');H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ps(code):
 r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert r.returncode==0,r.stderr;return json.loads(r.stdout)
assert (D/'REFERENCE_ALL_COMPLETE.json').exists() and (D/'UNCHANGED_WORKER_RESTORE_REQUESTED.json').exists() and not (D/'REFERENCE_ATTENTION.json').exists()
cases={}
for f in (D/'runs').iterdir():
 r=json.loads((f/'RESULT.json').read_bytes());assert r['phase']=='complete' and r['result_present'] and not r['error_files'];cases[f.name]=r
assert len(cases)==2
old=json.loads((D/'IDLE_WORKER_BORROW_ACTUAL.json').read_bytes());actualsha={k:H(W/k) for k in old['source_SHA']};assert actualsha==old['source_SHA']
started=json.loads((W/'E1_WAVE50_QUERY_REVIEW_WORKER_STARTED.json').read_bytes());state=json.loads((W/'E1_WAVE50_QUERY_REVIEW_WORKER_STATE.json').read_bytes());assert not (W/'E1_WAVE50_QUERY_REVIEW_WORKER_ATTENTION.json').exists()
pid=started['pid'];v=ps("$all=@(Get-CimInstance Win32_Process);$p=$all|Where-Object {$_.ProcessId -eq "+str(pid)+"};$t=Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_e1_wave50_query_review';[pscustomobject]@{worker=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=@($all|Where-Object {$_.ParentProcessId -eq "+str(pid)+"}|Select-Object ProcessId,CommandLine);reference_processes=@($all|Where-Object {$_.CommandLine -like '*scut_wave50_gate_compare*'}|Select-Object ProcessId,CommandLine);task=@{name=$t.TaskName;state=$t.State.ToString();action=$t.Actions|Select-Object Execute,Arguments;triggers=@($t.Triggers|Where-Object {$_ -ne $null}).Count}}|ConvertTo-Json -Depth 6 -Compress")
assert v['worker'] and abs(v['worker']['creation_epoch']-started['epoch'])<2 and 'eval_worker_e1_wave50_query_review.py' in v['worker']['CommandLine']
assert not v['reference_processes'] and v['task']['state']=='Running' and v['task']['triggers']==0 and v['task']['action']==old['identity']['task']
lock=W.parent/'worker.lock';held=False
with lock.open('r+b') as f:
 f.seek(0)
 try:msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
 except OSError:held=True
 else:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
assert held,'Restored demand worker must own original shared OS lock'
tasks=['MOD4_SCUT_Wave50_Gate_Reference_Oneoff_20261012','MOD4_SCUT_Wave50_Gate_Reference_StateReviewed_20261012','MOD4_SCUT_Wave50_Gate_Reference_RayABI_20261012','MOD4_SCUT_Wave50_Gate_Reference_CommandHook_20261012']
taskstate=ps("$names="+','.join("'"+x+"'" for x in tasks)+";@($names|ForEach-Object {$t=Get-ScheduledTask -TaskName $_ -ErrorAction SilentlyContinue;if($t){[pscustomobject]@{name=$t.TaskName;state=$t.State.ToString();triggers=@($t.Triggers|Where-Object {$_ -ne $null}).Count}}})|ConvertTo-Json -Compress")
assert all(t['state']=='Ready' and t['triggers']==0 for t in taskstate)
v.update(epoch=time.time(),passed=True,source_SHA=actualsha,original_namespace_state=state,shared_OS_lock_actually_held_by_restored_worker=True,all_reference_children_and_coordinators_exited=True,oneoff_tasks_complete_no_triggers=taskstate,reference_cases_complete=cases,original_task_source_actions_and_zero_triggers_unchanged=True,no_GPU_or_budget_replay=True)
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(REMOTE)))
        save('UNCHANGED_WORKER_ACTUAL_RESTORED_VERIFIED.json',v)
        print(json.dumps(dict(passed=True,worker=v['worker'],no_reference_processes=True,original_shared_OS_lock_held=True)))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('WORKER_RESTORE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_worker_restart=True));raise

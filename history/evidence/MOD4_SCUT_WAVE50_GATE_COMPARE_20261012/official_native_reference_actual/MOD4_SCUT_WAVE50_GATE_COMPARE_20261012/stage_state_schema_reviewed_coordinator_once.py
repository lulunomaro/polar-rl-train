"""New no-GPU-failure scope waits through the worker's legitimate network_retry schema."""
from scut_wave_schema_io import *
PRIOR='D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012'

def main():
    assert not (R/'STATE_SCHEMA_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json').exists()
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,time,subprocess,hashlib,base64,torch
P=Path(PRIOR_TOKEN);D=Path(ROOT_TOKEN);TASK=TASK_TOKEN;h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ps(code):
 r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert r.returncode==0,r.stderr;return json.loads(r.stdout) if r.stdout.strip() else None
attention=json.loads((P/'REFERENCE_ATTENTION.json').read_bytes());assert "KeyError: 'jobs'" in attention['error'] and attention['own_child_pid'] is None
assert not (P/'IDLE_WORKER_BORROW_ACTUAL.json').exists() and not (P/'SHARED_GPU_LOCK_ACTUAL_ACQUIRED.json').exists() and not (P/'runs').exists()
oldstart=json.loads((P/'REFERENCE_COORDINATOR_STARTED.json').read_bytes());proc=ps("@(Get-CimInstance Win32_Process -Filter 'ProcessId="+str(oldstart['pid'])+"')|Select-Object ProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}}|ConvertTo-Json -Compress");assert not proc or abs(proc['creation_epoch']-oldstart['epoch'])>2
assert not D.exists();D.mkdir();code=(P/'reference_coordinator_once.py').read_text();anchor="        pending=[j for j in state['jobs'] if not (W/'jobs'/j/'complete.json').exists()]";assert code.count(anchor)==1
replacement="""        if state.get('phase')=='network_retry':
            if time.time()>deadline:raise RuntimeError('Existing bridge retry exceeds bounded wait; no worker/GPU takeover attempted.')
            (D/'WAITING_FOR_OWNED_SLOT.json').write_text(json.dumps(dict(epoch=time.time(),phase='waiting_existing_bridge_retry',original_state=state,no_worker_or_GPU_mutation=True),indent=2));time.sleep(15);continue
        assert state.get('phase')=='polling' and 'jobs' in state, 'Unknown owned worker schema; never invent jobs'
        pending=[j for j in state['jobs'] if not (W/'jobs'/j/'complete.json').exists()]"""
code=code.replace(anchor,replacement).replace("str(D/'scut_wave50_placement_reviewed_probe.py')","str(P/'scut_wave50_placement_reviewed_probe.py')").replace("sha(D/'scut_wave50_placement_reviewed_probe.py')","sha(P/'scut_wave50_placement_reviewed_probe.py')").replace("cwd=D/'original'","cwd=P/'original'")
header="from pathlib import Path\nimport sys\nD=Path(__file__).resolve().parent\nP=Path("+repr(str(P))+ ")\nsys.stdout=sys.stderr=(D/'coordinator.log').open('x',encoding='utf8')\n"
code=header+code;compile(code,'reference_coordinator_state_schema_reviewed_once.py','exec');entry=D/'reference_coordinator_state_schema_reviewed_once.py';entry.write_text(code,encoding='utf8')
cpu=json.loads((P/'TARGET_CPU_ADMITTED.json').read_bytes());assert cpu['passed'];inputs={n:dict(path=str(P/n),bytes=(P/n).stat().st_size,sha256=h(P/n)) for n in ('scut_wave50_placement_reviewed_probe.py','exact_wave50_test.usda','actual_mod4_wave50_query.npz','FIXTURE.json')}
for name,row in cpu['stage_files'].items():assert h(P/name)==row['sha256']
assert not torch.cuda.is_initialized();cpu.update(epoch=time.time(),remote_root=str(D),source_inputs_root=str(P),source_input_indices=inputs,original_cpu_ref=str(P/'TARGET_CPU_ADMITTED.json'),original_cpu_ref_SHA=h(P/'TARGET_CPU_ADMITTED.json'),own_new_coordinator=dict(path=str(entry),bytes=entry.stat().st_size,sha256=h(entry)),original_all_policy_USD_fixture_probe_bytes_reused_exact=True,old_reader_error=attention,no_old_coordinator_or_GPU_replay=True)
(D/'TARGET_CPU_ADMITTED.json').write_text(json.dumps(cpu,indent=2))
actionArgs='-X utf8 "'+str(entry)+'"';s="$old=Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_e1_wave50_query_review';if(Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue){throw 'New reference task exists'};$a=New-ScheduledTaskAction -Execute '"+EXEC_TOKEN+"' -Argument '"+actionArgs+"' -WorkingDirectory '"+str(D)+"';$settings=New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 2) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries;Register-ScheduledTask -TaskName '"+TASK+"' -Action $a -Principal $old.Principal -Settings $settings|Out-Null;Start-ScheduledTask -TaskName '"+TASK+"';$t=Get-ScheduledTask -TaskName '"+TASK+"';[pscustomobject]@{name=$t.TaskName;state=$t.State.ToString();triggers=@($t.Triggers|Where-Object {$_ -ne $null}).Count;action=$t.Actions|Select-Object Execute,Arguments,WorkingDirectory;principal=$t.Principal|Select-Object UserId,LogonType,RunLevel}|ConvertTo-Json -Depth 5 -Compress"
task=ps(s);assert task['triggers']==0 and 'reference_coordinator_state_schema_reviewed_once.py' in task['action']['Arguments']
v=dict(epoch=time.time(),passed=True,new_root=str(D),oneoff_task=task,new_targetCPU=cpu,old_detached_healthy_bridge_state_reader_failure_preserved=True,old_worker_or_GPU_not_borrowed_by_failed_scope=True,no_task_or_source_CPU_GPU_replay=True,actual_TaskService_dispatch=True,actual_probe_requires_future_PID_progress_result=True)
(D/'STATE_SCHEMA_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('PRIOR_TOKEN',repr(PRIOR)).replace('ROOT_TOKEN',repr(REMOTE)).replace('TASK_TOKEN',repr(TASK)).replace('EXEC_TOKEN',repr(PY)))
        save('STATE_SCHEMA_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(dict(passed=True,new_root=REMOTE,oneoff_task=v['oneoff_task'],no_periodic_or_GPU_pass_inferred=True)))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('STATE_SCHEMA_REFERENCE_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),original_partial_evidence_retained=True,no_task_or_GPU_replay=True));raise

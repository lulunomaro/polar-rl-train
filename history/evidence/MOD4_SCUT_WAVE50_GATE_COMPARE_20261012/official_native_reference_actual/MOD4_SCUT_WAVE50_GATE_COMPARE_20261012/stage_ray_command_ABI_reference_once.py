"""New missing sensor/actor-command scope, preserving both initial complete traces."""
from scut_wave_ABI_io import *
INPUT='D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012'
OLD='D:/MOD4_async_eval/scut_wave50_gate_compare_schema_reviewed_20261012'

def main():
    assert not (R/'RAY_ABI_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json').exists()
    assert json.loads((R/'NATIVE_QUATERNION_AND_COMMAND_ABI_CPU_ACTUAL.json').read_bytes())['old_rough_height_scanner_offset_conversion_missing']
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,time,hashlib,subprocess,base64,torch
D=Path(ROOT_TOKEN);P=Path(INPUT_TOKEN);OLD=Path(OLD_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (OLD/'REFERENCE_ALL_COMPLETE.json').exists() and (OLD/'UNCHANGED_WORKER_RESTORE_REQUESTED.json').exists()
old={}
for folder in (OLD/'runs').iterdir():
 r=json.loads((folder/'RESULT.json').read_bytes());p=json.loads((folder/'probe.json').read_bytes());assert r['phase']=='complete' and not r['error_files'];old[folder.name]=dict(result=r,recorded_behavior=p['behavior_completion'],max_closure_mm=p['max_closure_mm'],scope_eligibility=False,reason='Initial rough-height scanner offsets still saved wxyz, native raycaster applies xyzw directly; CPU proves downward pattern turns upward. Actual old sensor rays were not saved and are not fabricated; original complete data remains but not a qualified original-policy/threshold comparison.')
assert not D.exists();D.mkdir();fixture=json.loads((P/'FIXTURE.json').read_bytes());fixture['mesh_file']=str(P/fixture['mesh_file']);(D/'FIXTURE.json').write_text(json.dumps(fixture,indent=2));cpu=json.loads((P/'TARGET_CPU_ADMITTED.json').read_bytes());assert cpu['passed']
for name,row in cpu['stage_files'].items():assert h(P/name)==row['sha256']
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),newroot_created=True,initial_results_preserved=old,original_cpu_reference=cpu,source_inputs_root=str(P),new_root=str(D))))
'''.replace('ROOT_TOKEN',repr(REMOTE)).replace('INPUT_TOKEN',repr(INPUT)).replace('OLD_TOKEN',repr(OLD)))
        save('INITIAL_TWO_REFERENCE_SCOPE_ABI_REJECTED_ACTUAL_REVIEW.json',v)
        with w.open_sftp() as f:
            raw=(D/'scut_wave50_ray_command_ABI_reviewed_probe.py').read_bytes()
            with f.open(REMOTE+'/scut_wave50_ray_command_ABI_reviewed_probe.py','wbx') as out:out.write(raw)
        admission=execute(w,r'''from pathlib import Path
import json,time,hashlib,torch,subprocess,base64
D=Path(ROOT_TOKEN);OLD=Path(OLD_TOKEN);P=Path(INPUT_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
probe=D/'scut_wave50_ray_command_ABI_reviewed_probe.py';assert h(probe)==PROBE_SHA_TOKEN;compile(probe.read_bytes(),str(probe),'exec')
code=(OLD/'reference_coordinator_state_schema_reviewed_once.py').read_text();code=code.replace("str(P/'scut_wave50_placement_reviewed_probe.py')","str(D/'scut_wave50_ray_command_ABI_reviewed_probe.py')").replace("sha(P/'scut_wave50_placement_reviewed_probe.py')","sha(D/'scut_wave50_ray_command_ABI_reviewed_probe.py')")
entry=D/'reference_coordinator_ray_command_ABI_reviewed_once.py';compile(code,str(entry),'exec');entry.write_text(code,encoding='utf8')
cpu=json.loads((P/'TARGET_CPU_ADMITTED.json').read_bytes());cpu.update(epoch=time.time(),remote_root=str(D),source_inputs_root=str(P),new_probe=dict(path=str(probe),bytes=probe.stat().st_size,sha256=h(probe)),new_coordinator=dict(path=str(entry),bytes=entry.stat().st_size,sha256=h(entry)),CPU_quaternion_format_contract_passed=True,actual_downward_height_sensor_and_actor_input_command_required_before_qualification=True,original_source_policy_USD_clock_solver_DR_route_unchanged=True,initial_complete_scope_results_ineligible_preserved=True,actual_GPU_not_yet_launched=True)
assert not torch.cuda.is_initialized();(D/'TARGET_CPU_ADMITTED.json').write_text(json.dumps(cpu,indent=2))
task=TASK_TOKEN;args='-X utf8 "'+str(entry)+'"';ps="$old=Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_e1_wave50_query_review';if(Get-ScheduledTask -TaskName '"+task+"' -ErrorAction SilentlyContinue){throw 'New oneoff exists'};$a=New-ScheduledTaskAction -Execute '"+EXEC_TOKEN+"' -Argument '"+args+"' -WorkingDirectory '"+str(D)+"';$s=New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 2) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries;Register-ScheduledTask -TaskName '"+task+"' -Action $a -Principal $old.Principal -Settings $s|Out-Null;Start-ScheduledTask -TaskName '"+task+"';$t=Get-ScheduledTask -TaskName '"+task+"';[pscustomobject]@{name=$t.TaskName;state=$t.State.ToString();triggers=@($t.Triggers|Where-Object {$_ -ne $null}).Count;action=$t.Actions|Select-Object Execute,Arguments,WorkingDirectory}|ConvertTo-Json -Depth 5 -Compress"
r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(ps.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert r.returncode==0,r.stderr;r=json.loads(r.stdout);assert r['triggers']==0
v=dict(epoch=time.time(),passed=True,targetCPU=cpu,oneoff_task=r,actual_TaskService_dispatch=True,no_periodic_no_boot_no_4090_PPO_or_budget_authority=True,scope='Actually missing original rough-height scanner ABI and observed BODY-command binding, original two complete raw traces preserved as scope-ineligible, no relabeling or old GPU replay')
(D/'RAY_ABI_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(REMOTE)).replace('INPUT_TOKEN',repr(INPUT)).replace('OLD_TOKEN',repr(OLD)).replace('PROBE_SHA_TOKEN',repr(H(raw))).replace('TASK_TOKEN',repr(TASK)).replace('EXEC_TOKEN',repr(PY)))
        save('RAY_ABI_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json',admission);print(json.dumps(dict(passed=True,scope=REMOTE,task=admission['oneoff_task'],new_missing_ABI_scope_only=True)))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('RAY_ABI_REFERENCE_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),partial_originals_retained=True,no_old_GPU_or_task_replay=True));raise

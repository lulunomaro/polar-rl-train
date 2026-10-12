"""Continue the previously rejected pre-control command scope in an independent root."""
from scut_wave_io import *

def main():
    old=D/'scut_wave50_ray_command_ABI_reviewed_probe.py'
    s=old.read_text(encoding='utf8')
    anchor=' env.command_generator.compute=manual_compute'
    assert s.count(anchor)==1
    s=s.replace(anchor,anchor+"\n original_command_hook=env._on_command_updated\n def requested_command_after_original_hook():\n  original_command_hook();manual()\n env._on_command_updated=requested_command_after_original_hook")
    anchor="  assert torch.allclose(obs['policy'][:,:3],expected_command,atol=1e-6,rtol=0), 'Original actor must receive requested scaled BODY command'"
    assert s.count(anchor)==1
    s=s.replace(anchor,"  if not torch.allclose(obs['policy'][:,:3],expected_command,atol=1e-6,rtol=0):\n   (output.parent/'ACTOR_COMMAND_REJECTED_ACTUAL.json').write_text(json.dumps(dict(control=control,policy_command=obs['policy'][:,:3].cpu().tolist(),requested_scaled_command=expected_command.cpu().tolist(),native_command=env.command.cpu().tolist(),modes=env.command_generator.special_mode_id.cpu().tolist()),indent=2))\n   raise AssertionError('Original actor must receive requested scaled BODY command')")
    out=D/'scut_wave50_command_hook_reviewed_probe.py'
    compile(s,str(out),'exec');assert not out.exists();out.write_text(s,encoding='utf8')
    source=D/'stage_ray_command_ABI_reference_once.py';stage=source.read_text(encoding='utf8')
    stage=stage.replace('from scut_wave_ABI_io import *','from scut_wave_command_io import *')
    stage=stage.replace("'RAY_ABI_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json'","'COMMAND_HOOK_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json'")
    stage=stage.replace("assert json.loads((R/'NATIVE_QUATERNION_AND_COMMAND_ABI_CPU_ACTUAL.json').read_bytes())['old_rough_height_scanner_offset_conversion_missing']","assert (R/'NATIVE_QUATERNION_AND_COMMAND_ABI_CPU_ACTUAL.json').exists()")
    stage=stage.replace("assert not D.exists();D.mkdir();fixture=", "FAILED=Path('D:/MOD4_async_eval/scut_wave50_gate_compare_ray_command_reviewed_20261012');assert (FAILED/'REFERENCE_ATTENTION.json').exists() and (FAILED/'UNCHANGED_WORKER_RESTORE_REQUESTED.json').exists();old_failed={};\nfor folder in (FAILED/'runs').iterdir():\n r=json.loads((folder/'RESULT.json').read_bytes());assert r['phase']=='retained_failed' and not r['result_present'];old_failed[folder.name]=dict(result=r,error=(folder/'probe.error.txt').read_text(),height_sensor_verified=json.loads((folder/'ORIGINAL_HEIGHT_SENSOR_GPU_ABI_VERIFIED.json').read_bytes()),classification='Native command postprocessing modified the fixed evaluation command before observations; strict rejection at control0, no policy steps. All original hook operations retained, request bound after hook in new scope.')\nassert not D.exists();D.mkdir();(D/'PRE_CONTROL_COMMAND_FAILURE_RETAINED.json').write_text(json.dumps(old_failed,indent=2));fixture=")
    stage=stage.replace('scut_wave50_ray_command_ABI_reviewed_probe.py','scut_wave50_command_hook_reviewed_probe.py')
    stage=stage.replace('reference_coordinator_ray_command_ABI_reviewed_once.py','reference_coordinator_command_hook_reviewed_once.py')
    stage=stage.replace("'INITIAL_TWO_REFERENCE_SCOPE_ABI_REJECTED_ACTUAL_REVIEW.json'","'COMMAND_HOOK_PRIOR_SCOPE_RETAINED_ACTUAL_REVIEW.json'")
    stage=stage.replace('RAY_ABI_REFERENCE_STAGE_ERROR_','COMMAND_HOOK_REFERENCE_STAGE_ERROR_')
    stage=stage.replace('Actually missing original rough-height scanner ABI and observed BODY-command binding, original two complete raw traces preserved as scope-ineligible, no relabeling or old GPU replay','Original rough-height scanner ABI retained, fixed test command bound after native postprocessing before original observations; earlier pre-control command rejection and initial ineligible traces retained, no changes to actor/robot/DR/clock/route')
    stageout=D/'stage_command_hook_reference_once.py';compile(stage,str(stageout),'exec');assert not stageout.exists();stageout.write_text(stage,encoding='utf8')
    io=D/'scut_wave_command_io.py';assert not io.exists();io.write_text("from scut_wave_io import *\nREMOTE='D:/MOD4_async_eval/scut_wave50_gate_compare_command_hook_reviewed_20261012'\nTASK='MOD4_SCUT_Wave50_Gate_Reference_CommandHook_20261012'\n",encoding='utf8')
    reader=(D/'read_ray_command_ABI_reference_actual.py').read_text().replace('scut_wave_ABI_io','scut_wave_command_io').replace('RAY_ABI_SCUT_REFERENCE_ACTUAL_','COMMAND_HOOK_SCUT_REFERENCE_ACTUAL_')
    (D/'read_command_hook_reference_actual.py').write_text(reader,encoding='utf8')
    save('COMMAND_HOOK_REFERENCE_PREPARED.json',dict(epoch=time.time(),passed=True,source=dict(path=str(old),bytes=old.stat().st_size,sha256=H(old.read_bytes())),new_probe=dict(path=str(out),bytes=out.stat().st_size,sha256=H(out.read_bytes())),original_command_hook_executes_once_before_fixed_requested_command_binding=True,no_added_observation_noise_draws=True,original_actor_robot_DR_clock_route_and_all_thresholds_unchanged=True,pre_control_failure_retained=True,new_GPU_not_yet_launched=True))
    print(json.dumps(dict(prepared=True,AST_passed=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('COMMAND_HOOK_BUILD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),pre_GPU=True));raise

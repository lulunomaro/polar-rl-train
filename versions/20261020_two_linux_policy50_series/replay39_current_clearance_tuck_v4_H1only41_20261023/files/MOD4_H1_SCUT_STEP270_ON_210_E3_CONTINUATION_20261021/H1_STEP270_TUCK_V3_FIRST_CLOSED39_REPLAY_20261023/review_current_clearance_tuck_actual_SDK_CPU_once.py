from pathlib import Path
import hashlib,importlib.util,json,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';C=D/'candidate_clearance_v4';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
    sdk=W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/CPU_SOURCE_ASSEMBLY_FIXTURE_V5_FINAL_BOUND_SOURCE/sdk_exact/source/isaaclab/isaaclab/managers/reward_manager.py'
    spec=importlib.util.spec_from_file_location('new_current_clearance_tuck_cpu',C/'step270_reward_installed_CPU_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);v=m.check(C,sdk)
    assert H(C/'h1_step270_sdk_runtime_candidate.py')=='0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34'
    v.update(epoch=time.time(),reward_module_SHA=H(C/'h1_step270_path_reward_v1.py'),installed_checker_SHA=H(C/'step270_reward_installed_CPU_v1.py'),runtime_SHA=H(C/'h1_step270_sdk_runtime_candidate.py'),not_installed_or_GO=True)
    put('CURRENT_CLEARANCE_TUCK_V4_ACTUAL_SDK_CPU_ACTUAL.json',v)
    print(json.dumps({k:v[k] for k in ('passed','actual_SDK_compute_control_rewards','reward_module_SHA','installed_checker_SHA','runtime_SHA','not_installed_or_GO')}))
except BaseException:
    put('CURRENT_CLEARANCE_TUCK_V4_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),not_training_failure=True));raise

from pathlib import Path
import ast, hashlib, importlib.util, json, sys, time, traceback

D=Path(__file__).resolve().parent; T=D.parent; W=T.parent; C=D/'candidate_reward_V3'; R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)

try:
    sdk=W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/CPU_SOURCE_ASSEMBLY_FIXTURE_V5_FINAL_BOUND_SOURCE/sdk_exact/source/isaaclab/isaaclab/managers/reward_manager.py'
    assert H(sdk)=='2ff82f8e385593e4c2206446ab4ef8de7c72dc0ef444f3e02f60df321d71919e'
    spec=importlib.util.spec_from_file_location('new_installed_reward_contract',C/'step270_reward_installed_CPU_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    result=m.check(C,sdk)
    old=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V32_20261023/payloads/h1'
    for name in ('h1_step270_sdk_runtime_candidate.py','step270_goal_and_scut_rates_candidate.py'):assert H(C/name)==H(old/name)
    prior=ast.parse((T/'H1_STEP270_REWARD_PATH_V1_20261022/h1_step270_path_reward_v1.py').read_text('utf8'))
    new=ast.parse((C/'h1_step270_path_reward_v1.py').read_text('utf8'))
    fn=lambda tree,name:next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    assert ast.dump(fn(prior,'path_increment'))==ast.dump(fn(new,'path_increment'))
    result.update(epoch=time.time(),passed=True,reward_module_SHA=H(C/'h1_step270_path_reward_v1.py'),installed_checker_SHA=H(C/'step270_reward_installed_CPU_v1.py'),runtime_SHA=H(C/'h1_step270_sdk_runtime_candidate.py'),goal_source_SHA=H(C/'step270_goal_and_scut_rates_candidate.py'),old_signed_potential_and_strict_events_AST_exact=True,runtime_command_publisher_boundary_physics_actorinputs_AST_and_bytes_unchanged=True,not_installed_or_GO=True)
    put('REPLAY_V2_REWARD_RUNTIME_AND_ACTUAL_SDK_COMPUTE_CPU_V3_ACTUAL.json',result)
    print(json.dumps(result))
except BaseException:
    put('REPLAY_V2_REWARD_CPU_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),not_training_failure=True));raise

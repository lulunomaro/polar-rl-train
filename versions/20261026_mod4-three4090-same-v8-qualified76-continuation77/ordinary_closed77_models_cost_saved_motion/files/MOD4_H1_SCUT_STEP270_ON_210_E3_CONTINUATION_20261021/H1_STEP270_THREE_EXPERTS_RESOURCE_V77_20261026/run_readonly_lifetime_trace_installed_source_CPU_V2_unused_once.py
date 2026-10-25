"""Execute the new actual source hooks on CPU fixtures only; no policy inference or simulator."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';M=T/'H1_STEP270_LIFETIME_GOAL_ACCOUNTING_DIAGNOSTIC_PREPARATION_20261026';C=M/'candidate_v2'
try:
    sys.path.insert(0,str(C));sp=importlib.util.spec_from_file_location('lifetime_sampler_CPU_fixture',C/'sampling_acceleration_installed_CPU_v2.py');module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
    result=module.check(C,'h1');assert result['passed'] and result['V8_reward_publication_AST']['passed'] and result['lifetime_goal_diagnostic_CPU']['passed']
    old=N/'payloads/h1'
    unchanged={name:hashlib.sha256((old/name).read_bytes()).hexdigest() for name in ('h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py')}
    out={'epoch':time.time(),'passed_local_source_CPU_only':True,'actual_new_trace_source_fixture':result,'unchanged_reward_and_reward_checker':unchanged,'candidate_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in C.glob('*.py')},'original77_runtime_not_changed':True,'not_fresh_target_SDK_admission_or_runtime_goal_events':True}
    with (M/'reports/READONLY_LIFETIME_TRACE_SOURCE_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
    print(json.dumps({'passed_local_source_CPU_only':True,'counter20k_fixture':True,'negative_trace_cases':len(result['lifetime_goal_diagnostic_CPU']['negative_source_cases_rejected']),'not_installed':True}))
except BaseException:
    with (M/'reports'/('READONLY_LIFETIME_TRACE_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump({'epoch':time.time(),'error':traceback.format_exc(),'no_same_once_retry':True},f,indent=2)
    raise

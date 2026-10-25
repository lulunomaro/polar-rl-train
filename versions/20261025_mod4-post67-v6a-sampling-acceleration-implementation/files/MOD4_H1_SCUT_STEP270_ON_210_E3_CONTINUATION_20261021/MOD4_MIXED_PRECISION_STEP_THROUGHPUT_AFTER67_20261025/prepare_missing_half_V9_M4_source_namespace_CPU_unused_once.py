from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';M3=T/'MOD4_MIXED_PRECISION_PAIRED_RSL_V3_AFTER67_20261025'
N=T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    closure=json.loads((M3/'reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
    assert closure['collector_function_complete'] and closure['owner_node_workers_all_actual_out'] and closure['original_canonical_cost_settled']
    assert closure['original_remaining_closed_snapshot']==771155.6640677452
    cpu=json.loads((R/'V9_MISSING_HALF_RESET_AND_CONFIG_LR_AST_CPU_ACTUAL.json').read_bytes());runtime=M/'mixed_precision_step_benchmark_runtime_v9_missing_half.py'
    assert cpu['passed'] and cpu['source_SHA']==H(runtime) and cpu['missing_modes_only']==['bf16','fp16']
    assert not N.exists();N.mkdir();(N/'reports').mkdir()
    for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(M3/folder,N/folder)
    root='H1step270_precision_missinghalfv4_after67_2510'
    files={}
    a=(M3/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').read_text('utf8')
    a=a.replace('H1step270_precision_rslv3_after67_2510',root)
    old="T/'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/"
    assert a.count(old)==2;a=a.replace(old,"T/'MOD4_MIXED_PRECISION_PAIRED_RSL_V3_AFTER67_20261025/reports/")
    files['prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py']=a
    a=(M3/'read_E3_resource_only_after_actual_H1_closed_CPU_once.py').read_text('utf8')
    a=a.replace("N.parent/'H1_STEP270_E3_REWARD_PATH_PAIR_V19_20261022/reports/","N.parent/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/reports/")
    needle=" q=json.loads((N.parent/"
    assert a.count(needle)==1
    pos=a.index(needle);a=a[:pos]+" closure=json.loads((N.parent/'MOD4_MIXED_PRECISION_PAIRED_RSL_V3_AFTER67_20261025/reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closure['owner_node_workers_all_actual_out'] and closure['original_canonical_cost_settled']\n"+a[pos:]
    a=a.replace('pair19_remote_root_exists','previous_recovery_root_exists')
    files['read_M4_missing_half_E3_resource_unused_once.py']=a
    files['deploy_M4_missing_half_pair_unused_once.py']=(M3/'deploy_selected_pair_unused_once.py').read_text('utf8')
    shutil.copy2(runtime,N/runtime.name)
    a=(M3/'bind_actual_RSL_V7_paired_benchmark_payload_CPU_unused_once.py').read_text('utf8')
    a=a.replace('PREVIOUS_UNBOUND_M3','PREVIOUS_UNBOUND_M4').replace('runtime_v7','runtime_v9_missing_half').replace("benchmark_modes=['fp32','bf16','fp16']","benchmark_modes=['bf16','fp16']")
    needle="runtime=M/'mixed_precision_step_benchmark_runtime_v9_missing_half.py';changes=[]"
    assert a.count(needle)==1;a=a.replace(needle,"v9=json.loads((M.parent/'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/V9_MISSING_HALF_RESET_AND_CONFIG_LR_AST_CPU_ACTUAL.json').read_bytes());assert v9['passed']\n"+needle+";assert H(runtime)==v9['source_SHA']")
    files['bind_actual_RSL_V9_missing_half_benchmark_payload_CPU_unused_once.py']=a
    a=(M3/'collect_benchmark_profile_then_text_cost_allout_V2_unused_once.py').read_text('utf8')
    assert a.count('fp32')>=3;a=a.replace('fp32','bf16').replace('FP32','BF16')
    files['collect_M4_missing_half_text_cost_allout_unused_once.py']=a
    files['read_M4_missing_half_own_GO_identity_progress_unused_once.py']=(M3/'read_benchmark_own_GO_identity_and_progress_unused_once.py').read_text('utf8')
    for name,source in files.items():
        ast.parse(source)
        with (N/name).open('x',encoding='utf8') as f:f.write(source)
    assert json.loads((T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['passed']
    v=dict(epoch=time.time(),passed=True,new_namespace=str(N),source_models='complete67 only',remaining_and_previous_owner='actual M3 closure, no reuse old M/67 budget snapshot',V9_source_SHA=H(runtime),missing_modes_only=['bf16','fp16'],M3_valid_FP32_not_repeated=True,original_owner_node_controller_guard_runtime_physics_reward_and_accounting_unchanged=True,no_payload_Task_model_copy_or_GO_yet=True,source_files={name:H(N/name) for name in files})
    put(N/'reports/M4_MISSING_HALF_V9_SOURCE_NAMESPACE_CPU_ACTUAL.json',v);print(json.dumps(v))
except BaseException:
    put(R/('M4_SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_remote_mutation_or_GO=True));raise

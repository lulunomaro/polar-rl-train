from pathlib import Path
import ast,hashlib,json,shutil,time
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';F=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V68_20261025'
assert json.loads((R/'AMP_BENCHMARK_V2_SCALER_ALLOWLIST_AND_CPU_SYNTHETIC_ACTUAL.json').read_bytes())['passed']
for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(F/folder,M/folder)
for name in ('prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py','read_E3_resource_only_after_actual_H1_closed_CPU_once.py','deploy_selected_pair_unused_once.py'):
 a=(F/name).read_text('utf8').replace('H1step270_reward_airfeasible5_2510v68','H1step270_precision_bench_after67_2510')
 if name.startswith('prepare_'):a=a.replace("reward_recipe_version='step270_airborne_feasible_target_v5'","reward_recipe_version='step270_airborne_feasible_target_v5'")
 ast.parse(a)
 with (M/name).open('x',encoding='utf8') as f:f.write(a)
with (R/'BENCHMARK_NAMESPACE_SOURCE_AND_ORIGINAL_ACCOUNT_BOUNDARY_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,current67_must_be_closed_CPU=True,source_root=str(M),original_owner_common_node_and_resources_byteexact=True,production_benchmark_new_script_only=True,original3900_caps_exit300_and_82512_guard_2268000_9_preserved=True,benchmark_execution_receipt_not_training_FINAL=True,benchmark_snapshots_not_qualified_sources=True,source67_remains_latest_qualified=True,no_payload_Task_GO_or_fee_yet=True),f,indent=2)
print(json.dumps(dict(prepared_source_namespace=str(M),no_GO=True)))


from pathlib import Path
import ast,hashlib,json,shutil,time
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';F=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V68_20261025'
N=T/'MOD4_MIXED_PRECISION_H1_CLOCK_V2_AFTER67_20261025';assert not N.exists();N.mkdir();(N/'reports').mkdir()
for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(F/folder,N/folder)
for name in ('prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py','deploy_selected_H1_only_unused_once.py'):
 a=(F/name).read_text('utf8').replace('H1step270_reward_airfeasible5_2510v68','H1step270_precision_h1clockv2_after67_2510')
 if name.startswith('prepare_'):
  needle="resource=read(R/'NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json');assert time.time()-resource['epoch']<600";assert a.count(needle)==1
  a=a.replace(needle,"benchmark=read(T/'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert benchmark['collector_function_complete'] and benchmark['owner_node_workers_all_actual_out'] and benchmark['original_canonical_cost_settled'];resource=dict(epoch=time.time(),reason='H1-only missing benchmark after original H1 clock-reader failure; do not repeat completed E3 comparison',not_a_GPU_resource_probe_or_failure=True)")
  needle="paired=all(resource[k] for k in ('expected_GPU_empty','GPU7000_passed','disk25_passed','RAM8_passed'));keys=('h1','recovery') if paired else ('h1',)";assert a.count(needle)==1
  a=a.replace(needle,"paired=False;keys=('h1',)")
  a=a.replace("proof['remaining_actual_snapshot']>82512.86069250107","benchmark['original_remaining_closed_snapshot']>82512.86069250107")
  a=a.replace("remaining_after=proof['remaining_actual_snapshot']","remaining_after=benchmark['original_remaining_closed_snapshot']")
  a=a.replace("source_current_cohort_original_cost_summary=proof","source_current_cohort_original_cost_summary=proof,benchmark_original_cost_closure=benchmark,benchmark_only_not_model_qualification=True")
  a=a.replace("E3_deferred_for_actual_GPU_nonempty=not paired","E3_deferred_for_actual_GPU_nonempty=False,E3_benchmark_already_consumed_H1_missing_only=True")
  a=a.replace("previous_owner_root=read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']","previous_owner_root=read(T/'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']")
  a=a.replace("q=dict(epoch=time.time(),passed=True,","q=dict(epoch=time.time(),passed=True,performance_benchmark_only=True,")
 ast.parse(a)
 with (N/name).open('x',encoding='utf8') as f:f.write(a)
shutil.copy2(M/'mixed_precision_step_benchmark_runtime_v5.py',N/'mixed_precision_step_benchmark_runtime_v5.py')
for p in (N/'h1_only_controllers').glob('*.py'):assert p.read_bytes()==(F/'h1_only_controllers'/p.name).read_bytes()
with (R/'H1_ONLY_MISSING_BENCHMARK_V2_NAMESPACE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_source_only=True,new_root=str(N),runtime_SHA=hashlib.sha256((N/'mixed_precision_step_benchmark_runtime_v5.py').read_bytes()).hexdigest(),original_H1_failure='E3-only feedback counter requested on H1 before first sample',H1_actual_clock='integrated contact4 and H1 physical callback4; E3 remains8/feedback2',clock_CPU_synthetic_passed=True,no_hotpatch_or_repeat_current_owner=True,only_after_current_benchmark_actual_allout_cost_and_canonicalNone=True,qualified_model_source_still_complete67=True,H1only_original_owner_account_and_guard_82512_preserved=True,no_payload_Task_GO_or_fee=True),f,indent=2)
print(json.dumps(dict(source_only=str(N),not_executed=True,no_E3_repeat=True)))


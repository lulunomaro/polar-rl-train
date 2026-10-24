from pathlib import Path
import ast,hashlib,json,shutil,time
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';F=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V68_20261025'
assert json.loads((R/'APPROVED_TWO_PREUPDATE_RETAINED_ON72_AND_OWN_CACHE_COMPLETE_ACTUAL.json').read_bytes())['passed']
assert json.loads((R/'V7_ACTUAL_INSTALLED_RSL_RUNNER_LEARN_LOGGER_CPU_INTEGRATION_V2_ACTUAL.json').read_bytes())['passed']
N=T/'MOD4_MIXED_PRECISION_PAIRED_RSL_V3_AFTER67_20261025';assert not N.exists();N.mkdir();(N/'reports').mkdir()
for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(F/folder,N/folder)
for name in ('prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py','read_E3_resource_only_after_actual_H1_closed_CPU_once.py','deploy_selected_pair_unused_once.py'):
 a=(F/name).read_text('utf8').replace('H1step270_reward_airfeasible5_2510v68','H1step270_precision_rslv3_after67_2510')
 if name.startswith('prepare_'):
  needle="resource=read(R/'NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json');assert time.time()-resource['epoch']<600";assert a.count(needle)==1
  a=a.replace(needle,needle+"\n benchmark=read(T/'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert benchmark['collector_function_complete'] and benchmark['owner_node_workers_all_actual_out'] and benchmark['original_canonical_cost_settled']")
  a=a.replace("proof['remaining_actual_snapshot']>82512.86069250107","benchmark['original_remaining_closed_snapshot']>82512.86069250107").replace("remaining_after=proof['remaining_actual_snapshot']","remaining_after=benchmark['original_remaining_closed_snapshot']")
  a=a.replace('source_current_cohort_original_cost_summary=proof','source_current_cohort_original_cost_summary=proof,benchmark_original_cost_closure=benchmark,benchmark_only_not_model_qualification=True')
  a=a.replace("previous_owner_root=read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']","previous_owner_root=read(T/'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']")
  a=a.replace('q=dict(epoch=time.time(),passed=True,','q=dict(epoch=time.time(),passed=True,performance_benchmark_only=True,')
 ast.parse(a)
 with (N/name).open('x',encoding='utf8') as f:f.write(a)
shutil.copy2(M/'mixed_precision_step_benchmark_runtime_v7.py',N/'mixed_precision_step_benchmark_runtime_v7.py')
a=(M/'bind_isolated_benchmark_payload_workers_and_manifest_CPU_unused_once.py').read_text('utf8').replace("R/'AMP_BENCHMARK_V3_SCALER_ALLOWLIST_AND_CPU_SYNTHETIC_ACTUAL.json'","M.parent/'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/V7_ACTUAL_INSTALLED_RSL_RUNNER_LEARN_LOGGER_CPU_INTEGRATION_V2_ACTUAL.json'").replace('runtime_v3','runtime_v7')
needle="q=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());assert set(q['specs'])=={'h1','recovery'}";assert a.count(needle)==1
a=a.replace(needle,"qp=R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json'\nwith (R/'PREVIOUS_UNBOUND_M3_CONFIG_EXACT.json').open('xb') as f:f.write(qp.read_bytes())\n"+needle)
needle="B=Path(q['payloads'][key]);oldmanifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());known={r['relative']:r for r in oldmanifest['files']}";assert a.count(needle)==1
a=a.replace(needle,needle+"\n for suffix,p in [('MANIFEST',B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),('TASK',B/'job0/TASK.json')]:\n  with (R/(key.upper()+'_PREVIOUS_UNBOUND_M3_'+suffix+'_EXACT.json')).open('xb') as f:f.write(p.read_bytes())")
a=a.replace("benchmark_complete_updates_per_mode=6,","benchmark_complete_updates_per_mode=6,benchmark_original_H1_trace_and_approved_retention_unchanged=True,phase_timing_CPU_wall_includes_implicit_GPU_wait_not_CUPTI=True,")
ast.parse(a)
with (N/'bind_actual_RSL_V7_paired_benchmark_payload_CPU_unused_once.py').open('x',encoding='utf8') as f:f.write(a)
# Dedicated finite closure collector: never collect benchmark snapshots as qualified models.
a=(M/'collect_benchmark_profile_then_text_cost_allout_V2_unused_once.py').read_text('utf8')
ast.parse(a)
with (N/'collect_benchmark_profile_then_text_cost_allout_V2_unused_once.py').open('x',encoding='utf8') as f:f.write(a)
with (R/'M3_PAIRED_V7_SOURCE_NAMESPACE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,new_source_root=str(N),source_models_latestqualified67=True,closing_owner_and_remaining_from_M_benchmark707s_actual=True,original_owner_node_account_caps_physics_reward_guards_unchanged=True,V7_actual_RSL_ABI_CPU_passed=True,M2_unused_obsolete=True,no_payload_Task_GO_yet=True),f,indent=2)
print(json.dumps(dict(prepared=str(N),qualified_sources='67 only',no_GO=True)))

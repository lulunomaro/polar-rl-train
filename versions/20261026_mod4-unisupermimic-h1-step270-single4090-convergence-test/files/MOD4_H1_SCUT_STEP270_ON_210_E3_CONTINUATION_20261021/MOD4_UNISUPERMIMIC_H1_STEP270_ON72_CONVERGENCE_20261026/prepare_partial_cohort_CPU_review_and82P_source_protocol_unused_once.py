from pathlib import Path
import ast,hashlib,json,time
H=Path(__file__).resolve().parent;T=H.parent;O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026';F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
assert not F.exists();(F/'reports').mkdir(parents=True);(F/'candidates').mkdir()
review=(P/'review_three_expert_complete_models_original_cost_CPU_V5_unused_once.py').read_text('utf8').replace("for key in ('h1','e2','recovery'):","for key in ('h1','recovery'):",1)
needle="    torch.set_num_threads(2);models={}"
review=review.replace(needle,"    failed=co['rows']['e2'];assert failed['original_error'] and failed['terminal_all_own_children_waited'] and not (failed.get('final') or {}).get('passed') and receipt['complete_models']['e2']==[]\n    fc=segment['experts']['e2'];assert fc['duration_bound_passed'] and fc['charged_seconds']>0 and abs(fc['charged_seconds']-(fc['ended_epoch']-fc['started_epoch']))<1e-5\n"+needle,1)
review=review.replace("result=dict(epoch=time.time(),passed=True,models=models,", "result=dict(epoch=time.time(),passed=True,qualification_scope='healthy_h1_recovery_models_with_failed_method_all3_original_cost',failed_method=dict(key='e2',original_error=True,no_qualified_model=True,no_native_policy_update=True,original_terminal=failed,actual_cost=fc),original_slots_cost=segment['experts'],models=models,")
review=review.replace("'THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'","'HEALTHY_PRODUCTION_PAIR_AND_FAILED_METHOD_ORIGINAL_ALL_COST_CPU_ACTUAL.json'")
(O/'review_closed81o_healthy_models_failed_method_and_all_original_cost_CPU_unused_once.py').write_text(review,'utf8')
# Keep the historical metadata helper's exact CRLF bytes; only the authorized guard role changes.
guard=(O/'candidates/same_three_closed_source_V8_landing_journal_CPU_v1.py').read_text('utf8')
guard=guard.replace('THREE_EXPERT_V8_LIFETIME_DIAG_CONTINUATION_AUTH_81N_ACTUAL.json','HEALTHY81O_SAME_V8_CONTINUATION_AUTH_82P_ACTUAL.json')
guard=guard.replace("auth['kind']=='actual_closed_three_same_V8_landing_journal_continuation'","auth['kind']=='actual_closed_healthy_pair_failed_method_all3_cost_same_V8'")
needle="assert set(proof['models'])=={'h1','e2','recovery'} and abs(proof['actual_cost_sumonce']-sum(v['actual_cost']['charged_seconds'] for v in proof['models'].values()))<1e-5"
new="assert key in ('h1','recovery') and proof['qualification_scope']=='healthy_h1_recovery_models_with_failed_method_all3_original_cost' and set(proof['models'])=={'h1','recovery'} and set(proof['original_slots_cost'])=={'h1','e2','recovery'} and proof['failed_method']['original_error'] and proof['failed_method']['no_qualified_model'] and abs(proof['actual_cost_sumonce']-sum(v['charged_seconds'] for v in proof['original_slots_cost'].values()))<1e-5 and all(v['duration_bound_passed'] for v in proof['original_slots_cost'].values())"
assert guard.count(needle)==1;guard=guard.replace(needle,new,1)
(F/'candidates/healthy_pair_failed_method_same_V8_source_guard_v1.py').write_text(guard,'utf8')
(F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py').write_bytes((O/'candidates/same_optimized_source_contract_metadata_candidate_v1.py').read_bytes())
assert hashlib.sha256((F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py').read_bytes()).hexdigest()=='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
report=dict(epoch=time.time(),source_only_new_namespace=str(F),no_payload_model_controller_Task_GO_or_fee=True,candidate_v5_CPU_reports=[str(H/'reports'/n) for n in ('AST_CANDIDATE_V5_CHECKPOINT_BOOTSTRAP_AND_SAMPLING_CONTEXT_ACTUAL.json','ACTUAL_RSL_CHECKPOINT_API_AND_INFERENCE_CONTEXT_CPU_V5_ACTUAL.json','CANDIDATE_V5_PHYSICAL_FORWARDING_AND_SAVE_FAILURE_CPU_ACTUAL.json')],source_only_not_installed=True,healthy_pair_guard_rejects_failed_method_as_source=True,original_three_slot_cost_required=True)
for p in (O/'review_closed81o_healthy_models_failed_method_and_all_original_cost_CPU_unused_once.py',F/'candidates/healthy_pair_failed_method_same_V8_source_guard_v1.py'):ast.parse(p.read_text('utf8'))
(F/'reports/SOURCE_ONLY82P_HEALTHY_PAIR_FAILED_METHOD_PROTOCOL_PREPARATION_ACTUAL.json').write_text(json.dumps(report,indent=2),'utf8')
print(json.dumps(dict(source_only82P=True,partial_cohort_reviewer_prepared=True)))

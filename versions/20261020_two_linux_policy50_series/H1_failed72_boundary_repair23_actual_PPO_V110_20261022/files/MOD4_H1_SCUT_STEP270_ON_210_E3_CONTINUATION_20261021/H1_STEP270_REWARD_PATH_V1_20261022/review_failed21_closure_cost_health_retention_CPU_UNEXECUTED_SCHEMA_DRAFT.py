from pathlib import Path
import json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;N=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V21_20261022';R=B/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 a=read(N/'reports/H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json');s=a['source210'];co=s['cohort'];seg=s['original_segment'];cost=seg['experts']['h1']
 assert a['actual_finite_transport_returned'] and s['all_owner_H1_children_actual_out'] and co['original_cost_settled'] and not a['complete_models']['h1']
 assert set(co['go'])==set(seg['experts'])=={'h1'} and co['rows']['h1']['final'] is None and co['rows']['h1']['original_error']
 assert cost['started_epoch']==co['go']['h1']['learning_started_epoch'] and abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5 and cost['duration_bound_passed']
 prod=N/'current_pair_closed_text/h1/job0/production';error=read(prod/'LEARN_ORIGINAL_ERROR_BEFORE_SAVE.json');prefix=read(prod/'failed_prefix_complete.json');bad=read(next(prod.glob('ACTUAL_BAD_TERRAIN_QUERY_*.json')))
 h=read(next(prod.glob('logs/*/CLOCK_TRAINING_HEALTH.json')));idx=read(prod/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json');hist=read(prod/'control_prefix_raw/PREFIX_PAIR_RETENTION_HISTORY_ACTUAL.json')
 assert error['complete_updates']==prefix['updates']==72 and prefix['failed_partial_prefix'] and prefix['actual17Adam_steps']==[700360]
 assert 'Missing actual wheel terrain query' in error['error'] and bad['actual_bad_rows'][0]['actual_start'][1]>bad['actual_floor_xy_bounds'][1][1]
 assert h['actual_physics_callbacks']!=h['expected_physics_callbacks'];assert h['unknown_task_reset_events']==h['integrity_task_reset_events']==0 and not h['nonfinite_observed']
 # Prior approved removals stay historical removals. Failure preserves all currently present pairs.
 retained=[x['index'] for x in idx['retention_status'] if x['raw_retained']];assert retained==[0,70,71,72] and idx['retention_failure_flag_preserves_all_currently_present_files']
 transactions=hist.get('transactions',[])
 for x in transactions:
  intent=read(prod/'control_prefix_raw'/Path(x['intent']).name);receipt=read(prod/'control_prefix_raw'/Path(x['receipt']).name)
  assert receipt['removed']==x['removed'] and len(intent['files'])==len(receipt['removed'])
 result=dict(epoch=time.time(),passed_only_failed_closure_cost_allout_diagnostic_scope=True,qualified_FINAL=False,models={},failed_diagnostic_prefix=prefix,complete_updates_before_failure=72,actual_cost=cost,actual_cost_sumonce=cost['charged_seconds'],remaining_actual_snapshot=s['original_canonical_remaining'],all_owner_nodes_children_actual_out=True,original_canonical_cost_settled=True,all_scheduled_H1_original_locks_free=True,E3_not_scheduled_or_charged_or_locks_checked=True,original_error=error,actual_bad_query=bad,health=h,partial_control_callback_mismatch_not_relabelled_as_pass=True,retention=dict(producer_entries=len(idx['index']),retained_indices=retained,failure_preserves_currently_present=True,history_transactions=len(transactions),already_pruned_not_recoverable=True),original_reviewer_rejected_no_FINAL=read(N/'reports/V110_ORIGINAL_COMPLETE_REVIEWER_ACTUAL_EXIT_REJECTION.json'),not_production_source_or_skill=True,no_PT_reloading_GPU_or_account_write=True)
 put('V110_FAILED21_ORIGINAL_COST_ALL_OUT_HEALTH_AND_RETENTION_CPU_ACTUAL.json',result)
 print(json.dumps(dict(failed_no_FINAL=True,complete_updates=72,actual_cost_sumonce=cost['charged_seconds'],remaining=s['original_canonical_remaining'],retained=retained)))
except BaseException:put('V110_FAILED_CLOSURE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise

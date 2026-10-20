from pathlib import Path
import hashlib,json,time
from reconcile_exact_closed_E3_pending_CPU import apply_closed
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;F=W/'MOD4_POLICY_50HZ_CONTINUATION_20261020';A=W/'MOD4_E3_AUTOMATIC_CONTINUATION_20261020'
read=lambda p:json.loads(Path(p).read_bytes())
def main():
 boundary=read(F/'reports/collect_policy50_saved_boundary_original_account_V4_missing_once_RETURNED_ACTUAL.json');assert boundary['actual_finite_transport_returned'] and boundary['actual']['boundary_handback']['all_old_single_100Hz_and_current50Hz_own_processes_actual_out'];review=read(F/'reports/review_policy50_second_closed_all_out_original_account_CPU_once_CPU_ACTUAL.json');assert review['passed'] and review['current_window'] is None
 single=read(W/'MOD4_AVAILABLE_E2_E3_HOUR18_20261019/reports/SINGLE_E3_CLOSED_FINAL_WHOLE_MODEL_AND_PENDING_COST_CPU_ACTUAL.json');assert single['passed'];pending={single['pending_cost']['run_id']:single['pending_cost']};sources=[dict(run_id=single['pending_cost']['run_id'],report='SINGLE_E3_CLOSED_FINAL_WHOLE_MODEL_AND_PENDING_COST_CPU_ACTUAL.json')]
 for folder,pattern in ((A/'reports','collect_auto_E3_*_RETURNED_ACTUAL.json'),(F/'reports','collect_policy50_*_RETURNED_ACTUAL.json')):
  for path in sorted(folder.glob(pattern)):
   q=read(path)
   if not q.get('actual_finite_transport_returned'):continue
   for x in q.get('actual',{}).get('complete_finals',[]):
    p=x['pending_cost'];old=pending.get(p['run_id'])
    if old:assert old['cost']==p['cost'] and old['GO']==p['GO']
    else:pending[p['run_id']]=p;sources.append(dict(run_id=p['run_id'],report=str(path),whole_CPU_proof=x['whole_CPU_proof_path'],complete_final=x['producer_final']))
 old=read(A/'reports/collect_auto_E3_new_closed_windows_hourly_V12_once_RETURNED_ACTUAL.json')['actual']['series']['SERIES_CURRENT.json']['completed'];new=boundary['actual']['series']['SERIES_CURRENT.json']['completed'];expected={x['run_id'] for x in old+new}|{single['pending_cost']['run_id']};assert set(pending)==expected and len(old)==15 and len(new)==2 and len(pending)==18
 oldtotal=sum(pending[x['run_id']]['cost']['actual_production_seconds'] for x in old);assert oldtotal==54697.34736418724;assert sum(pending[x['run_id']]['cost']['actual_production_seconds'] for x in new)==review['series_completed_actual_pending_seconds']
 cprobe=read(R/'RETURNED_ORIGINAL_LINUX4090_READONLY_V2_ACTUAL.json')['actual']['original_canonical'];fixture=dict(active_segment=None,authorized_training_seconds=1188000,budget_extensions=[dict(id=str(i)) for i in range(7)],charged_training_seconds=1188000-cprobe['remaining_training_seconds'],remaining_training_seconds=cprobe['remaining_training_seconds'],completed_segments=cprobe['completed_segments']);transaction='E3_CLOSED_OFFLINE_INTERVALS_ONCE_20261020_V32';pcs=sorted(pending.values(),key=lambda x:x['GO']['learning_started_epoch']);after,added=apply_closed(fixture,pcs,transaction)
 payload=dict(epoch=time.time(),transaction_id=transaction,expected_original_canonical_SHA=cprobe['SHA'],expected_original_remaining=cprobe['remaining_training_seconds'],pending=pcs,sources=sources,all_72_old_and_current_series_actual_out_proof=boundary['actual']['boundary_handback'],expected_total_seconds=sum(p['cost']['actual_production_seconds'] for p in pcs),old_single_seconds=single['pending_cost']['cost']['actual_production_seconds'],old100_seconds=oldtotal,policy50_seconds=review['series_completed_actual_pending_seconds'],legacy_Windows9400_and_unknown512_not_in_transaction=True,no_budget_extension_or_refund_or_rounding=True)
 with (R/'EXACT_CLOSED_E3_PENDING_RECONCILIATION_PAYLOAD_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(pending_intervals=len(pcs),exact_sum=payload['expected_total_seconds'],all_own_actual_out=True,dryrun_remaining_snapshot=after['remaining_training_seconds'])))
if __name__=='__main__':main()

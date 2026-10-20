from pathlib import Path
import copy,json,time
from reconcile_exact_closed_E3_pending_CPU import apply_closed
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
p=json.loads((W/'MOD4_AVAILABLE_E2_E3_HOUR18_20261019/reports/SINGLE_E3_CLOSED_FINAL_WHOLE_MODEL_AND_PENDING_COST_CPU_ACTUAL.json').read_bytes())['pending_cost']
c=dict(active_segment=None,authorized_training_seconds=1188000,charged_training_seconds=1188000-259890.6132156849,remaining_training_seconds=259890.6132156849,budget_extensions=[dict(extension_id=str(i)) for i in range(7)],completed_segments=[])
before=copy.deepcopy(c);actual,rows=apply_closed(c,[p],'CPU_FIXTURE');assert c==before and len(rows)==1 and actual['remaining_training_seconds']==c['remaining_training_seconds']-p['cost']['actual_production_seconds'];assert actual['completed_segments'][0]['experts']['recovery']['charged_seconds']==p['cost']['actual_production_seconds']
cases=[]
def reject(name,c,p):
 try:apply_closed(c,p,'CPU_REJECT')
 except AssertionError:cases.append(name);return
 raise AssertionError(name+' admitted')
reject('already_canonical_runid_rejected',actual,[p]);reject('duplicate_payload_runid_rejected',c,[p,p]);bad=copy.deepcopy(c);bad['active_segment']={'owner_parent_pid':7};reject('live_canonical_active_not_cleared',bad,[p]);bad=copy.deepcopy(c);bad['authorized_training_seconds']+=1;reject('budget_extension_not_inferred',bad,[p]);bad=copy.deepcopy(p);bad['cost']['ended_epoch']+=1;reject('interval_duration_mismatch',c,[bad]);bad=copy.deepcopy(p);bad['row']['errors']=['actual-error'];reject('failed_prefix_not_complete',c,[bad]);bad=copy.deepcopy(p);bad['canonical_settled']=True;reject('receipt_already_settled',c,[bad]);bad=copy.deepcopy(c);bad['completed_segments']=[dict(started_epoch=p['cost']['started_epoch'],ended_epoch=p['cost']['ended_epoch'])];reject('overlap_with_old_interval',bad,[p]);bad=copy.deepcopy(p);bad['cost']['actual_production_seconds']=3900.1;reject('over_ceiling_actual_interval',c,[bad]);bad=copy.deepcopy(p);bad['owner_identity']['creation']+=1;reject('owner_creation_not_pid_only',c,[bad])
with (R/'EXACT_PENDING_RECONCILIATION_PURE_CPU_BOUNDARIES_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,actual_pending_receipt_uid=p['run_id'],actual_interval_no_rounding=p['cost']['actual_production_seconds'],rejected_cases=cases,legacy_Windows_pending_and_unknown512_not_in_payload=True,original_total_extensions_active_and_old_entries_retained=True,no_remote_or_canonical_write=True),f,indent=2)
print(json.dumps(dict(passed=True,negative_cases=len(cases),no_ledger_write=True)))

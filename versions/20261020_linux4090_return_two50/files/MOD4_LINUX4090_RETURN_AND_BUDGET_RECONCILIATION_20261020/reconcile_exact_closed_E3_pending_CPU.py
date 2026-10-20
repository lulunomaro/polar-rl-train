"""Pure validation and exact once-only debit of closed E3 intervals; no I/O."""
import copy,math
def apply_closed(canonical,pending,transaction_id):
 assert canonical['active_segment'] is None
 assert canonical['authorized_training_seconds']==1188000 and len(canonical['budget_extensions'])==7
 assert abs(canonical['charged_training_seconds']+canonical['remaining_training_seconds']-1188000)<1e-5
 assert pending and len(pending)==len({x['run_id'] for x in pending})
 existing={x.get('run_id') for x in canonical['completed_segments']}|{x.get('reconciled_pending_run_id') for x in canonical['completed_segments']}
 assert not any(x['run_id'] in existing for x in pending),'Pending run already present: never debit twice'
 c=copy.deepcopy(canonical);added=[]
 for p in sorted(pending,key=lambda x:x['GO']['learning_started_epoch']):
  go=p['GO'];cost=p['cost'];row=p['row'];start=go['learning_started_epoch'];end=cost['ended_epoch'];seconds=cost['actual_production_seconds']
  assert p['canonical_settled'] is False and p['run_id']==go['run_id'] and row['key']=='recovery'
  assert row['phase']=='production' and row['terminal_all_own_children_waited'] and row['returncode']==0 and not row['errors'] and row['final']['passed']
  assert cost['actual_returncode']==0 and cost['duration_bound_passed'] and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
  assert all(math.isfinite(x) for x in (start,end,seconds)) and 0<seconds<=3900 and end>=start and cost['started_epoch']==start and cost['accounted_through_epoch']==end and abs(seconds-(end-start))<1e-5
  assert p['owner_identity']['pid']==go['original_owner_pid'] and abs(p['owner_identity']['creation']-go['original_owner_creation'])<.01
  for s in c['completed_segments']:
   a=s.get('started_epoch');b=s.get('ended_epoch')
   if a is not None and b is not None:assert max(a,start)>=min(b,end),'Pending interval overlaps an existing canonical interval'
  x=dict(started_epoch=start,accounted_through_epoch=end,charged_seconds=seconds,max_parent_seconds=3900,ended_epoch=end,actual_returncode=0,duration_bound_passed=True)
  segment=dict(pid=p['owner_identity']['pid'],owner_parent_pid=p['owner_identity']['pid'],original_owner_creation=p['owner_identity']['creation'],kind='Linux_E3_completed_offline_pending_reconciled',run_id=p['run_id'],reconciled_pending_run_id=p['run_id'],reconciliation_transaction_id=transaction_id,started_epoch=start,ended_epoch=end,accounted_through_epoch=end,charged_expert_seconds=seconds,experts={'recovery':x},charge_contract='Original real GO through owner-received terminal interval; source closed pending receipt, once only',source_SHA=go['source_SHA'],source_pending_cost_was_not_original_canonical_settled=True)
  c['charged_training_seconds']+=seconds;c['remaining_training_seconds']-=seconds;c['completed_segments'].append(segment);added.append(segment)
 assert c['remaining_training_seconds']>=0 and c['active_segment'] is None
 assert c['authorized_training_seconds']==canonical['authorized_training_seconds'] and c['budget_extensions']==canonical['budget_extensions']
 assert c['completed_segments'][:len(canonical['completed_segments'])]==canonical['completed_segments']
 assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5
 return c,added

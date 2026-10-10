"""One immutable complete133 decision/new134 annotation CAS; protect all runtime budget bytes."""
from review133_io import *
import traceback

def main():
 collection=sorted((P/'reports').glob('CURB133_COLLECTED_[0-9]*.json'))[-1];review=sorted((P/'reports').glob('CURB133_SCHEMA_REVIEW_[0-9]*.json'))[-1]
 assert json.loads(review.read_bytes())['review_complete'];assert not (R/'COMPLETE133_SLOPE134_SYNC_STARTED.json').exists()
 save('COMPLETE133_SLOPE134_SYNC_STARTED.json',dict(epoch=time.time(),one_complete_review_and_new_expert_annotation_only=True))
 n,w=connect_both()
 try:
  reports={'E1_CURB20_133_COMPLETE_ACTUAL_COLLECTION.json':collection.read_bytes(),'E1_CURB20_133_COMPLETE_ACTUAL_REVIEW.json':review.read_bytes(),
   'E1_CURB20_133_COMPLETE_SCOPE_DECISION.json':(R/'CURB133_COMPLETE_SCOPE_DECISION.json').read_bytes(),
   'E1_CURB20_133_PREFIX_DIRECTION_ACTUAL_DIAGNOSIS.json':(R/'CURB133_PREFIX_DIRECTION_ACTUAL_DIAGNOSIS.json').read_bytes(),
   'E1_SLOPE5_134_FROZEN_PREPARED.json':(R/'SLOPE5_FROZEN_PREPARED.json').read_bytes(),
   'E1_SLOPE5_134_FROZEN_PUBLISHED.json':(R/'SLOPE134_PUBLISHED.json').read_bytes(),
   'NEXT_E1_SLOPE5_FROZEN_AND_INDEPENDENT_WORK_ORDER.md':(R/'NEXT_E1_SLOPE5_FROZEN_AND_INDEPENDENT_WORK_ORDER.md').read_bytes()}
  with n.open_sftp() as f:
   names=f.listdir(E+'/reports');assert all(name not in names for name in reports)
   current=json.loads(f.open(E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json').read());scope=current['terrain_subexpert_revision004']['curb20_formal_reviewed_scope'];assert scope['root']==NEW and scope['own_formal_complete'] and scope['behavior133_review_pending']
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  receipt=linux_json(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(CENTRAL)/'reports';B=Path(BUDGET);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];scope=rev['curb20_formal_reviewed_scope'];assert scope['root']==ROOT and scope['behavior133_review_pending']
review=json.loads((R/'E1_CURB20_133_COMPLETE_ACTUAL_REVIEW.json').read_bytes());decision=json.loads((R/'E1_CURB20_133_COMPLETE_SCOPE_DECISION.json').read_bytes());published=json.loads((R/'E1_SLOPE5_134_FROZEN_PUBLISHED.json').read_bytes())
assert review['review_complete'] and decision['in_scope_forward_curb_behavior_regression'] and not decision['selected_as_qualified_CURB']
assert hashlib.sha256(budget).hexdigest()==published['actual_authority']['canonical_SHA'] and json.loads(budget)['active_segment'] is None
scope.update(behavior133_review_pending=False,actual_133_collection=str(R/'E1_CURB20_133_COMPLETE_ACTUAL_COLLECTION.json'),actual_133_complete_review=str(R/'E1_CURB20_133_COMPLETE_ACTUAL_REVIEW.json'),actual_133_complete_decision=str(R/'E1_CURB20_133_COMPLETE_SCOPE_DECISION.json'),actual_133_prefix_diagnosis=str(R/'E1_CURB20_133_PREFIX_DIRECTION_ACTUAL_DIAGNOSIS.json'),qualified_CURB=False,more_CURB_learning_admitted=False,candidate_frozen_as_review_evidence_only=True)
rev.update(active_next_expert='E1_SLOPE',curb133_complete_review_unqualified=True,next_independent_work_order=str(R/'NEXT_E1_SLOPE5_FROZEN_AND_INDEPENDENT_WORK_ORDER.md'),slope5_134_frozen_scope=dict(prepared=str(R/'E1_SLOPE5_134_FROZEN_PREPARED.json'),published=str(R/'E1_SLOPE5_134_FROZEN_PUBLISHED.json'),jobs=[x['job_id'] for x in published['jobs']],source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',actual_complete_review_pending=True,learning_executor_deployed=False,new_budget_seconds=0))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE133-SLOPE134-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();append='\n\nLatest actual CURB133 complete review: ascending26/27 source to22/27 own389; descending27/27, ordinary0, five original-positive incomplete prefixes retained. Old signed4pi8/8 each and world64/64 are diagnostic, not qualifiedCURB. No blind CURB900s or height progression. Approved004 independentSLOPE5 new134 actually published, frozen result/fullraw review pending; see NEXT_E1_SLOPE5_FROZEN_AND_INDEPENDENT_WORK_ORDER. source3643c97 selected; own389df0c only frozen review evidence. No newlearningexecutor/canonical delta; localWASD player unaffected.\n'.encode()
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.COMPLETE133-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,complete133_decision_synced=True,new134_frozen_publication_synced=True,active_next_expert='E1_SLOPE',own389_not_qualified_or_retrained=True,master_approval_tracks_RM_canonical_bytes_preserved=True,no_PPO_or_4090_launch=True,canonical_sha256=hashlib.sha256(budget).hexdigest(),remaining_seconds=json.loads(budget)['authorized_training_seconds']-json.loads(budget)['charged_training_seconds'])))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  p=save('COMPLETE133_SLOPE134_METADATA_SYNCED.json',receipt)
  with n.open_sftp() as f:put(f,E+'/reports/E1_CURB20_133_COMPLETE_AND_SLOPE134_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(receipt))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE133_SLOPE134_SYNC_ERROR.json',dict(error=traceback.format_exc(),no_blind_replay_or_overwrite=True));raise

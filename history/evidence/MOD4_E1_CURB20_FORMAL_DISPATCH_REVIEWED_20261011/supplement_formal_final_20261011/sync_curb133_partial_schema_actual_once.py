"""Latest completed actual flat case/schema reader report, metadata only."""
from stage_formal_dispatch_reviewed_once import D,R,E,B,NEW,connect_both,cleanup,put,linux_json,save,H
import json,time,traceback
def main():
 assert not (R/'CURB133_PARTIAL_SCHEMA_SYNC_STARTED.json').exists()
 collection=sorted(R.glob('CURB133_COLLECTED_[0-9]*.json'))[-1];review=sorted(R.glob('CURB133_SCHEMA_REVIEW_[0-9]*.json'))[-1]
 v=json.loads(review.read_bytes());assert not v['review_complete'] and set(v['retention'])=={'flat'} and len(v['pending'])==3
 save('CURB133_PARTIAL_SCHEMA_SYNC_STARTED.json',dict(epoch=time.time(),new_actual_flat_and_schema_review_only=True))
 n,w=connect_both()
 try:
  reports={'E1_CURB20_133_CURRENT_COLLECTION.json':collection.read_bytes(),'E1_CURB20_133_PARTIAL_ACTUAL_SCHEMA_REVIEW.json':review.read_bytes(),'E1_CURB20_133_ACTUAL_SCHEMA_READER_REVIEW.json':(R/'CURB133_ACTUAL_SCHEMA_READER_REVIEW.json').read_bytes()}
  with n.open_sftp() as f:
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  receipt=linux_json(n,r'''from pathlib import Path
import json,time,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);scope=v['terrain_subexpert_revision004']['curb20_formal_reviewed_scope']
assert scope['root']==ROOT and scope['own_formal_complete'] and scope['behavior133_review_pending']
q=json.loads((R/'E1_CURB20_133_PARTIAL_ACTUAL_SCHEMA_REVIEW.json').read_bytes());assert not q['review_complete'] and set(q['retention'])=={'flat'}
scope.update(actual_133_partial_review=str(R/'E1_CURB20_133_PARTIAL_ACTUAL_SCHEMA_REVIEW.json'),actual_133_schema_reader_review=str(R/'E1_CURB20_133_ACTUAL_SCHEMA_READER_REVIEW.json'),actual_133_reader='review_formal_reviewed_curb133_schema_actual.py',behavior133_review_pending=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.CURB133SCHEMA-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,actual133_complete_flat_only=True,remaining_three_case_review_pending=True,reader_schema_error_original_retained=True,source_result_runtime_and_own_checkpoint_SHA_bound=True,master_approval_tracks_RM_canonical_bytes_preserved=True,no_GPU_queue_or_PPO_action=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  p=save('CURB133_PARTIAL_ACTUAL_SCHEMA_METADATA_SYNCED.json',receipt)
  with n.open_sftp() as f:put(f,E+'/reports/E1_CURB20_133_PARTIAL_ACTUAL_SCHEMA_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(receipt))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('CURB133_PARTIAL_SCHEMA_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_blind_replay=True));raise

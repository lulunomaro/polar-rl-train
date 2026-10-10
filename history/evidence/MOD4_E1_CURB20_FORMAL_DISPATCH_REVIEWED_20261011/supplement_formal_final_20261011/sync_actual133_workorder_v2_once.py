"""New post-final actual389 review workorder only; no old sync/GPU replay."""
from stage_formal_dispatch_reviewed_once import R,E,B,NEW,connect_both,cleanup,linux_json,put,save
import json,time,traceback
def main():
 assert not (R/'CURB389_REVIEW_WORKORDER_V2_SYNC_STARTED.json').exists()
 save('CURB389_REVIEW_WORKORDER_V2_SYNC_STARTED.json',dict(epoch=time.time(),new_workorder_only=True))
 n,w=connect_both()
 try:
  with n.open_sftp() as f:put(f,E+'/reports/NEXT_E1_CURB20_133_ACTUAL_REVIEW_WORK_ORDER_V2.md',(R/'NEXT_E1_CURB20_133_ACTUAL_REVIEW_WORK_ORDER_V2.md').read_bytes())
  v=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
j=lambda p:json.loads(p.read_bytes());p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);scope=v['terrain_subexpert_revision004']['curb20_formal_reviewed_scope']
assert scope['root']==ROOT and scope['own_formal_complete'] and scope['behavior133_review_pending']
assert j(B)['active_segment'] is None and j(B)['authorized_training_seconds']==828000
name='NEXT_E1_CURB20_133_ACTUAL_REVIEW_WORK_ORDER_V2.md';assert name not in str(scope.get('next_actual_review_work_order',''))
scope['next_actual_review_work_order']=str(R/name);scope['actual_review_work_order_v2_synced_epoch']=time.time()
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.CURB389WO-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),synced=True,work_order=str(R/name),work_order_sha256=hashlib.sha256((R/name).read_bytes()).hexdigest(),master_approval_tracks_RM_canonical_bytes_preserved=True,no_learning_or_queue_action=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  p=save('CURB389_REVIEW_WORKORDER_V2_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:put(f,E+'/reports/E1_CURB20_FORMAL_REVIEWED_WORKORDER_V2_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(v))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('CURB389_REVIEW_WORKORDER_V2_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_blind_replay=True));raise

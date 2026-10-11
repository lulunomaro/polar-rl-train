from slope_io import *
import traceback
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
def main():
 save('SNAPSHOT_SCOPE_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True,old402_error_and_cost_retained=True))
 actual=sorted(R.glob('SLOPE_SNAPSHOT_ACTUAL_[0-9]*.json'))[-1]
 reports={'E1_SLOPE5_402_PRELEARN_SNAPSHOT_REJECTION_ACTUAL.json':(R/'SNAPSHOT_FULL_RECEIPTS_402_FAILURE_ACTUAL.json').read_bytes(),'E1_SLOPE5_SNAPSHOT_REVIEWED_TARGET_CPU_VERIFIED.json':(R/'SNAPSHOT_REPAIR_TARGET_CPU_PASSED.json').read_bytes(),'E1_SLOPE5_SNAPSHOT_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json':(R/'SNAPSHOT_DISPATCH_ACTUAL_RECEIPT.json').read_bytes(),'E1_SLOPE5_SNAPSHOT_REVIEWED_CURRENT_ACTUAL.json':actual.read_bytes(),'NEXT_E1_SLOPE5_SNAPSHOT_REVIEWED_AND_135_WORK_ORDER.md':(R/'NEXT_SLOPE_SNAPSHOT_REVIEWED_AND_135_WORK_ORDER.md').read_bytes()}
 n,w=connect_both()
 try:
  with n.open_sftp() as f:
   names=f.listdir(E+'/reports');assert all(k not in names for k in reports)
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  row=linux_json(n,r'''from pathlib import Path
import json,hashlib,time,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);beforeB=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE';s=rev['slope5_independent_scope'];assert s['root']=='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_INDEPENDENT_20261011'
s.update(previous402_scope=dict(root=s['root'],failed_before_PPO_snapshot_literal=True,original_error_and_unique_cost_retained=True,actual_rejection=str(R/'E1_SLOPE5_402_PRELEARN_SNAPSHOT_REJECTION_ACTUAL.json')),root=ROOT,source_count=404,actual_current=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_CURRENT_ACTUAL.json'),actual_dispatch=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json'),actual_target_CPU=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_TARGET_CPU_VERIFIED.json'),SDK_native_small_exact_reused=True,big_freshresume_and_formal_pending_at_snapshot=True,actual_collector='collect_slope_snapshot135_actual.py',actual_reviewer='review_slope135_actual.py',next_actual_work_order=str(R/'NEXT_E1_SLOPE5_SNAPSHOT_REVIEWED_AND_135_WORK_ORDER.md'),ownformal_and135_review_required=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SLOPE404-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
a=json.loads(beforeB);b=json.loads(B.read_bytes());assert a['authorized_training_seconds']==b['authorized_training_seconds']==828000 and b['charged_training_seconds']>=a['charged_training_seconds'];assert all((R/k).read_bytes()==raw for k,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,new404_scope_and_old402_error_refs=True,master_approval_tracks_RM_bytes_preserved=True,no_budget_write=True,normal_original_parent_accounting_allowed=True,canonical_before_SHA=hashlib.sha256(beforeB).hexdigest(),canonical_after_SHA=hashlib.sha256(B.read_bytes()).hexdigest())))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  rp=save('SNAPSHOT_SCOPE_METADATA_SYNCED.json',row)
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE5_SNAPSHOT_REVIEWED_SCOPE_METADATA_SYNCED.json',rp.read_bytes())
  print(json.dumps(row))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SNAPSHOT_SCOPE_SYNC_ERROR.json',dict(error=traceback.format_exc(),no_blind_sync_replay=True));raise

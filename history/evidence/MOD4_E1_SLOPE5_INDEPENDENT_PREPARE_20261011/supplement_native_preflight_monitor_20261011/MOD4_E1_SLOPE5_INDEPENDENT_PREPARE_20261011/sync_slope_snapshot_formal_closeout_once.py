from slope_io import *
import traceback
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
def main():
 ownp=sorted(R.glob('SNAPSHOT_OWN_FORMAL_CPU_[0-9]*.json'))[-1];own=json.loads(ownp.read_bytes());assert not own['pending'] and own['ready'] and own['canonical']['active'] is None
 assert all(x['actual'] is None or x['actual']['state']=='Z' for x in own['actual_parent_guardian_child']) and all(x['free'] for x in own['two_real_OS_locks'])
 actualp=sorted(R.glob('SLOPE_SNAPSHOT_ACTUAL_[0-9]*.json'))[-1];actual=json.loads(actualp.read_bytes());assert actual['phase']=='E1_SLOPE5_independent_saved_review_ready'
 collection=sorted(R.glob('SLOPE135_COLLECTED_[0-9]*.json'))[-1];col=json.loads(collection.read_bytes());assert 'actual_worker' in col
 review=dict(epoch=time.time(),formal_own_save_and_unique_exit_CPU_reviewed=True,formal_PASSED=own['formal_PASSED'],own_checkpoint=own['checkpoint'],actual_snapshot_count=own['actual_snapshot_count'],source_count=404,actual_parent_guardian_child=own['actual_parent_guardian_child'],two_OS_locks=own['two_real_OS_locks'],canonical=own['canonical'],full135_behavior_review_pending=True,qualified_SLOPE_claimed=False,gate_trained=False,all_courses_finished=False,no_more_PPO_without135_fullreview=True)
 rp=save('SNAPSHOT_FORMAL_FINAL_ACTUAL_REVIEW.json',review);save('SNAPSHOT_FORMAL_CLOSEOUT_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True))
 reports={'E1_SLOPE5_SNAPSHOT_REVIEWED_FORMAL_FINAL_ACTUAL_REVIEW.json':rp.read_bytes(),'E1_SLOPE5_SNAPSHOT_REVIEWED_OWN_FORMAL_CPU_VERIFIED.json':ownp.read_bytes(),'E1_SLOPE5_SNAPSHOT_REVIEWED_FORMAL_FINAL_CURRENT_ACTUAL.json':actualp.read_bytes(),'E1_SLOPE5_135_ACTUAL_CURRENT_COLLECTION.json':collection.read_bytes(),'E1_SLOPE5_SNAPSHOT_REVIEWED_STAGE_GIT_RECORDED.json':(R/'SNAPSHOT_REPAIR_STAGE_GIT_RECORDED.json').read_bytes(),'E1_SLOPE5_SNAPSHOT_REVIEWED_MONITOR_ACTUAL_VERIFIED.json':(R/'SNAPSHOT_MONITOR_ACTUAL_VERIFIED.json').read_bytes(),'E1_SLOPE5_SNAPSHOT_REVIEWED_COMPLETE_PREFLIGHT_ACTUAL_REVIEW.json':(R/'SNAPSHOT_COMPLETE_PREFLIGHT_ACTUAL_REVIEW.json').read_bytes()}
 n,w=connect_both()
 try:
  with n.open_sftp() as f:
   names=f.listdir(E+'/reports');assert all(x not in names for x in reports)
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  row=linux_json(n,r'''from pathlib import Path
import json,hashlib,time,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);beforeB=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE';s=rev['slope5_independent_scope'];assert s['root']==ROOT
own=json.loads((R/'E1_SLOPE5_SNAPSHOT_REVIEWED_OWN_FORMAL_CPU_VERIFIED.json').read_bytes());s.update(actual_current=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_FORMAL_FINAL_CURRENT_ACTUAL.json'),actual_own_final_CPU=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_OWN_FORMAL_CPU_VERIFIED.json'),formal_final_actual_review=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_FORMAL_FINAL_ACTUAL_REVIEW.json'),actual_135_collection=str(R/'E1_SLOPE5_135_ACTUAL_CURRENT_COLLECTION.json'),actual_own_checkpoint=own['checkpoint'],actual_snapshot_count=own['actual_snapshot_count'],formal_actual_saved_exit_CPU_PASSED=True,big_freshresume_and_formal_pending_at_snapshot=False,ownformal_and135_review_required=True,actual_135_fullreview_pending=True,qualified_SLOPE=False,automatic_more_PPO_disallowed=True,stage_git_receipt=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_STAGE_GIT_RECORDED.json'),monitor_receipt=str(R/'E1_SLOPE5_SNAPSHOT_REVIEWED_MONITOR_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SLOPE404FINAL-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';hb=hp.read_bytes();add=('\n\nSLOPE404实际formal完整保存/CPU102/ownPID/PASSED/唯一账段/父guardian孩子自然退出/两OS锁free已核。中央E1_SLOPE5_SNAPSHOT_REVIEWED_FORMAL_FINAL_ACTUAL_REVIEW与OWN_FORMAL_CPU_VERIFIED、E1_SLOPE5_135_ACTUAL_CURRENT_COLLECTION优先。135完整四case实际review前不更多PPO或升坡度，reviewready不是全课程finished。402原prelearn快照列表失败与全部成本保留，SDK/native/small exactSHA复用，无旧once重跑或预算扩展。\n').encode();assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.SLOPE404FINAL-'+str(time.time_ns()));tmp.write_bytes(hb+add);os.replace(tmp,hp)
assert B.read_bytes()==beforeB and json.loads(beforeB)['active_segment'] is None;assert all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,own_formal_saved_review_ready_and135_actual_collection_refs=True,master_approval_tracks_RM_canonical_bytes_preserved=True,canonical_SHA=hashlib.sha256(beforeB).hexdigest(),no_GPU_or_PPO_or_budget_action=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  p=save('SNAPSHOT_FORMAL_CLOSEOUT_METADATA_SYNCED.json',row)
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE5_SNAPSHOT_REVIEWED_FORMAL_CLOSEOUT_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(row))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SNAPSHOT_FORMAL_CLOSEOUT_SYNC_ERROR.json',dict(error=traceback.format_exc(),no_old_sync_replay=True));raise

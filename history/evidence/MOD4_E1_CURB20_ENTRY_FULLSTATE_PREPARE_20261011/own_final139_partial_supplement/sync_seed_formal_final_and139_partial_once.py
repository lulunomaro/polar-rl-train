"""Append actual own closeout and139 partial facts; no runtime/budget/old-report writes."""
from pathlib import Path
import sys,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
def latest(prefix):return max((p for p in R.glob(prefix+'*.json') if p.stem.removeprefix(prefix).isdigit()),key=lambda p:int(p.stem.removeprefix(prefix)))
def main():
 names={'E1_CURB20_ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW.json':latest('ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW_'),'E1_CURB20_ENTRY_SEED_OWN_FORMAL_CPU_VERIFIED.json':latest('ENTRY_SEED_OWN_FORMAL_CPU_ACTUAL_'),'E1_CURB20_ENTRY_SEED_FORMAL_FINAL_CURRENT_ACTUAL.json':latest('ENTRY_SEED_ACTUAL_'),'E1_CURB20_ENTRY139_CURRENT_ACTUAL_COLLECTION.json':latest('CURB139_COLLECTED_'),'E1_CURB20_ENTRY139_PARTIAL_ACTUAL_REVIEW.json':latest('CURB139_SCHEMA_REVIEW_'),'E1_CURB20_ENTRY_FINAL_READER_CPU_ENVIRONMENT_REVIEW.json':R/'ENTRY_FINAL_READER_CPU_ENVIRONMENT_REVIEW.json','E1_CURB20_ENTRY_STAGE_GIT_RECORDED.json':R/'STAGE_GIT_RECORDED.json'}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   assert not set(names)&set(f.listdir(io.E+'/reports'))
   for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';j=lambda p:json.loads(p.read_bytes())
final=j(R/'E1_CURB20_ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW.json');cpu=j(R/'E1_CURB20_ENTRY_SEED_OWN_FORMAL_CPU_VERIFIED.json');collection=j(R/'E1_CURB20_ENTRY139_CURRENT_ACTUAL_COLLECTION.json');partial=j(R/'E1_CURB20_ENTRY139_PARTIAL_ACTUAL_REVIEW.json')
assert final['formal_final_actual'] and final['active_Sactive_empty'] and cpu['passed'] and cpu['actual_source_count']==410 and cpu['actual_snapshot_file_count']==87
assert cpu['own_checkpoint']['sha256']==final['own']['checkpoint']['sha256'] and final['canonical_total_seconds']==1188000 and final['budget_extensions']==7
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')};B=Path(BUDGET);budget_before=B.read_bytes()
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_CURB'
scope=rev['curb20_entry_seed_reviewed_scope'];assert scope['root']==ROOT and scope['source_count']==410
scope.update(actual_formal_final=str(R/'E1_CURB20_ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW.json'),own_formal_CPU_verified=str(R/'E1_CURB20_ENTRY_SEED_OWN_FORMAL_CPU_VERIFIED.json'),actual_formal_current=str(R/'E1_CURB20_ENTRY_SEED_FORMAL_FINAL_CURRENT_ACTUAL.json'),formal_final_pending=False,actual_current_phase='E1_CURB20_entry_repair_saved_review_ready',own_checkpoint=cpu['own_checkpoint'],actual_unique_formal_seconds=final['unique_formal_load_learn_save_exit_seconds'],actual_snapshot_file_count=87,actual_natural_parent_guardian_child_exits=True,two_OS_locks_free=True,actual_139_collection=str(R/'E1_CURB20_ENTRY139_CURRENT_ACTUAL_COLLECTION.json'),actual_139_partial_review=str(R/'E1_CURB20_ENTRY139_PARTIAL_ACTUAL_REVIEW.json'),actual_139_complete_cases=list(collection['cases']),actual_139_pending=collection['pending'],actual_139_review_complete=partial['review_complete'],stage_Git=str(R/'E1_CURB20_ENTRY_STAGE_GIT_RECORDED.json'),more_PPO_requires_complete139_scope_decision=True,qualified_CURB=False)
rev.update(active_next_phase='CURB20_entry_own_saved_waiting_complete139_actual_review',monitor_cadence_minutes=30)
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRYFINAL-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nSource410 CURB20 entry bounded formal own final is actually saved and reviewed: model32069 SHA2fe67400d4119b94dbf33d7770b7fec44a9c73c568256e8161c3d8298ad73a04, CPU102, source410, 87actual snapshots, PID2748108, unique330.20350074768066s originalparent settled once. 7updates168controls3360000envsteps672callbacks, ordinary/integrity/unknown0, nonfinitefalse, STOPnone; ownhealth truncation union1977 (1693timeout/285route overlap1), bothcoverageexact. Natural actualparentguardianchild exits and twofcntl locksfree/active-Sactiveempty are a legal course review boundary, not allcourses finished. 139 fourcases actually autopublished; oneflat complete/errorfree crosshostbytesexact and exact132/115/129 contracts, other3actualpending. Flat signed1.5 errors .020799875/.046490490m/s, originalstrictfalse retained. No morePPO orheight upgrade beforecomplete ownCURB/contact/fullsignedcircle scope decision. New stdlibreader Torch-import failure retained as reader-only; independent admittedCPU environment completed same immutable facts, noGPU replay. Stagef54c1909/tagbf258 verified, laterreports requireordinary Git supplement. Same30minACTIVE quiethealthy monitor; no newbudget, no WASD actions.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRYFINAL-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert all((R/x).read_bytes()==b for x,b in protected.items()) and B.read_bytes()==budget_before
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,scope=scope,protected_master_approval_tracks_RM_exact=True,canonical_bytes_preserved=True,canonical_writer_actions=0,old_reports_preserved=True,reader_only_error_not_physical_failure=True)))
'''.replace('CENTRAL',repr(io.E)).replace('BUDGET',repr(io.B)).replace('ROOT',repr(NEW)))
  p=save('ENTRY_SEED_FINAL_CLOSEOUT_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_CURB20_ENTRY_SEED_FINAL_CLOSEOUT_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(dict(metadata_synced=True,own_final=True,complete139=v['scope']['actual_139_complete_cases'],remaining139=len(v['scope']['actual_139_pending']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_SEED_FINAL_METADATA_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise

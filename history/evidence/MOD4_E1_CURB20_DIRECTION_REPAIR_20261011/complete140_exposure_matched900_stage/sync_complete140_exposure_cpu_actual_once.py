from direction_io import *
import traceback
from prepare_direction140_decision_and_exposure_continuation_once import OLDROOT,ROOT

def main():
 n,w=io.connect_both()
 try:
  paths={'E1_CURB20_DIRECTION140_COMPLETE_ACTUAL_COLLECTION.json':sorted(R.glob('CURB140_COLLECTED_[0-9]*.json'))[-1],
   'E1_CURB20_DIRECTION140_COMPLETE_ACTUAL_REVIEW.json':sorted(R.glob('CURB140_SCHEMA_REVIEW_[0-9]*.json'))[-1],
   'E1_CURB20_DIRECTION140_COMPLETE_SCOPE_DECISION.json':R/'CURB140_COMPLETE_SCOPE_DECISION.json',
   'E1_CURB20_DIRECTION140_PREFIX_EXPOSURE_ACTUAL_DIAGNOSIS.json':R/'CURB140_COMPLETE_PREFIX_EXPOSURE_DIAGNOSIS.json',
   'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_TARGET_CPU_VERIFIED.json':R/'EXPOSURE_MATCHED_TARGET_CPU_PASSED.json',
   'NEXT_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_WORK_ORDER.md':R/'NEXT_DIRECTION_EXPOSURE_MATCHED_WORK_ORDER.md'}
  with n.open_sftp() as f:
   for name,p in paths.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os,fcntl
E=Path(CENTRAL_PATH_TOKEN);R=E/'reports';B=Path(BUDGET_PATH_TOKEN);old=Path(OLD_ROOT_TOKEN);D=Path(NEW_ROOT_TOKEN);j=lambda p:json.loads(p.read_bytes())
review=j(R/'E1_CURB20_DIRECTION140_COMPLETE_ACTUAL_REVIEW.json');assert review['review_complete'] and not review['pending']
dec=j(R/'E1_CURB20_DIRECTION140_COMPLETE_SCOPE_DECISION.json');assert not dec['qualified_CURB'] and dec['allow_one_exposure_duration_only_continuation']
cpu=j(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_TARGET_CPU_VERIFIED.json');assert cpu['passed'] and cpu['source_count']==424
st=j(old/'reports/E1_STATE.json');receipt=j(old/'reports/e1_CURB20_direction_repair_observation_PASSED.json');assert st['child'] is None and st['phase']=='E1_CURB20_direction_repair_saved_review_ready'
for loc in (st['owner'],j(old/'reports/E1_GUARDIAN_STARTED.json'),receipt['own_PID_bound_receipt']):
 p=Path('/proc')/str(loc['pid'])
 if p.exists():
  z=(p/'stat').read_text().split(') ',1)[1].split();assert z[0]=='Z' or int(z[19])!=loc.get('start_ticks')
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
bb=B.read_bytes();b=json.loads(bb);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);rev=c['terrain_subexpert_revision004'];scope=rev['curb20_entry_command_axis_next_scope'];assert scope['root']==str(old) and scope['source_count']==423
scope.update(actual_140_review_complete=True,actual_140_complete_collection=str(R/'E1_CURB20_DIRECTION140_COMPLETE_ACTUAL_COLLECTION.json'),actual_140_complete_review=str(R/'E1_CURB20_DIRECTION140_COMPLETE_ACTUAL_REVIEW.json'),actual_140_complete_scope_decision=str(R/'E1_CURB20_DIRECTION140_COMPLETE_SCOPE_DECISION.json'),actual_140_prefix_exposure_diagnosis=str(R/'E1_CURB20_DIRECTION140_PREFIX_EXPOSURE_ACTUAL_DIAGNOSIS.json'),qualified=False)
assert 'curb20_direction_exposure_matched_scope' not in rev
rev['curb20_direction_exposure_matched_scope']=dict(root=str(D),source_count=424,phase='CPU_admitted_dispatch_pending',selected_source=cpu['selected_checkpoint'],target_seconds=900,only_duration_axis=True,CPU_verified=str(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_TARGET_CPU_VERIFIED.json'),qualified=False,more_PPO_requires_candidate141_complete=True,next_work_order=str(R/'NEXT_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_WORK_ORDER.md'))
rev.update(active_next_expert='E1_CURB',active_next_phase='CURB20_direction_exposure_matched_CPU_admitted',monitor_cadence_minutes=60)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE140-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';before=p.read_bytes();text='\n\nActualcomplete140 full4case/twohost8JSON byteexact/fullraw reviewed: own423 e6df CPU104, up23/27 down27/27 ordinary0, originalpositive incomplete3/6/15/36 turning/lateral validprefixes, route48. Negative4pi7to3/8 diagnostic decline kept, positive8/8/world64/64. NoqualifiedCURB or E0/gate failure claim. Fullformalcommandtrace168control=1.68s, entryoffset.8/1.65m, nominalmaximum.504m; actualroot no centersidecross, bothsigned/standing coverage valid. Prephysics/after-update histogram endpoints exactly reconciled, originalreader failures retained. Exposurehypothesis only, notcausalproof. One approved005 same-scope900s continuation selectedown423 explicitly, newisolatedsource424 CPU admitted/dispatchpending, original423 allbytes intact plusonecontroller. FullSDK/native/small/big/fresh/clock exactSHA reuse, no replay. Samegeometry-entry-direction startup strict exact/CUDA/episode+1; uniqueownsave then new1414case review mandatory, noautomaticthirdblock. Oldactualexits/twofcntl-free/uniqueclosed330.210305929s; sole330h7extensions unchanged; E0/Wave/SLOPE/player untouched, hourlyquietmonitor. Allsavedreports/errors/Git receipts appended.\n';assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE140-'+str(time.time_ns()));tmp.write_bytes(before+text.encode());os.replace(tmp,p)
assert B.read_bytes()==bb and all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),metadata_synced=True,complete140_review=True,new_root=str(D),new_source_count=424,new_CPU_passed=True,new_dispatch_pending=True,old423_naturally_exited_and_unique_closed=True,protected_master_approval_tracks_RM_canonical_bytes_exact=True,no_GPU_PPO_or_budget_write=True)
q=R/'E1_CURB20_DIRECTION140_COMPLETE_AND_EXPOSURE_CPU_METADATA_SYNCED.json';assert not q.exists();q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL_PATH_TOKEN',repr(io.E)).replace('BUDGET_PATH_TOKEN',repr(io.B)).replace('OLD_ROOT_TOKEN',repr(OLDROOT)).replace('NEW_ROOT_TOKEN',repr(ROOT)))
  save('COMPLETE140_AND_EXPOSURE_CPU_METADATA_SYNCED.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE140_CPU_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),old_sync_not_replayed=True));raise

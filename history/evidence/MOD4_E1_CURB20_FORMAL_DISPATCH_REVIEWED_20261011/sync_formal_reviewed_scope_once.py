"""New386 effective annotation, retain failed384 scope/history and all frozen plans."""
from stage_formal_dispatch_reviewed_once import D,R,E,B,NEW,connect_both,cleanup,linux_json,save,put
import json,time,traceback
def main():
 path=sorted(R.glob('FORMAL_REVIEWED_ACTUAL_[0-9]*.json'))[-1];a=json.loads(path.read_bytes());assert a['root']==NEW
 save('FORMAL_REVIEWED_SCOPE_SYNC_STARTED.json',dict(epoch=time.time(),new_scope_annotation_only=True,no_GPU_canonical_or_old_sync_replay=True))
 n,w=connect_both()
 try:
  files={'E1_CURB20_FORMAL_REVIEWED_CURRENT_ACTUAL.json':path.read_bytes(),'E1_CURB20_FORMAL_REVIEWED_TARGET_CPU_VERIFIED.json':(R/'FORMAL_DISPATCH_TARGET_CPU_PASSED.json').read_bytes(),'E1_CURB20_FORMAL_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json':(R/'FORMAL_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').read_bytes(),'E1_CURB20_FRESH_RESTORE_LOGGER_REJECTION_REVIEW.json':(R/'FRESH_PROCESS_ACTUAL_FULLRESUME_THEN_LOGGER_REJECTION.json').read_bytes()}
  with n.open_sftp() as f:
   for name,raw in files.items():put(f,E+'/reports/'+name,raw)
  v=linux_json(n,r'''from pathlib import Path
import json,time,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};j=lambda p:json.loads(p.read_bytes())
a=j(R/'E1_CURB20_FORMAL_REVIEWED_CURRENT_ACTUAL.json');cpu=j(R/'E1_CURB20_FORMAL_REVIEWED_TARGET_CPU_VERIFIED.json');assert a['root']==ROOT and cpu['passed'] and cpu['source_count']==389 and cpu['original_zero_step_guard_unchanged_and_reached_before_logger_failure']
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();v=json.loads(old);revision=v['terrain_subexpert_revision004'];assert revision['approved'] and revision['active_next_expert']=='E1_CURB' and 'curb20_formal_reviewed_scope' not in revision
revision['curb20_formal_reviewed_scope']=dict(epoch=time.time(),root=ROOT,source_count=389,source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',actual_phase_at_sync=a['reports']['E1_STATE.json']['phase'],current_actual=str(R/'E1_CURB20_FORMAL_REVIEWED_CURRENT_ACTUAL.json'),target_CPU=str(R/'E1_CURB20_FORMAL_REVIEWED_TARGET_CPU_VERIFIED.json'),new_fullstate_PPO_preflight_complete='E1_COMPLETE_PPO_PREFLIGHT_PASSED.json' in a['reports'],own_formal_complete='e1_CURB20_independent_observation_PASSED.json' in a['reports'],requires_complete133_behavior_review=True,SDK_native_small_big_PPO_exact_reused=True,old380_prelearn_and384_postlearn_failures_preserved=True,no_more_PPO_automatic=True,new_budget_seconds=0,E0_Wave_protected=True,gate_untrained=True)
revision['curb20_fresh_process_scope']['fresh_restore_completed_before_logger_save_rejection']=True;revision['curb20_fresh_process_scope']['superseded_by_formal_reviewed_scope']=ROOT
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.CURB389-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='CURB389 fresh-process-only restore actual:';assert marker.encode() not in old
msg='\n\n'+marker+' '+ROOT+'; phase '+a['reports']['E1_STATE.json']['phase']+'. Prior384 completed4 PPO updates/96controls/1.92Msteps/384callbacks saved7f1, then strict zero-step startup rejected attempted restoration in already-stepped env; originalfalse/raw/error and unique291.510988474s retained. New389 preserves388 sourcebytes; copied old main was inadvertently dispatched on388 restoreonly, originalinvalidattempt kept, ownparent/guardian/child naturalexit required before correctedwrapper formal, verifies saved discardedCURB CPU102, actual386 freshprocess sameCURB fullrestore/noPPO/noadditionalcontrols passed, subsequent optionalzeroPPOsave failed because loggerwriter not initialized. New388 CPU ties completed384 fullsave and386 actualfullrestore eight receipts/source/PID/zero-counter/exactpartialactoroptimizer together; oldprobe failure/partialfile retained. No further GPU preflight; only300s formal from complete129 source3c97. SDK/native/small/big completed learning not repeated. Fullsave/133complete review required, no automatic next block or height. All prior once excluded; actualprocess/source/PID/fullsave/PASSED/one segment priority; annotation only, immutable master/approval/tracks/RM/canonical authorization unchanged.\n'
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CURB389-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert all((R/n).read_bytes()==b for n,b in protected.items()) and j(B)['authorized_training_seconds']==828000
print(json.dumps(dict(epoch=time.time(),new_fresh_process_scope_metadata_synced=True,actual_phase=a['reports']['E1_STATE.json']['phase'],master_approval_tracks_RM_bytes_preserved=True,no_canonical_write=True,original_failed384_retained_not_pass_relabel=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  p=save('FORMAL_REVIEWED_SCOPE_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:put(f,E+'/reports/E1_CURB20_FORMAL_REVIEWED_SCOPE_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(v))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('FORMAL_REVIEWED_SCOPE_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_sync_replay=True));raise

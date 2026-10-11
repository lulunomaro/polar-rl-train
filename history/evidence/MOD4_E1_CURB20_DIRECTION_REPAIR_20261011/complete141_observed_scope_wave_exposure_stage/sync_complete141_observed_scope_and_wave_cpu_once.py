"""Append new final/complete evidence and CAS current metadata at actual idle boundary."""
from direction_io import *
import tomllib,traceback

def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 req=json.loads((R/'COMPLETE141_WAVE_NEXT_MONITOR_REQUEST.json').read_bytes())
 assert t['status']==req['status']=='ACTIVE' and t['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and t['target_thread_id']==req['targetThreadId']
 assert t['prompt'].replace('\r\n','\n').rstrip('\n')==req['prompt'].replace('\r\n','\n').rstrip('\n')
 mon=save('COMPLETE141_WAVE_NEXT_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),status=t['status'],rrule=t['rrule'],same_target=True,prompt_SHA=H(t['prompt'].encode()),hourly_ACTIVE_healthy_pending_silent=True))
 files={
 'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_OWN_FINAL_CPU_VERIFIED.json':sorted(R.glob('EXPOSURE_MATCHED_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1],
 'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW.json':R/'EXPOSURE_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW.json',
 'E1_CURB20_DIRECTION141_COMPLETE_ACTUAL_COLLECTION.json':sorted(R.glob('CURB141_COLLECTED_[0-9]*.json'))[-1],
 'E1_CURB20_DIRECTION141_COMPLETE_ACTUAL_REVIEW.json':sorted(R.glob('CURB141_SCHEMA_REVIEW_[0-9]*.json'))[-1],
 'E1_CURB20_DIRECTION141_COMPLETE_OBSERVED_SCOPE_DECISION.json':R/'CURB141_COMPLETE_OBSERVED_SCOPE_DECISION.json',
 'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_COMPLETE_TRAINING_TRACE_ACTUAL.json':sorted(R.glob('EXPOSURE424_COMPLETE_TRAINING_TRACE_ACTUAL_[0-9]*.json'))[-1],
 'E1_CURB20_DIRECTION141_FINAL_SENSOR_RECEIPT_SCHEMA_REVIEW.json':R/'CURB141_FINAL_SENSOR_RECEIPT_READER_SCHEMA_REVIEW.json',
 'E1_WAVE35_SAVED_EXPOSURE_CPU_ACTUAL.json':R/'WAVE366_COMPLETE_SAVED_EXPOSURE_CPU_ACTUAL.json',
 'NEXT_E1_WAVE35_EXPOSURE_REPAIR_WORK_ORDER.md':R/'NEXT_WAVE35_EXPOSURE_REPAIR_WORK_ORDER.md',
 'E1_CURB20_DIRECTION141_WAVE_NEXT_MONITOR_ACTUAL_VERIFIED.json':mon}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in files.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os,fcntl
E=Path(CENTRAL_PATH_TOKEN);R=E/'reports';B=Path(BUDGET_PATH_TOKEN);j=lambda p:json.loads(p.read_bytes())
own=j(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_OWN_FINAL_CPU_VERIFIED.json');D=Path(own['root'])
assert own['passed'] and own['closeout_ready'] and own['actual_source_count']==424 and own['actual_finite_tensor_count']==104
st=j(D/'reports/E1_STATE.json');assert st['phase']=='E1_CURB20_direction_exposure_matched_saved_review_ready' and st['child'] is None
receipt=j(D/'reports/e1_CURB20_direction_exposure_matched_observation_PASSED.json');assert receipt['checkpoint']['sha256']==own['own_checkpoint']['sha256']
for loc in (st['owner'],j(D/'reports/E1_GUARDIAN_STARTED.json'),receipt['own_PID_bound_receipt']):
 p=Path('/proc')/str(loc['pid'])
 if p.exists():
  z=(p/'stat').read_text().split(') ',1)[1].split();assert z[0]=='Z' or int(z[19])!=loc.get('start_ticks',int(z[19]))
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
before_budget=B.read_bytes();b=json.loads(before_budget);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
assert [x for x in b['completed_segments'] if x['pid']==own['own_PID']]==own['own_unique_completed_segment']
review=j(R/'E1_CURB20_DIRECTION141_COMPLETE_ACTUAL_REVIEW.json');decision=j(R/'E1_CURB20_DIRECTION141_COMPLETE_OBSERVED_SCOPE_DECISION.json')
assert review['review_complete'] and not review['pending'] and decision['accepted_observed_CURB20_mirrored_scope'] and decision['checkpoint']['sha256']==own['own_checkpoint']['sha256']
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);rev=c['terrain_subexpert_revision004'];scope=rev['curb20_direction_exposure_matched_scope'];assert scope['root']==str(D) and scope['source_count']==424
scope.update(phase=st['phase'],actual_state=st,formal_started=True,formal_final_pending=False,formal_saved_exit=True,
 own_final_CPU_verified=str(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_OWN_FINAL_CPU_VERIFIED.json'),own_checkpoint=own['own_checkpoint'],
 formal_final_actual_review=str(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW.json'),actual_source_count=424,
 actual_snapshot_file_count=own['actual_snapshot_file_count'],actual_finite_tensors=104,actual_141_collection=str(R/'E1_CURB20_DIRECTION141_COMPLETE_ACTUAL_COLLECTION.json'),
 actual_141_review=str(R/'E1_CURB20_DIRECTION141_COMPLETE_ACTUAL_REVIEW.json'),actual_141_complete=True,
 actual_scope_decision=str(R/'E1_CURB20_DIRECTION141_COMPLETE_OBSERVED_SCOPE_DECISION.json'),complete_training_exposure=str(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_COMPLETE_TRAINING_TRACE_ACTUAL.json'),
 accepted_observed_CURB20_mirrored_scope=True,frozen_for_observed_scope=True,qualified=False,no_more_CURB20_PPO=True,no_gate_deployment=True)
rev['wave35_exposure_repair_next_scope']=dict(expert='E1_WAVE',phase='old_fulltrace_CPU_diagnosis_complete_newscope_preparation',
 source_selected_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',old366_trace_CPU_actual=str(R/'E1_WAVE35_SAVED_EXPOSURE_CPU_ACTUAL.json'),
 next_work_order=str(R/'NEXT_E1_WAVE35_EXPOSURE_REPAIR_WORK_ORDER.md'),new_implementation_targetCPU_CUDA_PPO_not_yet_deployed=True,
 old131_original_incomplete_preserved=True,not_warmstarting_old2b4_or_CURB7b7003=True)
rev.update(active_next_expert='E1_WAVE',active_next_phase='WAVE35_exposure_repair_CPU_preparation',monitor_cadence_minutes=60,
 monitor_actual_verified=str(R/'E1_CURB20_DIRECTION141_WAVE_NEXT_MONITOR_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE141-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';before=p.read_bytes();text='\n\nActual424900s fullsaved naturalexit own32114 7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43 CPU104/source424/91snapshot+ownfreeze/PID2845252/46updates1104controls22.08Msteps4416callbacks/unique935.517459s originalparent closed, all9 samegeometryentrydirection restore/actualexits/twofcntl-free/active-Sactiveempty. Complete141 allfour errorfree/fullJSONbyteSHA/full180926768NPZ4c4d4c31cdd61b25ed218a93dfe71405ce8c2d59b321e61902421c55ae9918b1 reviewed. CURB20 mirrored up23to27/27 down27/27 with original1N two-wheel support: accept/freeze observed20mm scope only, no thirdCURB20 block/highergeometry/globalgraduation. Negative4pi diagnostic3to0/8/world64to60/64 originalfalse retained; E0frozen/gateuntrained. Full424 trace11.04s signed+standing and cumulativehist phase exact, rootcross544/590 onlyproxy. OldWave full144trace CPUactual1.44s maxgentle.432m diagnosed; actively nextindependentWave35 fromreviewed1293c97 pernewworkorder, newexecutor/fullstate/PPO stillnotdeployed. Reader sensor_recipe assertion/SSH10054 preserved, independentreadonlyschema repairs noGPU replay/noinitialbiasrawexactclaim. Allnewreports/errors/metadata/monitor/workorder ordinaryGit supplement; noledgerwrites, oldonce replay, otherexpert/player intervention.\n';assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE141-'+str(time.time_ns()));tmp.write_bytes(before+text.encode());os.replace(tmp,p)
assert B.read_bytes()==before_budget and all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),metadata_synced=True,root=str(D),state=st,own_checkpoint=own['own_checkpoint'],actual_fullsave_PID_unique_and_closeout_verified=True,
 all_141_cases_actual_complete=True,accepted_observed_CURB20_mirrored_scope=True,not_whole_course_or_gate_finished=True,next_expert='E1_WAVE',
 protected_master_approval_tracks_RM_canonical_bytes_exact=True,hourly_monitor_verified=True,no_GPU_PPO_budget_write=True)
q=R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_FORMAL_FINAL_CURRENT_ACTUAL.json';assert not q.exists();q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL_PATH_TOKEN',repr(io.E)).replace('BUDGET_PATH_TOKEN',repr(io.B)))
  q=save('COMPLETE141_AND_WAVE_NEXT_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_CURB20_DIRECTION_EXPOSURE_MATCHED_COMPLETE141_AND_WAVE_NEXT_METADATA_SYNCED.json',q.read_bytes())
  print(json.dumps(dict(metadata_synced=True,all141_complete=True,CURB20_scope_frozen=True,next_expert='E1_WAVE')))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:
  save('COMPLETE141_WAVE_NEXT_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),old_sync_not_replayed=True));raise

"""Append actual complete139 evidence and next single-axis work order; never touch ledger."""
from pathlib import Path
import sys,json,time,tomllib,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io

def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'ENTRY139_COMPLETE_MONITOR_REQUEST.json').read_bytes())
 assert all(t[k]==req[k] for k in ('id','kind','name','status','rrule','target_thread_id')) and t['prompt'].replace('\r\n','\n')==req['prompt'].replace('\r\n','\n')
 verified=save('ENTRY139_COMPLETE_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),id=t['id'],kind=t['kind'],name=t['name'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],same_existing_heartbeat=True,actual_interval_minutes=60,actual_prompt_SHA=io.H(t['prompt'].encode()),normalized_prompt_SHA=io.H(t['prompt'].replace('\r\n','\n').encode()),actual139_complete=True,healthy_pending_silent=True,no_new_automation_training_or_budget=True))
 names={
 'E1_CURB20_ENTRY139_COMPLETE_ACTUAL_COLLECTION.json':R/'CURB139_COLLECTED_1791709644684366800.json',
 'E1_CURB20_ENTRY139_COMPLETE_ACTUAL_REVIEW.json':R/'CURB139_FINAL_RESET_SCHEMA_REVIEW_1791709852083172200.json',
 'E1_CURB20_ENTRY139_COMPLETE_SCOPE_DECISION.json':R/'ENTRY139_COMPLETE_SCOPE_DECISION.json',
 'E1_CURB20_ENTRY139_COMPLETE_PREFIX_DIRECTION_DIAGNOSIS.json':R/'ENTRY139_COMPLETE_PREFIX_ACTUAL_DIAGNOSIS.json',
 'E1_CURB20_ENTRY139_SAVED_TRAINING_COMMAND_EXPOSURE.json':R/'ENTRY139_SAVED_TRAINING_COMMAND_EXPOSURE_ACTUAL_REVIEW.json',
 'E1_CURB20_ENTRY139_FINAL_RESET_SENSOR_READER_REVIEW.json':R/'ENTRY139_FINAL_RESET_READER_ADMITTED.json',
 'E1_CURB20_ENTRY139_ORIGINAL_SENSOR_READER_ERROR.json':R/'CURB139_SCHEMA_REVIEW_ERROR_1791709652411144600.json',
 'E1_CURB20_ENTRY139_COMPLETE_MONITOR_ACTUAL_VERIFIED.json':verified,
 'NEXT_E1_CURB20_ENTRY_COMMAND_AXIS_CPU_AND_BOUNDED_RETRAIN_WORK_ORDER.md':R/'NEXT_E1_CURB20_ENTRY_COMMAND_AXIS_CPU_AND_BOUNDED_RETRAIN_WORK_ORDER.md'}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   assert not set(names)&set(f.listdir(io.E+'/reports'))
   for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);D=Path(ROOT);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
review=j(R/'E1_CURB20_ENTRY139_COMPLETE_ACTUAL_REVIEW.json');col=j(R/'E1_CURB20_ENTRY139_COMPLETE_ACTUAL_COLLECTION.json');decision=j(R/'E1_CURB20_ENTRY139_COMPLETE_SCOPE_DECISION.json');verified=j(R/'E1_CURB20_ENTRY139_COMPLETE_MONITOR_ACTUAL_VERIFIED.json')
assert review['review_complete'] and len(col['cases'])==4 and not col['pending'] and not decision['own_CURB_scope_qualified']
assert decision['candidate139_ascending_complete']==23 and decision['descending_complete']==27 and decision['valid_incomplete_ascending_prefixes']==[6,12,15,18]
assert verified['actual_interval_minutes']==60 and verified['status']=='ACTIVE'
state=j(D/'reports/E1_STATE.json');assert state['child'] is None and state['phase']=='E1_CURB20_entry_repair_saved_review_ready'
budget_before=B.read_bytes();budget=json.loads(budget_before);assert budget['active_segment'] is None and budget['authorized_training_seconds']==1188000 and len(budget['budget_extensions'])==7
assert 36000+sum(x['additional_training_seconds'] for x in budget['budget_extensions'])==1188000
cp=review['own']['checkpoint'];assert cp['sha256']=='2fe67400d4119b94dbf33d7770b7fec44a9c73c568256e8161c3d8298ad73a04' and H(Path(cp['path']).read_bytes())==cp['sha256']
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];scope=rev['curb20_entry_seed_reviewed_scope'];assert scope['root']==str(D) and scope['source_count']==410 and c['budget_retrain_revision005']['approved']
scope.update(actual_139_collection=str(R/'E1_CURB20_ENTRY139_COMPLETE_ACTUAL_COLLECTION.json'),actual_139_complete_review=str(R/'E1_CURB20_ENTRY139_COMPLETE_ACTUAL_REVIEW.json'),actual_139_complete_cases=list(col['cases']),actual_139_pending=[],actual_139_review_complete=True,actual_139_scope_decision=str(R/'E1_CURB20_ENTRY139_COMPLETE_SCOPE_DECISION.json'),actual_139_prefix_diagnosis=str(R/'E1_CURB20_ENTRY139_COMPLETE_PREFIX_DIRECTION_DIAGNOSIS.json'),actual_saved_training_command_exposure=str(R/'E1_CURB20_ENTRY139_SAVED_TRAINING_COMMAND_EXPOSURE.json'),qualified=False,candidate_frozen_as_review_evidence_only=True,candidate_not_default_warmstart=True)
rev.update(active_next_expert='E1_CURB',active_next_phase='CURB20_entry_command_axis_CPU_component_preparation',next_work_order=str(R/'NEXT_E1_CURB20_ENTRY_COMMAND_AXIS_CPU_AND_BOUNDED_RETRAIN_WORK_ORDER.md'),monitor_cadence_minutes=60,monitor_actual_verified=str(R/'E1_CURB20_ENTRY139_COMPLETE_MONITOR_ACTUAL_VERIFIED.json'))
rev['curb20_entry_command_axis_next_scope']=dict(phase='CPU_component_preparation',learning_executor_deployed=False,new_GPU_or_PPO_started=False,source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',scope='episode-bound actual CURB command-to-reset-entry direction only',geometry_entry_reward_LR_DR_clock_family_quotas_unchanged=True,not_a_proven_causal_repair=True)
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRY139COMPLETE-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nLatest actual139 complete: all4 frozen cases complete/errorfree, twohost JSON byteSHA and full180943239B raw SHA d4c9b622b6c37fa2ca750a9e0f86c830eae1570433266e63f435ff20b40e4cc7/fullcontracts independently reviewed. Up13226/27 ->13322/27 ->13923/27; down27/27,ordinary0,closure.652400020mm,48declaredroute truncations. All four139 incomplete6/12/15/18 original+BODYvx.3/yaw0 turn and move sideways before both wheels finish the curb; three source-complete regress. Not qualifiedCURB; own4102fe frozen review evidence only, not next default warmstart or blind900s/highergeometry. Negative4pi7->5/8/world63/64 diagnostics and alloriginalfalse retained. Finalframeenv69 route-reset warmupfalse is independently raw-bound/oldreset-sourceSHA-bound; originalreadererror/source retained, no productiontol relaxation. Saved410168control trace proves positive/negative/standing on bothCURB sides, so no missingpositivecoverage or causalclaim. New approved004005 command-to-entry episode-direction CPU workorder, still no new executor/GPU/PPO. Same mod4-10 ACTIVE1hour quiethealthy/pending; previouspartial30min/hourly files retained as history. All saved fullreview/reader/source/prefix/commands/workorder/central/monitor receipts ordinaryGit supplement required; protectedmasterapprovaltracksRM andcanonicalbytes exact, no oldonce/GPU/record/tag/budgettail replay or WASD action.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRY139COMPLETE-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert all((R/x).read_bytes()==b for x,b in protected.items()) and B.read_bytes()==budget_before
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,actual139_review_complete=True,CURB_qualified=False,ascending_complete=23,descending_complete=27,pending=[],next_phase=rev['active_next_phase'],new_learning_executor_deployed=False,actual_monitor_minutes=60,remaining_seconds_snapshot=budget['authorized_training_seconds']-budget['charged_training_seconds'],canonical_SHA=H(budget_before),canonical_bytes_preserved=True,protected_master_approval_tracks_RM_exact=True,no_GPU_PPO_queue_or_budget_action=True)))
'''.replace('CENTRAL',repr(io.E)).replace('BUDGET',repr(io.B)).replace('ROOT',repr(NEW)))
  receipt=save('ENTRY139_COMPLETE_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_CURB20_ENTRY139_COMPLETE_METADATA_SYNCED.json',receipt.read_bytes())
  print(json.dumps(dict(actual139_complete=True,metadata_synced=True,CURB_qualified=False,new_training_deployed=False,actual_monitor_minutes=60)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY139_COMPLETE_SYNC_REJECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise

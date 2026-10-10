"""New actual formal closeout after own PASSED/CPU/source receipt, annotation only."""
from stage_split_state_admission_once import D,R,E,B,NEW,connect_both,cleanup,linux_json,save,put
from pathlib import Path
import json,time,traceback
def main():
 actual=json.loads(sorted(R.glob('SPLIT_STATE_ACTUAL_[0-9]*.json'))[-1].read_bytes())
 cpu=json.loads(sorted(R.glob('SPLIT_STATE_OWN_FORMAL_CPU_VERIFIED_[0-9]*.json'))[-1].read_bytes())
 assert cpu['passed'] and not cpu['pending'] and actual['reports']['E1_STATE.json']['phase']=='E1_CURB20_independent_saved_review_ready'
 assert not actual['canonical']['active_segment'] and all(not x['held'] for x in actual['OS_locks'])
 for x in actual['actual_processes']:assert x['actual'] is None or x['actual']['state']=='Z' or x['actual']['start_ticks']!=x['locator']['start_ticks']
 summary=dict(epoch=time.time(),review_complete=True,own_formal_CPU_receipt=cpu,actual_phase=actual['reports']['E1_STATE.json']['phase'],actual_parent_guardian_child_exited=True,two_OS_locks_free=True,unique_segment_settled_once=True,own_fullsave_not_behavior_graduation=True,requires_actual133_complete_review=True,new_budget_seconds=0)
 p=save('SPLIT_STATE_FORMAL_FINAL_ACTUAL_REVIEW.json',summary)
 collection=sorted(R.glob('CURB133_COLLECTED_[0-9]*.json'))
 save('SPLIT_STATE_FORMAL_CLOSEOUT_SYNC_STARTED.json',dict(epoch=time.time(),new_actual_formal_closeout_only=True,no_Git_or_GPU_or_canonical_action=True))
 n,w=connect_both()
 try:
  reports={'E1_CURB20_SPLIT_STATE_FORMAL_FINAL_ACTUAL_REVIEW.json':p.read_bytes(),
   'E1_CURB20_SPLIT_STATE_OWN_FINAL_CPU_VERIFIED.json':json.dumps(cpu,ensure_ascii=False,indent=2).encode(),
   'E1_CURB20_SPLIT_STATE_FORMAL_FINAL_CURRENT_ACTUAL.json':json.dumps(actual,ensure_ascii=False,indent=2).encode()}
  if collection:reports['E1_CURB20_133_CURRENT_COLLECTION.json']=collection[-1].read_bytes()
  with n.open_sftp() as f:
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  result=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};budget=B.read_bytes();j=lambda p:json.loads(p.read_bytes())
a=j(R/'E1_CURB20_SPLIT_STATE_FORMAL_FINAL_CURRENT_ACTUAL.json');cpu=j(R/'E1_CURB20_SPLIT_STATE_OWN_FINAL_CPU_VERIFIED.json')
assert a['root']==ROOT and cpu['passed'] and len(cpu['unique_completed_segment'])==1
for k in ('E1_CURB133_ASYNC_PUBLISHED.json','e1_CURB20_independent_observation_PASSED.json'):assert k in a['reports']
l=j(B);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);revision=v['terrain_subexpert_revision004'];assert revision['approved'] and revision['active_next_expert']=='E1_CURB';scope=revision['curb20_split_state_scope'];assert scope['root']==ROOT and not scope['own_formal_complete']
scope.update(epoch=time.time(),actual_phase_at_sync=a['reports']['E1_STATE.json']['phase'],new_fullstate_PPO_preflight_complete=True,own_formal_complete=True,own_formal_checkpoint=cpu['checkpoint'],own_final_CPU_report=str(R/'E1_CURB20_SPLIT_STATE_OWN_FINAL_CPU_VERIFIED.json'),current_actual=str(R/'E1_CURB20_SPLIT_STATE_FORMAL_FINAL_CURRENT_ACTUAL.json'),own_formal_actual_segment_seconds=cpu['actual_total_segment_seconds'],behavior133_review_pending=True,no_more_PPO_automatic=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.CURB388FINAL-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='CURB388 own formal closed actual:';assert marker.encode() not in old
msg='\n\n'+marker+' '+ROOT+'; own '+cpu['checkpoint']['sha256']+'; full CPU102/PID/source384/srcsnapshot/PASSED/unique segment checked, ownparent/guardian/child naturally exited and two OS locks free. Big4 PPO completed once under384; 386 freshzero-step process actual sameCURB fullresume proves allstate; optionalpartialsave logger failure retained;388 independentCPU split admission binds both; big/freshGPU not repeated; SDK/native/small exactreuse. Formal only300s load-learn-save-exit complete,133 fourcase published and actualcomplete errorfree twohostJSON/fullNPZ review required before any further PPO or height expansion. Old failed380 cost/raw/error and previous active snapshots retained. No E0/Wave optimizer or save overwrite; not qualifiedCURB/RM002/stairs/gate deployment.\n'
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CURB388FINAL-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),own_formal_closeout_metadata_synced=True,original_scope_sync_not_replayed=True,master_approval_tracks_RM_canonical_bytes_preserved=True,behavior133_pending_not_graduation=True,remaining_seconds=l['authorized_training_seconds']-l['charged_training_seconds'])))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  p=save('SPLIT_STATE_FORMAL_CLOSEOUT_METADATA_SYNCED.json',result)
  with n.open_sftp() as f:put(f,E+'/reports/E1_CURB20_SPLIT_STATE_FORMAL_CLOSEOUT_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(result))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SPLIT_STATE_FORMAL_CLOSEOUT_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_sync_replay_check_actual_CAS=True));raise

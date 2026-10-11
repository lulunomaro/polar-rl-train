from direction_io import *
import traceback
def main():
 root=json.loads((R/'DIRECTION_ACTIVE_ROOT.json').read_bytes())['root'];n,w=io.connect_both()
 try:
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';D=Path(ROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
cpu=j(R/'E1_CURB20_DIRECTION_TARGET_CPU_VERIFIED.json');dispatch=j(R/'E1_CURB20_DIRECTION_DISPATCH_ACTUAL_RECEIPT.json');assert cpu['passed'] and dispatch['root']==str(D) and dispatch['source_count']==421
state=j(D/'reports/E1_STATE.json');budget=j(B);assert budget['authorized_training_seconds']==1188000 and len(budget['budget_extensions'])==7
assert 36000+sum(x['additional_training_seconds'] for x in budget['budget_extensions'])==1188000
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];assert rev['curb20_entry_seed_reviewed_scope']['actual_139_review_complete'] and c['budget_retrain_revision005']['approved']
scope=dict(root=str(D),source_count=421,phase=state['phase'],learning_executor_deployed=True,formal_started=bool((D/'reports/e1_CURB20_direction_repair_observation_PASSED.json').exists() or state['phase']=='bounded_E1_CURB20_direction_repair_learning'),qualified=False,
 source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',actual_CPU=str(R/'E1_CURB20_DIRECTION_TARGET_CPU_VERIFIED.json'),actual_dispatch=str(R/'E1_CURB20_DIRECTION_DISPATCH_ACTUAL_RECEIPT.json'),actual_state=state,only_episode_command_direction_axis=True,no_new_rng=True,not_a_proven_causal_repair=True)
rev['curb20_entry_command_axis_next_scope']=scope;rev.update(active_next_expert='E1_CURB',active_next_phase=state['phase'],next_work_order=str(R/'NEXT_E1_CURB20_DIRECTION_SCOPE_AND_CANDIDATE140_REVIEW_WORK_ORDER.md'),monitor_cadence_minutes=60,monitor_actual_verified=str(R/'E1_CURB20_DIRECTION_MONITOR_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.DIRECTION-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nLatest actual independentCURB direction source421 CPU schema admitted and uniquely dispatched at '+str(D)+'. RealSDK10 direction scope actualpassed, native20k/preflights/fresh/formal actualownphase/PIDreceipt laterpriority. Current phase '+state['phase']+'; CPU is not formal. Only episode-reset command sign matches actualCURBentry, no liveposition/yawcorrection or extraRNG. Oldsource410139up23/down27of27 unqualified preserved; newwarmstart1293c97, only owncompletePASSED afterallnewscope permits300s andcandidate1404case actualreview. No repeatedclock/oldonce/extension/clear/recharge/WASDaction. Sameheartbeat ACTIVEhourlyquiet; allsavederrors/readerproofs/newdeployment/metadata/monitorandlaterownresultsGit.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.DIRECTION-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert all((R/x).read_bytes()==b for x,b in protected.items())
current=dict(epoch=time.time(),metadata_synced=True,root=str(D),source_count=421,state=state,formal_started=scope['formal_started'],qualified=False,actual_monitor_minutes=60,canonical_read_only_no_ledger_write=True,protected_master_approval_tracks_RM_exact=True)
(R/'E1_CURB20_DIRECTION_CURRENT_ACTUAL.json').write_text(json.dumps(current,indent=2));print(json.dumps(current))
'''.replace('CENTRAL',repr(io.E)).replace('ROOT',repr(root)).replace('BUDGET',repr(io.B)))
  q=save('DIRECTION_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_CURB20_DIRECTION_METADATA_SYNCED.json',q.read_bytes())
  print(json.dumps(dict(metadata_synced=True,state=v['state']['phase'],formal_started=v['formal_started'],monitor_minutes=60)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_UPLOADED_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise

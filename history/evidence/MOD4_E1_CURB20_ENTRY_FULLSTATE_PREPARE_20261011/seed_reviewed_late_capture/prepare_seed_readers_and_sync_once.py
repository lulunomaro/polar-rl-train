from pathlib import Path
import sys,json,time,ast
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
for original,new in (('read_entry_fullstate_actual.py','read_entry_seed_actual.py'),('read_entry_own_formal_cpu_actual.py','read_entry_seed_own_formal_cpu_actual.py')):
 p=D/new;assert not p.exists();t=(D/original).read_text(encoding='utf8').replace('from stage_entry_fullstate_and_cpu_once import NEW,save','from stage_dispatch_seed_reviewed_once import NEW,save').replace('ENTRY_FULLSTATE_ACTUAL_','ENTRY_SEED_ACTUAL_').replace('ENTRY_OWN_FORMAL_CPU_ACTUAL_','ENTRY_SEED_OWN_FORMAL_CPU_ACTUAL_').replace('ENTRY_OWN_CPU_READER_REJECTED_','ENTRY_SEED_OWN_CPU_READER_REJECTED_');ast.parse(t);p.write_text(t,encoding='utf8')
n,w=io.connect_both()
try:
 names={'E1_CURB20_ENTRY_SEED_REVIEWED_CPU_DISPATCH_ACTUAL.json':R/'ENTRY_SEED_DISPATCH_ACTUAL_RECEIPT.json','E1_CURB20_ENTRY409_FRESH_FAILED_ACTUAL_REVIEW.json':R/'ENTRY_FRESH_ACTUAL_FAILURE_REVIEW_1791704758705696500.json','E1_CURB20_ENTRY_SEED_REVIEWED_SOURCE_FREEZE.json':R/'ENTRY_SEED_SOURCE_FREEZE.json'}
 with n.open_sftp() as f:
  assert not set(names)&set(f.listdir(io.E+'/reports'))
  for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
 v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';N=Path(ROOT);j=lambda p:json.loads(p.read_bytes());a=j(R/'E1_CURB20_ENTRY_SEED_REVIEWED_CPU_DISPATCH_ACTUAL.json');assert a['CPU']['passed']
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_CURB'
scope=dict(root=ROOT,source_count=410,old409_allbytes_preserved=True,new_fresh_seed20260928_explicit=True,valid409_SDK_small_big_native_exact_reused=True,own_CPU_and_dispatch=str(R/'E1_CURB20_ENTRY_SEED_REVIEWED_CPU_DISPATCH_ACTUAL.json'),old_actual_failed_fresh=str(R/'E1_CURB20_ENTRY409_FRESH_FAILED_ACTUAL_REVIEW.json'),formal_target_seconds=300,actual_current_phase=j(N/'reports/E1_STATE.json')['phase'] if (N/'reports/E1_STATE.json').exists() else 'own_dispatch_pending_first_state',formal_final_pending=not (N/'reports/e1_CURB20_entry_repair_observation_PASSED.json').exists(),source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e')
rev.update(curb20_entry_seed_reviewed_scope=scope,active_next_phase='CURB20_entry_seed_reviewed_fresh_restore_then_formal',monitor_cadence_minutes=30)
rev['curb20_entry_fullstate_reviewed_scope']['original_fresh_failed_actual']=scope['old_actual_failed_fresh'];rev['curb20_entry_fullstate_reviewed_scope']['closed_after_failed_fresh_before_formal']=True
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.SEED-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nSource409 SDK10 and small/big fullstate preflights actualPASSED retained; fresh0PPO rejected missing seed20260928 before startup restore, default42 retained. Old409 actual parent/guardian/child exited, twoOSlocks free and idle005 boundary acquired. Newsource410 copies all409bytes plusone unique wrapper, CPU102 verified and actuallydispatched with only seed-correct fresh scope then formal300s. Valid SDK/native/preflights are exact reused, no duplicatePPO. Local read_entry_seed_actual.py/read_entry_seed_own_formal_cpu_actual.py address410 only. Actualownfuture PASSED/final/139 override snapshot; no oldonce/main/fresh replay. Monitor30minACTIVE/silenthealthy, all saved errors/reports Git including prerecord ID length rejection, no new budget or WASD action.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.SEED-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert all((R/x).read_bytes()==b for x,b in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,scope=scope,protected_master_approval_tracks_RM_exact=True,canonical_writer_actions=0,actual_monitor_minutes=30)))
'''.replace('CENTRAL',repr(io.E)).replace('ROOT',repr(NEW)))
 p=save('ENTRY_SEED_SCOPE_METADATA_SYNCED.json',v)
 with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_CURB20_ENTRY_SEED_REVIEWED_SCOPE_METADATA_SYNCED.json',p.read_bytes())
 print(json.dumps(dict(metadata_synced=True,root=NEW,actual_phase=v['scope']['actual_current_phase'],formal_pending=v['scope']['formal_final_pending'])))
finally:io.cleanup(n,w)

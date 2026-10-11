from direction_io import *
import tomllib,traceback
def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'DIRECTION_STARTUP_MONITOR_REQUEST.json').read_bytes())
 assert t['status']==req['status']=='ACTIVE' and t['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and t['target_thread_id']==req['targetThreadId']
 assert t['prompt'].replace('\r\n','\n')+'\n'==req['prompt'].replace('\r\n','\n')
 q=save('DIRECTION_STARTUP_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),status=t['status'],rrule=t['rrule'],actual_interval_minutes=60,actual_prompt_SHA=H(t['prompt'].encode()),same_heartbeat_target=True,healthy_pending_silent=True))
 root=json.loads((R/'DIRECTION_STARTUP_ACTIVE_ROOT.json').read_bytes())['root'];n,w=io.connect_both()
 try:
  files={'E1_CURB20_DIRECTION_STARTUP_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json':R/'DIRECTION_STARTUP_DISPATCH_ACTUAL_RECEIPT.json','E1_CURB20_DIRECTION_STARTUP_REVIEWED_SOURCE_FREEZE.json':R/'DIRECTION_STARTUP_SOURCE_FREEZE.json','E1_CURB20_DIRECTION_STARTUP_MONITOR_ACTUAL_VERIFIED.json':q}
  with n.open_sftp() as f:
   for name,p in files.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';D=Path(ROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
state=j(D/'reports/E1_STATE.json');assert j(D/'reports/DIRECTION_REUSED_PHYSICAL_SCOPE_VERIFIED.json')['passed']
assert j(B)['authorized_training_seconds']==1188000 and len(j(B)['budget_extensions'])==7
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];prior=rev['curb20_entry_command_axis_next_scope'];assert prior['source_count']==421
rev['curb20_entry_direction_initial421_scope_history']=prior
formal_started=state['phase']=='bounded_E1_CURB20_direction_repair_learning' or (D/'reports/e1_CURB20_direction_repair_observation_PASSED.json').exists()
scope=dict(root=str(D),source_count=423,actual_state=state,phase=state['phase'],learning_executor_deployed=True,formal_started=formal_started,qualified=False,
 actual_dispatch=str(R/'E1_CURB20_DIRECTION_STARTUP_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json'),source_freeze=str(R/'E1_CURB20_DIRECTION_STARTUP_REVIEWED_SOURCE_FREEZE.json'),source421_SDK_native_exact_reused=True,old421_failedsmall_before_control_PPO_retained=True,
 only_small_initialization_binding_before_manifest_repaired=True,direction_math_runtime_checkpoint_unchanged=True,source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e')
rev['curb20_entry_command_axis_next_scope']=scope;rev.update(active_next_expert='E1_CURB',active_next_phase=state['phase'],monitor_cadence_minutes=60,monitor_actual_verified=str(R/'E1_CURB20_DIRECTION_STARTUP_MONITOR_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.DIRECTIONSTARTUP-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nActualsource423 startup-reviewed isolatedroot '+str(D)+': source421 failedsmall prelearn episode binding assertion retained and originalparent uniquely settled afteractualexits/locksfree; nohotpatch. Onlynewsmallworker binds initialcommandstate beforemanifest, noRNG/reset/math change. Actual421SDK10/native20k originalSHA reuse; new423smallfullPPO passed, ownbig/fresh/formal actualstate/PID/PASSED laterpriority. Samehourlyheartbeatquiet, canonical1188000sevenextensions noledgerwrites, source1293c97 and candidate140fourcase ownscope review required. Allsavedtrialerrors/source/proofs/metadata/monitor/Gitcaptured; E0/SLOPE/Wave/WASDuntouched.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.DIRECTIONSTARTUP-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert all((R/x).read_bytes()==b for x,b in protected.items())
v=dict(epoch=time.time(),metadata_synced=True,root=str(D),source_count=423,state=state,formal_started=formal_started,actual_monitor_minutes=60,canonical_read_only_no_ledger_write=True,protected_master_approval_tracks_RM_exact=True)
(R/'E1_CURB20_DIRECTION_STARTUP_REVIEWED_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL',repr(io.E)).replace('ROOT',repr(root)).replace('BUDGET',repr(io.B)))
  q=save('DIRECTION_STARTUP_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_CURB20_DIRECTION_STARTUP_REVIEWED_METADATA_SYNCED.json',q.read_bytes())
  print(json.dumps(dict(metadata_synced=True,root=root,phase=v['state']['phase'],formal_started=v['formal_started'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_STARTUP_METADATA_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise

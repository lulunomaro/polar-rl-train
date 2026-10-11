from direction_io import *
import tomllib,traceback
from prepare_direction140_decision_and_exposure_continuation_once import ROOT

def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'EXPOSURE_MATCHED_MONITOR_REQUEST.json').read_bytes())
 assert t['status']==req['status']=='ACTIVE' and t['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and t['target_thread_id']==req['targetThreadId']
 assert t['prompt'].replace('\r\n','\n')+'\n'==req['prompt'].replace('\r\n','\n')
 mon=save('EXPOSURE_MATCHED_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),status=t['status'],rrule=t['rrule'],same_target=True,prompt_SHA=H(t['prompt'].encode()),hourly_ACTIVE_healthy_pending_silent=True))
 startup=sorted(R.glob('EXPOSURE_MATCHED_STARTUP_ACTUAL_[0-9]*.json'))[-1];assert json.loads(startup.read_bytes())['startup_complete']
 n,w=io.connect_both()
 try:
  files={'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_DISPATCH_ACTUAL_RECEIPT.json':R/'EXPOSURE_MATCHED_DISPATCH_ACTUAL_RECEIPT.json',
   'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_STARTUP_ACTUAL_VERIFIED.json':startup,
   'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_CURRENT_ACTUAL.json':sorted(R.glob('EXPOSURE_MATCHED_ACTUAL_[0-9]*.json'))[-1],
   'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_MONITOR_ACTUAL_VERIFIED.json':mon}
  with n.open_sftp() as f:
   for name,p in files.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
E=Path(CENTRAL_PATH_TOKEN);R=E/'reports';D=Path(NEW_ROOT_TOKEN);B=Path(BUDGET_PATH_TOKEN);j=lambda p:json.loads(p.read_bytes());st=j(D/'reports/E1_STATE.json');loc=st['child'];assert loc and not (D/'reports/E1_ATTENTION.json').exists()
for a in (st['owner'],loc):
 p=Path('/proc')/str(a['pid']);z=(p/'stat').read_text().split(') ',1)[1].split();assert z[0]!='Z' and int(z[19])==a['start_ticks'] and str(D) in (p/'cmdline').read_bytes().decode()
bb=B.read_bytes();b=json.loads(bb);assert b['active_segment']['pid']==loc['pid'] and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
proof=j(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_STARTUP_ACTUAL_VERIFIED.json');assert proof['startup_complete'] and len(proof['markers'])==9
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);rev=c['terrain_subexpert_revision004'];scope=rev['curb20_direction_exposure_matched_scope'];assert scope['root']==str(D) and scope['source_count']==424
scope.update(phase=st['phase'],actual_state=st,dispatch_actual=str(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_DISPATCH_ACTUAL_RECEIPT.json'),startup_actual=str(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_STARTUP_ACTUAL_VERIFIED.json'),current_actual=str(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_CURRENT_ACTUAL.json'),formal_started=True,formal_final_pending=True,actual_same_geometry_entry_direction_full_CPU_CUDA_restore=True,no_PPO_preflight_replay=True,qualified=False)
rev.update(active_next_expert='E1_CURB',active_next_phase='CURB20_direction_exposure_matched_bounded_learning',monitor_cadence_minutes=60,monitor_actual_verified=str(R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_MONITOR_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.EXPOSUREACTIVE-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';before=p.read_bytes();text='\n\nActualsource424 new900s CURB20 same-entry-direction exposure continuation started. Parent2845157/start87454822, child2845252/start87454948 only locators; actualproc argv/cwd/start and ownstage/save/PIDreceipt priority. All9 actualstartup receipts sourcee6df fullsamegeometry-entry-direction restoredexact/newscopefalse, oldactorcriticstdoptimizer/D0D7/globalnamed/dictprivateCPUCUDA restored and actualdiskroundtrip/episode+1 passed; notPhysXexactresume. NoSDK/native/small/big/fresh/clock replay. Originalown423 e6df full140 up23/down27 validincomplete preserved; selected onlyonecontinuation notqualifiednewexpert. Own900loadlearnsaveexit/save25/15s guardian activeoriginalparent uniqueledger; futureownfinal+141 actualfullreview and complete exposure audit mandatory beforemorePPO. Hourlysameheartbeat ACTIVE quietpending, E0/Wave/SLOPE/player untouched, protectedhistoricalplan unchanged. Alllater savedreports/Git receipts supplement.\n';assert p.read_bytes()==before;tmp=p.with_name(p.name+'.EXPOSUREACTIVE-'+str(time.time_ns()));tmp.write_bytes(before+text.encode());os.replace(tmp,p)
assert all((R/name).read_bytes()==raw for name,raw in protected.items())
after=B.read_bytes();ba=json.loads(after);assert ba['active_segment']['pid']==loc['pid'] and ba['authorized_training_seconds']==b['authorized_training_seconds'] and ba['budget_extensions']==b['budget_extensions'] and ba['charged_training_seconds']>=b['charged_training_seconds']
v=dict(epoch=time.time(),metadata_synced=True,root=str(D),source_count=424,actual_owner=st['owner'],actual_child=loc,actual_startup_full9_same_scope_verified=True,formal_active_final_pending=True,hourly_monitor_verified=True,protected_master_approval_tracks_RM_bytes_exact=True,canonical_no_write_by_sync=True,canonical_before_SHA=hashlib.sha256(bb).hexdigest(),canonical_after_SHA=hashlib.sha256(after).hexdigest(),canonical_parent_accounting_may_advance=True,no_GPU_launch_or_budget_extension_by_sync=True)
q=R/'E1_CURB20_DIRECTION_EXPOSURE_MATCHED_DISPATCH_STARTUP_METADATA_SYNCED.json';assert not q.exists();q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL_PATH_TOKEN',repr(io.E)).replace('NEW_ROOT_TOKEN',repr(ROOT)).replace('BUDGET_PATH_TOKEN',repr(io.B)))
  save('EXPOSURE_MATCHED_DISPATCH_STARTUP_METADATA_SYNCED.json',v);print(json.dumps(dict(metadata_synced=True,source_count=424,startup9_verified=True,formal_active=True)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('EXPOSURE_MATCHED_ACTIVE_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise

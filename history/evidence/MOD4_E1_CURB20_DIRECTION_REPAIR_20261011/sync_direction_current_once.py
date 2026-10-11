from direction_io import *
import tomllib,traceback
def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'DIRECTION_MONITOR_REQUEST.json').read_bytes())
 assert all(t[k]==req[k] for k in ('id','kind','name','status','rrule')) and t['target_thread_id']==req['targetThreadId']
 assert t['prompt'].replace('\r\n','\n')+'\n'==req['prompt'].replace('\r\n','\n')
 verified=save('DIRECTION_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),id=t['id'],status=t['status'],rrule=t['rrule'],same_existing_heartbeat=True,actual_interval_minutes=60,target_thread_id=t['target_thread_id'],actual_prompt_SHA=H(t['prompt'].encode()),healthy_pending_silent=True,no_budget_action=True))
 root=json.loads((R/'DIRECTION_ACTIVE_ROOT.json').read_bytes())['root']
 p=R/'NEXT_E1_CURB20_DIRECTION_SCOPE_AND_CANDIDATE140_REVIEW_WORK_ORDER.md';assert not p.exists()
 p.write_text('''# Independent CURB20 episode-entry direction scope and actual candidate140 review

Human approved004005 unqualified-expert bounded retraining. Unique new source421/controller dispatched; original410 source bytes unchanged. New command axis binds the sign of the original gentle absolute velocity to the actual legal CURB reset entry once per physical episode, preserving original random draws/standing and all non-CURB/clearplane behavior. No live position/yaw correction, teacher, reward/LR/hardware/geometry/quota change. Warmstart only full129 source3643c97; failed4102fe remains review evidence.

Read own actual process argv/cwd/start, E1_STATE, own PID receipts, latest_complete, rolling freeze, manifest/snapshots and PASSED. New real SDK10x300 and native20k24warm120timed for changed command scope; old clock/DR/geometry exact reuse, no45min clock. New complete128x2 and20kx4 discard preflights, fresh20k0control0PPO strictsameCURBentrydirection CPUCUDA/wholeoldstreams/episode+1 restore, then unique300s including load-learn-save-exit/save25/local15sguardian. No old main/once or any passed contracts replay. Scope may naturally be pending while its child runs; no duplicate20k or hotpatch. Sole005 canonical330h/seven extensions, originalparent charge eachPPO segment once; noextension/recharge/clear.

After ownformalfullsave/PASSED/PID/uniquecharge/actualallparentguardianchildexit, candidate140 fourcase collection only actualcomplete/errorfree. Twohostprobe/result byteexact/fullNPZ SHA; exact132 same20mmvertical150mmstripplatform/9m40+40mirrors/.4mapproach/twowheelswholecurb→200mmafter/80env1500controls15s20260928white3 root30q/parameter/recipes/assignment pairing. Full6000callbacks, ground-contactintegralCOMlinkhardware original tolerances; 1Nsupport separate fromposition, stand26 no crossing requirement. All validfailed prefixes and ordinary/trunc coverage preserved, no resetteleport, shorterroute/window or relabelold139/133. Old115/129 exactskillcontracts plus allsignedcircles/alongcross/dedrift/±4pi/straight originalstrictfalse diagnostics. No qualifiedCURB ormorePPO/highergeometry before complete candidate ownscope decision. Reasonable complete result permits next independently diagnosed axis under005; do not infinitehold/onlyqueue/blindlongtraining. E0/SLOPE/Wave/CURB isolation preserved; gateuntrained/WASDplayeruntouched.

Allsaved successfulfailedreader/schema/source/proof/dispatch/native/PPO/fresh/formal/eval/metadata/monitor/Git reports recorded. Newstage uniqueannotatedtrial only once andactualremote main/tag/peeled; laterordinarysupplement, largeoriginalpath-size-SHA only, credentials excluded. Continueoriginalobjects afterpushfailure.
''',encoding='utf8')
 names={'E1_CURB20_DIRECTION_TARGET_CPU_VERIFIED.json':R/'DIRECTION_ACTUAL_SCHEMA_TARGET_CPU_PASSED.json','E1_CURB20_DIRECTION_DISPATCH_ACTUAL_RECEIPT.json':R/'DIRECTION_DISPATCH_ACTUAL_RECEIPT.json','E1_CURB20_DIRECTION_MONITOR_ACTUAL_VERIFIED.json':verified,'NEXT_E1_CURB20_DIRECTION_SCOPE_AND_CANDIDATE140_REVIEW_WORK_ORDER.md':p}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   assert not set(names)&set(f.listdir(io.E+'/reports'))
   for name,q in names.items():io.put(f,io.E+'/reports/'+name,q.read_bytes())
  v=io.linux_json(n,'''from pathlib import Path
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
 except BaseException:save('DIRECTION_METADATA_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise

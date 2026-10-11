from direction_io import *
import tomllib,traceback

def main():
    t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    req=json.loads((R/'DIRECTION_FINAL_MONITOR_REQUEST.json').read_bytes())
    assert t['status']==req['status']=='ACTIVE' and t['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and t['target_thread_id']==req['targetThreadId']
    assert t['prompt'].replace('\r\n','\n')+'\n'==req['prompt'].replace('\r\n','\n')
    q=save('DIRECTION_FINAL_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),status=t['status'],rrule=t['rrule'],actual_interval_minutes=60,prompt_SHA=H(t['prompt'].encode()),same_heartbeat_target=True,healthy_pending_silent=True))
    own=sorted(R.glob('DIRECTION_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]
    data=json.loads(own.read_bytes());assert data['passed'] and data['closeout_ready']
    n,w=io.connect_both()
    try:
        files={
          'E1_CURB20_DIRECTION_STARTUP_REVIEWED_OWN_FORMAL_CPU_VERIFIED.json':own,
          'E1_CURB20_DIRECTION_STARTUP_REVIEWED_FORMAL_FINAL_ACTUAL_REVIEW.json':R/'DIRECTION_FORMAL_FINAL_ACTUAL_REVIEW.json',
          'E1_CURB20_DIRECTION140_ACTUAL_COLLECTION.json':sorted(R.glob('CURB140_COLLECTED_[0-9]*.json'))[-1],
          'E1_CURB20_DIRECTION140_ACTUAL_REVIEW.json':sorted(R.glob('CURB140_SCHEMA_REVIEW_[0-9]*.json'))[-1],
          'E1_CURB20_DIRECTION_FINAL_MONITOR_ACTUAL_VERIFIED.json':q,
          'NEXT_E1_CURB20_DIRECTION140_ACTUAL_REVIEW_WORK_ORDER.md':None}
        note='''# Next CURB20 direction candidate140 actual full review

Source423 own formal model32069 e6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16 is fullysaved/CPU104/source423/91actualsrcsnapshot/PID2805952/PASSED/unique originalparent segment and actual full closeout verified. First300s window naturally ended, not whole coursefinished. Fourcase actualpublished and healthypending; no extraPPO or highercurb before complete actualbehavior decision.

Run read_direction_startup_actual.py and read_direction_own_formal_cpu_actual.py read-only as needed. collect_direction140_actual.py onlyactualcomplete/errorfree twohostJSONbyteexact/fullNPZ SHA; review_direction140_actual.py exact132geometry/initial root30q/parameters/recipes/assignments/fullraw/6000callbacks/groundcontactintegralCOMlinkhardware originaltolerances plus115/129signed skill diagnostics. Preserve allincompleteprefixes/ordinary/truncationreasoncoverage/fullsignedcircle alongcross/dedrift/originalfalse. SourceCPU102 cannot be hardcoded for own104 direction-state checkpoints; actual ownCPU identity binds counts. No validcomplete replay or resetteleport/shortprefix claimingroute.

Aftercomplete reasonable matchedscope decision follow004/005 authorized bounded independent CURB singleaxis continuation or diagnosis, then WAVE repair. No indefinitehold/queue-only/blindoldmixedPPO. Warmstart selection requires fullbehaviorreview; oldunqualified2fe/df0c/2b4 notautomaticdefaults, 1293c97 is existingreviewedsource. E0/SLOPE5-8-10accepted ranges frozen, gateuntrained/STAIRgeometry pending. No hotpatch/kill/dual20k/oldonce/main/clock/nativeSDK/preflight/fresh/record/tag/budgettail replay. Anynewauthority requires oldownsave/PASSED/actualexits/twofcntl-free locks/uniqueledgerclosed, budget005330h7extensions noadd/copy/clear. WASDuntouched. Every saved result/source/false/error/prefix/sync/monitor/workorder Git; largemodel/rawNPZ/USD/ZIP realpathbytesSHAonly, credentials excluded. Sameheartbeat hourlyACTIVE quietpending, notdelete atsinglelessonreviewready.
'''
        p=R/'NEXT_DIRECTION140_ACTUAL_REVIEW_WORK_ORDER.md';assert not p.exists();p.write_text(note,encoding='utf8');files['NEXT_E1_CURB20_DIRECTION140_ACTUAL_REVIEW_WORK_ORDER.md']=p
        with n.open_sftp() as f:
            for name,p in files.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
        v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os,fcntl
R=Path(CENTRAL)/'reports';B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
own=j(R/'E1_CURB20_DIRECTION_STARTUP_REVIEWED_OWN_FORMAL_CPU_VERIFIED.json');D=Path(own['root'])
assert own['closeout_ready'] and own['passed'] and own['actual_source_count']==423
state=j(D/'reports/E1_STATE.json');assert state['phase']=='E1_CURB20_direction_repair_saved_review_ready' and state['child'] is None
receipt=j(D/'reports/e1_CURB20_direction_repair_observation_PASSED.json');assert receipt['checkpoint']['sha256']==own['own_checkpoint']['sha256']
for loc in (state['owner'],j(D/'reports/E1_GUARDIAN_STARTED.json'),receipt['own_PID_bound_receipt']):
 p=Path('/proc')/str(loc['pid'])
 if p.exists():
  a=(p/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=loc.get('start_ticks',int(a[19]))
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
budget_before=B.read_bytes();b=json.loads(budget_before)
assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
assert [x for x in b['completed_segments'] if x['pid']==own['own_PID']]==own['own_unique_completed_segment']
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);rev=c['terrain_subexpert_revision004'];scope=rev['curb20_entry_command_axis_next_scope'];assert scope['root']==str(D) and scope['source_count']==423
scope.update(phase=state['phase'],actual_state=state,formal_started=True,formal_saved_exit=True,formal_final_actual_review=str(R/'E1_CURB20_DIRECTION_STARTUP_REVIEWED_FORMAL_FINAL_ACTUAL_REVIEW.json'),own_final_CPU_verified=str(R/'E1_CURB20_DIRECTION_STARTUP_REVIEWED_OWN_FORMAL_CPU_VERIFIED.json'),own_checkpoint=own['own_checkpoint'],actual_source_count=423,actual_snapshot_file_count=own['actual_snapshot_file_count'],actual_finite_tensors=own['actual_finite_tensor_count'],actual_140_collection=str(R/'E1_CURB20_DIRECTION140_ACTUAL_COLLECTION.json'),actual_140_review=str(R/'E1_CURB20_DIRECTION140_ACTUAL_REVIEW.json'),qualified=False,next_work_order=str(R/'NEXT_E1_CURB20_DIRECTION140_ACTUAL_REVIEW_WORK_ORDER.md'),old421_failedsmall_retained=True,actual421_failedsmall_seconds=21.062857627868652)
rev.update(active_next_expert='E1_CURB',active_next_phase='CURB20_direction_candidate140_actual_review',monitor_cadence_minutes=60,monitor_actual_verified=str(R/'E1_CURB20_DIRECTION_FINAL_MONITOR_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.DIRECTIONFINAL-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';before=p.read_bytes();text='\n\nActualsource423 CURB20 direction formal naturally fullsaved exited: own32069 e6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16, CPU104/source423/91srcsnapshot+ownfreeze/PID2805952/PASSED/unique330.21030592918396s originalparent closed. 7updates168control3.36Msteps672callbacks ordinary/integrity/unknown0/nonfinitefalse/STOPnone, closure.947713444mm. Timeout1693 route287 overlap1 unique1979/two coverageexact. Same-scope fresh0PPO fullstate/CUDA restore passed; initialformal explicit G3toCURB+entry+direction/newphysicalepisode disclosed. Actualparentguardianchildexit/twofcntl-free/active-Sactiveempty legalreviewready, not finishedcourse/fault. Candidate140 fourcases actuallypublished healthypending; collect/review fullroute+oldskills beforemorePPO/highergeometry/qualification, hourlymonitorquiet. old421 manifestbindingfailed0PPO unique21.062857627868652 retained; approximate21.028 oldprompt error preserved. Finalreports/reader/errors/monitor/Gitreceipt ordinarysupplement; alloriginaltrialobjects/weights/largeindices kept. Noledgerwrites/budgetextension/oldmain replay orWASD interference.\n';assert p.read_bytes()==before;tmp=p.with_name(p.name+'.DIRECTIONFINAL-'+str(time.time_ns()));tmp.write_bytes(before+text.encode());os.replace(tmp,p)
assert B.read_bytes()==budget_before and all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),metadata_synced=True,root=str(D),state=state,own_checkpoint=own['own_checkpoint'],candidate140_complete_pending=True,formal_fullsave_PID_unique_and_actual_closeout_verified=True,protected_master_approval_tracks_RM_canonical_bytes_exact=True,actual_hourly_monitor_verified=True,no_GPU_PPO_budget_write=True)
p=R/'E1_CURB20_DIRECTION_STARTUP_REVIEWED_FORMAL_FINAL_CURRENT_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL',repr(io.E)).replace('BUDGET',repr(io.B)))
        q=save('DIRECTION_FINAL_CLOSEOUT_METADATA_SYNCED.json',v)
        with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_CURB20_DIRECTION_STARTUP_REVIEWED_FINAL_CLOSEOUT_METADATA_SYNCED.json',q.read_bytes())
        print(json.dumps(dict(metadata_synced=True,phase=v['state']['phase'],formal_saved=True,candidate_pending=True,hourly_verified=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('DIRECTION_FINAL_CLOSEOUT_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise

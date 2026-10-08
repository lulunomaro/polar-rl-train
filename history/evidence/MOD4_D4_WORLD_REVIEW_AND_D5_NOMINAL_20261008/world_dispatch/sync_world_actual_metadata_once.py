"""Synchronize reviewed stage metadata only; never mutate runtime or budget."""
from pathlib import Path
import json,sys,time,hashlib

D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'WORLD_CENTRAL_METADATA_SYNCED.json').exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert hashlib.sha256((D.parent/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md').read_bytes()).hexdigest()==MASTER
review=read(R/'D4_BLOCK1_WORLD_DISPATCH_REVIEW.json')
git=read(R/'D4_WORLD_REPAIR_GIT_RECORDED.json')
assert git['remote_main_tag_peeled_verified'] and not git['push_pending']
actual=read(D.parent/'MOD4_D4_FULL_CONTRACT_20261008/reports/D4_BLOCKS_ACTUAL_VERIFIED.json')
scope=read(R/'D4_TRUE_WORLD_SCOPE_REVIEW.json')
S=D.parent/'MOD4_D5_SPRING_LAW_PREPARE_20261008'
spring=read(S/'reports/D5_NOMINAL_MODEL_CURVE_REVIEW.json')
spring_compact={k:v for k,v in spring.items() if k!='joints'}
spring_compact['joints']=[{k:v for k,v in j.items() if k!='curve'} for j in spring['joints']]
spring_compact['full_offline_curve_JSON_sha256']=hashlib.sha256((S/'reports/D5_NOMINAL_MODEL_CURVE_REVIEW.json').read_bytes()).hexdigest()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
repair='/home/egde/rl_candidates/MOD4_D4_WORLD_DISPATCH_REVIEW_20261008/reports'
try:
    with c.open_sftp() as f:
        def get(name):return json.loads(f.open(central+'/'+name).read())
        def put(name,obj,where=central):
            raw=obj.encode('utf8') if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2).encode('utf8')
            path=where+'/'+name;tmp=path+'.world_review_tmp'
            with f.open(tmp,'wb') as out:out.write(raw)
            f.posix_rename(tmp,path);assert f.open(path).read()==raw
        approval=get('PLAN_APPROVAL.json');tracks=get('EXECUTION_TRACKS.json');current=get('MOE_PLAN_EXECUTION_CURRENT.json');d5=get('NEXT_D5_FORCE_STROKE_WORK_ORDER.json')
        assert approval['approved'] and approval['approved_plan_sha256']==MASTER and 'S2' in approval['allowed_stages']
        old_handoff=f.open(central+'/LATEST_HANDOFF.md').read().decode('utf8')
        for name,obj in [('PLAN_APPROVAL.json',approval),('EXECUTION_TRACKS.json',tracks),('MOE_PLAN_EXECUTION_CURRENT.json',current),('NEXT_D5_FORCE_STROKE_WORK_ORDER.json',d5),('LATEST_HANDOFF.md',old_handoff)]:
            backup=name.rsplit('.',1)[0]+'_BEFORE_D4_WORLD_REPAIR_20261008.'+name.rsplit('.',1)[1]
            try:f.stat(central+'/'+backup)
            except FileNotFoundError:put(backup,obj)
        for name in ('D4_BLOCK1_WORLD_DISPATCH_REVIEW.json','D4_BLOCK1_WORLD_DISPATCH_REPORT.md','D4_WORLD_REPAIR_GIT_RECORDED.json',
                     'D4_TRUE_WORLD_SCOPE_REVIEW.json','WORLD_DISPATCH_PACKAGE.json','WORLD_PUBLICATION_DEPLOYED.json','COMPLETED_D4_SCOPE_FILES.json'):
            value=(R/name).read_text(encoding='utf8');put(name,value);put(name,value,repair)
        put('D5_NOMINAL_MODEL_CURVE_REVIEW.json',spring_compact)
        put('D5_NOMINAL_MODEL_CURVE_REPORT.md',(S/'reports/D5_NOMINAL_MODEL_CURVE_REPORT.md').read_text(encoding='utf8'))
        approval.setdefault('execution_events',{})['MOD4-D4-WORLD-FROZEN-DISPATCH-REPAIR-001']=dict(epoch=time.time(),
            status='ACTUAL_D4_WORLD_DISPATCH_REPAIRED_AND_LIMITED_SCOPE_REVIEWED',
            existing_S0E_S2_authorization_only=True,new_human_approval_inferred=False,master_plan_changed=False,
            production243_changed=False,old_world_is_D3_only=True,old_verdicts_preserved=True,
            actual_package_SHA=review['immutable_package']['sha256'],CPU_only_publisher=review['CPU_only_publisher'],
            baseline_scope_accepted=True,candidate_all_three_complete=scope['decision']['candidate_all_three_complete'],Git=git)
        cur=actual['current']
        current.update(epoch=actual['epoch'],actual_phase=actual['phase']['phase'],parent=actual['actual_owner'],
            guardian=actual['actual_guardian'],trainer=actual['actual_child'],source=actual['phase']['source'],
            run=cur['run'],active_log=actual['phase']['active_log'],deadline_epoch=actual['phase']['deadline_epoch'],
            own_current_save=cur['checkpoint'],live_health=cur['live_health'],live_health_is_not_final=True,
            current_block=2,block1_complete_reviewed=True,block1_actual_updates=1059,block1_actual_steps=508320000,
            block1_source=review['block1']['checkpoint'],block1_health=review['block1']['health'],
            actual_D4_to_D4_resume_startup=cur['startup'],formal_behavior_pending=scope['decision']['candidate_behavior_pending'],
            behavior_review_scope='Same3060/seed20261002/white_v3/D1-D4/A0 only',
            D4_candidate_behavior=scope['candidate28633'],new_budget_seconds=0,all_courses_finished=False,
            evaluator_world_dispatch_repair_receipt=git)
        tracks['epoch']=actual['epoch'];tracks['learning']=current
        tracks['evaluation'].update(epoch=scope['epoch'],
            original_D4_flat_spin_package_SHA='74200ad6e080c0483f8af95307ae385111a99f54e528ec359a29fcc834d93e18',
            true_D4_world_package_SHA='347ca4183e4f4cfa4ab98492637718996b62b9d4b1cb9f7f4119514484356ce5',
            old_world_job_not_D4_evidence=True,new_D4_baseline_scope_accepted=True,
            new_D4_closedloop_scope_pending=scope['decision']['candidate_behavior_pending'],
            candidate_scope=scope['candidate28633'],world_publication_CPU_helper=review['CPU_only_publisher'],
            production243_and_original3060worker_unchanged=True,
            future_controller_must_publish_corrected_world_directly=True,
            do_not_repeat_valid_flat_spin=True,canonical_write_authority=False,training_launch_authority=False,
            no_wait_for_evaluation_to_continue_validated_training=True)
        tracks['budget'].update(current_snapshot=actual['budget'],snapshot_epoch=actual['epoch'],
            actual_tail_adjusted_remaining_seconds=actual['actual_tail_adjusted_remaining_seconds'],new_budget_seconds=0)
        d5.update(epoch=time.time(),nominal_model_curve_offline_completed=True,
            actual_USD_SHA=spring['actual_USD_sha256'],nominal_model_unchanged=True,
            software_k_N_per_m=3500,software_d_N_s_per_m=3,
            existing_software_elastic_force_full_joint_range_N=[649.0263713,865.7044391],
            proposed_uncalibrated_plusminus10percent_force_range_N=[584.1237342,952.2748830],
            measured_hardware_force_stroke_available=False,actual_SDK_force_stroke_readback_completed=False,
            D5_learning_executor_deployed=False,D4_training_not_blocked=True,
            offline_review='D5_NOMINAL_MODEL_CURVE_REVIEW.json',
            next_required=['ActualSDK q/qd/k/d/preloadtarget/drive-effort and elastic-vs-viscous-vs-total/constraint separation inSI',
              'Record missing hardware calibration explicitly; do not adjust nominal law to force300-700N',
              'Only approved uncalibrated engineering pressure with independently verified physical/source bounds; if unavailable progress other approved verifiable groups',
              'Actual episodeRNG/parameter/readback/resume/newphysicalepisode and necessary genuinelynewscope completePPO discard contracts',
              'Select actual complete behavior-reviewed D4 source; safe fullsave/oldlaunch closed/realchildren exited/two locks/active boundary unique next executor'],
            scope_does_not_claim_real_force_certification=True,Git=git)
        tracks['next_D5_preparation']=d5
        for name,obj in [('PLAN_APPROVAL.json',approval),('EXECUTION_TRACKS.json',tracks),('MOE_PLAN_EXECUTION_CURRENT.json',current),('NEXT_D5_FORCE_STROKE_WORK_ORDER.json',d5)]:
            put(name,obj);(R/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
        heading=(R/'D4_BLOCK1_WORLD_DISPATCH_REPORT.md').read_text(encoding='utf8')
        heading+='\nActual production identity and bounded deadlines must be read fresh. Current block2 trainer1243218/start60603499, parent1211569/start59835171, guardian1212716/start59858959 locate only. Read own actual resume startup and previousPASSED source rather than first-block27575 assertions. New CPU-only true-world publisher1242451/start60584170 locate only, already executed, no launch/GPU/canonical authority. Old50-d4-world jobs are retainedD3-only diagnostics; trueD4 world45-anchor/55-bN use347ca418... whereas validflat/spin retain74200ad6...; match archivewithin each kind. Do not hotpatch the243 production controller or oldworker. Futurecontroller publishes correctedworlddirectly. Mainv1.5SHAunchanged; seeD4_WORLD_REPAIR_GIT_RECORDED unique remoteverifiedtrial. All previous once/main/resume, newworld build/deploy/publisher/record/synconce already executed; never rerun. Read-only actualcollectors may be reused by actualstage. Currenttrainingwindow continuesautomatically toblock3; no3060wait/repeatedclock45min. Advanceapproved D5/otherverifiedgroups atsafeactualboundary; forcecalibrationabsence is not currentD4 traininghold. MonitorACTIVEevery2h/healthyquiet, no extra time or allcoursefinishedclaim.\n\n# Prior handoff retained for provenance\n\n'
        put('LATEST_HANDOFF.md',heading+old_handoff)
        proof=dict(epoch=time.time(),receipt_epoch=actual['epoch'],metadata_only=True,
                   runtime_GPU_PPO_canonical_writes=0,master_plan_SHA_unchanged=True,Git=git)
        put('WORLD_CENTRAL_METADATA_SYNCED.json',proof);put('WORLD_CENTRAL_METADATA_SYNCED.json',proof,repair)
        (R/'WORLD_CENTRAL_METADATA_SYNCED.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
        print(json.dumps(proof))
finally:c.close()

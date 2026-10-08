"""Sync reviewed stage metadata only; production/worker/canonical stay untouched."""
from pathlib import Path
import json,sys,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent/'MOD4_D4_WORLD_DISPATCH_REVIEW_20261008';read=lambda p:json.loads(p.read_text(encoding='utf8'))
assert not (R/'D4_D5_ACTUAL_METADATA_SYNCED.json').exists()
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert hashlib.sha256((D.parent/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md').read_bytes()).hexdigest()==MASTER
review=read(W/'reports/D4_MODEL28633_COMPLETE_MATCHED_REVIEW.json');nom=read(R/'D5_NOMINAL_ACTUAL_SDK_REVIEW.json');g=read(R/'D4_COMPLETE_D5_SDK_GIT_RECORDED.json')
assert g['remote_main_tag_peeled_verified'] and not g['push_pending']
actual=read(D.parent/'MOD4_D4_FULL_CONTRACT_20261008/reports/D4_BLOCKS_ACTUAL_VERIFIED.json')
pressure=read(R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json') if (R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json').exists() else None
publication=read(R/'SPRING_PRESSURE_AUDIT_SCOPE_PUBLISHED.json');pressure_actual=read(R/'PRESSURE_SDK_CURRENT_ACTUAL.json')
worker_admission=read(R/'SPRING_AUDIT_WORKER_ADMITTED.json');worker_actual=read(R/'PRESSURE_WORKER_CURRENT_ACTUAL.json')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports';spring='/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008/reports'
try:
    with c.open_sftp() as f:
        def get(name):return json.loads(f.open(central+'/'+name).read())
        def put(name,obj,where=central):
            raw=obj.encode('utf8') if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2).encode('utf8')
            path=where+'/'+name;tmp=path+'.spring_actual_tmp'
            with f.open(tmp,'wb') as out:out.write(raw)
            f.posix_rename(tmp,path);assert f.open(path).read()==raw
        approval=get('PLAN_APPROVAL.json');tracks=get('EXECUTION_TRACKS.json');current=get('MOE_PLAN_EXECUTION_CURRENT.json');d5=get('NEXT_D5_FORCE_STROKE_WORK_ORDER.json')
        assert approval['approved'] and approval['approved_plan_sha256']==MASTER and 'S2' in approval['allowed_stages']
        handoff=f.open(central+'/LATEST_HANDOFF.md').read().decode('utf8')
        for name,obj in [('PLAN_APPROVAL.json',approval),('EXECUTION_TRACKS.json',tracks),('MOE_PLAN_EXECUTION_CURRENT.json',current),('NEXT_D5_FORCE_STROKE_WORK_ORDER.json',d5),('LATEST_HANDOFF.md',handoff)]:
            backup=name.rsplit('.',1)[0]+'_BEFORE_D4_COMPLETE_D5_ACTUAL_20261008.'+name.rsplit('.',1)[1]
            try:f.stat(central+'/'+backup)
            except FileNotFoundError:put(backup,obj)
        for n in ('D4_MODEL28633_COMPLETE_MATCHED_REVIEW.json','D4_MODEL28633_COMPLETE_MATCHED_REPORT.md'):
            put(n,(W/'reports'/n).read_text(encoding='utf8'))
        for n in ('D4_COMPLETE_D5_SDK_GIT_RECORDED.json','D5_NOMINAL_ACTUAL_SDK_REVIEW.json','D5_NOMINAL_ACTUAL_SDK_REPORT.md',
                  'SPRING_PRESSURE_CPU_PASSED.json','SPRING_PRESSURE_ADAPTER_CPU_PASSED.json','SPRING_PRESSURE_SDK_PUBLISHED.json','PRESSURE_SDK_CURRENT_ACTUAL.json',
                  'SPRING_PRESSURE_INDEX_REVIEW_PUBLISHED.json','PRESSURE_SDK_FIRST_INDEX_ERROR.json','PRESSURE_DEPENDENCY_ADMISSION_FIRST_ERROR.json',
                  'PRESSURE_DEPENDENCY_WORKER_ADMITTED.json','PRESSURE_WORKER_CURRENT_ACTUAL.json','PRESSURE_SDK_SECOND_FIXED_BASELINE_ERROR.json',
                  'SPRING_PRESSURE_AUDIT_SCOPE_PUBLISHED.json','SPRING_AUDIT_WORKER_ADMITTED.json',
                  'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json','D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REPORT.md'):
            if (R/n).exists():
                raw=(R/n).read_text(encoding='utf8');put(n,raw);put(n,raw,spring)
        approval.setdefault('execution_events',{})['MOD4-D4-COMPLETE-D5-NOMINAL-ACTUAL-001']=dict(epoch=time.time(),status='ACTUAL_D4_MATCHED_RETENTION_AND_NOMINAL_SPRING_SDK_REVIEWED_PRESSURE_PREPARATION',
            existing_S0E_S2_authorization_only=True,new_human_approval_inferred=False,master_plan_changed=False,production243_changed=False,
            nominal_force_is_SDK_approximate_not_PhysX_drive_or_hardware_force=True,hardware_force_stroke_available=False,D5_pressure_actual_SDK_reviewed=bool(pressure),D5_learning=False,Git=g)
        cur=actual['current'];assert cur and cur['block']==3
        current.update(epoch=actual['epoch'],actual_phase=actual['phase']['phase'],parent=actual['actual_owner'],guardian=actual['actual_guardian'],trainer=actual['actual_child'],
            source=actual['phase']['source'],run=cur['run'],active_log=actual['phase']['active_log'],deadline_epoch=actual['phase']['deadline_epoch'],
            current_block=3,own_current_save=cur['checkpoint'],live_health=cur['live_health'],live_health_is_not_final=True,actual_D4_to_D4_resume_startup=cur['startup'],
            block1_complete_reviewed=True,block2_complete_source_health_reviewed=True,block2_actual_updates=1058,block2_actual_steps=507840000,
            block2_source=review['block2']['checkpoint'],block2_health=review['block2']['health'],block2_behavior_review_pending=True,
            formal_behavior_pending=True,candidate28633_complete_firstseed_white3_reviewed=True,D4_candidate_behavior=review['candidate28633'],
            behavior_review_scope=review['scope'],new_budget_seconds=0,all_courses_finished=False,latest_stage_Git=g)
        tracks['epoch']=actual['epoch'];tracks['learning']=current
        tracks['evaluation'].update(epoch=review['epoch'],new_D4_baseline_scope_accepted=True,new_D4_closedloop_scope_pending=False,
            candidate28633_complete_limited_scope=True,candidate29690_behavior_review_pending=True,current_block3_behavior_pending=True,
            old_world_job_not_D4_evidence=True,old_world_diagnostics_preserved=True,true_world_package_SHA='347ca4183e4f4cfa4ab98492637718996b62b9d4b1cb9f7f4119514484356ce5',
            future_controller_must_publish_corrected_world_directly=True,do_not_repeat_valid_flat_spin=True,
            D5_nominal_SDK_review=nom,D5_pressure_SDK_publication=publication,D5_pressure_SDK_current_actual=pressure_actual,D5_pressure_scope_review=pressure,
            production243_unchanged=True,original3060worker_code_errors_taskXML_preserved=True,
            new_explicit_frozen_worker_authority=worker_admission,new_worker_current_actual=worker_actual,
            current_worker='eval_worker_spring_audit_review.py',current_worker_task='MOD4_AsyncFrozenEvaluation_v15_spring_audit_review',
            old_failed66_and67on_unexecuted66on_preserved_and_excluded=True,valid67off_reused=True,canonical_write_authority=False,training_launch_authority=False,no_wait_for_evaluation_to_continue_validated_training=True)
        tracks['budget'].update(current_snapshot=actual['budget'],snapshot_epoch=actual['epoch'],actual_tail_adjusted_remaining_seconds=actual['actual_tail_adjusted_remaining_seconds'],new_budget_seconds=0)
        d5.update(epoch=time.time(),actual_SDK_nominal_q_qd_k_d_preload_approximate_effort_readback_completed=True,
            actual_separate_PhysX_drive_force_measured=False,actual_constraint_force_measured=False,measured_hardware_force_stroke_available=False,
            nominal_parameter_readback_review='D5_NOMINAL_ACTUAL_SDK_REVIEW.json',nominal_model_unchanged=True,
            first_engineering_stiffness_factor_bounds=[.9,1.1],stiffness_N_m_bounds=[3150,3850],hardware_bound_certification=False,
            pressure_component_CPU_contracts_passed=10,pressure_adapter_CPU_contracts_passed=6,
            pressure_actual_SDK_published=True,pressure_actual_SDK_review_completed=bool(pressure),pressure_actual_SDK_scope=pressure,
            D5_learning_executor_deployed=False,D4_training_not_blocked=True,
            next_required=['Reuse actual completed nominal/CPU/pressureSDK evidence by exact source SHA; do not repeat valid67off or68on, clock45min or existingPPO ranges',
                'If pressureSDK is accepted, complete full actor/critic/std/optimizer/D1-D4/spring/global-named CUDA state save-resume and explicit newepisode contract',
                'Native20k and necessary genuinelynewrange128x2/20kx4 completePPO discard under unique canonical safe authority',
                'No hardware force-stroke calibration or300-700N certification; retain nominal3500 preload/damping/limits and explicitly label engineering pressure',
                'Select actual full behavior-reviewed D4 source; direct correctedworld publication, unique bounded executor at complete save/realchild exit/closed oldlaunch/two locks/clear active boundary'],
            scope_does_not_claim_real_force_certification=True,Git=g)
        tracks['next_D5_preparation']=d5
        for name,obj in [('PLAN_APPROVAL.json',approval),('EXECUTION_TRACKS.json',tracks),('MOE_PLAN_EXECUTION_CURRENT.json',current),('NEXT_D5_FORCE_STROKE_WORK_ORDER.json',d5)]:
            put(name,obj);(R/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
        heading=(W/'reports/D4_MODEL28633_COMPLETE_MATCHED_REPORT.md').read_text(encoding='utf8')+'\n\n'+(R/'D5_NOMINAL_ACTUAL_SDK_REPORT.md').read_text(encoding='utf8')
        if pressure:heading+='\n\n'+(R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REPORT.md').read_text(encoding='utf8')
        heading+='\nLatest actual identities and deadlines override snapshots. Block3 parent1211569/start59835171, guardian1212716/start59858959 and trainer1273629/start61325294 locate only. Firstpressure66-off constructor failed CUDA-index .numpy before its setter/timed loop;66-on neverexecuted, bothimmutablepackages retained. Corrected67-off completed and isreused;67-on hit inheritedD0 fixed3500 observer forintendedD5 stiffness. New68-on observer verifiesactual drive/buffer/model against independentD5 state, keepsallotherD0checks andrestoresnominalobserverafterread; originalmild_dr.py byteexact. Afteractualpreviousworkers/childrenexit andfreesharedlock, currentnewexplicitworker17640 eval_worker_spring_audit_review.py/newdemandtask was admitted, previousdemandsDisabled. It excludesonly66invalidand67onfailed, keepscompletedvalid67off/alloldresultswithoutreplay, andcontinuesfutureD4jobs. Currentattention isSPRING_AUDIT_WORKER_ATTENTION; WORKER_ATTENTION/PRESSURE_DEPENDENCY_WORKER_ATTENTION arehistory. InitialCPUadmissionreader counteditsownvenvparentasGPU/refusedbeforetaskmutation; independentnewreader auditedexactCPUparent/childchain. NoD5learningexecutor/native20k/newscopePPO/fulllearningresume yet. Mainv1.5SHAunchanged/existingS0E-S2authorizationonly/hardwarecalibrationabsent. ReadD4_COMPLETE_D5_SDK_GIT_RECORDED. Allstage/publish/CPU/record/sync/deployonce executed, oldmain/resume prohibited. MonitorACTIVEevery2h/healthyquiet, norepeatedclock45min/preflightortrainingwait3060. Current243protected; nextuniqueexecutoratfullsave/oldlaunchclosed/realchildexit/twolocks/clearactive. Noallcoursefinishedorextratime.\n\n# Prior handoff retained for provenance\n\n'
        put('LATEST_HANDOFF.md',heading+handoff)
        proof=dict(epoch=time.time(),metadata_only=True,production4090_training_runtime_PPO_canonical_writes=0,
                   new_explicit_frozen_worker_recovery_authority=True,master_plan_SHA_unchanged=True,Git=g)
        put('D4_D5_ACTUAL_METADATA_SYNCED.json',proof);put('D4_D5_ACTUAL_METADATA_SYNCED.json',proof,spring)
        (R/'D4_D5_ACTUAL_METADATA_SYNCED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
finally:c.close()

"""Freeze exact saved E2/E3 evidence, original criteria and next-purpose queue."""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent;T=HERE.parent;W=T.parent;R=HERE/'reports';SRC=HERE/'source'
OV=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
E2=OV/'E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V5'
E3=OV/'E3_CONCRETE_INSTANCE_OWNER_EFFORT_GAP_PLAN_SOURCE_20261030_V14'


def read(path):
    assert path.suffix in ('.json','.md','.py','.txt')
    return json.loads(path.read_bytes())


def row(path):
    assert path.suffix in ('.json','.md','.py','.txt')
    raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())


def write(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False)


def main():
    cpu=read(R/'CPU213_ACTUAL.json');assert cpu['passed']
    purpose=read(R/'CPU213_PURPOSE_FROZEN.json')
    for value in purpose['source_rows']:
        raw=Path(value['path']).read_bytes()
        assert len(raw)==value['bytes'] and hashlib.sha256(raw).hexdigest()==value['SHA']
    expert_rows=[]
    for name in ('E2','E3'):
        p=purpose['saved_CPU_proofs'][name];report=read(Path(p['path']))
        manifest=(OV/'E2_PPO50_gas400_source_preparation_20261028/E2_COMPLETE_INSTALL_MANIFEST_V1.json'
            if name=='E2' else OV/'E3_97_GAS400_COMPLETE_RUNTIME_SOURCE_CPU_PREPARATION_V1/E3_COMPLETE_INSTALL_MANIFEST_V1.json')
        data=read(manifest)
        wanted=(('train_E2_full_resume_v1.py','e2_directional_spin_runtime_v1.py','e2_command_checkpoint_v1.py')
            if name=='E2' else ('train_E3_fullstate_v1.py','e3_recovery_runtime_v1.py','e3_public_recovery_phase_v1.py','e3_fullstate_checkpoint_v1.py','e3_reset_bank_cache_v1.py'))
        runtime=[value for value in data['files'] if Path(value['relative']).name in wanted]
        critical={key:report[key] for key in ('passed','whole_model_all_tensors_finite',p['critical_D0_D7_key'],
            'actor9_critic8_STD6_original35_38','all17_Adam_and_original_nonLR_optimizer_settings',
            'new_branch_skill_qualified','WM_transition_data_collection_executed')}
        expert_rows.append(dict(expert=name,selected_formal=report['model'],
            selected_saved_CPU_proof=dict(**row(Path(p['path'])),critical_saved_flags=critical),
            source_iteration=p['stored_iteration'],Adam17=p['Adam_step'],LR=p['LR'],
            source_updates=report['new_updates'],nominal_gas_N_each=400,nominal_k_N_m=2000,
            policy_hz=50,feedback_hz=100,physics_us=2500,TGS=[32,4],dtype='F32',
            original_interface=dict(actor_obs=35,critic_obs=38,actions=6,fixed_original_SI_scales=True),
            original_complete_runtime_manifest=row(manifest),selected_original_runtime_rows=runtime,
            manifest_initial_typed_PT_is_history_not_selected_formal=True,
            only_selected_formal_above_may_be_used_in_a_future_NEW_task=True,
            original_models_not_opened_statted_hashed_or_decoded=True,
            format_normalized=True,full_original_skill_accepted=False,complete_SuperMimic_conversion=False))
    write('FORMALS213_EXACT_NORMALIZED_SOURCES_CPU_PROOFS.json',dict(
        schema='mod4.old_experts213.normalized_saved_scope.v1',epoch=time.time(),experts=expert_rows,
        evidence_scope='selected189/208 saved formal leads plus exact originalE2/E3 sources;not a global-latest model search',
        historical18_is_E0_matrix_not18actors=True,
        current_W35_210_actual_learning_status='ROOT_ACTUAL_RECEIPTS_ONLY_NOT_READ_OR_INFERRED_BY213',
        actual_new_model_raw_NPZ_USD_SDK_GPU_remote_calls=0))
    write('SKILL213_ORIGINAL_CRITERIA_EXPOSURE_AND_GAPS.json',dict(
        schema='mod4.old_experts213.original_skill_scope.v1',
        original_world_criterion=dict(source=str(W/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md'),
            source_lines=[223,225,233],along_cross_tol='max(.03,.1V)',V_half_m_s_tol=.05,
            signed_yaw_error_rad_s=.2,requires_complete_same_UID_original_episode_valid_samples=True,
            all_terminal_false_partial_and_no_exposure_retained=True,
            no_arbitrary90_95_100_percent_aggregate_graduation_line=True,
            pure_signed4pi_is_not_moving_signed4pi=True),
        E2=dict(command_scope='E2_WORLD_MOVING_SIGNED4',terrain='original flat',
            standing_fraction=.1,pure_fraction=.3,moving_fraction=.2,transition_within_pure=1/3,
            moving_signed_yaw_rad_s=[-4,4],world_progress_goal_m_s=.5,
            pure_abs_yaw_range=[1,12.566370614359172],transition_seconds=12,resample_seconds=[12,16],
            original_profiles=['standing','straight_negative','straight_zero','straight_positive',
                'pure_negative','pure_positive','transition_initial_negative','transition_initial_positive',
                'moving_yaw_minus4','moving_yaw_plus4'],
            reset='Original flat reset filter contains74eligible poses;74 is NOT a fixed pose index and is not W35 pose34 substitution',
            latest_saved_behavior=row(OV/'E2_V5_FINAL_EARLY_COMMAND_SAVED_TEXT_REVIEW_20261029_V1/HANDOFF_FROZEN_E2_V5_SAVED_TEXT_COMPLETE_COMMAND_PROFILE_REVIEW.md'),
            actual_consumed_V5=dict(num_envs=20000,controls=900,seconds=18,
                complete_naturally_observed_commands=20000,window_ended_acted_commands=20000,
                command_events_total=40000,original_non_timeout_events=0,time_out_events=0,
                moving_cycle_events=39594,cycle_population_seconds=63582.345703,
                actual_cycle_progress_m_s=.592000451,integrated_reference_progress_m_s=.501076759,
                nominal_world_cycle_abs_error_m_s=.106909574,reference_abs_error_m_s=.105483486,
                straight_zero_exposure=0,not_a_tracking_pass=True),
            gaps=['Per same-episode/command UID full signed cycle cross displacement and signed-yaw integral/error;old aggregates cannot reconstruct these',
                'All original false/terminal/partial spans and actual sampled overshoot endpoints;do not hide failure prefixes',
                'Complete signed4pi pure motion and complete12s transition facts retained separately from2pi moving windows',
                'Straight_zero unexposed is UNKNOWN;standing is a separate original profile',
                'No numerical standing/straight/height global graduation rule found in saved review;do not invent one',
                'Original D0white_v3/D1-D7 whole-skill coverage is not proven by format or a single18s frozen run',
                'No actual native127+54+31+8x6 executed-action dataset'],
            selected_213_new_component='source/e2_cycles213.py;source/e2_panel213.py;source/evaluate_e2_world213.py',
            full_skill=False),
        E3=dict(original_recipe_count=13,fall_recipes=list(range(12)),normal_zero_baseline_recipe=12,
            commands='Original RecoveryEnv.publish sets3BODYcommands zero and public request mode;fallen zero is not standing',
            request_rule='recipe!=12 and public age<300;age increments2 each50Hzcontrol =>3s',
            original_credit=dict(gravity_z_less_than=-.984807753,root_3D_speed_less_than_m_s=.03,
                angular_3D_speed_less_than_rad_s=.2,stable_public_ticks=50,
                public_ticks_per50Hz_control=2,stable_seconds=.5,
                one_credited_edge_per_original_attempt=True,soft_peak_upright_gain_not_a_recovery_credit=True),
            exact_original_mask_scope='Original bad_orientation/base_contact and namedheight/lin_vel_z rewards are request-masked for first3s by existing E3 source;closure2mm/mimic.01 stay active. Preserve this original scope,do not copy E0 terms or widen masks.',
            reset='Original immutable32,022,178B bank SHA78af9f…;nearest.25 full30joint pose/13 original xyzwrecipes,not ordinaryE0reset or new fakeair placement',
            latest_saved_behavior=row(OV/'E3_V4_FINAL_SAVED_TEXT_RECIPE_PHASE_REVIEW_20261029_V1/HANDOFF_FROZEN_E3_V4_SAVED_TEXT_REVIEW.md'),
            actual_consumed_V4=dict(num_envs=20000,controls=600,seconds=12,recovery_credit_events=141,
                observed_request_profile_exposures=414048,
                zero_credit_recipe_ids=[0,5,11],normal_baseline12_not_a_recovery_failure=True,
                non_timeout_union_events=396509,unique_reset_envs=6445,
                closure_reason_events=395685,orientation_reason_events=825,base_contact_reason_events=542,
                reason_overlap=543,time_out_events=0,
                credited_env_global_union='UNKNOWN;existing text bound23..141',
                exposure_ratio_not_attempt_success_probability=True),
            retained_action_chain=dict(V10_raw_singlepass_consumed=True,raw_rereads_in213=0,
                original_54wheel_comparator_false_and59neutral_unknown_retained=True,
                source='E3_V10_ACTUAL_ONE_PASS_JOIN_VALUES_F32_REVIEW_HANDOFF_20261030_V1',
                target_outside_position_limits_not_proof_of_illegal_effort_or_unique_closure_cause=True,
                no_target_clamp_or_PD_gain_or_guard_change_selected=True),
            gaps=['Actual concrete robot/legs/wheels instance MRO and ordinary nonabstract method owners,then exact observed source bytes/timing graph',
                'DCMotor clip mutates cached velocity;never recompute compute/clip for shadow estimates',
                'Only original cached effort/buffer ingress at natural call boundary after owner/source timing is proven;no guessed equivalent effort',
                'Per-attempt UID/timeline,all failures,credit edge before reset and actual support recovery;exposure ratios or soft gains cannot replace these',
                'Original13recipe andE0handoff retention functional acceptance;no aggregate invented pass rate',
                'No complete native50Hz own127+dynamic54+static31 terminal/action/reset dataset'],
            next_component='source/e3_existing_owner213.py plus unchanged source/existing_owner_v14_reference213.py',
            identity_bootstrap_constructor_and_runtime_caller='NOT_SELECTED_NOT_READY;do not revive V12/V13 recursive abstract-base collectors',
            full_skill=False)))
    worker=row(SRC/'evaluate_e2_world213.py')
    write('NEXT213_E2_UNCONSUMED_CALLER_TASK_AND_ADMISSION.json',dict(
        schema='mod4.experts213.E2_missing_world_field_queue.v1',status='NEW_SOURCE_AND_CPU_COMPONENT_PASS_TARGET_METADATA_NOT_YET_ADMITTED',
        new_purpose_id='E2_COMPLETE_WORLD_SIGNED_UID_FIELDS213_NEW_UNUSED',
        rationale='New cross/signedyaw/original-terminal fields unavailable from already-consumedV5 small summaries;no originalraw reread orold900once',
        worker=worker,CLI='ACTUAL_SDK_PYTHON -B -X utf8 NEW_UNUSED_JOB/evaluate_e2_world213.py --job-root NEW_UNUSED_JOB',
        input_layout=dict(base= str(E2/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json'),
            selected_formal_relative='source/E2_ADAPTED93_FINAL92.pt',
            selected_model_SHA=expert_rows[0]['selected_formal']['SHA'],selected_model_bytes=14615089,
            copy_213_source_to_job_root='all source/*.py except train_e2_213.py;source_cache213 must be atjobroot because the cache is established before runtimepath setup',
            trainer_installed_relative='runtime/isaac/mod4/train_e2_213.py',
            original_runtime_code_and_assets_unmodified=True,
            no_initial_typed_PT_or_W35_E0_E3_substitution=True),
        task_file='FROZEN_CASE_TASK.json',task_minimum=dict(
            kind='MOD4_E2_MISSING_FULL_WORLD_FIELDS213',source_SHA=expert_rows[0]['selected_formal']['SHA'],
            worker_SHA=worker['SHA'],num_envs=20000,controls=1200,warmup_controls=100,
            maximum_worker_seconds=1680,no_optimizer_steps=True,
            actual_target_SDK_new213_source_admission_passed='actualtrueonly',actual_private_GPU_EX_held_by_parent='actualtrueonly',
            canonical72_known_owner_readonly_passed='actualtrueonly',domain_kind='E2_WORLD_MOVING_SIGNED4',
            original_Adam=859300,original_LR=.00022500000000000002,
            GPU_UUID='root actual selected UUID;no host/GPU hardcode',
            early_observer_SHA=row(SRC/'e2_early_original_resample_observer_v2_complete.py')['SHA'],
            command_instances_SHA=row(SRC/'e2_observed_command_instances_v1.py')['SHA'],
            actual_CPU_report_SHA='actual new213 target-source report,not a dummy oroldV5schema',
            actual_CPU_waited_proof_SHA='actual original waitedRC0 report',
            ground_provider_contract='same actual original E2 flatheight-provider source contract from selectedV5'),
        required_root_prepared_files=['E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json',
            'E2_NEW86_CPU_ORIGINAL_WAIT_PROOF.json (passed/actual_waited/returncode0)',
            'E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json (reuse saved exactCPU report,not PTdecode)',
            'original_run_manifest.json SHAad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f'],
        target_source_metadata_work_remaining=['Bind NEW entry train_e2_213,worker/panel/cache namespaces and both old/new exact source SHA inverse deltas',
            'Read actual target CommandTerm methodsource/ABI,original E2 sampler/resume+new explicitcache/earlyobserver ordering and original flatheight API',
            'Retain selected RSL/SDK/TensorDict package proofs and actual sourceCLI/receipt graph;oldV5metadata reader is tied tooldmanifest and cannot be blindly rerun',
            'No new modelCPU decode;reuse exact saved wholeformal CPU proof and one declared runtime source read/decode'],
        source_read_contract=dict(selected_PT_physical_reads=1,selected_PT_decodes=1,
            cache='source/source_cache213.py,derived unchanged generic208V3kernel except namespace',
            original_D0_D7_guard_code_preserved=True,global_Path_or_open_redirection=False,
            own_new_roundtrip_artifact_reads_separate=True,old_JSONL_or_NPZ_review_reads=0),
        resource_and_control=dict(exclusive_owner='ROOT_ONLY_GLOBAL_SERIAL_SSH',
            sequence='freshLOCALexactCIM;fresh72CNone OR exact actual current owner/run/go;CLOSE72 beforetarget',
            startup='fresh4090 free>15669MiB/util<=30,RAM>32GiB,disk>25GiB,privateEX+originalsharedguards;nonemptycomputeUUIDallowed',
            worker_seconds=1680,original_supervisor_seconds=1800,
            parent_wait_and_exit_and_private_release_required=True,
            parent_must_bound_SDK_startup=True,canonical_writes=0,no_hotadd_or_training_stop=True,
            no_new_budget_or_Go_or_automation=True),
        actual_runtime_scope='original meanactor exactlyonce/control andvec.step once;1200requested=24s;retain early actualorigin,all original profile/phase/terminal/partial facts',
        new_producer='frozen_regression/E2_FULL_WORLD_SIGNED_UID_CYCLES_213_ACTUAL.jsonl;192MiB bounded with explicitretention_limited/streamSHA',
        metadata_only_read_allowlist=['ACTUAL_E2_93_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json',
            'ACTUAL_NATIVE24_E2_40050_CLOCK_QUEUE.json','ACTUAL_E2_EARLY_POSTRESTORE_RESAMPLE_BEFORE_MEAN_ACTION.json',
            'BOUNDED_FROZEN_E2_N20K_PROFILES_ACTUAL.json','E2_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json',
            'E2_FULL_WORLD_CYCLES213_ACTUAL.json','SOURCE213_SELECTED_PT_READ_COUNTS.json'],
        default_for_JSONL_gz_NPZ_PT='producer path/bytes/existingstreamSHA only;no content/hash transfer',
        no_instantaneous_MAE_or_aggregate_pass_substitution=True,
        actual_dispatched=False,full_E2_skill_accepted=False,full_SuperMimic_conversion=False))
    write('NEXT213_E3_EXISTING_INSTANCE_ONLY_TASK_AND_GAPS.json',dict(
        schema='mod4.experts213.E3_concrete_owner_queue.v1',status='REUSABLE_METADATA_COMPONENT_ONLY_BOOTSTRAP_SOURCE_NOT_SELECTED',
        components=[row(SRC/'e3_existing_owner213.py'),row(SRC/'existing_owner_v14_reference213.py')],
        frozen_original_V14_plan=row(E3/'CONCRETE_INSTANCE_OWNER_AND_EFFORT_SEMANTIC_GAP_MINIMUM_EVIDENCE_PLAN.json'),
        proposed_new_purpose=dict(purpose_id='E3_CONCRETE_EXISTING_OWNER213_NEW_UNUSED',kind='E3_ACTUAL_EXISTING_INSTANCE_OWNER213',
            original_target='same actual E3 source210 SDK/backend/config,not inferred from current W35/SDK frontend defaults',
            model_opens=0,raw_opens=0,NPZ_opens=0,actor_calls=0,extra_physics_steps=0,
            objects='already naturally created own robot plus original legs/wheels instances passed directly',
            manager='only already retained constructor name,else UNKNOWN'),
        callable='e3_existing_owner213.observe_original_e3_instances(robot,legs,wheels,purpose=...,already_retained_manager_name=...)',
        no_SDK_or_Torch_import_or_fileIO_in_probe=True,
        no_getters_or_descriptor_binding_or_compute_clip_apply_calls=True,
        purpose_authorizes_no_constructor_or_SSH_by_itself=True,
        next_root_source_action='Select and source-prove a minimal model-free originalN1 robot constructor closure on actualE3target;must not construct RecoveryEnv/bank/learner merely for type names',
        complete_runtime_bootstrap='NOT_PRESENT;callable component is not an executable N1bootstrap or actualowner proof',
        after_real_owners='One new bounded exact-source purpose for distinct observed concrete owner files,then originalwrite→apply→compute→clip→finalbuffer timing;no more recursive abstractbasefetch',
        future_effort_scope='Only after source/ABI/timing bind,NEW original20k fullrestore/native24/first40naturalcallbacks shadowlog-only;no extra clip/compute or target/PD/root edits',
        original_selected_formal_SHA=expert_rows[1]['selected_formal']['SHA'],
        original_Adam17=866060,source_iteration=43090,LR=.0002562890625000001,
        current_format_normalized_but_effort_or_recovery_skill_unqualified=True,
        old_V10raw_consumed_V11_V12_V13_errors_and_V14_unknowns_unchanged=True,
        root_exclusive_resource_CIM_72close_beforetarget_rules_same_asE2=True,
        no_current_training_interference=True))
    write('SUPERMIMIC213_ACTUAL_REMAINING_NOT_COMPONENT_RENAME.json',dict(
        selected_WM190=dict(source=str(T/'EXPERTS_RM70_SUPERMIMIC_READY_QUEUE_V190_20261031/teacher_world_model50_core190_v3.py'),
            SHA='9c240e24f41adb5a6e6724da8dbb027db023ef9e75feb3b92b9260dd63f8562c',
            only_previous128synthetic_pairs_and1WMupdate=True,previous_tests_not_rerun=True,
            source_scope='ownflat E0/E2 only;not E3recovery validation or RM70geometry',Pi_Critic_updates=0),
        actual_E2_E3_native_dataset_pairs=0,actual_213_WM_Pi_Critic_updates=0,
        required=['Own exact50Hz transitions:packed127 state+dynamic54aux+static31,raw/clipped6 and actual8processedtargetvectors+2feedbacktimestamps,episode/command UID,pre-reset endpoint/alloriginalreasons',
            'Same original named30joint/6motor order and typed source/hash/config/clock provenance;no zero-fill for missing fields',
            'E2 actualstate packing on flat and E3 public recovery/contacts/reset dynamics need separate own runtime bridge;cycle/attempt summaries are not that dataset',
            'Actual target source+SDK integration and bounded measured pairs,then independent nativeWM/Pi/Critic+norm/optimizers/RNG/fullsave;do not rename PPOweights',
            'Standalone BC matches original clipped6 outputs;later task-specific differentiable originalreward/BPTT needs independent frozen admission',
            'Deployment-available feedback/history/commands/publicrequest only;hiddenxi/recipe/privilegedterrain cannot leak into studentactor',
            'Own original fullskill matrices incl retained modes,valid signedcycles and genuineE3credit/support recovery/failures before replacing frozenPPOteacher'],
        no_new_aggregate_graduation_or_FP64_bitwise_precision_gates=True,
        normalized_format_does_not_imply_skill_or_complete_conversion=True))
    write('SOURCE213_ERRORS_AND_ONCE_STATUS.json',dict(
        actual_new_attempts=[
            dict(ID='NEW213_SAVED_E2_E3_METADATA_SOURCE_PREPARATION',status='ORIGINAL_SOURCE_DERIVATION_REJECTED_PARTIAL_FILES_RETAINED',
                reason='CRLF exact multi-line inverse mismatch while deriving E2train;no model/SDK/actor/physics execution'),
            dict(ID='NEW213_SOURCE_DERIVATION_V2_CRLF_REMAINDER_ONLY',status='SOURCE_REMAINDER_COMPLETED',
                fix='Normalize source text CRLF for newderivation only;continue only previously unwritten outputs;old error/partialsource/script untouched'),
            dict(ID=cpu['ID'],status='PASSED',groups=3,metadata_checks=12,negative_refusals=4,
                synthetic5env240controls=True,no_old_fixture_replay=True)],
        reader_events=['Named E3V9/E3V10 handoff filename guesses missing;read actual exactHANDOFF filenames instead;not robotfailures',
            'Broad masterplan/search and a combined source read output clipped;relevant source/line slices separately read;not a numerical decision from clipped output',
            'E2/E3 CPUreports use top-level flags,not .review objects;missing projection returnednull and corrected before the new exactschema purpose',
            'Install manifests use files,not small_source_files;corrected named metadata projection before source selection'],
        old_E2V5_actual900_consumed_despite_stale_UNUSED_filename_or_handoff=True,
        old_E3V4_V10_V11_V12_V13_consumed_or_failed_not_replayed=True,
        unchanged_V14_probe_component_UNUSED_not_its_old_tests=True,
        W35_208_source_and_210_runtime_not_changed=True,
        all_new_reports_Git='PENDING_ROOT_UNIQUE213_OR_ORDINARY_SUPPLEMENT;NO_CHILD_GIT'))
    with (HERE/'HANDOFF213.md').open('x',encoding='utf8') as f:f.write('''# Old experts next-source213

Saved E2final92 and E3final87 are400N/50Hz format-normalized,not whole-skill graduates. Exact selected sources/CPUreportSHAs/runtime rows are in reports/FORMALS213_EXACT_NORMALIZED_SOURCES_CPU_PROOFS.json. E2: b3ae94…a1e1,14,615,089B,17Adam859300,RSL42822,LR.00022500000000000002. E3:1cd999…84b8,14,715,029B,17Adam866060,RSL43090,LR.0002562890625000001. No model/raw/NPZ/USD/SDK/GPU/remote read was performed by213.

New E2 entry source/evaluate_e2_world213.py retains original flat plant/sampler/reward/35-38-6/D0-D7/meanactor,requests1200controls24s with original1680s worker limit,and adds original-same-UID cross/signedyaw/pre-reset cycle facts. See reports/NEXT213_E2_UNCONSUMED_CALLER_TASK_AND_ADMISSION.json for exact installation/Task/resource interface and remaining actual target-source metadata binding. This is a NEW missing-field source caller,not permission to rerun consumedV5/old900once or read its JSONL. SourceCache is one exactselectedPT read/decode;oldfullCPU proof is reused. Actual targetmetadata/supervisor/readers need a new explicit source/receipt join;they are not falsely marked admitted here.

New E2 field/schema CPU purpose passed3groups/12savedproofjoins/4negative refusals,5syntheticenv×240controls/12complete events. It imports no original SDK or actor and does not test fulltargetruntime. Old E2 actual18s moving cycle absolute error.10691m/s remains;cross/signedyaw missing facts cannot be reconstructed from summaries. Original world bounds remain max(.03,.1V) and signedyaw.2rad/s;no90/95/100%line. E2 movingyaw±4 is not4pi moving. Straightzero unexposed remainsUNKNOWN.

E3 preserves its exact original3s publicrequest/.5s stability credit,all13recipes and originalrequest mask scope. Its141credit events/414048profile exposures are not an attempt success rate;396509non-timeout resets and zero-credit0/5/11 remain. No target clamp,gain,closure2mm/mimic.01 or originalmasked guard is changed. Source/e3_existing_owner213.py reuses unchangedV14 metadata probe for already-created ownrobot/legs/wheels. The minimal N1 model-free constructor closure is still NOTSELECTED:do not call the component a runnablebootstrap,create fullRecoveryEnv/bank merely for names,or repeat abstractbasefetch. Actual concreteowners and their distinct exactsource/timing are needed before any effort shadow;DCMotorclip must not be invoked again.

Selected190WMv3 is a flat WMcomponent only,with previous128syntheticpairs/oneWMupdate and0Pi/Criticconversion. Actual127+54+31+8×6 data,own50Hzcollector/nativepolicy/critic/norm/optimizers and retained fullskills remain. No new WM runtime dependency is added to healthy210.

Original213 CRLF source inverse refusal and partialfiles are preserved;independentV2 continued unwritten files only. All new reports/errors/sources await root Git archive. W35/210 actuallearning is ROOT receipts only;213 performs no SSH/SDK/GPU/PT/raw/NPZ/Git and never hotpatches them.
''')
    allrows=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file():allrows.append(dict(**row(path),relative=path.relative_to(HERE).as_posix()))
    index=HERE/'INDEX213_FROZEN.json'
    with index.open('x',encoding='utf8') as f:json.dump(dict(
        schema='mod4.old_experts213.complete_source_evidence_index.v1',epoch=time.time(),
        files=allrows,CPU_source_rows=purpose['source_rows'],CPU_actual=cpu,
        status='SOURCE_CPU_COMPONENT_PASS_ACTUAL_TARGET_BINDING_PENDING',
        E2_new_caller_ready_for_target_source_admission=True,E3_runtime_bootstrap_ready=False,
        full_E2_E3_skills_or_SuperMimic_conversion=False,all_model_raw_SDK_GPU_remote_Git_calls=0,
        old_false_errors_and_source_retained=True,root_Git_pending=True),f,indent=2)
    print(json.dumps(dict(index=row(index),files=len(allrows),E2_worker=worker)))


if __name__=='__main__':main()

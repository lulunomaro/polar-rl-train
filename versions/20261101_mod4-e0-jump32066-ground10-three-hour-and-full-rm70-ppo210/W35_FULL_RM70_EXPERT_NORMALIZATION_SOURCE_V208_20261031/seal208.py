"""Close NEW208 source/CPU reports for root's sole Git/control handoff."""
from pathlib import Path
import hashlib, json, time

HERE=Path(__file__).resolve().parent
T=HERE.parent; W=T.parent; R=HERE/'reports'


def read(path):return json.loads(path.read_bytes())


def digest(path):
    raw=path.read_bytes()
    return dict(path=str(path),relative=path.relative_to(HERE).as_posix(),
                bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())


def write(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False)


def main():
    cpu=read(R/'CPU208_ACTUAL.json'); assert cpu['passed']
    purpose=read(R/'CPU208_PURPOSE_FROZEN.json')
    for row in purpose['source_rows']:
        raw=Path(row['path']).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
    scope=read(T/'FROZEN_EXPERTS_400N50_SKILL_SUPERMIMIC_CONTINUATION_V189_20261031/reports/EXPERT189_SAVED_FORMALS_AND_SKILL_GAPS_ACTUAL.json')
    expert_snapshot=[]
    for row in scope['experts']:
        expert_snapshot.append(dict(expert=row['expert'],formal=row['formal'],
            Adam17=row['Adam17'],nominal_gas_N=row['nominal_gas_N'],policy_Hz=row['policy_Hz'],
            physics_us=row['physics_us'],feedback_Hz=row['feedback_Hz'],
            formal_format_passed=row['formal_format_passed'],
            full_skill_accepted=False,native_SuperMimic_port_admitted=False,
            saved_behavior_review=row['saved_behavior_review']))
    write('EXPERT208_SAVED_NORMALIZATION_AND_REMAINING.json',dict(
        schema='mod4.experts208.selected_normalized_snapshot.v1',epoch=time.time(),
        scope='selected saved400N50 experts from189; no global-latest claim and no E0jump/mainline change',
        source_scope_path=str(T/'FROZEN_EXPERTS_400N50_SKILL_SUPERMIMIC_CONTINUATION_V189_20261031/reports/EXPERT189_SAVED_FORMALS_AND_SKILL_GAPS_ACTUAL.json'),
        experts=expert_snapshot,historical18_is_E0_matrix_not18_actors=True,
        original_acceptance=dict(along_cross='max(.03,.1V)',signed_yaw_rad_s=.2,
            no_90_95_100_percent_aggregate_graduation_line=True),
        actual_W35_old_cycle_scope=dict(rows5039_consumed=True,rereads=0,
            complete_cycle_events=1229,along_event_MAE_m_s=.02172158885234929,
            along_false_events116_preserved=True,old_cross_and_signed_yaw_acceptance='UNKNOWN'),
        selected_WM_component=dict(path=str(T/'EXPERTS_RM70_SUPERMIMIC_READY_QUEUE_V190_20261031/teacher_world_model50_core190_v3.py'),
            SHA='9c240e24f41adb5a6e6724da8dbb027db023ef9e75feb3b92b9260dd63f8562c',
            actual_previous_synthetic_pairs=128,actual_previous_WM_updates=1,
            previous_teacher_and_WM_CPU_not_rerun=True,
            complete_Pi_Critic_conversion=False,RM70_terrain_features_implemented=False),
        remaining_complete_SuperMimic=[
            'Actual own-source full-skill matrices incl D0white_v3 and D1-D7; all false/partial/no-exposure retained',
            'Target actual SDK binding for natural35/38 observations,6 raw actions,30 named joints and cached processed8x6 action targets',
            'Actual own packed127,54 dynamic auxiliary,static31 with original pre-reset endpoint and measured feedback timestamps; transition208 validates but does not invent missing packing',
            'Native50Hz real teacher data at20ms; old100Hz H1 WM and old UID cycle telemetry are not that dataset',
            'W35/RM70/curb/slope WM terrain-relative features from their real3D geometry; selected190 flat core is insufficient',
            'Separate native policy and critic, running norms/optimizers/dedicated RNG and full checkpoints; no renaming PPO tensors',
            'Standalone BC against original clipped6 target then task-specific differentiable reward/BPTT and full WM/Pi/Critic training admission',
            'Deployment-available student feedback/history/commands only; no staticxi or terrain-privilege leak into actor',
            'Own-plant retained full-skill acceptance before replacing any frozen teacher'],
        actual_new_expert_transition_reads=0,actual_new_neural_updates=0,
        full_SuperMimic_conversion=False))
    manifest=read(W/'rmuc2026_training/MANIFEST.sha256.json')
    binaries=[]
    for relative in ('assets/arena_collision.usdc','data/arena_collision.npz'):
        path=W/'rmuc2026_training'/relative
        binaries.append(dict(local_path=str(path),relative=relative,bytes=path.stat().st_size,
            SHA=manifest['files'][relative],SHA_provenance='existing original delivery manifest; no binary open or rehash in208',
            installed_relative='original_field/'+relative))
    audit=read(W/'RM2026_TERRAIN_AUDIT_20261009/GEOMETRY_AUDIT.json')
    write('GEOMETRY208_EXACT_ORIGINAL_FIELD_AND_BOUNDARY.json',dict(
        schema='mod4.rm70_208.original_geometry.v1',binaries=binaries,
        original_source=str(W/'rmuc2026_training/reports/source.json'),
        original_CAD_SHA='8dfe9ebd761e44d91361b3e593bc05416329112217b58cb35800b3cde2ffae33',
        world_axes='CAD XYZ with original mm->m plus original translation only; no flattening/scale/foreign geometry',
        slope_deg=1.5,width_local_tangent_m=2.0845,full_road_span_m=2.4064227271861265,
        peak_to_trough_nominal_m=.07,not_plus_minus70mm=True,
        exact_rough_audit=audit['rough'],
        original_2m_source=dict(path=str(T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_ADAPTED92_NEW86_COMMAND_UID_CYCLE_COMPLETE_CASE_SOURCE_20261030_V2/REFERENCE_EXACT_e1_terrain_runtime.py.txt'),
            function='boundary_timeout',definition_line=32,formula_line=36,registration_line=82,
            formula='(rootXY-spawnXY).abs().max(-1).values > 2.',time_out=True,
            purpose='finite old9x9 rough lesson spatial truncation, separate from physical guards'),
        new_course=dict(route='original rough_forward/reverse: x5.85..9.15,y6.45',
            boundary_x_m=[5.5,9.5],boundary_y_m=[5.405026944202456,7.495880414338017],
            end_margin_m=.35,end_margin_source='original rough route goal radius',
            term_name='rough_route_boundary',time_out=True,
            authorization='[REDACTED]',
            old_W35_course_preserved=True,full_route_pass_not_inferred=True),
        actual208_CAD_binary_reads=0,actual208_CAD_or_SDK_run=False,
        no_new_1um_FP64_bitwise_or_triangle_edge_gate=True))
    write('TARGET208_NEXT_ZERO_PT_AND_TRAINING_PROTOCOL.json',dict(
        schema='mod4.new208.target_queue.v1',status='SOURCE_CPU_CONTRACT_PASS_TARGET_ADMISSION_PENDING',
        root_owns_all_SSH_SDK_GPU_and_Git=True,child_current_remote_lease=False,
        no_hotadd_to_209_or_210=True,
        minimal_next=dict(entry='source/scene0pt208.py',
            command='ACTUAL_SDK_PYTHON -B -X utf8 runtime/isaac/mod4/scene0pt208.py --job-root NEW_UNUSED_JOB',
            source_files=['scene0pt208.py','field208.py','course_math208.py','launcher208.py'],
            binaries=binaries,task_file='SCENE0PT208_TASK.json',
            required_task_fields=dict(kind='NEW208_ORIGINAL_CAD_SCENE_ZERO_PT',num_envs=8,
                max_physics_steps=8,max_wall_seconds=180,model_opens=0,raw_JSONL_opens=0,
                neural_optimizer_updates=0,
                root_actual_exclusive_control_and_GPU_admission='ACTUAL true only after root-owned admission',
                GPU_UUID='actual selected UUID',worker_SHA='actual frozen source SHA'),
            actual_install_receipt='RM70_BINARY_INSTALL_ACTUAL.json: actual_postcopy_fullSHA_verified=true/files(relative,bytes,SHA)',
            expected_NEW_scope='8 translated original arenas,16 original route endpoint rays,8 scene physics steps; no robot/PT/neural calls',
            old_native160k_repeated=False,
            bounds='Parent supplies exclusive GPU/private/shared admission and finite subprocess wait/SDK close; 180s is worker check, App startup still needs parent bound',
            not_enough_for_training='Scene-only result does not prove robot foot contact/fullreset/20k memory/fullstate/native24'),
        full_learning_candidate=dict(entry='source/worker208.py',trainer='source/train208.py',
            source_qualification_kind='MOD4_W35_FULL_RM70_208',role='W35_RM70_FULL208',
            source_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',
            source_bytes=17619013,Adam17=648360,original_RSL_iteration=32336,LR=.00011390625000000003,
            num_envs=20000,no_slice_or_repeat_of_saved_D0_D7_state=True,
            finite_seconds=dict(parent=3900,save=3600,exit_headroom=300),
            original_canonical_generation='MOD4_SINGLE_WRITER72_20261026',
            original_budget_and_strict_reserve_unchanged=True,
            root_original_single_writer_only=True,
            next_admission=['Fresh exact LOCAL CIM and actual72 binding→CLOSE72→target serial lease',
                'Complete source/binary install and actual target SDK API/config source proof without extra model/raw reread',
                'Scene0PT as above, then original full20k state/GPU identity/own storage admission',
                'Original30-joint pose34 footprint/tangent3D reset and400N gas/PD actual readbacks',
                'Original fullactor/critic/STD/norm/17Adam/D0-D7/privatecommand RNG restore then one natural new-course episode',
                'Native24=192physics/48feedback and6motor hardware envelope before first new complete PPO update',
                'Own complete fullstate save, SDK close, parent wait and original terminal accounting'],
            current_admitted=False,scene20k_performance_unmeasured=True),
        frozen_old_W35_missing_skill=dict(entry='source/evaluate_skill208.py',
            task_contract='source/skill_task208.py',kind='MOD4_W35_FULL_WORLD_SKILL208',
            num_envs=20000,requested_controls=1600,warmup_controls=100,
            max_worker_seconds=1680,original_course_and_sampler_unchanged=True,
            actual_same_UID_cross_and_signed_yaw_now_in_new_rows=True,
            episode_and_command_UID_and_original_pre_reset_masks=True,
            no_optimizer_or_norm_updates=True,not_a_complete_WM_dataset=True,
            status='SOURCE_ONLY_TARGET_SDK_AND_ORIGINAL_EARLY_OBSERVER_ADMISSION_PENDING'),
        CURRENT_NO_REMOTE_CALLS=True))
    write('READER208_DIAGNOSTICS_AND_SOURCE_REVIEW.json',dict(
        scope='LOCAL reader/source-preparation history, not robot trial failures',
        diagnostics=[
            dict(kind='workspace filename inventory output truncated',resolution='Narrowed to exact known source/report roots; no conclusion from clipped inventory'),
            dict(kind='wrong source lookup path',path='polar-rl-train/isaac/mod4',resolution='Actual root is polar-rl-train/project/isaac/mod4; selected W35 source is independent frozen runtime'),
            dict(kind='missing handoff filename',path='W35_retention_fixed_next92_source_extension_candidate_v2/HANDOFF.md',resolution='Read actual FINAL_HANDOFF.md'),
            dict(kind='combined old G3 profile/source tool output truncated',resolution='Read named JSON properties and exact source slices; no raw/model read')],
        pre_CPU_unexecuted_source_review_adjustments=[
            'Restored inherited FAMILIES global and explicit no-old-plane retention_radius=None in new arena importer',
            'Replaced old fixed86 launcher path with root-bound NEW208 own-job storage; preserved original cooking settings',
            'Created skill_entry208 as original selected trainer with launcher import only, preserving old W35 field/course',
            'Explicit wxyz codec in NEW route reset; old G3 as_quat source untouched and not relabelled as fixed'],
        first208_CPU_execution_passed=True,CPU_reruns=0,old189_190_tests_rerun=0,
        old5039_raw_stream_reread=0,original_false_and_partial_reports_overwritten=0,
        source_derivation_script_consumed_do_not_rerun=True,
        final_selected_sources_are_frozen_CPU208_source_rows=True,
        all_new_reports_Git='PENDING_ROOT_UNIQUE208_ARCHIVE'))
    text='''# NEW208 frozen source and CPU handoff

LOCAL source package complete; first new CPU purpose passed four groups and seven negative rejections,8env x360synthetic controls/12complete synthetic cycle events. No model, original JSONL,NPZ,USD,SDK,CUDA,SSH,training,account,Goal,automation or Git action ran. Nothing here is actual RM70 admission, full-skill graduation or full SuperMimic conversion.

Use reports/TARGET208_NEXT_ZERO_PT_AND_TRAINING_PROTOCOL.json for the exact next task and callers. Minimal target entry is source/scene0pt208.py: four new source files plus the original collision USD/NPZ,8arena instances/8physics steps/16route endpoint rays,0PT. Parent must provide real source/binary receipt, SDK/GPU/private/shared/control admission, finite subprocess wait and SDK-close proof. Do not manufacture a passed receipt from this source specification. The8arena result is not20k robot admission.

The independent source/worker208.py and source/train208.py fork latest selected W35 ad504fec…df3f/17,619,013B/17Adam648360/RSL32336/LR.00011390625000000003. They retain original20k state without slicing,35/38 observations,6actions,400N/k2000/50Hz/100Hz/400Hz/TGS32/4 and original fullstate/physical health/save behavior. Every environment contains an instance of the original complete collision CAD; no35mm scaling or sine replacement. Source geometry is the supplied original CAD's70mm normal peak-to-trough with1.5deg slope,2.406422727m span and2.0845m local width. New full original route spatial boundary covers x5.5..9.5,y5.405026944..7.495880414; old2m course remains in frozen W35. Original closure2mm,mimic.01,bad_orientation/base_contact/low_base thresholds and original time_out stay unchanged. New course uses original rough BODY vx[-.3,.3],standing.2,vy=yaw0 and12..16s resampling. It does not silently run old plane world-yaw commands on rough CAD.

Actual target SDK source/API,scene0PT,20k arena/robot memory/fullpose/command/D0-D7/fullrestore/native24 admission remain. Root owns sole72 scheduling and all3900/save3600/exit300 accounting. No hotadd to healthy209/210. The full20k arena layout performance is unmeasured. Fullfootprint route reset has an explicit SDK wxyz quaternion codec for this new scope; old G3 reset bytes remain unchanged and no old behavior result is rewritten.

The separate source/evaluate_skill208.py and source/skill_entry208.py retain original frozen W35 geometry/commands/2m boundary while source/skill_cycle208.py adds same-cycle cross displacement,actual signed yaw and command integral,error,original episode/command UID and pre-reset terminal reasons. Requested1600controls is a NEW missing-field measurement,not a replay of the consumed5039JSONL or an old800once. It preserves the original sampled>=2pi endpoint/overshoot semantics and original along/cross max(.03,.1V),signed yaw.2 criteria. Individual false,terminal,partial and unexposed profiles remain. No new aggregate pass rate exists.

Source/transition208.py only validates natural127+54+31+6/8processedtargets/2feedback data. Actual SDK packing is still missing; no fields are invented. Selected190 WMv3 remains flat-only with128synthetic pairs/one previous WM update,0Pi/Critic conversion. See reports/EXPERT208_SAVED_NORMALIZATION_AND_REMAINING.json for selected E0/W35/E2/E3 metadata and concrete remaining complete-SuperMimic steps. E2/E3 are not whole-skill graduates;18gates are not18actors.

All source/report/reader diagnostics are pending root's unique208 Git phase using record_experiment.py and remote main/tag/peeled verification. No local-only file is called Git-recorded. Do not rerun consumed preparation or CPU once for stats/Git. Final INDEX208_FROZEN.json records every existing file's bytes/SHA except itself and final handoff response; original large artifacts are metadata-only.
'''
    with (HERE/'HANDOFF208.md').open('x',encoding='utf8') as f:f.write(text)
    rows=[digest(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
    with (HERE/'INDEX208_FROZEN.json').open('x',encoding='utf8') as f:json.dump(dict(
        schema='mod4.new208.complete_local_frozen_index.v1',epoch=time.time(),
        status='SOURCE_CPU_CONTRACT_PASS_TARGET_PENDING',files=rows,
        selected_source_rows=purpose['source_rows'],
        minimal_next_entry='source/scene0pt208.py',
        original_model_raw_NPZ_USD_SDK_remote_calls=0,
        CPU_once_passed=cpu,root_Git_status='PENDING_UNIQUE208_RECORD_AND_REMOTE_VERIFY',
        self_excluded_to_avoid_self_referential_hash=True),f,indent=2,ensure_ascii=False)
    print(json.dumps(dict(index=digest(HERE/'INDEX208_FROZEN.json'),files=len(rows),status='SOURCE_CPU_CONTRACT_PASS_TARGET_PENDING')))


if __name__=='__main__':main()

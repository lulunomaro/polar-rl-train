"""Persist CPU evidence boundaries and human video clarification; no GPU/network."""
from pathlib import Path
import hashlib
import json
import time

D=Path(__file__).resolve().parent
W=D.parent
R=D/'reports'
M=W/'MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015'


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def save(p,value):
    with Path(p).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)


proof=R/'NOMINAL_ISOLATED_GUARDS_METADATA_D0_D7_NEGATIVES_CPU_ACTUAL.json'
review=json.loads(proof.read_bytes())
assert review['passed'] and not review['target_CPU_native_or_GPU_admission']
video=Path('C:/Users/lulu/Downloads/42168288822-1-192.mp4')
assert video.stat().st_size==11455996
video_report=R/'HUMAN_VIDEO_AIRBORNE_STEP_HOP_SCOPE_CLARIFICATION_ACTUAL.json'
save(video_report,dict(epoch=time.time(),original_video=dict(path=str(video),bytes=video.stat().st_size,sha256=sha(video),original_retained=True),
    previous_actual_decoded_metadata=dict(frames=2020,fps=30.00000928218109,duration_s=67.3333125),
    visual_evidence='Overview and timestamped sequences were actually inspected in this chat. About42.05-42.65s and50.0-50.75s show approach/body lowering, extension, full aerial phase over the edge, then wheel landing and leg compression.',
    observed_motion_phases=['rolling approach and body lowering','leg extension and liftoff','forward/upward airborne edge clearance','wheel landing, leg compression and balance recovery'],
    not_observable_from_this_video=['joint torque and controller internals','spring energy contribution','exact platform height, target range or motor limits','contact force time series or hidden wheel contact'],
    target_scope='Reference is airborne wheel-leg step hopping. Previous12-24h estimate for low-step admission cannot be reused as its start date.',
    human_request_was_video_understanding_not_new_training_or_S8_approval=True,
    no_RL_checkpoint_protocol_budget_or_GPU_action=True))
work=D/'NEXT_NOMINAL_SOURCE_CPU_PASSED_TARGET_NATIVE_ADMISSION_AND_STEP_HOP_SCOPE_WORK_ORDER.json'
save(work,dict(epoch=time.time(),stage='S5 nominal absent-MildDR isolated audit compatibility CPU candidate',
    CPU_review=dict(path=str(proof),sha256=sha(proof),source_inverse_AST_exact_files=7,
                   actual_tensor_audit_fixtures_N80_N88_seeds02_03=4,strict_negative_cases=60,
                   whitev2_v3_metadata_RNG_three_hook_results_original_exact=True,
                   spring_constructor_parent_is_explicit_fixture=True,
                   full_SDK_constructor_GPU_setter_readback_not_tested=True),
    changes=['Guard only absent-MildDR audit registration in four original adapter candidates.',
             'Retain original gas-to-spring damping overlay, including reference restoration.',
             'Capture actual D0 read-only reference once; assert exact unchanged mass/inertia/materials and unity actual motor scales.',
             'Retain original separate D5/D6/D7 spring, damping, chassis COM and explicit PD audit methods.',
             'Absent MildDR metadata fields are null and its RNG keys absent, never synthesized.',
             'Legacy nominal uniform-COM rejection stays reproducible and saved; D7 pressure is audited per original tensor/frame contract.'],
    reader_failure=dict(V1='NOMINAL_CPU_REVIEW_ORIGINAL_ERROR_* preserved: extracted legacy audit missed os in CPU-reader globals, not a runtime or physical failure.',
                        V2='Only supplied os to extracted-function globals. All candidate bytes and original runtime stayed unchanged.'),
    no_original_shared_or_installed_source_modified=True,
    target_CPU_or_native_or_GPU_admitted=False,nominal_GPU_dispatched=False,
    next_actual_steps=['Materialize a new complete isolated namespace/package with explicit seven-file overlay plus own helper, not installed SDK edits.',
                       'Freeze all actual original runtime/assets, candidate source, model bytes and SDK binding; CPU import/manifest and target resource/OS-lock checks.',
                       'Retain V8 physical mainloops, query1e-6, contact integration, COM/hardware, same35/cache/reset/whole6 and A/B/C source identities.',
                       'Own unused nominal native120 must physically complete and independently pass actual source/parameter/audit/readback before any frozen full1500 credit.',
                       'Only actual source/backend/profile/seed/kind admission permits same-pair reuse. No old white_v2/v3 native/Task/once replay.',
                       'New bounded finite evaluation owner only after actual resources/leases and own source checks; no duplicate transport owner.'],
    video_clarification=dict(path=str(video_report),sha256=sha(video_report),previous_low_step_ETA_not_applicable=True,
                             no_airborne_jump_start_date_or_new_training_approval=True),
    current_GPU_and_learning='No new GPU job or PPO launched by this stage. Existing firstgate148 remains final, no automatic second window.',
    cost='CPU0PPO; solecanonical1188000s/sevenextensions unchanged. No copy/clear/refund/tail/recharge/new budget.',
    Git=dict(real_new_CPU_stage_requires_unique_future_record_experiment=True,
             reserved_id_not_yet_recorded='s5-nominal-absent-mild-audit-source-cpu',
             status='PENDING. First recover/verify existing e411 ordinary objects; no new record/tag/commit was made while that existing push remained unknown.',
             old_failure_reports_and_new_source_and_video_index_must_all_be_captured=True,
             old_stage_M_later_errors_still_need_ordinary_supplement=True),
    actual_followups_not_prepared_as_future_pass=True))
paths=sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
save(R/'NOMINAL_CPU_STAGE_ALL_SAVED_FILES_PENDING_GIT_INDEX_ACTUAL.json',dict(epoch=time.time(),
    entries=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),pending_Git=True) for p in paths],
    this_index_itself_and_later_workorders_monitor_receipts_also_require_archive=True,
    local_files_not_claimed_Git_recorded=True,existing_M_commit_to_recover='e411cb07f275b287f3644a69c4159737a3b0edc3'))
print(json.dumps(dict(CPU_passed=True,workorder=str(work),video_scope_recorded=True,Git_pending=True,new_GPU=False)))

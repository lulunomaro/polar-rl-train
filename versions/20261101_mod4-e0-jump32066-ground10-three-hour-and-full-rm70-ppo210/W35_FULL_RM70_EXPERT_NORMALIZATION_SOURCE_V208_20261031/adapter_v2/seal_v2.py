"""Append source-only robot admission handoff; frozen208 remains unchanged."""
from pathlib import Path
import hashlib, json, time

HERE=Path(__file__).resolve().parent; PACKAGE=HERE.parent


def row(path):
    raw=path.read_bytes()
    return dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())


def main():
    original=row(PACKAGE/'INDEX208_FROZEN.json')
    assert original['SHA']=='e4f5df8fbee2cf1c232e65dbf2068f0f72556aa075b47104ca1c49195bda920a'
    entry=row(HERE/'robot0pt208_v2.py')
    report=dict(schema='mod4.208.own_robot_zeroPT.source_addendum.v2',epoch=time.time(),
        status='SOURCE_ONLY_UNUSED_NO_ADDITIONAL_CPU_TEST_OR_SDK',
        frozen_original_index=original,entry=entry,
        install_entry_relative='runtime/isaac/mod4/robot0pt208_v2.py',
        existing_frozen_sources_required=[
            'course_math208.py','field208.py','launcher208.py','reset208.py','config208.py',
            'terrain208.py','command208.py','base_learning208.py','evidence208.py','learning208.py'],
        selected_base_runtime='reports/INSTALL208_SOURCE_INPUTS.json base_rows; use original source/binary install metadata, never substitute E0 flat74 reset bank',
        original_run_manifest_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb',
        binary_inputs=['original source_700N/robot.usd + small400N composition layer and import_contract',
            'original MOD4_RESET_COLLISION_BANK.npz (pose34 nearest250 selected by original code)',
            'original_field/assets/arena_collision.usdc','original_field/data/arena_collision.npz'],
        no_model_file_needed=True,no_saved_model_or_raw_read_permitted_by_this_source=True,
        no_PT_serializer_or_loader_calls_in_adapter=True,
        task_file='ROBOT0PT208_V2_TASK.json',
        task_fields=dict(kind='NEW208_FULL_RM70_OWN_MOD4_ROBOT_ZERO_PT_V2',num_envs=80,controls=8,
            physics_callbacks=64,feedback_samples=16,model_opens=0,actor_calls=0,optimizer_updates=0,
            max_worker_seconds=600,original_manifest_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb',
            actual_parent_exclusive_control_GPU_private_shared_admission='ACTUAL root true only',
            GPU_UUID='actual selected UUID',worker_SHA=entry['SHA']),
        command='ACTUAL_SDK_PYTHON -B -X utf8 runtime/isaac/mod4/robot0pt208_v2.py --job-root NEW_UNUSED_JOB',
        exact_runtime_scope=['Original MOD4 own30-joint robot,nearest250 pose34/full footprint/tangent3D physical reset on originalCAD',
            'Original400N nominal/k2000 composition and original DR/PD/torque-speed/hardware terms',
            'Fresh80 D0-D7 initialization only,not sliced/resumed20k DR population',
            'Original rough-only actual stand/.3command domain,35obs38critic6actions',
            'Eight zero six-dimensional ingress commands,no policy or critic or optimizer',
            '64actual physics callbacks +64leg/64wheel queue calls +16actual feedback timestamps',
            'Eight original RewardManager dt.02 calls,all original termination reason masks/pre-reset root13/q30',
            'Original health observer and learning_health_pass rule;2mm ordinary per-env reset not a new global gate'],
        proof_does_not_cover=['Actual PPO full20k source decode/actor/critic/STD/optimizer restore',
            'Actual20k wholearena+robot memory/throughput','Production native24 after original fullstate restore',
            'RM70 crossing skill/full-world W35 retained skills','Native WM/Pi/Critic conversion'],
        parent_must_supply='Exclusive actual target lease/private/shared/source+binary receipts and finite supervisor/wait/SDK close;600s worker check is not an AppLauncher startup timeout',
        root_can_dispatch_before_static_cohort_only_after_actual_target_proof=True,
        no_hotadd_to_healthy209_or210=True,
        no_local_execution=True,no_remote_execution_by_child=True,
        Git_status='PENDING_ROOT_UNIQUE208_ARCHIVE_WITH_V2_ADDENDUM')
    with (HERE/'ROBOT0PT208_V2_SOURCE_HANDOFF.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    with (HERE/'INDEX208_ROBOT_V2.json').open('x',encoding='utf8') as f:json.dump(dict(
        schema='mod4.208.robot_source_addendum_index.v2',files=[row(p) for p in sorted(HERE.glob('*')) if p.is_file()],
        original_frozen_index=original,all_original_source_and_CPU_bytes_unchanged=True,
        no_model_raw_SDK_GPU_local_test_or_remote_actions=True),f,indent=2)
    print(json.dumps(dict(index=row(HERE/'INDEX208_ROBOT_V2.json'),entry=entry)))


if __name__=='__main__':main()

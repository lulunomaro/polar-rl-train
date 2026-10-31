"""Write NEW218 source contracts/purpose freeze; only local .py/.json metadata."""
from pathlib import Path
import hashlib
import json
import time
from contract218 import (KIND, WORKER_KIND, SHA, SOURCE_BYTES, ITER, ADAM, LR,
                         GENERATION, OLD_CPU_SHA, WORKER214_SHA)

B = Path(__file__).resolve().parent.parent
T = B.parent
P208 = T / 'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031'
P214 = T / 'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101'
OV = T / 'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
ROOT217 = T / 'W35_SHARED_MATERIAL_20K_ORIGINAL_PHYSX_ADMISSION_V217_20261101/reports/ROOT217_ORIGINAL_20K_SHARED_MATERIAL_NATIVE_OR_ERROR_RETURNED_ACTUAL.json'


def ref(path):
    path = Path(path)
    assert path.suffix in ('.py', '.json', '.md', '.txt'), 'Source/metadata only'
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), SHA=hashlib.sha256(data).hexdigest())


def put(name, value):
    with (B / 'reports' / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    (B / 'reports').mkdir(exist_ok=True)
    runtime = 'runtime/isaac/mod4/'
    overlays = []
    def add(path, installed):
        overlays.append(dict(**ref(path), installed_relative=installed))
    for name in ['action_delay_checkpoint208_v3.py', 'base_learning208_v3.py',
        'chassis_pd_checkpoint208_v3.py', 'checkpoint_cache208_v3.py', 'command208_v3.py',
        'evidence208_v3.py', 'feedback_delay_checkpoint208_v3.py', 'gas_damping_checkpoint208_v3.py',
        'learning208_v3.py', 'reset208_v3.py', 'sensor_resume_contract208_v3.py',
        'source_cache208_v3.py', 'spring_pressure_checkpoint208_v3.py', 'terrain208_v3.py']:
        add(P208 / 'adapter_v3' / name, runtime + name)
    for name in ['course_math208.py', 'field208.py', 'launcher208.py']:
        add(P208 / 'source' / name, runtime + name)
    for name in ['config214_training.py', 'train_full214.py', 'field214.py', 'usd214.py', 'material214.py']:
        add(P214 / 'source' / name, runtime + name)
    add(P214 / 'source/worker_full214.py', 'worker_full214.py')
    for name in ['contract218.py', 'worker_full218.py']:
        add(B / 'source' / name, name)
    assert next(r['SHA'] for r in overlays if r['installed_relative'] == 'worker_full214.py') == WORKER214_SHA
    base = P208 / 'reports/INSTALL208_SOURCE_INPUTS.json'
    base_meta = json.loads(base.read_bytes())
    original_mild = OV / 'W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/mild_dr.py'
    put('INSTALL218_FROZEN_SOURCE_BINDINGS.json', dict(schema='mod4.218.install_bindings.v1',
        status='SOURCE_ONLY_NOT_INSTALLED_NOT_GO', base_install_metadata=ref(base),
        base_rows_reused_by_reference=len(base_meta['base_rows']),
        rule='Install all frozen base_rows then these exact overlay destinations in a NEW unused job; never patch210 or oldW35',
        overlay=overlays, original_production_mild_DR=ref(original_mild),
        probe_only_not_on_production_path=['mild_dr214.py','restore214.py','config214.py','material0pt214.py'],
        original_run_manifest=base_meta['original_full_manifest_path'],
        source_model_metadata=dict(SHA=SHA, bytes=SOURCE_BYTES, iteration=ITER, Adam=ADAM, LR=LR,
            installed_relative='source/W35_ADAPTED92_FINAL78.pt',
            original_target_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_RETENTION_2610v92/w35/adaptation/final_valid_update78.pt'),
        node_manifest_rule='files may contain required source/assets installation entries but must exclude every .pt; selected input is input_model_metadata only',
        child_model_USD_NPZ_reads=0))
    material = json.loads(ROOT217.read_bytes())
    n = material['native_result']
    put('ACTUAL217_SELECTED_READBACK_AND_SOURCE_SCOPE.json', dict(schema='mod4.218.actual217_selected_readback.v1',
        report=ref(ROOT217), passed=material['passed'], returncode=material['returncode'],
        all_own_children_waited=material['all_own_children_waited'],
        private_EX_released=material['private_EX_released'],
        actual_material_limit_error_count=material['actual_material_limit_error_count'],
        phase_evidence_complete=material['phase_evidence_complete'],
        missing_required_phases=material['missing_required_phases'],
        actual_original_shared_CAD_material_checks=material['actual_original_shared_CAD_material_checks'],
        native_selected={k:n[k] for k in ['kind','passed','num_envs','controls','physics_callbacks',
            'feedback_samples','processed_queue_calls_per_group','model_opens','actor_calls',
            'optimizer_updates','own20k_restore','material_setter_counts',
            'actual_D0_D7_own20k_restore_then_new_episode_native_integration',
            'source_physical_guards_unchanged','actual_PPO_fullstate_restore',
            'actual_native24_before_production_learning_still_required','full_RM70_skill',
            'complete_SuperMimic_conversion']},
        PhysX_handle_count='UNKNOWN_NOT_STAGE_PRIM_COUNT',
        source_of_material_values='Original CAD /Asset/physics_material; static.9 dynamic.8 restitution0, actual217 nine checks true; no invented coefficient',
        no_full_UTF8_log_or_trajectory_read_or_reproduction=True,
        training_still_blocked_by_E0_210_active_and_missing_future_new_formal_CPU_fresh_CNone=True))
    task = dict(status='TEMPLATE_UNBOUND_NOT_AN_ACTIVE_TASK', kind=WORKER_KIND,
        launch_contract_kind=KIND, run_id=None, role_key='w35_72', num_envs=20000,
        source_SHA=SHA, source_bytes=SOURCE_BYTES, source_iteration=ITER,
        source_Adam_step=ADAM, source_LR=LR, original_canonical_generation=GENERATION,
        worker_SHA=WORKER214_SHA, entrypoint_SHA=ref(B / 'source/worker_full218.py')['SHA'],
        original_saved_W35_fullstate_CPU_proof_SHA=OLD_CPU_SHA,
        original_saved_W35_fullstate_CPU_proof_reused=True,
        actual_scene0PT211_passed=True, actual_robot0PT212_passed=True,
        new_RM70_geometry_course_and_xyzw_source_reviewed=True,
        actual_shared_material20k0PT_passed=material['passed'],
        actual_material_limit_error_count=material['actual_material_limit_error_count'],
        source_read_purpose=dict(physical_byte_opens=1, decodes=1, source_bytes=SOURCE_BYTES),
        GPU_UUID=None, actual_private_EX_held_by_parent=False,
        launch_evidence_SHA=None, manifest_file='PACKAGE218_MANIFEST.json')
    put('TASK218_TEMPLATE_NOT_ACTIVE.json', task)
    put('PRELAUNCH218_EVIDENCE_TEMPLATE_NOT_ACTIVE.json', dict(schema='mod4.218.closed_actual_selectors.v1',
        status='PENDING_E0_NORMAL_CLOSED_NEW_FORMAL_CPU_AND_FRESH_CNone',
        reports=dict(ROOT217=dict(**ref(ROOT217), relative='closed_evidence/ROOT217_ORIGINAL_20K_SHARED_MATERIAL_NATIVE_OR_ERROR_RETURNED_ACTUAL.json', complete=True)),
        facts={}, root_must_fill='Each canonical gate key in contract218.validate_closed_facts uses {report,pointer}; stage only complete saved JSON under job, hash exact bytes. No active partial or fabricated CNone.',
        E0_final_artifact='Future actual SHA/iteration/17Adam only for closing prior210; never replace W35 training input with it'))
    put('READY218_TEMPLATE_NOT_ACTIVE.json', dict(passed=False, kind=KIND, manifest_SHA=None,
        source_SHA=SHA, source_iteration=ITER, Adam_step=ADAM, source_fullstate_CPU_passed=True,
        source_saved_fullstate_CPU_SHA=OLD_CPU_SHA,
        all_actor_critic_optimizer_tensors_finite=True, actual_35_38_6_shapes=True,
        launch_evidence_SHA=None, actual_shared_material20k0PT_passed=material['passed'],
        actual_material_limit_error_count=0, actual_target0PT_waited_RC=0,
        actual_target0PT_controls=8, actual_target0PT_physics=64, actual_target0PT_feedback=16,
        actual_target0PT_num_envs=20000, target0PT_private_EX_released=True,
        E0_210_closed_new_formal_CPU_and_fresh_CNone=False,
        status='SOURCE_TEMPLATE_OLD_W35_CPU_REUSED_NOT_A_NEW_MODEL_CPU_OR_ACTUAL_TRAINING_READY'))
    put('SCHEDULE218_TEMPLATE_NOT_ACTIVE.json', dict(status='TEMPLATE_NOT_AN_ACTIVE_SCHEDULE',
        run_id=None, scheduling_authority='human_requested_available_experts', deferred_experts=[],
        experts=dict(w35_72=dict(key='w35_72', execution_backend='target72', GPU_UUID=None,
            source_SHA=SHA, source_iteration=ITER, source_Adamstep=ADAM, source_kind=KIND,
            max_parent_seconds=3900, exit_headroom_seconds=300, num_envs=20000,
            no_physics_change=True, manifest_SHA=None, launch_evidence_SHA=None,
            prelaunch_control_snapshot_id=None, manifest_file='PACKAGE218_MANIFEST.json',
            worker_script='worker_full218.py', job_root=None, private_lock=None, python=None))))
    cpu_sources = [B / 'source' / name for name in ['contract218.py','worker_full218.py',
                   'solo218_protocol.py','check218_metadata_once.py']]
    cpu_sources += [P214 / 'source' / name for name in ['worker_full214.py','train_full214.py',
                    'config214_training.py','field214.py','usd214.py','material214.py']]
    cpu_sources += [P208 / 'adapter_v3' / name for name in ['source_cache208_v3.py',
                    'checkpoint_cache208_v3.py','reset208_v3.py']]
    put('CPU218_PURPOSE_FROZEN.json', dict(purpose_id='NEW218_SHARED214_NEXT_SOLO_TASK_READY_GO_METADATA_CPU_V1',
        frozen_epoch=time.time(), execution='ONCE_NEW_SOURCE_METADATA_PURPOSE_ONLY',
        groups=3, expected_rejections=17, model_raw_NPZ_USD_SDK_GPU_remote_reads=0,
        old208_213_214_fixture_replays=0, source_files=[ref(p) for p in cpu_sources],
        acceptance='Exact source/AST pins; synthetic Task/manifest/Ready/GO positive join;17 before-GO refusal cases. No hardware/training proof.'))
    print(json.dumps(dict(source_contracts_frozen=True, overlay_rows=len(overlays),
        CPU_purpose_frozen=True, actual217_selected_pass=material['passed'],
        training_ready=False, forbidden_reads=0)))


if __name__ == '__main__':
    main()

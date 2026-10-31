"""NEW218 one frozen source/Task/Ready/GO metadata purpose. No SDK/Torch."""
from pathlib import Path
import ast
import copy
import json
import sys
import time
from contract218 import (KIND, WORKER_KIND, SHA, SOURCE_BYTES, ITER, ADAM, LR,
    GENERATION, CANONICAL, OLD_CPU_SHA, WORKER214_SHA, h_bytes, owner_ready_sha,
    validate_closed_facts, validate_task, validate_manifest, validate_job_before_delegate)
import solo218_protocol as protocol

B = Path(__file__).resolve().parent.parent
R = B / 'reports'
PURPOSE = 'NEW218_SHARED214_NEXT_SOLO_TASK_READY_GO_METADATA_CPU_V1'


def dump(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    frozen = json.loads((R / 'CPU218_PURPOSE_FROZEN.json').read_bytes())
    assert frozen['purpose_id'] == PURPOSE and frozen['groups'] == 3
    assert frozen['expected_rejections'] == 17
    assert not (R / 'CPU218_ONCE_CONSUMED.json').exists()
    dump(R / 'CPU218_ONCE_CONSUMED.json', dict(purpose_id=PURPOSE, epoch=time.time(),
         status='STARTED_ONCE_REENTRY_FORBIDDEN', model_raw_NPZ_USD_SDK_GPU_remote_reads=0))
    groups = []
    for row in frozen['source_files']:
        raw = Path(row['path']).read_bytes()
        assert len(raw) == row['bytes'] and h_bytes(raw) == row['SHA']
        if row['path'].endswith('.py'):
            ast.parse(raw.decode('utf8'), filename=row['path'])
    groups.append(dict(group='new_metadata_caller_exact_source_freeze_and_AST', passed=True,
                       source_rows=len(frozen['source_files']), imported_SDK_Torch=False))
    f = dict(material217_passed=True, material217_num_envs=20000,
        material217_controls=8, material217_physics=64, material217_feedback=16,
        material217_model_opens=0, material217_actor_calls=0, material217_optimizer_updates=0,
        material217_own_restore_new_episode_and_setter_phases_complete=True,
        material217_owned_stdout_scan_complete=True, material217_limit64K_errors=0,
        material217_waited_RC=0, material217_App_closed=True,
        material217_all_own_children_waited_out=True,
        material217_private_EX_released_and_actual_FREE=True, material217_closed_epoch=100,
        E0_210_complete_final_saved=True, E0_210_App_closed=True,
        E0_210_worker_and_all_own_children_waited_out=True, E0_210_waited_RC=0,
        E0_210_original_owner_closed_and_cost_settled=True, E0_210_closed_epoch=110,
        E0_210_final_SHA='f'*64, E0_210_actual_new_PPO_updates=2,
        E0_210_final_iteration=32068, E0_210_final_Adam_step=642880,
        E0_new_formal_CPU_passed=True, E0_new_formal_CPU_whole_finite_35_38_6_STD_17Adam_DR=True,
        E0_new_formal_CPU_model_SHA='f'*64, E0_new_formal_CPU_iteration=32068,
        E0_new_formal_CPU_Adam_step=642880, E0_new_formal_CPU_finished_epoch=120,
        canonical_generation=GENERATION, canonical_path=CANONICAL, canonical_active=None,
        canonical_total_authorized_seconds=2268000, fresh_CNone_checked_epoch=130,
        fresh_LOCAL_exact_CIM_passed=True, fresh_LOCAL_exact_CIM_checked_epoch=129,
        fresh_control_snapshot_id='SYNTHETIC_ONLY_NOT_ACTUAL_CONTROL',
        no_new_writer_grant_copy_refund_or_210_hotadd=True)
    j = R / 'SYNTHETIC_METADATA_ONLY_FIXTURE218'
    j.mkdir(exist_ok=False)
    closed = dict(synthetic_fixture_only=True, actual_hardware_result=False, facts=f)
    dump(j / 'SYNTHETIC_CLOSED_FACTS.json', closed)
    raw = (j / 'SYNTHETIC_CLOSED_FACTS.json').read_bytes()
    evidence = dict(schema='mod4.218.closed_actual_selectors.v1', status='CLOSED_ACTUAL_ONLY',
        synthetic_fixture_only=True,
        reports=dict(closed=dict(relative='SYNTHETIC_CLOSED_FACTS.json', bytes=len(raw),
                                SHA=h_bytes(raw), complete=True)),
        facts={name:dict(report='closed', pointer='/facts/'+name) for name in f})
    dump(j / 'PRELAUNCH218_CLOSED_EVIDENCE.json', evidence)
    evidence_sha = h_bytes((j / 'PRELAUNCH218_CLOSED_EVIDENCE.json').read_bytes())
    task = dict(kind=WORKER_KIND, launch_contract_kind=KIND, role_key='w35_72',
        run_id='SYNTHETIC218_NOT_A_TRAINING_RUN', num_envs=20000, source_SHA=SHA,
        source_bytes=SOURCE_BYTES, source_iteration=ITER, source_Adam_step=ADAM, source_LR=LR,
        original_canonical_generation=GENERATION, worker_SHA=WORKER214_SHA,
        original_saved_W35_fullstate_CPU_proof_SHA=OLD_CPU_SHA,
        original_saved_W35_fullstate_CPU_proof_reused=True,
        actual_scene0PT211_passed=True, actual_robot0PT212_passed=True,
        new_RM70_geometry_course_and_xyzw_source_reviewed=True,
        actual_shared_material20k0PT_passed=True, actual_material_limit_error_count=0,
        source_read_purpose=dict(physical_byte_opens=1, decodes=1, source_bytes=SOURCE_BYTES),
        GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',
        launch_evidence_SHA=evidence_sha, manifest_file='PACKAGE218_MANIFEST.json')
    dump(j / 'TASK.json', task)
    task_bytes = (j / 'TASK.json').read_bytes()
    manifest = dict(files=[dict(relative='TASK.json', bytes=len(task_bytes), SHA=h_bytes(task_bytes))],
                    input_model_metadata=dict(SHA=SHA, bytes=SOURCE_BYTES))
    dump(j / 'PACKAGE218_MANIFEST.json', manifest)
    manifest_sha = h_bytes((j / 'PACKAGE218_MANIFEST.json').read_bytes())
    ready = dict(passed=True, kind=KIND, manifest_SHA=manifest_sha, source_SHA=SHA,
        source_iteration=ITER, Adam_step=ADAM, source_fullstate_CPU_passed=True,
        source_saved_fullstate_CPU_SHA=OLD_CPU_SHA,
        all_actor_critic_optimizer_tensors_finite=True, actual_35_38_6_shapes=True,
        launch_evidence_SHA=evidence_sha, actual_shared_material20k0PT_passed=True,
        actual_material_limit_error_count=0, actual_target0PT_waited_RC=0,
        actual_target0PT_controls=8, actual_target0PT_physics=64, actual_target0PT_feedback=16,
        actual_target0PT_num_envs=20000, target0PT_private_EX_released=True,
        E0_210_closed_new_formal_CPU_and_fresh_CNone=True)
    dump(j / 'ADMISSION218_READY.json', ready)
    spec = dict(key='w35_72', execution_backend='target72', GPU_UUID=task['GPU_UUID'],
        num_envs=20000, source_SHA=SHA, source_iteration=ITER, source_Adamstep=ADAM,
        source_kind=KIND, max_parent_seconds=3900, exit_headroom_seconds=300,
        no_physics_change=True, prelaunch_control_snapshot_id=f['fresh_control_snapshot_id'],
        manifest_SHA=manifest_sha, launch_evidence_SHA=evidence_sha)
    cfg = dict(experts=dict(w35_72=spec), deferred_experts=[])
    assert protocol.validate_schedule(cfg)
    row = dict(key='w35_72', phase='ready', manifest_SHA=manifest_sha, original_error=False,
        closed_source_CPU=dict(value=ready, SHA=owner_ready_sha(ready), actual_CPU_waited_EXIT0=True))
    assert protocol.valid_ready(row, spec)
    go = dict(protocol.flat_go_fields(spec), manifest_SHA=manifest_sha,
              source_CPU_SHA=owner_ready_sha(ready))
    assert validate_job_before_delegate(j, go, task, synthetic_fixture=True)['passed']
    groups.append(dict(group='synthetic_closed_evidence_Task_manifest_Ready_original_owner_GO_join',
                       passed=True, positive_joins=1, hardware_admission_claim=False,
                       manifest_contains_Task_but_Task_does_not_contain_Ready_SHA=True))
    rejections = []
    def rejected(name, call):
        try:
            call()
        except (ValueError, AssertionError, KeyError):
            rejections.append(dict(case=name, rejected=True));return
        raise AssertionError('Expected rejection: '+name)
    for name, key, value in [
        ('217_not_passed','material217_passed',False),
        ('80env_not20k','material217_num_envs',80),
        ('64K_error_even_RC0','material217_limit64K_errors',1),
        ('native8_without_restore_phases','material217_own_restore_new_episode_and_setter_phases_complete',False),
        ('217_child_not_waited_out','material217_all_own_children_waited_out',False),
        ('217_EX_not_FREE','material217_private_EX_released_and_actual_FREE',False),
        ('210_owner_still_active','E0_210_original_owner_closed_and_cost_settled',False),
        ('E0_CPU_different_artifact','E0_new_formal_CPU_model_SHA','e'*64),
        ('old_E0_CPU_iteration','E0_new_formal_CPU_iteration',32066),
        ('canonical_active_not_None','canonical_active',dict(owner=210)),
        ('CNone_predates_newCPU','fresh_CNone_checked_epoch',115),
    ]:
        changed = copy.deepcopy(f);changed[key] = value
        rejected(name, lambda changed=changed:validate_closed_facts(changed))
    changed = copy.deepcopy(task);changed['source_SHA'] = 'e'*64
    rejected('E0_not_W35_input', lambda:validate_task(changed))
    changed_cycle = copy.deepcopy(task);changed_cycle['source_CPU_SHA'] = owner_ready_sha(ready)
    rejected('Task_cannot_embed_Ready_SHA_cycle', lambda:validate_task(changed_cycle))
    changed_cfg = copy.deepcopy(cfg);changed_cfg['experts']['e0_72'] = dict(spec)
    rejected('no_second_or_pending_role', lambda:protocol.validate_schedule(changed_cfg))
    changed_go = copy.deepcopy(go);changed_go['source_CPU_SHA'] = OLD_CPU_SHA
    rejected('old_CPU_SHA_is_not_owner_Ready_SHA', lambda:validate_job_before_delegate(j, changed_go, task, synthetic_fixture=True))
    rejected('synthetic_proof_cannot_qualify_production', lambda:validate_job_before_delegate(j, go, task))
    changed_manifest = copy.deepcopy(manifest)
    changed_manifest['files'].append(dict(relative='source/W35_ADAPTED92_FINAL78.pt', bytes=SOURCE_BYTES, SHA=SHA))
    rejected('PT_not_in_node_hash_loop', lambda:validate_manifest(changed_manifest))
    assert len(rejections) == frozen['expected_rejections']
    groups.append(dict(group='before_GO_refusals_for_real_remaining_blockers', passed=True,
                       rejections=rejections))
    dump(R / 'CPU218_ACTUAL.json', dict(purpose_id=PURPOSE, epoch=time.time(), passed=True,
        groups=groups, group_count=len(groups), rejected_cases=len(rejections),
        synthetic_metadata_fixture_only=True, actual217_claim=False, actual_E0_closed_claim=False,
        actual_GPU_or_training_ready=False, source_model_reads=0, raw_reads=0, NPZ_USD_reads=0,
        SDK_GPU_remote_calls=0, old_fixture_replays=0,
        no_physical_material_capacity_or_full_PPO_restore_proved_by_this_CPU=True))
    print(json.dumps(dict(purpose_id=PURPOSE, passed=True, groups=3, rejections=len(rejections),
                          model_raw_NPZ_USD_SDK_GPU_remote=0)))


if __name__ == '__main__':
    main()

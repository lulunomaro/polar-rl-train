"""New synthetic JSON/AST ABI only. No actual Task/GO/owner is generated."""
from pathlib import Path
from copy import deepcopy
import ast
import hashlib
import json
import time
import traceback

N = Path(__file__).resolve().parent
R = N / 'reports'
purpose = json.loads((R / 'FROZEN275_NEW_WM_ONLY_METADATA_INTERFACE_CPU_PURPOSE.json').read_bytes())
with (R / 'CONSUMED275_NEW_WM_ONLY_METADATA_INTERFACE_CPU_ONCE.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), purpose_ID=purpose['purpose_ID'], actual_model_raw_SDK_GPU_remote_Git_GO=0), f)
groups, refusals = [], []
try:
    for row in purpose['source_files']:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['SHA']
    for p in N.glob('*.py'):
        ast.parse(p.read_text(encoding='utf8'))
    import wm_only_task275 as m
    task = m.make_task(dict(run_id='SYNTHETIC_METADATA275_NOT_ACTUAL',
        job_root='/synthetic275/job', owner_root='/synthetic275/owner',
        worker_SHA='a'*64, source_CPU_report_SHA='b'*64, actual272_receipt_SHA='c'*64,
        actual274_receipt_SHA='d'*64, qualified240_package_root='/synthetic275/teacher_package',
        model_path='/synthetic275/frozen_teacher.pt', model_SHA=m.SOURCE_SHA, model_bytes=22099209,
        generation='synthetic275', GPU_UUID='GPU-SYNTHETIC-NOT-RESOURCE'))
    assert task['source_SHA'] == m.SOURCE_SHA and task['source_parent_SHA'] == m.PARENT_SHA
    assert task['qualified240_package_root'] == '/synthetic275/teacher_package'
    spec = dict(task, key='jump_72', execution_backend='target72', manifest_SHA='e'*64)
    schedule = dict(run_id=task['run_id'], experts={'jump_72': spec},
        scheduling_authority='human_requested_available_experts', deferred_experts=[])
    assert m.validate_task(task) and m.validate_schedule(schedule)
    assert task['num_envs'] == 80 and task['ground_envs'] == 8 and task['jump_envs'] == 72
    assert task['WM_source_INDEX_SHA'] == purpose['selected273V2_INDEX_SHA']
    groups.append(dict(name='typed_current_teacher_WM_only_Task_extras_parent_provenance_original_slot_schedule', passed=True))

    evidence = dict(passed=True, WM_ONLY=True, FROZEN_TEACHER=True, teacher_fullstate_CPU_passed=True,
        actor35_critic38_STD6_full17Adam_finite=True, actual272_complete_current_packet_PASS=True,
        actual274_CUDA_H32_no_step_PASS=True, first_current_anchor_only=True,
        fresh_CNone_CIM_resources_actual=True, target_private_and_validation_EX_probe_released=True,
        actual_Pi_Critic_teacher_updates=0, admission_optimizer_steps=0,
        supported_start_candidates=2337, actual_resource_admission_SHA='f'*64)
    ready = m.make_ready_value(spec, evidence)
    digest = hashlib.sha256(json.dumps(ready, indent=2).encode()).hexdigest()
    row = dict(key='jump_72', phase='ready', manifest_SHA=spec['manifest_SHA'], original_error=False,
        closed_source_CPU=dict(value=ready, SHA=digest, actual_CPU_waited_EXIT0=True))
    assert m.valid_ready(row, spec) and digest == m.ready_value_SHA(ready)
    assert digest != task['source_CPU_report_SHA']
    go = dict(m.flat_go_fields(spec), run_id=task['run_id'], source_SHA=m.SOURCE_SHA,
        source_CPU_SHA=digest, source_qualification_kind=m.READY_KIND, manifest_SHA=spec['manifest_SHA'],
        learning_started_epoch=1000., save_deadline=4600., nominal_end_epoch=4900.,
        max_parent_seconds=3900, exit_headroom_seconds=300)
    assert m.validate_go(go, go['run_id'], task, 1001.) and m.validate_ready_go(go, ready, spec)
    assert 'source_CPU_SHA' not in m.flat_go_fields(spec) and 'GPU_UUID' not in m.flat_go_fields(spec)
    assert ready['actual_resource_admission_SHA'] != task['worker_SHA']
    groups.append(dict(name='whole_Ready_VALUE_SHA_original_owner_flat_GO_serialization_no_hash_cycle', passed=True,
        actual_owner_or_GO_executed=False, resource_SHA_scope_separate=True))

    def receipt(first=True):
        u, controls = (1, 32) if first else (2, 64)
        saved = dict(path='/synthetic275/production/WM_complete.pt', bytes=12345, SHA='1'*64,
            saved_WM_updates=u, WM_Adam_step_min=u, WM_Adam_step_max=u,
            teacher_iteration=2135, teacher_Adam_step=42940, teacher_LR=m.TEACHER_LR,
            typed_WM_only_task_present=True, full_WM_tree_finite=True,
            frozen_teacher_fullstate_preserved=True, replay_saved=False,
            complete_three_optimizer_conversion=False, save_epoch=1002. if first else 4601.)
        r = dict(passed=True, kind=m.FIRST_KIND if first else m.FINAL_KIND, run_id=task['run_id'],
            source_SHA=m.SOURCE_SHA, actual_new_WM_updates=u, actual_new_PPO_updates=0,
            actual_new_Pi_updates=0, actual_new_critic_updates=0, actual_new_STD_updates=0,
            actual_Pi_Critic_teacher_updates=0, WM_optimizer_count=1,
            teacher_actor_critic_STD_full17Adam_unchanged=True, teacher_iteration=2135,
            teacher_Adam_step=42940, teacher_LR=m.TEACHER_LR, convert_actor44_critic47=False,
            complete_three_optimizer_conversion=False, new_completed_controls=controls,
            new_environment_transitions=controls*80, physics_callbacks=controls*8, feedback_samples=controls*2,
            teacher_source_byte_reads=1, teacher_source_decodes=1,
            actual_resource_admission_SHA='3'*64,
            finite_WM_loss_grad_params_optimizer=True, native24_before_first_WM_step_passed=True)
        r['first_complete' if first else 'final'] = saved
        return r
    first, final = receipt(), receipt(False)
    assert m.validate_first(first, task, go) and m.validate_final(final, task, go)
    groups.append(dict(name='FIRST_final_actual_WM_counts_frozen2135_42940_LR_native24_full_WM_save', passed=True,
        synthetic_receipts_only=True, actual_PPO_Pi_Critic_teacher_updates=0))

    def reject(name, fn):
        try:
            fn()
        except (ValueError, TypeError, KeyError):
            refusals.append(name)
        else:
            raise AssertionError('Invalid metadata accepted: ' + name)
    reject('old2050_cannot_be_current_teacher', lambda: m.validate_task(dict(task, source_SHA=m.PARENT_SHA)))
    reject('actor44_conversion_not_WM_warm', lambda: m.validate_task(dict(task, actor_obs=44)))
    reject('Task_Ready_hash_cycle_forbidden', lambda: m.validate_task(dict(task, source_CPU_SHA=digest)))
    reject('Pi_updates_not_allowed', lambda: m.validate_task(dict(task, Pi_updates_allowed=True)))
    reject('future_actual_depth_not_allowed', lambda: m.validate_task(dict(task, future_actual_depth_in_H32=True)))
    other_schedule = deepcopy(schedule)
    other_schedule['experts']['another_role'] = deepcopy(spec)
    reject('second_slot_not_authorized', lambda: m.validate_schedule(other_schedule))
    reject('GO_PPO_masquerade', lambda: m.validate_go(dict(go, WM_ONLY=False), go['run_id'], task, 1001.))
    bad_row = deepcopy(row)
    bad_row['closed_source_CPU']['SHA'] = '2'*64
    assert not m.valid_ready(bad_row, spec)
    refusals.append('Ready_VALUE_digest_mismatch')
    reject('GO_model_CPU_SHA_is_not_Ready_SHA', lambda: m.validate_ready_go(dict(go, source_CPU_SHA=task['source_CPU_report_SHA']), ready, spec))
    reject('fake_new_PPO_update', lambda: m.validate_first(dict(first, actual_new_PPO_updates=1), task, go))
    reject('teacher_Adam_must_not_progress', lambda: m.validate_final(dict(final, teacher_Adam_step=42960), task, go))
    early = deepcopy(final)
    early['final']['save_epoch'] = 4599.
    reject('early_normal_save_not_full_window', lambda: m.validate_final(early, task, go))
    assert len(refusals) == 12
    owner = ast.parse(Path(purpose['actual240_owner_source']).read_text(encoding='utf8'))
    calls = [n for n in ast.walk(owner) if isinstance(n, ast.Call)]
    assert any(isinstance(n.func, ast.Name) and n.func.id == 'validate_schedule' for n in calls)
    assert any(isinstance(n.func, ast.Name) and n.func.id == 'flat_go_fields' for n in calls)
    assert any(isinstance(n.func, ast.Attribute) and n.func.attr == 'valid_ready' for n in calls)
    common = Path(purpose['actual240_common_source']).read_text(encoding='utf8')
    assert 'def charge_values(' in common and 'def authenticated_row(' in common
    assert 'torch' not in __import__('sys').modules
    groups.append(dict(name='new_interface_refusals_and_actual240_AST_call_shapes_no_control_execution',
        passed=True, refusals=refusals, original_HMAC_twofcntl_fee_functions_executed=0))
    report = dict(passed=True, epoch=time.time(), purpose_ID=purpose['purpose_ID'], groups=groups,
        refusals=len(refusals), source_only=True, synthetic_JSON_only=True,
        model_raw_assets_Torch_SDK_GPU_SSH_GO_account_Git=0, old_fixtures_replayed=0,
        actual_Pi_WM_updates=0, actual_Task_Ready_GO_admitted=False)
except BaseException:
    report = dict(passed=False, epoch=time.time(), purpose_ID=purpose['purpose_ID'], groups=groups,
        error=traceback.format_exc(), scope='NEW275 pure JSON interface only; no actual control/model case')
    raise
finally:
    with (R / 'ACTUAL275_NEW_WM_ONLY_METADATA_INTERFACE_CPU_RETURNED.json').open('x', encoding='utf8') as f:
        json.dump(report, f, indent=2, allow_nan=False)
print(json.dumps(dict(passed=report['passed'], groups=len(groups), refusals=len(refusals), actual_Pi_WM_updates=0)))

"""W35-only metadata contract; no model, authority, process or SDK access."""
from pathlib import Path
import hashlib
import json
import math

KIND = 'MOD4_W35_QUALIFIED343E_CONTINUE227_READY'
WORKER_KIND = 'MOD4_W35_FULL_RM70_QUALIFIED343E_CONTINUE227'
SHA = '343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'
SOURCE_BYTES = 17619269
ITER = 32404
ADAM = 649720
LR = .00017085937500000009
PRIOR_UPDATES = 68
CPU_SHA = 'cf90bf84c8f5586277f20db1f58e0bab33458f682525287661e8a5ca61d05774'
GENERATION = 'MOD4_SINGLE_WRITER72_20261026'
CANONICAL = '/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
SOURCE_JOB = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_SHARED214_SOLO219_1793475223790058200/w35_72'
SOURCE_MODEL = SOURCE_JOB + '/production/model_final_complete.pt'
# Preserve original three_slot_common_v1.GPUS['w35_72'] binding.
GPUS = {'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def owner_ready_sha(value):
    # Existing original-owner convention, not the historical formal-CPU SHA.
    return hashlib.sha256(json.dumps(value, indent=2).encode()).hexdigest()


def metadata(path):
    p = Path(path)
    require(p.suffix == '.json' and not p.name.endswith(('.partial', '.active')), 'Complete JSON only')
    b = p.read_bytes()
    return json.loads(b), dict(path=str(p), bytes=len(b), SHA=hashlib.sha256(b).hexdigest())


def qualified(closing, cpu, cpu_sha):
    require(cpu_sha == CPU_SHA and cpu['passed'] is True, 'Selected saved NEW219 CPU proof')
    q = cpu['roles']['w35_72']
    r = closing['roles']['w35_72']
    f = r['formal']
    require(closing['passed_collection'] and r['qualified_formal'], 'Qualified original219 formal')
    for value in (q, f, r['final']['final'], closing['formals']['w35_72']):
        require(value['SHA'] == SHA and value['bytes'] == SOURCE_BYTES, 'W35 formal identity')
    require(q['passed'] and q['actor35_critic38_STD6'] and q['complete_task_and_DR_state_present'], 'Whole state proof')
    require(q['finite_tensors'] == 181 and q['saved_iteration'] == ITER and q['Adam17_step'] == ADAM, 'Saved whole-model counters')
    require(q['new_PPO_updates'] == PRIOR_UPDATES and q['actual_saved_optimizer_LR'] == [LR], 'Actual saved LR and prior updates')
    require(q['save_at_or_after_requested_deadline'] is True, 'Original deadline complete save')
    require(f['path'] == SOURCE_MODEL and f['saved_iteration'] == ITER and f['Adam_min'] == f['Adam_max'] == ADAM, 'Remote input formal')
    require(f['actual_new_PPO_updates'] == PRIOR_UPDATES and r['final']['passed'], 'Complete prior run')
    require(r['errors'] == [] and r['actual_material_limit_error_count'] == 0 and r['private_EX_free'], 'No known material error / original EX free')
    terminal = r['original_node_terminal']['row']
    require(terminal['returncode'] == 0 and terminal['terminal_all_own_children_waited'] and not terminal['original_error'], 'Original worker wait0')
    require(r['original_node_exit']['all_own_children_waited'] and r['original_node_exit']['private_EX_released'], 'Original node exit')
    owner = closing['owner_closed']
    require(owner['passed'] and owner['canonical_None'] and owner['shared_locks_free'], 'Historical original owner closure')
    require(closing['formals']['w35_72']['two_host_SHA_equal'] is True, 'Saved formal transfer identity')
    # No separate post-app.close marker is invented. Original wait0 + FINAL +
    # errors[] and the frozen worker finally App.close establish the old close.
    return dict(source_SHA=SHA, source_bytes=SOURCE_BYTES, source_iteration=ITER,
                source_Adam_step=ADAM, source_LR=LR, source_prior_new_PPO_updates=PRIOR_UPDATES,
                source_model_path=SOURCE_MODEL, source_saved_fullstate_CPU_SHA=cpu_sha,
                source_fullstate_CPU_passed=True, all_actor_critic_optimizer_tensors_finite=True,
                actual_35_38_6_shapes=True, historical219_closed_epoch=owner['epoch'])


def fresh_admission(fresh, historical_closed_epoch):
    require(fresh['kind'] == 'ROOT227_FRESH_CNONE_CIM_RESOURCE_ADMISSION', 'New ROOT admission kind')
    required = dict(passed=True, canonical_path=CANONICAL, canonical_generation=GENERATION,
        canonical_active=None, canonical_total_authorized_seconds=2268000,
        fresh_LOCAL_exact_CIM_passed=True, private_EX_probe_free=True, shared_EX_probe_free=True,
        no_new_writer_grant_copy_refund_or_hotadd=True)
    for k, expected in required.items():
        require(type(fresh[k]) is type(expected) and fresh[k] == expected, 'Fresh ROOT fact: ' + k)
    epochs = [fresh[k] for k in ('CNone_checked_epoch', 'LOCAL_exact_CIM_checked_epoch', 'resource_checked_epoch')]
    require(all(type(x) in (int, float) and math.isfinite(x) and x >= historical_closed_epoch for x in epochs), 'New actual checks after old closure')
    require(fresh['control_snapshot_id'] and fresh['GPU_UUID'] in GPUS, 'Actual control snapshot / original72 GPU')
    # These are the original light limits; nonempty compute UUID is permitted.
    require(fresh['GPU_name'] == 'NVIDIA GeForce RTX 4090' and fresh['GPU_free_MiB'] > 15669 and fresh['GPU_util_percent'] <= 30, 'Original GPU light limits')
    require(fresh['RAM_available_bytes'] > 32*1024**3 and fresh['disk_free_bytes'] > 25*1024**3, 'Original RAM/disk light limits')
    for k in ('fresh_CNone_receipt_SHA', 'fresh_LOCAL_exact_CIM_receipt_SHA', 'fresh_resource_receipt_SHA'):
        require(isinstance(fresh[k], str) and len(fresh[k]) == 64, 'Actual report binding: ' + k)
    return True


def validate_task(task):
    expected = dict(kind=WORKER_KIND, launch_contract_kind=KIND, role_key='w35_72', num_envs=20000,
        source_SHA=SHA, source_bytes=SOURCE_BYTES, source_iteration=ITER, source_Adam_step=ADAM,
        source_LR=LR, source_prior_new_PPO_updates=PRIOR_UPDATES, model_path=SOURCE_MODEL,
        original_canonical_generation=GENERATION, selected219V3_fullstate_CPU_proof_SHA=CPU_SHA,
        selected219V3_fullstate_CPU_proof_reused=True, actual_scene0PT211_passed=True,
        actual_robot0PT212_passed=True, new_RM70_geometry_course_and_xyzw_source_reviewed=True,
        same_RM70_profile_fullstate_restore_required=True, actual_shared_material20k0PT_passed=True,
        actual_material_limit_error_count=0,
        source_read_purpose=dict(physical_byte_opens=1, decodes=1, source_bytes=SOURCE_BYTES))
    for k, v in expected.items():
        require(task[k] == v, 'Task identity: ' + k)
    require(task['GPU_UUID'] in GPUS and 'source_CPU_SHA' not in task, 'Selected GPU; no cyclic Ready hash in Task')
    require(task['max_parent_seconds'] == 3900 and task['save_after_seconds'] == 3600 and task['exit_headroom_seconds'] == 300, 'Original finite window')
    return True


def validate_ready(value, spec):
    return bool(value.get('passed') is True and value.get('kind') == KIND and
        value.get('source_SHA') == SHA and value.get('source_iteration') == ITER and
        value.get('Adam_step') == ADAM and value.get('source_LR') == LR and
        value.get('source_saved_fullstate_CPU_SHA') == CPU_SHA and
        value.get('source_fullstate_CPU_passed') is True and
        value.get('all_actor_critic_optimizer_tensors_finite') is True and
        value.get('actual_35_38_6_shapes') is True and
        value.get('manifest_SHA') == spec['manifest_SHA'] and
        value.get('launch_evidence_SHA') == spec['launch_evidence_SHA'] and
        value.get('fresh_CNone_CIM_and_resources_passed') is True and
        value.get('same_RM70_profile_fullstate_restore_required') is True and
        value.get('actual_shared_material20k0PT_passed') is True and
        value.get('actual_material_limit_error_count') == 0)


def validate_job(job, task, go):
    validate_task(task)
    job = Path(job)
    evidence, evidence_ref = metadata(job/'PRELAUNCH227_ACTUAL_EVIDENCE.json')
    require(evidence_ref['SHA'] == task['launch_evidence_SHA'] == go['launch_evidence_SHA'], 'Actual evidence binding')
    require(evidence['kind'] == 'ROOT227_QUALIFIED_AND_FRESH_ACTUAL_JOIN', 'Actual join kind')
    fresh_admission(evidence['fresh_actual'], evidence['qualification']['historical219_closed_epoch'])
    require(evidence['qualification']['source_SHA'] == SHA and evidence['qualification']['source_saved_fullstate_CPU_SHA'] == CPU_SHA, 'Qualified W35 evidence')
    ready, _ = metadata(job/'ADMISSION227_READY.json')
    manifest, mr = metadata(job/task['manifest_file'])
    require(validate_ready(ready, dict(manifest_SHA=mr['SHA'], launch_evidence_SHA=evidence_ref['SHA'])), 'Ready/manifest/evidence join')
    require(go['source_CPU_SHA'] == owner_ready_sha(ready), 'Owner-issued complete Ready hash')
    require(go['manifest_SHA'] == mr['SHA'] and go['source_qualification_kind'] == KIND, 'GO typed qualification')
    require(go['role_key'] == 'w35_72' and go['one_original_writer'] is True, 'Original sole role')
    require(go['prelaunch_control_snapshot_id'] == evidence['fresh_actual']['control_snapshot_id'], 'Fresh control binding')
    require(manifest['input_model_metadata']['SHA'] == SHA, 'Manifest selected W35 source')
    require(all(not r['relative'].endswith(('.pt', '.partial', '.active')) for r in manifest['files']), 'Model metadata only / complete source files')
    return dict(passed=True, source_SHA=SHA, model_opens=0, original_owner_ready_SHA=go['source_CPU_SHA'])

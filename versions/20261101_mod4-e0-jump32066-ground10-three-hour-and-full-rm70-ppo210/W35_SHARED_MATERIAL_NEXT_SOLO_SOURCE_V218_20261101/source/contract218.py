"""Metadata-only W35 shared-material next-window contract. No process control.

The root supplies frozen, closed actual JSON receipts. Selectors make every
gate fact traceable to one of those exact bytes. This module never opens PT,
NPZ, USD, logs, raw trajectories, or the canonical ledger.
"""
from pathlib import Path
import hashlib
import json
import math

KIND = 'MOD4_W35_SHARED214_NEXT_SOLO218_READY'
WORKER_KIND = 'MOD4_W35_FULL_RM70_MATERIAL_SHARED214'
SHA = 'ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
SOURCE_BYTES = 17619013
ITER = 32336
ADAM = 648360
LR = .00011390625000000003
GENERATION = 'MOD4_SINGLE_WRITER72_20261026'
CANONICAL = '/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
OLD_CPU_SHA = 'c633a5eb9f091c6d6b2327ae86b3d0b61d25c1b43964b20d875567f97c692442'
WORKER214_SHA = '3abbbbd66351380e2b287d8490cac73cfbc5dd27681c1b2d008085a88c082170'
GPUS = {'GPU-16828f91-2b45-b646-8dc0-9481138e2842',
        'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}


class Contract218Error(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Contract218Error(reason)


def h_bytes(data):
    return hashlib.sha256(data).hexdigest()


def owner_ready_sha(value):
    # Exactly the existing original-owner/node closed_source_CPU convention.
    return h_bytes(json.dumps(value, indent=2).encode())


def metadata(path):
    path = Path(path)
    require(path.suffix == '.json' and not path.name.endswith(('.partial', '.active')),
            'Only complete saved JSON metadata may be read')
    raw = path.read_bytes()
    return json.loads(raw), len(raw), h_bytes(raw)


def inside(job, relative):
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts, 'Receipt path must be job relative')
    actual = (Path(job) / p).resolve()
    require(actual.is_relative_to(Path(job).resolve()), 'Receipt escapes job')
    return actual


def pointer(value, text):
    require(isinstance(text, str) and text.startswith('/'), 'A JSON pointer is required')
    for part in text[1:].split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def project_closed(bundle, job, *, synthetic_fixture=False):
    require(bundle['schema'] == 'mod4.218.closed_actual_selectors.v1', 'Evidence schema')
    require(bundle['status'] == 'CLOSED_ACTUAL_ONLY', 'Pending/partial evidence cannot qualify')
    require(synthetic_fixture or bundle.get('synthetic_fixture_only') is not True,
            'Synthetic CPU fixture cannot qualify production')
    reports = {}
    for name, row in bundle['reports'].items():
        value, count, sha = metadata(inside(job, row['relative']))
        require(row['complete'] is True and count == row['bytes'] and sha == row['SHA'],
                'Closed actual receipt hash/length mismatch: ' + name)
        require(synthetic_fixture or value.get('synthetic_fixture_only') is not True,
                'Synthetic receipt cannot qualify production')
        reports[name] = value
    facts = {}
    for name, select in bundle['facts'].items():
        facts[name] = pointer(reports[select['report']], select['pointer'])
    validate_closed_facts(facts)
    return facts


def validate_closed_facts(f):
    required = {
        'material217_passed': True, 'material217_num_envs': 20000,
        'material217_controls': 8, 'material217_physics': 64, 'material217_feedback': 16,
        'material217_model_opens': 0, 'material217_actor_calls': 0,
        'material217_optimizer_updates': 0,
        'material217_own_restore_new_episode_and_setter_phases_complete': True,
        'material217_owned_stdout_scan_complete': True, 'material217_limit64K_errors': 0,
        'material217_waited_RC': 0, 'material217_App_closed': True,
        'material217_all_own_children_waited_out': True,
        'material217_private_EX_released_and_actual_FREE': True,
        'E0_210_complete_final_saved': True, 'E0_210_App_closed': True,
        'E0_210_worker_and_all_own_children_waited_out': True, 'E0_210_waited_RC': 0,
        'E0_210_original_owner_closed_and_cost_settled': True,
        'E0_new_formal_CPU_passed': True,
        'E0_new_formal_CPU_whole_finite_35_38_6_STD_17Adam_DR': True,
        'canonical_generation': GENERATION, 'canonical_path': CANONICAL,
        'canonical_active': None, 'canonical_total_authorized_seconds': 2268000,
        'fresh_LOCAL_exact_CIM_passed': True,
        'no_new_writer_grant_copy_refund_or_210_hotadd': True,
    }
    for name, wanted in required.items():
        actual = f[name]
        require(type(actual) is type(wanted) and actual == wanted, 'Closed gate: ' + name)
    final_sha = f['E0_210_final_SHA']
    require(isinstance(final_sha, str) and len(final_sha) == 64 and final_sha != SHA,
            'E0 closure artifact must be its own new formal, never W35 input')
    require(f['E0_new_formal_CPU_model_SHA'] == final_sha, 'E0 new CPU/final identity')
    updates = f['E0_210_actual_new_PPO_updates']
    require(type(updates) is int and updates > 0, 'E0 actual final updates')
    require(f['E0_210_final_iteration'] == 32066 + updates, 'E0 final iteration')
    require(f['E0_210_final_Adam_step'] == 642840 + 20 * updates, 'E0 final Adam')
    require(f['E0_new_formal_CPU_iteration'] == f['E0_210_final_iteration'] and
            f['E0_new_formal_CPU_Adam_step'] == f['E0_210_final_Adam_step'],
            'E0 new CPU iteration/Adam match')
    epochs = [f[k] for k in ('material217_closed_epoch', 'E0_210_closed_epoch',
                            'E0_new_formal_CPU_finished_epoch', 'fresh_CNone_checked_epoch',
                            'fresh_LOCAL_exact_CIM_checked_epoch')]
    require(all(type(x) in (int, float) and math.isfinite(x) for x in epochs), 'Actual epochs')
    require(epochs[0] <= epochs[3] and epochs[1] <= epochs[2] <= epochs[3],
            'Fresh CNone must follow actual closures and new E0 CPU')
    require(epochs[2] <= epochs[4], 'Fresh exact LOCAL CIM follows new E0 CPU')
    require(isinstance(f['fresh_control_snapshot_id'], str) and f['fresh_control_snapshot_id'],
            'Root fresh-control binding is required')
    return True


def validate_task(task):
    expected = dict(kind=WORKER_KIND, launch_contract_kind=KIND, role_key='w35_72',
        num_envs=20000, source_SHA=SHA, source_bytes=SOURCE_BYTES,
        source_iteration=ITER, source_Adam_step=ADAM, source_LR=LR,
        original_canonical_generation=GENERATION, worker_SHA=WORKER214_SHA,
        original_saved_W35_fullstate_CPU_proof_SHA=OLD_CPU_SHA,
        original_saved_W35_fullstate_CPU_proof_reused=True,
        actual_scene0PT211_passed=True, actual_robot0PT212_passed=True,
        new_RM70_geometry_course_and_xyzw_source_reviewed=True,
        actual_shared_material20k0PT_passed=True, actual_material_limit_error_count=0,
        source_read_purpose=dict(physical_byte_opens=1, decodes=1, source_bytes=SOURCE_BYTES))
    for key, value in expected.items():
        require(task[key] == value, 'W35 task identity: ' + key)
    require(task['GPU_UUID'] in GPUS, 'Selected original 72 GPU')
    require('source_CPU_SHA' not in task, 'Ready SHA must not be placed inside Task/manifest')
    return True


def validate_manifest(manifest):
    for row in manifest['files']:
        relative = row['relative']
        require(not relative.endswith(('.partial', '.active')), 'Active partial excluded')
        require(Path(relative).suffix != '.pt', 'Selected source PT must be metadata-only, not hashed by node')
    require(manifest['input_model_metadata']['SHA'] == SHA and
            manifest['input_model_metadata']['bytes'] == SOURCE_BYTES,
            'Manifest W35 model metadata')
    return True


def validate_ready(value, spec):
    return bool(value.get('passed') is True and value.get('kind') == KIND and
        value.get('manifest_SHA') == spec.get('manifest_SHA') and
        value.get('source_SHA') == SHA and value.get('source_iteration') == ITER and
        value.get('Adam_step') == ADAM and value.get('source_fullstate_CPU_passed') is True and
        value.get('source_saved_fullstate_CPU_SHA') == OLD_CPU_SHA and
        value.get('all_actor_critic_optimizer_tensors_finite') is True and
        value.get('actual_35_38_6_shapes') is True and
        value.get('launch_evidence_SHA') == spec.get('launch_evidence_SHA') and
        value.get('actual_shared_material20k0PT_passed') is True and
        value.get('actual_material_limit_error_count') == 0 and
        value.get('actual_target0PT_waited_RC') == 0 and
        value.get('actual_target0PT_controls') == 8 and
        value.get('actual_target0PT_physics') == 64 and
        value.get('actual_target0PT_feedback') == 16 and
        value.get('actual_target0PT_num_envs') == 20000 and
        value.get('target0PT_private_EX_released') is True and
        value.get('E0_210_closed_new_formal_CPU_and_fresh_CNone') is True)


def validate_job_before_delegate(job, go, task, *, synthetic_fixture=False):
    validate_task(task)
    bundle, _, bundle_sha = metadata(Path(job) / 'PRELAUNCH218_CLOSED_EVIDENCE.json')
    require(bundle_sha == task['launch_evidence_SHA'] == go['launch_evidence_SHA'],
            'Evidence binding to Task/GO')
    facts = project_closed(bundle, job, synthetic_fixture=synthetic_fixture)
    ready, _, _ = metadata(Path(job) / 'ADMISSION218_READY.json')
    manifest, _, manifest_sha = metadata(Path(job) / task['manifest_file'])
    validate_manifest(manifest)
    spec = dict(manifest_SHA=manifest_sha, launch_evidence_SHA=bundle_sha)
    require(validate_ready(ready, spec), 'Ready/manifest/source/evidence join')
    require(go['source_CPU_SHA'] == owner_ready_sha(ready), 'Original owner Ready SHA binding')
    require(go['manifest_SHA'] == manifest_sha and go['source_qualification_kind'] == KIND,
            'Original owner manifest/qualification binding')
    require(go['role_key'] == 'w35_72' and go['one_original_writer'] is True,
            'Next sole W35 role')
    require(go['prelaunch_control_snapshot_id'] == facts['fresh_control_snapshot_id'],
            'Original owner used the actual fresh control snapshot')
    return dict(passed=True, kind=KIND, source_SHA=SHA, launch_evidence_SHA=bundle_sha,
                original_owner_ready_SHA=go['source_CPU_SHA'], model_opens=0,
                note='Metadata gate only; underlying214 still performs full restore/native24 before PPO')

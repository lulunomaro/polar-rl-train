"""Derive teacher-guard provenance from actual original small source/metadata.

Never reads/stats a teacher/A1 checkpoint, creates an actor, or observes the SDK.
The evidence is source binding + actual successful FINAL, not a new tensor trace.
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
from pathlib import Path

WORKER_REL = 'worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py'
BRIDGE_REL = 'worker_sources/native_supermimic_bridge.py'
WORKER_PIN = (17704, '7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7')
BRIDGE_PIN = (13125, '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29')
EVIDENCE_KIND = 'PARENT_VERIFIED_ACTUAL_PRODUCER_TEACHER_STATE_GUARD_V1'
POLICY_VARIANT = 'A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def metadata(path):
    path = Path(path)
    need(path.suffix == '.json' and 'budget' not in path.name.lower(), 'explicit non-budget JSON only')
    with path.open('rb') as stream:
        raw = stream.read(8 * 1024 * 1024 + 1)
    need(len(raw) <= 8 * 1024 * 1024, 'producer metadata exceeds bound')
    result = json.loads(raw)
    need(type(result) is dict, 'producer metadata object required')
    return result, raw


def teacher_identity(value):
    need(type(value) is dict and value.get('teacher_frozen') is True, 'original teacher frozen byte provenance required')
    result = {key: value.get(key) for key in ('source_path', 'source_SHA', 'source_bytes', 'teacher_frozen')}
    need(type(result['source_path']) is str and result['source_path']
         and type(result['source_SHA']) is str and len(result['source_SHA']) == 64
         and all(c in '0123456789abcdef' for c in result['source_SHA'])
         and type(result['source_bytes']) is int and result['source_bytes'] > 0, 'original mother provenance differs')
    return result


def source_guard_mechanism(worker_raw, bridge_raw):
    """Audit full exact pinned modules, never execute/crop producer Python."""
    need((len(worker_raw), sha(worker_raw)) == WORKER_PIN, 'actual staged worker pin differs')
    need((len(bridge_raw), sha(bridge_raw)) == BRIDGE_PIN, 'actual staged bridge pin differs')
    worker = worker_raw.decode('utf-8').replace('\r\n', '\n')
    bridge = bridge_raw.decode('utf-8').replace('\r\n', '\n')
    tree = ast.parse(worker); ast.parse(bridge)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    guard = next(n for n in ast.walk(main) if isinstance(n, ast.FunctionDef) and n.name == 'assert_teacher_actor_unchanged')
    guard_text = ast.get_source_segment(worker, guard)
    for required in ('teacher.assert_frozen()', 'current=actor.state_dict()', 'set(current)==set(actor_snapshot)',
                     'torch.equal(current[key],value)', 'not p.requires_grad'):
        need(required in guard_text, 'original complete teacher guard differs: ' + required)
    need('actor_snapshot={key:value.detach().clone() for key,value in actor.state_dict().items()}' in worker,
         'original device snapshot must include all state_dict parameters and buffers')
    save = next(n for n in ast.walk(main) if isinstance(n, ast.FunctionDef) and n.name == 'save')
    calls = sorted((n for n in ast.walk(save) if isinstance(n, ast.Call)), key=lambda n:(n.lineno,n.col_offset))
    check = next(n for n in calls if isinstance(n.func, ast.Name) and n.func.id == 'assert_teacher_actor_unchanged')
    write = next(n for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == 'save')
    need((check.lineno,check.col_offset) < (write.lineno,write.col_offset), 'original check must precede each complete save')
    need("assert_teacher_actor_unchanged();put(out/'FINAL.json'" in worker, 'original check must precede success FINAL')
    need('a.to(device).eval().requires_grad_(False)' in bridge, 'original live teacher freeze/device semantics differ')
    return dict(full_modules_AST_parsed_not_executed=True, snapshot_scope='all actor.state_dict parameters and buffers on original actor device',
                worker_snapshot_lines=[70,72], before_each_save_lines=[81,83], before_FINAL_lines=[97,98],
                original_teacher_device_freeze_lines=[43,49], live_tensor_observation_by_this_verifier=None)


def derive_producer_guard(producer):
    """Called by stager/worker/semantic gate; no trusted caller boolean is accepted."""
    need(type(producer) is dict and type(producer.get('FINAL')) is dict, 'actual attested producer descriptor required')
    final = producer['FINAL']; cp = final.get('checkpoint')
    need(final.get('kind') == 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
         and final.get('passed_execution') is True and final.get('teacher_unchanged') is True
         and type(cp) is dict and cp.get('teacher_unchanged') is True, 'successful producer teacher invariance receipts required')
    for key in ('role_key', 'run_id'):
        need(producer.get(key) == final.get(key), 'producer guard identity differs: ' + key)
    mother = teacher_identity(final.get('teacher'))
    need(mother == teacher_identity(cp.get('teacher_source')), 'producer FINAL/checkpoint mother provenance differs')
    # lexical only: no checkpoint resolve/stat/open or independent mother file check.
    job = Path(os.path.abspath(producer['own_job_root']))
    task, task_raw = metadata(job / 'TASK.json')
    manifest, manifest_raw = metadata(job / 'INSTALL_MANIFEST.json')
    need(task.get('manifest_SHA') == sha(manifest_raw), 'actual producer TASK/INSTALL_MANIFEST byte binding differs')
    for key in ('role', 'role_key', 'run_id'):
        need(task.get(key) == final.get(key), 'actual producer TASK identity differs: ' + key)
    need(task.get('teacher_path') == mother['source_path'] and task.get('teacher_SHA') == mother['source_SHA']
         and task.get('teacher_bytes') == mother['source_bytes'], 'actual producer TASK teacher identity differs')
    files = manifest.get('files')
    need(type(files) is list and all(type(row) is dict for row in files), 'actual source install manifest files required')
    observed = {}
    raws = {}
    for relative, pin in ((WORKER_REL, WORKER_PIN), (BRIDGE_REL, BRIDGE_PIN)):
        rows = [row for row in files if row.get('relative') == relative]
        need(len(rows) == 1 and rows[0].get('bytes') == pin[0] and rows[0].get('SHA') == pin[1],
             'actual producer installed source manifest pin differs: ' + relative)
        source = job / relative
        need(not source.is_symlink() and not source.parent.is_symlink() and not job.is_symlink(), 'actual producer source symlink differs')
        raw = source.read_bytes()
        need((len(raw), sha(raw)) == pin, 'actual producer source bytes differ: ' + relative)
        observed[relative] = dict(path=str(source), bytes=len(raw), SHA256=sha(raw))
        raws[relative] = raw
    mechanism = source_guard_mechanism(raws[WORKER_REL], raws[BRIDGE_REL])
    return dict(kind=EVIDENCE_KIND, role=final['role'], role_key=final['role_key'], run_id=final['run_id'],
        source_A1_SHA=cp['SHA'], actual_staged_worker_source=observed[WORKER_REL],
        actual_staged_bridge_source=observed[BRIDGE_REL], actual_TASK_SHA=sha(task_raw), actual_INSTALL_MANIFEST_SHA=sha(manifest_raw),
        actual_producer_FINAL_SHA=producer['FINAL_SHA'], actual_producer_FINAL_bytes=producer['FINAL_bytes'],
        parent_verified_actual_staged_source=True, state_dict_snapshot_all_parameters_and_buffers=True,
        torch_equal_before_each_complete_save=True, torch_equal_before_success_FINAL=True,
        producer_success_FINAL_and_checkpoint_teacher_unchanged=True, original_bootstrap_teacher=mother,
        evidence_basis='ACTUAL_TASK_MANIFEST_SOURCE_BYTES_PLUS_SUCCESSFUL_ACTUAL_FINAL_NOT_A_NEW_GPU_TRACE',
        source_guard_mechanism=mechanism, actual_source_module_execution_by_this_verifier=False,
        mother_checkpoint_stat_open_hash=0, A1_checkpoint_stat_open_hash=0)


def validate_bound_probe_row(row):
    need(type(row) is dict and row.get('policy_variant') == POLICY_VARIANT, 'explicit ZERO_UPDATE bound-only actor row required')
    producer = row.get('a1_producer'); evidence = derive_producer_guard(producer)
    need(row.get('producer_teacher_freeze_evidence') == evidence, 'teacher producer guard must match rederived actual source evidence')
    mother = teacher_identity(producer['FINAL']['teacher'])
    need(row.get('original_bootstrap_teacher') == mother, 'explicit original mother identity differs from producer')
    need(row.get('actor_semantics') == 'OWN_A1_TEACHER_PLUS_POINT05_TANH_RESIDUAL_ZERO_UPDATE'
         and row.get('actor_container_identity') == 'OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE', 'bound probe effective-actor/container semantic identity differs')
    config = row.get('bound_only_probe', {})
    need(type(config) is dict and config.get('purpose') == 'FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1'
         and config.get('policy_variant') == POLICY_VARIANT and config.get('zero_update') is True
         and config.get('native_enabled') is True and type(config.get('collect_action_statistics')) is bool,
         'explicit native-capable ZERO_UPDATE selection required')
    expected = {'E3': 'a4c56390b4c549ba8bfb808a63206c0816ad50e8c9659dc053f98cc66b3c8127', 'W35': 'b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff'}
    need(row.get('role') in expected and row.get('source_SHA') == producer['FINAL']['checkpoint']['SHA'] == expected[row['role']],
         'bound probe must retain the actual qualified original A1 container')
    return evidence

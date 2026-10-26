"""Local source/small JSON only; creates no payload, TASK, controller or GO."""
from pathlib import Path
import ast
import hashlib
import json
import time

D = Path(__file__).resolve().parent
T = D.parent.parent
F = T / 'H1_STEP270_NATIVE_CONTINUATION_PHASE_OBSERVABILITY_V86_PREPARATION_20261026'
OLD = T / 'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026/payloads/e2'
B = D / 'candidate_overlay'


def H(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fresh(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)


def main():
    source_map = {
        'source/h1_supermimic_bridge_v1.py': F / 'source/h1_supermimic_bridge_native86_with_phase_sampling.py',
        'source/native_continuation_v1.py': F / 'source/native_continuation_v1.py',
        'native_continuation_v1.py': F / 'source/native_continuation_v1.py',
        'source/native_policy_phase_coverage_v1.py': F / 'source/native_policy_phase_coverage_v1.py',
        'NATIVE_CONTINUATION_BINDING_ACTUAL.json': F / 'NATIVE_CONTINUATION_BINDING_ACTUAL.json',
        'NATIVE85_ORIGINAL_COMPLETE_MANIFEST.json': OLD / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json',
    }
    for p in sorted((F / 'native_source_metadata').glob('*.json')):
        source_map['native_source_metadata/' + p.name] = p
    runtime = T / ('H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026/'
        'current_three_closed_text/e2/job0/production/NATIVE_FUDAN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json')
    source_map['native_source_metadata/NATIVE85M2_RUNTIME_OBJECTIVE_CONTRACT_ACTUAL.json'] = runtime
    for relative, source in source_map.items():
        assert source.suffix in ('.json', '.py'), 'Source-only copy restriction'
        fresh(B / relative, source.read_bytes())
    worker = (OLD / 'h1_unisupermimic_step270_worker_v1.py').read_text('utf8')
    old_kind = 'UNISUPERMIMIC_FUDAN_H1_83B_CROSSHOST_SOURCE_SDK_CPU_V84'
    assert worker.count(old_kind) == 1
    worker = worker.replace(old_kind, 'UNISUPERMIMIC_FUDAN_NATIVE85_CONTINUATION_SOURCE_SDK_CPU_V86')
    marker = "assert H(src)==go['source_SHA'];assert not (J/phase).exists()"
    assert worker.count(marker) == 1
    worker = worker.replace(marker, "assert H(src)==go['source_SHA'];from native86_source_guard_v1 import check_payload,validate_task_go;check_payload(B);validate_task_go(task,go,H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'));assert not (J/phase).exists()")
    fresh(B / 'h1_unisupermimic_step270_worker_v1.py', worker.encode('utf8'))
    unit = (OLD / 'test_native_h1_fudan_reference_CPU_v84.py').read_text('utf8')
    changes = {
        'validate_objective_contract)': 'validate_objective_contract, validate_reference_preparation)',
        '    require_native_manifest_pins(manifest, bundle)': '    validate_reference_preparation(bundle)',
        "sdk = read(B / 'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')": "sdk = read(B / 'TARGET_NATIVE86_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json')",
        "assert sdk['source_SHA'] == SOURCES['h1']['SHA'] and sdk['all17Adam'] == SOURCES['h1']['Adam']": "assert sdk['bootstrap_SHA'] == SOURCES['h1']['SHA'] and sdk['all17Adam'] == SOURCES['h1']['Adam']\n    assert sdk['source_SHA'] == manifest['source_SHA'] == '94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af'",
        'source_SHA=SOURCES[\'h1\'][\'SHA\']': "source_SHA=manifest['source_SHA']",
        "candidate_pins=bundle['candidate_pins']": "candidate_pins=read(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json')['candidate_pins']",
        'NATIVE_H1_FUDAN_REFERENCE_INSTALLED_CPU_V84_ACTUAL.json': 'NATIVE_H1_FUDAN_REFERENCE_INSTALLED_CPU_V86_ACTUAL.json',
    }
    for before, after in changes.items():
        assert unit.count(before) == 1, before
        unit = unit.replace(before, after)
    unit = unit.replace('UNEXECUTED target CPU source template', 'UNEXECUTED native86 target CPU source template', 1)
    fresh(B / 'test_native_h1_fudan_reference_CPU_v86.py', unit.encode('utf8'))
    for p in B.rglob('*.py'):
        ast.parse(p.read_text('utf8'), filename=str(p))
    rows = [dict(relative=p.relative_to(B).as_posix(), bytes=p.stat().st_size, SHA=H(p))
        for p in sorted(B.rglob('*')) if p.is_file()]
    candidates = dict(
        bridge_source_SHA=H(B / 'source/h1_supermimic_bridge_v1.py'),
        continuation_source_SHA=H(B / 'native_continuation_v1.py'),
        continuation_import_source_SHA=H(B / 'source/native_continuation_v1.py'),
        phase_diagnostic_source_SHA=H(B / 'source/native_policy_phase_coverage_v1.py'),
        finalization_source_SHA=H(OLD / 'source/native_finalization_v1.py'),
        native_CPU_source_SHA=H(B / 'test_native_h1_fudan_reference_CPU_v86.py'),
        native_source_guard_SHA=H(B / 'native86_source_guard_v1.py'),
        source_SDK_CPU_source_SHA=H(B / 'target_native86_source_sdk_cpu_review_v1.py'),
        native_CPU_loader_source_SHA=H(B / 'native86_closed_source_CPU_v1.py'),
        worker_source_SHA=H(B / 'h1_unisupermimic_step270_worker_v1.py'))
    contract = dict(schema='mod4.native86.exact_source_contract.v1', source_only=True,
        original_manifest_SHA=H(OLD / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),
        binding_SHA=H(B / 'NATIVE_CONTINUATION_BINDING_ACTUAL.json'),
        overlay_files=rows, candidate_pins=candidates, controller_replacements=[],
        metadata_replacements=[], controller_additions=[], removed_files=[],
        original_full_inventory_must_be_retained=True,
        controller_replacement_scope='exact_paths_originalSHA_newSHA_and_bytes_only; root must finalize',
        producer_module_path='B/native_continuation_v1.py', import_module_path='B/source/native_continuation_v1.py',
        both_module_paths_byte_exact=True,
        actual_installed86_SDK_CPU_passed=False, no_payload_Task_GO_or_real_model_access=True)
    fresh(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json', (json.dumps(contract, indent=2) + '\n').encode())
    lineage = dict(epoch=time.time(), source_only=True, exact_copies=[dict(relative=k,
        source_path=str(v), bytes=v.stat().st_size, SHA=H(v)) for k, v in source_map.items()],
        worker_original_SHA=H(OLD / 'h1_unisupermimic_step270_worker_v1.py'),
        worker_changes=['typed source qualification kind', 'pre-environment source/task/GO guard only'],
        reference_CPU_original_SHA=H(OLD / 'test_native_h1_fudan_reference_CPU_v84.py'),
        reference_CPU_text_replacements=changes,
        original_errors=[
            dict(id='NATIVE86_HELPER_READER_001', kind='nonexistent guessed source filename',
                 path=str(OLD / 'h1_unisupermimic_source_CPU_v1.py'), result='Get-Content path not found; corrected via rg'),
            dict(id='NATIVE86_HELPER_READER_002', kind='WindowsApps python shim no useful execution',
                 result='py3.14 available but no torch; parent supplied env_isaaclab interpreter'),
            dict(id='NATIVE86_HELPER_READER_003', kind='broad file enumeration access denied',
                 result='rg reported rmuc2026_work/unpack_verify_4zomhj13 denied; no writes; narrowed scope'),
            dict(id='NATIVE86_HELPER_READER_004', kind='nonexistent assumed vendored RSL source path',
                 path=str(OLD / 'lib/rsl_rl/runners/on_policy_runner.py'), result='Get-Content path not found; installed library inspected instead'),
        ], no_real_PT_NPZ_read_hash_copy=True, no_remote_GPU_policy_or_Git=True,
        actual_installed86_SDK_or_Task_GO=False, Git_status='pending parent ordinary supplement archive')
    fresh(D / 'reports/SOURCE_OVERLAY_LINEAGE_AND_READER_ERRORS_ACTUAL.json', (json.dumps(lineage, indent=2) + '\n').encode())
    print(json.dumps(dict(passed=True, overlay_files=len(rows), candidates=candidates, source_only=True)))


if __name__ == '__main__':
    main()

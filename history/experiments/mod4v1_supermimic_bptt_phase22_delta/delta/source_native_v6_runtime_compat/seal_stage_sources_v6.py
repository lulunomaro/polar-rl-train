"""One-shot NEW 14-small-source V6 input/index seal; never real native stage/dispatch.

Run only after the parent-pinned App V6 source and generated CLIs pass local tests.
Old authorities are read as exact small source files, not imported or used as C.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    import stage_a1_native_v6 as stage
    import test_stage_dispatch_stdlib_v6 as tests
    flat = HERE / '_SOURCE_INPUT'
    if flat.exists(): raise RuntimeError('one-shot NEW V6 source input already exists; no replay')
    local = json.loads((HERE / 'TEST_RESULTS_STDLIB_STAGE_DISPATCH_V6.json').read_bytes())
    pose = json.loads((HERE / 'CPU_TEST_RESULTS_V4.json').read_bytes())
    assert local['passed'] is True and local['tests_run'] == 37
    assert pose['passed'] is True and pose['tests_run'] == 66
    mapping = tests.actual_fourteen_sources()
    assert len(mapping) == 14 and set(mapping) == set(stage.FIXED_PINS)
    assert all(stage.is_sha(pin) for pin in stage.FIXED_PINS.values())
    rows = [];originals = []
    # Verify ALL source bytes before creating the exclusive source-input directory.
    material = []
    for install, path in sorted(mapping.items()):
        raw = path.read_bytes();sha = stage.sha_bytes(raw)
        assert sha == stage.FIXED_PINS[install], install
        material.append((install, path, raw, sha))
    for install, path, raw, sha in material:
        relative = 'sealed_source/' + path.name
        stage.write_bytes_once(flat / relative, raw)
        rows.append(dict(source_relative=relative, install_relative=install, SHA=sha, bytes=len(raw)))
        originals.append(dict(path=str(path), SHA=sha, bytes=len(raw), install_relative=install))
    replacements = []
    for install in ('worker_sources/pose_cache_runtime_adapter_v3.py', 'worker_sources/app_close_semantics_v5.py'):
        replacements.append(dict(logical_ABI_path=install, actual_source_filename=mapping[install].name,
            SHA=stage.FIXED_PINS[install], bytes=len(mapping[install].read_bytes()), explicit_NEW_V6_source_not_old_original_bytes=True))
    index = dict(kind=stage.SOURCE_INDEX_KIND, sealed=True, v5_abi_code_seal_SHA=stage.V5_ABI_CODE_SEAL_SHA,
        files=rows, runtime_compatibility_replacements=replacements,
        description='NEW V6 mapping: unchanged sealed V5 worker/owner/shim ABI, explicit new pose V4/App alias V6 source bytes; only small sources, not an actual native stage')
    stage.put_once(flat / 'SEALED_A1_SOURCE_INDEX_V6.json', index)
    resolved = stage.source_index_files(flat, index)
    assert resolved['worker_sources/ctx_reward_learner.py'][1] == resolved['worker_sources/ctx_reward_full_resume_candidate_v2.py'][1]
    artifacts = []
    names = ['pose_cache_runtime_adapter_v4.py', 'test_pose_cache_runtime_adapter_v4.py',
        'CPU_TEST_RESULTS_V4.json', 'POSE_CACHE_SENTINEL_DIFF_V4.patch', 'BUILD_POSE_CACHE_ADAPTER_V4.json',
        'build_pose_cache_adapter_v4.py', 'build_shadow_tests_v4.py', 'build_stage_candidates_v6.py',
        'stage_a1_native_v6.py', 'dispatch_a1_native_v6_once.py', 'test_stage_dispatch_stdlib_v6.py',
        'TEST_RESULTS_STDLIB_STAGE_DISPATCH_V6.json', 'STAGE_RUNTIME_COMPAT_DIFF_V6.patch',
        'BUILD_STAGE_CANDIDATES_V6.json', 'V6_RUNTIME_SOURCE_EVIDENCE_AND_MINIMAL_PLAN.md',
        'build_runtime_source_evidence_v6.py', 'RUNTIME_SOURCE_EVIDENCE_V6.json',
        'build_parent_payload_v6.py', 'V6_STAGE_CLI_AND_STATUS.md', 'seal_stage_sources_v6.py']
    for name in names:
        path = HERE / name;raw = path.read_bytes()
        if path.suffix == '.py': ast.parse(raw.decode('utf-8'));compile(raw, str(path), 'exec')
        artifacts.append(dict(relative=name, SHA=stage.sha_bytes(raw), bytes=len(raw)))
    receipt = dict(kind='NEW_V6_SOURCE_ONLY_FINAL_SEAL_NOT_NATIVE_RETRY', passed=True,
        tests_distinct=103, pose_shadow_tests=66, source_stage_fake_mock_tests=37,
        actual_pinned_small_sources=14, changed_source_pins=2, other_12_source_pins_unchanged=True,
        unchanged_original_owner_protected_AST_SHA=stage.OWNER_PROTECTED_AST_SHA,
        unchanged_original_owner_main_normalized_AST_SHA=stage.OWNER_NORMALIZED_MAIN_AST_SHA,
        v5_bundle_receipt_is_historical_ABI_reference_only=stage.V5_ABI_CODE_SEAL_SHA,
        new_runtime_compatibility_replacements=replacements,
        ready_input_relative='_SOURCE_INPUT/SEALED_A1_SOURCE_INDEX_V6.json',
        source_index_installed_alias_count=len(resolved), source_index_full_mapping_verified=True,
        actual_stage_dispatch_SDK_GPU_originalPT_C_locks_Git_SSH_operations=0,
        Torch_imported='torch' in sys.modules, actual_new_native_type_value_class_receipt_pending=True,
        historical_failed_raw_timestamp_type_value_known=False, native_BPTT_or_skill_claim=False,
        artifacts=artifacts, read_only_exact_small_sources=originals)
    stage.put_once(HERE / 'V6_SOURCE_PROVENANCE_AND_SEAL.json', receipt)
    lines = ['%s  %s' % (row['SHA'], row['relative']) for row in artifacts]
    lines += ['%s  _SOURCE_INPUT/%s' % (row['SHA'], row['source_relative']) for row in rows]
    lines += ['%s  _SOURCE_INPUT/SEALED_A1_SOURCE_INDEX_V6.json' % stage.identity(flat / 'SEALED_A1_SOURCE_INDEX_V6.json')['SHA']]
    stage.write_bytes_once(HERE / 'SHA256SUMS_NATIVE_RUNTIME_V6.txt', ('\n'.join(lines) + '\n').encode())
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__': main()

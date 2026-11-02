"""Freeze ONLY new V5 source/API/tests before any later long documentation.

Bounded prior input/manifest hashes and owned CPU fixtures only; no SDK/Torch,
model, GPU, process, C/accounting, lock, GO or training operation.
"""
from __future__ import annotations
import ast
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def record(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(name=path.name, path=str(path.resolve()), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def put(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def main():
    seal = HERE / 'CODE_DELIVERABLES_SHA256_V5.json'
    if seal.exists():
        raise RuntimeError('already sealed V5 code; do not overwrite or re-run tests into the sealed result')
    build = json.loads((HERE/'BUILD_APP_CLOSE_CANDIDATES_V5.json').read_bytes())
    tests = json.loads((HERE/'CPU_TEST_RESULTS_V5.json').read_bytes())
    assert tests['tests'] == 73 and tests['passed'] is True and tests['failures'] == tests['errors'] == 0
    for item in build['inputs'] + build['outputs']:
        current=record(item['path'])
        assert (current['bytes'], current['SHA256']) == (item['bytes'], item['SHA256']), item['path']
    prior=ROOT/'source_pose_cache_runtime_adapter_v3/DELIVERABLES_SHA256_V3.json'
    assert record(prior)['SHA256']=='40b0426ef060545c2c6c1513a9a723aa7f403264e522ccef3c63970dc240c9c5'
    prior_manifest=json.loads(prior.read_bytes())
    for item in prior_manifest['files']:
        current=record(item['path']);assert current['bytes']==item['bytes'] and current['SHA256']==item['SHA256']
    import build_app_close_candidates_v5 as builder
    pairs=[(builder.WORKER_OLD,builder.WORKER_NEW)]+list(builder.OWNERS)
    diffs=[]
    for old,new in pairs:
        before=(builder.OLD/old).read_text(encoding='utf-8')
        after=(HERE/new).read_text(encoding='utf-8')
        assert builder.normalized_source(after,undo_worker=(old==builder.WORKER_OLD),undo_owner=(old!=builder.WORKER_OLD))==ast.dump(ast.parse(before),include_attributes=False)
        diffs.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
                     fromfile=str(builder.OLD/old),tofile=str(HERE/new),n=3))
    (HERE/'SOURCE_PATCH_V5.diff').write_text(''.join(diffs),encoding='utf-8')
    source_names=['app_close_semantics_v5.py','resume_runtime_app_close_v5.py',
                  'build_app_close_candidates_v5.py',builder.WORKER_NEW]+[new for _,new in builder.OWNERS]+[
                  '_synthetic_app_fixture_v5.py','test_app_close_semantics_v5.py','seal_app_close_code_v5.py']
    for name in source_names:
        compile((HERE/name).read_bytes(),str(HERE/name),'exec',dont_inherit=True)
    # Every retained fixture is own stdlib synthetic JSON/test evidence. Hash,
    # but never execute/read an external model or enumerate any other workspace.
    cases=HERE/'CPU_SYNTHETIC_CASES_V5'
    fixtures=[record(path) for path in sorted(cases.rglob('*')) if path.is_file()]
    put('CPU_SYNTHETIC_CASES_SHA256_V5.json',dict(kind='OWN_CPU_FIXTURE_FILES_ONLY_NOT_NATIVE',
        root=str(cases),file_count=len(fixtures),files=fixtures))
    verification=dict(kind='V5_SOURCE_CODE_API_CPU_SEAL_NOT_NATIVE',CPU_tests=73,CPU_passed=True,
        CPU_fake_process_tests=6,bounded_old_input_files_unchanged=len(build['inputs']),
        prior_V3_manifest_SHA256=record(prior)['SHA256'],prior_V3_sealed_files_unchanged=len(prior_manifest['files']),
        normalized_whole_worker_and_both_owners_AST_equal_after_whitelist_undo=True,
        syntax_compiled_source_files=len(source_names),source_only_no_import_execution=True,
        protected_account_lock_deadline_wait_admission_save_learner_physics_changes=0,
        old_sources_or_sealed_outputs_written=False,actual_native_app_binding=None,
        historical_app_config_or_exit_cause=None,production_checkpoint_bytes_opened=0,
        SDK_Torch_GPU_native_training_or_account_operations=0,owned_synthetic_fixture_files_hashed=len(fixtures))
    put('CODE_VERIFICATION_V5.json',verification)
    names=source_names+['API_CONTRACT_V5.json','BUILD_APP_CLOSE_CANDIDATES_V5.json',
        'CPU_TEST_RESULTS_V5.json','CPU_TEST_EXECUTION_HISTORY_V5.json','CPU_TEST_RUN_V5.log',
        'SOURCE_PATCH_V5.diff','CPU_SYNTHETIC_CASES_SHA256_V5.json','CODE_VERIFICATION_V5.json']
    files=[record(HERE/name) for name in names]
    digest=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    put(seal.name,dict(kind='IMMUTABLE_V5_CODE_API_CPU_SEAL_NEW_ONLY',
        created_at_UTC=datetime.now(timezone.utc).isoformat(),files=files,
        file_count_excluding_this_manifest=len(files),bundle_SHA256=digest,
        manifest_self_excluded=True,additional_docs_may_only_be_new_unsealed_files=True,
        native_execution_or_binding_claim=None))
    print(json.dumps(dict(verification=verification,seal=record(seal),bundle_SHA256=digest,files=len(files)+1)))


if __name__=='__main__':
    main()

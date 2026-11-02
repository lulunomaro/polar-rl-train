"""Append-only overall V5 seal; never rewrites the already sealed code/API/CPU.

Bounded manifest references, owned fake fixtures and explicit report links only.
No SDK/Torch imports, production processes, model/PT, GPU, account, locks or Git.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CODE_SHA = '59e5cb530fbf2e2066856d9ba594afec151f4c5b512382a8905671586fe993a7'
PRIOR_SHA = '40b0426ef060545c2c6c1513a9a723aa7f403264e522ccef3c63970dc240c9c5'


def record(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return dict(name=path.name, path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def check(item):
    current = record(item['path'])
    assert (current['bytes'], current['SHA256']) == (item['bytes'], item['SHA256']), item['path']
    return current


def new_json(name, value):
    raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode('utf-8')
    with (HERE / name).open('xb') as stream:
        stream.write(raw)


def main():
    total = HERE / 'DELIVERABLES_SHA256_V5.json'
    verify = HERE / 'SOURCE_REVIEW_VERIFICATION_V5.json'
    if total.exists() or verify.exists():
        raise RuntimeError('V5 overall seal or verification already exists; append a new version, never overwrite')
    code_path = HERE / 'CODE_DELIVERABLES_SHA256_V5.json'
    assert record(code_path)['SHA256'] == CODE_SHA
    code = json.loads(code_path.read_bytes())
    for item in code['files']:
        check(item)
    digest = hashlib.sha256(json.dumps(code['files'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert digest == code['bundle_SHA256']
    build = json.loads((HERE / 'BUILD_APP_CLOSE_CANDIDATES_V5.json').read_bytes())
    for item in build['inputs']:
        check(item)
    prior = ROOT / 'source_pose_cache_runtime_adapter_v3/DELIVERABLES_SHA256_V3.json'
    assert record(prior)['SHA256'] == PRIOR_SHA
    prior_value = json.loads(prior.read_bytes())
    for item in prior_value['files']:
        check(item)
    cases = (HERE / 'CPU_SYNTHETIC_CASES_V5').resolve()
    fixtures = json.loads((HERE / 'CPU_SYNTHETIC_CASES_SHA256_V5.json').read_bytes())
    for item in fixtures['files']:
        assert Path(item['path']).resolve().is_relative_to(cases), item['path']
        check(item)
    tests = json.loads((HERE / 'CPU_TEST_RESULTS_V5.json').read_bytes())
    assert tests['tests'] == 73 and tests['passed'] is True and tests['failures'] == tests['errors'] == 0
    report_path = HERE / 'APP_CLOSE_SEMANTICS_V5_SOURCE_REVIEW.md'
    report = report_path.read_text(encoding='utf-8')
    links = re.findall(r'\[[^\]]+\]\(<([^>]+)>\)', report)
    text_line_counts = {}
    for destination in links:
        filename, marker, fragment = destination.partition('#')
        path = Path(filename).resolve()
        assert path.is_file(), destination
        if marker:
            matched = re.fullmatch(r'L(\d+)(?:-L?(\d+))?', fragment)
            assert matched, destination
            if path not in text_line_counts:
                text_line_counts[path] = len(path.read_text(encoding='utf-8').splitlines())
            start, end = int(matched.group(1)), int(matched.group(2) or matched.group(1))
            assert 1 <= start <= end <= text_line_counts[path], destination
    compile(Path(__file__).read_bytes(), str(Path(__file__)), 'exec', dont_inherit=True)
    verification = dict(
        kind='V5_APPEND_ONLY_DOCUMENTATION_AND_OVERALL_SEAL_NOT_NATIVE',
        code_manifest_SHA256=CODE_SHA,
        code_sealed_files_reverified=len(code['files']),
        code_manifest_unchanged=True,
        code_bundle_SHA256=code['bundle_SHA256'],
        old_inputs_unchanged=len(build['inputs']),
        prior_V3_manifest_SHA256=PRIOR_SHA,
        prior_V3_sealed_files_unchanged=len(prior_value['files']),
        owned_CPU_fixture_files_unchanged=len(fixtures['files']),
        explicit_report_links_and_line_ranges_valid=len(links),
        CPU_tests=73, CPU_tests_passed=True, CPU_fake_waited_processes=6,
        sealed_CPU_results_not_rerun_or_overwritten=True,
        protected_whole_worker_and_both_owners_AST_undo_equal=True,
        old_source_or_prior_seal_writes=0,
        production_checkpoint_bytes_opened=0,
        SDK_Torch_native_GPU_account_training_operations=0,
        actual_native_App_binding=None,
        historical_App_fast_shutdown_or_exit_cause=None,
        native_skill_pass_rate=None,
    )
    new_json(verify.name, verification)
    names = [item['name'] for item in code['files']] + [
        code_path.name, report_path.name, Path(__file__).name, verify.name,
    ]
    assert len(names) == len(set(names))
    files = [record(HERE / name) for name in names]
    bundle = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    new_json(total.name, dict(
        kind='V5_SOURCE_ONLY_APP_CLOSE_SEMANTICS_TOTAL_DELIVERABLES_NEW_ONLY',
        created_at_UTC=datetime.now(timezone.utc).isoformat(), files=files,
        file_count_excluding_this_manifest=len(files), bundle_SHA256=bundle,
        manifest_self_excluded=True,
        prior_code_manifest_SHA256=CODE_SHA,
        additional_owned_synthetic_fixtures_indexed_by='CPU_SYNTHETIC_CASES_SHA256_V5.json',
        actual_native_App_binding=None, historical_App_fast_shutdown_or_exit_cause=None,
        native_or_skill_acceptance_claim=None,
    ))
    print(json.dumps(dict(verification=verification, total_manifest=record(total),
        bundle_SHA256=bundle, top_level_deliverables_including_manifest=len(files)+1,
        report=record(report_path))))


if __name__ == '__main__':
    main()

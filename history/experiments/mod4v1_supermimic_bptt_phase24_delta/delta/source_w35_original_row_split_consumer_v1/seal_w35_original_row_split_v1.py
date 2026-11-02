"""Seal only this NEW source/synthetic directory; never imports task/runtime."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
R = HERE.parent
T = Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8')
MANIFEST = HERE / 'DELIVERABLES_SHA256_V1.json'
INPUTS = [T / 'rm70_intervals227.py', T / 'positional_rows227.py',
          R / 'source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py',
          R / 'source_a1_frozen_eval_integration_v2/worker_formal_a1_frozen_candidate_v2.py',
          R / 'source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py',
          R / 'source_frozen_eval_microbatch_parent_v1/DELIVERABLES_SHA256_V1.json']
PINS = {
    'rm70_intervals227.py': (14185, 'd84182d3675f41d53d35da54c4d80519b9b2280ccb6d3f47f33cfff64029d609'),
    'positional_rows227.py': (6557, '72627c449b8ce071bcf278027ef1f9fe6a32ab7f2d20910e895fb13bf8f3fd29'),
    'a1_frozen_eval_runtime_v2.py': (37927, '7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e'),
    'worker_formal_a1_frozen_candidate_v2.py': (14962, '4188b7ab43a1e69a457bdf82db7c5c46fe700c1094e96b14eb1415d7349c5b62'),
    'DELIVERABLES_SHA256_V1.json': (5607, '526efd650e1ed63487ba49b6a367670b2a233e1a7d06ec28b41a9da81f21eb11'),
    'w35_original_row_split_consumer_v1.py': (26594, '8b593a95c62981434dc99fc2475f1b7808b30f809109897e54c9db1f7d9ce879'),
    'test_w35_original_row_split_stdlib_v1.py': (21447, 'aedee98a6aba74446fe9f4f90991784dfe0a8ae9f169df8680662c40fc3072d8'),
}


def record(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest(),
                line_count=len(raw.splitlines()))


def put(path, value):
    assert path.parent == HERE and not path.exists(), 'only unused top-level new artifacts'
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf8')


def main():
    assert not MANIFEST.exists(), 'sealed source directory already has manifest; never overwrite'
    inputs = [record(path) for path in INPUTS]
    for value in inputs:
        name = Path(value['path']).name
        if name in PINS:
            assert (value['bytes'], value['SHA256']) == PINS[name], (name, 'source input changed')
    old = json.loads(INPUTS[-1].read_text('utf8'))
    old_verified = []
    old_root = INPUTS[-1].parent
    for value in old['files']:
        path = Path(value['path'])
        assert path.parent == old_root and path.suffix in ('.py', '.json', '.md', '.patch')
        actual = record(path)
        assert (actual['bytes'], actual['SHA256']) == (value['bytes'], value['SHA256']), path
        old_verified.append(actual)
    for name in ('w35_original_row_split_consumer_v1.py', 'test_w35_original_row_split_stdlib_v1.py'):
        value = record(HERE / name)
        assert (value['bytes'], value['SHA256']) == PINS[name], (name, 'published new code changed')
    tests = json.loads((HERE / 'CPU_TEST_RESULTS_V1.json').read_text('utf8'))
    assert tests['passed'] is True and tests['tests'] == 37 and tests['failures'] == tests['errors'] == 0
    assert tests['actual_JSONL_files_read'] == tests['original_PT_NPZ_files_read'] == tests['SDK_Torch_GPU_native_resource_account_operations'] == 0
    own_code = sorted(HERE.glob('*.py'))
    for path in own_code:
        compile(path.read_text('utf8'), str(path), 'exec')
    tree = ast.parse((HERE / 'w35_original_row_split_consumer_v1.py').read_text('utf8'))
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    imports.update(alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names)
    assert imports <= {'__future__', 'argparse', 'collections', 'hashlib', 'json', 'math', 'os', 'pathlib', 'sys'}
    links, final_manifest_links = [], []
    document = (HERE / 'W35_ORIGINAL_ROW_SPLIT_SOURCE_V1.md').read_text('utf8')
    for match in re.finditer(r'\]\(<([^>]+)>\)', document):
        destination = match.group(1)
        base, _, lines = destination.partition('#')
        path = Path(base)
        if path == MANIFEST:
            final_manifest_links.append(destination)
            continue
        assert path.is_file(), ('document link missing', destination)
        if lines:
            nums = re.fullmatch(r'L(\d+)(?:-L(\d+))?', lines)
            assert nums, destination
            start, end = int(nums[1]), int(nums[2] or nums[1])
            assert 1 <= start <= end <= len(path.read_bytes().splitlines()), destination
        links.append(destination)
    fixtures = []
    own_fixtures = HERE / 'CPU_SYNTHETIC_CASES_V1'
    assert own_fixtures.is_dir()
    for path in sorted(own_fixtures.rglob('*')):
        if path.is_file():
            assert path.suffix in ('.json', '.jsonl') and path.is_relative_to(own_fixtures)
            fixtures.append(record(path))
    assert fixtures and len(fixtures) <= 100, 'bounded own synthetic files only'
    put(HERE / 'AUDIT_INPUTS_SHA256_V1.json', dict(kind='BOUNDED_TEXT_SOURCE_INPUTS_ONLY', inputs=inputs,
          original_microbatch_top_files_byte_unchanged=old_verified, actual_raw_or_checkpoint_inputs=0))
    put(HERE / 'OWN_SYNTHETIC_FIXTURES_SHA256_V1.json', dict(kind='OWN_FAKE_CASES_NOT_ACTUAL_EVALUATION', files=fixtures))
    put(HERE / 'SOURCE_REVIEW_VERIFICATION_V1.json', dict(kind='SOURCE_SYNTHETIC_ONLY_W35_SPLIT_VERIFICATION',
          passed=True, completed_tests=tests, frozen_runtime_and_test_pins_unchanged=True,
          original_microbatch_unchanged_files=len(old_verified), compiled_own_source_files=len(own_code),
          consumer_imports=sorted(imports), bounded_source_inputs=len(inputs), checked_document_links=links,
          manifest_link_checked_after_publish=final_manifest_links, own_synthetic_files=len(fixtures),
          actual_RAW_PT_NPZ_SDK_Torch_GPU_SSH_C_account_lock_Git_operations=0,
          old_observer_accepted_or_eval_sources_written=False))
    files = []
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path != MANIFEST:
            value = record(path); value['name'] = path.name; files.append(value)
    canonical = json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8')
    put(MANIFEST, dict(kind='SOURCE_ONLY_SEALED_W35_ORIGINAL_ROW_SPLIT_CONSUMER_V1',
          created_UTC=datetime.now(timezone.utc).isoformat(), files=files,
          canonical_file_records_SHA256=hashlib.sha256(canonical).hexdigest(),
          actual_grading_result=None, old_sources_changed=False))
    assert all(Path(link.partition('#')[0]).is_file() for link in final_manifest_links)
    print(json.dumps(dict(passed=True, runtime=record(HERE / 'w35_original_row_split_consumer_v1.py'),
          manifest=record(MANIFEST), top_level_files=len(files) + 1, tests=37,
          unchanged_old_microbatch_files=len(old_verified), own_synthetic_files=len(fixtures),
          document_links=len(links) + len(final_manifest_links)), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

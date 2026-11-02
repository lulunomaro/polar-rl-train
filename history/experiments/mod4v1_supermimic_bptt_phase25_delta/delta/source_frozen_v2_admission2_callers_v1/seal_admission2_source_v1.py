"""One final source-only seal. Never rerun tests or execute generated callers."""
import ast
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys
import build_frozen_v2_admission2_callers_v1 as B

HERE = Path(__file__).resolve().parent
R = HERE.parent


def H(raw): return hashlib.sha256(raw).hexdigest()


def put(name, value):
    p = HERE / name
    with p.open('x', encoding='utf-8') as stream: json.dump(value, stream, indent=2); stream.write('\n')
    return p


def record(path):
    raw = path.read_bytes()
    return dict(file=path.relative_to(HERE).as_posix(), bytes=len(raw), SHA256=H(raw))


def main():
    assert not (HERE / 'DELIVERABLES_SHA256_V1.json').exists()
    result = json.loads((HERE / 'CPU_TEST_RESULTS_HARDENED_V1.json').read_bytes())
    assert result['testsRun'] == 42 and result['passed'] is True and result['failures'] == result['errors'] == 0
    assert result['actual_caller_or_SSH_SDK_GPU_PT_raw_C_locks_Git_parent_operations'] == 0
    # The normal no-emit builder validates all original source pins, only locally.
    preview = B.build(R, emit=False)
    pins, values = B.load_inputs(); sources, ops = B.render_callers(values)
    canonical = HERE / 'RENDERED_SOURCE_PREVIEW_V1'; canonical.mkdir()
    rendered = B.emit_sources(sources, canonical)
    for row in rendered: row['preview_path'] = 'RENDERED_SOURCE_PREVIEW_V1/' + row['file']
    preview['files'] = rendered
    preview['preview_only_not_root_callers_or_execution'] = True
    put('SOURCE_BUILD_PREVIEW_V1.json', preview)
    chunks = []
    for old, new in zip(B.TEMPLATES, B.OUTPUTS):
        chunks.extend(difflib.unified_diff(values[old].decode('utf-8').splitlines(keepends=True),
            sources[new].splitlines(keepends=True), fromfile=old, tofile=new))
    with (HERE / 'CALLER_WHITELIST_DIFF_V1.patch').open('x', encoding='utf-8', newline='') as f: f.write(''.join(chunks))
    fixtures = []
    for name in ('CPU_SYNTHETIC_CASES_V1', 'CPU_SYNTHETIC_CASES_FINAL_V1', 'CPU_SYNTHETIC_CASES_HARDENED_V1'):
        # Only newly-created and explicitly named fake subtrees inside this scope.
        base = HERE / name
        assert base.is_relative_to(HERE)
        for path in sorted(base.rglob('*')):
            if path.is_file():
                assert path.suffix in ('.py', '.json')
                fixtures.append(record(path))
    put('OWN_SYNTHETIC_FILES_SHA256_V1.json', dict(kind='OWN_FAKE_METADATA_SOURCE_FILES_ONLY', files=fixtures,
        no_native_raw_checkpoints_or_external_traversal=True))
    put('AUDIT_INPUTS_SHA256_V1.json', pins)
    links = []
    md = (HERE / 'USAGE_SOURCE_ADMISSION2_V1.md').read_text(encoding='utf-8')
    for match in re.finditer(r'\]\(<([^>]+)>\)', md):
        target = match.group(1); path_text, _, line = target.partition('#L'); path = Path(path_text)
        assert path.is_relative_to(R) and path.is_file()
        raw = path.read_bytes()
        if line:
            ends = line.split('-L'); last = int(ends[-1]); assert last <= len(raw.splitlines())
        links.append(target)
    own_py = [HERE / n for n in ('capture_source_inputs_v1.py', 'build_frozen_v2_admission2_callers_v1.py',
        'test_admission2_callers_stdlib_v1.py', 'seal_admission2_source_v1.py')]
    for path in own_py: compile(path.read_bytes(), str(path), 'exec')
    for name, source in sources.items(): compile(source, name, 'exec')
    assert not any(x in sys.modules for x in ('torch', 'isaacsim', 'omni', 'paramiko', 'project_connector'))
    assert all(not (R / name).exists() for name in B.OUTPUTS)
    put('SOURCE_REVIEW_VERIFICATION_V1.json', dict(passed=True, original_explicit_inputs=len(pins['files']),
        original_source_payload_PINS_unchanged=len(pins['verified_unchanged_payload14']), own_py_compiled_not_executed=len(own_py),
        rendered_callers_compiled_not_executed=len(sources), whitelist_restores_original_bytes_and_whole_AST=True,
        remote_parent_launch_body_identical_except_outer_request_metadata=True,
        doc_links_and_line_ranges_valid=len(links), test_receipt='CPU_TEST_RESULTS_HARDENED_V1.json', testsRun=42,
        caller_files_at_project_root_emitted=False, actual_release_or_admission_or_skill=None,
        SSH_SDK_GPU_PT_raw_C_locks_Git_parent_or_caller_operations=0))
    top_names = (
        'capture_source_inputs_v1.py', 'build_frozen_v2_admission2_callers_v1.py',
        'test_admission2_callers_stdlib_v1.py', 'seal_admission2_source_v1.py',
        'USAGE_SOURCE_ADMISSION2_V1.md', 'CPU_SOURCE_TEST_HISTORY_V1.json',
        'CPU_TEST_RESULTS_V1.json', 'CPU_TEST_RESULTS_FINAL_V1.json', 'CPU_TEST_RESULTS_HARDENED_V1.json',
        'SOURCE_BUILD_PREVIEW_V1.json', 'CALLER_WHITELIST_DIFF_V1.patch',
        'OWN_SYNTHETIC_FILES_SHA256_V1.json', 'AUDIT_INPUTS_SHA256_V1.json', 'SOURCE_REVIEW_VERIFICATION_V1.json')
    paths = [HERE / n for n in top_names]
    paths += [canonical / n for n in B.OUTPUTS]
    paths += [B.SNAPSHOT / 'INPUT_PINS.json'] + [B.SNAPSHOT / row['relative'] for row in pins['files']]
    entries = [record(p) for p in paths]
    encoded = json.dumps(entries, sort_keys=True, separators=(',', ':')).encode('utf-8')
    manifest = dict(kind='SEALED_SOURCE_ONLY_FROZEN_V2_ADMISSION2_FOUR_CALLERS_V1',
        created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), files=entries,
        bundle_SHA256=H(encoded), self_excluded=True, own_fake_files_index='OWN_SYNTHETIC_FILES_SHA256_V1.json',
        testsRun=42, tests_passed=True, actual_release_or_admission_or_skill=None,
        unchanged_original_stage_PIN=B.STAGE_PIN, unchanged_original_index_PIN=B.INDEX_PIN,
        unchanged_original_parent_PIN=B.PARENT_PIN, original_four_templates_and_fourteen_payload_unchanged=True,
        all_changes_inside_new_scope=True, root_callers_emitted_by_child=False)
    p = put('DELIVERABLES_SHA256_V1.json', manifest)
    print(json.dumps(dict(passed=True, deliverable_entries=len(entries), own_fake_files=len(fixtures),
        manifest_bytes=len(p.read_bytes()), manifest_SHA256=H(p.read_bytes()), bundle_SHA256=manifest['bundle_SHA256'],
        builder=record(HERE / 'build_frozen_v2_admission2_callers_v1.py'), rendered=rendered,
        test_count=42, actual_release_or_admission=None, root_callers_emitted=False), indent=2))


if __name__ == '__main__': main()

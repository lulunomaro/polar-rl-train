"""One-shot small-source seal; no stage, parent import, test rerun or native access."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import zipfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
H = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    cli = (HERE / 'stage_a1_microbatch_eval_v2.py').read_bytes()
    index_raw = (HERE / 'MICROBATCH_STAGE_INDEX_V2.json').read_bytes()
    tests_raw = (HERE / 'TEST_RESULTS_CLOSE_DEPENDENCY_V2.json').read_bytes()
    index, tests = json.loads(index_raw), json.loads(tests_raw)
    assert (len(cli), H(cli)) == (32953, '9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952')
    assert (len(index_raw), H(index_raw)) == (4886, '69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50')
    assert tests['passed'] is True and tests['tests_run'] == 8 and not tests['torch_imported']
    assert tests['actual_native_stage_dispatch_or_SDK_C_PT_operations'] == 0
    previous = PROJECT / 'source_stage_a1_microbatch_eval_v1' / 'stage_a1_microbatch_eval_v1.py'
    old_cli = previous.read_bytes()
    assert (len(old_cli), H(old_cli)) == (29335, 'dff8143d2464f82f720497ddfe4c241cfd4846e938a9f975962defdaac8c893b')
    old_index = (PROJECT / 'source_frozen_eval_microbatch_parent_v1' / 'MICROBATCH_STAGE_INDEX_V1.json').read_bytes()
    assert (len(old_index), H(old_index)) == (4529, '42e4714c8adf4361351e052d4006f863452fbad557343cc22f9dbad21951beaf')
    assert index['entries'][:13] == json.loads(old_index)['entries']
    members = {}
    for entry in index['entries']:
        path = Path(entry['path']); assert path.suffix == '.py'
        raw = path.read_bytes(); assert (len(raw), H(raw)) == (entry['bytes'], entry['SHA256'])
        name = 'flat/' + path.name; assert name not in members
        ast.parse(raw); compile(raw, str(path), 'exec')
        members[name] = raw
    assert len(members) == 14
    for path in HERE.glob('*.py'):
        raw = path.read_bytes(); ast.parse(raw); compile(raw, str(path), 'exec')
    delta = ''.join(difflib.unified_diff(old_cli.decode().splitlines(True), cli.decode().splitlines(True),
        fromfile='SEALED_V1/stage_a1_microbatch_eval_v1.py', tofile='NEW_V2/stage_a1_microbatch_eval_v2.py')).encode()
    patch_path = HERE / 'STAGER_V2_WHITELIST_DELTA.patch'
    with patch_path.open('xb') as stream: stream.write(delta)
    artifacts = {}
    names = ['stage_a1_microbatch_eval_v2.py', 'MICROBATCH_STAGE_INDEX_V2.json',
        'MICROBATCH_CLOSE_DEPENDENCY_STAGE_V2.md', 'TEST_RESULTS_CLOSE_DEPENDENCY_V2.json',
        'test_close_dependency_stage_v2.py', 'build_source_stage_microbatch_v2.py',
        'V2_DELTA_SOURCE_AUTHORING_RECEIPT.json', 'STAGER_V2_WHITELIST_DELTA.patch',
        'seal_stage_close_dependency_v2.py']
    for name in names:
        raw = (HERE / name).read_bytes()
        artifacts[name] = dict(path=str(HERE / name), bytes=len(raw), SHA256=H(raw))
    delivery = dict(kind='V2_SOURCE_ONLY_FOURTEENTH_CLOSE_DEPENDENCY_DELIVERY_NOT_INSTALLED',
        original_thirteen_index_unchanged=dict(bytes=len(old_index), SHA256=H(old_index)),
        original_V1_stager_unchanged=dict(bytes=len(old_cli), SHA256=H(old_cli)),
        original_thirteen_entries_unchanged=True, source_mappings=14,
        dependency=index['entries'][-1], artifacts=artifacts,
        original_runtime_thirteen_required_aliases_kept_as_subset=True,
        original_actor_models_accepted_physics_resource_parent_sources_unchanged=True,
        tests_new_only=tests, actual_native_App_close=None, actual_new_stage_dispatch=None,
        actual_effect_or_paired_reference_or_UID_cache_alignment=None,
        original_failed_eval_root_errors_retained=True)
    delivery_path = HERE / 'STAGER_SOURCE_DELIVERY_V2.json'
    delivery_raw = (json.dumps(delivery, indent=2) + '\n').encode()
    with delivery_path.open('xb') as stream: stream.write(delivery_raw)
    for name in ('stage_a1_microbatch_eval_v2.py', 'MICROBATCH_STAGE_INDEX_V2.json',
                 'MICROBATCH_CLOSE_DEPENDENCY_STAGE_V2.md', 'TEST_RESULTS_CLOSE_DEPENDENCY_V2.json'):
        members[name] = (HERE / name).read_bytes()
    members[delivery_path.name] = delivery_raw
    assert len(members) == 19
    bundle = HERE / 'MICROBATCH_STAGER_SMALL_SOURCE_BUNDLE_V2.zip'
    with zipfile.ZipFile(bundle, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in members.items(): archive.writestr(name, raw)
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None and set(archive.namelist()) == set(members)
        assert all(archive.read(name) == raw for name, raw in members.items())
    names += [delivery_path.name, bundle.name]
    final_rows = []
    for name in names:
        path = HERE / name; raw = path.read_bytes()
        final_rows.append(dict(path=str(path), bytes=len(raw), SHA256=H(raw)))
    inventory = HERE / 'SHA256_STAGER_DELIVERY_V2.txt'
    with inventory.open('x', encoding='utf-8', newline='\n') as stream:
        for row in final_rows: stream.write('{SHA256}  {bytes}  {path}\n'.format(**row))
    print(json.dumps(dict(passed=True, original_thirteen_identical=True, original_old_stager_index_unchanged=True,
        bundle_members=len(members), ZIP_CRC_and_all_member_bytes_match=True, tests_new_only=8,
        actual_native_operations=0, files=final_rows), indent=2))


if __name__ == '__main__': main()

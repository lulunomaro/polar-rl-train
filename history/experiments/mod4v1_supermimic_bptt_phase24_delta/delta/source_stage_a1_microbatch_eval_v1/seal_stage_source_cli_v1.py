"""One-shot LOCAL small-source package only. No native directory/PT/SDK/resources."""
from pathlib import Path
import ast
import hashlib
import json
import sys
import zipfile

HERE = Path(__file__).resolve().parent
PIN = (29335, 'dff8143d2464f82f720497ddfe4c241cfd4846e938a9f975962defdaac8c893b')
INDEX_PIN = (4529, '42e4714c8adf4361351e052d4006f863452fbad557343cc22f9dbad21951beaf')


def h(raw): return hashlib.sha256(raw).hexdigest()
def identity(path):
    raw = Path(path).read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA256=h(raw))
def put_once(path, value):
    with Path(path).open('xb') as stream:
        stream.write((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def main():
    cli = HERE / 'stage_a1_microbatch_eval_v1.py'
    raw = cli.read_bytes(); assert (len(raw), h(raw)) == PIN
    for name in ('stage_a1_microbatch_eval_v1.py', 'test_stage_a1_microbatch_stdlib_v1.py', 'seal_stage_source_cli_v1.py'):
        content = (HERE / name).read_bytes(); ast.parse(content); compile(content, str(HERE / name), 'exec')
    tests = json.loads((HERE / 'TEST_RESULTS_STDLIB_STAGER_V1.json').read_bytes())
    assert tests['passed'] is True and tests['tests_run'] == 20 and not tests['torch_imported']
    source_index = HERE.parent / 'source_frozen_eval_microbatch_parent_v1' / 'MICROBATCH_STAGE_INDEX_V1.json'
    index_raw = source_index.read_bytes(); assert (len(index_raw), h(index_raw)) == INDEX_PIN
    index = json.loads(index_raw); assert len(index['entries']) == 13
    members = {}; names = set(); aliases = set()
    for item in index['entries']:
        basename = item['path'].replace('\\', '/').rsplit('/', 1)[-1]
        assert basename not in names and item['relative'] not in aliases
        names.add(basename); aliases.add(item['relative'])
        data = Path(item['path']).read_bytes()
        assert (len(data), h(data)) == (item['bytes'], item['SHA256']); ast.parse(data)
        members['flat_sources/' + basename] = data
    for name in ('stage_a1_microbatch_eval_v1.py', 'MICROBATCH_STAGE_CLI_V1.md', 'TEST_RESULTS_STDLIB_STAGER_V1.json'):
        members[name] = (HERE / name).read_bytes()
    members['MICROBATCH_STAGE_INDEX_V1.json'] = index_raw
    manifest = dict(kind='SMALL_SOURCE_UPLOAD_BUNDLE_ONLY_NOT_STAGE_OR_DISPATCH_V1',
        files=[dict(relative=name, bytes=len(data), SHA256=h(data)) for name, data in sorted(members.items())],
        index_provenance_paths_not_dereferenced_on_Linux=True, flat_source_count=13,
        source_only=True, native_stage_dispatch_PT_C_locks_SDK_GPU_operations=0)
    members['SOURCE_BUNDLE_MANIFEST_V1.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    archive = HERE / 'MICROBATCH_STAGER_SMALL_SOURCE_BUNDLE_V1.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as package:
        for name, data in sorted(members.items()): package.writestr(name, data)
    with zipfile.ZipFile(archive) as package:
        assert package.testzip() is None and len(package.namelist()) == 18
        for name, data in members.items(): assert package.read(name) == data
    provenance = dict(kind='SEALED_SOURCE_MICROBATCH_STAGER_DELIVERY_V1',
        CLI=identity(cli), bundle=identity(archive), bundle_members=18,
        original_index=dict(**identity(source_index), expected_PIN=list(INDEX_PIN)),
        inputs_are_thirteen_sealed_sources_only=True,
        original_index_unchanged=True, no_old_source_edits=True,
        tests=tests, full_source_compile=True, runtime_operations=None,
        actual_native_stage=False, actual_dispatch=False, actual_frozen_evaluation=None,
        actual_model_source_or_cache_load=None, comparison=None, overall_eight_pass_rate=None)
    put_once(HERE / 'STAGER_SOURCE_DELIVERY_V1.json', provenance)
    inventory = [HERE / name for name in ('stage_a1_microbatch_eval_v1.py', 'test_stage_a1_microbatch_stdlib_v1.py',
        'MICROBATCH_STAGE_CLI_V1.md', 'TEST_RESULTS_STDLIB_STAGER_V1.json', 'seal_stage_source_cli_v1.py',
        'MICROBATCH_STAGER_SMALL_SOURCE_BUNDLE_V1.zip', 'STAGER_SOURCE_DELIVERY_V1.json')]
    with (HERE / 'SHA256_STAGER_DELIVERY_V1.txt').open('x', encoding='utf-8') as stream:
        for path in inventory:
            item = identity(path); stream.write('%s  %d  %s\n' % (item['SHA256'], item['bytes'], item['path']))
    print(json.dumps(provenance, indent=2))


if __name__ == '__main__': main()

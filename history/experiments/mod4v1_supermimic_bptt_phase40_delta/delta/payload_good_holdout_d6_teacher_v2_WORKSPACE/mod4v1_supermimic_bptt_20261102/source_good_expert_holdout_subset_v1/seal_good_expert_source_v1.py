"""Seal/verify only the explicit NEW source files and indexed text dependencies.
No native import, model/static/raw read, stage, subprocess, lock or execution of
parent/worker is performed. Existing seals are verified, never replaced.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
NAMES = (
    'API_CONTRACT_GOOD_EXPERT_HOLDOUT_V1.json',
    'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json',
    'SOURCE_REVIEW_GOOD_EXPERT_HOLDOUT_V1.md',
    'TEST_REPORT_GOOD_EXPERT_HOLDOUT_V1.json',
    'build_source_manifest_v1.py',
    'derive_holdout_sources_v1.py',
    'e1_good_expert_holdout_bridge_v1.py',
    'e1_good_expert_holdout_factories_v1.py',
    'e1_good_expert_holdout_worker_v1.py',
    'good_expert_holdout_runtime_v1.py',
    'holdout_protocol_components_v1.py',
    'seal_good_expert_source_v1.py',
    'single_gpu_good_expert_holdout_parent_v1.py',
    'test_good_expert_holdout_stdlib_v1.py',
)
SEAL_NAME = 'GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json'


def text_digest(path):
    path = Path(path)
    assert path.suffix.lower() in ('.py', '.json', '.md'), path
    value = path.read_bytes()
    if path.suffix == '.py':
        ast.parse(value.decode('utf-8-sig'), filename=str(path))
    return dict(bytes=len(value), SHA256=hashlib.sha256(value).hexdigest())


def main():
    assert sys.argv[1:] in ([], ['--verify']), 'only optional --verify is supported'
    index = json.loads((HERE / NAMES[1]).read_text(encoding='utf-8'))
    report = json.loads((HERE / NAMES[3]).read_text(encoding='utf-8'))
    assert index['kind'] == 'SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_C878_S135_INDEX_V1'
    assert len(index['overlay_entries']) == 20
    assert report['passed'] and report['tests_run'] == 21 and not report['errors'] and not report['failures']
    assert not any(report['audit'].values())
    for state in (index, report):
        assert all(state[key] is False for key in ('enabled', 'staged', 'dispatched'))
    dependencies = index['overlay_entries'] + index['inherited_original_worker_source_entries']
    for row in dependencies:
        assert text_digest(row['path']) == dict(bytes=row['bytes'], SHA256=row['SHA256']), row['path']
    files = [dict(name=name, **text_digest(HERE / name)) for name in sorted(NAMES)]
    records = ''.join(f"{row['name']}\t{row['bytes']}\t{row['SHA256']}\n" for row in files)
    seal = dict(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_IMMUTABLE_SEAL_V1',
                enabled=False, staged=False, dispatched=False, native_measurement=False,
                root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',
                root_SHA256=hashlib.sha256(records.encode('utf-8')).hexdigest(),
                files=files, indexed_text_dependencies_verified=len(dependencies),
                canonical_runtime_SHA256='7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e')
    target = HERE / SEAL_NAME
    if target.exists():
        assert json.loads(target.read_text(encoding='utf-8')) == seal, 'sealed content changed: create NEW version'
        mode = 'SOURCE_SEAL_VERIFIED_NO_WRITES'
    else:
        assert '--verify' not in sys.argv, 'source seal missing'
        with target.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(seal, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        mode = 'SOURCE_SEAL_CREATED_NOT_STAGE'
    print(json.dumps(dict(kind=mode, root_SHA256=seal['root_SHA256'], files=len(files),
                         indexed_text_dependencies_verified=len(dependencies),
                         enabled=False, staged=False, dispatched=False), sort_keys=True))


if __name__ == '__main__':
    main()

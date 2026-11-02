"""One-shot small SOURCE payload ZIP; no native/static-tree stage or dispatcher call."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

HERE = Path(__file__).resolve().parent


def sha(raw): return hashlib.sha256(raw).hexdigest()


def main():
    seal = json.loads((HERE / 'V6_SOURCE_PROVENANCE_AND_SEAL.json').read_bytes())
    assert seal['passed'] is True and seal['tests_distinct'] == 103
    index_path = HERE / '_SOURCE_INPUT/SEALED_A1_SOURCE_INDEX_V6.json'
    index = json.loads(index_path.read_bytes())
    assert index['sealed'] is True and index['kind'] == 'SEALED_A1_NATIVE_V6_SOURCE_INDEX_V1'
    names = ['stage_a1_native_v6.py', 'dispatch_a1_native_v6_once.py', 'V6_STAGE_CLI_AND_STATUS.md',
        'V6_SOURCE_PROVENANCE_AND_SEAL.json', '_SOURCE_INPUT/SEALED_A1_SOURCE_INDEX_V6.json']
    for row in index['files']:
        rel = row['source_relative']
        assert not PurePosixPath(rel).is_absolute() and '..' not in PurePosixPath(rel).parts
        name = '_SOURCE_INPUT/' + rel
        raw = (HERE / name).read_bytes()
        assert sha(raw) == row['SHA'] and len(raw) == row['bytes']
        names.append(name)
    assert len(index['files']) == 14 and len(names) == len(set(names))
    members = [];materials = []
    for name in names:
        path = HERE / name
        assert path.resolve(strict=True).is_relative_to(HERE) and not path.is_symlink()
        raw = path.read_bytes();materials.append((name, raw))
        members.append(dict(relative=name, SHA=sha(raw), bytes=len(raw)))
    manifest = dict(kind='NEW_V6_PARENT_SMALL_SOURCE_INPUT_ONLY_NOT_NATIVE_STAGE',
        files=members, fourteen_source_index_SHA=sha(index_path.read_bytes()),
        changed_runtime_source_pins=2, unchanged_owner_worker_shim=True,
        actual_stage_dispatch_SDK_GPU_originalPT_C_locks_Git_SSH_operations=0,
        parent_must_use_NEW_root_and_explicit_original_owner_gates=True)
    raw_manifest = (json.dumps(manifest, indent=2) + '\n').encode()
    manifest_name = 'PARENT_SOURCE_PAYLOAD_MANIFEST_V6.json'
    with (HERE / manifest_name).open('xb') as stream: stream.write(raw_manifest)
    archive = HERE / 'V6_PARENT_SMALL_SOURCE_PAYLOAD.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, raw in materials: output.writestr(name, raw)
        output.writestr(manifest_name, raw_manifest)
    with zipfile.ZipFile(archive, 'r') as checked:
        assert checked.testzip() is None
        for row in members:
            raw = checked.read(row['relative'])
            assert sha(raw) == row['SHA'] and len(raw) == row['bytes']
        assert checked.read(manifest_name) == raw_manifest
        count = len(checked.namelist())
    raw = archive.read_bytes()
    receipt = dict(kind='NEW_V6_SMALL_SOURCE_ZIP_COMPLETE_NOT_NATIVE_EXECUTION',
        passed=True, path=str(archive), SHA=sha(raw), bytes=len(raw), members=count,
        contents_manifest_SHA=sha(raw_manifest), source_index_SHA=sha(index_path.read_bytes()),
        actual_stage_dispatch_SDK_GPU_originalPT_C_locks_Git_SSH_operations=0)
    with (HERE / 'PARENT_SMALL_PAYLOAD_RECEIPT_V6.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(receipt, stream, indent=2);stream.write('\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__': main()

"""Read-only verification of this NEW textual SOURCE package; no entry imports."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def verify():
    seal_raw = (HERE / 'SOURCE_SEAL.json').read_bytes()
    seal = json.loads(seal_raw)
    assert seal['kind'] == 'PHASE1_TYPED_CAPTURE_MATERIALIZER_SOURCE_SEAL_V1'
    rows = seal['files']
    assert type(rows) is list and len(rows) == seal['member_count']
    names = set()
    python_files = 0
    json_files = 0
    for row in rows:
        relative = row['relative']
        p = PurePosixPath(relative)
        assert type(relative) is str and not p.is_absolute() and p.parts == (relative,)
        assert relative not in names and relative != 'SOURCE_SEAL.json'
        assert not any(c in relative for c in ('\\', ':')) and relative not in ('.', '..')
        assert p.suffix.lower() in ('.py', '.json', '.md', '.txt')
        names.add(relative)
        path = HERE / relative
        assert not path.is_symlink() and path.is_file()
        raw = path.read_bytes()
        assert (len(raw), H(raw)) == (row['bytes'], row['SHA256']), relative
        if p.suffix == '.py':
            ast.parse(raw.decode('utf-8-sig'), filename=str(path))
            python_files += 1
        elif p.suffix == '.json':
            json.loads(raw)
            json_files += 1
    canonical = json.dumps(rows, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    assert H(canonical) == seal['content_root_SHA256']
    assert {p.name for p in HERE.iterdir()} == names | {'SOURCE_SEAL.json'}
    index = json.loads((HERE / 'SOURCE_INDEX.json').read_bytes())
    assert index['kind'] == 'PHASE1_TYPED_CAPTURE_MATERIALIZER_SOURCE_INDEX_V1'
    for name, pin in index['own_python_sources'].items():
        raw = (HERE / name).read_bytes()
        assert (len(raw), H(raw)) == (pin['bytes'], pin['SHA256'])
    receipt = json.loads((HERE / 'SOURCE_TEST_RECEIPT_attempt4.json').read_bytes())
    assert receipt['tests_run'] == 9 and receipt['passed'] and not receipt['audit_violations']
    assert receipt['immutable_old_source_before_after_equal'] and receipt['immutable_old_source_inputs'] == 407
    for name, pin in receipt['tested_source_files'].items():
        raw = (HERE / name).read_bytes()
        assert (len(raw), H(raw)) == (pin['bytes'], pin['SHA256']), name
    assert not index['actual_prepare_calls'] and not index['actual_stage_calls']
    assert not index['native_enabled'] and not index['exact'] and index['gate1'] == 'UNKNOWN'
    return dict(kind='READONLY_TYPED_MATERIALIZER_SOURCE_SEAL_VERIFICATION_V1', passed=True,
        members=len(rows), files_including_seal=len(rows)+1, Python_AST_files=python_files,
        JSON_files=json_files, seal_bytes=len(seal_raw), seal_SHA256=H(seal_raw),
        content_root_SHA256=seal['content_root_SHA256'],
        materialized=False, parent_launches=0, native_enabled=False, exact=False,
        gate1='UNKNOWN', stage2_GO=False)


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False))

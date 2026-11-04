"""Read-only V2 member/index/test pin verification; never import entries."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
H=lambda raw:hashlib.sha256(raw).hexdigest()


def pin(path):
    raw=Path(path).read_bytes()
    return dict(bytes=len(raw),SHA256=H(raw))


def main():
    seal_raw=(HERE/'SOURCE_SEAL.json').read_bytes();seal=json.loads(seal_raw)
    assert seal['kind']=='PHASE1_TYPED_CAPTURE_MATERIALIZER_SOURCE_SEAL_V2'
    assert seal['materializer_source_publication']==2 and seal['source_only'] is True
    rows=seal['files'];assert type(rows) is list and len(rows)==seal['member_count']==18
    assert len({r['relative'] for r in rows})==18
    assert {p.name for p in HERE.iterdir()}=={r['relative'] for r in rows}|{'SOURCE_SEAL.json'}
    assert H(json.dumps(rows,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==seal['content_root_SHA256']
    py=js=0
    for row in rows:
        rel=row['relative'];assert type(rel) is str and '/' not in rel and '\\' not in rel and rel not in ('.','..')
        path=HERE/rel;assert not path.is_symlink() and path.is_file()
        raw=path.read_bytes();assert (len(raw),H(raw))==(row['bytes'],row['SHA256'])
        if path.suffix=='.py':ast.parse(raw,filename=str(path));py+=1
        elif path.suffix=='.json':json.loads(raw);js+=1
    index=json.loads((HERE/'SOURCE_INDEX.json').read_bytes())
    assert index['kind']=='PHASE1_TYPED_CAPTURE_MATERIALIZER_SOURCE_INDEX_V2' and index['source_version']==2
    assert len(index['own_python_sources'])==9
    for name,value in index['own_python_sources'].items():assert pin(HERE/name)==value
    receipt=json.loads((HERE/'SOURCE_TEST_RECEIPT_attempt1.json').read_bytes())
    assert receipt['passed'] is True and receipt['tests_run']==6 and not receipt['audit_violations']
    for name,value in receipt['tested_source_files'].items():assert pin(HERE/name)==value
    assert receipt['old_pinned_text_sources_before']==receipt['old_pinned_text_sources_after']
    assert receipt['old_pinned_text_sources_after']['count']==436
    assert pin(HERE/'SOURCE_MIRROR_INPUTS.json')==dict(bytes=93889,SHA256='c47b837bce45d3fa3c917db437181ee83814feef0ca0c2b67df4f0c6f49d9d90')
    assert index['finite_active_source_binding']['complete_aliases']==34
    assert index['derivation']['entire_source_and_AST_same_vs_typed_V1']==13
    assert index['shared_helpers']['complete_functions']==17
    for field in ('materialized','native_enabled','exact','stage2_GO'):
        assert seal[field] is False and index[field] is False
    assert seal['gate1']==index['gate1']=='UNKNOWN' and seal['parent_launches']==index['parent_launches']==0
    print(json.dumps(dict(kind='READONLY_TYPED_MATERIALIZER_SOURCE_SEAL_VERIFICATION_V2',passed=True,
        members=18,files_including_seal=19,Python_AST_files=py,JSON_files=js,
        seal_bytes=len(seal_raw),seal_SHA256=H(seal_raw),content_root_SHA256=seal['content_root_SHA256'],
        materialized=False,parent_launches=0,native_enabled=False,exact=False,gate1='UNKNOWN',stage2_GO=False)))


if __name__=='__main__':
    main()

"""Local only: exact71-file transfer payload; no transport, model or network."""
import base64
import hashlib
import json
from pathlib import Path
import time

B=Path(__file__).resolve().parent
Z=B.parents[1]
M=Z/'method_agent'
idxpath=M/'reports/REPRODUCIBILITY_INDEX_V2.json'
rawindex=idxpath.read_bytes()
idx=json.loads(rawindex)
assert len(idx['files'])==70
entries=[]
for row in idx['files']:
    rel=row['relative_path']
    p=M/rel
    assert p.resolve().is_relative_to(M.resolve()) and '__pycache__' not in p.parts
    data=p.read_bytes()
    assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    entries.append(dict(relative=rel,bytes=len(data),sha256=row['sha256'],base64=base64.b64encode(data).decode()))
entries.append(dict(relative='reports/REPRODUCIBILITY_INDEX_V2.json',bytes=len(rawindex),
    sha256=hashlib.sha256(rawindex).hexdigest(),base64=base64.b64encode(rawindex).decode()))
actual={p.relative_to(M).as_posix() for p in M.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert actual=={row['relative'] for row in entries} and len(entries)==71
payload=dict(schema_version=1,id='MOE_METHOD_EXACT71_TRANSFER_PAYLOAD_V1',epoch=time.time(),
    root='/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025',
    destination='method_bundle',index_sha256=hashlib.sha256(rawindex).hexdigest(),
    file_count=len(entries),total_bytes=sum(row['bytes'] for row in entries),files=entries,
    includes_old_H1_directories=False,transport_executed=False,archive_status='PENDING_ROOT_GIT')
out=B/'METHOD_TRANSFER_PAYLOAD.json'
with out.open('x',encoding='utf-8') as stream:json.dump(payload,stream,separators=(',',':'))
report=dict(id='LOCAL_BUILD_METHOD_EXACT71_PAYLOAD_V1',epoch=time.time(),
    payload_path=str(out),payload_bytes=out.stat().st_size,payload_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
    file_count=len(entries),source_total_bytes=payload['total_bytes'],index_excludes_self_rows=70,
    final_index_itself_included=True,all_source_hashes_verified=True,remote_connection=False,
    training_ready=False,archive_status='PENDING_ROOT_GIT')
with (B/'reports/LOCAL_METHOD_PAYLOAD_BUILD_V1_ACTUAL.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
print(json.dumps(report))

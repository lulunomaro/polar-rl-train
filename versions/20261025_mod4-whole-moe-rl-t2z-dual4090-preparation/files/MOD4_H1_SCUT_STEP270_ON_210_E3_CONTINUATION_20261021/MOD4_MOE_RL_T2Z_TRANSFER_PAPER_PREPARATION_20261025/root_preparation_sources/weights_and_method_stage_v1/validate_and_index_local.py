"""Local-only helper QA and append-only index, no remote or model execution."""
import ast
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import time

B=Path(__file__).resolve().parent;Z=B.parents[1]
records=[]
for p in B.glob('*.py'):
    ast.parse(p.read_text(encoding='utf-8-sig'))
    records.append(dict(check='PYTHON_AST',file=p.name,status='PASS'))
spec=importlib.util.spec_from_file_location('reviewed_helper',B/'remote_stage_helper.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
payload=json.loads((B/'METHOD_TRANSFER_PAYLOAD.json').read_text())
assert payload['file_count']==71 and payload['total_bytes']==690537
assert payload['index_sha256']==mod.METHOD_INDEX_SHA
for row in payload['files']:
    data=base64.b64decode(row['base64'],validate=True)
    assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    p=Z/'method_agent'/row['relative']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    mod._safe_relative(row['relative'])
records.append(dict(check='ALL71_METHOD_PAYLOAD_SOURCE_BYTES_SHA_AND_PATHS',status='PASS'))
for bad in ('/absolute','../escape','a/../../escape','a\\b','C:/outside','', '.'):
    try:mod._safe_relative(bad)
    except RuntimeError:pass
    else:raise AssertionError('Unsafe relative path not rejected: '+bad)
records.append(dict(check='SEVEN_UNSAFE_PATH_NEGATIVES',status='PASS'))
for rel,sha in mod.ENGINEERING_SHA.items():
    assert hashlib.sha256((Z/'engineering_agent'/rel).read_bytes()).hexdigest()==sha
records.append(dict(check='FIVE_FROZEN_ENGINEERING_SOURCE_SHA_BINDINGS',status='PASS'))
bridge=ast.parse((Z/'method_agent/upstream_bridge.py').read_text())
required=next(ast.literal_eval(n.value) for n in bridge.body if isinstance(n,ast.Assign)
              and any(isinstance(x,ast.Name) and x.id=='REQUIRED_HASHES' for x in n.targets))
old=Z.parent/'MOD4_T2Z_H1_TRANSFER_PAPER_PREPARATION_20261025/method_agent/integration_v1/upstream_source_receipts'
for path,sha in required.items():
    p=old/(path.replace('/','__')+'.txt')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
records.append(dict(check='METHOD_EXPECTED_FIXED_SOURCE_SHA_MATCHES_RETAINED_PRIMARY_TEXT',status='PASS',
    old_H1_transferred=False,remote_fixed_checkout_not_rechecked_by_this_local_QA=True))
report=dict(id='WEIGHTS_METHOD_HELPER_LOCAL_QA_V1',epoch=time.time(),status='PASS_LOCAL_SOURCE_ONLY',records=records,
    remote_connection=False,remote_helper_invoked=False,CPU_method_tests_executed=False,
    weights_downloaded=False,GPU_used=False,training_started=False,training_ready=False,
    next_owner='root only; user temporarily bans new subagents after this round',archive_status='PENDING_ROOT_GIT')
out=B/'reports/LOCAL_HELPER_QA_V1_ACTUAL.json'
with out.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
files=[]
for p in sorted(B.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.name=='HELPER_FINAL_INDEX_V1_ACTUAL.json':continue
    raw=p.read_bytes();files.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
idx=B/'reports/HELPER_FINAL_INDEX_V1_ACTUAL.json'
with idx.open('x',encoding='utf-8') as stream:
    json.dump(dict(id='WEIGHTS_METHOD_HELPER_FINAL_LOCAL_INDEX_V1',epoch=time.time(),files=files,
        total_bytes=sum(x['bytes'] for x in files),index_self_excluded=True,archive_status='PENDING_ROOT_GIT',
        transport_executed=False,training_ready=False,no_auto_followup_or_subdelegation=True),stream,indent=2)
print(json.dumps(dict(status=report['status'],checks=len(records),files_excluding_index=len(files),index=str(idx))))

"""Append-only first collector schema failure evidence. No capture retry, source refresh or raw access."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;A=D/'revisions/capture_attempt_01'
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
assert not A.exists();A.mkdir(parents=True)
names=['capture_source_once.py','capture_source_01.log','CAPTURE_FIRST_STOP.json','CAPTURE_STARTED.json','FILESET_ALLOWLIST.json','PREPARATION_MINIMUM_INITIAL.json'];copies=[]
for n in names:
 p=D/n;b=p.read_bytes()
 with(A/n).open('xb')as f:f.write(b)
 x=rec(p);y=rec(A/n);assert x['SHA']==y['SHA']and x['bytes']==y['bytes'];copies.append(dict(original=x,archived=y))
prefix=json.loads((D/'CAPTURE_FIRST_STOP.json').read_bytes());assert len(prefix['copied_text_records'])==prefix['counts']['snapshot_files']==798
v=dict(status='PRESERVED_FIRST_COLLECTOR_SCHEMA_ERROR_AFTER_COPY_NOT_SOURCE_OR_ROBOT_FAILURE',failed_source=rec(D/'capture_source_once.py'),complete_merged_stderr_log=rec(D/'capture_source_01.log'),prefix=rec(D/'CAPTURE_FIRST_STOP.json'),copies=copies,error_line=150,wrong_original_expression="gate=result.get('proposed_gate',{}); ... gate.get('passed')is False",actual_saved_required_field='startup_stand_original_v1_gate',new_saved_reader_requires_exact_bool_false=True,original_snapshots_copied=798,copied_bytes=17739938,original_CAPTURE_not_modified_or_rerun=True,unsealed_before_stop=['SOURCE_MANIFEST','CASE_AND_TARGET_REGISTRY','refs/claim resolutions','sourceafterpins','INDEX','finalreceipt'],raw_or_binary_payload_opens=0,raw_or_binary_payload_hashes=0,Git_mutation=0,permission='Parent2026-11-04 06:50:42 NEW saved-only closure from798 snapshots/allowedprior metadata/ParentExpected; no original source recapture/refresh/mapQA',active_V6_V7_C18_excluded=True)
with(D/'SOURCE_CAPTURE_SCHEMA_FAILURE_RECEIPT_001.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(dict(status=v['status'],archive_files=len(copies),copied_text_records=798,raw_payload=0,failed_source_SHA=v['failed_source']['SHA'])))

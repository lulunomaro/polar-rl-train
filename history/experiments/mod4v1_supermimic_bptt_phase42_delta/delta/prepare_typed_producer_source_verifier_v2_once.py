"""Preserve the parent driver's spelling failure; derive a fresh source verifier."""
from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;src=R/'verify_phase1_typed_producer_frozen_source_once.py';dst=R/'verify_phase1_typed_producer_frozen_source_v2_once.py';err=R/'reports/PHASE1_TYPED_PRODUCER_FROZEN_SOURCE_VERIFIER_PRECASE_ENCODING_FAILURE_V1.json';assert not dst.exists()and not err.exists()and(R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_STARTED_V1.json').exists()and not(R/'reports/PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_VERIFY_V1.json').exists();b=src.read_bytes();s=b.decode('utf-8');t=s
for old,new in [("'utf8-sig'","'utf-8-sig'"),('PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_VERIFY_V1.json','PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_VERIFY_V2.json'),('PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_STARTED_V1.json','PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_STARTED_V2.json'),('PARENT_READONLY_TYPED_PRODUCER_FROZEN_SOURCE_IDENTITY_VERIFY_V1','PARENT_READONLY_TYPED_PRODUCER_FROZEN_SOURCE_IDENTITY_VERIFY_V2')]:
 assert t.count(old)==1;t=t.replace(old,new)
ast.parse(t);v=dict(kind='PARENT_SOURCE_VERIFIER_ENCODING_SPELLING_FAILURE_NOT_PRODUCER_FAILURE',epoch=time.time(),first_returncode=1,exception='LookupError: unknown encoding: utf8-sig',phase='FIRST_PY_MEMBER_AST_BEFORE_FINITE34_VERIFICATION',old_result_written=False,producer_or_dependency_files_written=0,project_imports_or_tests_or_Torch_SDK_model_raw_C_resources=0,old_source_sha256=hashlib.sha256(b).hexdigest(),new_source_sha256=hashlib.sha256(t.encode()).hexdigest(),actual_fix="utf8-sig -> utf-8-sig",other_changes='EXCLUSIVE_V2_OUTPUT_MARKER_KIND_NAMES_ONLY',old_failure_and_marker_retained=True)
with err.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
with dst.open('x',encoding='utf-8',newline='\n')as f:f.write(t)
print(json.dumps(v,indent=2))

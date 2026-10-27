"""Freeze own interface/source files only; no actual model access."""
from pathlib import Path
import ast,json,hashlib,datetime
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in D.glob('*.py'):ast.parse(p.read_bytes())
name='review_actual_native88C_case_safe_V2_bound_formal_CPU_unused_once.py';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (D/'FROZEN_SOURCE_STATUS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,status='SOURCE_ONLY_FROZEN_UNUSED_WRAPPER',wrapper=name,wrapper_SHA=H(D/name),metadata_source_checks=3,
 frozen_reviewer_SHA_unchanged='a97587c3ee6ff7015949d06aa429851026f8d3837ab65bda56f69a048906bbb9',models_read_or_statted_or_hashed=False,actual_wrapper_or_reviewer_executed=False,network_GPU_or_account=False,original_errors_reports_and_partial_retained=True,source_failures=[],root_Git_pending=True),f,indent=2)
rows=[dict(relative=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file()]
with (D/'INDEX_SHA256_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,files=rows,scope='complete own directory except self-index'),f,indent=2)
print(json.dumps(dict(frozen_UTC=now,index_SHA=H(D/'INDEX_SHA256_ACTUAL.json'),wrapper_SHA=H(D/name),files=len(rows)),indent=2))

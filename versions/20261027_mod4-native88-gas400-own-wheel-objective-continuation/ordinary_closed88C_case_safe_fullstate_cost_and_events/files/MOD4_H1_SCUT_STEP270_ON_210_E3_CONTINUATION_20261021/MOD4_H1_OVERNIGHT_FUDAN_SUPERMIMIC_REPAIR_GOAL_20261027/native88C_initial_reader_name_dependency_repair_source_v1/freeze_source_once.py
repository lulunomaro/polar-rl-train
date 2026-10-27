"""Freeze own tiny source fixtures/reports, never a real model."""
from pathlib import Path
import ast,json,hashlib,datetime
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in D.rglob('*.py'):ast.parse(p.read_bytes())
name='native88_initial_CPU_reader_primitives_v1.py';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (D/'FROZEN_SOURCE_STATUS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,status='SOURCE_ONLY_FROZEN_NOT_MODEL_QUALIFICATION',new_primitives=name,new_primitives_SHA=H(D/name),tiny_CPU_checks=9,
 only_added_helpers=['H','read'],all_original_definition_AST_exact=True,unresolved_source_globals_after=[],actual_models_statted_read_hashed=0,actual_CPU_reviewer_main_written_or_run=False,
 previous_shared_witness_completed_loads=1,previous_NEW_FINAL_loads=0,next_new_purpose_shared_witness_additional_read_required=1,original_directories_modified=False,root_Git_pending=True),f,indent=2)
rows=[]
for p in sorted(D.rglob('*')):
 if p.is_file():
  assert p.suffix.lower() not in ('.pt','.pth','.npz','.usd','.usdc','.zip')
  rows.append(dict(relative=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
with (D/'INDEX_SHA256_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_UTC=now,files=rows,scope='complete own source/tiny fixture directory except self-index'),f,indent=2)
print(json.dumps(dict(frozen_UTC=now,index_SHA=H(D/'INDEX_SHA256_ACTUAL.json'),new_primitives_SHA=H(D/name),files=len(rows)),indent=2))

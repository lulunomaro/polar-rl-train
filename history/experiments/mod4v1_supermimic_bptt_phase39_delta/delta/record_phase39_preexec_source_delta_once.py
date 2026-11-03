"""Record pre-first-execution source guard/note delta; no Git/native operation."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;p=R/'archive_phase39_binding_teacher_schema_delta.py';out=R/'reports/PHASE39_PREEXEC_SOURCE_GUARD_NOTE_DELTA_V1.json';assert not out.exists()and not(R.parent/'repo-lqr/history/experiments/mod4v1_supermimic_bptt_phase39_delta').exists();prepared=json.loads((R/'reports/PHASE39_ARCHIVE_SOURCE_PREPARED_V1.json').read_bytes());assert prepared['SHA256']=='8c5bbf52cef7e45a7b1ec47714cc26e550ed7269dfa6c330addea2a825c63d2b';raw=p.read_bytes();ast.parse(raw);assert b'b4seal='in raw and b'contradictory 4vs9'in raw
v=dict(kind='PHASE39_PRE_FIRST_EXECUTION_SOURCE_GUARD_NOTE_DELTA',epoch=time.time(),prepared_SHA256=prepared['SHA256'],actual_source_bytes=len(raw),actual_source_SHA256=hashlib.sha256(raw).hexdigest(),changes=['late final B4 seal bound and SOURCE-only note','D5 lifecycle final snapshot vs later pending work label','active guard4/runtime9 schema contradiction explicitly preserved'],actual_Git_model_raw_SDK_CPU_C_or_resource_operations=0,old_preparer_anchor_failure_and_V2_preserved=True)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

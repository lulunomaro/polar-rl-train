"""Freeze source/AST feasibility only, without any model or raw motion file."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;P=D/'FROZEN_NATIVE_FULL_ATTEMPT_FEASIBILITY_INDEX.json'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p!=P:
  assert p.suffix.lower() not in ('.pt','.npz','.usd','.zip')
  files.append(dict(relative=p.relative_to(D).as_posix(),path=str(p),bytes=p.stat().st_size,SHA=H(p)))
v=dict(schema='mod4.native86.full_attempt.source_feasibility.frozen_index.v1',epoch=time.time(),frozen=True,
 files=files,file_count=len(files),excludes_only_self=True,source_AST_passed=True,driver_executed=False,
 smallN_actual_SDK_admitted=False,model_PT_raw_NPZ_read_hash_copy=False,actor_physics_GPU_SSH_Git_ledger=False,
 failed_attempts=[],old_frozen_directories_unchanged=True,archive_status='pending root ordinary source supplement')
with P.open('x',encoding='utf8') as stream:json.dump(v,stream,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps(dict(index=str(P),index_SHA=H(P),files=len(files),driver_SHA=H(D/'native_frozen_single_attempt_driver_candidate_v1.py'),frozen=True)))

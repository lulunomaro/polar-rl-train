"""Freeze this design/source review; no model files or candidate implementation."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;P=D/'FROZEN_NATIVE_PHASE_RETENTION_NEXT_CANDIDATE_INDEX.json'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p!=P:
  assert p.suffix.lower() not in ('.pt','.npz','.usd','.zip')
  files.append(dict(relative=p.relative_to(D).as_posix(),path=str(p),bytes=p.stat().st_size,SHA=H(p)))
value=dict(schema='mod4.native.phase_retention.source_design.frozen_index.v1',epoch=time.time(),frozen=True,
 files=files,file_count=len(files),excludes_only_self=True,source_metadata_CPU_passed=4,source_metadata_CPU_total=4,
 candidate_sampler_implemented=False,candidate_runtime_admitted=False,
 real_PT_raw_NPZ_read_hash_copy=False,SSH_GPU_actor_physics_rollout_Git_ledger=False,
 old_frozen_directories_unchanged=True,failed_attempts=[],
 archive_status='pending root ordinary supplement to actual86B trial1457; not claimed recorded')
with P.open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps(dict(index=str(P),index_SHA=H(P),files=len(files),frozen=True)))

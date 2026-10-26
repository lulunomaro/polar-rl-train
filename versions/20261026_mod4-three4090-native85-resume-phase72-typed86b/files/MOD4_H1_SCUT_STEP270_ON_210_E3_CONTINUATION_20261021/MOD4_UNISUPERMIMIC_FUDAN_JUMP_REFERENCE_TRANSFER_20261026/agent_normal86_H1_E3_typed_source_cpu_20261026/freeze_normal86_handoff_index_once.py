"""Freeze all normal86 source/report bytes; no model files are permitted."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;P=D/'FROZEN_NORMAL86_H1_E3_TYPED_SOURCE_CPU_INDEX.json'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p!=P:
  assert p.suffix.lower() not in ('.pt','.npz','.usd','.zip')
  rows.append(dict(relative=p.relative_to(D).as_posix(),path=str(p),bytes=p.stat().st_size,SHA=H(p)))
c={key:dict(contract_SHA=H(D/'candidate_overlays'/key/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json'),
    source_guard_SHA=H(D/'candidate_overlays'/key/'normal86_source_guard_v1.py'),
    loader_SHA=H(D/'candidate_overlays'/key/'normal86_closed_source_CPU_v1.py')) for key in ('h1','recovery')}
value=dict(schema='mod4.normal86.H1_E3.typed_source_CPU.frozen_index.v1',epoch=time.time(),frozen=True,
 file_count=len(rows),files=rows,excludes_only_self=True,contracts=c,synthetic_CPU_passed=56,synthetic_CPU_total=56,
 actual86_installed_SDK_CPU=False,real_PT_NPZ_read_hash_copy=False,remote_GPU_policy_ledger_lock_Task_GO_Git=False,
 Git='pending root ordinary supplement; not claimed recorded')
with P.open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps(dict(index=str(P),index_SHA=H(P),files=len(rows),contracts=c,frozen=True)))

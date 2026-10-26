"""Freeze every local source/report byte; excludes only this index itself."""
from pathlib import Path
import hashlib
import json
import time
D = Path(__file__).resolve().parent
destination = D / 'FROZEN_NATIVE86_TYPED_SOURCE_WORKER_CPU_INDEX.json'
files = []
for p in sorted(D.rglob('*')):
    if p.is_file() and p != destination:
        assert p.suffix.lower() not in ('.pt', '.npz', '.usd', '.zip'), 'No real payload permitted'
        files.append(dict(relative=p.relative_to(D).as_posix(), path=str(p),
            bytes=p.stat().st_size, SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
value = dict(schema='mod4.native86.source_worker_CPU.frozen_index.v1', epoch=time.time(),
    frozen=True, files=files, file_count=len(files), excludes_only_self=True,
    passed_synthetic_CPU=52, total_synthetic_CPU=52, actual86_installed_SDK_CPU=False,
    real_PT_NPZ_read_hash_copy=False, remote_GPU_policy_ledger_lock_Task_GO_Git=False,
    archive_status='pending root ordinary85 supplement; not claimed recorded')
with destination.open('x', encoding='utf8') as stream:
    json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n')
print(json.dumps(dict(index=str(destination), files=len(files), index_SHA=hashlib.sha256(destination.read_bytes()).hexdigest(), frozen=True)))

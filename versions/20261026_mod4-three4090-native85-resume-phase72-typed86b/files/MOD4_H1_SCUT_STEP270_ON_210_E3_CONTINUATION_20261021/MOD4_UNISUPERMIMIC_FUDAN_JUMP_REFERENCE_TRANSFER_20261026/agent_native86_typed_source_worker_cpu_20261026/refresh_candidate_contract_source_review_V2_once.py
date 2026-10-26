"""Preserve prior contract; refresh exact source pins after final guard review."""
from pathlib import Path
import hashlib
import json
import time

D = Path(__file__).resolve().parent
B = D / 'candidate_overlay'
P = B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json'
raw = P.read_bytes()
with (D / 'reports/NATIVE86_SOURCE_CONTRACT_V1_BEFORE_FINAL_GUARD_REVIEW_ACTUAL.json').open('xb') as stream:
    stream.write(raw)
c = json.loads(raw)
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for row in c['overlay_files']:
    p = B / row['relative']
    row.update(bytes=p.stat().st_size, SHA=H(p))
for key, relative in (
    ('native_source_guard_SHA', 'native86_source_guard_v1.py'),
    ('native_CPU_loader_source_SHA', 'native86_closed_source_CPU_v1.py'),
    ('source_SDK_CPU_source_SHA', 'target_native86_source_sdk_cpu_review_v1.py')):
    c['candidate_pins'][key] = H(B / relative)
c['source_review_revision'] = 2
c['previous_contract_SHA'] = hashlib.sha256(raw).hexdigest()
tmp = P.with_suffix('.json.review2.partial')
with tmp.open('x', encoding='utf8') as stream:
    json.dump(c, stream, indent=2)
    stream.write('\n')
tmp.replace(P)
report = dict(epoch=time.time(), preserved_previous_contract=True,
    previous_contract_SHA=hashlib.sha256(raw).hexdigest(), current_contract_SHA=H(P),
    changes=['Preserve legitimate absent Adam state for never-gradient params; strict native load roundtrip retained',
             'Retain all original fresh SDK/reward/boundary/sampling/reference/objective ready checks',
             'Bind ready reference/adapter/objective to original native85 producer'],
    failures_found=False, source_only=True, actual86_SDK_CPU=False,
    no_real_PT_NPZ_or_remote_GPU=True, git='pending parent ordinary supplement')
with (D / 'reports/NATIVE86_FINAL_GUARD_SOURCE_REVIEW_V2_ACTUAL.json').open('x', encoding='utf8') as stream:
    json.dump(report, stream, indent=2)
print(json.dumps(report))

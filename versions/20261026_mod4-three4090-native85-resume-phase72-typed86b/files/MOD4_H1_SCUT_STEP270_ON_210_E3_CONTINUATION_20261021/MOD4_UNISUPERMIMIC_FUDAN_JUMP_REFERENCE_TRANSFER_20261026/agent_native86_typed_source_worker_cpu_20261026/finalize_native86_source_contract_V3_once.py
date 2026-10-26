"""Finalize exact source contract after required node-loader wiring review."""
from pathlib import Path
import hashlib
import json
import time

D = Path(__file__).resolve().parent
B = D / 'candidate_overlay'
P = B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
raw = P.read_bytes()
with (D / 'reports/NATIVE86_SOURCE_CONTRACT_V2_BEFORE_DISPATCH_FINALIZATION_ACTUAL.json').open('xb') as stream:
    stream.write(raw)
c = json.loads(raw)
rows = {r['relative']: r for r in c['overlay_files']}
rows['closed_production_continuation_CPU_v2.py'] = dict(relative='closed_production_continuation_CPU_v2.py')
for relative, row in rows.items():
    p = B / relative
    row.update(bytes=p.stat().st_size, SHA=H(p))
c['overlay_files'] = [rows[k] for k in sorted(rows)]
old = json.loads((B / 'NATIVE85_ORIGINAL_COMPLETE_MANIFEST.json').read_bytes())
old_rows = {r['relative']: r for r in old['files']}
name = 'closed_production_continuation_CPU_v2.py'
c['controller_replacements'] = [dict(rows[name], original_SHA=old_rows[name]['SHA'])]
c['controller_additions'] = []
c['metadata_replacements'] = []
for key, relative in (
    ('native_source_guard_SHA', 'native86_source_guard_v1.py'),
    ('native_CPU_loader_source_SHA', 'native86_closed_source_CPU_v1.py'),
    ('source_SDK_CPU_source_SHA', 'target_native86_source_sdk_cpu_review_v1.py'),
    ('worker_source_SHA', 'h1_unisupermimic_step270_worker_v1.py'),
    ('native_dispatcher_source_SHA', name)):
    c['candidate_pins'][key] = H(B / relative)
c['source_review_revision'] = 3
c['previous_contract_SHA'] = hashlib.sha256(raw).hexdigest()
c['required_root_finalization'] = dict(
    controller_replacements=['three_slot_common_v1.py', 'forwarded_original_owner_control_v1.py', 'three_real_gpu_resource_v1.py'],
    controller_additions=['mixed86_protocol_v1.py'], metadata_replacements=['job0/TASK.json'],
    each_row='relative/original_SHA(if replacement)/bytes/SHA; no directories or removal',
    controller_spec_fields=['manifest_SHA', 'native_source_contract_SHA', 'candidate_pins'],
    TASK_forbidden_circular_fields=['manifest_SHA', 'native_source_contract_SHA'],
    GO_fields=['manifest_SHA', 'bootstrap_SHA', 'bootstrap_Adam', 'native_continuation_restore_required',
               'source_native_iteration=68', 'window_start_WM=680', 'window_start_Pi=58'])
tmp = P.with_suffix('.json.final3.partial')
with tmp.open('x', encoding='utf8') as stream:
    json.dump(c, stream, indent=2); stream.write('\n')
tmp.replace(P)
print(json.dumps(dict(passed=True, revision=3, contract_SHA=H(P), dispatcher_replacement=c['controller_replacements'][0],
    actual_installed86_SDK_CPU=False, no_PT_NPZ_remote_GPU_Git=True)))

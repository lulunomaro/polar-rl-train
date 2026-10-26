"""Exact field-name alignment to root's actual pure mixed86 protocol."""
from pathlib import Path
import hashlib
import json
D = Path(__file__).resolve().parent
B = D / 'candidate_overlay'
P = B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
raw = P.read_bytes()
with (D / 'reports/NATIVE86_SOURCE_CONTRACT_V3_BEFORE_ROOT_SCHEMA_ALIGNMENT_ACTUAL.json').open('xb') as stream:
    stream.write(raw)
c = json.loads(raw)
for row in c['overlay_files']:
    path = B / row['relative']; row.update(bytes=path.stat().st_size, SHA=H(path))
c['candidate_pins']['native_source_guard_SHA'] = H(B / 'native86_source_guard_v1.py')
c['source_review_revision'] = 4
c['previous_contract_SHA'] = hashlib.sha256(raw).hexdigest()
c['required_root_finalization']['GO_fields'] = ['manifest_SHA', 'bootstrap_SHA', 'bootstrap_Adam',
    'native_continuation_restore_required', 'source_native_iteration=68',
    'window_start_world_updates=680', 'window_start_policy_updates=58']
c['required_root_finalization']['TASK_typed_bootstrap_field'] = 'bootstrap_source_SHA'
c['root_ready_protocol_source'] = str(D.parent.parent / 'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86_20261026/mixed86_protocol_v1.py')
c['root_ready_protocol_source_SHA'] = H(Path(c['root_ready_protocol_source']))
tmp = P.with_suffix('.json.final4.partial')
with tmp.open('x', encoding='utf8') as stream:
    json.dump(c, stream, indent=2); stream.write('\n')
tmp.replace(P)
print(json.dumps(dict(passed=True, contract_SHA=H(P), source_review_revision=4)))

"""Verify the app's persisted monitor against the reviewed UTF-8 source."""
from pathlib import Path
import hashlib
import json
import time
import tomllib

A = Path(__file__).resolve().parent
source = A / 'MONITOR_SCOPE105_COST_S4_CPU_AND_BODYFRAME_ACTUAL_20261014.txt'
saved = Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
receipt = A / 'reports/MONITOR_SCOPE105_AND_S4_CPU_ACTUAL_UPDATED.json'
assert not receipt.exists(), 'Do not overwrite an existing verification receipt'
value = tomllib.loads(saved.read_text(encoding='utf-8'))
assert value['id'] == 'mod4-10'
assert value['kind'] == 'heartbeat'
assert value['status'] == 'ACTIVE'
assert value['rrule'] == 'FREQ=HOURLY;INTERVAL=1'
assert value['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
assert value['prompt'] == source.read_text(encoding='utf-8')
result = dict(
    epoch=time.time(), passed=True,
    persisted_automation=str(saved), source=str(source),
    source_size=source.stat().st_size,
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    exact_persisted_prompt=True,
    automation_id=value['id'], kind=value['kind'], status=value['status'],
    rrule=value['rrule'], target_thread_id=value['target_thread_id'],
    original_updated_at=value.get('updated_at'),
    new_automation_created=False, GPU_or_PPO_started=False,
    canonical_budget_mutated=False,
    gate_training_started=False,
    monitor_scope='S3 limited expert domains, approved005 cost audit and S4 CPU preparation; declared birth-bodyframe CPU proposal only',
)
with receipt.open('x', encoding='utf-8', newline='\n') as out:
    json.dump(result, out, ensure_ascii=False, indent=2)
    out.write('\n')
print(json.dumps(result, ensure_ascii=False))

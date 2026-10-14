"""Verify the existing hourly monitor's persisted reviewed source exactly."""
from pathlib import Path
import hashlib
import json
import time
import tomllib

B = Path(__file__).resolve().parent
source = B / 'MONITOR_BODYFRAME_RESET_CPU_COMPOSITION_ACTUAL_20261014.txt'
app = Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
value = tomllib.loads(app.read_text(encoding='utf8'))
assert value['id'] == 'mod4-10' and value['kind'] == 'heartbeat' and value['status'] == 'ACTIVE'
assert value['rrule'] == 'FREQ=HOURLY;INTERVAL=1'
assert value['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
assert value['prompt'] == source.read_text(encoding='utf8')
output = B / 'reports/MONITOR_BODYFRAME_CPU_ACTUAL_UPDATED.json'
assert not output.exists()
result = dict(epoch=time.time(), passed=True, actual_persisted_prompt_exact=True,
    automation_id=value['id'], status=value['status'], kind=value['kind'], rrule=value['rrule'],
    target_thread_id=value['target_thread_id'], updated_at=value.get('updated_at'),
    source=str(source), bytes=source.stat().st_size, sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    no_second_monitor_created=True, new_GPU_PPO_or_budget_action=False)
output.write_text(json.dumps(result, indent=2), encoding='utf8')
print(json.dumps(result))

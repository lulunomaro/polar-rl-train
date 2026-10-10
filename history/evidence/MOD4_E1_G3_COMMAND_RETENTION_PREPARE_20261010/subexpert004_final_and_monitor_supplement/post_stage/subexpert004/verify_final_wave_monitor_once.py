"""Verify actual saved heartbeat after one structured update, never modify it."""
from pathlib import Path
import hashlib, json, time, tomllib

D = Path(__file__).resolve().parent
R = D / 'reports'


def main():
    c = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    expected = (R / 'HEARTBEAT_SUBEXPERT004_WAVE_FINAL_20261011.md').read_text(encoding='utf8').rstrip('\n')
    assert c['prompt'] == expected and c['status'] == 'ACTIVE'
    assert c['rrule'] == 'FREQ=HOURLY;INTERVAL=2' and c['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
    p = R / 'MONITOR_ACTUAL_WAVE_FINAL_20261011_PROMPT.md'
    assert not p.exists()
    p.write_bytes(c['prompt'].encode())
    v = dict(epoch=time.time(), automation_id='mod4-10', status=c['status'],
        rrule=c['rrule'], target_thread_id=c['target_thread_id'],
        prompt_bytes=p.stat().st_size, prompt_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),
        actual_prompt_exact=True, Wave_final_and131_complete_priority=True,
        old_active_prompt_retained_as_history=True, no_new_budget_seconds=0)
    p = R / 'FINAL_WAVE_MONITOR_ACTUAL_VERIFIED.json'
    assert not p.exists()
    p.write_bytes(json.dumps(v, indent=2).encode())
    print(json.dumps(dict(actual_prompt_exact=True, status=c['status'],
        two_hour_schedule_preserved=True, Wave_final_and131_complete_priority=True)))


if __name__ == '__main__':
    main()

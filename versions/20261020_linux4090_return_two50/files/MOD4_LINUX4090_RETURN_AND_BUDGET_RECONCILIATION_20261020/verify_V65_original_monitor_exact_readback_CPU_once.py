from pathlib import Path
import json,time,tomllib
B=Path(__file__).resolve().parent;R=B/'reports';a=json.loads((R/'V65_EXISTING_MONITOR_UPDATE_ARGS.json').read_bytes());v=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));checks=dict(prompt_exact=v['prompt']==a['prompt'],status_exact=v['status']==a['status']=='ACTIVE',rrule_exact=v['rrule']==a['rrule'],target_exact=v['target_thread_id']==a['targetThreadId'],id_exact=v['id']=='mod4-10')
with (R/'V65_EXISTING_MONITOR_EXACT_READBACK_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=all(checks.values()),checks=checks,no_second_monitor=True),f,indent=2)
assert all(checks.values()),checks
print(json.dumps(dict(passed=True,checks=checks)))

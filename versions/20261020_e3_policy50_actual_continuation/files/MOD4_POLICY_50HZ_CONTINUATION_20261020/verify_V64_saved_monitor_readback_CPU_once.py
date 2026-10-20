from pathlib import Path
import json,time,tomllib
B=Path(__file__).resolve().parent;R=B/'reports'
a=json.loads((R/'V64_EXISTING_AUTOMATION_UPDATE_ARGS.json').read_bytes())
t=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
checks={'prompt_exact':t['prompt']==a['prompt'],'status_exact':t['status']==a['status'],'rrule_exact':t['rrule']==a['rrule'],'target_exact':t['target_thread_id']==a['targetThreadId'],'original_id_exact':t['id']=='mod4-10'}
with (R/'V64_EXISTING_AUTOMATION_EXACT_READBACK_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),checks=checks,passed=all(checks.values()),no_second_monitor=True),f,indent=2)
assert all(checks.values()),checks
print(json.dumps(dict(passed=True,checks=checks)))

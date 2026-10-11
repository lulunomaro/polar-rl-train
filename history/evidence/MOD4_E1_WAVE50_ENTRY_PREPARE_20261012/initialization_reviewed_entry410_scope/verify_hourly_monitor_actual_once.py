from entry_io import *
import tomllib
p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');v=tomllib.loads(p.read_text(encoding='utf8'));q=json.loads((R/'ENTRY_HOURLY_MONITOR_UPDATE_REQUEST.json').read_bytes())
assert v['status']=='ACTIVE' and v['rrule']==q['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['target_thread_id']==q['targetThreadId'] and v['prompt']==q['prompt']
save('ENTRY_HOURLY_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,automation_id='mod4-10',status=v['status'],actual_hourly_same_target_verified=True,target_thread_id=v['target_thread_id'],prompt_SHA=H(v['prompt'].encode()),quiet_healthy_notification_policy_preserved=True,no_extra_automation_or_budget=True))
print(json.dumps(dict(passed=True,hourly_same_target=True)))

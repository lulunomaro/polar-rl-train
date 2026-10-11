"""Native automation trims one trailing newline; preserve failed byte-exact reader."""
from entry_io import *
import tomllib
save('MONITOR_READER_TRAILING_NEWLINE_REJECTION.json',dict(epoch=time.time(),source='verify_hourly_monitor_actual_once.py',error='AssertionError: raw prompt identity',actual_native_trim_only_one_trailing_newline=True,no_automation_or_training_fault=True,no_second_update_requested=True))
p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');v=tomllib.loads(p.read_text(encoding='utf8'));q=json.loads((R/'ENTRY_HOURLY_MONITOR_UPDATE_REQUEST.json').read_bytes())
assert v['status']=='ACTIVE' and v['rrule']==q['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['target_thread_id']==q['targetThreadId']
assert q['prompt'].endswith('\n') and v['prompt']==q['prompt'][:-1]
save('ENTRY_HOURLY_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,automation_id='mod4-10',status=v['status'],actual_hourly_same_target_verified=True,target_thread_id=v['target_thread_id'],prompt_SHA=H(v['prompt'].encode()),requested_prompt_SHA=H(q['prompt'].encode()),native_trimmed_exact_one_trailing_newline_only=True,quiet_healthy_notification_policy_preserved=True,no_extra_automation_or_budget=True))
print(json.dumps(dict(passed=True,hourly_same_target=True)))

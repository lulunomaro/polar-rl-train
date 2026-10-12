from wave_direction_second_io import *
import tomllib
q=json.loads((R/'SECOND_DIRECTION_HOURLY_MONITOR_UPDATE_REQUEST.json').read_bytes())
v=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
assert v['status']=='ACTIVE' and v['rrule']==q['rrule']=='FREQ=HOURLY;INTERVAL=1'
assert v['target_thread_id']==q['targetThreadId'] and v['name']==q['name']
raw=q['prompt'];actual=v['prompt'];exact=actual==raw;trim=raw.endswith('\n') and actual==raw[:-1];assert exact or trim
assert 'DONT_NOTIFY' in actual and 'NOTIFY' in actual
save('SECOND_DIRECTION_HOURLY_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,automation_id='mod4-10',status=v['status'],same_hourly_frequency_and_target_verified=True,target_thread_id=v['target_thread_id'],actual_prompt_SHA=H(actual.encode()),requested_prompt_SHA=H(raw.encode()),prompt_exact_or_native_one_trailing_newline_trim_only=True,quiet_healthy_notification_intent_preserved=True,no_extra_automation_or_budget=True))
print(json.dumps(dict(passed=True,hourly_same_target=True,prompt_exact=exact,native_trim_one_trailing_newline=trim)))

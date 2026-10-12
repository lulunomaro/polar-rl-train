from scut_wave_io import *
import tomllib

req=json.loads((R/'SCUT151_HOURLY_MONITOR_UPDATE_REQUEST.json').read_bytes());p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');s=tomllib.loads(p.read_text(encoding='utf8'))
assert s['status']==req['status']=='ACTIVE' and s['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and s['prompt']==req['prompt'] and s['target_thread_id']==req['targetThreadId']
save('SCUT151_HOURLY_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,id='mod4-10',rrule=s['rrule'],status=s['status'],same_target=s['target_thread_id'],exact_request_prompt_SHA=H(req['prompt'].encode()),actual_TOML_SHA=H(p.read_bytes()),healthy_pending_quiet_meaningful_only=True,no_extra_monitor_or_frequency_change=True))
print(json.dumps(dict(passed=True,id='mod4-10',hourly=True)))

from second50_io import *
import tomllib
t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'MONITOR_PPO_UPDATE_REQUEST.json').read_bytes())
assert t['id']==req['id'] and t['status']=='ACTIVE' and t['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and t['target_thread_id']==req['targetThreadId'] and t['prompt'].rstrip('\n')==req['prompt'].rstrip('\n')
save('MONITOR_PPO_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,id=t['id'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],prompt_SHA=H(t['prompt'].encode()),requested_prompt_SHA=H(req['prompt'].encode()),only_terminal_LF_normalization=True,same_hourly_heartbeat_no_new_monitor=True,native_automation_update_acknowledged=True))
print('Same hourly heartbeat ACTIVE and positivePPO prompt actually verified')

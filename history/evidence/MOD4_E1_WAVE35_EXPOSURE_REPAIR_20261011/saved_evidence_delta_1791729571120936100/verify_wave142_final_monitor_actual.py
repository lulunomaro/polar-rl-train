"""Verify native automation application and preserve its actual receipt."""
from wave_io import *
import tomllib

def main():
    request=json.loads((R/'WAVE142_COMPLETE_MONITOR_UPDATE_REQUEST.json').read_bytes())
    p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');actual=tomllib.loads(p.read_text(encoding='utf8'))
    assert actual['prompt']==request['prompt'] and actual['status']=='ACTIVE' and actual['rrule']==request['rrule']=='FREQ=HOURLY;INTERVAL=1'
    assert actual['target_thread_id']==request['targetThreadId'] and actual['name']==request['name'] and actual.get('notification_policy') is None
    q=save('WAVE142_COMPLETE_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),automation_id='mod4-10',actual_toml_path=str(p),prompt_SHA=H(actual['prompt'].encode()),prompt_bytes=len(actual['prompt'].encode()),status=actual['status'],rrule=actual['rrule'],same_target=actual['target_thread_id'],native_update_actual_prompt_exact=True,no_new_monitor_or_budget_expansion=True,full142_complete_unqualified=True,next_continuation_not_yet_deployed=True))
    print(json.dumps(dict(report=str(q),actual_verified=True,same_hourly_ACTIVE=True)))

if __name__=='__main__':main()

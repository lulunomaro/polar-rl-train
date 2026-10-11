from second_io import *
import tomllib
def main():
 req=json.loads((R/'SECOND_MONITOR_UPDATE_REQUEST.json').read_bytes());path=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');v=tomllib.loads(path.read_text(encoding='utf8'))
 assert v['prompt']==req['prompt'] and v['status']=='ACTIVE' and v['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['target_thread_id']==req['targetThreadId'] and v['name']==req['name'] and v.get('notification_policy') is None
 save('SECOND_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),automation_id='mod4-10',actual_toml_path=str(path),status=v['status'],rrule=v['rrule'],same_target=v['target_thread_id'],prompt_SHA=H(v['prompt'].encode()),prompt_bytes=len(v['prompt'].encode()),native_update_actual_prompt_exact=True,no_new_monitor_or_budget=True))
 print(json.dumps(dict(actual_verified=True,same_hourly_ACTIVE=True)))
if __name__=='__main__':main()

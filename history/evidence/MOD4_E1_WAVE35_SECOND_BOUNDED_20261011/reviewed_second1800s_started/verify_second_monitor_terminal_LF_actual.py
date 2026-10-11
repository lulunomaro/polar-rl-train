from second_io import *
import tomllib
def main():
 old=D/'verify_second_monitor_actual.py'
 save('SECOND_MONITOR_LITERAL_READER_REJECTION.json',dict(epoch=time.time(),original_source=str(old),source_SHA=H(old.read_bytes()),error='AssertionError at exact prompt comparison; native automation_update succeeded but app removed exactly one terminal LF. Frequency/name/target/status/notification all exact; no scheduling or physical failure.',original_request_and_prompt_bytes_retained=True,no_second_automation_update=True))
 req=json.loads((R/'SECOND_MONITOR_UPDATE_REQUEST.json').read_bytes());path=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');v=tomllib.loads(path.read_text(encoding='utf8'))
 assert req['prompt'].endswith('\n') and v['prompt']==req['prompt'][:-1]
 assert v['status']=='ACTIVE' and v['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['target_thread_id']==req['targetThreadId'] and v['name']==req['name'] and v.get('notification_policy') is None
 save('SECOND_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),automation_id='mod4-10',actual_toml_path=str(path),status=v['status'],rrule=v['rrule'],same_target=v['target_thread_id'],actual_prompt_SHA=H(v['prompt'].encode()),request_prompt_SHA=H(req['prompt'].encode()),actual_prompt_bytes=len(v['prompt'].encode()),app_removed_exactly_one_terminal_LF_only=True,native_update_actual_content_exact=True,no_new_monitor_or_budget=True,original_literal_reader_rejection_preserved=True))
 print(json.dumps(dict(actual_verified=True,same_hourly_ACTIVE=True,only_one_terminal_LF_normalized=True)))
if __name__=='__main__':main()

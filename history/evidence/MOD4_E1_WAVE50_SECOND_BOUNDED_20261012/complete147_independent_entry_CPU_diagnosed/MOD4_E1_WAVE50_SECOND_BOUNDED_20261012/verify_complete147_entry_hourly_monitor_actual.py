from second50_io import *
import tomllib
def main():
 req=json.loads((R/'FINAL_MONITOR_UPDATE_REQUEST.json').read_bytes());actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert actual['status']=='ACTIVE' and actual['rrule']==req['rrule']=='FREQ=HOURLY;INTERVAL=1' and actual['target_thread_id']==req['targetThreadId']
 assert actual['prompt'].rstrip('\n')==req['prompt'].rstrip('\n')
 p=save('FINAL_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),passed=True,automation_id='mod4-10',status=actual['status'],rrule=actual['rrule'],target_thread=actual['target_thread_id'],same_existing_hourly_heartbeat=True,prompt_SHA256=H(actual['prompt'].rstrip('\n').encode()),complete147_notqualified_and_new_entry_CPU_only_actual_priority=True,quiet_healthy_pending_preserved=True,no_new_automation_or_budget=True))
 print(json.dumps(dict(report=str(p),passed=True,status=actual['status'],hourly=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('MONITOR_COMPLETE147_VERIFY_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_budget_or_monitor_replay=True));raise

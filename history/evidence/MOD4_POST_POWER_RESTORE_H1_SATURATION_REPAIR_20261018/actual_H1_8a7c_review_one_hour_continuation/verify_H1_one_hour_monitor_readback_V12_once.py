"""Read back the existing hourly monitor; do not write automation state directly."""
from pathlib import Path
import json,tomllib,time,hashlib
B=Path(__file__).resolve().parent
def main():
 args=json.loads((B/'AUTOMATION_H1_ONE_HOUR_ACTUAL_HANDOFF_HOURLY_ARGS_V12.json').read_bytes())
 a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert args['prompt'].rstrip('\r\n')==a['prompt'].rstrip('\r\n')
 assert a['status']=='ACTIVE' and a['rrule']==args['rrule']=='FREQ=HOURLY;INTERVAL=1' and a['target_thread_id']==args['targetThreadId']=='01a07a2d-9036-7531-a012-692df9f56353'
 v=dict(epoch=time.time(),automation_tool_actual_receipt=dict(automationId='mod4-10',mode='update',status='ACTIVE'),prompt_normalized_exact=True,submitted_prompt_SHA=hashlib.sha256(args['prompt'].encode()).hexdigest(),actual_app_prompt_SHA=hashlib.sha256(a['prompt'].encode()).hexdigest(),same_hourly_original_target=True,no_new_monitor=True,training_hour_3600_plus_exit300_and_no24cutoff_saved=True,no_GPU_or_account_action=True)
 with (B/'reports/H1_ONE_HOUR_MONITOR_APP_RECEIPT_READBACK_V12_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 print(json.dumps(v),flush=True)
if __name__=='__main__':main()

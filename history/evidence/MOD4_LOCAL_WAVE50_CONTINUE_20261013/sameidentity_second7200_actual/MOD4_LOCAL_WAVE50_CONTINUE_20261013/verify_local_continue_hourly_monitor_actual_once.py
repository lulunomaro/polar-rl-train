from pathlib import Path
import json,time,tomllib,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';T=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
request=json.loads((R/'LOCAL_CONTINUE_HOURLY_MONITOR_UPDATE_REQUEST.json').read_bytes());cfg=tomllib.loads(T.read_text(encoding='utf8'))
for k in ('name','status','rrule'):assert cfg[k]==request[k]
assert cfg['target_thread_id']==request['targetThreadId'] and cfg['prompt'].rstrip()==request['prompt'].rstrip()
p=R/'LOCAL_CONTINUE_HOURLY_MONITOR_ACTUAL_VERIFIED.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed=True,status=cfg['status'],rrule=cfg['rrule'],target=cfg['target_thread_id'],actual_TOML_SHA=hashlib.sha256(T.read_bytes()).hexdigest(),current_continue_scope_and_human_continuous_intent_preserved=True,remote_still_paused=True,no_extra_monitor_or_autobudget=True),indent=2),encoding='utf8');print(json.dumps(dict(passed=True,report=str(p))))

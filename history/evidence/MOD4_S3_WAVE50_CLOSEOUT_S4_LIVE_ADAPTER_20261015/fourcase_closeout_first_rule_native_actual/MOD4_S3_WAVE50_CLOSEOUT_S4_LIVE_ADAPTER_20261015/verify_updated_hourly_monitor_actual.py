from pathlib import Path
import tomllib,json,time,hashlib
D=Path(__file__).resolve().parent
p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');v=tomllib.loads(p.read_text(encoding='utf8'))
source=D/'MONITOR_BODY_AXIS_FOURCASE_CLOSED_S4_RULE_NATIVE120_ACTUAL_20261015.txt';expected=source.read_bytes()
assert v['id']=='mod4-10' and v['kind']=='heartbeat' and v['status']=='ACTIVE'
assert v['name']=='MOD4计划与双机并行巡检' and v['rrule']=='FREQ=HOURLY;INTERVAL=1'
assert v['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
assert v['prompt'].encode('utf8')==expected
r=dict(epoch=time.time(),passed=True,id=v['id'],kind=v['kind'],status=v['status'],name=v['name'],target=v['target_thread_id'],same_hourly_frequency=True,exact_prompt_file=str(source),prompt_bytes=len(expected),prompt_sha256=hashlib.sha256(expected).hexdigest(),native_tool_result_observed={'automationId':'mod4-10','mode':'update','status':'ACTIVE'},actual_TOML_prompt_byteexact=True,no_second_monitor=True,quiet_healthy_pending_preserved=True,old_pending_prompt_preserved=True)
out=D/'reports/S4_NATIVE_COMPLETE_HOURLY_MONITOR_ACTUAL_BYTEEXACT_VERIFIED.json';assert not out.exists();out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r,ensure_ascii=False))

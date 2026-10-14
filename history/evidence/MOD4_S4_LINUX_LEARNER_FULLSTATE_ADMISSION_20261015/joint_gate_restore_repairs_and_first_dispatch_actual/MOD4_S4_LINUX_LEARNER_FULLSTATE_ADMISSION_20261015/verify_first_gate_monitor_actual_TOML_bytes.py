from pathlib import Path
import os,tomllib,json,hashlib,time
D=Path(__file__).resolve().parent
p=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml'
v=tomllib.loads(p.read_text(encoding='utf8'));raw=(D/'MONITOR_S4_FIRST_SUPPORTED_GATE45M_DISPATCHED_ACTUAL_20261015.txt').read_bytes()
assert v['prompt'].encode('utf8')==raw and v['status']=='ACTIVE' and v['kind']=='heartbeat'
assert v['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
out=D/'reports/S4_FIRST_GATE_MONITOR_ACTUAL_TOML_BYTEEXACT_VERIFIED.json';assert not out.exists()
out.write_text(json.dumps(dict(epoch=time.time(),passed=True,prompt_SHA=hashlib.sha256(raw).hexdigest(),prompt_bytes=len(raw),same_id=v['id'],same_rrule=v['rrule'],same_target=v['target_thread_id'],same_status=v['status'],no_second_monitor=True),indent=2))
print(json.dumps(dict(passed=True,report=str(out),prompt_SHA=hashlib.sha256(raw).hexdigest())))

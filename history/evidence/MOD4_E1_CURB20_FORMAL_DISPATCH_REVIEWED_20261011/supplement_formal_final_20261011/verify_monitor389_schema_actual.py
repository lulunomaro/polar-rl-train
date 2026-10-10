"""Read actual app TOML after update; retain normalized exact prompt receipt."""
from pathlib import Path
import os,tomllib,json,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports'
cfg=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml'
actual=tomllib.loads(cfg.read_text(encoding='utf8'));expected=(D/'MONITOR_CURRENT_FORMAL389_SCHEMA_PROMPT.md').read_text(encoding='utf8')
assert actual['status']=='ACTIVE' and actual['rrule']=='FREQ=HOURLY;INTERVAL=2'
assert actual['prompt'].strip()==expected.strip() and actual['name']=='MOD4计划与双机并行巡检'
assert actual['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
raw=actual['prompt'].encode();(D/'MONITOR_ACTUAL_FORMAL389_SCHEMA_POSTUPDATE_PROMPT.md').write_bytes(raw)
v=dict(epoch=time.time(),automation_id='mod4-10',status=actual['status'],rrule=actual['rrule'],name=actual['name'],target_thread_id=actual['target_thread_id'],actual_prompt_bytes=len(raw),actual_prompt_sha256=hashlib.sha256(raw).hexdigest(),app_trailing_whitespace_normalization_only=actual['prompt']!=expected,normalized_prompt_exact=True,no_canonical_GPU_or_player_action=True)
(R/'MONITOR_FORMAL389_SCHEMA_UPDATED_VERIFIED.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(v,ensure_ascii=True))

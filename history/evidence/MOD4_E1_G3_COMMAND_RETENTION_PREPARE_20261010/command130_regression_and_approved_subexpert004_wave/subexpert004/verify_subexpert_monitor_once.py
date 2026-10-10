"""Verify actual saved schedule and prompt after the actual structured update."""
from pathlib import Path
import hashlib,json,time,tomllib
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');c=tomllib.loads(p.read_text(encoding='utf8'));expected=(R/'HEARTBEAT_SUBEXPERT004_WAVE_EXECUTING_20261010.md').read_text(encoding='utf8').rstrip('\n')
 assert c['prompt']==expected and c['status']=='ACTIVE' and c['rrule']=='FREQ=HOURLY;INTERVAL=2' and c['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 raw=c['prompt'].encode();q=R/'MONITOR_ACTUAL_SUBEXPERT004_PROMPT.md';assert not q.exists();q.write_bytes(raw)
 q=R/'SUBEXPERT_MONITOR_ACTUAL_VERIFIED.json';assert not q.exists();q.write_bytes(json.dumps(dict(epoch=time.time(),automation_id='mod4-10',status=c['status'],rrule=c['rrule'],target_thread_id=c['target_thread_id'],prompt_bytes=len(raw),prompt_SHA=hashlib.sha256(raw).hexdigest(),actual_prompt_exact=True,prior_reader_error_repaired_before_one_actual_tool_mutation=True,new_budget_seconds=0),indent=2).encode())
 print(json.dumps(dict(actual_prompt_exact=True,status=c['status'],two_hour_schedule_preserved=True)))
if __name__=='__main__':main()

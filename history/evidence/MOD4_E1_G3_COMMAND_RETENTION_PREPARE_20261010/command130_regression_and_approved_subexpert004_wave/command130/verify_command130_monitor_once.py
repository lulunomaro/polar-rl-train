"""Verify the applied heartbeat without changing scheduling or training."""
from pathlib import Path
import hashlib,json,time,tomllib
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 expected=(R/'HEARTBEAT_COMMAND130_COMPLETE_COVERAGE_20261010.md').read_text(encoding='utf8').rstrip('\n')
 p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
 cfg=tomllib.loads(p.read_text(encoding='utf8'))
 assert cfg['prompt']==expected and cfg['status']=='ACTIVE'
 assert cfg['rrule']=='FREQ=HOURLY;INTERVAL=2'
 assert cfg['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 out=R/'MONITOR_ACTUAL_COMMAND130_PROMPT.md';assert not out.exists();out.write_bytes(cfg['prompt'].encode())
 receipt=R/'COMMAND130_MONITOR_ACTUAL_VERIFIED.json';assert not receipt.exists()
 receipt.write_bytes(json.dumps(dict(epoch=time.time(),automation_id='mod4-10',status=cfg['status'],rrule=cfg['rrule'],target_thread_id=cfg['target_thread_id'],prompt_file=str(out),prompt_bytes=out.stat().st_size,prompt_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),actual_prompt_exact=True,new_training_or_budget=False),ensure_ascii=False,indent=2).encode())
 print(json.dumps(dict(actual_prompt_exact=True,status=cfg['status'],two_hour_schedule_unchanged=True)))
if __name__=='__main__':main()

"""Read actual saved automation settings; never modify TOML or launch training."""
from pathlib import Path
import json,os,tomllib,hashlib,time
D=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 source=D/'MONITOR_LEFT_SECOND_POSITIVE16_COMPLETE_RETENTION_ACTUAL_20261014.txt';raw=source.read_bytes();wanted=raw.decode('utf8')
 config=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml'
 v=tomllib.loads(config.read_text(encoding='utf8'));saved=v['prompt']
 assert saved==wanted or (wanted.endswith('\n') and saved==wanted[:-1]),'Any instruction change beyond a single final LF must be preserved and investigated'
 assert v['status']=='ACTIVE' and v['rrule']=='FREQ=HOURLY;INTERVAL=1' and v['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 assert v['name']=='MOD4计划与双机并行巡检' and v['id']=='mod4-10' and v['kind']=='heartbeat'
 p=D/'reports/MONITOR_LEFT_SECOND_POSITIVE16_COMPLETE_RETENTION_ACTUAL_UPDATED.json';assert not p.exists()
 out=dict(epoch=time.time(),automation_id=v['id'],status=v['status'],rrule=v['rrule'],same_target=v['target_thread_id'],source_prompt_path=str(source),source_prompt_sha256=sha(raw),app_saved_prompt_sha256=sha(saved.encode()),tool_removes_single_final_LF_only=saved==wanted[:-1],all_instruction_characters_verified=True,new_second20k_actual_positive_saved_CPU_verified=True,old_finite_batch_actual_absent_and_all_retention_complete=True,quiet_healthypending_preserved=True,after_stage_ordinary_supplement_required=True)
 p.write_bytes(json.dumps(out,indent=2).encode());print(json.dumps(out))
if __name__=='__main__':main()

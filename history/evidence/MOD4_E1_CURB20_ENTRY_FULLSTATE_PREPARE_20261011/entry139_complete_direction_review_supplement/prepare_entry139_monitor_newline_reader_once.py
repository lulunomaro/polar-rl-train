"""Native app trimmed one finalLF; preserve failed validator, finish only unexecuted sync."""
from pathlib import Path
import json,time,tomllib,hashlib,sys
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import save
H=lambda b:hashlib.sha256(b).hexdigest()
def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'ENTRY139_COMPLETE_MONITOR_REQUEST.json').read_bytes())
 assert all(t[k]==req[k] for k in ('id','kind','name','status','rrule','target_thread_id'))
 a=t['prompt'].replace('\r\n','\n');b=req['prompt'].replace('\r\n','\n');assert a+'\n'==b
 old=D/'verify_sync_entry139_complete_once.py';source=old.read_text(encoding='utf8');needle="t['prompt'].replace('\\r\\n','\\n')==req['prompt'].replace('\\r\\n','\\n')";assert source.count(needle)==1
 new=D/'verify_sync_entry139_complete_app_trimmed_once.py';assert not new.exists();new.write_bytes(source.replace(needle,"t['prompt'].replace('\\r\\n','\\n')+'\\n'==req['prompt'].replace('\\r\\n','\\n')").encode('utf8'))
 save('ENTRY139_COMPLETE_MONITOR_TRAILING_NEWLINE_ACTUAL_DIAGNOSIS.json',dict(epoch=time.time(),old_source=str(old),old_source_SHA=H(old.read_bytes()),new_source=str(new),new_source_SHA=H(new.read_bytes()),native_actual_prompt_bytes=len(t['prompt'].encode()),requested_prompt_bytes=len(req['prompt'].encode()),native_actual_prompt_SHA=H(t['prompt'].encode()),requested_prompt_SHA=H(req['prompt'].encode()),only_exactly_one_final_newline_trimmed=True,all_other_prompt_characters_and_cadence_target_status_exact=True,original_error_reports_retained=True,no_native_update_repeat=True,no_central_CAS_before_original_assertion=True,no_GPU_PPO_or_budget_action=True))
 print(json.dumps(dict(new_source=str(new),exactly_one_finalLF_only=True,no_automation_repeat=True)))
if __name__=='__main__':main()

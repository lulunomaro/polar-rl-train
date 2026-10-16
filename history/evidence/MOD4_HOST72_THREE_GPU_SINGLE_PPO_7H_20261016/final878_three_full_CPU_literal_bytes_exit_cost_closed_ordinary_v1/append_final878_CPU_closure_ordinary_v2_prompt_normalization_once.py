"""Read-only prompt normalization repair; V1 rejected before capture/commit."""
from pathlib import Path
import json,os,time,tomllib,hashlib,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 old=D/'MONITOR_WORLD3_FINAL878_CPU_LITERAL_VERIFIED_COST_EXIT_CLOSED_RETENTION_PENDING_20261016.txt';new=D/'MONITOR_WORLD3_FINAL878_CPU_LITERAL_VERIFIED_COST_EXIT_CLOSED_RETENTION_PENDING_V2_APP_EXACT_20261016.txt'
 c=tomllib.loads((Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml').read_text(encoding='utf8'));a=old.read_text(encoding='utf8');b=c['prompt'];assert a.rstrip('\n')==b and len(a)==len(b)+1 and c['status']=='ACTIVE' and c['rrule']=='FREQ=HOURLY;INTERVAL=1';assert not new.exists()
 with new.open('xb') as f:f.write(b.encode('utf8'))
 report=R/'FINAL878_MONITOR_TRAILING_NEWLINE_V1_REJECTION_V2_READONLY_NORMALIZATION_ACTUAL.json';assert not report.exists()
 report.write_text(json.dumps(dict(epoch=time.time(),V1_error='Strict byte equality rejected because automation tool normalized one terminal newline; rejected before destination capture or any Git commit',original_monitor=str(old),original_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),actual_app_exact_copy=str(new),app_prompt_SHA=hashlib.sha256(b.encode()).hexdigest(),prompt_text_content_exact_except_one_terminal_newline=True,no_automation_schedule_target_status_change=True,no_runtime_or_weight_or_cost_changes=True,V1_source_and_error_preserved=True),indent=2),encoding='utf8')
 p=D/'append_final878_CPU_closure_and_same_hourly_monitor_ordinary_once.py';src=p.read_text(encoding='utf8').replace(old.name,new.name);src=src.replace("if __name__=='__main__':","if __name__=='__unused__':");scope={'__file__':str(p),'__name__':'final_append_v2_readonly_prompt_repair'};exec(compile(src,str(Path(__file__)),'exec'),scope);scope['main']()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FINAL878_ORDINARY_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_duplicate_record_tag_commit_or_runtime=True),f,indent=2)
  raise

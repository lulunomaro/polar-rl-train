"""Retain pre-record archive rejection; bind exact app prompt after trailing-newline normalization."""
from pathlib import Path
import ast,hashlib,json,time,tomllib,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
try:
 m=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 old=R/'CURRENT_ACTUAL71_WITH_HUMAN_GPU_STATUS_MONITOR_SOURCE.txt';before=old.read_text('utf8');actual=m['prompt']
 assert before==actual+'\n' and m['status']=='ACTIVE' and m['rrule']=='FREQ=HOURLY;INTERVAL=1' and m['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 canonical=R/'CURRENT_ACTUAL71_WITH_HUMAN_GPU_STATUS_MONITOR_SOURCE_APP_CANONICAL_ACTUAL.txt'
 with canonical.open('x',encoding='utf8') as f:f.write(actual)
 with (R/'APP_TRAILING_NEWLINE_NORMALIZATION_AND_ARCHIVE_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_pre_record_assertion_retained=True,failed_before_record_tag_commit_or_archive_directory=True,only_difference='App saved prompt omitted the single final newline; all other characters, ACTIVE/hourly/target exact',original_source_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),actual_app_canonical_source_SHA=hashlib.sha256(canonical.read_bytes()).hexdigest(),old_source_file_preserved=True,no_host_training_budget_or_monitor_guard_change=True),f,indent=2)
 oldsource=N/'archive_actual71_http_channel_lifetime_fix_unique_once.py';s=oldsource.read_text('utf8');needle='CURRENT_ACTUAL71_WITH_HUMAN_GPU_STATUS_MONITOR_SOURCE.txt';assert s.count(needle)==1;s=s.replace(needle,canonical.name,1)
 new=N/'ARCHIVE_ACTUAL71_EXACT_APP_SOURCE_V2.py'
 with new.open('x',encoding='utf8') as f:f.write(s)
 ast.parse(s);exec(compile(s,str(new),'exec'),{'__name__':'actual71_archive_v2','__file__':str(new)})
except BaseException:
 with (R/('ACTUAL71_ARCHIVE_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),resume_existing_objects_only_no_repeat_record=True),f,indent=2)
 raise

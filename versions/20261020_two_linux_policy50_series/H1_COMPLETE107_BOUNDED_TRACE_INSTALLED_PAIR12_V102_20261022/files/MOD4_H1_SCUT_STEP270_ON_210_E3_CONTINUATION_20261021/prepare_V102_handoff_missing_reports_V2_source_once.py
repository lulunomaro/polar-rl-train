from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;R=T/'reports'
old=T/'prepare_V102_complete107_bounded_trace_pair12_handoff_archive_once.py';new=T/'prepare_V102_complete107_bounded_trace_pair12_handoff_archive_V2_once.py'
source=old.read_text('utf8')
with (R/'V102_HANDOFF_READER_V1_ORIGINAL_HEALTH_PATH_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),actual_returncode=1,helper=str(old),helper_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),error_type='FileNotFoundError',original_error="[Errno 2] No such file or directory: 'C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\H1_STEP270_E3_BOUNDED_TRACE_PAIR_V12_20261022\\payloads\\h1\\clock_training_health.py'",original_traceback_scope='main line21 H(p) -> pathlib.read_bytes -> pathlib.open -> io.open FileNotFoundError',actual_manifest_health_relative='job0/runtime/isaac/mod4/clock_training_health.py',health_report_was_already_created=True,no_training_transport_GPU_account_write_or_training_failure=True,old_helper_not_rerun=True),f,indent=2)
source=source.replace("('clock_training_health.py','853b", "('job0/runtime/isaac/mod4/clock_training_health.py','853b")
needle="put(R/'V102_H1_COMPLETE107_HEALTH_DISK_SAVEDSTOP_EPISODE387_ACTUAL.json',health_report)";assert source.count(needle)==1
source=source.replace(needle,"health_report=read(R/'V102_H1_COMPLETE107_HEALTH_DISK_SAVEDSTOP_EPISODE387_ACTUAL.json');assert health_report['original_health_SHA']==H(healthpaths[0]) and health_report['H1_current_episode_snapshot']==proof['models']['h1']['H1_current_episode_snapshot']")
source=source.replace(";ns={};exec(compile(ast.parse(audit.read_text('utf8')).body[0].value,'unused_docstring','exec'),{}) if False else None",'')
ast.parse(source);new.open('x',encoding='utf8').write(source)
print(json.dumps(dict(new_missing_reports_only_helper=str(new),no_old_once_reexecution=True)))

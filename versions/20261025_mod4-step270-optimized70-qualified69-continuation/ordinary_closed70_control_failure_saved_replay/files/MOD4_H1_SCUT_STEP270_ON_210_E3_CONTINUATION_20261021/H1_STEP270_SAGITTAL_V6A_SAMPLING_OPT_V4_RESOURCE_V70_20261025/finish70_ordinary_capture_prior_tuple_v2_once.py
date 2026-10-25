"""New entry after local prior-index tuple error, before any Git/archive mutation."""
from pathlib import Path
import ast,json,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
try:
 old=N/'ARCHIVE70_ORDINARY_EXACT_SOURCE.py';source=old.read_text('utf8')
 needle="for p in (S/'COMPLETE_FILE_CAPTURE_INDEX.json'):ns['prior'](p)";assert source.count(needle)==1
 source=source.replace(needle,"for p in (S/'COMPLETE_FILE_CAPTURE_INDEX.json',):ns['prior'](p)",1)
 new=N/'ARCHIVE70_ORDINARY_EXACT_SOURCE_V2.py'
 with new.open('x',encoding='utf8') as f:f.write(source)
 ast.parse(source)
 with (R/'ARCHIVE70_LOCAL_PRIOR_TUPLE_FIX_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_error_retained=True,original_failed_before_archive_directory_or_git_mutation=True,only_change='One-element tuple comma for prior capture-index enumeration',no_experiment_remote_budget_or_binary_read=True),f,indent=2)
 exec(compile(source,str(new),'exec'),{'__name__':'ordinary70_capture_v2','__file__':str(new)})
except BaseException:
 with (R/('CLOSED70_ORDINARY_ARCHIVE_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),resume_existing_objects_only=True),f,indent=2)
 raise

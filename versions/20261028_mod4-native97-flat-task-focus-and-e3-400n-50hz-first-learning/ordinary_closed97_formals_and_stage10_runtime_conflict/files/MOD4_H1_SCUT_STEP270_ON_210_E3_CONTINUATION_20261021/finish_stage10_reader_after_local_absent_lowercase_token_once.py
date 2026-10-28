from pathlib import Path
import json,time,ast
T=Path(__file__).resolve().parent
p=T/'prepare_stage10_readonly_terminal_new_source_once.py'
out=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/NEW_HOST_STAGE10_READONLY_TERMINAL_FULL_LOG_SOURCE_V1'
assert out.is_dir() and sorted(x.name for x in out.iterdir())==['reports'] and not list((out/'reports').iterdir())
with (out/'reports/ORIGINAL_LOCAL_PREPARER_ABSENT_LOWERCASE_TOKEN_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),entry=str(p),exception='AssertionError: stage9',cause='Stage9 source has no lowercase stage9 token; strict preparer stopped before any new entry was written',no_entry_execution_network_credential_GPU_model_or_account=True),f,indent=2)
s=p.read_text(encoding='utf8')
for a,b in [("assert not out.exists()\nout.mkdir();(out/'reports').mkdir()","assert out.is_dir() and (out/'reports').is_dir()"),(" 'stage9':'stage10',\n",'')]:
 assert s.count(a)==1;s=s.replace(a,b)
ast.parse(s)
exec(compile(s,str(p),'exec'),dict(__file__=str(p),__name__='__main__'))

from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parent;old=P/'review_NEW97_H1_formal_initial_whole_CPU_UNUSED_once.py'
s=old.read_text('utf8').replace('verify_saved_migration,NATIVE_CONTRACT','verify_saved_migration,NATIVE_CONTRACT,SOURCE_PINS',1)
a="assert full['UniSuperMimic_test_contract']==NATIVE_CONTRACT;verify_saved_migration(full,p)"
assert s.count(a)==1;s=s.replace(a,a+";assert native['args']==SOURCE_PINS['native_args']",1)
new=P/'review_NEW97_H1_formal_initial_whole_CPU_UNUSED_once_v2.py'
with new.open('x',encoding='utf8') as f:f.write(s)
ast.parse(s)
v=dict(frozen=True,unused=True,selected=new.name,SHA=hashlib.sha256(new.read_bytes()).hexdigest(),original_unused_v1_retained=old.name,delta='Explicit saved native args equal already-admitted same-architecture source args; other closure/model/optimizer checks unchanged',model_or_fixture_executions=0)
with (P/'FROZEN_UNUSED_H1_REVIEWER_V2_INDEX.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
with (P/'reports/LOCAL_REVIEWER_V2_PREPARATION_SHELL_PARSE_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(error='PowerShell ParserError: missing argument in parameter list in nested quoted Python -c command',original_tool_result='1df2c5',before_Python_or_file_model_network_execution=True,corrected_by='This explicit file-based preparer; no frozen V1 changes'),f,indent=2)
print(v['SHA'])

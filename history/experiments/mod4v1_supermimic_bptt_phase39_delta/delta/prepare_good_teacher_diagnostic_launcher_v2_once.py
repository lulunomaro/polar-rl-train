"""Retain the V1 missing-interpreter failure; derive a NEW configured-launcher call."""
from pathlib import Path
import json,hashlib,ast,time
R=Path(__file__).resolve().parent;old=R/'diagnose_good_holdout_bootstrap_teacher_identity_once.py';new=R/'diagnose_good_holdout_bootstrap_teacher_identity_v2_once.py';out=R/'reports/GOOD_HOLDOUT_TEACHER_DIAGNOSTIC_LAUNCHER_PREEXEC_ERRATUM_V1.json';assert not new.exists()and not out.exists();failed=json.loads((R/'reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V1.json').read_bytes());assert failed['returncode']==127 and failed['stdout']==''and failed['stderr']=='bash: python: command not found\n';raw=old.read_bytes();t=raw.decode()
for a,b in [('GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V1.json','GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2.json'),('GOOD_HOLDOUT_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_STARTED_ONCE.json','GOOD_HOLDOUT_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2_STARTED_ONCE.json'),('ACTUAL_GOOD_HOLDOUT_TEACHER_METADATA_SCHEMA_DIAGNOSIS_NOT_MODEL_OR_NEW_PREFLIGHT','ACTUAL_GOOD_HOLDOUT_TEACHER_METADATA_SCHEMA_DIAGNOSIS_V2_NOT_MODEL_OR_NEW_PREFLIGHT'),("'python -B -c '+shlex.quote(code)","'PYTHONDONTWRITEBYTECODE=1 '+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code)")]:
 assert t.count(a)==1;t=t.replace(a,b)
ast.parse(t)
with new.open('x',encoding='utf8',newline='\n')as f:f.write(t)
v=dict(kind='MISSING_REMOTE_DEFAULT_PYTHON_RETAINED_NEW_CONFIGURED_LAUNCHER_SOURCE',epoch=time.time(),old_RC=127,old_original_metadata_reads=0,zero_read_count_basis='remote shell command not found before executing Python code',old_source_SHA256=hashlib.sha256(raw).hexdigest(),new_source=new.name,new_source_SHA256=hashlib.sha256(t.encode()).hexdigest(),old_error_receipt_preserved=True,actual_new_remote_or_model_SDK_C_operations=0)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

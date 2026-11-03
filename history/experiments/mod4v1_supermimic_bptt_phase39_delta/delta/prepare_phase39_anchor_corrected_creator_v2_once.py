"""Retain failed source-preparer; correct only its actual archive-template anchor."""
from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;old=R/'prepare_archive_phase39_binding_teacher_schema_once.py';new=R/'prepare_archive_phase39_binding_teacher_schema_v2_once.py';out=R/'reports/PHASE39_PREPARER_ANCHOR_FAILURE_AND_V2_SOURCE_V1.json';assert not new.exists()and not out.exists()and not(R/'archive_phase39_binding_teacher_schema_delta.py').exists()and not(R/'reports/PHASE39_ARCHIVE_SOURCE_PREPARED_V1.json').exists()and not(R.parent/'repo-lqr/history/experiments/mod4v1_supermimic_bptt_phase39_delta').exists();raw=old.read_bytes();t=raw.decode();a="anchor='rows=[];files=[];refs=0;D.mkdir(parents=True)'";b="anchor='D.mkdir(parents=True);rows=[];files=[];refs=0'";assert t.count(a)==1;t=t.replace(a,b);ast.parse(t)
with new.open('x',encoding='utf8',newline='\n')as f:f.write(t)
v=dict(kind='PHASE39_SOURCE_CREATOR_WRONG_ANCHOR_PREEXEC_FAILURE_RETAINED',epoch=time.time(),old_source_SHA256=hashlib.sha256(raw).hexdigest(),actual_old_exit=1,actual_error='AssertionError template anchor statement order',actual_phase='before writing new archive SOURCE or any Git call',new_source=new.name,new_SHA256=hashlib.sha256(t.encode()).hexdigest(),old_script_and_failures_preserved=True,actual_model_SDK_CPU_native_C_Git_operations=0)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

"""Prepare a distinct, unconsumed A2 scientific application caller; source only."""
from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;old=R/'run_phase1_v4_scientific_capture_application_once.py';new=R/'run_phase1_v4_admission2_scientific_capture_application_once.py';out=R/'reports/PHASE1_V4_ADMISSION2_SCIENTIFIC_CALLER_SOURCE_V1.json';assert not new.exists()and not out.exists();raw=old.read_bytes();t=raw.decode()
for a,b in [('PHASE1_V4_ACTUAL_SCIENTIFIC_CAPTURE_APPLICATION_V1.json','PHASE1_V4_ADMISSION2_ACTUAL_SCIENTIFIC_CAPTURE_APPLICATION_V1.json'),('PHASE1_V4_SCIENTIFIC_CAPTURE_APPLICATION_STARTED_ONCE.json','PHASE1_V4_ADMISSION2_SCIENTIFIC_CAPTURE_APPLICATION_STARTED_ONCE.json'),('PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_LATEST_CLOSED_RESULT_PATH.json','PHASE1_E3_CAPTURE_V4_ADMISSION2_LATEST_CLOSED_RESULT_PATH.json'),('PHASE1_V4_SCIENTIFIC_CACHE_APPLICATION_V1_','PHASE1_V4_ADMISSION2_SCIENTIFIC_CACHE_APPLICATION_V1_'),('NEW_V4_SCIENTIFIC_ORIGINAL_WHOLE_FINALS_ONCE_NOT_STATUS_OR_GIT','NEW_V4_ADMISSION2_SCIENTIFIC_ORIGINAL_WHOLE_FINALS_ONCE_NOT_STATUS_OR_GIT')]:
 assert t.count(a)==1,(a,t.count(a));t=t.replace(a,b)
a='phase1_scientific_capture_cache_apply_v1.py';assert t.count(a)==3;t=t.replace(a,'phase1_scientific_capture_cache_apply_v2.py')
a="q['physical_JSON_opens']==q['JSON_decodes']==dict(worker_final=1,group_final=1)";assert t.count(a)==1;t=t.replace(a,"q['physical_JSON_opens']==q['original_byte_SHA256_calculations']==q['JSON_decodes']==dict(worker_final=1,group_final=1)")
ast.parse(t);program=(R/'phase1_scientific_capture_cache_apply_v2.py').read_bytes();ast.parse(program)
with new.open('x',encoding='utf-8',newline='\n')as f:f.write(t)
h=lambda b:hashlib.sha256(b).hexdigest();v=dict(kind='NEW_ADMISSION2_SCIENTIFIC_CALLER_SOURCE_NOT_EXECUTED',epoch=time.time(),original_caller=dict(name=old.name,bytes=len(raw),SHA256=h(raw)),new_caller=dict(name=new.name,bytes=len(new.read_bytes()),SHA256=h(new.read_bytes())),new_cache_program=dict(name='phase1_scientific_capture_cache_apply_v2.py',bytes=len(program),SHA256=h(program)),V1_source_preserved_unexecuted=True,actual_target_FINAL_model_SDK_C_resource_operations=0,requires_A2_actual_qualified_closed_double_wait_EX_before_any_marker_or_connection=True)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

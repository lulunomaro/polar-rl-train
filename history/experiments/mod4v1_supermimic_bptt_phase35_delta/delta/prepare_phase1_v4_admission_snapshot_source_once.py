"""NEW own-root one-shot published readiness/wait diagnostic; no watcher/retry."""
from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;old=R/'read_phase1_capture_first_actual_admission_v1_once.py';new=R/'read_phase1_capture_v4_actual_admission_snapshot_once.py';out=R/'reports/PHASE1_V4_ADMISSION_SNAPSHOT_SOURCE_V1.json';assert not new.exists()and not out.exists();raw=old.read_bytes();t=raw.decode()
for a,b in [('PHASE1_E3_CAPTURE_V1_FIRST_ACTUAL_ADMISSION_SNAPSHOT.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_ADMISSION_SNAPSHOT.json'),('PHASE1_E3_CAPTURE_V1_ORIGINAL_PARENT_DISPATCH_ONCE.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ORIGINAL_PARENT_DISPATCH_ONCE.json'),('ONE_PUBLISHED_PHASE1_CAPTURE_ACTUAL_ADMISSION_SNAPSHOT_V1','ONE_PUBLISHED_PHASE1_CAPTURE_ACTUAL_ADMISSION_SNAPSHOT_V4')]:
 assert t.count(a)==1;t=t.replace(a,b)
ast.parse(t)
with new.open('x',encoding='utf-8',newline='\n')as f:f.write(t)
v=dict(kind='NEW_V4_ONE_METADATA_DIAGNOSTIC_SOURCE_NOT_EXECUTED',epoch=time.time(),original=old.name,original_SHA256=hashlib.sha256(raw).hexdigest(),new=new.name,SHA256=hashlib.sha256(new.read_bytes()).hexdigest(),actual_read_or_parent_or_model_operations=0,metadata_whitelist_unchanged=True)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

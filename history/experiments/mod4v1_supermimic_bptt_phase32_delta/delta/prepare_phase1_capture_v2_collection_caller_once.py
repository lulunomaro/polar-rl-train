"""NEW V2 own collection caller, only fixed source/dispatch/output purpose changes."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;old=R/'collect_phase1_capture_v1_closed_metadata_once.py';new=R/'collect_phase1_capture_bootstrap_v2_closed_metadata_once.py';out=R/'reports/PHASE1_BOOTSTRAP_V2_COLLECTION_CALLER_SOURCE_V1.json';assert not new.exists()and not out.exists()
raw=old.read_bytes();text=raw.decode();changes=[('source_phase1_capture_result_collector_v1','source_phase1_capture_result_collector_v2'),('PHASE1_CAPTURE_V1_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json','PHASE1_CAPTURE_BOOTSTRAP_V2_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json'),('PHASE1_E3_CAPTURE_V1_LATEST_CLOSED_RESULT_PATH.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_LATEST_CLOSED_RESULT_PATH.json'),('c6847784e4733f53767dc20f064b584eecda02f1046d88855f25d8e8381eca6c','8a0dfd808483687f3a718d327c6dddf77d6989ed140eddc4de6dc262b832c29c'),('5deb47562c45109d35ad6b502a047802ed29aee40dff349e34888f4c488abe51','f810645b940445863ea4375f5b27b5fea15e5b2b0eaff53aacf88ffb08ffb1dd'),('PHASE1_E3_CAPTURE_V1_ACTUAL_CLOSED_','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_'),('PHASE1_E3_CAPTURE_V1_ORIGINAL_PARENT_DISPATCH_ONCE.json','PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ORIGINAL_PARENT_DISPATCH_ONCE.json')]
for a,b in changes:assert text.count(a)==1,a;text=text.replace(a,b)
ast.parse(text)
with new.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
v=dict(kind='NEW_V2_COLLECTION_CALLER_SOURCE_ONLY_NOT_EXECUTED',epoch=time.time(),old=old.name,old_SHA256=hashlib.sha256(raw).hexdigest(),new=new.name,bytes=len(new.read_bytes()),SHA256=hashlib.sha256(new.read_bytes()).hexdigest(),changed_only_fixed_source_and_new_purpose_paths=True,actual_collect_SDK_parent_model_raw_C_operations=0)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

"""NEW fixed V4 collection caller; metadata paths/source seal only, not executed."""
from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;old=R/'collect_phase1_capture_reset_binding_v3_closed_metadata_once.py';new=R/'collect_phase1_capture_device_binding_v4_closed_metadata_once.py';out=R/'reports/PHASE1_DEVICE_BINDING_V4_COLLECTION_CALLER_SOURCE_V1.json';assert not new.exists()and not out.exists();b=old.read_bytes();t=b.decode()
for a,z in [('source_phase1_capture_result_collector_v3','source_phase1_capture_result_collector_v4'),('PHASE1_CAPTURE_RESET_BINDING_V3_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json','PHASE1_CAPTURE_DEVICE_BINDING_V4_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json'),('PHASE1_E3_CAPTURE_RESET_BINDING_V3_LATEST_CLOSED_RESULT_PATH.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_LATEST_CLOSED_RESULT_PATH.json'),('2f6188fe03958bfd237efab6c22ea6f63ffa61c54608144607db5d8bc9ff577f','23a5267920106b40b1efcf5db7921a16c6418621365d18933f0c9d69bfefc594'),('71e4df44944aa9c4b81702bd673259107570ddd49bd692993b9fe81d1e7a303d','ff037967e391148328fc7a3400eb30b41b1123cab5313954d87e2d779067ba2c'),('PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_CLOSED_','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_CLOSED_'),('PHASE1_E3_CAPTURE_RESET_BINDING_V3_ORIGINAL_PARENT_DISPATCH_ONCE.json','PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ORIGINAL_PARENT_DISPATCH_ONCE.json')]:
 assert t.count(a)==1,a;t=t.replace(a,z)
ast.parse(t)
with new.open('x',encoding='utf-8',newline='\n')as f:f.write(t)
raw=new.read_bytes();v=dict(kind='NEW_V4_COLLECTION_CALLER_SOURCE_ONLY',epoch=time.time(),original=old.name,original_SHA256=hashlib.sha256(b).hexdigest(),new=new.name,bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),changed_only_fixed_sources_and_new_purpose_paths=True,actual_collection_SDK_parent_model_raw_canonical_operations=0)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

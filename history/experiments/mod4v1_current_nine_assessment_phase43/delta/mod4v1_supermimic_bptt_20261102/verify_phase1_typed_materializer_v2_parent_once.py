"""Parent readonly verifier call; no old tests/materializer entry/native operations."""
from pathlib import Path
import hashlib,io,contextlib,json,runpy,time
R=Path(__file__).resolve().parent;D=R/'source_phase1_typed_capture_materializer_v2';out=R/'reports/PHASE1_TYPED_MATERIALIZER_V2_PARENT_READONLY_VERIFY_V1.json';assert not out.exists();H=lambda b:hashlib.sha256(b).hexdigest();seal=(D/'SOURCE_SEAL.json').read_bytes();program=(D/'verify_source_seal_v2.py').read_bytes();assert(len(seal),H(seal))==(4060,'02425bc3a05a2556f2ef509adadd96c13bf9d35948a5bdd9f90fe731cd809d41');assert(len(program),H(program))==(3132,'391cdc947067ea0e45c07a4ad841a3e6ef8271e85528e9d8ca97bd4efebe1d5d');buf=io.StringIO()
with contextlib.redirect_stdout(buf):runpy.run_path(str(D/'verify_source_seal_v2.py'),run_name='__main__')
v=json.loads(buf.getvalue());assert v['passed']and v['members']==18 and v['Python_AST_files']==9 and v['JSON_files']==5 and v['seal_SHA256']==H(seal)and v['content_root_SHA256']=='b62254ad746b0649dca810116354f753c8a48eb7ff785e2e076652a2172dc59e';assert(D/'SOURCE_SEAL.json').read_bytes()==seal and(D/'verify_source_seal_v2.py').read_bytes()==program
receipt=dict(kind='ACTUAL_PARENT_READONLY_MATERIALIZER_HISTORY_V2_SOURCE_VERIFICATION',epoch=time.time(),status='PASS_SOURCE_ONLY',verification=v,author_six_case_suite_replayed=False,whole_materializer_load_prepare_metadata_stage_or_native_called=False,actual_SDK_model_raw_C_Git_or_resource_operations=0,materializer_source_publication=2,Producer_wire_version=1,compact_wire_included=False,actual_Linux_preflight_passed=False,Gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt,indent=2))

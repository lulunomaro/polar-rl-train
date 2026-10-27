"""Small JSON fixtures; existing source only. No real models or network."""
from pathlib import Path
import copy,hashlib,json,sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from native87_control_dependency_source_contract_v1 import *
D=Path(__file__).resolve().parent;T=D.parent.parent
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/h1'/RELATIVE
qpath=N/'reports/AVAILABLE_TWO_NATIVE87R2_SOURCE_PREPARED_ACTUAL.json';q=json.loads(qpath.read_bytes())
raw=OLD.read_bytes();SHA=hashlib.sha256(raw).hexdigest();checks=[]
def good(v,name):
 assert v,name
 checks.append(name)
def reject(fn,name):
 try:fn()
 except (ValueError,FileNotFoundError,KeyError,TypeError):checks.append(name);return
 raise AssertionError('unexpected acceptance '+name)
B=Path(q['payloads']['h1']);manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
good(SHA==q['specs']['h1']['owner_control_dependency_binding_SHA'],'old_h1_binding_equals_R2_spec_pin')
good(not (B/RELATIVE).exists() and not any(r['relative']==RELATIVE for r in manifest['files']),'actual_R2_bundle_and_manifest_missing_required_h1_metadata')
reject(lambda:validate_control_dependency_closure(B,q['specs']['h1'],manifest),'actual_R2_dependency_closure_rejected')
with tempfile.TemporaryDirectory(prefix='native87_control_JSON_fixture_') as temp:
 root=Path(temp);(root/RELATIVE).write_bytes(raw)
 m=dict(files=[dict(relative=RELATIVE,SHA=SHA,bytes=len(raw))])
 good(validate_control_dependency_closure(root,q['specs']['h1'],m)['passed'],'synthetic_exact_binding_manifest_positive')
 reject(lambda:validate_control_dependency_closure(root,q['specs']['h1'],dict(files=[])),'unmanifested_binding_refused')
 bad=copy.deepcopy(m);bad['files'].append(dict(bad['files'][0]))
 reject(lambda:validate_control_dependency_closure(root,q['specs']['h1'],bad),'duplicate_binding_manifest_row_refused')
 bad=copy.deepcopy(m);bad['files'][0]['SHA']='a'*64
 reject(lambda:validate_control_dependency_closure(root,q['specs']['h1'],bad),'wrong_binding_SHA_refused')
 bad=copy.deepcopy(q['specs']['h1']);bad.pop('owner_control_dependency_binding_SHA')
 reject(lambda:validate_control_dependency_closure(root,bad,m),'missing_spec_pin_refused')
 v=json.loads(raw);v['DEPS_root']='/home/unapproved/deps';modified=json.dumps(v).encode();(root/RELATIVE).write_bytes(modified)
 wrong=hashlib.sha256(modified).hexdigest();bad=dict(q['specs']['h1'],owner_control_dependency_binding_SHA=wrong)
 reject(lambda:validate_control_dependency_closure(root,bad,dict(files=[dict(relative=RELATIVE,SHA=wrong,bytes=len(modified))])),'selfconsistent_wrong_dependency_root_refused')
good(validate_control_dependency_closure(Path(q['payloads']['recovery']),q['specs']['recovery'],dict(files=[]))['h1_binding_required'] is False,'target72_loopback_not_falsely_given_h1_dependency')
result=dict(passed=True,count=len(checks),checks=checks,scope='source_and_small_JSON_fixture_only',actual_control_connection_tested=False,source_SDK_or_model_reexecuted=False,
 inputs=[dict(path=str(OLD),bytes=len(raw),SHA=SHA),dict(path=str(qpath),SHA=hashlib.sha256(qpath.read_bytes()).hexdigest())])
with (D/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(result))

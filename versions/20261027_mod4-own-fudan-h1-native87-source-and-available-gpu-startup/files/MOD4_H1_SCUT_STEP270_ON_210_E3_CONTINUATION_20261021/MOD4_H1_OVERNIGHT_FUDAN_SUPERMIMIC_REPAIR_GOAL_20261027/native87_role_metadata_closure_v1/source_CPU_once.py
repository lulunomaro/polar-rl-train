"""New metadata/AST tests only. No SDK, checkpoint, remote dependency or network."""
from pathlib import Path
import ast,copy,hashlib,json,sys,tempfile
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
import native87_protocol_v1 as protocol
from native87_role_metadata_closure_v1 import *
T=D.parent.parent;N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
old=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/h1'/RELATIVE
raw=old.read_bytes();q=json.loads((N/'reports/AVAILABLE_TWO_NATIVE87R2_SOURCE_PREPARED_ACTUAL.json').read_bytes());checks=[]
def yes(v,name):
 assert v,name
 checks.append(name)
def reject(fn,name):
 try:fn()
 except (ValueError,AssertionError,KeyError,FileNotFoundError,TypeError):checks.append(name);return
 raise AssertionError('unexpected acceptance: '+name)
yes(hashlib.sha256(raw).hexdigest()==EXPECTED_SHA,'old_binding_exact_source_SHA')
task=dict(key='h1',execution_backend='source210',owner_control_dependency_binding_SHA=EXPECTED_SHA)
c=dict(candidate_pins={RELATIVE:EXPECTED_SHA});m=dict(files=[dict(relative=RELATIVE,SHA=EXPECTED_SHA,bytes=len(raw))])
with tempfile.TemporaryDirectory(prefix='native87_role_metadata_fixture_') as temp:
 B=Path(temp);(B/RELATIVE).write_bytes(raw)
 yes(validate_role_metadata_closure(B,task,c,m)['passed'],'exact_h1_Task_contract_manifest_file_positive')
 for name,which in [('Task','task'),('contract','contract'),('manifest','manifest')]:
  t=copy.deepcopy(task);cc=copy.deepcopy(c);mm=copy.deepcopy(m)
  if which=='task':t.pop('owner_control_dependency_binding_SHA')
  elif which=='contract':cc['candidate_pins']={}
  else:mm['files']=[]
  reject(lambda:validate_role_metadata_closure(B,t,cc,mm),'missing_'+name+'_pin_refused')
 mm=copy.deepcopy(m);mm['files'].append(dict(mm['files'][0]));reject(lambda:validate_role_metadata_closure(B,task,c,mm),'duplicate_manifest_binding_refused')
 (B/RELATIVE).write_bytes(raw+b' ');reject(lambda:validate_role_metadata_closure(B,task,c,m),'changed_binding_bytes_refused')
 (B/RELATIVE).unlink();reject(lambda:validate_role_metadata_closure(B,task,c,m),'missing_binding_file_refused')
 yes(validate_role_metadata_closure(B,dict(key='recovery',execution_backend='target72'),dict(candidate_pins={}),dict(files=[]))['scope']=='target72_original_loopback_not_required','target72_explicit_not_required')
cpu=json.loads((N/'reports/AVAILABLE_TWO_NATIVE87R2_ACTUAL_SOURCE_CPU_RETURNED_ACTUAL.json').read_bytes())
for key in ('h1','recovery'):
 spec=cpu['specs_with_preinstalled_CPU_proof'][key];e=copy.deepcopy(cpu['results'][key]['ready_envelope'])
 row=dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=e,original_error=False)
 yes(not protocol.native87_valid_ready(row,spec),'old_'+key+'_CPU_without_new_closure_flag_refused')
 v=e['value'];v['role_control_dependency_metadata_closure_checked']=True
 if key=='h1':
  v['owner_control_dependency_binding_SHA']=EXPECTED_SHA
  v['role_control_dependency_CPU']=dict(checked=True,scope='source210_h1_exact_installed_dependency_SHA_and_import',actual_installed_dependencies_verified=True,binding_SHA=EXPECTED_SHA)
 else:v['role_control_dependency_CPU']=dict(checked=True,scope='target72_original_loopback_not_required',actual_installed_dependencies_verified=False)
 e['SHA']=protocol.digest(v)
 yes(protocol.native87_valid_ready(row,spec),'synthetic_'+key+'_explicit_new_role_closure_positive')
 v['role_control_dependency_CPU']['actual_installed_dependencies_verified']=key!='h1';e['SHA']=protocol.digest(v)
 yes(not protocol.native87_valid_ready(row,spec),'wrong_'+key+'_installed_dependency_claim_refused')
bad=copy.deepcopy(q['specs']['h1']);bad.pop('owner_control_dependency_binding_SHA')
reject(lambda:protocol.validate_spec(bad),'h1_spec_missing_control_pin_refused')
entry=ast.parse((D/'target_native87_source_sdk_cpu_v1.py').read_bytes());main=next(x for x in entry.body if isinstance(x,ast.FunctionDef) and x.name=='main')
calls=[x for x in ast.walk(main) if isinstance(x,ast.Call)]
verify=next(x for x in calls if isinstance(x.func,ast.Name) and x.func.id=='verify_dependencies')
loads=[x for x in calls if isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='torch' and x.func.attr=='load']
yes(len(loads)==1 and verify.lineno<loads[0].lineno,'original_forwarder_verify_before_only_bootstrap_torch_load')
guard=ast.parse((D/'native87_source_guard_v1.py').read_bytes())
yes(any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='validate_role_metadata_closure' for x in ast.walk(guard)),'sourceguard_really_calls_role_metadata_closure')
def fn(tree,name):return ast.dump(next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name))
oldguard=ast.parse((D/'ORIGINAL_native87_source_guard_v1.py.txt').read_bytes())
for name in ('validate_task_go','validate_whole_policy','validate_precontrol_actual'):
 yes(fn(guard,name)==fn(oldguard,name),name+'_AST_exact')
yes(protocol.KIND=='MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2','kind_unchanged')
with (D/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=len(checks),checks=checks,source_and_fixture_only=True,actual_installed_dependency_verify_executed=False,actual_checkpoint_or_SDK_or_network_executed=False),f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks))))

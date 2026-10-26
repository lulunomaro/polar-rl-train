"""No remote/GPU: explicit new task readiness and exact original accounting boundaries."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import time

J=Path(__file__).resolve().parent
P=J.parent/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
before=(P/'controllers/three_slot_common_v1.py').read_text('utf8')
after=(J/'payload/three_slot_common_v1.py').read_text('utf8')
def funcs(source):
    return {x.name:x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef)}
a,b=funcs(before),funcs(after)
for name in a:
    if name!='valid_ready':assert ast.dump(a[name])==ast.dump(b[name]),name
v=copy.deepcopy(b['valid_ready']);assert isinstance(v.body[0],ast.If)
assert ast.unparse(v.body[0].test)=="spec.get('finite_method_test')"
v.body=v.body[1:];assert ast.dump(v)==ast.dump(a['valid_ready'])
owner_old=funcs((P/'controllers/three_slot_finite_owner_v1.py').read_text('utf8'))['owner']
owner_new=funcs((J/'owner_source/three_slot_finite_owner_v1.py').read_text('utf8'))['owner']
def nested_account(f):return next(x for x in f.body if isinstance(x,ast.FunctionDef) and x.name=='account')
assert ast.dump(nested_account(owner_old))==ast.dump(nested_account(owner_new))
for name in ('three_slot_finite_node_v1.py','three_real_gpu_resource_v1.py','forwarded_original_owner_control_v1.py'):
    assert (J/'payload'/name).read_bytes()==(P/'payloads/e2'/name).read_bytes()
scope={'json':json,'hashlib':hashlib}
exec(compile(ast.Module(body=[b['valid_ready'],b['terminal'],b['charge_values']],type_ignores=[]),'<actual-method-ready-and-original-charge>', 'exec'),scope)
q=json.loads((J/'reports/REVIEWABLE_FINITE_SINGLE_GPU_METHOD_TEST_PAYLOAD_AND_ORIGINAL_WRITER_PLAN_ACTUAL.json').read_bytes());spec=q['spec']
value=dict(passed=True,kind='UNISUPERMIMIC_MOD4_NATIVE30_ACTION6_FINITE_METHOD_TEST',source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],upstream_revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',actual_installed_CPU_passed=True,native_joint_states=30,actions=6,source80_actual_cost_models_allout_passed=True,not_production_E2_source_or_skill_qualification=True)
def row(v):return dict(key='e2',phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True))
assert scope['valid_ready'](row(value),spec)
rejected=[]
for name,new in [('source_SHA','0'*64),('GPU_UUID','other'),('upstream_revision','0'*40),('native_joint_states',6),('actions',30),('actual_installed_CPU_passed',False),('source80_actual_cost_models_allout_passed',False),('not_production_E2_source_or_skill_qualification',False),('kind','closed_same_backend_production')]:
    bad=dict(value);bad[name]=new;assert not scope['valid_ready'](row(bad),spec);rejected.append(name)
bad=row(value);bad['manifest_SHA']='0'*64;assert not scope['valid_ready'](bad,spec);rejected.append('manifest_SHA')
bad=row(value);bad['closed_source_CPU']['SHA']='0'*64;assert not scope['valid_ready'](bad,spec);rejected.append('HMAC-bound_CPU_result_digest')
bad=row(value);bad['original_error']=True;assert not scope['valid_ready'](bad,spec);rejected.append('original_error')
charge=scope['charge_values'];c=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.);segment=dict(experts={},charged_expert_seconds=0.)
go=dict(e2=dict(learning_started_epoch=100.,max_parent_seconds=3900))
c,segment=charge(c,segment,go,{},102.)
terminal=dict(e2=dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=105.))
c,segment=charge(c,segment,go,terminal,108.);c,segment=charge(c,segment,go,terminal,110.)
assert segment['experts']['e2']['charged_seconds']==5. and c['charged_training_seconds']==5.
with (J/'reports/EXACT_NEW_METHOD_READY_NEGATIVES_AND_ORIGINAL_ACCOUNTING_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,explicit_new_method_ready_positive=True,rejected_fields=rejected,original_production_valid_ready_after_removing_exact_new_branch_AST_equal=True,all_other_common_functions_AST_exact=True,owner_nested_account_AST_exact=True,node_and_resource_control_bytes_exact=True,actual_original_charge_terminal_repeat_sumonce5=True,no_remote_GPU_CUDA_or_budget_write=True),f,indent=2)
print(json.dumps(dict(passed=True,negative_cases=len(rejected),original_accounting_exact=True)))

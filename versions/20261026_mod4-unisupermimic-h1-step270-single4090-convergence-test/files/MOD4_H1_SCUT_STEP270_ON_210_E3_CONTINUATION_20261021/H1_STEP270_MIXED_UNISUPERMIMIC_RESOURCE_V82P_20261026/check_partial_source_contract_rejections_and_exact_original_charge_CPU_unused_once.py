from pathlib import Path
import ast,copy,json,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026';R=N/'reports'
g=ast.parse((N/'candidates/healthy_pair_failed_method_same_V8_source_guard_v1.py').read_text('utf8'));load=next(n for n in g.body if isinstance(n,ast.FunctionDef) and n.name=='load')
a=next(n for n in load.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='proof' for x in n.targets));index=load.body.index(a);condition=load.body[index+1];assert isinstance(condition,ast.Assert)
check=compile(ast.fix_missing_locations(ast.Module(body=[condition],type_ignores=[])),'actual82P_partial_guard_condition','exec')
proof=dict(qualification_scope='healthy_h1_recovery_models_with_failed_method_all3_original_cost',models=dict(h1={},recovery={}),original_slots_cost={k:dict(charged_seconds=20.0,duration_bound_passed=True) for k in ('h1','e2','recovery')},failed_method=dict(original_error=True,no_qualified_model=True),actual_cost_sumonce=60.0)
exec(check,dict(key='h1',proof=proof));exec(check,dict(key='recovery',proof=proof));rejected=[]
for label,modify in [('failed_e2_source',lambda p:p['models'].update(e2={})),('missing_e2_cost',lambda p:p['original_slots_cost'].pop('e2')),('fee_rewrite',lambda p:p.update(actual_cost_sumonce=40.0)),('masked_error',lambda p:p['failed_method'].update(original_error=False)),('failed_model_promotion',lambda p:p['failed_method'].update(no_qualified_model=False)),('duration_false',lambda p:p['original_slots_cost']['h1'].update(duration_bound_passed=False))]:
 p=copy.deepcopy(proof);modify(p)
 try:exec(check,dict(key='h1',proof=p))
 except AssertionError:rejected.append(label)
 else:raise AssertionError('mutation accepted '+label)
try:exec(check,dict(key='e2',proof=proof))
except AssertionError:rejected.append('wrong_method_source_key')
else:raise AssertionError('e2 accepted')
for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py'):
 # Prospective controllers are copied byte-exact by the binder, not modified in source preparation.
 assert (O/'controllers'/name).is_file()
f=lambda p,n:ast.dump(next(x for x in ast.parse(p.read_text('utf8')).body if isinstance(x,ast.FunctionDef) and x.name==n),include_attributes=False)
assert f(O/'controllers/three_slot_common_v1.py','charge_values')==f(T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026/controllers/three_slot_common_v1.py','charge_values')
result=dict(epoch=time.time(),passed=True,actual_guard_condition_executed=True,synthetic_rejections=rejected,original_owner_charge_values_AST_exact=True,not_installed_or_model_admission=True,no_remote_or_GPU_action=True)
with (R/'PARTIAL_SOURCE_CONTRACT_REJECTIONS_ORIGINAL_CHARGE_CPU_ACTUAL.json').open('x',encoding='utf8') as h:json.dump(result,h,indent=2)
print(json.dumps(dict(passed=True,rejections=len(rejected))))

from pathlib import Path
import ast,hashlib,json,types
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
def assignment(tree,name):return next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets))
def main():
 route=T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025/strict_user_forwarded_original210_transport_v1.py';raw=route.read_bytes();actual_route_PY=ast.literal_eval(assignment(ast.parse(raw),'PY'));assert actual_route_PY=='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
 entry=B/'install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v2_canonicalWorkerPython.py';tree=ast.parse(entry.read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='worker_python_from_control_alias');scope={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual selected converter source>','exec'),scope);convert=scope[fn.name]
 call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='code' and len(n.args)>3 and isinstance(n.args[3],ast.Call) and any(k.arg=='python' for k in n.args[3].keywords))
 job=ast.literal_eval(assignment(tree,'JOB'));worker='evaluate_E3_adapted97_source210_frozen600_once_v1.py';scope.update(JOB=job,route=types.SimpleNamespace(PY=actual_route_PY),authority={'synthetic_readonly_fixture':True},index={'manifest_SHA':'synthetic_source_fixture_only','local_source_SHAs':{worker:'synthetic_source_fixture_only'}})
 payload=eval(compile(ast.Expression(body=call.args[3]),'<actual d.code payload AST>','eval'),scope);control=eval(compile(ast.Expression(body=call.args[1]),'<actual d.code control interpreter AST>','eval'),scope)
 assert control==actual_route_PY and payload['control_route_PY']==actual_route_PY and payload['python']=='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
 remote=B/'remote_E3_source210_verify_metadata_CPU_and_detach_v2.py';rt=ast.parse(remote.read_bytes())
 def predicate(tree):
  return next(n for n in ast.walk(tree) if isinstance(n,ast.Assert) and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Subscript) and isinstance(n.test.left.value,ast.Name) and n.test.left.value.id=='v' and isinstance(n.test.left.slice,ast.Constant) and n.test.left.slice.value=='python')
 pred=predicate(rt);old=L/'E3_97_SOURCE210_FROZEN_RECIPE_DOMAIN_ADMISSION_SOURCE_20261029_V1/remote_E3_source210_verify_metadata_CPU_and_detach_v1.py';assert ast.dump(pred,include_attributes=False)==ast.dump(predicate(ast.parse(old.read_bytes())),include_attributes=False)
 compiled=compile(ast.Module(body=[pred],type_ignores=[]),'<UNCHANGED actual strict remote Python predicate>','exec');exec(compiled,{'v':payload});original_rejected=False
 try:exec(compiled,{'v':dict(payload,python=actual_route_PY)})
 except AssertionError:original_rejected=True
 assert original_rejected
 rejected=[]
 for x in ('/usr/bin/python3.12','/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.11','/tmp/python','python',None):
  try:convert(x)
  except AssertionError:rejected.append(x)
  else:raise AssertionError('Unknown alias accepted')
 assert convert(payload['python'])==payload['python']
 helper=ast.parse((B/'source210_project_launch_helpers_v1.py').read_bytes());assert ast.literal_eval(assignment(helper,'PY'))==payload['python']
 names=['evaluate_E3_adapted97_source210_frozen600_once_v1.py','E3_source210_target_source_SDK_metadata_admission_v1.py','e3_recipe_domain_telemetry_v1.py','e3_original_recipe_phase_catalog_v1.py','e3_frozen_worker_call_guard_v1.py','lossless_snapshot_pinned75d683.py','source210_project_launch_helpers_v1.py'];oldroot=L/'E3_97_SOURCE210_FROZEN_RECIPE_DOMAIN_ADMISSION_SOURCE_20261029_V1'
 for n in names:assert (B/n).read_bytes()==(oldroot/n).read_bytes()
 parsed=[]
 for p in B.glob('*.py'):ast.parse(p.read_bytes());parsed.append(p.name)
 codefile=B/'E3_source210_actual_receipts_readonly_CODE_v2.py';code=ast.literal_eval(assignment(ast.parse(codefile.read_bytes()),'CODE'));ast.parse(code);assert job in code and oldroot.name not in code
 report=dict(passed=True,actual_route_source=str(route),actual_route_source_SHA=hashlib.sha256(raw).hexdigest(),actual_route_PY_AST_constant=actual_route_PY,route_module_not_imported_or_called=True,actual_selected_d_code_control_argument=control,actual_selected_d_code_submitted_workerpython=payload['python'],actual_selected_payload_AST_executed_synthetic_other_fields=True,remote_canonical_assert_AST_identical=True,actual_original_alias_rejected_by_remote_predicate=original_rejected,converted_payload_accepted_by_same_predicate=True,converter_wrong_alias_negatives=rejected,supervisor_helper_uses_same_canonical=True,worker_CPU_metric_physics_queue_source_bytes_unchanged=names,all_selected_source_and_readonly_CODE_AST_passed=parsed,no_PT_raw_binary_credentials_SDK_GPU_remote_or_route_execution=True)
 with (B/'reports/REAL_ROUTE_ALIAS_SELECTED_PAYLOAD_STRICT_REMOTE_PREDICATE_CPU_ACTUAL.json').open('x') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(passed=True,real_route_alias=actual_route_PY,submitted_workerpython=payload['python'],negative_aliases=len(rejected),source_only=True)))
if __name__=='__main__':main()

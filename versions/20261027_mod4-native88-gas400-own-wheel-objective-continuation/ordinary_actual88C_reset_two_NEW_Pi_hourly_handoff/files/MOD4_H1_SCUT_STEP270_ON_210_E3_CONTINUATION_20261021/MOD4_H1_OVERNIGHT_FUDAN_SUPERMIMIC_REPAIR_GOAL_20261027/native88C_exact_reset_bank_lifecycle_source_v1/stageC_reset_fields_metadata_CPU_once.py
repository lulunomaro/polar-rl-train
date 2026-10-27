"""Only new stageC/reset fields. Does not execute the old31-case fixture."""
from pathlib import Path
import ast,json,sys,copy,hashlib,traceback
D=Path(__file__).resolve().parent;OLD=D.parent/'native88_first_policy_closure_review_source_v1';sys.path.insert(0,str(D))
import native88_closing_protocol_v1 as p
def read(path):return json.loads(path.read_bytes())
def main():
 checks=[]
 C='H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027';B=C.replace('V88C_','V88B_')
 for name in ('observe_native88_first_new_policy_finite_unused_once.py','collect_native88_finals_actual_cost_unused_once.py','review_native88_finals_initial_CPU_unused_once.py'):
  tree=ast.parse((D/name).read_bytes());main_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
  compare=next(n for n in ast.walk(main_node) if isinstance(n,ast.Compare) and isinstance(n.left,ast.Attribute) and isinstance(n.left.value,ast.Name) and n.left.value.id=='N' and n.left.attr=='name')
  ns=dict(N=Path('/SOURCE_ONLY/'+C),require_name=C)
  assert eval(compile(ast.Expression(compare),'newstagepredicate','eval'),ns);checks.append(dict(name=name+' C accepted',passed=True))
  ns['N']=Path('/SOURCE_ONLY/'+B);assert not eval(compile(ast.Expression(compare),'oldstagepredicate','eval'),ns);checks.append(dict(name=name+' B rejected',passed=True))
 # Only old SAVED SYNTHETIC JSON inputs; no old function/fixture is executed.
 F=OLD/'fixtures/SYNTHETIC_OBSERVER_PUBLICATION';out=F/'job0/production'
 first=read(out/'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json');index=read(out/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json');pre=read(out/'NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json');go=read(F/'job0/GO_PRODUCTION.json')
 producer=first['producer'];source=p.SOURCES['h1']
 spec=dict(key='h1',source_SHA=source['SHA'],manifest_SHA=go['manifest_SHA'],candidate_pins={'source/native_own_fudan88_gas400_training_v2.py':producer['bridge_source_SHA'],'source/native_finalization_own88_gas400.py':producer['finalization_source_SHA']},
  gas400_parameter_source_contract_SHA=producer['gas400_parameter_source_contract_SHA'],actual_gas400_asset_composition_report_SHA=producer['actual_gas400_asset_composition_report_SHA'],own_step_objective_qualification_SHA=producer['own_step_objective_qualification_SHA'],objective_contract_SHA=producer['runtime_objective_contract_SHA'])
 for label,value in [('missing',None),('false',False)]:
  bad=copy.deepcopy(pre)
  if value is not None:bad['original_first_reset_completed']=value
  try:p.validate_first_new_positive(first,index,bad,go,spec)
  except ValueError as e:assert 'first reset' in str(e);checks.append(dict(name='actual original_first_reset_completed '+label+' rejected',passed=True,error=str(e)))
  else:raise AssertionError('missing actual reset accepted')
 good=copy.deepcopy(pre);good['original_first_reset_completed']=True;proof=dict(passed=True,source_only=True,actual_SDK_scene_reset_or_PhysX_validated=False);good['reset_bank_exact_compatibility_source_CPU']=proof
 v=p.validate_first_new_positive(first,index,good,go,spec)
 assert v['passed'] and v['original_first_reset_completed'];checks.append(dict(name='separate actual first-reset field true accepted metadata',passed=True))
 assert v['reset_bank_exact_compatibility_source_CPU']==proof and v['reset_bank_source_proof_not_GPU_physics'] is True;checks.append(dict(name='source-only bank proof recorded separately, no GPU upgrade',passed=True))
 reviewer=ast.parse((D/'review_native88_finals_initial_CPU_unused_once.py').read_bytes())
 added=next(n for n in ast.walk(reviewer) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='require' and 'exact_gas400_reset_bank_source_CPU_passed' in ast.unparse(n))
 for label,value in [('missing',None),('false',False),('true',True)]:
  ns=dict(envelope=dict(value={} if value is None else dict(exact_gas400_reset_bank_source_CPU_passed=value)),require=p.require)
  try:exec(compile(ast.Module(body=[added],type_ignores=[]),'newCPUflag','exec'),ns)
  except ValueError:
   assert value is not True;checks.append(dict(name='installed reset-bank source CPU flag '+label+' rejected',passed=True))
  else:assert value is True;checks.append(dict(name='installed reset-bank source CPU flag true accepted',passed=True))
 for file in D.glob('*.py'):ast.parse(file.read_bytes())
 result=dict(passed=True,count=len(checks),scope='only new stageC/reset metadata and AST predicates',checks=checks,
  old31_fixture_not_executed=True,old_saved_synthetic_JSON_only=True,no_network_actual_process_GPU_SDK_model_or_physics=True,
  source_pins={name:hashlib.sha256((D/name).read_bytes()).hexdigest() for name in ('observe_native88_first_new_policy_finite_unused_once.py','native88_closing_protocol_v1.py','review_native88_finals_initial_CPU_unused_once.py')})
 with (D/'STAGE_C_RESET_FIELDS_METADATA_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 print(json.dumps(dict(passed=True,count=len(checks))))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (D/'STAGE_C_RESET_FIELDS_METADATA_CPU_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),metadata_only=True),f,indent=2)
  raise

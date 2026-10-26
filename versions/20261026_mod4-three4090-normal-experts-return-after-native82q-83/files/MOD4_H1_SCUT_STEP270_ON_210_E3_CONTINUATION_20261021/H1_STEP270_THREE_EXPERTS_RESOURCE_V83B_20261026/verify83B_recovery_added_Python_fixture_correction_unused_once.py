"""Correct the local synthetic fixture's namespace; preserve earlier overly broad KeyError catch."""
from pathlib import Path
import ast,copy,json,time
N=Path(__file__).resolve().parent;B=N/'payloads/recovery';read=lambda p:json.loads(p.read_bytes())
before={x['relative']:x for x in read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')['files']};after={x['relative']:x for x in read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files']}
tree=ast.parse((B/'original_account_policy50_source_CPU.py').read_bytes());f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='strict_same_V8_root_inventory');ns={};exec(compile(ast.Module(body=[f],type_ignores=[]),'actual_inventory_function','exec'),ns)
ns['strict_same_V8_root_inventory'](before,after,'original_account_policy50_source_CPU.py','recovery')
bad=copy.deepcopy(after);bad['unapproved_added.py']=dict(SHA='0'*64,bytes=0);rejected=False
try:ns['strict_same_V8_root_inventory'](before,bad,'original_account_policy50_source_CPU.py','recovery')
except AssertionError:rejected=True
assert rejected
with (N/'reports/RECOVERY_LOCAL_FIXTURE_NAMESPACE_LIMITATION_AND_CORRECTED_ASSERTION_REJECTION_ACTUAL.json').open('x',encoding='utf8') as out:json.dump(dict(epoch=time.time(),corrected_actual_AssertionError_rejection_passed=True,original_sourceCPU_reports_retained=True,original_83_and83B_synthetic_recovery_added_python_case_overbroad_KeyError_catch_after_namespace_reassignment=True,other_metadata_cases_unchanged_no_reexecution=True,actual_installed_target_CPU_and_guard_already_passed_separately=True,no_runtime_or_training_change=True),out,indent=2)
print(json.dumps(dict(corrected_fixture_passed=True,no_runtime_change=True)))

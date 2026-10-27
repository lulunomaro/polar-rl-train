"""Exact SOURCE-only stageC derivation. No old entry/fixture is executed."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;OLD=D.parent/'native88_first_policy_closure_review_source_v1'
def H(raw):return hashlib.sha256(raw).hexdigest()
def write(name,raw):
 with (D/name).open('xb') as f:f.write(raw)
files=('observe_native88_first_new_policy_finite_unused_once.py','native88_closing_protocol_v1.py','native88_observer_readonly_remote_v1.py','collect_native88_finals_actual_cost_unused_once.py','native88_close_readonly_remote_v1.py','review_native88_finals_initial_CPU_unused_once.py','native88_initial_CPU_reader_primitives_v1.py','native88_event_curve_summary_v1.py')
rows=[]
for name in files:
 original=(OLD/name).read_bytes();new=original
 if name in ('observe_native88_first_new_policy_finite_unused_once.py','collect_native88_finals_actual_cost_unused_once.py','review_native88_finals_initial_CPU_unused_once.py'):
  before=b'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027';after=b'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027'
  assert new.count(before)==1;new=new.replace(before,after)
 if name=='native88_closing_protocol_v1.py':
  before=b" require(pre['actual_GPU_runtime_readback_passed'] is True and pre['before_first_native_physical_control_and_Pi'] is True and pre['actual_environment_count']==4096,'actual fresh GPU precontrol')"
  assert new.count(before)==1
  new=new.replace(before,before+b"\n require(pre.get('original_first_reset_completed') is True,'original actual first reset must complete before newPi')")
  before=b"SHA=first['SHA'],before_control=first['before_control'],not_skill_or_FINAL=True)"
  assert new.count(before)==1
  new=new.replace(before,b"SHA=first['SHA'],before_control=first['before_control'],original_first_reset_completed=True,reset_bank_exact_compatibility_source_CPU=pre.get('reset_bank_exact_compatibility_source_CPU'),reset_bank_source_proof_not_GPU_physics=True,not_skill_or_FINAL=True)")
 if name=='review_native88_finals_initial_CPU_unused_once.py':
  before=b" require(pre['actual_GPU_runtime_readback_passed'] is True and pre['before_first_native_physical_control_and_Pi'] is True and pre['actual_environment_count']==4096,'actual new4096 GPU readback')"
  assert new.count(before)==1
  new=new.replace(before,before+b"\n require(pre.get('original_first_reset_completed') is True,'original actual first reset did not complete')")
  before=b"actual_GPU_precontrol=pre,actual_physical_precontrol=plant,actual_objective_contract=objective,"
  assert new.count(before)==1
  new=new.replace(before,b"actual_GPU_precontrol=pre,actual_physical_precontrol=plant,actual_objective_contract=objective,\n  original_first_reset_completed=True,reset_bank_exact_compatibility_source_CPU=pre.get('reset_bank_exact_compatibility_source_CPU'),reset_bank_source_proof_not_GPU_physics=True,")
  before=b"   envelope=cpu['results'][key]['ready_envelope']"
  assert new.count(before)==1
  new=new.replace(before,before+b"\n   require(envelope['value'].get('exact_gas400_reset_bank_source_CPU_passed') is True,'fresh installed exact gas400 reset-bank source CPU proof required')")
 ast.parse(new);write(name,new);rows.append(dict(relative=name,old_SHA=H(original),new_SHA=H(new),bytes=len(new),changed=original!=new))
cli=(OLD/'CLI_SOURCE_ONLY_NOT_EXECUTED.ps1').read_bytes().replace(b'native88_first_policy_closure_review_source_v1',b'native88C_exact_reset_bank_lifecycle_source_v1').replace(b'V88B_20261027',b'V88C_20261027').replace(b'NATIVE88B_ACTUAL_',b'NATIVE88C_ACTUAL_')
write('CLI_SOURCE_ONLY_NOT_EXECUTED.ps1',cli)
def fun(raw,name):return next(n for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
checks={}
for name in ('native88_observer_readonly_remote_v1.py','native88_close_readonly_remote_v1.py','native88_initial_CPU_reader_primitives_v1.py','native88_event_curve_summary_v1.py'):checks[name+'_byteexact']=(D/name).read_bytes()==(OLD/name).read_bytes()
for name in ('closing_gate','validate_fees','verify_window','native_window','validate_actual_GO_binding','validate_detached','publication_index_status'):
 checks[name+'_AST_exact']=ast.dump(fun((OLD/'native88_closing_protocol_v1.py').read_bytes(),name))==ast.dump(fun((D/'native88_closing_protocol_v1.py').read_bytes(),name))
assert all(checks.values())
write('SOURCE_DERIVATION_ACTUAL.json',json.dumps(dict(passed=True,scope='source-only stageC + exact reset evidence fields; no old fixture executed',files=rows,checks=checks),indent=2).encode())
print(json.dumps(dict(passed=True,files=len(rows),exact_checks=len(checks))))

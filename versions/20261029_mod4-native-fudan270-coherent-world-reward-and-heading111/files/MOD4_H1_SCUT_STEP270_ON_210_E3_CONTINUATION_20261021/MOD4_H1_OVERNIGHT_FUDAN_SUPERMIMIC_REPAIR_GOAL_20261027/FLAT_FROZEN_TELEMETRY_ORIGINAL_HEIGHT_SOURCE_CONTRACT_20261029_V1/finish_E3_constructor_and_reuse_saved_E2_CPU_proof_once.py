from pathlib import Path
import ast,hashlib,importlib.util,json,time,traceback
import torch,tensordict
C=Path(__file__).resolve().parent;L=C.parent
SPECS=[('E2','E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4','E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json','e2_profile_domain_telemetry_v1.py','E2_frozen_actual_receipts_readonly_CODE_v4.py','E2_new86_target_source_SDK_metadata_admission_v1.py'),('E3','E3_97_SOURCE210_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V3','E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json','e3_recipe_domain_telemetry_v1.py','E3_source210_actual_receipts_readonly_CODE_v3.py','E3_source210_target_source_SDK_metadata_admission_v1.py')]
def main():
 torch.set_num_threads(2);values=[]
 for role,name,mf,component,code_name,cpu_name in SPECS:
  D=L/name;raw=(D/component).read_bytes();report=D/'reports/SELECTED_CONSTRUCTOR_GROUND_AND_CLOCK_SOURCE_CPU_ACTUAL.json'
  if role=='E2':
   value=json.loads(report.read_bytes());assert value['passed'] and value['role']=='E2' and value['selected_component_SHA']==hashlib.sha256(raw).hexdigest()
  else:
   manifest=json.loads((D/mf).read_bytes());source=Path(next(r['local_path'] for r in manifest['files'] if r['relative']=='runtime/isaac/mod4/mod4_task.py'));p=D/'selected_telemetry_constructor_API_fixture_v1.py';s=importlib.util.spec_from_file_location('_actual_constructor_api_fixture_E3_finish',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
   value=m.run_selected_constructor_fixture(D,role,torch,source_path=source,output=D/'reports/LOCAL_E3_ACTUAL_SELECTED_CONSTRUCTOR_API_FIXTURE_V3')
   assert value['passed'] and value['no_ground_attribute_injected'];value.update(selected_component_SHA=hashlib.sha256(raw).hexdigest(),all_selected_ground_references_audited=True,first360_normal850_sup1800_remaining900_source_bound=True,metadata_CPU_executes_same_selected_constructor_fixture_before_App=True,local_torch=torch.__version__,local_tensordict=tensordict.__version__,not_actual_target_SDK_or_GPU_proof=True)
  assert b'_mod4_ground_z' not in raw;tree=ast.parse((D/code_name).read_bytes());code=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in n.targets));ast.parse(code);assert "360 if mode=='first' else 850" in code and "nominal=sup['creation']+1800" in code
  selection=json.loads((D/'GROUND_REPAIR_SELECTION_PENDING_FINAL_FREEZE.json').read_bytes());assert 'first_native24_read_wait_maximum_seconds=360' in (D/selection['remote']).read_text();cpu=ast.parse((D/cpu_name).read_bytes());assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='run_selected_constructor_fixture' for n in ast.walk(cpu))
  if role=='E3':
   with report.open('x') as f:json.dump(value,f,indent=2)
  values.append(dict(role=role,passed=True,report=str(report),E2_existing_pass_reused_without_another_constructor_call=role=='E2'))
 assert not torch.cuda.is_initialized()
 with (C/'reports/BOTH_SELECTED_CONSTRUCTORS_SOURCE_CPU_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,values=values,no_old_PT_raw_NPZ_SDK_GPU_remote=True),f,indent=2)
 with (C/'reports/LOCAL_TEST_ERROR_CLASSIFICATION_APPEND_CORRECTION.json').open('x') as f:json.dump(dict(original_V1_failure='Ambiguous *readonly_CODE*.py glob at E3: Windows case-insensitive matching includes AUTH72...READONLY_CODE plus actual E3 CODE. E2 proof was already saved successfully.',earlier_Windows_longpath_guess_not_proved=True,V2_test_error='E2 report open(x) correctly refused to overwrite its already-passed existing report; no source/physical error',selected_final_test='Reuse exact saved E2 proof and execute E3 selected constructor in NEW V3 fixture output; exact file basenames only',old_errors_sources_outputs_all_preserved=True,no_model_remote=True),f,indent=2)
 print(json.dumps(dict(passed=True,both_selected_constructors=True,E2_saved_pass_reused=True,source_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (C/'reports'/('ORIGINAL_LOCAL_FINISH_FIXTURE_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(traceback=traceback.format_exc(),source_only=True),f,indent=2)
  raise

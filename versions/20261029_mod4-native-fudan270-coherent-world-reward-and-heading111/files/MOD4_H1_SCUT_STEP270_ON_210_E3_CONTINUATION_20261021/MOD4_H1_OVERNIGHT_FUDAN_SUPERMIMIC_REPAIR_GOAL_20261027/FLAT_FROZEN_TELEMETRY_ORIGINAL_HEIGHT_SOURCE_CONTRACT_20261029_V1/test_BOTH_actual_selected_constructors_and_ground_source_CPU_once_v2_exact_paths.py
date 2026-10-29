from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
import torch
C=Path(__file__).resolve().parent;L=C.parent
SPECS=[('E2','E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4','E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json','e2_profile_domain_telemetry_v1.py'),('E3','E3_97_SOURCE210_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V3','E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json','e3_recipe_domain_telemetry_v1.py')]
def main():
 torch.set_num_threads(2);assert not torch.cuda.is_initialized();values=[]
 for role,name,mf,component in SPECS:
  D=L/name;manifest=json.loads((D/mf).read_bytes());source=Path(next(r['local_path'] for r in manifest['files'] if r['relative']=='runtime/isaac/mod4/mod4_task.py'));p=D/'selected_telemetry_constructor_API_fixture_v1.py';s=importlib.util.spec_from_file_location('_actual_constructor_api_fixture_'+role,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  value=m.run_selected_constructor_fixture(D,role,torch,source_path=source,output=D/'reports'/('LOCAL_'+role+'_ACTUAL_SELECTED_CONSTRUCTOR_API_FIXTURE_V2'))
  assert value['passed'] and value['no_ground_attribute_injected'];raw=(D/component).read_bytes();assert b'_mod4_ground_z' not in raw
  selection=json.loads((D/'GROUND_REPAIR_SELECTION_PENDING_FINAL_FREEZE.json').read_bytes());files=[D/('E2_frozen_actual_receipts_readonly_CODE_v4.py' if role=='E2' else 'E3_source210_actual_receipts_readonly_CODE_v3.py')];assert files[0].is_file();tree=ast.parse(files[0].read_bytes());code=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in n.targets));ast.parse(code)
  assert "360 if mode=='first' else 850" in code and "nominal=sup['creation']+1800" in code and 'nominal-time.time()<=900' in code
  remote=(D/selection['remote']).read_text();assert 'first_native24_read_wait_maximum_seconds=360' in remote and 'ground_provider_contract=' in remote
  cpu=D/('E2_new86_target_source_SDK_metadata_admission_v1.py' if role=='E2' else 'E3_source210_target_source_SDK_metadata_admission_v1.py');ct=ast.parse(cpu.read_bytes());assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='run_selected_constructor_fixture' for n in ast.walk(ct));assert 'torch.load(' not in cpu.read_text()
  value.update(selected_component_SHA=hashlib.sha256(raw).hexdigest(),all_selected_ground_references_audited=True,first360_normal850_sup1800_remaining900_source_bound=True,metadata_CPU_executes_same_selected_constructor_fixture_before_App=True,local_torch=torch.__version__,local_tensordict=__import__('tensordict').__version__,not_actual_target_SDK_or_GPU_proof=True)
  with (D/'reports/SELECTED_CONSTRUCTOR_GROUND_AND_CLOCK_SOURCE_CPU_ACTUAL.json').open('x') as f:json.dump(value,f,indent=2)
  values.append(dict(role=role,passed=True,report=str(D/'reports/SELECTED_CONSTRUCTOR_GROUND_AND_CLOCK_SOURCE_CPU_ACTUAL.json')))
 assert not torch.cuda.is_initialized();(C/'reports').mkdir(exist_ok=True)
 with (C/'reports/BOTH_SELECTED_CONSTRUCTORS_SOURCE_CPU_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,values=values,no_old_PT_raw_NPZ_SDK_GPU_remote=True),f,indent=2)
 print(json.dumps(dict(passed=True,both_actual_selected_constructors=True,source_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (C/'reports').mkdir(exist_ok=True)
  with (C/'reports'/('ORIGINAL_LOCAL_CONSTRUCTOR_API_FIXTURE_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(passed=False,traceback=traceback.format_exc(),source_only=True),f,indent=2)
  raise

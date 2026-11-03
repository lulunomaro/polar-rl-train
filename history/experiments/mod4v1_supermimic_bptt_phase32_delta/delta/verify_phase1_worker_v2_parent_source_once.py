"""Independent frozen V2 source, exact deltas and stdlib regression; never native."""
from pathlib import Path
import ast,json,hashlib,sys,unittest,time
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_worker_v2';old=R/'source_phase1_capture_worker_v1';out=R/'reports/PHASE1_WORKER_V2_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists()
H=lambda b:hashlib.sha256(b).hexdigest()
raw=(D/'SOURCE_SEAL.json').read_bytes();assert H(raw)=='caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5';seal=json.loads(raw);assert len(seal['files'])==13 and seal['content_root_sha256']=='83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2'
before={}
for row in seal['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256']);before[row['relative']]=H(b)
assert H((old/'SOURCE_SEAL.json').read_bytes())=='3f713457c5d66c44ad1fe962ff954e6f65f87afedfef1d6e5bb7fa608e76bea7'
for n in ('single_gpu_passive_capture_parent_v1.py','phase1_capture_contract.py','phase1_capture_observer.py'):assert (D/n).read_bytes()==(old/n).read_bytes(),n
runtime=(old/'phase1_capture_runtime.py').read_text(encoding='utf-8')
pairs=[('def put_json(path, value):','def put_json(path, value, *, add_capture_epoch=True):'),('if type(value) is dict else value','if type(value) is dict and add_capture_epoch else value'),('core()._validate_returned_app_binding(binding)','core()._validate_returned_app_binding(binding, helper)'),("put_json(case / 'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json', binding)","put_json(case / 'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json', binding, add_capture_epoch=False)")]
for a,b in pairs:assert runtime.count(a)==1;runtime=runtime.replace(a,b)
dump=lambda x:ast.dump(ast.parse(x),include_attributes=False)
assert dump(runtime)==dump((D/'phase1_capture_runtime.py').read_text(encoding='utf-8')),'unrelated runtime change'
w=(old/'worker_passive_interface_v1.py').read_text(encoding='utf-8');sub='        from launch_storage_contract import parent_five_storage\n        from n80_gpu_capacity import capacity_ctor\n';assert w.count(sub)==1
w=w.replace(sub,"        bootstrap=bootstrap_original_helpers(group)\n        parent_five_storage=bootstrap['modules']['launch_storage_contract'].parent_five_storage\n        capacity_ctor=bootstrap['modules']['n80_gpu_capacity'].capacity_ctor\n")
a=ast.parse(w);b=ast.parse((D/'worker_passive_interface_v1.py').read_text(encoding='utf-8'));bootstrap=[x for x in b.body if isinstance(x,ast.FunctionDef)and x.name=='bootstrap_original_helpers'];assert len(bootstrap)==1;b.body.remove(bootstrap[0]);assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),'worker main unrelated change'
index=json.loads((D/'CAPTURE_SOURCE_INDEX.json').read_bytes());prior=json.loads((old/'CAPTURE_SOURCE_INDEX.json').read_bytes());assert index['original17']==prior['original17'] and index['dependency_sources']==prior['dependency_sources'];rows=index['original17']+index['new_sources']+index['dependency_sources'];assert len(rows)==27
for row in rows:
 p=Path(row['path']);assert p.suffix in('.py','.json')and p.resolve().is_relative_to(R);b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256'])
sys.path.insert(0,str(D));suite=unittest.defaultTestLoader.discover(str(D),pattern='test*.py');result=unittest.TextTestRunner(verbosity=0).run(suite);assert result.wasSuccessful() and result.testsRun==96
for rel,sha in before.items():assert H((D/rel).read_bytes())==sha
v=dict(kind='PHASE1_WORKER_V2_PARENT_INDEPENDENT_SOURCE_AND_96_STDLIB_VERIFY_V1',epoch=time.time(),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),whole_parent_contract_observer_bytes_identical=True,worker_main_only_two_imports_to_same_bootstrap=True,runtime_only_explicit_epoch_option_binding_and_missing_helper_fixes=True,original17_and_dependency5_unchanged=True,all27_source_mappings_verified=True,source13_unchanged_after_test=True,source_seal_SHA256=H(raw),actual_preflight_stage_parent_SDK_PT_raw_GPU_canonical_operations=0,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),**v),indent=2))

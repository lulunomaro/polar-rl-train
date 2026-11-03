"""Independent frozen B2 SOURCE/28 stdlib check; no SDK or new historical CPU claim."""
from pathlib import Path
import ast,json,hashlib,sys,unittest,time
R=Path(__file__).resolve().parent;D=R/'source_phase1_passive_sensor_capture_v2';old=R/'source_phase1_passive_sensor_capture_v1';out=R/'reports/PHASE1_B2_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists()
H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(2909,'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a');seal=json.loads(raw);assert len(seal['files'])==13
before={}
for row in seal['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256']);before[row['relative']]=H(b)
assert H((old/'SOURCE_SEAL.json').read_bytes())=='3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881'
for row in json.loads((old/'SOURCE_SEAL.json').read_bytes())['files']:
 b=(old/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256'])
nodes=lambda p:{n.name:n for n in ast.parse(p.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
ns=lambda n:ast.dump(n,include_attributes=False)
a,b=nodes(old/'passive_capture.py'),nodes(D/'passive_capture.py');runtime=('stdlib_snapshot','tensor_snapshot_adapter','BoundedRecorder','_same_callable','_plain_scale','_root_asset_configuration','PassiveCapture','install_passive_capture');assert all(ns(a[k])==ns(b[k])for k in runtime)
for k in ('install_passive_capture','preflight'):assert ast.dump(a[k].args,include_attributes=False)==ast.dump(b[k].args,include_attributes=False)
a,b=nodes(old/'source_api.py'),nodes(D/'source_api.py');helpers=('sha','_nodes','pin','_source_class_chain','_code_key','_find_code','verify_callable','verify_class','closure_functions');assert all(ns(a[k])==ns(b[k])for k in helpers)
for n in('cpu_reference_tap_fixture.py','fake_runtime.py','OBSERVER_HOOK_SPEC.md'):assert(old/n).read_bytes()==(D/n).read_bytes()
manifest=json.loads((D/'SOURCE_API_MANIFEST.json').read_bytes());assert len(manifest['roles'])==8 and manifest['source_revision']==2
for role,row in manifest['roles'].items():
 c=row['reset_chain'];assert c['status']=='SOURCE_CONFIRMED_LIVE_UNKNOWN' and c['live_binding']=='UNKNOWN' and [x['env_attribute']for x in c['layers']]==['_explicit_pd','_chassis_com','_gas_damping','_spring_pressure'];assert all(x['function']['freevars']==['adapter','original']for x in c['layers'])
historical=json.loads((R/'reports/PHASE1_PASSIVE_TAP_CPU_V1.json').read_bytes());assert historical['returncode']==0
sys.path.insert(0,str(D));suite=unittest.defaultTestLoader.discover(str(D),pattern='test*.py');result=unittest.TextTestRunner(verbosity=0).run(suite);assert result.wasSuccessful()and result.testsRun==28
for rel,sha in before.items():assert H((D/rel).read_bytes())==sha
v=dict(kind='B2_PARENT_SOURCE_REVIEW_AND_INDEPENDENT_STDLIB_VERIFY_V1',epoch=time.time(),seal_SHA256=H(raw),sealed_members=13,tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),role_source_chains=len(manifest['roles']),same_runtime_AST_definitions=len(runtime),same_original_verifier_helpers=len(helpers),old_CPU_fixture_fake_hook_bytes_unchanged=True,old_CPU_invariance_scope='HISTORICAL_B1_RUNTIME_ONLY_NOT_B2_NEW_EXECUTION_OR_CHANGED_PREFLIGHT',old_B1_seal_unchanged=True,B2_sealed_bytes_unchanged_after_tests=True,actual_SDK_TorchCPU_tap_parent_stage_PT_raw_GPU_C_operations=0,gate1='UNKNOWN',exact=False,stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),**v),indent=2))

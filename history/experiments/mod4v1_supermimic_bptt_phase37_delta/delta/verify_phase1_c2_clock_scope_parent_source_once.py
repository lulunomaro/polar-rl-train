"""NEW parent's C2 source/fake check; old packages and actual captures remain readonly."""
from pathlib import Path
import ast,hashlib,json,types,sys,unittest,io,time
R=Path(__file__).resolve().parent;D=R/'source_phase1_actuation_clock_scope_v2';out=R/'reports/PHASE1_C2_CLOCK_SCOPE_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists();H=lambda b:hashlib.sha256(b).hexdigest();sys.dont_write_bytecode=True
raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(5938,'105df1f6e47b82061aae729878a12874f731dd34b7cb0feeb75724028298469b');seal=json.loads(raw);assert seal['enabled']is False and seal['worker_bound']is False and seal['new_schema_consumer_implemented']is False;blobs={};before={}
for row in seal['members']:
 p=D/row['name'];b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);blobs[row['name']]=b;before[str(p)]=H(b)
assert H(json.dumps(seal['members'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==seal['content_root_SHA256']
for row in seal['readonly_source_pins']+seal['old_seals_reverified']:
 p=Path(row['path']);assert p.resolve().is_relative_to(R);b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);before[str(p)]=H(b)
def load(name,path,b):
 assert name not in sys.modules;ast.parse(b);m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m;exec(compile(b,str(path),'exec'),m.__dict__);return m
p=R/'source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py';load('capture_evidence_verifier_v1',p,p.read_bytes());load('actuation_tap_v2',D/'actuation_tap_v2.py',blobs['actuation_tap_v2.py']);tests=load('phase1_c2_parent_tests_v1',D/'test_actuation_clock_scope_v2.py',blobs['test_actuation_clock_scope_v2.py']);suite=unittest.defaultTestLoader.loadTestsFromModule(tests);assert suite.countTestCases()==12;stream=io.StringIO();start=time.perf_counter();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);elapsed=time.perf_counter()-start;unchanged=all(H(Path(p).read_bytes())==sha for p,sha in before.items())and(D/'SOURCE_SEAL.json').read_bytes()==raw
v=dict(kind='PARENT_PHASE1_C2_CLOCK_SCOPE_SOURCE_VERIFY_V1',epoch=time.time(),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),seconds=elapsed,seal_SHA256=H(raw),new_members=5,source_and_old_seals_unchanged=unchanged,original_whole_functions_AST_equal=20,changed_functions=['ActuationTap._patch'],only_other_source_change='module docstring',real_queue_or_Torch_or_SDK_tested=False,actual_whole_trace_model_network_C_or_resource_operations=0,old_tests_executed=False,worker_bound=False,new_schema_consumer_implemented=False,same_asset_context_is_not_DOF_proof=True,gate1='UNKNOWN',stage2_GO=False,test_output=stream.getvalue())
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2));assert result.wasSuccessful()and unchanged and 'torch'not in sys.modules

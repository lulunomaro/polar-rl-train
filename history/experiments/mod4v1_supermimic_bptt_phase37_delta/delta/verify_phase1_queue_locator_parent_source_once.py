"""Parent's NEW source-only 11-case review; no actual capture/remote/SDK access."""
from pathlib import Path
import ast,hashlib,json,sys,time,types,unittest,io
R=Path(__file__).resolve().parent;D=R/'source_phase1_queue_failure_locator_v1';out=R/'reports/PHASE1_QUEUE_LOCATOR_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists();sys.dont_write_bytecode=True
H=lambda b:hashlib.sha256(b).hexdigest();sealraw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(sealraw),H(sealraw))==(2929,'91ac90660e1d4e902b3c019bc9e4e9846d778fe722759eb41a2ff05a40a356a9');seal=json.loads(sealraw);before={};blobs={}
for row in seal['members']:
 p=D/row['name'];b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);before[str(p)]=H(b);blobs[row['name']]=b
assert len(blobs)==4 and seal['tests']==11 and seal['stage2_GO']is False
for row in seal['input_pins']:
 p=R/row['name'];b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);before[str(p)]=H(b)
for row in seal['old_seals_reverified']:
 p=R/row['name'];b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);before[str(p)]=H(b);s=json.loads(b)
 for x in s['members']:
  f=p.parent/x['name'];raw=f.read_bytes();assert(len(raw),H(raw))==(x['bytes'],x['SHA256']);before[str(f)]=H(raw)
def module(name,path,blob):
 assert name not in sys.modules;ast.parse(blob);m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m;exec(compile(blob,str(path),'exec'),m.__dict__);return m
p=R/'source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py';pure=module('capture_evidence_verifier_v1',p,p.read_bytes());loc=module('queue_failure_locator_v1',D/'queue_failure_locator_v1.py',blobs['queue_failure_locator_v1.py']);test=module('phase1_queue_locator_parent_unittest_v1',D/'test_queue_failure_locator_v1.py',blobs['test_queue_failure_locator_v1.py'])
start=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromModule(test);assert suite.countTestCases()==11;log=io.StringIO();result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite);elapsed=time.perf_counter()-start
unchanged=all(H(Path(path).read_bytes())==sha for path,sha in before.items())and(D/'SOURCE_SEAL.json').read_bytes()==sealraw;v=dict(kind='PARENT_PHASE1_QUEUE_LOCATOR_SOURCE_VERIFY_V1',epoch=time.time(),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),seconds=elapsed,source_and_old_sealed_members_unchanged=unchanged,source_seal_SHA256=H(sealraw),source_files_verified=len(before),old_tests_executed=False,actual_whole_worker_group_trace_model_SDK_GPU_C_or_network_operations=0,torch_imported='torch'in sys.modules,gate1='UNKNOWN',stage2_GO=False,test_output=log.getvalue())
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2));assert v['passed']and unchanged and not v['torch_imported']

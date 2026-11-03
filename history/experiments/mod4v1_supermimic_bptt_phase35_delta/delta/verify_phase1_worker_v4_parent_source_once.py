"""Independent final V4 source/one-line projection and44 stdlib regressions."""
from pathlib import Path
import ast,json,hashlib,sys,time,unittest,copy
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_worker_v4';old=R/'source_phase1_capture_worker_v3';out=R/'reports/PHASE1_WORKER_V4_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists()
H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(2919,'ba3409a5450e378ea97eac64f0fec4c3409ac974a4c3378d0c6e6a6cfc405180');s=json.loads(raw);assert len(s['files'])==13 and s['content_root_sha256']=='758dc867cc4040a6f1eb9f587cc88f69a3866e03a9553290128a1681cda039e8';before={}
for row in s['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256']);before[row['relative']]=H(b)
for n in('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py','single_gpu_passive_capture_parent_v1.py'):assert(D/n).read_bytes()==(old/n).read_bytes()
original=(old/'worker_passive_interface_v1.py').read_bytes();current=(D/'worker_passive_interface_v1.py').read_bytes();a=b'boundary=core().OriginalEpisodeBoundary(torch,env.device,n=80)';b=b'boundary=core().OriginalEpisodeBoundary(torch,bridge.device,n=80)';assert original.count(a)==current.count(b)==1 and current.replace(b,a)==original and current==original.replace(a,b)
index=json.loads((D/'CAPTURE_SOURCE_INDEX.json').read_bytes());prior=json.loads((old/'CAPTURE_SOURCE_INDEX.json').read_bytes());assert index['source_version']==4
projection=copy.deepcopy(index);projection['source_version']=3;projection['source_derivation']=prior['source_derivation'];projection['new_sources']=prior['new_sources'];projection.pop('boundary_device_source_contract');assert projection==prior
rows=index['original17']+index['new_sources']+index['dependency_sources'];assert len(rows)==27
for row in rows:
 p=Path(row['path']);assert p.resolve().is_relative_to(R)and p.suffix in('.py','.json');v=p.read_bytes();assert(len(v),H(v))==(row['bytes'],row['SHA256'])
contract=index['boundary_device_source_contract'];assert contract['read_only_fixture_source_not_runtime_dependency']and contract['parent_CPU_result']=='NOT_REPRESENTED_BY_THIS_SOURCE_SEAL'and not contract['actual_Torch_CPU_executed_here'];proof=contract['seal'];assert proof['SHA256']=='c9fae49e96b7042863372e7fb681c7c93fd8ce733646908222c9af6f7d306bdc'and len(proof['members'])==8
for row in [proof]+[dict(path=str(Path(proof['path']).parent/x['relative']),bytes=x['bytes'],SHA256=x['SHA256'])for x in proof['members']]:
 p=Path(row['path']);assert p.resolve().is_relative_to(R);v=p.read_bytes();assert(len(v),H(v))==(row['bytes'],row['SHA256'])
sys.path.insert(0,str(D));suite=unittest.defaultTestLoader.discover(str(D),pattern='test*.py');res=unittest.TextTestRunner(verbosity=0).run(suite);assert res.wasSuccessful()and res.testsRun==44
for name,sha in before.items():assert H((D/name).read_bytes())==sha
v=dict(kind='PARENT_V4_ONE_EXISTING_DEVICE_ARGUMENT_SOURCE_VERIFY_V1',epoch=time.time(),source_version=4,seal_SHA256=H(raw),tests_run=res.testsRun,failures=len(res.failures),errors=len(res.errors),four_other_candidates_bytes_identical_V3=True,entire_worker_reverse_bytes_projection_equal=True,worker_only_diff='OriginalEpisodeBoundary(torch,env.device,n=80) -> OriginalEpisodeBoundary(torch,bridge.device,n=80)',full_index_reverse_projection_equal_V3=True,source27_verified=True,boundary_readonly_source8_verified=True,source13_hash_unchanged_after_tests=True,actual_Torch_SDK_native_PT_raw_GPU_canonical_stage_dispatch_operations=0,actual_V3_root_cause_confirmed=False,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),**v),indent=2))

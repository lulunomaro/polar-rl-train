"""Independent frozen V3 propagation audit and44 stdlib regressions; no native."""
from pathlib import Path
import json,hashlib,sys,unittest,time,ast
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_worker_v3';old=R/'source_phase1_capture_worker_v2';out=R/'reports/PHASE1_WORKER_V3_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists()
H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(2920,'80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da');seal=json.loads(raw);assert len(seal['files'])==13 and seal['content_root_sha256']=='b1b6ec96f93561d201c307cab9b17fbdc8591c6e362cef45a29ee63419f87963'
before={}
for row in seal['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256']);before[row['relative']]=H(b)
for n in('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py','worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py'):assert(D/n).read_bytes()==(old/n).read_bytes()
index=json.loads((D/'CAPTURE_SOURCE_INDEX.json').read_bytes());prior=json.loads((old/'CAPTURE_SOURCE_INDEX.json').read_bytes());assert index['source_version']==3 and index['original17']==prior['original17'] and index['all_actuation_original_sources']==prior['all_actuation_original_sources']
for name in('actuation','adapter','partition'):assert index['dependency_seals'][name]==prior['dependency_seals'][name]
rows=index['original17']+index['new_sources']+index['dependency_sources'];assert len(rows)==27
for row in rows:
 p=Path(row['path']);assert p.suffix in('.py','.json')and p.resolve().is_relative_to(R);b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256'])
for oldrow,newrow in zip(prior['dependency_sources'],index['dependency_sources']):
 if not newrow['install_relative'].startswith('phase1_deps/sensor/'):assert oldrow==newrow
closure=index['sensor_source_manifest']['original_source_closure'];assert closure['pin_references']==435 and closure['unique_full_source_files']==len(closure['sources'])==155
for row in closure['sources']:
 p=Path(row['path']);assert p.suffix=='.py'and p.resolve().is_relative_to(R);b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);ast.parse(b)
sys.path.insert(0,str(D));suite=unittest.defaultTestLoader.discover(str(D),pattern='test*.py');result=unittest.TextTestRunner(verbosity=0).run(suite);assert result.wasSuccessful()and result.testsRun==44
for rel,sha in before.items():assert H((D/rel).read_bytes())==sha
v=dict(kind='V3_PARENT_FROZEN_PROPAGATION_AND_44_STDLIB_VERIFY_V1',epoch=time.time(),source_version=3,seal_SHA256=H(raw),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),five_candidates_bytes_identical_V2=True,original17_C182_adapter10_partition9_unchanged=True,only_runtime_dependency_change='3sensor aliases to complete sealed B2',all27_mappings_verified=True,B2_source_pin_references=435,B2_unique_source_files_verified=155,source13_hash_unchanged_after_tests=True,actual_TorchCPUtap_SDK_native_PT_raw_C_GPU_stage_dispatch_operations=0,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),**v),indent=2))

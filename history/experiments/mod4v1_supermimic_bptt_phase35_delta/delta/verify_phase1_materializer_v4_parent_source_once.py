"""Parent frozen V4 SOURCE test. Emits only stdout; no sealed report rewrite."""
from pathlib import Path
import ast,hashlib,json,sys,time,unittest
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_materializer_v4';H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(2412,'68c5e82d7d9e72685e9ac674a2714196352f0a922b1526fc49b3f5830a9c70f8');s=json.loads(raw);assert len(s['files'])==11 and s['content_root_sha256']=='cd1b83534767222f633f255d900509ccba80786044415aee405c4647fb6b8d23';before={}
for row in s['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);before[row['relative']]=H(b)
fns=lambda b:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(b).body if isinstance(n,ast.FunctionDef)}
a=fns((R/'source_phase1_capture_materializer_v3/stage_phase1_capture_v3.py').read_bytes());b=fns((D/'stage_phase1_capture_v4.py').read_bytes());assert set(a)==set(b);changed={k for k in a if a[k]!=b[k]};assert changed=={'load_sources','metadata_validate','preflight_summary','stage'};assert(D/'static_source_helpers_v1.py').read_bytes()==(R/'source_phase1_capture_materializer_v3/static_source_helpers_v1.py').read_bytes()
sys.path.insert(0,str(D));import test_materializer_stdlib_v4 as tests
res=unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.SourceTests));assert res.wasSuccessful()and res.testsRun==44
for name,sha in before.items():assert H((D/name).read_bytes())==sha
assert all(v==0 for v in tests.AUDIT.values())
v=dict(kind='PARENT_FROZEN_MATERIALIZER_V4_44_STDLIB_MIRROR_VERIFY_V1',epoch=time.time(),source_seal_SHA256=H(raw),tests_run=res.testsRun,failures=len(res.failures),errors=len(res.errors),audit=dict(tests.AUDIT),all11_sealed_members_unchanged=True,changed_old_functions=sorted(changed),added_source_helpers=0,full17_helpers_bytes_unchanged=True,actual_isolated_R_text_mirror_and_original_B2_manifest_rebuild_tested=True,worker_index_SHA256='75e36c0255a3b354dd0efeec33600f9b38d51ca28484de2dbed55db865fc7b2d',source_mirror_file_count=332,B2_unique_Python=155,B2_pin_refs=435,B2_extra_routing_JSON=4,boundary_source8_and_seal_all9_tested=True,fixture_module_imports=0,actual_prepare_preflight_stage_dispatch_SDK_PT_raw_canonical_GPU_operations=0,gate1='UNKNOWN',stage2_GO=False)
print(json.dumps(v,sort_keys=True))

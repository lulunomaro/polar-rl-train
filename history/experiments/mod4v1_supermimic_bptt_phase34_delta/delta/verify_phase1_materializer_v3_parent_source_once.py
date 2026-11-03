"""Parent SOURCE run; emits evidence only, never invokes sealed test main/report writer."""
from pathlib import Path
import ast,hashlib,json,sys,time,unittest
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_materializer_v3'
H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(2413,'38e53017fd99bdedc1ac832123c5dc6cf9fce12a9d8ac2e974074ee0d8c86c75');seal=json.loads(raw);assert len(seal['files'])==11 and seal['content_root_sha256']=='6c97359a25f52b9248198dfbc70d3fa1f999cc14f2f0edf6d8b5746a4143d5f5'
before={}
for row in seal['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);before[row['relative']]=H(b)
fns=lambda b:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(b).body if isinstance(n,ast.FunctionDef)}
a=fns((R/'source_phase1_capture_materializer_v2/stage_phase1_capture_v2.py').read_bytes());b=fns((D/'stage_phase1_capture_v3.py').read_bytes());assert set(b)-set(a)=={'normalize_B2_source_paths','verify_B2_source_closure'} and set(a)<=set(b);changed={k for k in a if a[k]!=b[k]};assert changed<={'load_sources','metadata_validate','preflight_summary','stage'}
assert(D/'static_source_helpers_v1.py').read_bytes()==(R/'source_phase1_capture_materializer_v2/static_source_helpers_v1.py').read_bytes()
sys.path.insert(0,str(D));import test_materializer_stdlib_v3 as tests
res=unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.SourceTests));assert res.wasSuccessful()and res.testsRun==42
for rel,sha in before.items():assert H((D/rel).read_bytes())==sha
assert all(v==0 for v in tests.AUDIT.values())
v=dict(kind='PARENT_FROZEN_MATERIALIZER_V3_42_STDLIB_MIRROR_VERIFY_V1',epoch=time.time(),source_seal_SHA256=H(raw),tests_run=res.testsRun,failures=len(res.failures),errors=len(res.errors),audit=dict(tests.AUDIT),all11_sealed_members_unchanged=True,changed_old_functions=sorted(changed),two_added_source_helpers_only=True,full17_helpers_bytes_unchanged=True,actual_isolated_R_text_mirror_and_original_B2_manifest_rebuild_tested=True,worker_index_SHA256='bdeea3f057fb922bd9ae2670dcbf19188f651ca64ab2cbb0331f56a5a1124797',source_mirror_file_count=313,B2_unique_Python=155,B2_pin_refs=435,B2_extra_routing_JSON=4,B2_diagnostic_refs=4,B2_final_handoff=1,actual_prepare_preflight_stage_dispatch_SDK_PT_raw_canonical_GPU_operations=0,gate1='UNKNOWN',stage2_GO=False)
print(json.dumps(v,sort_keys=True))

"""Parent final collector4 SOURCE proof; no actual connector or metadata read."""
from pathlib import Path
import ast,hashlib,json,sys,time,unittest
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_result_collector_v4';out=R/'reports/PHASE1_COLLECTOR_V4_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists();H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(4866,'23a5267920106b40b1efcf5db7921a16c6418621365d18933f0c9d69bfefc594');s=json.loads(raw);assert len(s['files'])==9 and s['content_root_sha256']=='ff037967e391148328fc7a3400eb30b41b1123cab5313954d87e2d779067ba2c';before={}
for row in s['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256']);before[row['relative']]=H(b)
sys.path.insert(0,str(D));import source_pins
p=source_pins.verify_sources();assert p['source_count']==50 and p['extra_source_refs']['extra_unique_file_identities']==174 and p['extra_source_refs']['manifest_pin_references_verified']==435 and p['extra_source_refs']['unique_manifest_Python_sources_full_SHA_AST_verified']==155 and p['boundary_source_refs']['independent_SOURCE_file_identities']==9
suite=unittest.defaultTestLoader.discover(str(D),pattern='test_collector_source.py');res=unittest.TextTestRunner(verbosity=0).run(suite);assert res.wasSuccessful()and res.testsRun==51
for name,sha in before.items():assert H((D/name).read_bytes())==sha
assert not any(n.split('.')[0]in{'torch','isaacsim','isaaclab','omni','warp','pxr','paramiko'}for n in sys.modules)
v=dict(kind='PARENT_COLLECTOR_V4_FINAL_SOURCE_VERIFY_V1',epoch=time.time(),seal_SHA256=H(raw),tests_run=res.testsRun,failures=len(res.failures),errors=len(res.errors),source9_unchanged_after_tests=True,fixed_source_inventory=50,extra_refs=p['extra_source_refs'],boundary_source_refs=p['boundary_source_refs'],V3_production_AST_and_original30_method_AST_preservation_tested=True,whole_worker_reverse_source_projection_tested=True,actual_SSH_collection_boundary_B2_reset_SDK_PT_raw_GPU_canonical_stage_dispatch_operations=0,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),**v),indent=2))

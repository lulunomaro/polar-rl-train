"""Parent check of final collector V3; SOURCE/tests only, no connector invocation."""
from pathlib import Path
import ast,hashlib,json,sys,time,unittest
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_result_collector_v3';out=R/'reports/PHASE1_COLLECTOR_V3_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists()
H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(3595,'2f6188fe03958bfd237efab6c22ea6f63ffa61c54608144607db5d8bc9ff577f');seal=json.loads(raw);assert len(seal['files'])==9 and seal['content_root_sha256']=='71e4df44944aa9c4b81702bd673259107570ddd49bd692993b9fe81d1e7a303d';before={}
for row in seal['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256']);before[row['relative']]=H(b)
sys.path.insert(0,str(D));import source_pins
pins=source_pins.verify_sources();assert pins['source_count']==50 and pins['extra_source_refs']['manifest_pin_references_verified']==435 and pins['extra_source_refs']['unique_manifest_Python_sources_full_SHA_AST_verified']==155 and pins['extra_source_refs']['extra_unique_file_identities']==174
suite=unittest.defaultTestLoader.discover(str(D),pattern='test_collector_source.py');res=unittest.TextTestRunner(verbosity=0).run(suite);assert res.wasSuccessful() and res.testsRun==43
for rel,digest in before.items():assert H((D/rel).read_bytes())==digest
assert not any(n.split('.')[0]in{'torch','isaacsim','isaaclab','omni','warp','pxr','paramiko'}for n in sys.modules)
v=dict(kind='PARENT_COLLECTOR_V3_FINAL_SOURCE_VERIFY_V1',epoch=time.time(),seal_SHA256=H(raw),tests_run=res.testsRun,failures=len(res.failures),errors=len(res.errors),source9_unchanged_after_tests=True,fixed_source_inventory=pins['source_count'],extra_refs=pins['extra_source_refs'],V2_production_AST_and_original30_method_AST_preservation_tested=True,actual_SSH_collection_B2_reset_SDK_PT_raw_GPU_canonical_stage_dispatch_operations=0,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),**v),indent=2))

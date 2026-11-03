"""Parent review of frozen decoded application; no actual capture documents."""
from pathlib import Path
import hashlib,json,sys,time,unittest,ast
R=Path(__file__).resolve().parent;D=R/'source_phase1_actual_capture_application_v1';out=R/'reports/PHASE1_CAPTURE_APPLICATION_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists()
H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(1525,'3e70492d5e572addc3aff3bea53b1bea21ae064c2c35f1138e80bdc39e419eb2');s=json.loads(raw);assert len(s['members'])==5 and s['content_root_SHA256']=='eb10aedd5a0e45ece0d60f0effa2f33504421af33b19f3a2afd227072be962e7';before={}
for row in s['members']:
 b=(D/row['name']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);before[row['name']]=H(b)
refs=json.loads((D/'SOURCE_PINS_V1.json').read_bytes())['source_pins'];assert len(refs)==20
for row in refs:
 p=Path(row['path']);assert p.resolve().is_relative_to(R) and p.suffix in('.py','.md','.json');b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256'])
sys.path[:0]=[str(D),str(R/'source_phase1_capture_evidence_verifier_v1')];suite=unittest.defaultTestLoader.discover(str(D),pattern='test_actual_capture_application_v1.py');res=unittest.TextTestRunner(verbosity=0).run(suite);assert res.wasSuccessful()and res.testsRun==20
for name,sha in before.items():assert H((D/name).read_bytes())==sha
assert not any(n.split('.')[0]in{'torch','isaaclab','isaacsim','omni','warp','pxr','paramiko'}for n in sys.modules)
v=dict(kind='PARENT_CAPTURE_APPLICATION_SOURCE_AND_20_SYNTHETIC_VERIFY_V1',epoch=time.time(),source_seal_SHA256=H(raw),tests_run=res.testsRun,failures=len(res.failures),errors=len(res.errors),source5_unchanged=True,source_reference_pins_verified=20,actual_capture_documents_processed=0,actual_PT_raw_SDK_GPU_SSH_canonical_operations=0,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),**v),indent=2))

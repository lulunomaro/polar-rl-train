"""Independent pure decoded verifier SOURCE review/tests; no actual capture input."""
from pathlib import Path
import ast,json,hashlib,sys,unittest,time
R=Path(__file__).resolve().parent;D=R/'source_phase1_capture_evidence_verifier_v1';out=R/'reports/PHASE1_PURE_EVIDENCE_VERIFIER_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists()
H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(1473,'303a87170fee6b358c440231909f0cb33156b282fabb62d6a0098ad1df47a3a8');seal=json.loads(raw);assert seal['member_count']==len(seal['members'])==5;before={}
for row in seal['members']:
 b=(D/row['name']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);before[row['name']]=H(b)
code=(D/'capture_evidence_verifier_v1.py').read_bytes();tree=ast.parse(code);imports={a.name for n in tree.body if isinstance(n,ast.Import)for a in n.names};assert imports=={'copy','hashlib','json','math','struct'}
assert not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in{'open','exec','eval','__import__'}for n in ast.walk(tree))
sys.path.insert(0,str(D));suite=unittest.defaultTestLoader.discover(str(D),pattern='test*.py');res=unittest.TextTestRunner(verbosity=0).run(suite);assert res.wasSuccessful()and res.testsRun==27
for rel,sha in before.items():assert H((D/rel).read_bytes())==sha
assert not any(x.split('.')[0]in{'torch','isaacsim','isaaclab','omni','warp','pxr','paramiko'}for x in sys.modules)
v=dict(kind='PURE_CAPTURE_VERIFIER_PARENT_SOURCE_AND_27_SYNTHETIC_VERIFY_V1',epoch=time.time(),source_seal_SHA256=H(raw),tests_run=res.testsRun,failures=len(res.failures),errors=len(res.errors),source_members_unchanged=True,full517line_processor_and_scope_read_by_parent=True,stdlib_import_roots=sorted(imports),source_reference_scope='17 frozen schema/method refs only; actual future V3 producer provenance not authenticated',actual_capture_documents_processed=0,actual_SDK_PT_raw_GPU_canonical_SSH_operations=0,gate1='UNKNOWN',exact=False,stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),**v),indent=2))

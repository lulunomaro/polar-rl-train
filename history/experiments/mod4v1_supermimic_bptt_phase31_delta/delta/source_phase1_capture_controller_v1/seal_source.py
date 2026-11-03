"""Freeze SOURCE controller after pure metadata/AST tests; later calls verify only."""
from pathlib import Path
import sys,hashlib,json,io,unittest,contextlib
HERE=Path(__file__).resolve().parent;target=HERE/'SOURCE_SEAL.json'
def digest(raw):return hashlib.sha256(raw).hexdigest()
if target.exists():
 s=json.loads(target.read_bytes())
 for name,meta in s['files'].items():
  p=(HERE/name).resolve();assert p.is_relative_to(HERE);b=p.read_bytes();assert len(b)==meta['bytes']and digest(b)==meta['sha256']
 print(json.dumps(dict(readonly_verified=True,content_root=s['content_root_sha256'],actual_parent_started=False)));raise SystemExit(0)
sys.path.insert(0,str(HERE));import test_controller_source
buf=io.StringIO()
with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):result=unittest.TextTestRunner(stream=buf,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_controller_source))
assert result.wasSuccessful()and result.testsRun==9
receipt=HERE/'SOURCE_RECEIPT.json';assert not receipt.exists();receipt.write_text(json.dumps(dict(kind='PHASE1_CAPTURE_OUTER_CONTROLLER_SOURCE_AST_METADATA_PASS',tests=9,failures=0,errors=0,output=buf.getvalue(),actual_Popen_parent_wait_SDK_PT_GPU_canonical_lock_signal_operations=0,actual_parent_started=False,actual_parent_wait_returned=False,gate1='UNKNOWN'),indent=2),encoding='utf-8')
names=['phase1_capture_parent_actual_wait_controller_v1.py','test_controller_source.py','README.md','seal_source.py','SOURCE_RECEIPT.json'];files={}
for name in names:
 b=(HERE/name).read_bytes();files[name]=dict(bytes=len(b),sha256=digest(b))
root=digest(json.dumps(files,sort_keys=True,separators=(',',':')).encode());s=dict(kind='PHASE1_CAPTURE_OUTER_CONTROLLER_SOURCE_SEAL_V1',files=files,content_root_sha256=root,filesystem_readonly_claim=False,actual_parent_started=False,actual_parent_wait_returned=False,gate1='UNKNOWN')
with target.open('x',encoding='utf-8')as f:json.dump(s,f,indent=2)
print(json.dumps(dict(seal=str(target),seal_SHA256=digest(target.read_bytes()),content_root=root,controller=files[names[0]],tests=9,actual_parent_started=False),indent=2))

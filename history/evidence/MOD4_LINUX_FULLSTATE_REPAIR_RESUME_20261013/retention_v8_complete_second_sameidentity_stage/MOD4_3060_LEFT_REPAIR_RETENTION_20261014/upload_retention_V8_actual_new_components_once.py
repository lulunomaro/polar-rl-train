"""Root-only new V8 source upload; preserves every old source byte."""
from pathlib import Path
import sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as t
ROOT='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_RETENTION_20261014';t.ROOT=ROOT
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    receipt=R/'RETENTION_V8_TARGET_NEW_COMPONENTS_ACTUAL.json';assert not receipt.exists()
    proof=json.loads((R/'PLANE_METADATA_V7_INDEPENDENT_ACTUAL_CPU_REVIEW.json').read_bytes())
    assert proof['actual_new_metadata_query_consistency_review'] and proof['actual_boundary']['shared_OS_lock_free']
    z=D/'RETENTION_CPU_PREPARED_V8.zip';sha=H(z)
    assert z.stat().st_size==174839 and sha=='20c732a3795251e1f5327fb1da7097f20978d08e2bde9b86ef17c6c10de423f4'
    assert json.loads((R/'RETENTION_V8_REPRESENTED_REFERENCE_SYNTHETIC_CPU_PASSED.json').read_bytes())['passed_CPU_synthetic_only']
    c=t.connect();sf=None
    try:
        guard=t.py(c,t.guard_code());assert not guard['new_root_unused']
        sf=c.open_sftp();sf.get_channel().settimeout(60)
        try:sf.stat(ROOT+'/'+z.name)
        except FileNotFoundError:pass
        else:raise AssertionError('Existing upload path: use readonly outcome recovery')
        with sf.open(ROOT+'/'+z.name,'wx') as f:f.write(z.read_bytes());f.flush()
        code="""from pathlib import Path
import json,hashlib,zipfile,time,importlib.metadata as metadata,torch
R=Path(ROOT);P=R/'payload';S=Path(SHARED);z=R/ZIP
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(z)==SHA;new=[];preserved=[]
with zipfile.ZipFile(z) as f:
 for n in f.namelist():
  dst=P/n;assert dst.resolve().is_relative_to(P.resolve())
  if n.endswith('/'):dst.mkdir(parents=True,exist_ok=True);continue
  b=f.read(n)
  if dst.exists():assert dst.read_bytes()==b,('Existing source would change',n);preserved.append(n)
  else:
   dst.parent.mkdir(parents=True,exist_ok=True)
   with dst.open('xb') as out:out.write(b)
   new.append(n)
m=json.loads((P/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())
for row in m['package_files_v8']:assert H(P/row['relative'])==row['sha256'],row['relative']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
assert H(m['V7_actual_native_binding']['path'])==m['V7_actual_native_binding']['sha256']
assert H(m['v5_sdk_primary_stub']['actual_installed_stub_path'])==m['v5_sdk_primary_stub']['actual_sha256']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,value in sdk['versions'].items():
 if value is not None:assert metadata.version(name)==value,name
for row in sdk['files']:assert H(row['path'])==row['sha256'],row['path']
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),actual_uploaded_ZIP_SHA=SHA,new_files=new,existing_shared_bytes_preserved=preserved,target_source_and_SDK_binding_stub_exact=True,no_GPU=True,no_PPO=True)))
"""
        prefix='ROOT='+repr(ROOT)+'\nSHARED='+repr('D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload')+'\nZIP='+repr(z.name)+'\nSHA='+repr(sha)+'\n'
        value=t.py(c,prefix+code)
        receipt.write_text(json.dumps(dict(**value,actual_resource_boundary=guard),indent=2),encoding='utf8')
        print(json.dumps(dict(report=str(receipt),new_files=len(value['new_files']),existing_bytes_preserved=len(value['existing_shared_bytes_preserved']),no_GPU=True)))
    except BaseException:
        (R/('RETENTION_V8_ORIGINAL_UPLOAD_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),unknown_outcome_requires_readonly_recovery=True),indent=2),encoding='utf8');raise
    finally:
        if sf:sf.close()
        t.close(c)

if __name__=='__main__':main()

"""CPU-only sequential source upload. Preserves every existing V3/V4 byte."""
from pathlib import Path
import sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'));import transport_249_only as t
ROOT='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_RETENTION_20261014'
def main():
 receipt=R/'TYPED_RAYCAST_V6_TARGET_COMPONENTS_ACTUAL.json';assert not receipt.exists()
 prior=json.loads((R/'retention_baseline1aa_flat_120_v5_INDEPENDENT_BOUNDARY.json').read_bytes());assert prior['actual_parent_absent'] and prior['actual_child_absent'] and prior['shared_OS_lock_free']
 z=D/'retention_hardware_scalar_serializer_v6_CPU_COMPONENTS.zip';h=hashlib.sha256(z.read_bytes()).hexdigest();assert h=='c892004967b77b0e2d16a1ebd6ecdcc4419a45c8ebab682e3d91de1e743c6d8a' and z.stat().st_size==93057
 v=json.loads((R/'HARDWARE_SCALAR_V6_SYNTHETIC_CPU_FIXTURE_PASSED.json').read_bytes());assert v['passed_CPU_synthetic_only']
 c=t.connect();sf=None
 try:
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  try:sf.stat(ROOT+'/'+z.name)
  except FileNotFoundError:pass
  else:raise AssertionError('New V5 upload path exists; use readonly unknown-outcome recovery')
  sf.put(str(z),ROOT+'/'+z.name)
  code="""from pathlib import Path
import json,hashlib,zipfile,time
R=Path(ROOT);P=R/'payload';z=R/ZIP;assert hashlib.sha256(z.read_bytes()).hexdigest()==SHA
new=[];preserved=[]
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
m=json.loads((P/'RETENTION_CPU_MANIFEST_V6.json').read_bytes());stub=m['v5_sdk_primary_stub'];assert hashlib.sha256(Path(stub['actual_installed_stub_path']).read_bytes()).hexdigest()==stub['actual_sha256']
print(json.dumps(dict(epoch=time.time(),actual_uploaded_ZIP_SHA=SHA,new_files=new,existing_shared_bytes_preserved=preserved,actual_installed_API_stub_exact=True,no_GPU=True,no_PPO=True)))
"""
  value=t.py(c,'ROOT='+repr(ROOT)+'\nZIP='+repr(z.name)+'\nSHA='+repr(h)+'\n'+code)
  receipt.write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(dict(report=str(receipt),new_files=len(value['new_files']),existing_bytes_preserved=len(value['existing_shared_bytes_preserved']),no_GPU=True)))
 except BaseException:
  (R/('TYPED_RAYCAST_V6_ORIGINAL_UPLOAD_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),unknown_outcome_requires_actual_readonly_recovery=True),indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()

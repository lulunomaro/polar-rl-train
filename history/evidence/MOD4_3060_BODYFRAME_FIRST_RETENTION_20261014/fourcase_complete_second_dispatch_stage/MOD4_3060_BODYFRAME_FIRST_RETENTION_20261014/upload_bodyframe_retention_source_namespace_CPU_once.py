"""Root-only explicit new namespace upload/target CPU; no GPU launch or retries."""
from pathlib import Path
import argparse,sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';ROOT='D:/MOD4_async_eval/MOD4_3060_BODYFRAME_FIRST_RETENTION_20261014';SHARED='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute-root-upload',action='store_true');a=p.parse_args();assert a.execute_root_upload,'Explicit root execution flag required'
 proof=json.loads((R/'BODYFRAME_FIRST_RETENTION_CPU_PREPARED_ACTUAL.json').read_bytes());assert proof['CPU_prepared_no_remote_or_GPU']
 z=Path(proof['package']['path']);assert H(z)==proof['package']['sha256'] and z.stat().st_size==proof['package']['bytes']
 receipt=R/'BODYFRAME_FIRST_RETENTION_TARGET_SOURCE_UPLOAD_CPU_ACTUAL.json';intent=R/'BODYFRAME_FIRST_RETENTION_SOURCE_UPLOAD_INTENT_ACTUAL.json';assert not receipt.exists() and not intent.exists()
 sys.path.insert(0,str(D));import transport_249_own_f516_retention as t;t.ROOT=ROOT
 c=None;sf=None
 try:
  c=t.connect();guard=t.py(c,t.guard_code());assert guard['new_root_unused']
  intent.write_text(json.dumps(dict(epoch=time.time(),package=proof['package'],newroot=ROOT,unknown_outcome_requires_readonly_recovery=True),indent=2),encoding='utf8')
  sf=c.open_sftp();sf.get_channel().settimeout(60);sf.mkdir(ROOT)
  with sf.open(ROOT+'/'+z.name,'wx') as out:out.write(z.read_bytes());out.flush()
  code=r'''
from pathlib import Path
import json,hashlib,zipfile,torch,importlib.metadata as metadata,time
R=Path(ROOT);P=R/'payload';S=Path(SHARED);z=R/ZIP
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(z)==ZIP_SHA and not P.exists();P.mkdir();(R/'attempts').mkdir();(R/'leases').mkdir()
with zipfile.ZipFile(z) as f:
 for n in f.namelist():
  dst=P/n;assert dst.resolve().is_relative_to(P.resolve()) and not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True)
  with dst.open('xb') as out:out.write(f.read(n))
m=json.loads((P/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())
for row in m['package_files_v8']:assert H(P/row['relative'])==row['sha256'],row['relative']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
assert H(m['v5_sdk_primary_stub']['actual_installed_stub_path'])==m['v5_sdk_primary_stub']['actual_sha256']
assert H(m['V7_actual_native_binding']['path'])==m['V7_actual_native_binding']['sha256']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for n,v in sdk['versions'].items():
 if v is not None:assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
import sys
sys.path.insert(0,str(P))
from f516_retention_source_CPU_validator_v1 import validate_path
source=P/'source/model_32830_bodyframe_first.pt';owned=validate_path(source)
result=dict(epoch=time.time(),actual_new_namespace_created=True,source_whole20k_195_107_99_CPU_verified=True,source_owned_body_state_independently_validated=True,legacy_counts_apply_to_core_only=True,source_SHA=SOURCE_SHA,source_bytes=source.stat().st_size,target_source_and_SDK_binding_stub_exact=True,package_SHA=ZIP_SHA,no_GPU_no_PPO_no_budgetwrite=True,all_original_physics_mainloop_and_shared_source_bytes_preserved=True)
(R/'BODYFRAME_FIRST_RETENTION_UPLOAD_TARGET_CPU_ACTUAL_COMPLETE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''
  prefix='ROOT='+repr(ROOT)+'\nSHARED='+repr(SHARED)+'\nZIP='+repr(z.name)+'\nZIP_SHA='+repr(proof['package']['sha256'])+'\nSOURCE_SHA='+repr(proof['source_complete_file_SHA'])+'\n'
  value=t.py(c,prefix+code,90);receipt.write_text(json.dumps(dict(**value,actual_resource_boundary=guard),indent=2),encoding='utf8');print(json.dumps(dict(receipt=str(receipt),target_CPU_actual=True,no_GPU=True)))
 except BaseException:
  (R/('BODYFRAME_FIRST_RETENTION_UPLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),unknown_outcome_requires_readonly_recovery=True),indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  if c:t.close(c)
if __name__=='__main__':main()

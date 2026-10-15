"""New finite-A package upload/target CPU; no GPU or task dispatch here."""
from pathlib import Path
import hashlib,json,sys,time,traceback
D=Path(__file__).resolve().parent;Q=D/'payload';R=D/'reports'
import transport_s5_single_retention_A_actual as t
ROOT=t.ROOT;SHARED='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 proof=json.loads((R/'S5_SINGLE_RETENTION_A_CPU_PREPARED_ACTUAL.json').read_bytes());assert proof['CPU_prepared_no_remote_or_GPU']
 assert not (R/'S5_SINGLE_A_UPLOAD_INTENT.json').exists();z=Path(proof['package']['path']);assert H(z)==proof['package']['sha256'];c=sf=None
 try:
  c=t.connect();guard=t.py(c,t.guard_code());assert guard['new_root_unused'] and guard['shared_OS_lock_free']
  save('S5_SINGLE_A_UPLOAD_INTENT.json',dict(epoch=time.time(),root=ROOT,package=proof['package'],guard=guard,unknown_outcome_actual_readonly_not_retry=True))
  sf=c.open_sftp();sf.get_channel().settimeout(60);sf.mkdir(ROOT)
  with sf.open(ROOT+'/'+z.name,'wx') as f:f.write(z.read_bytes());f.flush()
  code=r'''
from pathlib import Path
import hashlib,json,zipfile,torch,sys,time,importlib.metadata as metadata
R=Path(C['root']);Q=R/'payload';S=Path(C['shared']);z=R/C['zip'];H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(z)==C['zipSHA'] and z.stat().st_size==C['zipbytes'] and not Q.exists();Q.mkdir();(R/'attempts').mkdir();(R/'leases').mkdir()
with zipfile.ZipFile(z) as f:
 for name in f.namelist():
  p=Q/name;assert p.resolve().is_relative_to(Q.resolve()) and not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(f.read(name))
assert H(Q/'RETENTION_CPU_MANIFEST_V8.json')==C['manifestSHA'];m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())
for row in m['package_files_v8']:assert (Q/row['relative']).stat().st_size==row['bytes'] and H(Q/row['relative'])==row['sha256'],row['relative']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
assert H(m['V7_actual_native_binding']['path'])==m['V7_actual_native_binding']['sha256'] and H(m['v5_sdk_primary_stub']['actual_installed_stub_path'])==m['v5_sdk_primary_stub']['actual_sha256']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for n,v in sdk['versions'].items():
 if v is not None:assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
source=m['source_single'];assert H(source['local_path'])==source['sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
whole=torch.load(source['local_path'],map_location='cpu',weights_only=False);tensors=[]
def walk(x):
 if torch.is_tensor(x):assert x.device.type=='cpu' and (not x.is_floating_point() or torch.isfinite(x).all());tensors.append(x)
 elif hasattr(x,'items'):
  for y in x.values():walk(y)
 elif isinstance(x,(list,tuple)):
  for y in x:walk(y)
walk(whole);assert sum(x.is_floating_point() for x in tensors)==102 and whole['E1_terrain_state']['num_envs']==20000 and len(whole['actor_state_dict'])==9
sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
rng=torch.get_rng_state().clone()
for n in (80,88):
 single=Single35(source['local_path'],n,'cpu');assert single.exact()
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),actual_targetCPU=True,sourceSHA=source['sha256'],whole_float102=True,source_saved_N20000=True,actor9_STD_source_exact=True,packageSHA=H(z),manifestSHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),package_files=len(m['package_files_v8']),shared_files=len(m['shared_source_freeze']),SDK_stub_binding_and_all_source_SHA_exact=True,no_CUDA_PPO_or_budget_write=True)))
'''
  ctx=dict(root=ROOT,shared=SHARED,zip=z.name,zipSHA=proof['package']['sha256'],zipbytes=proof['package']['bytes'],manifestSHA=proof['manifest_SHA'])
  v=t.py(c,'C='+repr(ctx)+'\n'+code,90);save('S5_SINGLE_A_UPLOAD_TARGET_CPU_ACTUAL.json',v);print(json.dumps(v))
 except BaseException:
  save('S5_SINGLE_A_UPLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_actual_readonly_first_no_retry=True));raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()

"""Preserve unexecuted V1; bind new V2 package, lease namespace and target path."""
from pathlib import Path
import ast,hashlib,json,shutil,time,zipfile
D=Path(__file__).resolve().parent;old=D/'curb113_frozen_v1';E=D/'curb113_frozen_v2';Q=E/'eval_payload_v2'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not E.exists()
error=dict(epoch=time.time(),id='curb113-v1-static-target-namespace-rejection',status='CPU_PRE_DISPATCH_REJECTED',no_network_GPU_Task_or_lease=True,
 findings=['V1 dispatcher ROOT CURB113_EVAL differs from manifest source CURB878_EVAL','V1 worker namespace CURB113_EVAL differs from lease local directory name curb113_frozen_v1'],original_preserved=True)
(D/'reports/CURB113_V1_STATIC_TARGET_NAMESPACE_REJECTION_ACTUAL.json').write_text(json.dumps(error,indent=2))
shutil.copytree(old/'eval_payload_v2',Q)
(E/'reports').mkdir()
root='D:/MOD4_async_eval/'+D.name+'/'+E.name
worker=Q/'paired_full80_parameter_bound_v2.py';s=worker.read_text();s=s.replace("lease['namespace']=='MOD4_THREE_EXPERTS_AND_CURB113_EVAL_20261016'", "lease['namespace']=="+repr(E.name));worker.write_text(s,encoding='utf8')
mfile=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';m=json.loads(mfile.read_bytes());m['source_single_policy']['local_path']=root+'/payload/source/CURB113.pt'
for row in m['file_rows']:
 p=Q/row['relative'];row.update(bytes=p.stat().st_size,sha256=H(p))
mfile.write_text(json.dumps(m,indent=2),encoding='utf8')
for name in ['dispatch_curb113_frozen3060_unused_case_once.py','collect_curb113_own_case_actual_readonly.py','review_curb113_actual_physical_source_route_CPU.py']:
 s=(old/name).read_text();s=s.replace('D:/MOD4_async_eval/MOD4_THREE_EXPERTS_AND_CURB113_EVAL_20261016/curb113_frozen_v1',root)
 compile(s,name,'exec');(E/name).write_text(s,encoding='utf8')
z=E/'CURB113_FROZEN_3060_V2.zip'
with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as a:
 for p in sorted(Q.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:a.write(p,p.relative_to(Q).as_posix())
prep=json.loads((old/'reports/CURB113_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').read_bytes())
prep.update(epoch=time.time(),source=m['source_single_policy'],package=dict(path=str(z.resolve()),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(mfile),worker_SHA=H(worker),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),scripts=[str((E/n).resolve()) for n in ['dispatch_curb113_frozen3060_unused_case_once.py','collect_curb113_own_case_actual_readonly.py','review_curb113_actual_physical_source_route_CPU.py']],old_V1_preserved_never_dispatched=True)
assert prep['source']['local_path']==root+'/payload/source/CURB113.pt'
assert prep['source']['sha256']==H(Q/'source/CURB113.pt')
assert "lease['namespace']=="+repr(E.name) in worker.read_text()
assert H(Q/'full80_runtime_native_v1.py')==H(old/'eval_payload_v2/full80_runtime_native_v1.py')
for row in m['file_rows']:assert H(Q/row['relative'])==row['sha256']
(E/'reports/CURB113_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
print(json.dumps(dict(CPU_static_binding_passed=True,source=prep['source'],root=root,namespace=E.name,package=prep['package'],no_target_pass_claimed=True)))

"""Finite readonly exact SDK/source copy; no72 mutation, models, GPU or ledger."""
from pathlib import Path
import base64,hashlib,importlib.util,json,sys,time,traceback
HERE=Path(__file__).resolve().parent;W=HERE.parents[2]
REPORTS=HERE/'reports'
CODE=r'''from pathlib import Path
import base64,hashlib,io,json,os,sys,zipfile,importlib.util,importlib.metadata as md
sdk=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1')
names=('isaaclab','isaaclab_rl','isaacsim','rsl-rl-lib','torch','torchvision','numpy','warp-lang','tensordict','scipy','gymnasium','pip','setuptools','wheel')
versions={};metadata={}
for name in names:
 try:
  d=md.distribution(name);versions[name]=d.version
  metadata[name]=dict(metadata_path=str(d._path),requires=d.requires,direct_url=d.read_text('direct_url.json'))
 except md.PackageNotFoundError:versions[name]=None
assert versions['isaaclab']=='6.1.14' and versions['torch']=='2.10.0+cu128' and versions['rsl-rl-lib']=='5.0.1'
origins={name:md.distribution(name).read_text('direct_url.json') for name in ('isaaclab','isaaclab_rl')}
modules={}
for name in ('isaaclab','isaaclab_rl'):
 s=importlib.util.find_spec(name);assert s is not None;modules[name]=dict(origin=s.origin,locations=list(s.submodule_search_locations or []))
assert sdk.is_dir()
buf=io.BytesIO();rows=[];total=0
with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for relative in ('apps','source'):
  root=sdk/relative;assert root.is_dir()
  for p in sorted(root.rglob('*')):
   if not p.is_file() or p.is_symlink() or any(x in ('__pycache__','.git','build','dist') for x in p.parts):continue
   size=p.stat().st_size;assert size<32*1024**2
   total+=size;assert total<256*1024**2 and len(rows)<30000
   before=p.stat();raw=p.read_bytes();after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
   rel=p.relative_to(sdk).as_posix();z.writestr(rel,raw);rows.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 for p in [sdk/'LICENSE',sdk/'README.md',sdk/'pyproject.toml',sdk/'isaaclab.sh']:
  if not p.is_file() or p.is_symlink():continue
  before=p.stat();raw=p.read_bytes();after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  rel=p.relative_to(sdk).as_posix();z.writestr(rel,raw);rows.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 assert any(r['relative']=='LICENSE' for r in rows),'full source license required'
raw=buf.getvalue()
print(json.dumps(dict(passed=True,executable=sys.executable,versions=versions,metadata=metadata,module_origins=modules,source_root=str(sdk),source_files=rows,
 archive_bytes=len(raw),archive_SHA=hashlib.sha256(raw).hexdigest(),archive_base64=base64.b64encode(raw).decode(),
 source_only_no_PT_GPU_SDK_import_or_ledger_IO=True,no_remote_file_written=True)))
'''
def save(name,value):
 with (REPORTS/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 REPORTS.mkdir(exist_ok=True);save('EXACT72_SDK_SOURCE_EXTRACTION_ENTERED_ACTUAL.json',dict(epoch=time.time(),no_old_once_reuse=True,no_GPU_PT_or_account=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 path=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py'
 sp=importlib.util.spec_from_file_location('existing72_memory_recovery_only',path);sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None;result=d.code(c,d.PY72,CODE,{},timeout=120)
  raw=base64.b64decode(result.pop('archive_base64'));assert len(raw)==result['archive_bytes'] and hashlib.sha256(raw).hexdigest()==result['archive_SHA']
  p=HERE/'EXACT72_ISAACLAB_SOURCE_AND_APPS.zip'
  with p.open('xb') as f:f.write(raw)
  result.update(actual_finite_returned=True,local_archive_path=str(p),epoch=time.time())
  save('EXACT72_SDK_SOURCE_EXTRACTION_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(passed=True,source_files=len(result['source_files']),archive_bytes=len(raw),archive_SHA=result['archive_SHA'],versions=result['versions'],actual_returned=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('EXACT72_SDK_SOURCE_EXTRACTION_ORIGINAL_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),epoch=time.time(),no_remote_mutation_or_model=True));raise

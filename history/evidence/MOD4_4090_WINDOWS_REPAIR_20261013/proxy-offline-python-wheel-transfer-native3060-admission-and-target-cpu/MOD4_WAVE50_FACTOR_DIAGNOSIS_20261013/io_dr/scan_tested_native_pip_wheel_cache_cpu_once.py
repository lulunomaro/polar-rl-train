from pathlib import Path
import json,time,zipfile,hashlib,importlib.metadata as m
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from email.parser import Parser
W=Path('C:/Users/lulu/Desktop/claude/mjcf');F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr';cache=Path('C:/Users/lulu/AppData/Local/pip/Cache')
out=F/'WINDOWS4090_TESTED_PIP_CACHE_MINIMAL_DEPENDENCY_CPU_ACTUAL.json';assert not out.exists()
seeds={'isaacsim':{'all','extscache'},'isaaclab':{''},'isaaclab_rl':{'rsl-rl'},'isaaclab_assets':{''},'isaaclab_tasks':{''},'torch':{''},'torchvision':{''},'tensordict':{''},'warp-lang':{''},'rsl-rl-lib':{''},'scipy':{''},'psutil':{''},'setuptools':{''},'wheel':{''}}
wanted={canonicalize_name(k):set(v) for k,v in seeds.items()};processed={};missing_local=[]
while True:
 pending=[name for name,x in wanted.items() if processed.get(name)!=x]
 if not pending:break
 for name in pending:
  extras=wanted[name].copy();processed[name]=extras.copy()
  try:d=m.distribution(name)
  except m.PackageNotFoundError:missing_local.append(name);continue
  for text in d.requires or []:
   r=Requirement(text)
   if r.marker is not None and not any(r.marker.evaluate({'extra':e}) for e in extras|{''}):continue
   key=canonicalize_name(r.name)
   wanted.setdefault(key,set()).update(r.extras or {''})
versions={name:m.version(name) for name in wanted if name not in missing_local}
editable={canonicalize_name(x) for x in ('isaaclab','isaaclab_rl','isaaclab_assets','isaaclab_tasks')}
matches={};scanned=0;zip_errors=[]
for p in list(cache.rglob('*.body'))+list(cache.rglob('*.whl')):
 scanned+=1
 try:
  if not zipfile.is_zipfile(p):continue
  with zipfile.ZipFile(p) as z:
   meta=[n for n in z.namelist() if n.endswith('.dist-info/METADATA')]
   if len(meta)!=1:continue
   text=z.read(meta[0]).decode('utf8');headers=Parser().parsestr(text);name=canonicalize_name(headers['Name']);version=headers['Version']
   if name in editable or versions.get(name)!=version:continue
   wheel=meta[0].rsplit('/',1)[0]+'/WHEEL';wh=Parser().parsestr(z.read(wheel).decode('utf8'));tags=wh.get_all('Tag') or []
   if not tags or not any(t.endswith(('win_amd64','any')) and (t.startswith(('cp311','py3','py2.py3')) or 'abi3' in t) for t in tags):continue
   row=dict(path=str(p),bytes=p.stat().st_size,distribution=name,version=version,tags=tags,metadata_SHA256=hashlib.sha256(text.encode()).hexdigest(),needs_hash_before_actual_copy=True)
   if name not in matches or row['bytes']>matches[name]['bytes']:matches[name]=row
 except Exception as e:zip_errors.append(dict(path=str(p),error_type=type(e).__name__,error=str(e)))
report=dict(epoch=time.time(),CPU_cache_only_no_existing_files_modified=True,no_GPU_or_installedSDKimport=True,dependency_scope='actual testednative required closure, isaacsim all/extscache +4editables +rsl_rl only, Windows311 markers',cache_root=str(cache),cache_files_scanned=scanned,wanted_versions=versions,editable_source_already_exact_not_wheel=sorted(editable),selected_matching_cache_wheels=list(matches.values()),total_matching_bytes=sum(x['bytes'] for x in matches.values()),missing_wheels=[dict(name=n,version=v) for n,v in versions.items() if n not in editable and n not in matches],missing_local_dependency_metadata=missing_local,reader_zip_errors=zip_errors,not_whole_environment_copy=True,archive_or_remote_transfer_not_performed=True,Git_archive_pending_root=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),scanned=scanned,matching=len(matches),bytes=report['total_matching_bytes'],missing=report['missing_wheels']),ensure_ascii=True))

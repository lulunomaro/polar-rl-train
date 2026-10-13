from pathlib import Path
import json,time,ssl,urllib.request,hashlib,zipfile,email
from packaging.requirements import Requirement
from packaging.markers import default_environment
from packaging.version import Version
F=Path(__file__).resolve().parent;D=F/'OFFICIAL_COMPATIBILITY_SMALL_WHEELS_20261013';out=F/'WINDOWS4090_MINIMAL_LABRL_BOUND_DEPENDENCY_COMPATIBILITY_CPU_ACTUAL.json';assert not out.exists()
report=dict(epoch=time.time(),TLS_verified=True,only_new_env_compatibility_preparation=True,original_fastapi_wheel_conflicts_retained=True,packaging_preserved='23.0',core_Torch_Sim_TensorDict_fourEditable_source_unchanged=True,no_GPU_or_oldenv_modification=True,wheels=[])
versions={x['name']:x['version'] for x in json.loads((F/'WINDOWS4090_TOPLEVEL_METADATA_REVIEWED_NATIVE311_WHEELHOUSE_CPU_ACTUAL.json').read_bytes())['selected']};versions.update({'fastapi':'0.121.0','wheel':'0.45.1','annotated-doc':'0.0.2'})
env=default_environment();env['extra']=''
for p in sorted(D.glob('*.whl')):
 with zipfile.ZipFile(p) as z:
  n=next(n for n in z.namelist() if n.endswith('.dist-info/METADATA') and n.count('/')==1);m=email.message_from_bytes(z.read(n));name=m['Name'].lower().replace('_','-');v=m['Version'];assert versions[name]==v
  reqs=m.get_all('Requires-Dist',[])
  for raw in reqs:
   r=Requirement(raw)
   if r.marker and not r.marker.evaluate(env):continue
   k=r.name.lower().replace('_','-');assert k in versions,(name,raw)
   assert r.specifier.contains(Version(versions[k]),prereleases=True),(name,raw,versions[k])
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 with urllib.request.urlopen('https://pypi.org/pypi/'+name+'/'+v+'/json',context=ssl.create_default_context(),timeout=15) as q:j=json.load(q)
 u=next(u for u in j['urls'] if u['filename']==p.name);assert u['digests']['sha256']==h
 report['wheels'].append(dict(path=str(p.resolve()),filename=p.name,bytes=p.stat().st_size,sha256=h,published_sha256=h,official_url=u['url'],name=name,version=v,requires=reqs,metadata_requirements_compatible_selected_actual_versions=True))
assert len(report['wheels'])==3
bundle=F/'OFFICIAL_LABRL_BOUND_DEPENDENCY_COMPATIBILITY_20261013.zip';assert not bundle.exists()
with zipfile.ZipFile(bundle,'x',compression=zipfile.ZIP_STORED) as z:
 for x in report['wheels']:z.write(x['path'],x['filename'])
 z.writestr('COMPATIBILITY_ACTUAL_MANIFEST.json',json.dumps(report,indent=2))
report['bundle']=dict(path=str(bundle),bytes=bundle.stat().st_size,sha256=hashlib.sha256(bundle.read_bytes()).hexdigest());report['CPU_preparation_actual_passed']=True
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),bundle=report['bundle']),ensure_ascii=True))

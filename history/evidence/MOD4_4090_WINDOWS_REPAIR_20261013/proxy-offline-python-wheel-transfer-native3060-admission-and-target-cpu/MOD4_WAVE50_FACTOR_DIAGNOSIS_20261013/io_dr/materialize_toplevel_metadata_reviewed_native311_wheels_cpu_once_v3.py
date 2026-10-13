"""Copy exact native cache bytes to a new owned wheelhouse; never modify cache."""
from pathlib import Path
import json,time,hashlib,shutil,zipfile,email,urllib.request,ssl
from packaging.tags import sys_tags,parse_tag
from packaging.utils import canonicalize_name,parse_wheel_filename
F=Path(__file__).resolve().parent
out=F/'WINDOWS4090_TOPLEVEL_METADATA_REVIEWED_NATIVE311_WHEELHOUSE_CPU_ACTUAL.json'
if out.exists():raise RuntimeError('materialization receipt already exists; never replay once')
assert __import__('sys').version_info[:2]==(3,11)
scan=json.loads((F/'WINDOWS4090_TESTED_PIP_CACHE_MINIMAL_DEPENDENCY_CPU_ACTUAL.json').read_bytes())
rows=scan.get('matching_wheels',scan.get('wheels'))
if rows is None:
 for k,v in scan.items():
  if isinstance(v,list) and v and isinstance(v[0],dict) and 'metadata_SHA256' in v[0]:rows=v;break
assert rows is not None
small=F/'OFFICIAL_MISSING_SMALL_WHEELS_20261013'
for p in sorted(small.glob('*.whl')):rows.append(dict(path=str(p),bytes=p.stat().st_size,official_small_download=True))
compatible=set(sys_tags());selected={};report=dict(epoch=time.time(),native311=True,source_cache_unchanged=True,no_GPU_or_SDKimport=True,selected=[],rejected=[],official_small=[],Git_archive_pending_root=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
try:
 for row in rows:
  p=Path(row['path'])
  with zipfile.ZipFile(p) as z:
   mn=[n for n in z.namelist() if n.endswith('.dist-info/METADATA') and n.count('/')==1];wn=[n for n in z.namelist() if n.endswith('.dist-info/WHEEL') and n.count('/')==1]
   assert len(mn)==len(wn)==1
   m=email.message_from_bytes(z.read(mn[0]));wm=email.message_from_bytes(z.read(wn[0]));tags=wm.get_all('Tag',[])
   parsed=set().union(*(parse_tag(t) for t in tags))
   if not(parsed&compatible):report['rejected'].append(dict(path=str(p),tags=tags,reason='actual Windows311 sys_tags incompatible'));continue
   name=canonicalize_name(m['Name']);ver=m['Version'];assert scan['wanted_versions'][name]==ver
   if name in selected:report['rejected'].append(dict(path=str(p),reason='one compatible artifact for same distribution/version already selected'));continue
   # Native tested wheels here use a single Tag; compressed multiple tag variants require independent review.
   tag_string='.'.join(sorted({t.interpreter for t in parsed}))+'-'+'.'.join(sorted({t.abi for t in parsed}))+'-'+'.'.join(sorted({t.platform for t in parsed}));assert parse_tag(tag_string)==parsed,'compressed Tag axes not exact Cartesian product'
   build=wm.get('Build');bn=name.replace('-','_')+'-'+ver+('-'+build if build else '')+'-'+tag_string+'.whl'
   parsedname,parsedver,_,parsedtags=parse_wheel_filename(bn);assert canonicalize_name(parsedname)==name and str(parsedver)==ver and parsedtags==parsed
   selected[name]=dict(source=p,filename=bn,bytes=p.stat().st_size,version=ver,tags=tags,official_small=row.get('official_small_download',False))
 total=sum(x['bytes'] for x in selected.values());free=shutil.disk_usage(F).free;guard=2*total+2*1024**3
 report.update(selected_bytes=total,actual_durable_free=free,required_durable_guard=guard,guardpassed=free>=guard)
 assert free>=guard,'actual durable guard failed'
 wh=F/'TESTED_MINIMAL_NATIVE311_WHEELHOUSE_20261013';assert not wh.exists();wh.mkdir()
 for name,r in selected.items():
  src=r.pop('source');h=sha(src)
  if r['official_small']:
   with urllib.request.urlopen('https://pypi.org/pypi/'+name+'/'+r['version']+'/json',timeout=15,context=ssl.create_default_context()) as q:j=json.load(q)
   official=[u for u in j['urls'] if u['filename']==r['filename']];assert len(official)==1 and official[0]['digests']['sha256']==h
   report['official_small'].append(dict(name=name,url=official[0]['url'],published_sha256=h,source=str(src),bytes=r['bytes']))
  dst=wh/r['filename'];shutil.copyfile(src,dst);assert dst.stat().st_size==r['bytes'] and sha(dst)==h and sha(src)==h
  report['selected'].append(dict(name=name,source=str(src),destination=str(dst),sha256=h,**r))
  out.write_text(json.dumps(report,indent=2),encoding='utf8')
 (wh/'ACTUAL_WHEELHOUSE_MANIFEST.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 bundle=F/'TESTED_MINIMAL_NATIVE311_WHEELHOUSE_20261013.zip';assert not bundle.exists()
 with zipfile.ZipFile(bundle,'x',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
  for p in sorted(wh.iterdir()):z.write(p,p.name)
 report['bundle']=dict(path=str(bundle),bytes=bundle.stat().st_size,sha256=sha(bundle),compression='ZIP_STORED',ZIP64=True)
 report['complete']=True;report['seconds']=time.time()-report['epoch'];out.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(out),count=len(selected),bundle=report['bundle'],missing=[dict(name=n,version=v) for n,v in scan['wanted_versions'].items() if n not in selected and n not in ('isaaclab','isaaclab-rl','isaaclab-assets','isaaclab-tasks')]),ensure_ascii=True))
except Exception as e:
 report['error_type']=type(e).__name__;report['error']=str(e);report['complete']=False;out.write_text(json.dumps(report,indent=2),encoding='utf8');raise

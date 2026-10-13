from pathlib import Path
import json,time,hashlib,zipfile,shutil,email,sys
from packaging.tags import sys_tags,parse_tag
R=Path(__file__).resolve().parent
out=R/'install_reports/NATIVE311_WHEELHOUSE_MISSING4_INDEPENDENT_CPU_ACTUAL.json';assert not out.exists()
p=R/'packages/TESTED_MINIMAL_NATIVE311_WHEELHOUSE_20261013.zip'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
assert p.stat().st_size==4533794337 and sha(p)=='9c90884ec8c5cdc91a0ed0483e6b875357060fa9900ef425c8eb3384a12c8ed6'
guard=2*p.stat().st_size+2*1024**3;free=shutil.disk_usage(R).free;assert free>=guard
dest=R/'native311_wheelhouse';assert not dest.exists();dest.mkdir()
proof=json.loads((R/'install_reports/MISSING4_INDEPENDENT_ARTIFACT_CPU_ACTUAL.json').read_bytes());assert len(proof['files'])==4
report=dict(epoch=time.time(),python=sys.executable,bundle=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)),actual_durable_free=free,required_durable_guard=guard,original_cache_not_modified=True,no_GPU_Kit_PPO=True,extracted=[],missing4=[])
with zipfile.ZipFile(p) as z:
 m=json.loads(z.read('ACTUAL_WHEELHOUSE_MANIFEST.json'));assert len(m['selected'])==176
 expected={x['filename']:x for x in m['selected']}
 for n in z.namelist():
  if n=='ACTUAL_WHEELHOUSE_MANIFEST.json':continue
  assert n in expected and '/' not in n and '\\' not in n and ':' not in n
  target=dest/n
  with z.open(n) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst,8*1024**2)
  row=expected[n];assert target.stat().st_size==row['bytes'] and sha(target)==row['sha256'];report['extracted'].append(dict(path=str(target),bytes=target.stat().st_size,sha256=row['sha256'],name=row['name'],version=row['version']))
needed={'isaacsim-kernel','isaacsim-extscache-kit','isaacsim-asset','isaacsim-robot-motion'};actualnames=set();tags=set(sys_tags())
for item in proof['files']:
 f=Path(item['path']);assert f.is_relative_to(R/'official_missing_nvidia_wheels_v4')
 assert f.stat().st_size==item['bytes'] and sha(f)==item['sha256']
 with zipfile.ZipFile(f) as z:
  mn=[n for n in z.namelist() if n.endswith('.dist-info/METADATA') and n.count('/')==1];wn=[n for n in z.namelist() if n.endswith('.dist-info/WHEEL') and n.count('/')==1];assert len(mn)==len(wn)==1
  md=email.message_from_bytes(z.read(mn[0]));wm=email.message_from_bytes(z.read(wn[0]));name=md['Name'].lower().replace('_','-');assert name in needed and md['Version']=='5.1.0.0'
  compatible=set().union(*(parse_tag(t) for t in wm.get_all('Tag',[])));assert compatible&tags
  assert name not in actualnames;actualnames.add(name)
 target=dest/f.name;shutil.copyfile(f,target);assert sha(target)==item['sha256'];report['missing4'].append(dict(path=str(target),bytes=target.stat().st_size,sha256=item['sha256'],name=name,version=md['Version'],official_verified_proxy_download=True))
assert actualnames==needed
allrows=report['extracted']+report['missing4'];req=R/'ACTUAL_NATIVE311_FULL_WHEELHOUSE_PINS.txt';assert not req.exists()
with req.open('x',encoding='utf8') as f:
 for row in sorted(allrows,key=lambda x:x['name']):f.write(row['name']+'=='+row['version']+' --hash=sha256:'+row['sha256']+'\n')
report.update(requirement_file=str(req),actual_pinned_wheels=len(allrows),complete=True,no_full_SDK_GPU_admission_claimed=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),count=len(allrows),no_GPU=True)))

"""Official PEP658 small metadata, verified against its published SHA. No wheels."""
from pathlib import Path
from email.parser import BytesParser
import hashlib,json,time,urllib.request,urllib.parse
B=Path(__file__).resolve().parent;R=B/'reports';base=json.loads((R/'OFFICIAL_TORCH211_VISION026_PRIMARY_PIN_CANDIDATES_ACTUAL.json').read_bytes());rows=[]
for p in base['pins']:
 expected=p['index_metadata_attributes']['data-core-metadata'];assert expected.startswith('sha256=');url=urllib.parse.urldefrag(p['official_url'])[0]+'.metadata'
 with urllib.request.urlopen(url,timeout=20) as response:
  assert urllib.parse.urlsplit(response.url).scheme=='https';raw=response.read(1024**2+1);assert len(raw)<=1024**2
 assert hashlib.sha256(raw).hexdigest()==expected.split('=',1)[1];path=R/(p['package']+'_EXACT_CU128_WHEEL_FULL_METADATA_UTF8.txt')
 with path.open('xb') as f:f.write(raw)
 m=BytesParser().parsebytes(raw);assert m['Name']==p['package'] and m['Version']==p['version'];requires=m.get_all('Requires-Dist',[])
 if p['package']=='torchvision':assert any(x.replace(' ','')=='torch==2.11.0' for x in requires)
 if p['package']=='torch':assert any('cu12' in x or '12.8' in x for x in requires) and not any('cu13' in x for x in requires)
 rows.append(dict(**p,exact_metadata_url=url,exact_metadata_path=str(path),exact_metadata_bytes=len(raw),exact_metadata_SHA=hashlib.sha256(raw).hexdigest(),exact_wheel_requires_dist=requires,metadata_published_SHA_passed=True))
v=dict(epoch=time.time(),passed=True,pins=rows,default_PyPI_torch_metadata_is_not_the_selected_CUDA128_build=True,actual_newhost_joint_resolve_install_pipcheck_SDK_and_fullrestore_pending=True,no_wheel_download_SSH_or_install=True)
with (R/'EXACT_CU128_TORCH211_VISION026_PEP658_METADATA_PINS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v))

"""Public official metadata only. No SSH, credentials, package installation or GPU."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,time,urllib.request,urllib.parse
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.rows=[]
 def handle_starttag(self,t,a):
  if t=='a':self.rows.append(dict(a))
def fetch(url,name):
 with urllib.request.urlopen(url,timeout=20) as response:
  assert urllib.parse.urlsplit(response.url).scheme=='https';data=response.read(8*1024**2+1);assert len(data)<=8*1024**2
 with (R/name).open('xb') as f:f.write(data)
 return data,dict(url=url,path=str(R/name),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),default_TLS_hostname_CA_verification=True)
sources=[];values={}
for package,version in [('torch','2.11.0'),('torchvision','0.26.0')]:
 raw,row=fetch('https://pypi.org/pypi/'+package+'/'+version+'/json','OFFICIAL_'+package+'_'+version+'_PRIMARY_FULL_UTF8.json');sources.append(row);values[package]=json.loads(raw)['info'];assert values[package]['version']==version
requires=values['torchvision']['requires_dist'];assert 'torch==2.11.0' in requires or 'torch (==2.11.0)' in requires
pins=[]
for package,version in [('torch','2.11.0'),('torchvision','0.26.0')]:
 index='https://download.pytorch.org/whl/cu128/'+package+'/'
 raw,row=fetch(index,'OFFICIAL_'+package+'_CU128_INDEX_FULL_UTF8.txt');sources.append(row);p=Links();p.feed(raw.decode());filename=package+'-'+version+'+cu128-cp312-cp312-manylinux_2_28_x86_64.whl';matches=[]
 for link in p.rows:
  url=urllib.parse.urljoin(index,link.get('href',''));u=urllib.parse.urlsplit(url)
  if urllib.parse.unquote(u.path).endswith('/'+filename):matches.append((url,link))
 assert len(matches)==1,(filename,len(matches));url,link=matches[0];u=urllib.parse.urlsplit(url);assert u.scheme=='https' and u.hostname in ('download.pytorch.org','download-r2.pytorch.org');digest=urllib.parse.parse_qs(u.fragment)['sha256'][0];assert len(digest)==64
 pins.append(dict(package=package,version=version+'+cu128',filename=filename,official_index=index,official_url=url,published_SHA=digest,index_metadata_attributes=link))
value=dict(epoch=time.time(),passed_public_metadata=True,source='official PyPI and PyTorch CUDA128 indexes',vendor_runtime_change_is_explicit_not_exact72_Torch=True,pins=pins,torch_requires_dist=values['torch']['requires_dist'],vision_requires_dist=requires,source_receipts=sources,no_SSH_install_GPU_or_model=True,actual_newhost_joint_runtime_resolution_install_pipcheck_and_SDK_restore_pending=True)
with (R/'OFFICIAL_TORCH211_VISION026_PRIMARY_PIN_CANDIDATES_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
print(json.dumps(value))

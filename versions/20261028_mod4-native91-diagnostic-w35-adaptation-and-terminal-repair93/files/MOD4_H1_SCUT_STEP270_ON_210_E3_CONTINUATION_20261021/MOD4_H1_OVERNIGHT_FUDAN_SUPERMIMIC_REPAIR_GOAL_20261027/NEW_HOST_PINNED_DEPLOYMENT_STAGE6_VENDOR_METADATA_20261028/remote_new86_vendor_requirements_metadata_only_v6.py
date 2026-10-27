"""One bounded package-METADATA audit. No install, SDK/Torch import or GPU load."""
from pathlib import Path
from html.parser import HTMLParser
from email.parser import BytesParser
import ast,hashlib,json,os,re,time,traceback,urllib.request,urllib.parse,zipfile
ROOT=Path('/data/robemo/polar-rl-train');RUN=ROOT/'setup_runs/W35_PINNED_ENV_STAGE6_VENDOR_METADATA_20261028_V6';S1=ROOT/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1'
DEADLINE=time.time()+90
def put(name,value):
 with (RUN/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def progress(stage,**fields):print(json.dumps(dict(stage=stage,epoch=time.time(),**fields)),flush=True)
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def fetch(url,name):
 assert time.time()<DEADLINE-15
 req=urllib.request.Request(url,headers={'User-Agent':'MOD4-owned-vendor-metadata-audit/6'})
 with urllib.request.urlopen(req,timeout=15) as response:
  body=response.read(2*1024**2+1);assert response.status==200 and len(body)<=2*1024**2
  final=response.url;assert urllib.parse.urlsplit(final).scheme=='https'
 p=RUN/name
 with p.open('xb') as f:f.write(body)
 return body,dict(url=url,actual_final_url=final,bytes=len(body),SHA=hashlib.sha256(body).hexdigest(),default_CA_TLS_hostname_validation=True)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.rows=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.rows.append(dict(attrs))
def metadata(raw):
 m=BytesParser().parsebytes(raw)
 return dict(name=m['Name'],version=m['Version'],requires_dist=m.get_all('Requires-Dist',[]),requires_python=m['Requires-Python'],metadata_SHA=hashlib.sha256(raw).hexdigest())
def main():
 assert ROOT.resolve()==ROOT and RUN.resolve().is_relative_to(ROOT) and not ROOT.is_symlink()
 marker=json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert marker['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700'
 progress('VENDOR_REQUIREMENTS_METADATA_ONLY_STARTED',no_install=True)
 html,primary=fetch('https://pypi.nvidia.com/isaacsim-kernel/','OFFICIAL_ISAACSIM_KERNEL_SIMPLE_INDEX_UTF8.txt');links=Links();links.feed(html.decode('utf8'))
 filename='isaacsim_kernel-6.0.1.0-cp312-none-manylinux_2_35_x86_64.whl'
 rows=[r for r in links.rows if urllib.parse.unquote(urllib.parse.urlsplit(urllib.parse.urljoin(primary['actual_final_url'],r.get('href',''))).path).endswith('/'+filename)]
 assert len(rows)==1,'exact official target kernel wheel link must be unique'
 wheel_url=urllib.parse.urljoin(primary['actual_final_url'],rows[0]['href']);u=urllib.parse.urlsplit(wheel_url);assert u.scheme=='https'
 published=urllib.parse.parse_qs(u.fragment).get('sha256');assert published and len(published)==1 and re.fullmatch('[0-9a-f]{64}',published[0])
 # The kernel wheel already downloaded by Stage5 is reused. Only owned cache/tmp
 # directories are searched. Completed Torch/vision wheels are not opened.
 roots=[S1/'cache/pip',ROOT/'setup_runs/W35_PINNED_ENV_STAGE5_CACHE_CONTINUE_20261028_V5/tmp']
 found=None;seen=0;needle='isaacsim_kernel-6.0.1.0.dist-info/METADATA'
 for base in roots:
  if not base.is_dir():continue
  for current,dirs,names in os.walk(base,followlinks=False):
   dirs[:]=[d for d in dirs if not (Path(current)/d).is_symlink()]
   for name in names:
    seen+=1;assert seen<=12000 and time.time()<DEADLINE-10,'bounded owncache metadata search'
    p=Path(current)/name
    if p.suffix not in ('.body','.whl') or p.is_symlink() or not p.resolve().is_relative_to(ROOT):continue
    # Kernel6.0.1.0 is73.5MB in the actual Stage5 download receipt. A broad
    # byte range excludes already verified multi-GB Torch and8MB vision.
    if not 50*1024**2<p.stat().st_size<100*1024**2:continue
    try:
     with zipfile.ZipFile(p) as z:
      if needle not in z.namelist():continue
      raw=z.read(needle)
    except zipfile.BadZipFile:continue
    assert H(p)==published[0],'cached kernel wheel must match official published fullSHA'
    found=dict(cache_path=str(p),bytes=p.stat().st_size,official_published_SHA=published[0],official_link=wheel_url,metadata=metadata(raw))
    with (RUN/'OFFICIAL_CACHED_KERNEL_FULL_METADATA_UTF8.txt').open('xb') as f:f.write(raw)
    break
   if found:break
  if found:break
 assert found,'already-downloaded kernel wheel not located; no blind redownload'
 assert found['metadata']['name'].lower().replace('_','-')=='isaacsim-kernel' and found['metadata']['version']=='6.0.1.0'
 numpy=[x for x in found['metadata']['requires_dist'] if re.match(r'^numpy\b',x,re.I)];assert len(numpy)==1 and re.sub(r'\s+','',numpy[0])=='numpy==2.3.1'
 source=[]
 for module in ('isaaclab','isaaclab_rl','isaaclab_physx','isaaclab_ov','isaaclab_ovphysx'):
  p=S1/'sdk/source'/module/'setup.py';assert p.resolve().is_relative_to(ROOT) and p.is_file();raw=p.read_bytes();tree=ast.parse(raw)
  assignments=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INSTALL_REQUIRES' for t in n.targets)]
  requirements=ast.literal_eval(assignments[0].value) if assignments else None
  source.append(dict(path=str(p),SHA=hashlib.sha256(raw).hexdigest(),INSTALL_REQUIRES=requirements))
 # Public primary JSON responses are retained whole; no guessed SDK version.
 public=[]
 for name,version in [('numpy','2.3.1'),('packaging','23.2')]:
  raw,r=fetch('https://pypi.org/pypi/'+name+'/'+version+'/json','OFFICIAL_'+name+'_'+version+'_JSON_UTF8.json');v=json.loads(raw);assert v['info']['version']==version
  public.append(dict(source=r,requires_dist=v['info'].get('requires_dist'),requires_python=v['info'].get('requires_python')))
 bootstrap=[]
 for p in (S1/'venv/lib/python3.12/site-packages').glob('wheel-*.dist-info/METADATA'):
  raw=p.read_bytes();bootstrap.append(dict(path=str(p),value=metadata(raw)))
 plan=dict(schema='mod4.new86.explicit.vendor.runtime_environment.v1',new_runtime_venv_under=str(ROOT/'runtime_envs/vendor_sim601_torch210_lab_exact_v1'),old_bootstrap_venv_unchanged=True,reuse_verified_Torch_vision_wheels_and_owned_pip_cache_no_redownload=True,critical=dict(torch='2.10.0+cu128',torchvision='0.25.0+cu128',isaacsim='6.0.1.0',rsl_rl_lib='5.0.1',isaaclab='extracted exact72 source6.1.14',isaaclab_rl='extracted exact72 source0.5.5'),explicit_vendor_delta=dict(numpy='2.3.1',packaging='23.2',typing_extensions='4.12.2'),separate_build_environment='Original bootstrap or temporary isolated buildenv, every tmp/cache/home/log path under authorizedROOT; runtime does not inherit bootstrap wheel/packaging requirements',not_exact72_whole_package_environment=True,no_ignore_required_dependencies=True,actual_install_and_pipcheck_SDK_CUDA_source_restore_still_pending=True)
 put('STAGE6_VENDOR_REQUIREMENTS_METADATA_ACTUAL.json',dict(passed=True,epoch=time.time(),official_index=primary,cached_kernel=found,exact_sdk_source=source,official_small_metadata=public,old_bootstrap_wheel_metadata=bootstrap,typed_next_install_plan=plan,no_GPU_Torch_SDK_model_install_process_account_or_GO=True))
 progress('VENDOR_REQUIREMENTS_METADATA_ONLY_PASSED',numpy_requirement=numpy,actual_install_not_executed=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('STAGE6_ORIGINAL_METADATA_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_originals_preserved=True,no_install_or_GPU=True));raise

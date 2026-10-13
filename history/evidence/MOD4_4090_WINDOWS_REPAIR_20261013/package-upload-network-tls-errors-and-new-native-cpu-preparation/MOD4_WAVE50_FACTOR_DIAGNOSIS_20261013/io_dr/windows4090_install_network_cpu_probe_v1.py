"""Bounded package endpoint tests. TLS checked; proxy credential values never saved."""
from pathlib import Path
import os,time,json,urllib.parse,urllib.request,re
import requests
R=Path(__file__).resolve().parent
def proxy_desc(value):
 try:
  p=urllib.parse.urlsplit(value if '://' in value else 'http://'+value)
  return dict(scheme=p.scheme,hostname=p.hostname,port=p.port,credentials_present=p.username is not None or p.password is not None)
 except Exception:return dict(parse_failed=True,value_not_saved=True)
raw_proxies=urllib.request.getproxies()
report=dict(epoch=time.time(),proxy_descriptors={k:proxy_desc(v) for k,v in raw_proxies.items()},tests=[],no_OS_condarc_or_installedenv_write=True,no_Isaac_Torch_CUDA_GPU_or_PPO=True,TLS_verify_true=True)
try:
 from conda.base.context import context
 report['conda_proxy_descriptors']={k:proxy_desc(v) for k,v in context.proxy_servers.items()}
except Exception as e:report['conda_context_error_type']=type(e).__name__
out=R/'install_reports'/('PACKAGE_NETWORK_CPU_ACTUAL_'+str(time.time_ns())+'.json')
urls=['https://repo.anaconda.com/pkgs/main/win-64/repodata.json','https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/win-64/repodata.json','https://pypi.org/simple/pip/','https://pypi.nvidia.com/isaacsim/','https://download.pytorch.org/whl/cu128/torch/']
for url in urls:
 for trust in (True,False):
  started=time.time()
  try:
   with requests.Session() as s:
    s.trust_env=trust
    r=s.head(url,allow_redirects=True,timeout=4,verify=True)
    row=dict(url=url,trust_existing_proxy_environment=trust,status=r.status_code,seconds=time.time()-started,response_host=urllib.parse.urlsplit(r.url).hostname)
  except Exception as e:
   text=str(e)
   for v in raw_proxies.values():text=text.replace(v,'[proxyvalue-redacted]')
   text=re.sub(r'(?<=//)[^/@\s]+:[^/@\s]+@','[credential-redacted]@',text)
   row=dict(url=url,trust_existing_proxy_environment=trust,error_type=type(e).__name__,error=text,seconds=time.time()-started)
  report['tests'].append(row);out.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(out),actual=report),ensure_ascii=True))

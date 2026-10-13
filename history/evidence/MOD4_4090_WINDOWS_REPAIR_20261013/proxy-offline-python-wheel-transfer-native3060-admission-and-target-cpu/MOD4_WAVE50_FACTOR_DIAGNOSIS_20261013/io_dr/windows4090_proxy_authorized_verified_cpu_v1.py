"""One bounded verified endpoint probe. Explicit process-only authorized proxy."""
from pathlib import Path
import json,time,os,urllib.request,urllib.parse,ssl
R=Path(__file__).resolve().parent
out=R/'install_reports'/'AUTHORIZED_PROXY_VERIFIED_ENDPOINTS_CPU_ACTUAL.json'
if out.exists():raise RuntimeError('immutable actual exists; no repeat endpoint attempt')
os.environ['HTTP_PROXY']=os.environ['HTTPS_PROXY']='http://127.0.0.1:7897'
ctx=ssl.create_default_context()
assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
opener=urllib.request.build_opener(urllib.request.ProxyHandler({'http':'http://127.0.0.1:7897','https':'http://127.0.0.1:7897'}),urllib.request.HTTPSHandler(context=ctx))
report=dict(epoch=time.time(),pid=os.getpid(),python=os.sys.executable,process_only_authorized_proxy='127.0.0.1:7897',TLS_verified=True,no_system_DNS_condarc_or_security_change=True,no_GPU_Kit_or_PPO=True,tests=[])
urls=['https://repo.anaconda.com/pkgs/main/win-64/repodata.json','https://pypi.org/simple/pip/','https://download.pytorch.org/whl/cu128/torch/','https://pypi.nvidia.com/isaacsim/']
for url in urls:
 t=time.time()
 try:
  req=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'MOD4-authorized-environment-admission'})
  with opener.open(req,timeout=12) as r:row=dict(url=url,status=r.status,response_host=urllib.parse.urlsplit(r.url).hostname,seconds=time.time()-t,verified=True)
 except Exception as e:row=dict(url=url,error_type=type(e).__name__,error=str(e),seconds=time.time()-t,verified=False)
 report['tests'].append(row)
 out.write_text(json.dumps(report,indent=2),encoding='utf8')
report['all_endpoints_verified_success']=all(x.get('status')==200 and x['verified'] for x in report['tests'])
out.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=True))

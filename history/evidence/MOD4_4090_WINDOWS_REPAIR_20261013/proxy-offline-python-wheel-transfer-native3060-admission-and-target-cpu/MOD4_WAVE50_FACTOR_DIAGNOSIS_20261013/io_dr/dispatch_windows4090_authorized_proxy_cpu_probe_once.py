from pathlib import Path
import sys,time,json,hashlib,traceback
W=Path(__file__).resolve().parents[2];F=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
p=F/'windows4090_proxy_authorized_verified_cpu_v1.py';sha=hashlib.sha256(p.read_bytes()).hexdigest()
out=F/('WINDOWS4090_AUTHORIZED_PROXY_CPU_DISPATCH_ACTUAL_'+str(time.time_ns())+'.json')
report=dict(epoch=time.time(),source=str(p),sha256=sha,no_GPU_or_install=True,events=[])
try:
 s=connect()
 pre=powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$r='"+R+"';@{own_python=Test-Path -LiteralPath ($r+'/env/python.exe');actual_base_complete=Test-Path -LiteralPath ($r+'/install_reports/OFFLINE_PY311_BASE_ACTUAL_COMPLETE.json');new_source_present=Test-Path -LiteralPath ($r+'/windows4090_proxy_authorized_verified_cpu_v1.py');proof_present=Test-Path -LiteralPath ($r+'/install_reports/AUTHORIZED_PROXY_VERIFIED_ENDPOINTS_CPU_ACTUAL.json');freeC=(Get-PSDrive C).Free}|ConvertTo-Json",timeout=35)
 pre=json.loads(pre);report['pre']=pre;out.write_text(json.dumps(report,indent=2),encoding='utf8')
 assert pre['own_python'] and pre['actual_base_complete'] and not pre['new_source_present'] and not pre['proof_present']
 upload(p,R+'/'+p.name,timeout=60);report['events'].append('new_source_uploaded')
 code="$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$r='"+R+"';if((Get-FileHash -LiteralPath ($r+'/"+p.name+"') -Algorithm SHA256).Hash.ToLower() -ne '"+sha+"'){throw 'source SHA mismatch'};& ($r+'/env/python.exe') ($r+'/"+p.name+"');if($LASTEXITCODE-ne0){throw 'endpoint reader exit'}"
 result=powershell(s,code,timeout=65);report['actual']=json.loads(result);report['source_sha_actual_verified']=True;s.close()
 out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),actual=report['actual']),ensure_ascii=True))
except Exception as e:
 report['error_type']=type(e).__name__;report['error']=str(e);report['traceback']=traceback.format_exc();out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),error=report['error']),ensure_ascii=True));raise

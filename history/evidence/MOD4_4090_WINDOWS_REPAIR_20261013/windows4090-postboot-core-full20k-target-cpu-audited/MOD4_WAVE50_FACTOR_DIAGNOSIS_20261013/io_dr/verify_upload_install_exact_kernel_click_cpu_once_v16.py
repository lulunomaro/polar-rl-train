from pathlib import Path
import json,time,sys,ssl,urllib.request,hashlib,traceback
F=Path(__file__).resolve().parent;W=F.parents[1];sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';p=F/'OFFICIAL_CLICK_KERNEL_PIN_20261013/click-8.1.7-py3-none-any.whl';h=hashlib.sha256(p.read_bytes()).hexdigest()
out=F/('WINDOWS4090_KERNEL_EXACT_CLICK_CPU_REPAIR_ACTUAL_'+str(time.time_ns())+'.json');j=dict(epoch=time.time(),package=str(p),bytes=p.stat().st_size,sha256=h,no_GPU_Kit_PPO_or_SDKsource_change=True,FastAPI_upstream_contradiction_not_relabeled_pass=True)
try:
 with urllib.request.urlopen('https://pypi.org/pypi/click/8.1.7/json',context=ssl.create_default_context(),timeout=15) as q:official=json.load(q)
 u=next(x for x in official['urls'] if x['filename']==p.name);assert u['digests']['sha256']==h;j['publishedSHA_exact']=True;j['officialURL']=u['url'];out.write_text(json.dumps(j,indent=2),encoding='utf8')
 s=connect();remote=R+'/packages/'+p.name
 pre=powershell(s,"if(Test-Path -LiteralPath '"+remote+"'){'PRESENT'}else{'ABSENT'}",timeout=25);assert pre=='ABSENT','unknown outcome review needed; never replay once'
 upload(p,remote,timeout=60)
 code="if((Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()-ne'"+h+"'){throw 'click officialSHA'};$o='"+R+"/install_logs/06A_KERNEL_EXACT_CLICK_CPU_INSTALL.stdout.log';$e='"+R+"/install_logs/06A_KERNEL_EXACT_CLICK_CPU_INSTALL.stderr.log';if((Test-Path -LiteralPath $o)-or(Test-Path -LiteralPath $e)){throw 'immutable logs consumed'};$env:CUDA_VISIBLE_DEVICES='';$env:PYTHONNOUSERSITE='1';& '"+R+"/env/python.exe' -m pip install --no-deps --no-index '"+remote+"' 1>$o 2>$e;$c=$LASTEXITCODE;$v=@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;exit_code=$c;passed=$c-eq0;stdout=$o;stderr=$e;no_GPU_Kit_PPO_SDKsource_change=$true};[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($v|ConvertTo-Json)))"
 import base64
 j['actual']=json.loads(base64.b64decode(powershell(s,code,timeout=45)).decode('utf8'));s.close();out.write_text(json.dumps(j,indent=2),encoding='utf8');assert j['actual']['passed'];print(json.dumps(dict(report=str(out),actual=j['actual']),ensure_ascii=True))
except Exception as e:j.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());out.write_text(json.dumps(j,indent=2),encoding='utf8');raise

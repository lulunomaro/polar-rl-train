from pathlib import Path
import json,time,sys,base64,hashlib,traceback
F=Path(__file__).resolve().parent;W=F.parents[1]
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
p=F/'windows4090_kernel_http_consumer_cpu_audit_v17.py';remote=R+'/install_helpers/'+p.name
h=hashlib.sha256(p.read_bytes()).hexdigest();out=F/('WINDOWS4090_KERNEL_HTTP_CONSUMER_CPU_COLLECTION_'+str(time.time_ns())+'.json')
j={'source':str(p),'source_sha256':h,'remote_source':remote,'no_GPU_or_SDK_mutation':True}
try:
 s=connect()
 pre=powershell(s,"$d='"+R+"/install_helpers';if(!(Test-Path -LiteralPath $d)){New-Item -ItemType Directory -Path $d|Out-Null};if(Test-Path -LiteralPath '"+remote+"'){(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()}else{'ABSENT'}",timeout=25)
 if pre=='ABSENT':upload(p,remote,timeout=60)
 else:assert pre==h,'unknown-source outcome requires review'
 code="$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$env:CUDA_VISIBLE_DEVICES='';$env:PYTHONNOUSERSITE='1';if((Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()-ne'"+h+"'){throw 'CPU observer SHA'};$a=& '"+R+"/env/python.exe' '"+remote+"';$c=$LASTEXITCODE;if($c-ne0){throw ($a|Out-String)};$v=$a|ConvertFrom-Json;$b=[IO.File]::ReadAllBytes($v.report);[Convert]::ToBase64String($b)"
 actual=json.loads(base64.b64decode(powershell(s,code,timeout=180)).decode('utf8'));s.close();j['actual']=actual;out.write_text(json.dumps(j,indent=2),encoding='utf8')
 print(json.dumps({'report':str(out),'versions':actual['versions'],'source_consumers':actual['source_consumers'],'pipcheck':actual['post_click_pipcheck_actual'],'headless_sources':[{'path':q['path'],'sha256':q['sha256']} for q in actual['headless_entry_sources']],'apps_actual_exists':actual['apps_actual_exists']},ensure_ascii=True))
except BaseException as e:
 j.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());out.write_text(json.dumps(j,indent=2),encoding='utf8');raise

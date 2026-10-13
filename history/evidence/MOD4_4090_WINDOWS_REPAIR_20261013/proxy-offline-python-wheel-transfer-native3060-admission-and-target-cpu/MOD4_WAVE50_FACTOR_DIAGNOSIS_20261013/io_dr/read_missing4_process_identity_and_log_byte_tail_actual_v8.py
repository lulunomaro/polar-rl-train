from pathlib import Path
import time,json,sys,traceback
F=Path(__file__).resolve().parent;W=F.parents[1];sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
out=F/('WINDOWS4090_MISSING4_PROCESS_LOG_BYTE_TAIL_ACTUAL_'+str(time.time_ns())+'.json');j=dict(epoch=time.time(),no_task_RPC_no_GetContent_live_log=True,no_mutation=True)
try:
 s=connect();r='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';code="$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$x=@();foreach($z in @(14048,18416)){$p=Get-Process -Id $z -ErrorAction SilentlyContinue;if($p){$x+=@{pid=$p.Id;name=$p.Name;start=$p.StartTime.ToUniversalTime().ToString('o');CPU=$p.CPU}}};$ls=@();foreach($q in @('stdout','stderr')){$p='"+r+"/install_logs/02A_VERIFIED_PROXY_MISSING4_NVIDIA_DOWNLOAD.'+$q+'.log';$f=[IO.File]::Open($p,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::ReadWrite);$len=$f.Length;$n=[Math]::Min($len,4096);$f.Seek(-$n,[IO.SeekOrigin]::End)|Out-Null;$b=New-Object byte[] $n;$got=$f.Read($b,0,$n);$f.Dispose();$ls+=@{path=$p;bytes=$len;actual_tail=[Convert]::ToBase64String($b)}};@{processes=$x;logs=$ls}|ConvertTo-Json -Depth 8"
 j['actual']=json.loads(powershell(s,code,timeout=25));s.close();out.write_text(json.dumps(j,indent=2),encoding='utf8');import base64
 brief=dict(processes=j['actual']['processes'],logs=[dict(path=x['path'],bytes=x['bytes'],tail=base64.b64decode(x['actual_tail']).decode('utf8','replace')) for x in j['actual']['logs']]);print(json.dumps(dict(report=str(out),actual=brief),ensure_ascii=True))
except Exception as e:j.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());out.write_text(json.dumps(j,indent=2),encoding='utf8');raise

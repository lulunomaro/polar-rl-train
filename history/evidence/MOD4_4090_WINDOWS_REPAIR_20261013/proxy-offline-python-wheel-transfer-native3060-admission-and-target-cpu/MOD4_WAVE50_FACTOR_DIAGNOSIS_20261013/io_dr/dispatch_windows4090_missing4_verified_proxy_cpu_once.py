from pathlib import Path
import time,json,sys,hashlib,traceback
W=Path(__file__).resolve().parents[2];F=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';name='MOD4_Windows4090_VerifiedProxy_NvidiaMissing4_CPU_20261013'
p=F/'windows4090_missing_nvidia_verified_proxy_download_cpu_v4.ps1';h=hashlib.sha256(p.read_bytes()).hexdigest()
out=F/('WINDOWS4090_MISSING4_VERIFIED_PROXY_CPU_DISPATCH_ACTUAL_'+str(time.time_ns())+'.json');j=dict(epoch=time.time(),source=str(p),source_sha256=h,task=name,no_GPU_or_PPO=True)
try:
 s=connect();code="$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$r='"+R+"';@{source_present=Test-Path -LiteralPath ($r+'/"+p.name+"');task_present=[bool](Get-ScheduledTask -TaskName '"+name+"' -ErrorAction SilentlyContinue);started_present=Test-Path -LiteralPath ($r+'/install_reports/NVIDIA_MISSING4_SUPERVISOR_STARTED.json')}|ConvertTo-Json"
 j['pre']=json.loads(powershell(s,code,timeout=30));out.write_text(json.dumps(j,indent=2),encoding='utf8');assert not any(j['pre'].values())
 upload(p,R+'/'+p.name,timeout=60)
 code="$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$r='"+R+"';if((Get-FileHash -LiteralPath ($r+'/"+p.name+"') -Algorithm SHA256).Hash.ToLower()-ne'"+h+"'){throw 'sourceSHA'};$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File C:\\Users\\Win10\\Documents\\MOD4_WAVE50_WINDOWS_4090_20261013\\"+p.name+"';$u=New-ScheduledTaskPrincipal -UserId 'Win10' -LogonType S4U -RunLevel Highest;$st=New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 2);Register-ScheduledTask -TaskName '"+name+"' -Action $a -Principal $u -Settings $st|Out-Null;Start-ScheduledTask -TaskName '"+name+"';Start-Sleep -Seconds 2;$t=Get-ScheduledTask -TaskName '"+name+"';@{task=$t.TaskName;state=[string]$t.State;triggers=@($t.Triggers).Count;started=if(Test-Path -LiteralPath ($r+'/install_reports/NVIDIA_MISSING4_SUPERVISOR_STARTED.json')){Get-Content -LiteralPath ($r+'/install_reports/NVIDIA_MISSING4_SUPERVISOR_STARTED.json') -Raw|ConvertFrom-Json}else{$null};stage=if(Test-Path -LiteralPath ($r+'/install_reports/02A_VERIFIED_PROXY_MISSING4_NVIDIA_DOWNLOAD_STARTED.json')){Get-Content -LiteralPath ($r+'/install_reports/02A_VERIFIED_PROXY_MISSING4_NVIDIA_DOWNLOAD_STARTED.json') -Raw|ConvertFrom-Json}else{$null}}|ConvertTo-Json -Depth 12"
 j['dispatch']=json.loads(powershell(s,code,timeout=35));s.close();out.write_text(json.dumps(j,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),actual=j['dispatch']),ensure_ascii=True))
except Exception as e:j.update(error=str(e),error_type=type(e).__name__,traceback=traceback.format_exc());out.write_text(json.dumps(j,indent=2),encoding='utf8');raise

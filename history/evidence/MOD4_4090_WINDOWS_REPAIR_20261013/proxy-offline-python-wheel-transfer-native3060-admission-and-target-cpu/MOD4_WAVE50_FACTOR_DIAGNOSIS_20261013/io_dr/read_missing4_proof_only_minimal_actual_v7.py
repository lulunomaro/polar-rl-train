from pathlib import Path
import time,json,sys,traceback
F=Path(__file__).resolve().parent;W=F.parents[1];sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
out=F/('WINDOWS4090_MISSING4_PROOF_ONLY_ACTUAL_'+str(time.time_ns())+'.json');j=dict(epoch=time.time(),no_task_RPC_no_live_log_Read=True,no_GPU_mutation=True)
try:
 s=connect();r='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';code="$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$p='"+r+"/install_reports/NVIDIA_MISSING4_DOWNLOAD_ACTUAL_COMPLETE.json';if(Test-Path -LiteralPath $p){Get-Content -LiteralPath $p -Raw}else{'MISSING_COMPLETION_PROOF'}"
 raw=powershell(s,code,timeout=25);s.close();j['actual']=json.loads(raw) if raw!='MISSING_COMPLETION_PROOF' else dict(complete_pending=True);out.write_text(json.dumps(j,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),actual=j['actual']),ensure_ascii=True))
except Exception as e:j.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());out.write_text(json.dumps(j,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),error_type=type(e).__name__),ensure_ascii=True));raise

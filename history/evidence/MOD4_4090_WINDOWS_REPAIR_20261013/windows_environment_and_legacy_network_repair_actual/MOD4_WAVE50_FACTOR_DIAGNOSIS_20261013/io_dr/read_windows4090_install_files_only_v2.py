"""One tiny readonly filesystem snapshot; no CIM/WMI/task action/retry loop."""
from pathlib import Path
import sys,json,time,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf');F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
code=r"""$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';$d=Join-Path $r 'install_reports';$f=@(Get-ChildItem -LiteralPath $d -File|Select-Object Name,Length,LastWriteTimeUtc);$s=Join-Path $d 'INSTALL_SUPERVISOR_STARTED.json';$started=if(Test-Path -LiteralPath $s){[IO.File]::ReadAllText($s)|ConvertFrom-Json}else{$null};$e=@(Get-ChildItem -LiteralPath $d -File|Where-Object{$_.Name-like'*FAIL*'-or$_.Name-like'*ENDED*'}|Sort-Object LastWriteTimeUtc -Descending|Select-Object -First 2);$last=@();foreach($x in $e){$last+=@{name=$x.Name;content=([IO.File]::ReadAllText($x.FullName)|ConvertFrom-Json)}};$logs=@(Get-ChildItem -LiteralPath (Join-Path $r 'install_logs') -File|Select-Object Name,Length,LastWriteTimeUtc);@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();started=$started;reports=$f;last_receipts=$last;logs=$logs;Python_present=(Test-Path -LiteralPath (Join-Path $r 'env\python.exe'));no_mutation=$true}|ConvertTo-Json -Depth 8 -Compress"""
c=connect();p=F/('WINDOWS4090_INSTALL_FILES_ONLY_ACTUAL_'+str(time.time_ns())+'.json')
try:
 raw=powershell(c,code,45);r=json.loads(raw);r['read_only_no_CIM_or_WMI']=True;r['original_combined_reader_timeout_retained']=True;p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),actual=r),ensure_ascii=False))
except BaseException:p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_CIM_WMI_GPU_or_mutation=True,one_connection_no_retry=True),indent=2),encoding='utf8');raise
finally:c.close()

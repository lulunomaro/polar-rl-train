from pathlib import Path
import sys,json,time,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf');F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
code=r"""
$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';$files=@();foreach($f in @(Get-ChildItem -LiteralPath (Join-Path $r 'install_reports') -File -ErrorAction SilentlyContinue)){$txt=[IO.File]::ReadAllText($f.FullName);try{$v=$txt|ConvertFrom-Json}catch{$v=$null};$files+=@{path=$f.FullName;bytes=$f.Length;sha256=(Get-FileHash -LiteralPath $f.FullName).Hash.ToLower();content=$v}};$logs=@();foreach($f in @(Get-ChildItem -LiteralPath (Join-Path $r 'install_logs') -File -ErrorAction SilentlyContinue)){$logs+=@{path=$f.FullName;bytes=$f.Length;modified=$f.LastWriteTimeUtc;lastlines=@(Get-Content -LiteralPath $f.FullName -Tail 12 -ErrorAction SilentlyContinue)}};$procs=@(Get-CimInstance Win32_Process|Where-Object{$_.CommandLine-like('*'+$r+'*')}|Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine,ExecutablePath);@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();reports=$files;logs=$logs;own_processes=$procs;Python_present=(Test-Path -LiteralPath (Join-Path $r 'env\python.exe'));no_GPU_or_OS_or_environment_mutation=$true}|ConvertTo-Json -Depth 14 -Compress
"""
c=connect();attempts=[]
try:
 for i in range(6):
  try:
   raw=powershell(c,code,45);attempts.append(dict(attempt=i+1,passed=True));r=json.loads(raw)
   # This process inventory includes this transient readonly SSH command; it is
   # not itself an installer or a GPU child. Actual creation/argv remain raw.
   r['connection_attempts']=attempts;r['actual_stage_priority']=True
   p=F/('WINDOWS4090_INSTALL_CURRENT_ACTUAL_'+str(time.time_ns())+'.json');p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
   print(json.dumps(dict(report=str(p),Python_present=r['Python_present'],receipts=[dict(name=Path(x['path']).name,content=x['content']) for x in r['reports']],logs=r['logs'],processes=r['own_processes']),ensure_ascii=False));break
  except RuntimeError as e:
   attempts.append(dict(attempt=i+1,passed=False,error=str(e)))
   if not any(s in str(e) for s in ('kex_exchange','banner exchange','MaxStartups','Connection closed')) or i==5:raise
   time.sleep(5)
except BaseException:
 p=F/('WINDOWS4090_INSTALL_CURRENT_READER_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),attempts=attempts,no_mutation=True),indent=2),encoding='utf8');raise
finally:c.close()

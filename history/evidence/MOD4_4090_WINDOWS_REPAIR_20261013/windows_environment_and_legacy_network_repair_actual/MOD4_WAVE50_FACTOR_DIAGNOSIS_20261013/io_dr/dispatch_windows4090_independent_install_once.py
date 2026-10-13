from pathlib import Path
import sys,time,json,hashlib,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf')
F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
ROOT='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
stamp=str(time.time_ns());p=F/('WINDOWS4090_INSTALL_DISPATCH_ACTUAL_'+stamp+'.json');record=dict(epoch=time.time(),root=ROOT,source=[],phases=[],no_GPU_Kit_or_PPO=True,no_Linux_3060_or_budget_write=True)
c=None
def save():p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
def call(code,timeout=45):
 attempts=[]
 for i in range(6):
  try:
   raw=powershell(c,code,timeout);attempts.append(dict(attempt=i+1,passed=True,epoch=time.time()));record['phases'].append(dict(attempts=attempts));save();return json.loads(raw)
  except RuntimeError as e:
   attempts.append(dict(attempt=i+1,passed=False,error=str(e),epoch=time.time()));save()
   if not any(s in str(e) for s in ('kex_exchange','banner exchange','MaxStartups','Connection closed by 10.24.4.210 port 22')):raise
   if i==5:raise
   time.sleep(5)
try:
 c=connect()
 record['newroot_actual']=call(r"""
$ErrorActionPreference='Stop';$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';if(Test-Path -LiteralPath $r){throw 'New independent Windows4090 root already exists, immutable guard'};$v=Get-Volume -DriveLetter C;if($v.SizeRemaining-lt80GB){throw 'Durable install guard below80GiB'};if(!(Test-Path -LiteralPath 'D:\anaconda\Scripts\conda.exe')){throw 'conda executable missing'};New-Item -ItemType Directory -Path $r|Out-Null;foreach($d in @('install_logs','install_reports')){New-Item -ItemType Directory -Path (Join-Path $r $d)|Out-Null};$a=@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();root=$r;actual_root_previously_unused=$true;durable_free=$v.SizeRemaining;ownroot_created_once=$true;no_existingenv_SDK_GPU_or_budget_modification=$true};[IO.File]::WriteAllText((Join-Path $r 'install_reports\NEW_ROOT_CREATED_UNUSED_ACTUAL.json'),($a|ConvertTo-Json),[Text.UTF8Encoding]::new($false));$a|ConvertTo-Json -Compress
""")
 save()
 for filename in ('windows4090_install_cpu_supervisor_v1.ps1','tested_constraints_v1.txt','metadata_cpu_admission_v1.py'):
  f=F/filename;h=hashlib.sha256(f.read_bytes()).hexdigest()
  upload(str(f),ROOT+'/'+filename,timeout=90)
  record['source'].append(dict(path=str(f),remote=ROOT+'/'+filename,bytes=f.stat().st_size,sha256=h));save()
 record['dispatch_actual']=call(r"""
$ErrorActionPreference='Stop';$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';$receipt=Join-Path $r 'install_reports\INSTALL_DISPATCH_RECEIPT.json';if(Test-Path -LiteralPath $receipt){throw 'Install dispatcher already consumed'};if(Test-Path -LiteralPath (Join-Path $r 'env')){throw 'Newprefix already exists'};$sources=@();foreach($n in @('windows4090_install_cpu_supervisor_v1.ps1','tested_constraints_v1.txt','metadata_cpu_admission_v1.py')){$f=Join-Path $r $n;$sources+=@{path=$f;bytes=(Get-Item -LiteralPath $f).Length;sha256=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLower()}};$proc=Start-Process powershell.exe -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $r 'windows4090_install_cpu_supervisor_v1.ps1')) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $r 'install_logs\supervisor.stdout.log') -RedirectStandardError (Join-Path $r 'install_logs\supervisor.stderr.log');$cim=Get-CimInstance Win32_Process -Filter ('ProcessId='+$proc.Id);$a=@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();PID=$proc.Id;CIM=@{pid=$cim.ProcessId;creation=$cim.CreationDate;argv=$cim.CommandLine;executable=$cim.ExecutablePath};root=$r;sources=$sources;stage='conda_new_Python311';no_GPU_Kit_or_PPO=$true;originalenvs_unchanged=$true;no_budgetwrite=$true};[IO.File]::WriteAllText($receipt,($a|ConvertTo-Json -Depth 7),[Text.UTF8Encoding]::new($false));$a|ConvertTo-Json -Depth 7 -Compress
""")
 assert {x['sha256'] for x in record['source']}=={x['sha256'] for x in record['dispatch_actual']['sources']}
 record['actual_dispatch_source_bytes_SHA_exact']=True;save()
 print(json.dumps(dict(report=str(p),dispatch=record['dispatch_actual']),ensure_ascii=False))
except BaseException:
 record['original_error']=traceback.format_exc();record['phase_outcome_unknown_check_actual_receipts_before_any_retry']=True;save();raise
finally:
 if c is not None:c.close()

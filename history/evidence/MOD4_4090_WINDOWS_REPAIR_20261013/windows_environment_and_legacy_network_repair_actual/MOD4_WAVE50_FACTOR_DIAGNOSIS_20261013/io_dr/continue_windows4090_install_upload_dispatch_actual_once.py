"""Only previously unexecuted payload upload/dispatch after actual root creation."""
from pathlib import Path
import sys,json,time,hashlib,traceback,runpy
W=Path('C:/Users/lulu/Desktop/claude/mjcf');F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
ROOT='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
p=F/('WINDOWS4090_INSTALL_UPLOAD_DISPATCH_CONTINUATION_'+str(time.time_ns())+'.json');r=dict(epoch=time.time(),root=ROOT,source=[],upload_attempts=[],root_creation_not_repeated=True,no_GPU_Kit_PPO_or_budget_write=True)
def save():p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
c=connect()
def ps(code):
 for i in range(6):
  try:return json.loads(powershell(c,code,45))
  except RuntimeError as e:
   r.setdefault('SSH_read_attempt_errors',[]).append(dict(epoch=time.time(),attempt=i+1,error=str(e)));save()
   if not any(s in str(e) for s in ('kex_exchange','banner exchange','MaxStartups','Connection closed')) or i==5:raise
   time.sleep(5)
try:
 r['actual_before']=ps(r"""$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';if(!(Test-Path -LiteralPath (Join-Path $r 'install_reports\NEW_ROOT_CREATED_UNUSED_ACTUAL.json'))){throw 'Missing actual ownroot receipt'};if((Test-Path -LiteralPath (Join-Path $r 'env'))-or(Test-Path -LiteralPath (Join-Path $r 'install_reports\INSTALL_DISPATCH_RECEIPT.json'))){throw 'Install possibly consumed; no blindlaunch'};$rows=@();foreach($n in @('windows4090_install_cpu_supervisor_v1.ps1','tested_constraints_v1.txt','metadata_cpu_admission_v1.py')){$f=Join-Path $r $n;$rows+=@{name=$n;exists=(Test-Path -LiteralPath $f);sha256=$(if(Test-Path -LiteralPath $f){(Get-FileHash -LiteralPath $f).Hash.ToLower()}else{$null})}};@{root=$r;source=$rows;original_root_creation_preserved=$true}|ConvertTo-Json -Depth 5 -Compress""");save()
 for row in r['actual_before']['source']:
  f=F/row['name'];h=hashlib.sha256(f.read_bytes()).hexdigest()
  if row['sha256']!=h:
   for i in range(6):
    try:
     upload(str(f),ROOT+'/'+row['name'],timeout=90)
     r['upload_attempts'].append(dict(name=row['name'],attempt=i+1,passed=True,epoch=time.time()));save();break
    except RuntimeError as e:
     r['upload_attempts'].append(dict(name=row['name'],attempt=i+1,passed=False,error=str(e),epoch=time.time()));save()
     if not any(s in str(e) for s in ('Connection closed','kex_exchange','banner exchange','MaxStartups')) or i==5:raise
     time.sleep(5)
  r['source'].append(dict(path=str(f),remote=ROOT+'/'+row['name'],bytes=f.stat().st_size,sha256=h));save()
 r['dispatch']=ps(r"""$ErrorActionPreference='Stop';$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';$receipt=Join-Path $r 'install_reports\INSTALL_DISPATCH_RECEIPT.json';if((Test-Path -LiteralPath $receipt)-or(Test-Path -LiteralPath (Join-Path $r 'install_logs\supervisor.stdout.log'))){throw 'Install dispatcher or process output consumed; actualstate required'};if(Test-Path -LiteralPath (Join-Path $r 'env')){throw 'Prefix already consumed'};$ss=@();foreach($n in @('windows4090_install_cpu_supervisor_v1.ps1','tested_constraints_v1.txt','metadata_cpu_admission_v1.py')){$f=Join-Path $r $n;$ss+=@{path=$f;bytes=(Get-Item -LiteralPath $f).Length;sha256=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLower()}};$p=Start-Process powershell.exe -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $r 'windows4090_install_cpu_supervisor_v1.ps1')) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $r 'install_logs\supervisor.stdout.log') -RedirectStandardError (Join-Path $r 'install_logs\supervisor.stderr.log');$ci=Get-CimInstance Win32_Process -Filter ('ProcessId='+$p.Id);$a=@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();PID=$p.Id;CIM=@{pid=$ci.ProcessId;creation=$ci.CreationDate;argv=$ci.CommandLine;executable=$ci.ExecutablePath};sources=$ss;root=$r;no_GPU_Kit_PPO_or_budget_write=$true;stage='conda_new_Python311'};[IO.File]::WriteAllText($receipt,($a|ConvertTo-Json -Depth 7),[Text.UTF8Encoding]::new($false));$a|ConvertTo-Json -Depth 7 -Compress""")
 assert {x['sha256'] for x in r['source']}=={x['sha256'] for x in r['dispatch']['sources']}
 r['actual_source_bytes_SHA_exact']=True;save();print(json.dumps(dict(report=str(p),dispatch=r['dispatch']),ensure_ascii=False))
except BaseException:r['original_error']=traceback.format_exc();r['no_oldroot_or_dispatch_replay']=True;save();raise
finally:c.close()

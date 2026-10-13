"""Continue only unexecuted CPU installation after initial SSH child ended."""
from pathlib import Path
import sys,json,time,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf');F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
code=r"""
$ErrorActionPreference='Stop';$r='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';$n='MOD4_Windows4090_CPU_Environment_Install_20261013';if((Test-Path -LiteralPath (Join-Path $r 'env'))-or(Test-Path -LiteralPath (Join-Path $r 'install_reports\INSTALL_SUPERVISOR_STARTED.json'))){throw 'Original install stage already executed; independent actualstage required'};if(Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue){throw 'New demandtask already registered, unknown outcome must read actual'};$file=Join-Path $r 'windows4090_install_cpu_supervisor_v1.ps1';if((Get-FileHash -LiteralPath $file).Hash.ToLower()-ne'85df6a8e2c084686fbafca6c5e4b0014167d2374f093f8931cee2481a6c2f963'){throw 'Immutable source SHA mismatch'};$a=New-ScheduledTaskAction -Execute 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File '+$file);$pr=New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest;$s=New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit ([TimeSpan]::FromHours(6)) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $n -Action $a -Principal $pr -Settings $s|Out-Null;Start-ScheduledTask -TaskName $n;Start-Sleep -Seconds 2;$t=Get-ScheduledTask -TaskName $n;$info=Get-ScheduledTaskInfo -TaskName $n;$p=@(Get-CimInstance Win32_Process|Where-Object{$_.CommandLine-like('*'+$file+'*')}|Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine,ExecutablePath);$receipt=@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();task=$n;state=$t.State.ToString();last_run=$info.LastRunTime;last_result=$info.LastTaskResult;trigger_count=@($t.Triggers|Where-Object{$null-ne$_}).Count;action=$t.Actions;principal=$t.Principal;own_installer_processes=$p;original_StartProcess_dispatch_retained=$true;original_stage_was_unexecuted=$true;only_newroot_CPU_install=$true;no_GPU_Kit_PPO_or_budget_write=$true};[IO.File]::WriteAllText((Join-Path $r 'install_reports\DETACHED_DEMAND_TASK_DISPATCH_ACTUAL.json'),($receipt|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false));$receipt|ConvertTo-Json -Depth 10 -Compress
"""
p=F/('WINDOWS4090_DETACHED_INSTALL_TASK_DISPATCH_ACTUAL_'+str(time.time_ns())+'.json');r=dict(epoch=time.time(),powershell_source_CPU_parse_error_count=0,original_StartProcess_actualPID16560_now_absent_no_START_receipt_zero_logs=True,original_error_and_source_retained=True,attempts=[])
c=connect()
try:
 for i in range(6):
  try:
   raw=powershell(c,code,45);r['attempts'].append(dict(attempt=i+1,passed=True));r['actual']=json.loads(raw);p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),actual=r['actual']),ensure_ascii=False));break
  except RuntimeError as e:
   r['attempts'].append(dict(attempt=i+1,passed=False,error=str(e)));p.write_text(json.dumps(r,indent=2),encoding='utf8')
   if not any(s in str(e) for s in ('kex_exchange','banner exchange','MaxStartups','Connection closed')) or i==5:raise
   time.sleep(5)
except BaseException:r['error']=traceback.format_exc();r['do_not_repeat_TaskRegister_or_Start_without_actual_recheck']=True;p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');raise
finally:c.close()

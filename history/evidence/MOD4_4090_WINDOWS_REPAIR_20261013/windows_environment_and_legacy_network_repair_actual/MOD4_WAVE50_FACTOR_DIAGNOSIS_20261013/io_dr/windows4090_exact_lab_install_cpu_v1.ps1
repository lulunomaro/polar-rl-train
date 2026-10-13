$ErrorActionPreference='Stop'
$Root='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013'
$Python=Join-Path $Root 'env\python.exe'
$Reports=Join-Path $Root 'install_reports'
$Logs=Join-Path $Root 'install_logs'
$env:CUDA_VISIBLE_DEVICES='';$env:PYTHONNOUSERSITE='1'
$Utf8=[System.Text.UTF8Encoding]::new($false)
function Write-LabReceipt([string]$Name,$Object){$p=Join-Path $Reports ($Name+'.json');if(Test-Path -LiteralPath $p){throw ('Immutable lab receipt exists '+$p)};[IO.File]::WriteAllText($p,($Object|ConvertTo-Json -Depth 10),$Utf8)}
function Lab-Stage([string]$Name,[string[]]$Arguments){
 $start=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000
 Write-LabReceipt ($Name+'_STARTED') @{epoch=$start;PID=$PID;argv=$Arguments;no_GPU_Kit_PPO=$true;no_budgetwrite=$true}
 $stdout=Join-Path $Logs ($Name+'.stdout.log');$stderr=Join-Path $Logs ($Name+'.stderr.log')
 if((Test-Path -LiteralPath $stdout)-or(Test-Path -LiteralPath $stderr)){throw 'Immutable lab stage logs exist'}
 $p=Start-Process -FilePath $Python -ArgumentList $Arguments -PassThru -Wait -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
 Write-LabReceipt ($Name+'_ENDED') @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;started=$start;exit_code=$p.ExitCode;PID=$p.Id;passed=$p.ExitCode-eq0;stdout=$stdout;stderr=$stderr;no_GPU_Kit_PPO=$true}
 if($p.ExitCode-ne0){throw ('Lab stage '+$Name+' rejected '+$p.ExitCode)}
}
try{
 if(!(Test-Path -LiteralPath (Join-Path $Reports 'INSTALL_BASE_ENV_COMPLETE_LAB_PENDING.json'))){throw 'Ownbaseenv actualmetadata completion required'}
 if((Test-Path -LiteralPath (Join-Path $Reports 'EXACT_LAB_SUPERVISOR_STARTED.json'))-or(!(Test-Path -LiteralPath $Python))){throw 'Lab stage already consumed or ownPython missing'}
 Write-LabReceipt 'EXACT_LAB_SUPERVISOR_STARTED' @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();PID=$PID;ownroot=$Root;newenv_only=$true;oldenvs_notmodified=$true;no_GPU_Kit_PPO=$true}
 Lab-Stage '07_EXACT_THREE_PACKAGES_CPU_EXTRACT' @((Join-Path $Root 'extract_three_exact_packages_cpu_v1.py'))
 Lab-Stage '08_TESTED_LAB_REQUIRED_DEPENDENCIES' @('-m','pip','install','--constraint',(Join-Path $Root 'tested_constraints_v1.txt'),'--requirement',(Join-Path $Root 'tested_lab_dependencies_v1.txt'))
 foreach($n in @('isaaclab','isaaclab_rl','isaaclab_assets','isaaclab_tasks')){Lab-Stage ('09_EDITABLE_'+$n) @('-m','pip','install','--no-deps','--no-build-isolation','--editable',(Join-Path $Root ('sdk_exact\source\'+$n)))}
 Lab-Stage '10_FULL_ENV_METADATA_CPU_ADMISSION' @((Join-Path $Root 'metadata_full_environment_cpu_admission_v1.py'))
 Lab-Stage '11_PIP_REQUIREMENTS_CONSISTENCY_CPU' @('-m','pip','check')
 Write-LabReceipt 'EXACT_LAB_INSTALL_CPU_COMPLETE' @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();PID=$PID;full_environment_CPU_metadata_admitted=$true;actual_GPU_backend_probe_pending=$true;no_GPU_Kit_PPO=$true;no_oldenvs_or_budget_modified=$true}
 exit 0
}catch{Write-LabReceipt ('EXACT_LAB_ORIGINAL_FAILURE_'+[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()) @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();PID=$PID;original_error=$_.Exception.Message;detail=($_|Out-String);source_errors_logs_retained=$true;no_GPU_Kit_PPO_or_budgetwrite=$true};exit 1}

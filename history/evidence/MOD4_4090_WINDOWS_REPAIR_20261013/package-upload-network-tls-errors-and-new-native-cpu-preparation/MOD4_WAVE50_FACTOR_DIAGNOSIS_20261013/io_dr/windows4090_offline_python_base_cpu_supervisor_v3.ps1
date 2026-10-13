$ErrorActionPreference='Stop'
$Root='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013'
$Reports=Join-Path $Root 'install_reports';$Logs=Join-Path $Root 'install_logs';$Prefix=Join-Path $Root 'env'
$Utf8=[Text.UTF8Encoding]::new($false);$env:CUDA_VISIBLE_DEVICES='';$env:CONDA_OFFLINE='true';$env:PYTHONNOUSERSITE='1'
function Write-Off([string]$Name,$Value){$p=Join-Path $Reports ($Name+'.json');if(Test-Path -LiteralPath $p){throw 'immutable offline receipt exists'};[IO.File]::WriteAllText($p,($Value|ConvertTo-Json -Depth 10),$Utf8)}
function Off-Stage([string]$Name,[string]$Exe,[string[]]$Arguments){$start=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;Write-Off ($Name+'_STARTED') @{epoch=$start;pid=$PID;executable=$Exe;argv=$Arguments;no_GPU_Kit_PPO_or_budgetwrite=$true};$o=Join-Path $Logs ($Name+'.stdout.log');$e=Join-Path $Logs ($Name+'.stderr.log');if((Test-Path -LiteralPath $o)-or(Test-Path -LiteralPath $e)){throw 'immutable offline logs exists'};$p=Start-Process -FilePath $Exe -ArgumentList $Arguments -PassThru -Wait -WindowStyle Hidden -RedirectStandardOutput $o -RedirectStandardError $e;Write-Off ($Name+'_ENDED') @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;started=$start;pid=$p.Id;exit=$p.ExitCode;passed=$p.ExitCode-eq0;stdout=$o;stderr=$e;no_GPU_PPO_or_canonical_write=$true};if($p.ExitCode-ne0){throw ($Name+' failed '+$p.ExitCode)}}
try{
 if(Test-Path -LiteralPath $Prefix){throw 'newprefix already exists, actualstage required'}
 if(!(Test-Path -LiteralPath (Join-Path $Reports '01B_NEW_PYTHON311_CONDA_OFFICIAL_HTTPS_ENDED.json'))){throw 'Previous failedHTTPS actualexit required'}
 Write-Off 'OFFLINE_BASE_SUPERVISOR_STARTED' @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();pid=$PID;only_exact20_base_archives_from_actual_testedPython311=$true;old_source_reports_raw_preserved=$true;no_globalcondarc_or_systemDNS_TLSchange=$true;no_whole_large_env_copy=$true;no_GPU_PPO=$true}
 Off-Stage '01C_CPU_BASE_ARCHIVES_EXTRACT' 'D:\anaconda\python.exe' @((Join-Path $Root 'windows4090_extract_minimal_conda_base_offline.py'))
 Off-Stage '01D_CONDA_BASE_OFFLINE_CREATE' 'D:\anaconda\Scripts\conda.exe' @('create','--prefix',$Prefix,'--yes','--offline','--no-default-packages','--file',(Join-Path $Root 'OFFLINE_PY311_BASE_EXPLICIT.txt'))
 Off-Stage '01E_OWN_PYTHON_BASE_CPU_VERSION' (Join-Path $Prefix 'python.exe') @('--version')
 Off-Stage '01F_OWN_PIP_BASE_CPU_VERSION' (Join-Path $Prefix 'python.exe') @('-m','pip','--version')
 Write-Off 'OFFLINE_PY311_BASE_ACTUAL_COMPLETE' @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();pid=$PID;Python=(Join-Path $Prefix 'python.exe');version_expected='3.11.15';base_packages20_actual=$true;full_Torch_Isaac_Lab_CPUadmission_pending=$true;no_GPU_Kit_PPO_or_budgetwrite=$true}
 exit 0
}catch{Write-Off ('OFFLINE_BASE_ORIGINAL_FAILURE_'+[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()) @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();pid=$PID;error=$_.Exception.Message;detail=($_|Out-String);source_raw_cost_retained=$true;no_GPU_PPO_budgetwrite=$true};exit 1}

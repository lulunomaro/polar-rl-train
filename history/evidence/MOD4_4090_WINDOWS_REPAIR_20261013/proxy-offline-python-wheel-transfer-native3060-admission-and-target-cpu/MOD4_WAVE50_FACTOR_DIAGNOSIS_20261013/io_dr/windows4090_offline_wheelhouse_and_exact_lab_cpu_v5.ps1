$ErrorActionPreference='Stop'
$Root='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013';$Python=Join-Path $Root 'env\python.exe';$Reports=Join-Path $Root 'install_reports';$Logs=Join-Path $Root 'install_logs';$Utf8=[Text.UTF8Encoding]::new($false)
$env:CUDA_VISIBLE_DEVICES='';$env:PYTHONNOUSERSITE='1';$env:HTTP_PROXY='http://127.0.0.1:7897';$env:HTTPS_PROXY='http://127.0.0.1:7897'
function Rec([string]$Name,$v){$p=Join-Path $Reports ($Name+'.json');if(Test-Path -LiteralPath $p){throw 'immutable CPU receipt exists'};[IO.File]::WriteAllText($p,($v|ConvertTo-Json -Depth 12),$Utf8)}
function Stage([string]$Name,[string[]]$Arguments){$start=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;$o=Join-Path $Logs ($Name+'.stdout.log');$e=Join-Path $Logs ($Name+'.stderr.log');if((Test-Path -LiteralPath $o)-or(Test-Path -LiteralPath $e)){throw 'immutable CPU logs exist'};$p=Start-Process -FilePath $Python -ArgumentList $Arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $o -RedirectStandardError $e;Rec ($Name+'_STARTED') @{epoch=$start;pid=$p.Id;parent=$PID;argv=$Arguments;no_GPU_Kit_PPO=$true};$p.WaitForExit();$p.Refresh();Rec ($Name+'_ENDED') @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;start=$start;pid=$p.Id;exit=$p.ExitCode;passed=$p.ExitCode-eq0;stdout=$o;stderr=$e;no_GPU_PPO=$true};if($p.ExitCode-ne0){throw ($Name+' failed '+$p.ExitCode)}}
try{
 if(!(Test-Path -LiteralPath (Join-Path $Reports 'OFFLINE_PY311_BASE_ACTUAL_COMPLETE.json'))){throw 'actual own offline base required'}
 if(!(Test-Path -LiteralPath (Join-Path $Reports 'NVIDIA_MISSING4_DOWNLOAD_ACTUAL_COMPLETE.json'))){throw 'actual missing4 verified download required'}
 Rec 'OFFLINE_WHEELHOUSE_EXACT_LAB_CPU_SUPERVISOR_STARTED' @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();pid=$PID;all_old_envs_SDK_untouched=$true;no_GPU_Kit_PPO_budgetwrite=$true;newroot_only=$true}
 Stage '03A_NATIVE311_WHEELHOUSE_CPU_EXTRACT_VALIDATE' @((Join-Path $Root 'extract_native_wheelhouse_and_validate_missing4_cpu_v5.py'))
 Stage '03B_EXACT_PINNED_NATIVE311_WHEELHOUSE_INSTALL' @('-m','pip','install','--no-deps','--no-index','--require-hashes','--find-links',(Join-Path $Root 'native311_wheelhouse'),'--requirement',(Join-Path $Root 'ACTUAL_NATIVE311_FULL_WHEELHOUSE_PINS.txt'))
 Stage '03C_EXACT_THREE_PACKAGES_CPU_EXTRACT' @((Join-Path $Root 'extract_three_exact_packages_cpu_v1.py'))
 foreach($n in @('isaaclab','isaaclab_rl','isaaclab_assets','isaaclab_tasks')){Stage ('03D_EDITABLE_'+$n) @('-m','pip','install','--no-deps','--no-build-isolation','--editable',(Join-Path $Root ('sdk_exact\source\'+$n)))}
 Stage '03E_FULL_ENV_METADATA_CPU_ADMISSION' @((Join-Path $Root 'metadata_full_environment_cpu_admission_v1.py'))
 Stage '03F_NATIVE_LIBRARIES_CPU_ADMISSION' @((Join-Path $Root 'windows4090_native_libraries_cpu_admission_v5.py'))
 Stage '03G_PIP_REQUIREMENTS_CONSISTENCY_CPU' @('-m','pip','check')
 Rec 'WINDOWS4090_FULL_ENVIRONMENT_CPU_ACTUAL_COMPLETE' @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();pid=$PID;full_environment_CPU_metadata_native_libraries_pipcheck_admitted=$true;actual_GPU_backend_source_fullrestore_probe_pending=$true;no_GPU_Kit_PPO=$true;no_oldenvs_or_canonicalbudget_modified=$true}
 exit 0
}catch{Rec ('OFFLINE_WHEELHOUSE_EXACT_LAB_CPU_ORIGINAL_FAILURE_'+[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()) @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();pid=$PID;error=$_.Exception.Message;detail=($_|Out-String);old_false_original_source_partial_reports_retained=$true;no_GPU_PPO_budgetwrite=$true};exit 1}

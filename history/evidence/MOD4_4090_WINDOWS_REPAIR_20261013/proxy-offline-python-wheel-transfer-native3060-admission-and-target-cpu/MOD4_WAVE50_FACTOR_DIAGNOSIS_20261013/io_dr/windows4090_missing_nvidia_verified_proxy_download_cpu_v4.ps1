$ErrorActionPreference='Stop'
$Root='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013'
$Reports=Join-Path $Root 'install_reports';$Logs=Join-Path $Root 'install_logs';$Prefix=Join-Path $Root 'env';$Dest=Join-Path $Root 'official_missing_nvidia_wheels_v4'
$Utf8=[Text.UTF8Encoding]::new($false)
$env:HTTP_PROXY='http://127.0.0.1:7897';$env:HTTPS_PROXY='http://127.0.0.1:7897';$env:CUDA_VISIBLE_DEVICES='';$env:PYTHONNOUSERSITE='1'
function Rec([string]$Name,$v){$p=Join-Path $Reports ($Name+'.json');if(Test-Path -LiteralPath $p){throw 'immutable receipt exists'};[IO.File]::WriteAllText($p,($v|ConvertTo-Json -Depth 12),$Utf8)}
try{
 if(!(Test-Path -LiteralPath ($Prefix+'/python.exe'))){throw 'own Python311 absent'}
 $proof=Get-Content -LiteralPath (Join-Path $Reports 'AUTHORIZED_PROXY_VERIFIED_ENDPOINTS_CPU_ACTUAL.json') -Raw|ConvertFrom-Json
 if(!$proof.all_endpoints_verified_success){throw 'verified proxy endpoint proof required'}
 if(Test-Path -LiteralPath $Dest){throw 'new download directory already exists'}
 $free=(Get-PSDrive C).Free;if($free-lt30GB){throw 'durable guard 30GiB failed'}
 New-Item -ItemType Directory -Path $Dest|Out-Null
 $start=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000
 Rec 'NVIDIA_MISSING4_SUPERVISOR_STARTED' @{epoch=$start;pid=$PID;mode='CPU wheel download only';process_proxy='127.0.0.1:7897';TLS_verify=$true;no_GPU_Kit_PPO_budget=$true;actual_durable_free=$free;guard_bytes=30GB}
 $args=@('-m','pip','download','--no-cache-dir','--no-deps','--only-binary=:all:','--retries','1','--timeout','30','--index-url','https://pypi.nvidia.com','--dest',$Dest,'isaacsim-kernel==5.1.0.0','isaacsim-extscache-kit==5.1.0.0','isaacsim-asset==5.1.0.0','isaacsim-robot-motion==5.1.0.0')
 $o=Join-Path $Logs '02A_VERIFIED_PROXY_MISSING4_NVIDIA_DOWNLOAD.stdout.log';$e=Join-Path $Logs '02A_VERIFIED_PROXY_MISSING4_NVIDIA_DOWNLOAD.stderr.log'
 if((Test-Path -LiteralPath $o)-or(Test-Path -LiteralPath $e)){throw 'immutable stage logs exist'}
 $p=Start-Process -FilePath ($Prefix+'/python.exe') -ArgumentList $args -PassThru -WindowStyle Hidden -RedirectStandardOutput $o -RedirectStandardError $e
 Rec '02A_VERIFIED_PROXY_MISSING4_NVIDIA_DOWNLOAD_STARTED' @{epoch=$start;pid=$p.Id;parent=$PID;executable=($Prefix+'/python.exe');argv=$args;no_GPU_PPO=$true}
 $p.WaitForExit();$p.Refresh()
 $files=@(Get-ChildItem -LiteralPath $Dest -File|ForEach-Object{@{path=$_.FullName;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()}})
 Rec '02A_VERIFIED_PROXY_MISSING4_NVIDIA_DOWNLOAD_ENDED' @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;start=$start;pid=$p.Id;exit=$p.ExitCode;passed=$p.ExitCode-eq0;files=$files;stdout=$o;stderr=$e;TLS_verified=$true;no_GPU_Kit_PPO=$true}
 if($p.ExitCode-ne0){throw 'missing4 verified download failed'}
 if($files.Count-ne4){throw 'actual four pinned Nvidia wheels required'}
 Rec 'NVIDIA_MISSING4_DOWNLOAD_ACTUAL_COMPLETE' @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();pid=$PID;files=$files;only_download_not_SDK_admission=$true;no_GPU_PPO=$true}
 exit 0
}catch{Rec ('NVIDIA_MISSING4_ORIGINAL_FAILURE_'+[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()) @{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();pid=$PID;error=$_.Exception.Message;detail=($_|Out-String);original_partial_downloads_retained=$true;no_GPU_PPO=$true};exit 1}

$ErrorActionPreference='Stop'
$Root='C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013'
$Prefix=Join-Path $Root 'env'
$Logs=Join-Path $Root 'install_logs'
$Reports=Join-Path $Root 'install_reports'
$env:CUDA_VISIBLE_DEVICES=''
$env:PYTHONNOUSERSITE='1'
$env:PIP_DISABLE_PIP_VERSION_CHECK='1'
$Utf8=[System.Text.UTF8Encoding]::new($false)
$Start=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000
function Write-Receipt([string]$Name,$Object){
 $Path=Join-Path $Reports ($Name+'.json')
 if(Test-Path -LiteralPath $Path){throw ('Immutable receipt already exists: '+$Path)}
 [IO.File]::WriteAllText($Path,($Object|ConvertTo-Json -Depth 12),$Utf8)
}
function Stage([string]$Name,[string]$Exe,[string[]]$Arguments){
 $Started=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000
 Write-Receipt ($Name+'_STARTED') ([ordered]@{epoch=$Started;supervisor_pid=$PID;phase=$Name;executable=$Exe;argv=$Arguments;no_GPU_Kit_or_PPO=$true;canonical_write=$false})
 $Out=Join-Path $Logs ($Name+'.stdout.log');$Err=Join-Path $Logs ($Name+'.stderr.log')
 if((Test-Path -LiteralPath $Out)-or(Test-Path -LiteralPath $Err)){throw ('Immutable stage logs already exist: '+$Name)}
 $Process=Start-Process -FilePath $Exe -ArgumentList $Arguments -PassThru -Wait -WindowStyle Hidden -RedirectStandardOutput $Out -RedirectStandardError $Err
 $Ended=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000
 Write-Receipt ($Name+'_ENDED') ([ordered]@{started=$Started;ended=$Ended;wall_seconds=$Ended-$Started;exit_code=$Process.ExitCode;process_pid=$Process.Id;supervisor_pid=$PID;stdout=$Out;stderr=$Err;passed=$Process.ExitCode-eq0;no_GPU_Kit_or_PPO=$true;no_existing_env_modification=$true;canonical_write=$false})
 if($Process.ExitCode-ne0){throw ('Stage '+$Name+' failed with exit '+$Process.ExitCode)}
}
try{
 if(!(Test-Path -LiteralPath (Join-Path $Reports 'NEW_ROOT_CREATED_UNUSED_ACTUAL.json'))){throw 'Missing actual newroot creation receipt'}
 if(Test-Path -LiteralPath $Prefix){throw 'New independent prefix must be unused'}
 if(!(Test-Path -LiteralPath 'D:\anaconda\Scripts\conda.exe')){throw 'Original conda executable missing'}
 $Volume=Get-Volume -DriveLetter C
 if($Volume.SizeRemaining-lt80GB){throw 'Actual durable volume below80GiB install guard'}
 Write-Receipt 'INSTALL_HTTPS_REVIEWED_SUPERVISOR_STARTED' ([ordered]@{epoch=$Start;pid=$PID;root=$Root;prefix=$Prefix;durable_free=$Volume.SizeRemaining;guard_bytes=80GB;original_envs_unchanged=$true;no_GPU_Kit_PPO=$true;human_authorized_independent_windows_install=$true;no_Linux_or_3060_RPC=$true;no_budget_write=$true})
 Stage '01B_NEW_PYTHON311_CONDA_OFFICIAL_HTTPS' 'D:\anaconda\Scripts\conda.exe' @('create','--prefix',$Prefix,'--yes','--override-channels','--channel','https://repo.anaconda.com/pkgs/main','python=3.11','pip')
 $Python=Join-Path $Prefix 'python.exe'
 if(!(Test-Path -LiteralPath $Python)){throw 'Conda returned success but own Python missing'}
 Stage '02_PIP_UPDATE' $Python @('-m','pip','install','--upgrade','pip')
 Stage '03_OFFICIAL_TORCH_CU128' $Python @('-m','pip','install','torch==2.7.0+cu128','torchvision==0.22.0+cu128','--index-url','https://download.pytorch.org/whl/cu128')
 Stage '04_TESTED_CORE_PINS' $Python @('-m','pip','install','--constraint',(Join-Path $Root 'tested_constraints_v1.txt'),'rsl-rl-lib==5.0.1','tensordict==0.12.3','warp-lang==1.13.0','numpy==1.26.0','scipy==1.15.3','gymnasium==1.2.1')
 Stage '05_OFFICIAL_ISAACSIM_ALL_EXTSCACHE' $Python @('-m','pip','install','--constraint',(Join-Path $Root 'tested_constraints_v1.txt'),'isaacsim[all,extscache]==5.1.0','--extra-index-url','https://pypi.nvidia.com')
 Stage '06_CPU_PACKAGE_METADATA' $Python @((Join-Path $Root 'metadata_cpu_admission_v1.py'))
 Write-Receipt 'INSTALL_BASE_ENV_COMPLETE_LAB_PENDING' ([ordered]@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;passed_base_packages=$true;Lab_editable_exact_source_pending=$true;newenv=$Prefix;no_GPU_Kit_PPO=$true;no_existing_env_or_SDK_modification=$true;metadata_report=(Join-Path $Reports 'BASE_PACKAGE_METADATA_CPU_ACTUAL.json');qualification_claimed=$false;no_canonical_write=$true})
 Write-Receipt 'INSTALL_HTTPS_REVIEWED_SUPERVISOR_EXIT' ([ordered]@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;pid=$PID;exit_code=0;installation_wall_seconds=([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000)-$Start;no_PPO_cost=$true;no_budget_write=$true;Lab_CPU_admission_pending=$true})
 exit 0
}catch{
 Write-Receipt ('INSTALL_FAILURE_'+[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()) ([ordered]@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000;pid=$PID;original_error=$_.Exception.Message;detail=($_|Out-String);all_prior_logs_receipts_retained=$true;new_env_only=$true;no_GPU_Kit_PPO=$true;no_canonical_write=$true})
 exit 1
}

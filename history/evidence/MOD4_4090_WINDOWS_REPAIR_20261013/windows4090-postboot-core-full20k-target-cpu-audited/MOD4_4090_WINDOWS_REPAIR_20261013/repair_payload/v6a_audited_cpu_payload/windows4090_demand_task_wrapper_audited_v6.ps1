param(
    [Parameter(Mandatory=$true)][string]$LeasePath,
    [Parameter(Mandatory=$true)][string]$ManifestPath,
    [Parameter(Mandatory=$true)][string]$AttemptPath,
    [Parameter(Mandatory=$true)][string]$PythonPath,
    [Parameter(Mandatory=$true)][string]$RuntimePath,
    [Parameter(Mandatory=$true)][ValidateSet('sdk','native','fullrestore','train')][string]$StageMode,
    [int]$TrainSeconds=3600
)
$ErrorActionPreference='Stop'
$TaskPayloadPath=$PSScriptRoot
$TaskLease=Get-Content -LiteralPath $LeasePath -Raw | ConvertFrom-Json
$TaskScopePath=[IO.Path]::GetFullPath([string]$TaskLease.scope_root)
$TaskEnvironmentRoot=[IO.Path]::GetFullPath([string]$TaskLease.environment_root)
$TaskGlobalLock=[IO.Path]::GetFullPath([string]$TaskLease.shared_gpu_lock)
if (-not $TaskScopePath.StartsWith($TaskEnvironmentRoot + '\',[StringComparison]::OrdinalIgnoreCase) -or $TaskGlobalLock -ne (Join-Path $TaskEnvironmentRoot 'WINDOWS4090_GPU_EXCLUSIVE.lock')) {throw 'Scope must bind the single environment-wide native GPU lock'}
$TaskAttemptPath=[IO.Path]::GetFullPath($AttemptPath)
if (-not $TaskAttemptPath.StartsWith($TaskScopePath + '\attempts\',[StringComparison]::OrdinalIgnoreCase)) {throw 'Attempt outside explicitly leased scope'}
if (-not $TaskLease.approved_GPU_scope -or $TaskLease.mode -ne $StageMode) {throw 'GPU lease not approved for requested stage'}
$TaskLogPath=Join-Path $TaskScopePath ('dispatch_logs\' + [string]$TaskLease.case_id)
New-Item -ItemType Directory -Path $TaskLogPath -Force | Out-Null
$TaskStartedPath=Join-Path $TaskLogPath 'DEMAND_WRAPPER_STARTED_ACTUAL.json'
if (Test-Path -LiteralPath $TaskStartedPath) {throw 'Demand wrapper already consumed; do not replay'}
$TaskStart=@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000; wrapperPID=$PID; case=[string]$TaskLease.case_id; noSSHChildLifetimeDependency=$true; noPeriodicOrBootTrigger=$true; stage=$StageMode}
$TaskStream=[IO.File]::Open($TaskStartedPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
try {$TaskBytes=[Text.Encoding]::UTF8.GetBytes(($TaskStart | ConvertTo-Json));$TaskStream.Write($TaskBytes,0,$TaskBytes.Length);$TaskStream.Flush($true)} finally {$TaskStream.Close()}
Set-Location -LiteralPath $TaskPayloadPath
& $PythonPath (Join-Path $TaskPayloadPath 'run_windows4090_stage_audited_v6_once.py') --lease $LeasePath --manifest $ManifestPath --attempt $AttemptPath --python $PythonPath --runtime-root $RuntimePath --mode $StageMode --train-seconds $TrainSeconds *> (Join-Path $TaskLogPath 'parent_stdout.log')
$TaskExitCode=$LASTEXITCODE
@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000; wrapperPID=$PID; parentExitCode=$TaskExitCode; parentEXITReceiptExpected=(Join-Path $AttemptPath 'EXIT_RECEIPT.json'); noAutomaticRestart=$true; OSlockOwnershipOnlyInsidePythonParent=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $TaskLogPath 'DEMAND_WRAPPER_EXIT_ACTUAL.json') -Encoding utf8
exit $TaskExitCode

param(
    [Parameter(Mandatory=$true)][string]$LeasePath,
    [Parameter(Mandatory=$true)][string]$ManifestPath,
    [Parameter(Mandatory=$true)][string]$AttemptPath,
    [Parameter(Mandatory=$true)][string]$PythonPath,
    [Parameter(Mandatory=$true)][string]$RuntimePath,
    [Parameter(Mandatory=$true)][ValidateSet('sdk','native','fullrestore','train')][string]$StageMode,
    [int]$TrainSeconds=3600,
    [switch]$StartApprovedLease
)
$ErrorActionPreference='Stop'
$TaskLease=Get-Content -LiteralPath $LeasePath -Raw | ConvertFrom-Json
$TaskScopePath=[IO.Path]::GetFullPath([string]$TaskLease.scope_root)
$TaskEnvironmentRoot=[IO.Path]::GetFullPath([string]$TaskLease.environment_root)
$TaskGlobalLock=[IO.Path]::GetFullPath([string]$TaskLease.shared_gpu_lock)
if (-not $TaskScopePath.StartsWith($TaskEnvironmentRoot + '\',[StringComparison]::OrdinalIgnoreCase) -or $TaskGlobalLock -ne (Join-Path $TaskEnvironmentRoot 'WINDOWS4090_GPU_EXCLUSIVE.lock')) {throw 'Scope must bind the single environment-wide native GPU lock'}
$TaskName='MOD4_Windows4090_Repair_20261013_' + [string]$TaskLease.case_id
if ($TaskLease.case_id -notmatch '^[A-Za-z0-9_-]+$') {throw 'Unsafe or missing unique case ID'}
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {throw 'Already registered once; inspect actual receipts instead of replacing task'}
foreach ($TaskFilePath in @($LeasePath,$ManifestPath,$PythonPath,(Join-Path $PSScriptRoot 'windows4090_demand_task_wrapper_audited_v6.ps1'))) {if (-not (Test-Path -LiteralPath $TaskFilePath -PathType Leaf)) {throw ('Missing explicit file: ' + $TaskFilePath)}}
if ($StartApprovedLease -and (-not $TaskLease.approved_GPU_scope -or $TaskLease.mode -ne $StageMode)) {throw 'Starting needs exact approved GPU stage lease'}
function QuoteTaskArg([string]$TaskArgument) {if ($TaskArgument.Contains('"')) {throw 'Unexpected quote in task path'};return '"' + $TaskArgument + '"'}
$TaskArguments='-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ' + (QuoteTaskArg (Join-Path $PSScriptRoot 'windows4090_demand_task_wrapper_audited_v6.ps1')) + ' -LeasePath ' + (QuoteTaskArg $LeasePath) + ' -ManifestPath ' + (QuoteTaskArg $ManifestPath) + ' -AttemptPath ' + (QuoteTaskArg $AttemptPath) + ' -PythonPath ' + (QuoteTaskArg $PythonPath) + ' -RuntimePath ' + (QuoteTaskArg $RuntimePath) + ' -StageMode ' + $StageMode + ' -TrainSeconds ' + $TrainSeconds
$TaskAction=New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument $TaskArguments -WorkingDirectory $PSScriptRoot
# Demand only: no startup, periodic or time trigger. Interactive logon explicitly
# requires the approved Win10 user to be logged in; it stores no credentials.
$TaskPrincipal=New-ScheduledTaskPrincipal -UserId 'Win10' -LogonType Interactive -RunLevel Highest
$TaskSettings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$TaskDefinition=New-ScheduledTask -Action $TaskAction -Principal $TaskPrincipal -Settings $TaskSettings
Register-ScheduledTask -TaskName $TaskName -InputObject $TaskDefinition | Out-Null
$TaskXML=Export-ScheduledTask -TaskName $TaskName
$TaskRegistered=Get-ScheduledTask -TaskName $TaskName
if (@($TaskRegistered.Triggers | Where-Object { $null -ne $_ }).Count -ne 0) {throw 'Unexpected trigger registered'}
$TaskReceiptPath=Join-Path $TaskScopePath ('dispatch_logs\' + [string]$TaskLease.case_id)
New-Item -ItemType Directory -Path $TaskReceiptPath -Force | Out-Null
$TaskXML | Set-Content -LiteralPath (Join-Path $TaskReceiptPath 'REGISTERED_DEMAND_TASK_ACTUAL.xml') -Encoding utf8
@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000; task=$TaskName; user='Win10'; triggers=0; actionArguments=$TaskArguments; sourceWrapperSHA=(Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'windows4090_demand_task_wrapper_audited_v6.ps1') -Algorithm SHA256).Hash.ToLower(); registered=$true; GPUstartRequested=[bool]$StartApprovedLease; noStoredCredentials=$true; separateWindowsNamespace=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $TaskReceiptPath 'DEMAND_TASK_REGISTERED_ACTUAL.json') -Encoding utf8
if ($StartApprovedLease) {Start-ScheduledTask -TaskName $TaskName}

$ErrorActionPreference = 'Stop'
$stageRoot = $PSScriptRoot
$workspaceRoot = Split-Path -Parent $stageRoot
$playerRoot = Join-Path $workspaceRoot 'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
$driverPath = Join-Path $playerRoot 'drive_rm7v7_moe.py'
$pythonPath = Join-Path $workspaceRoot '.venv/Scripts/pythonw.exe'
$receiptPath = Join-Path $stageRoot 'reports/REQUESTED_PLAYER_V3_LAUNCH_AND_CURRENT_ACTUAL.json'
if (Test-Path -LiteralPath $receiptPath) { throw 'This player launch has already been consumed.' }
$before = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python(w)?\.exe$' -and $_.CommandLine -match 'drive_rm7v7_moe\.py' })
if ($before.Count -ne 0) { throw 'A player is already active; preserve that window.' }
$began = [DateTimeOffset]::Now
$launched = Start-Process -FilePath $pythonPath -ArgumentList @('-B','-X','utf8',$driverPath) -WorkingDirectory $playerRoot -RedirectStandardOutput (Join-Path $stageRoot 'reports/PLAYER_V3_STDOUT.txt') -RedirectStandardError (Join-Path $stageRoot 'reports/PLAYER_V3_STDERR.txt') -PassThru
$launchInfo = [ordered]@{ epoch=$began.ToUnixTimeMilliseconds()/1000; launch_pid=$launched.Id; requested_executable=$pythonPath; requested_argv=@('-B','-X','utf8',$driverPath); prelaunch_actual_matching_players=$before.Count; user_requested_visible_interactive_player=$true }
$launchInfo | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $stageRoot 'reports/PLAYER_V3_PROCESS_STARTED_ACTUAL.json') -Encoding utf8
$verified = $false
while (([DateTimeOffset]::Now - $began).TotalSeconds -lt 45) {
    $newRuns = @(Get-ChildItem -LiteralPath (Join-Path $playerRoot 'rm7v7_moe_runs') -Directory | Where-Object { $_.CreationTimeUtc -ge $began.UtcDateTime.AddSeconds(-1) } | Sort-Object CreationTimeUtc -Descending)
    foreach ($run in $newRuns) {
        $startedPath=Join-Path $run.FullName 'INTERACTIVE_STARTED.json'
        $currentPath=Join-Path $run.FullName 'INTERACTIVE_CURRENT.json'
        if (!(Test-Path -LiteralPath $startedPath) -or !(Test-Path -LiteralPath $currentPath)) { continue }
        try { $started=Get-Content -LiteralPath $startedPath -Raw | ConvertFrom-Json; $current=Get-Content -LiteralPath $currentPath -Raw | ConvertFrom-Json } catch { continue }
        if ($started.checkpoint -ne 'latest_moe_scut_fudan_hour7_20261019.onnx' -or $started.pid -ne $current.pid) { continue }
        $identity=Get-CimInstance Win32_Process -Filter "ProcessId = $($current.pid)"
        if ($null -eq $identity -or $identity.CommandLine -notmatch [regex]::Escape($driverPath)) { continue }
        if (!$started.viewer_running -or !$current.finite -or $null -ne $current.fault) { continue }
        $process=Get-Process -Id $current.pid
        $result=[ordered]@{ status='STARTED_AND_ACTUAL_CURRENT_VERIFIED'; verified_epoch=[DateTimeOffset]::Now.ToUnixTimeMilliseconds()/1000; launch=$launchInfo; run_path=$run.FullName; actual_identity=($identity | Select-Object ProcessId,ParentProcessId,ExecutablePath,CreationDate,CommandLine); main_window_title=$process.MainWindowTitle; main_window_handle=$process.MainWindowHandle.ToInt64(); interactive_started=$started; interactive_current=$current; training_or_budget_changed=$false; new_remote_transport=$false }
        $result | ConvertTo-Json -Depth 24 | Set-Content -LiteralPath $receiptPath -Encoding utf8
        Copy-Item -LiteralPath $startedPath -Destination (Join-Path $stageRoot 'reports/PLAYER_V3_INTERACTIVE_STARTED_SNAPSHOT.json')
        Copy-Item -LiteralPath $currentPath -Destination (Join-Path $stageRoot 'reports/PLAYER_V3_INTERACTIVE_CURRENT_SNAPSHOT.json')
        $verified=$true
        Write-Output ([pscustomobject]$result | Select-Object status,run_path,main_window_title,main_window_handle | ConvertTo-Json)
        break
    }
    if ($verified) { break }
    Start-Sleep -Milliseconds 500
}
if (!$verified) {
    $failure=[ordered]@{ status='UNVERIFIED'; actual_processes=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python(w)?\.exe$' -and $_.CommandLine -match 'drive_rm7v7_moe\.py' } | Select-Object ProcessId,ParentProcessId,ExecutablePath,CreationDate,CommandLine); do_not_blindly_relaunch=$true }
    $failure | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $stageRoot 'reports/PLAYER_V3_LAUNCH_VERIFICATION_ORIGINAL_ERROR.json') -Encoding utf8
    throw 'No fresh successful interactive receipt within the bounded launch check; inspect original outputs without relaunching.'
}

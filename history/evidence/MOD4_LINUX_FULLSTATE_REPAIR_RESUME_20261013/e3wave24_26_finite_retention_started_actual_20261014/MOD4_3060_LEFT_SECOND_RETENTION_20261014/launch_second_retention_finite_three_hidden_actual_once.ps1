$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$receiptPath = Join-Path $taskRoot 'reports/SECOND_RETENTION_FINITE_BATCH_ROOT_DISPATCH_ACTUAL.json'
$intentPath = Join-Path $taskRoot 'reports/SECOND_RETENTION_FINITE_BATCH_ROOT_DISPATCH_INTENT.json'
$startedPath = Join-Path $taskRoot 'reports/SECOND_RETENTION_FIXED_THREE_STARTED_ACTUAL.json'
if ((Test-Path -LiteralPath $receiptPath) -or (Test-Path -LiteralPath $intentPath) -or (Test-Path -LiteralPath $startedPath)) { throw 'Inspect actual previous launch outcome; do not replay' }
$upload = Get-Content -LiteralPath (Join-Path $taskRoot 'reports/SECOND_RETENTION_TARGET_SOURCE_UPLOAD_CPU_ACTUAL.json') -Raw | ConvertFrom-Json
if (-not $upload.source_whole20k_195_107_99_CPU_verified) { throw 'No actual target CPU admission' }
$waveReview = Get-Content -LiteralPath (Join-Path (Split-Path $taskRoot -Parent) 'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json') -Raw | ConvertFrom-Json
if (-not ($waveReview.passed -and $waveReview.actual_parent_child_exited_and_shared_OSlockfree)) { throw 'Wave full data and actual lease boundary missing' }
$exe = 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
$scriptPath = Join-Path $taskRoot 'run_second_retention_fixed_three_candidate_batch_once.py'
$intent = @{ epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000.0; sourceSHA='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'; script=$scriptPath; ownThreeOnly=$true; unknownOutcomeReadOnlyNoReplay=$true; noPPO=$true }
$intent | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $intentPath -Encoding utf8NoBOM
$argsExact = @('"'+$scriptPath+'"','--execute-root-fixed-three-cases')
$p = Start-Process -FilePath $exe -ArgumentList $argsExact -WorkingDirectory $taskRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskRoot 'reports/SECOND_RETENTION_FINITE_BATCH_STDOUT.log') -RedirectStandardError (Join-Path $taskRoot 'reports/SECOND_RETENTION_FINITE_BATCH_STDERR.log') -PassThru
$actual = Get-CimInstance Win32_Process -Filter ('ProcessId='+$p.Id)
if (-not $actual -or $actual.CommandLine -notlike '*run_second_retention_fixed_three_candidate_batch_once.py*') { throw 'Unknown launch outcome: inspect actual STARTED/ERROR, no restart' }
$value = @{ epoch=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000.0; pid=$actual.ProcessId; parentPid=$actual.ParentProcessId; creation=$actual.CreationDate.ToString('o'); argv=$actual.CommandLine; executable=$actual.ExecutablePath; scriptSHA=(Get-FileHash -LiteralPath $scriptPath -Algorithm SHA256).Hash.ToLowerInvariant(); sole210and249TransportOwnerWhileActuallyActive=$true; noPPO=$true; fixedNewCases=3; originalNativesReusedNoReplay=$true }
$value | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding utf8NoBOM
$value | ConvertTo-Json -Depth 6 -Compress

$ErrorActionPreference = 'Stop'
$scope = 'F:\RMPOLAR-RL\mjcf_mod4_h1_archive_01a1967f_20261102'
$workspace = 'C:\Users\lulu\Desktop\claude\mjcf'
$python = 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe'
$names = @(
    'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021',
    'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013'
)
New-Item -ItemType Directory -Path (Join-Path $scope 'workspace') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $scope 'receipts') -Force | Out-Null
$once = Join-Path $scope 'receipts\MIGRATION462_STARTED.json'
if (Test-Path -LiteralPath $once) { throw 'Migration462 has already started; inspect receipts before resuming.' }
@{ epoch=[DateTimeOffset]::Now.ToUnixTimeSeconds(); status='STARTED'; directories=$names; preserves_original_paths='directory junctions'; authorization='[REDACTED]' } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $once -Encoding utf8
foreach ($name in $names) {
    $source = Join-Path $workspace $name
    $destination = Join-Path (Join-Path $scope 'workspace') $name
    $backup = $source + '.migration462_verified_backup'
    $receipt = Join-Path (Join-Path $scope 'receipts') ($name + '.verified.json')
    $cutover = Join-Path (Join-Path $scope 'receipts') ($name + '.cutover.json')
    $log = Join-Path (Join-Path $scope 'receipts') ($name + '.robocopy.log')
    $resolvedSource = (Resolve-Path -LiteralPath $source).Path
    if ($resolvedSource -ne $source -or -not $source.StartsWith($workspace + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected source scope' }
    $sourceItem = Get-Item -LiteralPath $source -Force
    if ($sourceItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Source already a reparse point' }
    if (Test-Path -LiteralPath $destination) { throw 'Destination already exists; do not overwrite' }
    if (Test-Path -LiteralPath $backup) { throw 'Backup already exists' }
    $busy = @(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.Name -match '^(python|pythonw|ffmpeg|robocopy)(\.exe)?$' -and $_.CommandLine -and $_.CommandLine.Contains($source, [StringComparison]::OrdinalIgnoreCase) })
    if ($busy.Count) { throw ('Source has active process: ' + ($busy.ProcessId -join ',')) }
    Write-Output ('COPY_START ' + $name)
    & robocopy $source $destination /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /XJ /MT:16 /NFL /NDL /NP /BYTES "/LOG:$log"
    $copyCode = $LASTEXITCODE
    if ($copyCode -gt 7) { throw ('Robocopy failure ' + $copyCode) }
    Write-Output ('VERIFY_START ' + $name)
    & $python -u -B -X utf8 (Join-Path $scope 'admin\copy_verify_tree.py') --source $source --destination $destination --receipt $receipt
    if ($LASTEXITCODE -ne 0) { throw 'Byte verification failed; source retained' }
    $verified = Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
    if (-not $verified.passed) { throw 'Invalid verification receipt' }
    $busy = @(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.Name -match '^(python|pythonw|ffmpeg|robocopy)(\.exe)?$' -and $_.CommandLine -and $_.CommandLine.Contains($source, [StringComparison]::OrdinalIgnoreCase) })
    if ($busy.Count) { throw 'New source process; cutover postponed' }
    Move-Item -LiteralPath $source -Destination $backup
    try {
        New-Item -ItemType Junction -Path $source -Target $destination | Out-Null
        $link = Get-Item -LiteralPath $source -Force
        if ($link.LinkType -ne 'Junction' -or $link.Target -ne $destination) { throw 'Junction target mismatch' }
    } catch {
        if (-not (Test-Path -LiteralPath $source)) { Move-Item -LiteralPath $backup -Destination $source }
        throw
    }
    $resolvedBackup = (Resolve-Path -LiteralPath $backup).Path
    if ($resolvedBackup -ne $backup -or -not $backup.StartsWith($workspace + '\', [StringComparison]::OrdinalIgnoreCase) -or -not $backup.EndsWith('.migration462_verified_backup')) { throw 'Backup deletion escaped explicit scope' }
    if ((Get-Item -LiteralPath $backup -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Backup unexpectedly a reparse point' }
    Remove-Item -LiteralPath $backup -Recurse -Force
    @{ passed=$true; completed=[DateTimeOffset]::Now.ToUnixTimeSeconds(); original_path=$source; new_path=$destination; original_path_type='Junction'; copied_bytes=$verified.bytes; files=$verified.files; all_file_SHA256_verified=$true; C_originals_deleted=$true; backup_absent=(-not(Test-Path -LiteralPath $backup)); unrelated_workspace_changes=0; model_deserializations=0; physics_steps=0; verification_receipt=$receipt } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $cutover -Encoding utf8
    Write-Output ('MIGRATED ' + $name + ' ' + $verified.bytes)
}
@{ passed=$true; completed=[DateTimeOffset]::Now.ToUnixTimeSeconds(); directories=$names; freeC=(Get-PSDrive -Name C).Free; freeF=(Get-PSDrive -Name F).Free } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $scope 'receipts\MIGRATION462_COMPLETE.json') -Encoding utf8

# Read-only transport payload. No disk mount, format, drive assignment, WSL start,
# registry writes, package installation, recursive search, training or budget write.
$ErrorActionPreference = 'Stop'
$taskResult = [ordered]@{ observed_at = (Get-Date).ToString('o'); read_only = $true; disk_mount_or_OS_changes = $false; no_credentials_output = $true }
try {
    $taskResult.disks = @(Get-Disk | Select-Object Number,FriendlyName,BusType,PartitionStyle,OperationalStatus,IsBoot,IsSystem,Size)
} catch { $taskResult.disks_error = $_.Exception.Message }
try {
    $taskResult.partitions = @(Get-Partition | Select-Object DiskNumber,PartitionNumber,DriveLetter,Type,GptType,Size,IsBoot,IsSystem)
} catch { $taskResult.partitions_error = $_.Exception.Message }
try {
    $taskResult.volumes = @(Get-Volume | Select-Object DriveLetter,FileSystem,FileSystemLabel,HealthStatus,OperationalStatus,Size,SizeRemaining)
} catch { $taskResult.volumes_error = $_.Exception.Message }
try {
    $taskResult.visible_filesystem_drives = @(Get-PSDrive -PSProvider FileSystem | Select-Object Name,Root,Used,Free)
} catch { $taskResult.filesystem_drives_error = $_.Exception.Message }
# --list only; never use --mount/--install/--shutdown or access a stopped distro UNC.
if (Get-Command wsl.exe -ErrorAction SilentlyContinue) {
    $taskResult.wsl_list_verbose = @(& wsl.exe --list --verbose 2>&1 | ForEach-Object { "$($_)" })
    $taskResult.wsl_list_exit_code = $LASTEXITCODE
}
$taskResult.canonical_visible_readback = @()
foreach ($taskDrive in @(Get-PSDrive -PSProvider FileSystem)) {
    foreach ($taskRelative in @('home\egde\rl_candidates\MOD4_native_floor_continue10h_20260930\TRAINING_BUDGET_10H.json', 'rl_candidates\MOD4_native_floor_continue10h_20260930\TRAINING_BUDGET_10H.json')) {
        $taskPath = Join-Path -Path $taskDrive.Root -ChildPath $taskRelative
        try {
            if (Test-Path -LiteralPath $taskPath -PathType Leaf) {
                $taskFile = Get-Item -LiteralPath $taskPath
                $taskHash = (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLowerInvariant()
                $taskBudget = Get-Content -LiteralPath $taskPath -Raw | ConvertFrom-Json
                $taskResult.canonical_visible_readback += [ordered]@{ path=$taskPath; bytes=$taskFile.Length; sha256=$taskHash; last_write_time=$taskFile.LastWriteTimeUtc.ToString('o'); property_names=@($taskBudget.PSObject.Properties.Name); original_authority_not_replaced=$true; only_snapshot_read_no_write=$true }
            }
        } catch {
            $taskResult.canonical_visible_readback += [ordered]@{ path=$taskPath; read_error=$_.Exception.Message; attempted_write=$false }
        }
    }
}
$taskResult.canonical_not_visible_is_not_proof_Linux_original_missing = $true
$taskResult | ConvertTo-Json -Depth 9 -Compress

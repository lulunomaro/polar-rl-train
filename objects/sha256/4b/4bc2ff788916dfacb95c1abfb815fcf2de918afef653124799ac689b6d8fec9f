<#
Read-only heartbeat monitor for the RM2025 training run.

Replaces the Codex automation heartbeat with a plain local PowerShell loop that uses
Start-Sleep between snapshots.  It NEVER touches the training process (no restart, no
kill, no config change): it only SSHes to the target, snapshots the latest log and
appends one row to docs/monitor_log.txt + docs/monitor_status.json + docs/monitor_history.csv.

QUOTING HISTORY (the bug this rewrite kills):
  Windows PowerShell 5.1 strips embedded double quotes when handing arguments to a
  native .exe, so a remote `printf "...\n"` reached bash unquoted, and `grep -E "a|b"`
  split into a pipeline (`bash: Mean: command not found`).  Everything below therefore
  uses ONLY single quotes (doubled for PowerShell) plus plain `echo` section markers.

Start (detached):
  Start-Process -WindowStyle Hidden powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','D:\claude2\fangzhen\scripts\monitor_rm2025.ps1'
Debug exactly one cycle in the foreground:
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\monitor_rm2025.ps1 -Once
Stop:  New-Item -ItemType File D:\claude2\fangzhen\docs\STOP_MONITOR   (checked every loop)
#>
param(
  [int]$IntervalSec = 600,
  [double]$MaxHours = 14,
  [string]$Experiment = 'rm2025_later_flat_v2',
  [double]$WarnStd = 0.25,
  [double]$WarnEp = 100,
  [int]$WarnAfterIter = 120,
  [switch]$Once
)

$root = 'D:\claude2\fangzhen'
$py   = Join-Path $root '.venv\Scripts\python.exe'
$tsh  = Join-Path $root 'scripts\tsh.py'
$raw  = Join-Path $root 'docs\_monitor_raw.txt'
$log  = Join-Path $root 'docs\monitor_log.txt'
$st   = Join-Path $root 'docs\monitor_status.json'
$hist = Join-Path $root 'docs\monitor_history.csv'
$stop = Join-Path $root 'docs\STOP_MONITOR'
$env:TSH_OUT = $raw

$base   = '/home/egde/fangzhen_linux'
$expDir = $base + '/train/logs/rsl_rl/' + $Experiment
$remote = 'echo ==PROC==; pgrep -cf ''[m]jlab.scripts.train'' || echo 0; ' +
          'echo ==CKPT==; ls -t ' + $expDir + '/*/model_*.pt 2>/dev/null | head -4; ' +
          'echo ==LOG==; L=$(cat ' + $base + '/logs/linux_launch/latest_rm2025_later_log_file); ' +
          'grep -E ''Learning iteration|Mean episode length|Mean action std|Steps per second|Mean reward|ETA'' $L | tail -14; ' +
          'echo ==GPU==; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; ' +
          'echo ==ERR==; grep -cE ''RuntimeError|Traceback|CUDA out of memory'' $L || true'

function Get-Section([string]$text, [string]$name) {
  $m = [regex]::Match($text, '(?s)==' + $name + '==\r?\n(.*?)(?=\r?\n==[A-Z]+==|$)')
  if ($m.Success) { $m.Groups[1].Value.Trim() } else { '' }
}

function Get-LastMatch([string]$text, [string]$pattern) {
  $ms = [regex]::Matches($text, $pattern)
  if ($ms.Count -gt 0) { $ms[$ms.Count - 1].Groups[1].Value } else { $null }
}

if (-not (Test-Path $hist)) { Set-Content -Path $hist -Value 'time,iter,ep,std,fps,reward,note' }
Add-Content -Path $log -Value ((Get-Date -Format 'MM-dd HH:mm') + '  monitor started, interval ' + $IntervalSec + 's, max ' + $MaxHours + 'h, once=' + $Once)

$deadline = (Get-Date).AddHours($MaxHours)
$lastIter = -2
$stall    = 0
$samples  = 0

while ($true) {
  if (Test-Path $stop) { Add-Content -Path $log -Value ((Get-Date -Format 'MM-dd HH:mm') + '  STOP_MONITOR seen, exiting'); break }
  if (-not $Once -and (Get-Date) -ge $deadline) { Add-Content -Path $log -Value ((Get-Date -Format 'MM-dd HH:mm') + '  max hours reached, exiting'); break }

  $note = ''
  try {
    & $py $tsh exec $remote | Out-Null
    $t = Get-Content $raw -Raw
    if ($t -match '--- STDERR ---') { $t = $t.Substring(0, $t.IndexOf('--- STDERR ---')) }

    $logTxt = Get-Section $t 'LOG'
    $proc   = Get-Section $t 'PROC'
    $ckp    = (Get-Section $t 'CKPT') -split '\r?\n' | Where-Object { $_ } | Select-Object -Last 1
    $gpuTxt = Get-Section $t 'GPU'
    $errTxt = Get-Section $t 'ERR'

    $iter = if ($v = Get-LastMatch $logTxt 'Learning iteration (\d+)/') { [int]$v } else { -1 }
    $ep   = if ($v = Get-LastMatch $logTxt 'Mean episode length:\s+([\d.]+)') { [double]$v } else { -1 }
    $std  = if ($v = Get-LastMatch $logTxt 'Mean action std:\s+([\d.]+)') { [double]$v } else { -1 }
    $fps  = if ($v = Get-LastMatch $logTxt 'Steps per second:\s+([\d.]+)') { [double]$v } else { -1 }
    $rew  = if ($v = Get-LastMatch $logTxt 'Mean reward:\s+(-?[\d.]+)') { [double]$v } else { [double]::NaN }
    $pnum = if ($proc -match '(\d+)') { [int]$Matches[1] } else { -1 }
    $errs = if ($errTxt -match '(\d+)') { [int]$Matches[1] } else { -1 }
    $gpu  = if ($gpuTxt) { ($gpuTxt -replace '\s+', ' ').Trim() } else { '?' }
    $ckptName = if ($ckp) { Split-Path $ckp -Leaf } else { '?' }

    if ($pnum -le 0) { $note = 'DEAD' }
    elseif ($std -ge $WarnStd) { $note = 'STD_HIGH' }
    elseif ($errs -gt 0) { $note = 'LOG_ERRORS' }
    elseif ($iter -ge $WarnAfterIter -and $ep -ge 0 -and $ep -lt $WarnEp) { $note = 'EP_LOW' }

    if ($iter -eq $lastIter -and $iter -ge 0) { $stall++ } else { $stall = 0 }
    if ($stall -ge 3 -and $note -eq '') { $note = 'STALLED' }
    $lastIter = $iter
    $samples++

    $line = '{0}  iter={1,-5} ep={2,-8} std={3,-6} rew={4,-8} fps={5,-8} gpu={6,-16} ckpt={7,-14} proc={8} {9}' -f `
      (Get-Date -Format 'MM-dd HH:mm'), $iter, $ep, $std, $rew, $fps, $gpu, $ckptName, $pnum, $note
    Add-Content -Path $hist -Value ('{0},{1},{2},{3},{4},{5},{6}' -f (Get-Date -Format s), $iter, $ep, $std, $fps, $rew, $note)
    @{ time = (Get-Date -Format o); iter = $iter; ep = $ep; std = $std; fps = $fps; reward = $rew; gpu = $gpu
       ckpt = $ckptName; proc = $pnum; errs = $errs; note = $note; samples = $samples } |
      ConvertTo-Json -Compress | Set-Content -Path $st
  } catch {
    $line = (Get-Date -Format 'MM-dd HH:mm') + '  MONITOR_ERROR ' + $_.Exception.Message
  }

  Add-Content -Path $log -Value $line
  if ($Once) { Write-Host $line; break }
  Start-Sleep -Seconds $IntervalSec
}
Add-Content -Path $log -Value ((Get-Date -Format 'MM-dd HH:mm') + '  monitor exit')

<#
Keep the v2 run moving without ever racing it.

`rm2025_later_flat_v2` was launched with TARGET_ITER=500, which at the measured 5.1 s per
iteration is ~45 minutes - far short of the budget the launcher comment assumed (15 s/iter
=> "10 h").  When the trainer exits at that budget the run simply stops, so this watchdog
resumes it toward a larger target, and it does it the only safe way:

  * it NEVER touches a live trainer: the remote continue script checks `pgrep` itself and
    exits if anything is training, so a race here cannot produce two runs on one GPU;
  * it only fires when no trainer exists AND the newest checkpoint is below the target;
  * it gives up after -MaxAttempts failed restarts and says so in the log, instead of
    hammering a run whose identity gate is failing;
  * it is read-only apart from that one continue call; no kills, no config edits.

Start (detached):
  Start-Process -WindowStyle Hidden powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass',
    '-File','D:\claude2\fangzhen\scripts\watchdog_rm2025_later.ps1' -PassThru
Debug one cycle:  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\watchdog_rm2025_later.ps1 -Once
Stop:             New-Item -ItemType File D:\claude2\fangzhen\docs\STOP_WATCHDOG
#>
param(
  [int]$IntervalSec = 240,
  [double]$MaxHours = 12,
  [string]$Experiment = 'rm2025_later_flat_v2',
  [int]$TargetIter = 1500,
  [int]$MaxAttempts = 3,
  [int]$MinMinutesBetweenAttempts = 15,
  [switch]$Once
)

$root = 'D:\claude2\fangzhen'
$py   = Join-Path $root '.venv\Scripts\python.exe'
$tsh  = Join-Path $root 'scripts\tsh.py'
$raw  = Join-Path $root 'docs\_watchdog_raw.txt'
$log  = Join-Path $root 'docs\watchdog_log.txt'
$st   = Join-Path $root 'docs\watchdog_status.json'
$stop = Join-Path $root 'docs\STOP_WATCHDOG'
$env:TSH_OUT = $raw

$base   = '/home/egde/fangzhen_linux'
$expDir = $base + '/train/logs/rsl_rl/' + $Experiment
$probe  = 'echo ==PROC==; pgrep -cf ''[m]jlab.scripts.train'' || echo 0; ' +
          'echo ==ITER==; find ' + $expDir + ' -name ''model_[0-9]*.pt'' -printf ''%f\n'' 2>/dev/null ' +
          '| sed ''s/^model_//; s/\.pt$//'' | sort -n | tail -1; ' +
          'echo ==LOG==; L=$(cat ' + $base + '/logs/linux_launch/latest_rm2025_later_log_file); ' +
          'grep -E ''Mean episode length|Learning iteration|Mean action std'' $L | tail -6'

function Get-Section([string]$text, [string]$name) {
  $m = [regex]::Match($text, '(?s)==' + $name + '==\r?\n(.*?)(?=\r?\n==[A-Z]+==|$)')
  if ($m.Success) { $m.Groups[1].Value.Trim() } else { '' }
}
function Get-LastMatch([string]$text, [string]$pattern) {
  $ms = [regex]::Matches($text, $pattern)
  if ($ms.Count -gt 0) { $ms[$ms.Count - 1].Groups[1].Value } else { $null }
}

Add-Content -Path $log -Value ((Get-Date -Format 'MM-dd HH:mm') + '  watchdog started interval ' +
  $IntervalSec + 's exp ' + $Experiment + ' target ' + $TargetIter + ' once=' + $Once)

$deadline = (Get-Date).AddHours($MaxHours)
$attempts = 0
$lastAttempt = [datetime]::MinValue

while ($true) {
  if (Test-Path $stop) { Add-Content -Path $log -Value ((Get-Date -Format 'MM-dd HH:mm') + '  STOP_WATCHDOG seen, exiting'); break }
  if (-not $Once -and (Get-Date) -ge $deadline) { Add-Content -Path $log -Value ((Get-Date -Format 'MM-dd HH:mm') + '  max hours reached, exiting'); break }

  $note = ''
  $continuation = ''
  try {
    & $py $tsh exec $probe | Out-Null
    $t = Get-Content $raw -Raw
    if ($t -match '--- STDERR ---') { $t = $t.Substring(0, $t.IndexOf('--- STDERR ---')) }
    $procTxt = Get-Section $t 'PROC'
    $iterTxt = Get-Section $t 'ITER'
    $logTxt  = Get-Section $t 'LOG'

    $proc = if ($procTxt -match '(\d+)') { [int]$Matches[1] } else { -1 }
    $iter = if ($iterTxt -match '(\d+)') { [int]$Matches[1] } else { -1 }
    $ep   = if ($v = Get-LastMatch $logTxt 'Mean episode length:\s+([\d.]+)') { [double]$v } else { -1 }
    $lr   = if ($v = Get-LastMatch $logTxt 'Learning iteration\s+(\d+)/') { [int]$v } else { -1 }

    if ($proc -le 0 -and $iter -ge 0 -and $iter -lt $TargetIter) {
      $elapsed = ((Get-Date) - $lastAttempt).TotalMinutes
      if ($attempts -ge $MaxAttempts) {
        $note = 'ATTEMPTS_EXHAUSTED'
      } elseif ($elapsed -lt $MinMinutesBetweenAttempts) {
        $note = 'COOLDOWN'
      } else {
        $lastAttempt = Get-Date
        $attempts++
        $cmd = 'cd ' + $base + ' && TARGET_ITER=' + $TargetIter +
               ' bash migration/linux/continue_rm2025_later_training.sh 2>&1 | tail -5'
        & $py $tsh exec $cmd | Out-Null
        $continuation = (Get-Content $raw -Raw) -replace '(?s)--- STDERR ---.*$', ''
        $continuation = ($continuation -replace '\s+', ' ').Trim()
        $note = 'CONTINUED'
      }
    } elseif ($proc -gt 0) {
      $note = 'RUNNING'
    } elseif ($iter -ge $TargetIter) {
      $note = 'TARGET_REACHED'
    }

    $line = '{0}  proc={1} iter={2,-5} ep={3,-9} note={4} {5}' -f `
      (Get-Date -Format 'MM-dd HH:mm'), $proc, $iter, $ep, $note, $continuation
    @{ time = (Get-Date -Format o); proc = $proc; iter = $iter; ep = $ep; note = $note
       attempts = $attempts; target = $TargetIter; last = $continuation } |
      ConvertTo-Json -Compress | Set-Content -Path $st
  } catch {
    $line = (Get-Date -Format 'MM-dd HH:mm') + '  WATCHDOG_ERROR ' + $_.Exception.Message
  }

  Add-Content -Path $log -Value $line
  if ($Once) { Write-Host $line; break }
  Start-Sleep -Seconds $IntervalSec
}
Add-Content -Path $log -Value ((Get-Date -Format 'MM-dd HH:mm') + '  watchdog exit')

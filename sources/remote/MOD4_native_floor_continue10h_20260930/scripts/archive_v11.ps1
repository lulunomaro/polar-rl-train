# Build the V11 baseline archive (V11_original) and a working copy (V11_fix_working).
# Nothing here modifies the live tree; it only copies and fingerprints.
$ErrorActionPreference = 'Stop'
$ROOT = 'D:\claude2\fangzhen'
Set-Location $ROOT
$SRC = @(
  'robot\out_cc',                 # validated closed-chain MJCF + meshes (training plant)
  'sim2sim_cc\rm_vehicle',        # deployment bundle: mjcf / meshes / xacro / config
  'train\rmvehicle\src\rmvehicle',# RL interface: env cfg, robot cfg, names, mdp terms, assets
  'train\deploy',                 # exported ONNX policies + skill reports
  'train\verify_skills.py',
  'train\export_onnx.py',
  'scripts',                      # build_cc.py, cc_gaps.py, leg2d.py, exporters, guards
  'sim2sim\wsl',                  # sim2sim drivers (demo_cc.sh, final_cc.sh, probes)
  'sim2real',                     # sim2real bridge + jump-channel patches
  'docs'                          # HOWTO / PLAN / MOTOR_PARAMS / figures
)
$CKPT = @(
  'train\logs\rsl_rl\rn_cc_v11',
  'train\logs\rsl_rl\rn_cc_v12'
)
foreach ($d in @('V11_original','V11_fix_working')) {
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}
function Sync-Tree($src, $dstRoot) {
  if (-not (Test-Path $src)) { return $false }
  $item = Get-Item $src
  if ($item.PSIsContainer) {
    $leaf = Split-Path $src -Leaf
    $parent = Split-Path (Split-Path $src -Parent) -Parent
    $rel = $src.Substring($ROOT.Length + 1)
    $dst = Join-Path $dstRoot $rel
    robocopy $src $dst /MIR /NFL /NDL /NJH /NJS /NP /R:1 /W:1 | Out-Null
  } else {
    $rel = $src.Substring($ROOT.Length + 1)
    $dst = Join-Path $dstRoot $rel
    New-Item -ItemType Directory -Force -Path (Split-Path $dst -Parent) | Out-Null
    Copy-Item $src $dst -Force
  }
  return $true
}
$copied = @()
foreach ($s in ($SRC + $CKPT)) {
  $full = Join-Path $ROOT ($s -replace '^train\\logs','train\logs')
  if (Test-Path $full) { Sync-Tree $full 'V11_original' | Out-Null; $copied += $s }
  else { Write-Host "  (absent: $s)" }
}
foreach ($s in $SRC) {
  $full = Join-Path $ROOT $s
  if (Test-Path $full) { Sync-Tree $full 'V11_fix_working' | Out-Null }
}
Write-Host ("archived {0} source trees into V11_original (+ working copy)" -f $copied.Count)
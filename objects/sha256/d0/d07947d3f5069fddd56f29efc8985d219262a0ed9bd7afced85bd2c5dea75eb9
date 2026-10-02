$ErrorActionPreference = "Continue"
$R = "D:\claude2\fangzhen"
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'
$env:RM_MOTOR='dm8009'; $env:CC_MOTOR='dm8009'
$env:RM_WHEEL_SCALE='55.0'; $env:RM_WZ_MAX='14.0'; $env:RM_FLAT_PROP='0.25'
$env:RM_TERRAIN_CAP_H='0.20'; $env:RM_GYRO_TARGET='12.566'
$py = "$R\.venv-train\Scripts\python.exe"
Set-Location "$R\train"

"### waiting for v14 to finish"
while ($true) {
  $p = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match "mjlab.scripts.train" }
  if (-not $p) { break }; Start-Sleep 20
}
"### v14 exited at $(Get-Date -Format HH:mm:ss)"
$run = Get-ChildItem "$R\train\logs\rsl_rl\rm_cc_v14" -Directory | Where-Object { $_.Name -notlike "seed*" } | Select-Object -First 1
$ck  = (Get-ChildItem $run.FullName -Filter "model_*.pt" | Sort-Object { [int]($_.BaseName -replace "model_","") } | Select-Object -Last 1).FullName
"### final checkpoint: $ck"

"`n=== 1. export ONNX (contract-carrying)"
& $py export_onnx.py --task RMVehicle-CC-Field-v0 --checkpoint $ck --out deploy/rm_cc_v14_final.onnx 2>&1 |
    Select-String -Pattern "wrote|metadata|action sample|onnx inputs|deployment contract" | ForEach-Object { $_.Line }
Set-Location $R
"`n=== 2. contract drift gate"
& $py scripts\check_contract_drift.py 2>&1 | Select-Object -Last 4
"DRIFT_EXIT=$LASTEXITCODE"

"`n=== 3. verify skills on the 2026 map (field task)"
Set-Location "$R\train"
& $py verify_skills.py --task RMVehicle-CC-Field-v0 --checkpoint $ck --num-envs 64 `
    --out deploy/skills_v14_field.json 2>&1 | Select-String -Pattern "cmd|SUMMARY|\+|\|" | ForEach-Object { $_.Line } | Select-Object -Last 26
"`n=== 4. verify skills on flat arena (skills task)"
& $py verify_skills.py --task RMVehicle-CC-Skills-v0 --checkpoint $ck --num-envs 64 `
    --out deploy/skills_v14_flat.json 2>&1 | Select-String -Pattern "SUMMARY" | ForEach-Object { $_.Line }

"`n=== 5. record a play video of v14"
& $py -m mjlab.scripts.play RMVehicle-CC-Skills-v0 --checkpoint-file $ck --num-envs 8 `
    --viewer native --video True --video-length 500 --video-width 960 --video-height 540 2>&1 |
    Select-String -Pattern "Recording|video|Error|Traceback" | ForEach-Object { $_.Line } | Select-Object -Last 6
$v = Get-ChildItem "$R\train\logs\rsl_rl" -Recurse -Include *.mp4 -ErrorAction SilentlyContinue |
     Sort-Object LastWriteTime | Select-Object -Last 1
if ($v) { New-Item -ItemType Directory -Force "$R\docs\videos" | Out-Null
          Copy-Item $v.FullName "$R\docs\videos\v14_skills_play.mp4" -Force
          "video -> docs/videos/v14_skills_play.mp4 ($([math]::Round($v.Length/1kb)) KB)" }

"`n=== 6. seed and launch v15"
$env:RM_SEED_WHL_STD='0.30'; $env:RM_SEED_LEG_STD='0.22'
& $py "$R\scripts\seed_v15.py" --src $ck 2>&1 | Select-Object -Last 6
Start-Process -FilePath "powershell.exe" -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$R\scripts\run_v15.ps1" -WindowStyle Hidden -RedirectStandardOutput "$R\docs\_cc_v15.log" -RedirectStandardError "$R\docs\_cc_v15.log.err"
"### v15 launched -> docs/_cc_v15.log at $(Get-Date -Format HH:mm:ss)"

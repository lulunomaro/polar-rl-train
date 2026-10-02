$ErrorActionPreference = "Continue"
$R = "D:\claude2\fangzhen"
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
$env:RM_MOTOR='dm8009'; $env:CC_MOTOR='dm8009'; $env:RM_WHEEL_SCALE='55.0'; $env:RM_WZ_MAX='14.0'
$py = "$R\.venv-train\Scripts\python.exe"
Set-Location "$R\train"
"### waiting for v15"
while ($true) {
  $p = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match "mjlab.scripts.train" }
  if (-not $p) { break }; Start-Sleep 30
}
"### v15 exited $(Get-Date -Format HH:mm:ss)"
$run = Get-ChildItem "$R\train\logs\rsl_rl\rm_cc_v15" -Directory | Where-Object { $_.Name -notlike "seed*" } | Select-Object -First 1
$ck  = (Get-ChildItem $run.FullName -Filter "model_*.pt" | Sort-Object { [int]($_.BaseName -replace "model_","") } | Select-Object -Last 1).FullName
"### final v15 checkpoint: $ck"
"`n=== 1. export"
& $py export_onnx.py --task RMVehicle-CC-Field-v0 --checkpoint $ck --out deploy/rm_cc_v15_final.onnx 2>&1 |
    Select-String -Pattern "wrote|metadata contract|action sample" | ForEach-Object { $_.Line }
Set-Location $R
"`n=== 2. contract gate"
& $py scripts\check_contract_drift.py 2>&1 | Select-Object -Last 3
"DRIFT_EXIT=$LASTEXITCODE"
Set-Location "$R\train"
"`n=== 3. verify: gyro BOTH directions, flat arena"
& $py verify_skills.py --task RMVehicle-CC-Skills-v0 --checkpoint $ck --num-envs 64 --only gyro `
    --gyro-ladder "6,10,12,14,-6,-10,-14" --out deploy/skills_v15_gyro.json 2>&1 |
    Select-String -Pattern "cmd wz|\+\d+\.\d+ +-|\-\d+\.\d+ +-|peak|SUMMARY" | ForEach-Object { $_.Line }
"`n=== 4. verify: run + jump on the 2026 map"
& $py verify_skills.py --task RMVehicle-CC-Field-v0 --checkpoint $ck --num-envs 64 --only run `
    --out deploy/skills_v15_field_run.json 2>&1 | Select-String -Pattern "cmd vx|\d\.\d+ +\|" | ForEach-Object { $_.Line }
& $py verify_skills.py --task RMVehicle-CC-Field-v0 --checkpoint $ck --num-envs 64 --only jump `
    --out deploy/skills_v15_field_jump.json 2>&1 | Select-String -Pattern "SUMMARY|UPRIGHT|target rise|\d\.\d\d +\|" | ForEach-Object { $_.Line }
"`n=== 5. seed + launch v16"
$env:RM_SEED_WHL_STD='0.15'; $env:RM_SEED_LEG_STD='0.18'
& $py "$R\scripts\seed_v15.py" --src $ck --dst-dir "logs/rsl_rl/rm_cc_v16/seed_from_v15" 2>&1 | Select-Object -Last 3
Start-Process -FilePath "powershell.exe" -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$R\scripts\run_v16.ps1" -WindowStyle Hidden -RedirectStandardOutput "$R\docs\_cc_v16.log" -RedirectStandardError "$R\docs\_cc_v16.log.err"
"### v16 launched $(Get-Date -Format HH:mm:ss)"

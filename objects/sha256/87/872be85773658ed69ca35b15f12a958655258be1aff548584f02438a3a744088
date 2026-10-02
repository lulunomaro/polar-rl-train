$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='legacy54'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v10\2026-09-04_21-24-03\model_7498.pt'
Write-Output "=== mjlab play: FLAT skills (run / gyro / jump) ==="
& $py -m mjlab.scripts.play RMVehicle-CC-Skills-v0 --checkpoint-file $ck --num-envs 16 --video True --video-length 450 --video-width 960 --video-height 540 2>&1 |
  Select-String -Pattern 'Recording|video|Video|wrote|Error|error|Trace|Exception|iteration|ModuleNotFound' | Select-Object -Last 14
Write-Output "=== mjlab play: 2026 FIELD map ==="
& $py -m mjlab.scripts.play RMVehicle-CC-Field-v0 --checkpoint-file $ck --num-envs 16 --video True --video-length 450 --video-width 960 --video-height 540 2>&1 |
  Select-String -Pattern 'Recording|video|Video|wrote|Error|error|Trace|Exception|ModuleNotFound' | Select-Object -Last 14
Write-Output "=== produced files ==="
Get-ChildItem -Recurse -Filter *.mp4 logs\rsl_rl\rm_cc_v10, logs\rsl_rl\rm_cc_v11 -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
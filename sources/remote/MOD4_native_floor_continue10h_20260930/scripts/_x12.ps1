$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='legacy54'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v10\2026-09-04_21-24-03\model_7498.pt'
foreach($task in 'RMVehicle-CC-Skills-v0','RMVehicle-CC-Field-v0'){
  Write-Output "=== play $task ==="
  & $py -m mjlab.scripts.play $task --checkpoint-file $ck --num-envs 8 --viewer native --video True --video-length 400 --video-width 960 --video-height 540 2>&1 |
    Select-String -Pattern 'Recording|Loading|Step|Error|error|Trace|ValueError|GLFW|Exception|OpenBLAS|Stoppable' | Select-Object -First 6
}
Write-Output "=== mp4 outputs ==="
Get-ChildItem -Recurse -Include *.mp4,*.avi logs -ErrorAction SilentlyContinue | Select-Object FullName,Length
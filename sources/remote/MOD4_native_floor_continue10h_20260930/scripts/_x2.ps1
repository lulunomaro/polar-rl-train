$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$py = 'D:\claude2\fangzhen\.venv\Scripts\python.exe'
$onnx = 'D:\claude2\fangzhen\train\deploy\rm_cc_v10_final.onnx'
Write-Output "=== V1: three skills on the plant v10 was trained on (legacy 50.9 N*m) ==="
& $py scripts\skills_video.py --onnx $onnx --model robot\out_cc_legacy54\scene_cc.xml --leg-eff 50.9 --wheel-eff 10 --phases run,gyro,jump --seconds 6 --out docs\videos\v10_skills_legacy.mp4 2>&1 | Select-String -Pattern 'policy|plant|render|wrote|Error|Trace' | ForEach-Object { "  " + $_.Line }
Write-Output "=== V2: same policy on the honest DM8009 plant (40 N*m + no wheel over-torque) ==="
& $py scripts\skills_video.py --onnx $onnx --model robot\out_cc\scene_cc.xml --leg-eff 40 --wheel-eff 5.5 --phases run,gyro,jump --seconds 6 --out docs\videos\v10_skills_honest.mp4 2>&1 | Select-String -Pattern 'policy|plant|render|wrote|Error|Trace' | ForEach-Object { "  " + $_.Line }
Write-Output "=== V3: RMUC2026 7v7 map traverse ==="
& $py scripts\skills_video.py --onnx $onnx --model sim2sim_cc\rm_vehicle_cc\mjcf\scene_field.xml --leg-eff 50.9 --wheel-eff 10 --phases field --seconds 12 --out docs\videos\v10_field_map.mp4 2>&1 | Select-String -Pattern 'policy|plant|render|wrote|Error|Trace' | ForEach-Object { "  " + $_.Line }
Write-Output "=== files ==="
Get-ChildItem docs\videos\*.mp4 | Select-Object Name,Length,LastWriteTime
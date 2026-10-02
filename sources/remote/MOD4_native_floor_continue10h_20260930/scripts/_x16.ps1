$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$py = 'D:\claude2\fangzhen\.venv\Scripts\python.exe'
$onnx = 'D:\claude2\fangzhen\train\deploy\rm_cc_v10_final.onnx'
Write-Output "=== re-render three skills on the COMPLETE model (honest DM8009 plant) ==="
& $py scripts\skills_video.py --onnx $onnx --model robot\out_cc\scene_cc.xml --leg-eff 40 --wheel-eff 5.5 --phases run,gyro,jump --seconds 6 --out docs\videos\v10_skills_honest_fixedmodel.mp4 2>&1 | Select-String -Pattern 'policy|plant|render|wrote|Error|Trace'
Write-Output "=== 2026 map traverse ==="
& $py scripts\skills_video.py --onnx $onnx --model sim2sim_cc\rm_vehicle_cc\mjcf\scene_field.xml --leg-eff 40 --wheel-eff 5.5 --phases field --seconds 14 --out docs\videos\v10_field_fixedmodel.mp4 2>&1 | Select-String -Pattern 'render|wrote|Error|Trace'
Write-Output "=== regenerate the sim2sim deploy bundle from the fixed model ==="
& $py scripts\export_sim2sim_cc.py 2>&1 | Select-String -Pattern 'wrote|copied|error|Error|meshes|xml' | Select-Object -Last 8
& $py scripts\export_field_scene.py 2>&1 | Select-String -Pattern 'wrote|hf|error|Error' | Select-Object -Last 6
Get-ChildItem docs\videos\*.mp4 | Sort-Object LastWriteTime | Select-Object -Last 4 Name,Length,LastWriteTime
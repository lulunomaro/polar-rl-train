$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$py = 'D:\claude2\fangzhen\.venv\Scripts\python.exe'
$onnx = 'D:\claude2\fangzhen\train\deploy\rm_cc_v10_final.onnx'
Write-Output "=== contact sheet of stills ==="
& $py scripts\vid_stills.py docs\videos\v10_skills_legacy.mp4 docs\videos\v10_skills_honest.mp4 docs\videos\v10_field_map.mp4 --out docs\crops\fig_F_v10_stills.png 2>&1 | Select-Object -Last 2
Write-Output "=== numbers: plant v10 trained on (50.9 N*m) ==="
& $py scripts\verify_skills_mujoco.py --onnx $onnx --scene robot\out_cc_legacy54\scene_cc.xml --leg-eff 50.9 --wheel-eff 10 --skip-field --out docs\crops\skills_v10_legacy.json 2>&1 | Select-String -Pattern '===|cmd|best|SUMMARY|jump|gyro|run|vx|wz|air' | Select-Object -Last 26
Write-Output "=== numbers: honest DM8009 plant (40 N*m, 5.5 N*m wheels) ==="
& $py scripts\verify_skills_mujoco.py --onnx $onnx --scene robot\out_cc\scene_cc.xml --leg-eff 40 --wheel-eff 5.5 --skip-field --out docs\crops\skills_v10_honest.json 2>&1 | Select-String -Pattern '===|cmd|best|SUMMARY|jump|gyro|run|vx|wz|air' | Select-Object -Last 26
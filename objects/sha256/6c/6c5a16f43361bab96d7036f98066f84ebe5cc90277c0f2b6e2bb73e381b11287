$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='legacy54'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v10\2026-09-04_21-24-03\model_7498.pt'
Write-Output "=== mjlab-side verify of v10 (authoritative obs path) ==="
& $py verify_skills.py --task RMVehicle-CC-Field-v0 --checkpoint $ck --num-envs 64 --out D:\claude2\fangzhen\docs\crops\skills_v10_mjlab.json 2>&1 | Select-String -Pattern 'run|gyro|jump|vx|wz|rise|air|SUMMARY|Error|Trace|===|cmd' | Select-Object -Last 30
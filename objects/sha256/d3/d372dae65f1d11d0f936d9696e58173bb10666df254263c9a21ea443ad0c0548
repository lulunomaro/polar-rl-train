$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='dm8009'; $env:RM_RISE_MIN='0.08'; $env:RM_RISE_MAX='0.20'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v11\2026-09-05_00-35-08\model_7997.pt'
& $py verify_skills.py --task RMVehicle-CC-Skills-v0 --checkpoint $ck --num-envs 64 --out D:\claude2\fangzhen\docs\crops\skills_v11_flat.json 2>&1 | Select-String -Pattern 'SUMMARY|achieved|target rise|peak rise' | ForEach-Object { "  " + $_.Line.Trim() }
$env:PYTHONIOENCODING='utf-8'
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match "mjlab.scripts.train" } | ForEach-Object { "stopping v15 pid $($_.ProcessId)"; Stop-Process -Id $_.ProcessId -Force }
Start-Sleep 6
Remove-Item -Recurse -Force D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v15\2* -ErrorAction SilentlyContinue
Set-Location D:\claude2\fangzhen
$env:RM_SEED_WHL_STD='0.18'; $env:RM_SEED_LEG_STD='0.20'
& .venv-train\Scripts\python.exe scripts\seed_v15.py --src train\logs\rsl_rl\rm_cc_v14\2026-09-05_19-27-33\model_9495.pt 2>&1 | Select-Object -Last 4
Start-Process -FilePath "powershell.exe" -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','D:\claude2\fangzhen\scripts\run_v15.ps1' -WindowStyle Hidden -RedirectStandardOutput 'D:\claude2\fangzhen\docs\_cc_v15.log' -RedirectStandardError 'D:\claude2\fangzhen\docs\_cc_v15.log.err'
"v15 relaunched $(Get-Date -Format HH:mm:ss)"

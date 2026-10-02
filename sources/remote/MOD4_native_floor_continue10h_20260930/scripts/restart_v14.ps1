param([string]$Log = "D:\claude2\fangzhen\docs\_cc_v14.log")
$mine = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match "mjlab.scripts.train" }
foreach ($p in $mine) { Write-Output "stopping training pid $($p.ProcessId)"; Stop-Process -Id $p.ProcessId -Force }
Start-Sleep 5
if (Test-Path "D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v14") {
  Get-ChildItem "D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v14" -Directory | Where-Object { $_.Name -notlike "seed*" } | Remove-Item -Recurse -Force
}
Start-Process -FilePath "powershell.exe" -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','D:\claude2\fangzhen\scripts\run_v14.ps1' -WindowStyle Hidden -RedirectStandardOutput $Log -RedirectStandardError ($Log + ".err")
Write-Output "relaunched v14 -> $Log"

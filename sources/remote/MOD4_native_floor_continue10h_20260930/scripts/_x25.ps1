$env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$src = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v11\2026-09-05_00-35-08\videos\play\rl-video-step-0.mp4'
Copy-Item $src 'D:\claude2\fangzhen\docs\videos\v11_mjlab_flat.mp4' -Force
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
  $cl = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
  if ($cl -like '*mjlab.scripts.play*') { Write-Output "killing play pid $($_.Id)"; Stop-Process -Id $_.Id -Force }
}
Start-Sleep -Seconds 3
Remove-Item $src -Force -ErrorAction SilentlyContinue
& .venv\Scripts\python.exe scripts\vid_stills.py docs\videos\v11_mjlab_flat.mp4 --per-video 4 --scale 0.62 --out docs\crops\fig_K_v11_mjlab_flat.png 2>&1 | Select-Object -Last 1
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
$env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
& .venv\Scripts\python.exe scripts\vid_stills.py docs\videos\v11_mjlab_map.mp4 --per-video 4 --scale 0.62 --out docs\crops\fig_L_v11_mjlab_map.png 2>&1 | Select-Object -Last 1
Write-Output '--- v12 health ---'
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
& .venv\Scripts\python.exe scripts\tail_log.py docs\_cc_v12.log 1500
Write-Output '--- videos ---'
Get-ChildItem docs\videos\*.mp4 | Sort-Object LastWriteTime | Select-Object -Last 5 Name,Length,LastWriteTime
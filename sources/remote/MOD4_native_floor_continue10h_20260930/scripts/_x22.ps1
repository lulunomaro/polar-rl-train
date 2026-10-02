$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$py = 'D:\claude2\fangzhen\.venv\Scripts\python.exe'
& $py scripts\export_sim2sim_cc.py --out D:\claude2\fangzhen\sim2sim_cc\rm_vehicle_cc --prefix rm_vehicle_cc 2>&1 | Select-String -Pattern 'plant torques|wrote config|compiles|Error|Trace' | Select-Object -First 6
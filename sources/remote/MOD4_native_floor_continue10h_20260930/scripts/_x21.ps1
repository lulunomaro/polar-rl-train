$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$py = 'D:\claude2\fangzhen\.venv\Scripts\python.exe'
& $py scripts\export_sim2sim_cc.py --out D:\claude2\fangzhen\sim2sim_cc\rm_vehicle_cc --prefix rm_vehicle_cc 2>&1 | Select-String -Pattern 'wrote|compiles|Error|Trace' | Select-Object -Last 6
& $py scripts\export_field_scene.py --out D:\claude2\fangzhen\sim2sim_cc\rm_vehicle_cc 2>&1 | Select-String -Pattern 'wrote|compiles|Error' | Select-Object -Last 2
Write-Output '--- bundle now ---'
& $py scripts\chk_bundle.py
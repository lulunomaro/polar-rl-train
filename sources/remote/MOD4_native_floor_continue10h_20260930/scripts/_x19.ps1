$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$py = 'D:\claude2\fangzhen\.venv\Scripts\python.exe'
Write-Output '=== refresh the sim2sim bundle from the fixed model ==='
& $py scripts\export_sim2sim_cc.py 2>&1 | Select-String -Pattern 'wrote|compiles|Error|Trace' | Select-Object -Last 6
& $py scripts\export_field_scene.py 2>&1 | Select-String -Pattern 'wrote|compiles|Error' | Select-Object -Last 3
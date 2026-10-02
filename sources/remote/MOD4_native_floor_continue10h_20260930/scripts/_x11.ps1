$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$env:CC_MOTOR='legacy54'
.venv\Scripts\python.exe scripts\build_cc.py 2>&1 | Select-Object -Last 1
if (Test-Path robot\out_cc_legacy54) { Remove-Item -Recurse -Force robot\out_cc_legacy54 }
Copy-Item -Recurse robot\out_cc robot\out_cc_legacy54
$env:CC_MOTOR='dm8009'
.venv\Scripts\python.exe scripts\build_cc.py 2>&1 | Select-Object -Last 1
.venv\Scripts\python.exe scripts\install_cc_assets.py 2>&1 | Select-String -Pattern 'installed|Error|Trace' | Select-Object -First 2
Write-Output '--- pixel check: is the robot drawn now? ---'
.venv\Scripts\python.exe scripts\diag2.py
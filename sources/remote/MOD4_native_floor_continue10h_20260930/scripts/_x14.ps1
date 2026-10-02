$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$env:CC_MOTOR='dm8009'; $env:CC_BASE_FACES='220000'; $env:CC_LEG_FACES='9000'
.venv\Scripts\python.exe scripts\build_cc.py 2>&1 | Select-String -Pattern 'base ->|leg meshes'
.venv\Scripts\python.exe scripts\cc_gaps.py 2>&1 | Select-Object -Last 1
.venv\Scripts\python.exe scripts\install_cc_assets.py 2>&1 | Select-String -Pattern 'installed'
$tot = (Get-ChildItem robot\out_cc\meshes\*.stl | Measure-Object Length -Sum).Sum
Write-Output ("mesh payload on disk = {0:N1} MB" -f ($tot/1MB))
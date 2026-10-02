$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
$env:CC_MOTOR='legacy54'
.venv\Scripts\python.exe scripts\build_cc.py 2>&1 | Select-Object -Last 2
if (Test-Path robot\out_cc_legacy54) { Remove-Item -Recurse -Force robot\out_cc_legacy54 }
Copy-Item -Recurse robot\out_cc robot\out_cc_legacy54
$env:CC_MOTOR='dm8009'
.venv\Scripts\python.exe scripts\build_cc.py 2>&1 | Select-Object -Last 2
Write-Output "--- xml inventory ---"
Get-ChildItem robot\out_cc\*.xml, robot\out_cc_legacy54\*.xml | Select-Object FullName, Length
Write-Output "--- armature / forcerange check ---"
Select-String -Path robot\out_cc\rm_vehicle_cc.xml -Pattern 'armature=.0\.0158','forcerange=.-40 40' -Encoding UTF8 | Measure-Object | ForEach-Object { "honest: matched $($_.Count) lines" }
Select-String -Path robot\out_cc_legacy54\rm_vehicle_cc.xml -Pattern 'armature=.0\.035','forcerange=.-54 54' -Encoding UTF8 | Measure-Object | ForEach-Object { "legacy: matched $($_.Count) lines" }
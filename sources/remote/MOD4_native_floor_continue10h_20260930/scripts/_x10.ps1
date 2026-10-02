$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
Write-Output '================ scene_cc.xml (verbatim) ================'
Get-Content robot\out_cc\scene_cc.xml
Write-Output '================ diagnostics ================'
.venv\Scripts\python.exe scripts\diag_render.py
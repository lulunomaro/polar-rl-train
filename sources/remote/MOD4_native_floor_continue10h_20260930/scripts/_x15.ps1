$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
.venv\Scripts\python.exe scripts\install_cc_assets.py 2>&1 | Select-String -Pattern 'installed'
Write-Output ("GPU before: " + (nvidia-smi --query-gpu=memory.used --format=csv,noheader))
Set-Location D:\claude2\fangzhen
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:PIP_CACHE_DIR='D:\pipcache'
$env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
Write-Output "WAIT_V10 $(Get-Date -Format HH:mm:ss)"
while (Get-Process -Id 11104 -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 10 }
Write-Output "V10_EXITED $(Get-Date -Format HH:mm:ss)"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
Write-Output "--- install honest plant into training package ---"
.venv\Scripts\python.exe scripts\install_cc_assets.py 2>&1 | Select-Object -Last 8
Write-Output "--- clean scaling sweep (nothing else on the GPU) ---"
Write-Output "### base 1024 (what v3-v10 used)"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 1024 --steps 150 2>&1 | Select-String -Pattern 'RESULT|ms/policy|contacts:|Error|memory' | ForEach-Object { $_.Line }
Write-Output "### 4096"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 4096 --steps 150 2>&1 | Select-String -Pattern 'RESULT|ms/policy|contacts:|Error|memory' | ForEach-Object { $_.Line }
Write-Output "### 4096 + solver iterations 30"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 4096 --steps 150 --iterations 30 --ls-iterations 20 --tolerance 1e-6 2>&1 | Select-String -Pattern 'RESULT|ms/policy|contacts:|Error|memory' | ForEach-Object { $_.Line }
Write-Output "### 8192 + iterations 30 + smaller buffers"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 8192 --steps 120 --iterations 30 --ls-iterations 20 --tolerance 1e-6 --njmax 320 --nconmax 48 2>&1 | Select-String -Pattern 'RESULT|ms/policy|contacts:|Error|memory' | ForEach-Object { $_.Line }
Write-Output "SCALE_DONE $(Get-Date -Format HH:mm:ss)"
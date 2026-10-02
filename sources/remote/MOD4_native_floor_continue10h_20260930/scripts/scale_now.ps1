Set-Location D:\claude2\fangzhen
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
Write-Output "### 1024"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 1024 --steps 150 2>&1 | Select-String -Pattern 'RESULT|ms/policy|nvidia-smi memory|Error' | ForEach-Object { "   " + $_.Line }
Write-Output "### 2048"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 2048 --steps 150 2>&1 | Select-String -Pattern 'RESULT|ms/policy|nvidia-smi memory|Error' | ForEach-Object { "   " + $_.Line }
Write-Output "### 4096"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 4096 --steps 150 2>&1 | Select-String -Pattern 'RESULT|ms/policy|nvidia-smi memory|Error' | ForEach-Object { "   " + $_.Line }
Write-Output "### 4096 it=30"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 4096 --steps 150 --iterations 30 --ls-iterations 20 --tolerance 1e-6 2>&1 | Select-String -Pattern 'RESULT|ms/policy|nvidia-smi memory|Error' | ForEach-Object { "   " + $_.Line }
Write-Output "### 8192 it=30 njmax320"
.venv-train\Scripts\python.exe scripts\gpu_scale.py --envs 8192 --steps 120 --iterations 30 --ls-iterations 20 --tolerance 1e-6 --njmax 320 --nconmax 48 2>&1 | Select-String -Pattern 'RESULT|ms/policy|nvidia-smi memory|Error|memory' | ForEach-Object { "   " + $_.Line }
Write-Output "SWEEP_DONE"
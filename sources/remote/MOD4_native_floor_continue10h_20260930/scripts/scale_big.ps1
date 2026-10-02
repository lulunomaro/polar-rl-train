Set-Location D:\claude2\fangzhen
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
foreach($n in '8192','12288','14336'){
  Write-Output "### FIELD envs=$n"
  .venv-train\Scripts\python.exe scripts\gpu_scale.py --task RMVehicle-CC-Field-v0 --envs $n --steps 80 2>&1 |
    Select-String -Pattern 'RESULT|ms/policy|VRAM|Error|out of memory|CUDA|Trace' | ForEach-Object { "   " + $_.Line }
}
Write-Output "PROBE_DONE"
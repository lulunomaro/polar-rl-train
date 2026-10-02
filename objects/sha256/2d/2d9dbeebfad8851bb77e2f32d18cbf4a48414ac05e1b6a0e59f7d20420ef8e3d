Set-Location D:\claude2\fangzhen
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
foreach($n in '4096','8192'){
  Write-Output "### FIELD task, envs=$n"
  .venv-train\Scripts\python.exe scripts\gpu_scale.py --task RMVehicle-CC-Field-v0 --envs $n --steps 100 2>&1 |
    Select-String -Pattern 'RESULT|ms/policy|VRAM|actuator |sim    :|Error|memory|Trace' | ForEach-Object { "   " + $_.Line }
}
Write-Output "FIELD_SWEEP_DONE"
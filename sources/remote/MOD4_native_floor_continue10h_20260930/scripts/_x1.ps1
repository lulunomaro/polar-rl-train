$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='legacy54'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v10\2026-09-04_21-24-03\model_7498.pt'
Write-Output "--- export v10 -> ONNX ---"
& $py D:\claude2\fangzhen\train\export_onnx.py --task RMVehicle-CC-Field-v0 --checkpoint $ck --out D:\claude2\fangzhen\train\deploy\rm_cc_v10_final.onnx 2>&1 | Select-String -Pattern 'onnx|obs|action|Saved|saved|Error|Trace|steps' | Select-Object -Last 12
Get-Item D:\claude2\fangzhen\train\deploy\rm_cc_v10_final.onnx -ErrorAction SilentlyContinue | Select-Object Name,Length
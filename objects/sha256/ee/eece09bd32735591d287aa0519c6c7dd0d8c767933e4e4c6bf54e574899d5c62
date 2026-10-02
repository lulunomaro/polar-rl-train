$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
Write-Output "--- onnx_play.py args ---"
Select-String -Path sim_mujoco\onnx_play.py -Pattern 'add_argument' -Encoding UTF8 | ForEach-Object { "  " + $_.Line.Trim() }
Write-Output "--- verify_skills_mujoco.py args + video hooks ---"
Select-String -Path scripts\verify_skills_mujoco.py -Pattern 'add_argument|Renderer|imageio|def main|scene_field|--onnx|--video' -Encoding UTF8 | ForEach-Object { "  L$($_.LineNumber): " + $_.Line.Trim().Substring(0,[Math]::Min(110,$_.Line.Trim().Length)) }
Write-Output "--- export_onnx.py args ---"
Select-String -Path train\export_onnx.py -Pattern 'add_argument' -Encoding UTF8 | ForEach-Object { "  " + $_.Line.Trim() }
Write-Output "--- deps ---"
.venv\Scripts\python.exe -c "import importlib
for m in ('imageio','imageio_ffmpeg','cv2','onnxruntime','mujoco'):
    try:
        importlib.import_module(m); print(' ', m, 'OK')
    except Exception as e: print(' ', m, 'MISSING', type(e).__name__)"
Write-Output "--- existing onnx ---"
Get-ChildItem train\deploy\*.onnx | Select-Object Name,Length,LastWriteTime
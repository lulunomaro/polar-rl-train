@echo off
setlocal
cd /d "%~dp0"
if not exist ".runtime\Scripts\python.exe" py -3 -m venv .runtime
if errorlevel 1 goto :failed
.runtime\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :failed
echo Runtime ready. Double-click ONNX_MuJoCo_Launcher.bat.
pause
exit /b 0
:failed
echo Installation failed. Check Python 3 and network access.
pause
exit /b 1

@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
py -3.12 -m venv ".venv"
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -c "import tkinter,mujoco,onnxruntime,numpy;print('Environment OK')"
if errorlevel 1 goto failed
echo Setup complete. Run START_WINDOWS.bat.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.12 x64 with Tcl/Tk and launcher, then retry.
pause
exit /b 1

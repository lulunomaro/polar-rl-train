@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo Launching MOD4v3 Pure-RL COD Forward Leap ^& Jump-Onto-Step Playground...
"D:\claude2\fangzhen\.venv\Scripts\python.exe" "%~dp0play_rl_forward_leap_wasd.py" %*
endlocal

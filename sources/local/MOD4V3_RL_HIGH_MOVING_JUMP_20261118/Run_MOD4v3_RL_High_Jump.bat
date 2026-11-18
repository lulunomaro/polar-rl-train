@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo Launching MOD4v3 Pure-RL Deep-Crouch High Jump ^& Moving Multi-Jump Playground...
"D:\claude2\fangzhen\.venv\Scripts\python.exe" "%~dp0play_rl_high_jump_wasd.py" %*
endlocal

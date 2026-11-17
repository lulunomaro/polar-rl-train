@echo off
chcp 65001 >nul
title MOD4v3 Deep-Crouch High Jump & Moving Jump (c874)
set "PY=D:\claude2\fangzhen\.venv\Scripts\python.exe"
set "HERE=%~dp0"
echo Starting MOD4v3 High-Jump + Moving-Jump WASD Playground (Base Policy: c874a1af)...
"%PY%" -X utf8 -B "%HERE%play_high_jump_wasd.py" %*
if errorlevel 1 (
    echo.
    echo [ERROR] Player exited with code %errorlevel%.
    pause
)

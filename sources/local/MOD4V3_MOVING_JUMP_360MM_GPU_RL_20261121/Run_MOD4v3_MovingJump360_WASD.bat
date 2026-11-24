@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONDONTWRITEBYTECODE=1"
set "JUMP360_PY=%~dp0..\..\..\..\.venv\Scripts\python.exe"
if exist "%JUMP360_PY%" (
    "%JUMP360_PY%" -B "%~dp0play_moving_jump360.py" %*
) else (
    python -B "%~dp0play_moving_jump360.py" %*
)
exit /b %ERRORLEVEL%

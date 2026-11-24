@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0..\.."
set "PYTHONDONTWRITEBYTECODE=1"
set "JUMP380_PY=%CD%\..\..\..\..\.venv\Scripts\python.exe"
if exist "%JUMP380_PY%" (
    "%JUMP380_PY%" -B jump380_r10_play.py %*
) else (
    python -B jump380_r10_play.py %*
)
exit /b %ERRORLEVEL%

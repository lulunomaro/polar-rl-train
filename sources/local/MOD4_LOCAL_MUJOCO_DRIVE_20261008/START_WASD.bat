@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
"%~dp0..\.venv\Scripts\python.exe" "%~dp0drive_latest.py"
if errorlevel 1 pause

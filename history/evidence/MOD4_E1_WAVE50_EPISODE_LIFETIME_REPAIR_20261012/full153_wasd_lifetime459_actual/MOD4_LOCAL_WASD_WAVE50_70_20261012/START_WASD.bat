@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
"%~dp0..\.venv\Scripts\pythonw.exe" "%~dp0drive_series.py"

@echo off
chcp 65001 >nul
cd /d "%~dp0"
"%~dp0..\.venv\Scripts\python.exe" -B -X utf8 "%~dp0drive_rm7v7_moe.py"
if errorlevel 1 pause

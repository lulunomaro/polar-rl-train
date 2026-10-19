@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run SETUP_WINDOWS.bat first.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -B -X utf8 "player\drive_rm7v7_moe.py"
if errorlevel 1 pause

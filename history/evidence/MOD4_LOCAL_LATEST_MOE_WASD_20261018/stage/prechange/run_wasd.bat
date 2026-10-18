@echo off
setlocal
cd /d "%~dp0"
if exist ".runtime\Scripts\python.exe" set "PYTHON=.runtime\Scripts\python.exe"
if not defined PYTHON if exist "..\.venv\Scripts\python.exe" set "PYTHON=..\.venv\Scripts\python.exe"
if not defined PYTHON set "PYTHON=python"
"%PYTHON%" drive_wasd.py
if errorlevel 1 pause

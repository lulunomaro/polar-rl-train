@echo off
setlocal
cd /d "%~dp0"
if exist ".runtime\Scripts\python.exe" set "MOD4PY=.runtime\Scripts\python.exe"
if not defined MOD4PY if exist "..\.venv\Scripts\python.exe" set "MOD4PY=..\.venv\Scripts\python.exe"
if not defined MOD4PY set "MOD4PY=python"
"%MOD4PY%" -B -X utf8 drive_wasd.py --policy policies/imported/mod4_latest_moe_20261018.onnx --yaw-assist 0
if errorlevel 1 pause

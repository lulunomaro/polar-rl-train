@echo off
setlocal
set "PY=%~dp0..\..\..\..\.venv\Scripts\python.exe"
"%PY%" -X utf8 -B "%~dp0play_e0_drive.py" --manifest "%~dp0SELECTED_E0.json" %*

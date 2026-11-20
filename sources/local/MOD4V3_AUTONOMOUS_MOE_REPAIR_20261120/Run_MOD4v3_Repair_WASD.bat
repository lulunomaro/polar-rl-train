@echo off
setlocal
set "REPAIR_DIR=%~dp0"
set "PYTHON=%REPAIR_DIR%..\..\..\..\.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo MOD4v3 Python environment missing: %PYTHON%
  pause
  exit /b 1
)
set "OMP_NUM_THREADS=1"
set "OPENBLAS_NUM_THREADS=1"
set "MKL_NUM_THREADS=1"
set "MUJOCO_GL=glfw"
"%PYTHON%" -X utf8 -B "%REPAIR_DIR%play_repaired.py" --candidate "%REPAIR_DIR%CANDIDATE.json" %*
if errorlevel 1 pause

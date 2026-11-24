@echo off
setlocal
set "FSM_DIR=%~dp0"
set "PYTHON=%FSM_DIR%..\..\..\..\.venv\Scripts\python.exe"
set "OMP_NUM_THREADS=1"
set "OPENBLAS_NUM_THREADS=1"
set "MKL_NUM_THREADS=1"
set "MUJOCO_GL=glfw"
set "PYTHONDONTWRITEBYTECODE=1"
set "CUDA_VISIBLE_DEVICES=-1"
cd /d "%FSM_DIR%"
"%PYTHON%" -X utf8 -B "%FSM_DIR%play_manual_fsm_wasd.py" %*
set "FSM_EXIT=%ERRORLEVEL%"
if not "%FSM_EXIT%"=="0" if "%~1"=="" pause
exit /b %FSM_EXIT%

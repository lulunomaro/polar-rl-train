@echo off
setlocal
set "STAGE1_DIR=%~dp0"
set "PYTHON=%STAGE1_DIR%..\..\..\..\.venv\Scripts\python.exe"
set "OMP_NUM_THREADS=1"
set "OPENBLAS_NUM_THREADS=1"
set "MKL_NUM_THREADS=1"
set "MUJOCO_GL=glfw"
set "CUDA_VISIBLE_DEVICES=-1"
"%PYTHON%" -X utf8 -B "%STAGE1_DIR%play_unified_soft_moe.py" %*
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" if "%~1"=="" pause
exit /b %EXITCODE%

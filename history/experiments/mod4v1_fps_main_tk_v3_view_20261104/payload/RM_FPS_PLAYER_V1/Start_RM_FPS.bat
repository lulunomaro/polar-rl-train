@echo off
chcp 65001 >nul
setlocal
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
"C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe" -B -X utf8 "%~dp0player_main_tk_v1.py" --scene latest_rm %*
if errorlevel 1 pause
endlocal

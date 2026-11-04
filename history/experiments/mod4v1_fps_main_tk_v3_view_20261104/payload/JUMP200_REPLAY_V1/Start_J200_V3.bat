@echo off
chcp 65001 >nul
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
cd /d "%~dp0.."
"C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe" -B -X utf8 "%~dp0play.py" --case attitude --rate 0.5 --start 2.4 --follow %*
if errorlevel 1 pause

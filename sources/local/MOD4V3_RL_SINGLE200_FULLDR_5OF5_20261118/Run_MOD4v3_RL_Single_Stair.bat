@echo off
chcp 65001 >nul
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
echo Starting MOD4v3 Pure-Neural RL Single-Step (200mm) Interactive Playground...
"D:\claude2\fangzhen\.venv\Scripts\python.exe" -X utf8 "%~dp0play_rl_single_stair_wasd.py"
pause

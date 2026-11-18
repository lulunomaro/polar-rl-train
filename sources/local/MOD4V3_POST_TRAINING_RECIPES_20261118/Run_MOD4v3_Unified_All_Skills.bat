@echo off
chcp 65001 >nul
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
echo Starting MOD4v3 Unified 3-Expert MoE Playground (E0 Locomotion + E1 Stair Climb + E2 COD Forward Leap / Step Jump)...
"D:\claude2\fangzhen\.venv\Scripts\python.exe" -X utf8 "%~dp0scripts\play_unified_all_skills_wasd.py"
pause

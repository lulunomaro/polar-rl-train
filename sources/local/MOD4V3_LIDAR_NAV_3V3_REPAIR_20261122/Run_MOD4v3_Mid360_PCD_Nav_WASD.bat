@echo off
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1
if exist "%~dp0..\..\..\..\.venv\Scripts\python.exe" (
    "%~dp0..\..\..\..\.venv\Scripts\python.exe" -B "%~dp0play_lidar_nav_wasd.py" --pcd-prior --close-stale %*
) else (
    python -B "%~dp0play_lidar_nav_wasd.py" --pcd-prior --close-stale %*
)
if errorlevel 1 pause

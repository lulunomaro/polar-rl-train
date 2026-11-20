@echo off
setlocal
call "%~dp0..\MOD4V3_AUTONOMOUS_MOE_REPAIR_20261120\Run_MOD4v3_Repair_WASD.bat" --proving-ground %*
exit /b %errorlevel%

@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  start "MOD4 ONNX Launcher" powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0launcher.ps1"
) else (
  start "MOD4 ONNX Launcher" powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0launcher.ps1" -IncomingOnnx "%~1"
)

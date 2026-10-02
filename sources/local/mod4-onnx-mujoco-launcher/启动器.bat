@echo off
if "%~1"=="" (
  call "%~dp0ONNX_MuJoCo_Launcher.bat"
) else (
  call "%~dp0ONNX_MuJoCo_Launcher.bat" "%~1"
)

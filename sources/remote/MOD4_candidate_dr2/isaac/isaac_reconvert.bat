@echo off
rem Re-convert robot/out_cc_linkfix/rm_vehicle_cc.xml -> isaac/assets/rm_vehicle_cc
cd /d D:\claude2\fangzhen
.venv-isaaclab\Scripts\python.exe isaac\convert_robot.py

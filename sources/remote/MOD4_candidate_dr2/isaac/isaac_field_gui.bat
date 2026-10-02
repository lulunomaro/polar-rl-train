@echo off
rem Isaac Lab viewport: 24 robots on the RMUC2026 7v7 field (measured from RMUC2026_V2.0.0.stp)
cd /d D:\claude2\fangzhen
.venv-isaaclab\Scripts\python.exe isaac\preview_robots.py ^
  --usd isaac\assets\rm_vehicle_serial\rm_vehicle_serial.usda --serial --field --env-x0 -6 ^
  --knee-kp 600 --knee-kd 60 --kp 600 --kd 60 --num_envs 24 --steps 80 --balance 0 --iters 16 ^
  --viz kit --hold

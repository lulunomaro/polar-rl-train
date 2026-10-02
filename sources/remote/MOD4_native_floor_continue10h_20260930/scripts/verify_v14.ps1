Set-Location D:\claude2\fangzhen\train
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'
$env:RM_MOTOR='dm8009'; $env:CC_MOTOR='dm8009'
$env:RM_WHEEL_SCALE='55.0'; $env:RM_WZ_MAX='14.0'
$ck = "logs/rsl_rl/rm_cc_v14/2026-09-05_19-27-33/model_9495.pt"
& D:\claude2\fangzhen\.venv-train\Scripts\python.exe verify_skills.py --task RMVehicle-CC-Skills-v0 --checkpoint $ck --num-envs 64 --only gyro --out deploy/skills_v14_flat_gyro.json 2>&1
"GYRO_EXIT $LASTEXITCODE"
& D:\claude2\fangzhen\.venv-train\Scripts\python.exe verify_skills.py --task RMVehicle-CC-Skills-v0 --checkpoint $ck --num-envs 64 --only jump --out deploy/skills_v14_flat_jump.json 2>&1
"JUMP_EXIT $LASTEXITCODE"
& D:\claude2\fangzhen\.venv-train\Scripts\python.exe verify_skills.py --task RMVehicle-CC-Field-v0 --checkpoint $ck --num-envs 64 --only run --out deploy/skills_v14_field_run.json 2>&1
"RUN_EXIT $LASTEXITCODE"

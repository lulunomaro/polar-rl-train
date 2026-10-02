Set-Location D:\claude2\fangzhen\train
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:PIP_CACHE_DIR='D:\pipcache'
$env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
# --- v13 objectives: high-rate 小陀螺, deeper RMUC2026 terrain, actuator-transfer DR ---
$env:RM_WZ_MAX='14.0'        # yaw command +-14 rad/s (kinematic ceiling 17.1)
$env:RM_WHEEL_SCALE='20.0'   # wheel action scale 10 -> 20 so +-14 rad/s is reachable
$env:RM_FLAT_PROP='0.25'     # 75% of envs spawn on 2026-map terrain (was 0.45)
$env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'
Write-Output "V13_START $(Get-Date -Format HH:mm:ss) wz=+-14 wheel_scale=20 flat=0.25 envs=10240 plant=dm8009 dr=+armature+frictionloss"
D:\claude2\fangzhen\.venv-train\Scripts\python.exe -m mjlab.scripts.train RMVehicle-CC-Field-v0 `
  --env.scene.num-envs 10240 --agent.max-iterations 700 `
  --agent.logger tensorboard --agent.experiment-name rm_cc_v13 `
  --agent.resume True --agent.load-run seed_from_v12 --agent.load-checkpoint model_8696.pt 2>&1
Write-Output "V13_EXIT $(Get-Date -Format HH:mm:ss)"
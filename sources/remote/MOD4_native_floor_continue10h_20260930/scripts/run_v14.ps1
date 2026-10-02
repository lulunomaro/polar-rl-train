Set-Location D:\claude2\fangzhen\train
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:PIP_CACHE_DIR='D:\pipcache'
$env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
# --- v14 = the CORRECTED plant (base COM 0.239 m above the axle, Izz 14x) + a 小陀螺 that can
#     actually reach high rate (wheel action unit 55 rad/s) + the RMUC2026 map curriculum.
$env:RM_WZ_MAX='14.0'        # the yaw window the curriculum is allowed to open up to
$env:RM_WZ0='4.0'            # ... and where it starts (v12's proven hold rate was 5.75)
$env:RM_WHEEL_SCALE='55.0'   # action +-1 = 55 rad/s of wheel = 14.9 rad/s of yaw
$env:RM_FLAT_PROP='0.25'     # 75% of envs spawn on 2026-map terrain
$env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'
Write-Output "V14_START $(Get-Date -Format HH:mm:ss) plant=post-baseinertia-fix wz=4->14 curriculum wheel_scale=55 wheel_kd=0.6 flat=0.25 envs=10240"
D:\claude2\fangzhen\.venv-train\Scripts\python.exe -m mjlab.scripts.train RMVehicle-CC-Field-v0 `
  --env.scene.num-envs 10240 --agent.max-iterations 800 `
  --agent.logger tensorboard --agent.experiment-name rm_cc_v14 `
  --agent.resume True --agent.load-run seed_from_v12 --agent.load-checkpoint model_8696.pt 2>&1
Write-Output "V14_EXIT $(Get-Date -Format HH:mm:ss) code $LASTEXITCODE"

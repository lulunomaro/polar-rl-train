Set-Location D:\claude2\fangzhen\train
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:PIP_CACHE_DIR='D:\pipcache'
$env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
# --- v15 = v14's plant + the two things v14 proved were missing:
#     (a) a WIDE, upright-gated yaw-tracking kernel (a plain Gaussian cannot pull the policy
#         out of its own dead zone at large errors - same trick Fudan open-sourced, see §29,
#     (b) a crash-proof yaw curriculum (tilt<12 deg AND roll/pitch rate<0.6, 3 consecutive
#         decisions), and (c) the terrain curriculum capped at the measured leg stroke.
#     The user's acceptance number: 小陀螺 2 rev/s = 12.57 rad/s.
$env:RM_WZ_MAX='14.0'; $env:RM_WZ0='5.0'      # start at what v14 demonstrably holds
$env:RM_WHEEL_SCALE='55.0'
$env:RM_GYRO_WIDE_W='1.5'; $env:RM_GYRO_BAND='6.0'   # wide triangular yaw-tracking kernel
$env:RM_TERRAIN_CAP_H='0.20'
$env:RM_FLAT_PROP='0.45'   # v13/v14 used 0.25 and the RUN skill collapsed on the map (0.14-0.44 m/s
$env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'
$SEEDDIR = "logs/rsl_rl/rm_cc_v15/seed_from_v14"
$CKPT = (Get-ChildItem "D:\claude2\fangzhen\train\$SEEDDIR" -Filter *.pt | Sort-Object LastWriteTime | Select-Object -Last 1).Name
Write-Output "V15_START $(Get-Date -Format HH:mm:ss) seed=$CKPT gyro_target=12.566 linear_w=1.5 wheel_std=0.30 terrain_cap=0.20"
D:\claude2\fangzhen\.venv-train\Scripts\python.exe -m mjlab.scripts.train RMVehicle-CC-Field-v0 `
  --env.scene.num-envs 10240 --agent.max-iterations 900 `
  --agent.logger tensorboard --agent.experiment-name rm_cc_v15 `
  --agent.resume True --agent.load-run seed_from_v14 --agent.load-checkpoint $CKPT 2>&1
Write-Output "V15_EXIT $(Get-Date -Format HH:mm:ss) code $LASTEXITCODE"

# v14's own numbers said 0.25 was too little flat ground; v11 already learned this and
# settled on 0.45. The 55% that remains is still the seven 2026-map columns.
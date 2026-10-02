Set-Location D:\claude2\fangzhen\train
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:PIP_CACHE_DIR='D:\pipcache'
$env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
# --- v16 = v15's plant + rewards, plus the two things v15 proved were still wrong:
#     (1) BOTH spin directions must hold before the yaw window widens (sign-aware curriculum),
#     (2) one skill per env per command window (v15: window hit the full +-14 and every skill
#         reward improved, while terrain_levels/mean FELL 0.275 -> 0.055 - the gyro skill was
#         starving the map skill).
$env:RM_WZ_MAX='14.0'; $env:RM_WZ0='6.0'
$env:RM_WHEEL_SCALE='55.0'
$env:RM_GYRO_WIDE_W='1.5'; $env:RM_GYRO_BAND='6.0'
$env:RM_SKILL_SPLIT='1'; $env:RM_SKILL_GYRO_FRAC='0.25'; $env:RM_SKILL_WZ_LOCO='2.0'
$env:RM_TERRAIN_CAP_H='0.20'
$env:RM_FLAT_PROP='0.45'
$env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'
$SEEDDIR = "logs/rsl_rl/rm_cc_v16/seed_from_v15"
$CKPT = (Get-ChildItem "D:\claude2\fangzhen\train\$SEEDDIR" -Filter *.pt | Sort-Object LastWriteTime | Select-Object -Last 1).Name
Write-Output "V16_START $(Get-Date -Format HH:mm:ss) seed=$CKPT skill_split=1 sign_aware_curriculum=1 flat=0.45 cap=0.20"
D:\claude2\fangzhen\.venv-train\Scripts\python.exe -m mjlab.scripts.train RMVehicle-CC-Field-v0 `
  --env.scene.num-envs 10240 --agent.max-iterations 900 `
  --agent.logger tensorboard --agent.experiment-name rm_cc_v16 `
  --agent.resume True --agent.load-run seed_from_v15 --agent.load-checkpoint $CKPT 2>&1
Write-Output "V16_EXIT $(Get-Date -Format HH:mm:ss) code $LASTEXITCODE"

# v17 = the link-fixed plant (relative-angle end stop + self-consistent passive ranges)
#       + the actuator-delay DR.  Seeded from v16 model_10899.  Everything else is v16
#       verbatim, so any behaviour change is attributable to those variable groups.
$ErrorActionPreference = 'Continue'
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:PIP_CACHE_DIR='D:\pipcache'
$env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
$env:RM_WZ_MAX='14.0'; $env:RM_WZ0='6.0'; $env:RM_WHEEL_SCALE='55.0'
$env:RM_GYRO_WIDE_W='1.5'; $env:RM_GYRO_BAND='6.0'
$env:RM_SKILL_SPLIT='1'; $env:RM_SKILL_GYRO_FRAC='0.25'; $env:RM_SKILL_WZ_LOCO='2.0'
$env:RM_TERRAIN_CAP_H='0.20'; $env:RM_FLAT_PROP='0.45'
$env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'
# --- v18 = v17b plus ONE new variable group: narrower velocity/heading tracking  The 0-4 ms actuator delay DR and
#     the wheel torsion/rolling friction DR are switched OFF here because bundling all
#     three (run 2026-09-06_07-07-19) collapsed the seeded policy to alive 0.18 / 180 steps.
$env:RM_DELAY_MIN_LAG='0'; $env:RM_DELAY_MAX_LAG='2'
$env:RM_LV_STD='0.35'; $env:RM_AV_STD='0.6'; $env:RM_DELAY_HOLD_PROB='0.75'
Set-Location 'D:\claude2\fangzhen\train'
$CK = (Get-ChildItem 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v17a' -Recurse -Filter 'model_*.pt' |
        Sort-Object { [int]($_.BaseName -replace 'model_','') } | Select-Object -Last 1).FullName
Write-Output ('V18_START ' + (Get-Date -Format HH:mm:ss) + ' seed=' + $CK)
& 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe' 'D:\claude2\fangzhen\scripts\seed_v15.py' --src $CK --dst-dir 'logs/rsl_rl/rm_cc_v18/seed_from_v17b' 2>&1 | Select-Object -Last 4
& 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe' -m mjlab.scripts.train RMVehicle-CC-Field-v0 --env.scene.num-envs 10240 --agent.max-iterations 900 --agent.logger tensorboard --agent.experiment-name rm_cc_v18 --agent.resume True --agent.load-run seed_from_v17b --agent.load-checkpoint (Split-Path -Leaf $CK) 2>&1
Write-Output ('V18_EXIT ' + (Get-Date -Format HH:mm:ss) + ' code ' + $LASTEXITCODE)

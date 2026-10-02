Set-Location D:\claude2\fangzhen\train
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'
$env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
$env:RM_WZ_MAX='14.0'; $env:RM_WZ0='4.0'; $env:RM_WZ_EVERY='20'; $env:RM_WZ_STEP='1.0'
$env:RM_FLAT_PROP='0.25'
$env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'
& D:\claude2\fangzhen\.venv-train\Scripts\python.exe -m mjlab.scripts.train RMVehicle-CC-Field-v0 --env.scene.num-envs 1024 --agent.max-iterations 4 --agent.experiment-name v14_smoke *>&1
Write-Output "SMOKE_EXIT $LASTEXITCODE"


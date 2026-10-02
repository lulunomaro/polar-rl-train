Set-Location D:\claude2\fangzhen\train
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'
$env:PYTHONIOENCODING='utf-8'; $env:PIP_CACHE_DIR='D:\pipcache'
$env:CC_MOTOR='dm8009'; $env:RM_MOTOR='dm8009'
$env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'; $env:RM_FLAT_PROP='0.45'
Write-Output "V12_START $(Get-Date -Format HH:mm:ss) envs=10240 jump_p=0.25 rise=0.06-0.16 plant=dm8009"
D:\claude2\fangzhen\.venv-train\Scripts\python.exe -m mjlab.scripts.train RMVehicle-CC-Field-v0 `
  --env.scene.num-envs 10240 --agent.max-iterations 700 `
  --agent.logger tensorboard --agent.experiment-name rm_cc_v12 `
  --agent.resume True --agent.load-run seed_from_v11 --agent.load-checkpoint model_7997.pt 2>&1
Write-Output "V12_EXIT $(Get-Date -Format HH:mm:ss)"
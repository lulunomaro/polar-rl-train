$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='legacy54'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v10\2026-09-04_21-24-03\model_7498.pt'
$vid = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v10\2026-09-04_21-24-03\videos\play\rl-video-step-0.mp4'
if (Test-Path $vid) { Remove-Item $vid -Force }
& $py -m mjlab.scripts.play RMVehicle-CC-Skills-v0 --checkpoint-file $ck --device cpu --num-envs 4 --viewer native --video True --video-length 400 --video-width 960 --video-height 540 > D:\claude2\fangzhen\docs\_play_cpu.log 2>&1
Write-Output "exit=$LASTEXITCODE"
if (Test-Path $vid) { Copy-Item $vid D:\claude2\fangzhen\docs\videos\v10_mjlab_skills_fixed.mp4 -Force; Write-Output ("saved " + (Get-Item D:\claude2\fangzhen\docs\videos\v10_mjlab_skills_fixed.mp4).Length + " B") } else { Write-Output 'no video'; Get-Content D:\claude2\fangzhen\docs\_play_cpu.log -Tail 8 }
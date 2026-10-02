$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='dm8009'; $env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v11\2026-09-05_00-35-08\model_7997.pt'
$vid = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v11\2026-09-05_00-35-08\videos\play\rl-video-step-0.mp4'
foreach($pair in @('flat|RMVehicle-CC-Skills-v0','map|RMVehicle-CC-Field-v0')){
  $tag = $pair.Split('|')[0]; $task = $pair.Split('|')[1]
  Write-Output "=== play $task ==="
  if (Test-Path $vid) { Remove-Item $vid -Force }
  & $py -m mjlab.scripts.play $task --checkpoint-file $ck --num-envs 4 --viewer native --video True --video-length 500 --video-width 960 --video-height 540 > "D:\claude2\fangzhen\docs\_play_$tag.log" 2>&1
  if (Test-Path $vid) {
    Copy-Item $vid "D:\claude2\fangzhen\docs\videos\v11_mjlab_$tag.mp4" -Force
    Write-Output ("   saved v11_mjlab_$tag.mp4 = " + (Get-Item "D:\claude2\fangzhen\docs\videos\v11_mjlab_$tag.mp4").Length + " B")
  } else {
    Write-Output "   no video; log tail:"; Get-Content "D:\claude2\fangzhen\docs\_play_$tag.log" -Tail 5 | ForEach-Object { "     " + $_ }
  }
}
$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='legacy54'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v10\2026-09-04_21-24-03\model_7498.pt'
$vid = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v10\2026-09-04_21-24-03\videos\play\rl-video-step-0.mp4'
foreach($pair in @(@('skills','RMVehicle-CC-Skills-v0'), @('field','RMVehicle-CC-Field-v0'))){
  $tag = $pair[0]; $task = $pair[1]
  Write-Output "=== play $task ==="
  if (Test-Path $vid) { Remove-Item $vid -Force }
  & $py -m mjlab.scripts.play $task --checkpoint-file $ck --num-envs 8 --viewer native --video True --video-length 450 --video-width 960 --video-height 540 > "D:\claude2\fangzhen\docs\_play_$tag.log" 2>&1
  if (Test-Path $vid) {
    Copy-Item $vid "D:\claude2\fangzhen\docs\videos\v10_mjlab_$tag.mp4" -Force
    $len = (Get-Item "D:\claude2\fangzhen\docs\videos\v10_mjlab_$tag.mp4").Length
    Write-Output "   saved v10_mjlab_$tag.mp4 ($len bytes)"
  } else {
    Write-Output "   NO VIDEO PRODUCED - log tail:"
    Get-Content "D:\claude2\fangzhen\docs\_play_$tag.log" -Tail 6
  }
}
Get-ChildItem D:\claude2\fangzhen\docs\videos\*.mp4 | Select-Object Name,Length
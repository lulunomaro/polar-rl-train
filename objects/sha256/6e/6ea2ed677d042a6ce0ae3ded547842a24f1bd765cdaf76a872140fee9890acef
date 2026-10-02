$env:TMP='D:\tmp'; $env:TEMP='D:\tmp'; $env:TMPDIR='D:\tmp'; $env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen\train
$env:RM_MOTOR='dm8009'; $env:RM_RISE_MIN='0.06'; $env:RM_RISE_MAX='0.16'; $env:RM_JUMP_P='0.25'
$py = 'D:\claude2\fangzhen\.venv-train\Scripts\python.exe'
$ck = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v11\2026-09-05_00-35-08\model_7997.pt'
$dir = 'D:\claude2\fangzhen\train\logs\rsl_rl\rm_cc_v11\2026-09-05_00-35-08\videos\play'
$vid = Join-Path $dir 'rl-video-step-0.mp4'
if (Test-Path $vid) { Remove-Item $vid -Force }
$p = Start-Process -FilePath $py -ArgumentList @('-m','mjlab.scripts.play','RMVehicle-CC-Field-v0','--checkpoint-file',$ck,'--num-envs','4','--viewer','native','--video','True','--video-length','450','--video-width','960','--video-height','540') -RedirectStandardOutput 'D:\claude2\fangzhen\docs\_play_map2.log' -RedirectStandardError 'D:\claude2\fangzhen\docs\_play_map2.err' -PassThru -WindowStyle Hidden
$prev = -1; $stable = 0
for ($i = 0; $i -lt 46; $i++) {
  Start-Sleep -Seconds 10
  if (Test-Path $vid) {
    $len = (Get-Item $vid).Length
    if ($len -eq $prev -and $len -gt 100000) { $stable++ ; if ($stable -ge 2) { break } } else { $stable = 0 }
    $prev = $len
  }
}
Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object { $cl=(Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine; if($cl -like '*mjlab.scripts.play*'){ Stop-Process -Id $_.Id -Force } }
Start-Sleep -Seconds 2
if (Test-Path $vid) {
  Copy-Item $vid 'D:\claude2\fangzhen\docs\videos\v11_mjlab_map.mp4' -Force
  Remove-Item $vid -Force -ErrorAction SilentlyContinue
  Write-Output ("saved v11_mjlab_map.mp4 = " + (Get-Item 'D:\claude2\fangzhen\docs\videos\v11_mjlab_map.mp4').Length + " B")
} else { Write-Output 'no map video produced'; Get-Content 'D:\claude2\fangzhen\docs\_play_map2.log' -Tail 6 }
$localTrainingRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$saveStopPath = Join-Path $localTrainingRoot 'STOP_AFTER_SAVE'
Set-Content -LiteralPath $saveStopPath -Value 'Human requested local training stop after the current PPO update and full save.' -Encoding utf8
Write-Output 'Requested full save and natural exit at the next PPO update boundary.'

$env:PYTHONIOENCODING='utf-8'
Set-Location D:\claude2\fangzhen
Write-Output "=== mjlab play/video scripts ==="
Get-ChildItem third_party\rc_mjlab\mjlab\src\mjlab\scripts -Filter *.py | Select-Object Name
Write-Output "=== play.py args ==="
Select-String -Path third_party\rc_mjlab\mjlab\src\mjlab\scripts\play.py -Pattern 'add_argument|video|render' -Encoding UTF8 | ForEach-Object { "  L$($_.LineNumber): " + $_.Line.Trim().Substring(0,[Math]::Min(120,$_.Line.Trim().Length)) }
Write-Output "=== field_cfg: terrain fractions ==="
Select-String -Path train\rmvehicle\src\rmvehicle\field_cfg.py -Pattern 'frac|flat|weight|percent|rows|def |env-overrid|environ' -Encoding UTF8 | ForEach-Object { "  L$($_.LineNumber): " + $_.Line.Trim().Substring(0,[Math]::Min(120,$_.Line.Trim().Length)) }
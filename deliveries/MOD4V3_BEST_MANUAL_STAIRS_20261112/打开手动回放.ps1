param([string]$Python = "", [switch]$Map)
if (-not $Python) {
    $localPython = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../.venv/Scripts/python.exe'))
    if (Test-Path -LiteralPath $localPython) { $Python = $localPython } else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
$scriptPath = Join-Path $PSScriptRoot 'viewer/showcase.py'
$mode = if ($Map) { 'map' } else { 'play' }
Start-Process -FilePath $Python -ArgumentList @('-X','utf8',('"'+$scriptPath+'"'),'--mode',$mode) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden

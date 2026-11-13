$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$WorkspaceRoot = Split-Path $RepoRoot -Parent
$PythonPath = Join-Path $WorkspaceRoot '.venv\Scripts\python.exe'
$EntryPath = Join-Path $PSScriptRoot 'manual_replay\replay_latest.py'
Start-Process -FilePath $PythonPath -ArgumentList @('-X','utf8','-B','-u',('"' + $EntryPath + '"')) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden

$ErrorActionPreference='Stop'
[Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false)
Add-Type -Path 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -Path (Join-Path $PSScriptRoot 'SwMassAudit.cs') -ReferencedAssemblies 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
$result=[SwMassAudit]::Read()
$destination=Join-Path $PSScriptRoot 'mass_audit_001.json'
if(Test-Path -LiteralPath $destination){throw 'Snapshot already exists'}
$result | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $destination -Encoding UTF8
Write-Output ('MASS_AUDIT_SAVED '+$destination)
$result['assembly_mass_visible'] | ConvertTo-Json -Depth 8
$result['assembly_mass_all_unsuppressed'] | ConvertTo-Json -Depth 8

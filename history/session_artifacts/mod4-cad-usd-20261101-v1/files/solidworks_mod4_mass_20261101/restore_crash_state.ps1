$ErrorActionPreference='Stop'
[Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false)
$plan=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'recovery_restore_plan.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$receipt=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'apply_materials_stage3_001.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$resultPath=Join-Path $PSScriptRoot 'recovery_restored_001.json'
$marker=Join-Path $PSScriptRoot 'recovery_restored_001.running'
if((Test-Path -LiteralPath $resultPath) -or (Test-Path -LiteralPath $marker)){throw 'Restore operation already started; inspect it instead of repeating'}
[string[]]$suppress=@($plan.changes | Where-Object {$_.before_suppression -eq 0} | ForEach-Object {$_.name})
[string[]]$files=@($receipt.parts.PSObject.Properties | ForEach-Object {$_.Name})
[string[]]$materials=@($receipt.parts.PSObject.Properties | ForEach-Object {$_.Value.material_after})
Add-Type -Path 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -Path (Join-Path $PSScriptRoot 'SwRestoreCrashState.cs') -ReferencedAssemblies 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
[IO.File]::WriteAllText($marker,[DateTime]::UtcNow.ToString('o'))
$result=[SwRestoreCrashState]::Run($plan.assembly_path,$PSScriptRoot,$suppress,$files,$materials)
$result | ConvertTo-Json -Depth 25 | Set-Content -LiteralPath $resultPath -Encoding UTF8
Write-Output ('RECOVERY_RESTORED '+$resultPath)
$result.GetEnumerator() | Where-Object {$_.Key -ne 'components_after_restore'} | ForEach-Object {[pscustomobject]@{key=$_.Key;value=$_.Value}} | ConvertTo-Json -Depth 12

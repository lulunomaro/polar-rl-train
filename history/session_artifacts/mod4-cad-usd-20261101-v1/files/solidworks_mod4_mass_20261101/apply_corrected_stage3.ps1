$ErrorActionPreference='Stop'
[Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false)
$resultPath=Join-Path $PSScriptRoot 'apply_materials_stage3_001.json'
$runningPath=Join-Path $PSScriptRoot 'apply_materials_stage3_001.running'
if((Test-Path -LiteralPath $resultPath) -or (Test-Path -LiteralPath $runningPath)){throw 'This confirmed material operation already started; inspect its result instead of repeating it.'}
$snapshot=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'inventory_before.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Add-Type -Path 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -Path (Join-Path $PSScriptRoot 'SwApplyCorrectedStage3.cs') -ReferencedAssemblies 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
[IO.File]::WriteAllText($runningPath,[DateTime]::UtcNow.ToString('o'))
$result=[SwApplyCorrectedStage3]::Run($PSScriptRoot,$snapshot.assembly_path)
$result | ConvertTo-Json -Depth 35 | Set-Content -LiteralPath $resultPath -Encoding UTF8
Write-Output ('MATERIAL_OPERATION_SAVED '+$resultPath)
Write-Output ('STATUS '+$result['status'])
foreach($p in $result['parts'].GetEnumerator()) { Write-Output ($p.Key+' '+$p.Value['material_before']+' -> '+$p.Value['material_after']+'; saved='+$p.Value['save_succeeded']) }
$result['assembly_mass_after_visible'] | ConvertTo-Json -Depth 8
$result['drivetrain_material_parts_locations'] | ConvertTo-Json -Depth 8
$result['location_components_highlighted'] | ConvertTo-Json -Depth 8

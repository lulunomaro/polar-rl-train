param([string]$Name='before')
$ErrorActionPreference='Stop'
Add-Type -Path 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -Path (Join-Path $PSScriptRoot 'SwInventory.cs') -ReferencedAssemblies 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
$result=[SwInventory]::Read()
$destination=Join-Path $PSScriptRoot ('inventory_'+$Name+'.json')
if(Test-Path -LiteralPath $destination){throw 'Inventory snapshot already exists'}
$result | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $destination -Encoding UTF8
Write-Output ('INVENTORY_SAVED '+$destination)
Write-Output ('Components='+$result['components'].Count+'; unique_models='+$result['part_properties'].Count)
$result['assembly_mass_including_hidden'] | ConvertTo-Json -Depth 8

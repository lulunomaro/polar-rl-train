# Compile-only. Never changes sealed sources, licenses, environment or board state.
$ErrorActionPreference='Stop'
$root=(Get-Item -LiteralPath $PSScriptRoot).FullName
$compiler='C:\Keil_v5\ARM\ARMCLANG\bin\armclang.exe'
$fromelf='C:\Keil_v5\ARM\ARMCLANG\bin\fromelf.exe'
if (-not (Test-Path -LiteralPath $compiler -PathType Leaf)) { throw 'Exact user-provided ARM compiler path is absent' }
$events=@()
function Invoke-Recorded([string]$Phase,[string]$Target,[string]$Exe,[string[]]$Arguments,[string]$Log) {
  if (Test-Path -LiteralPath $Log) { throw "Preserve prior log: $Log" }
  $code=-999
  try {
    & $Exe @Arguments 2>&1 | Out-File -LiteralPath $Log -Encoding utf8
    $code=$LASTEXITCODE
  } catch {
    $_ | Out-File -LiteralPath $Log -Encoding utf8 -Append
    $exitProperty=$_.Exception.PSObject.Properties['ExitCode']
    if($null -ne $exitProperty) { $code=[int]$exitProperty.Value }
  }
  "exit_code=$code" | Add-Content -LiteralPath $Log -Encoding utf8
  [pscustomobject]@{phase=$Phase;target=$Target;executable=$Exe;arguments=$Arguments;log=$Log;exit_code=$code}
}
$targets=@(
  [pscustomobject]@{id='cortex_m4_sp_hard';cpu='cortex-m4';fpu='fpv4-sp-d16'},
  [pscustomobject]@{id='cortex_m7_sp_hard';cpu='cortex-m7';fpu='fpv5-sp-d16'}
)
$sources=@(
  [pscustomobject]@{id='active_box_qp';path=(Resolve-Path -LiteralPath (Join-Path $root 'active_box_qp.c')).Path}
)
$sourceHashes=@()
foreach($source in $sources) {
  $item=Get-Item -LiteralPath $source.path
  $sourceHashes += [pscustomobject]@{id=$source.id;path=$source.path;bytes=$item.Length;sha256=(Get-FileHash -LiteralPath $source.path -Algorithm SHA256).Hash.ToLowerInvariant()}
}
$objects=@()
foreach($target in $targets) {
  $dir=Join-Path $root $target.id
  New-Item -ItemType Directory -Path $dir -Force | Out-Null
  $flags=@('--target=arm-arm-none-eabi',"-mcpu=$($target.cpu)","-mfpu=$($target.fpu)",'-mfloat-abi=hard','-mthumb','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off')
  $macroArgs=$flags+@('-dM','-E',(Join-Path $root 'target_probe.c'))
  $events += Invoke-Recorded 'preprocessor_target_macros' $target.id $compiler $macroArgs (Join-Path $dir 'target_macros_01.log')
  foreach($source in $sources) {
    $object=Join-Path $dir ($source.id+'.o')
    if(Test-Path -LiteralPath $object) { throw "Preserve existing object rather than overwrite: $object" }
    $argsForCompile=$flags+@('-c',$source.path,'-o',$object)
    $event=Invoke-Recorded 'object_compile_only' $target.id $compiler $argsForCompile (Join-Path $dir ($source.id+'_compile_01.log'))
    $events += $event
    $present=Test-Path -LiteralPath $object -PathType Leaf
    $bytes=0;$digest=$null
    if($present) { $bytes=(Get-Item -LiteralPath $object).Length;$digest=(Get-FileHash -LiteralPath $object -Algorithm SHA256).Hash.ToLowerInvariant() }
    $objects += [pscustomobject]@{source_id=$source.id;source=$source.path;target=$target.id;cpu=$target.cpu;fpu=$target.fpu;abi='hard';object=$object;compile_exit=$event.exit_code;present=$present;bytes=$bytes;sha256=$digest}
    if($event.exit_code -eq 0 -and $present -and (Test-Path -LiteralPath $fromelf -PathType Leaf)) {
      $events += Invoke-Recorded 'fromelf_text_verbose_headers' $target.id $fromelf @('--text','-v',$object) (Join-Path $dir ($source.id+'_fromelf_01.log'))
    }
  }
}
$metadata=[pscustomobject]@{
  scope='AB3_ACTIVE_BOUND_QP_NEW_STAGE_COMPILE_ONLY_NOT_ROBOT_MPC_OR_RUNTIME';compiler=$compiler;fromelf_exact_path=$fromelf;
  prior_version_probe=[pscustomobject]@{executable=$compiler;arguments=@('--version');log=(Join-Path $root 'armclang_version_01.log');exit_code=0};
  prior_fromelf_help=[pscustomobject]@{executable=$fromelf;arguments=@('--help');log=(Join-Path $root 'fromelf_help_01.log');exit_code=0};
  sources=$sourceHashes;targets=$targets;commands=$events;objects=$objects;
  no_armcc_or_link_or_bin_or_runtime_or_license_change=$true
}
$metaPath=Join-Path $root 'BUILD_RECEIPT.json'
if(Test-Path -LiteralPath $metaPath) { throw 'Preserve original build receipt rather than overwrite' }
$metadata | ConvertTo-Json -Depth 12 | Out-File -LiteralPath $metaPath -Encoding utf8
$compiled=@($objects | Where-Object {$_.compile_exit -eq 0 -and $_.present}).Count
$failed=@($events | Where-Object {$_.exit_code -ne 0}).Count
Write-Output "ARM_OBJECT_BUILD compiled_objects=$compiled total_objects=$($objects.Count) failed_command_events=$failed"
if($failed -ne 0){exit 1}
exit 0

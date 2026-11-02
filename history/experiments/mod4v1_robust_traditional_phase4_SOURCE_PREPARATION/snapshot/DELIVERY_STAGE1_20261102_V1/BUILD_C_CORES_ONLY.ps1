param([string]$CC="gcc",[string]$OutputName="build_core_only")
$ErrorActionPreference="Stop"
$root=$PSScriptRoot
$dest=Join-Path $root $OutputName
if(Test-Path -LiteralPath $dest){throw "Choose a new output directory; preserve existing artifacts."}
New-Item -ItemType Directory -Path $dest | Out-Null
$sources=@(
"SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.c",
"SPR_AUDIT/portable_control_v3_current/pc3_estimator.c",
"SPR_AUDIT/portable_control_v3_current/pc3_controller.c",
"SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c",
"SPR_AUDIT/ACTIVE_BOX_QP_V3/active_box_qp.c",
"SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c",
"SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_model.c",
"SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.c",
"SPR_AUDIT/portable_spin_h2_v1/sh2_controller.c",
"SPR_AUDIT/portable_spin_h2_v1/sh2_pipeline.c"
)
foreach($relative in $sources){
 $inputPath=Join-Path $root $relative
 $outputPath=Join-Path $dest ((Split-Path $relative -Leaf)+".o")
 & $CC -std=c99 -O2 -Wall -Wextra -Werror -pedantic -Wvla -fno-fast-math -ffp-contract=off -c $inputPath -o $outputPath
 if($LASTEXITCODE -ne 0){throw "Compilation failed: $relative"}
}
Write-Output "Host objects only. No firmware, BSP, actuator I/O or hardware qualification."

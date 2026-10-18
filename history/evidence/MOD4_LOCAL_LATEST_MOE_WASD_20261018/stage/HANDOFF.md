# Latest local manual MoE player

User request: bring the latest checkpoint mixture into the prior local WASD player
so they can drive and request jumps. No training/task/budget/controller changes.

Player: `C:/Users/lulu/Desktop/claude/mjcf/mod4-onnx-mujoco-launcher`
Launch: `run_latest_moe.bat` (also the normal launcher selects newest imported ONNX).
Current ONNX: `policies/imported/mod4_latest_moe_20261018.onnx`, SHA
`02a04afcc32a22b6f72cc67357d60f3ae66ab112e9297aaa2fb7ac7dacc5607f`, 1047240 B.
Exact full checkpoint paths/sizes/SHAs are in its adjacent JSON and export report.

Latest *closed, completely collected* expert sources at integration time:
H1 c3904f14 / 73 updates / Adam653880;
E2 b7415bba / 240 updates / Adam681220;
E3 dc55e041 / 98 updates / Adam663420. Fourth hour was still running remotely;
no intermediate production checkpoint was downloaded/audited and no remote SSH occurred.
This local task does not replace continued three-GPU hourly training.

Ordinary driving uses the unchanged gate148 argmax between its original byte-exact
E0 and W35 experts. Manual public jump/recovery requests use complete latest H1/E3
actions. Local spin selector mode6 dispatches latest E2 after rewriting mode to normal
for that expert. This is not a newly trained five-way selector. No parameter averaging,
action blending, gate retraining, terrain-ID routing, yaw correction, or external force
is used by default. Old models and player source snapshots are retained.

G starts/pauses, WASD adjusts driving commands, J requests mode4 for 80 controls,
K selects recovery, Z/B selects +/-4 spin, N or X returns to ordinary driving,
R resets. The player starts paused. An initial J first runs 100 normal controls.
P and Y remain existing optional user test controls; neither is enabled by default.

Final runtime check: 1000 actual MuJoCo observation rows across six scenarios,
Torch/ONNX clipped-action maximum error 8.58306884765625e-06 (bound1e-4), finite
simulation, zero Viewer key conflicts. Observed body-height rise in jump scenario,
but no strict takeoff/landing/recovery qualification is inferred. MuJoCo differs from
the training PhysX backend, uses the existing local arena and hardware adapter, and
does not reproduce full20k DR, stochastic actions, actuator/sensor history or SDK physics.
Source weights and graph action order are exact; physical skill transfer is not claimed.

Actual visible responding MuJoCo window and process creation/argv are recorded in
LOCAL_PLAYER_ACTUAL_WINDOW_CIM_VERIFIED.json. Venv launcher PID is a shim; the child
Python owns the window. These PIDs are snapshots, not permanent identities.

All observed setup/export/reader errors, preexisting dirty player source, symbolic
shape graph and report-writing defects are retained or explicitly described. No old
failure was relabeled. The player local Git repository has no remote, so this stage
captures its source and reports in polar-rl-train. All model binaries remain external
with actual paths/sizes/SHAs. Original player uncommitted changes are not committed
in its own repository as if authored here.

The current fourth-hour remote originalwriter remains174112; its hour closing and
continuation follow F/V20 work order. This local player is not a finite transport
collector and does not reserve210/72/249. It can remain open while training continues.

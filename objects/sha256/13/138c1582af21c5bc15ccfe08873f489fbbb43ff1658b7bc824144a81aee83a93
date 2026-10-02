# MOD4 ONNX to MuJoCo Launcher

Windows launcher and runtime adapter for importing a RoboMaster MOD4 policy exported from Isaac Lab and driving it in MuJoCo.

This public repository contains source code only. Robot meshes, MJCF models, ONNX checkpoints, training reports, and remote `.pt` checkpoints are deliberately excluded. Put an authorized delivery in this layout before running:

```text
model/
  rm_training_arena.xml
  rm_training_arena_headless.xml
  assets/*.stl
policies/
  POLICY.onnx
  POLICY.json        # optional but recommended
```

The supplied MOD4 adapter accepts the original policy and the sequence policy contracts:

- original: `observation` `[batch,35]` -> `action` `[batch,6]`;
- sequence: `obs_history` `[batch,175]` -> `actions` `[batch,6]`;
- the sequence input is five 35-D frames flattened in Isaac Lab's **term-major** order;
- action order: left crank, left hip, right crank, right hip, left wheel, right wheel;
- MJCF: 6 actuators and at least 10 equality constraints, with the body, joint, actuator, sensor, and closure-site names used by `sim_runtime.py`.

It fails before launch when the ONNX shape, node names, history semantics, hash metadata, actuator count, or equality count does not match. Policy switching resets and reseeds the history buffer so observations from different contracts are never mixed. A validation PASS proves interface and topology compatibility; it does not prove policy quality or sim-to-real robustness.

## Windows use

1. Install Python 3, then double-click `install_runtime.bat`.
2. Double-click `ONNX_MuJoCo_Launcher.bat` or `启动器.bat`.
3. Import an ONNX, select a test location, and start MuJoCo. The new independent
   driver window opens with speed, posture, loop residuals and a live speed curve.

The launcher starts raw policy playback with yaw assist **off**. Enabling the
checkbox adds feedback to the wheel targets; the driver window labels this
explicitly. Results with assist enabled do not measure the raw policy's ability.

Select a matching controller JSON with the new button, or pass `--runtime-config`
on the command line. `runtime_profile.example.json` shows the **original adapter's**
parameters (2500/10 leg PD); it is not a profile for the recent 60/2 checkpoint.
Use the gains, action scales, motor limits, pose conventions and MJCF validated
for the selected policy. Matching the ONNX dimensions alone cannot establish this.

The launcher copies imported policies to `policies/imported/`; that directory is ignored by Git.

## Independent driver window

| Key / action | Behavior |
|---|---|
| Hold W / S | Forward / reverse; release to stop the velocity command |
| Forward / reverse buttons | Continuous command until Stop |
| Speed slider | 0.1–1.5 m/s; command ramps at 0.6 m/s² |
| X / Space | Ramp the velocity command to zero |
| R | Explicit reset; clears a frozen failure |
| P | Pause / resume physical stepping |
| Hold A / D | Turn in ONNX + MuJoCo mode |
| Mouse in simulation window | Inspect the robot and change the camera |

Vehicle keys are handled **only in the driver window**. MuJoCo keeps its own
Viewer shortcuts; the new mode registers no Viewer vehicle-key callback.
Losing focus while holding a drive key stops the command. Missing command
heartbeats ramp to zero after two seconds. Pause freezes physics, rather than
merely setting a zero speed command. A closure/mimic fault stays visible until R;
the player does not silently reset or swap policies.

Each launch has isolated command, telemetry and log files under `.playback/`.
One panel is allowed per checkout. The launcher Stop button requests graceful
shutdown of that local session; it does not kill training or unrelated processes.
Closing the driver window shuts down only its own replay workers. Closing the
simulation window alone leaves the panel available to inspect logs and exit.

The panel reports instantaneous world-Z wheel loads, root height, tilt, action
delta/d2, residuals and wall-clock playback ratio. Wheel load samples are not
contact-duty or airborne percentages. In MuJoCo mode height is root Z minus the
spawn's initial ground Z; it does not sample later terrain height. These are
live diagnostics, not a 15-second training graduation or robustness certificate.

```powershell
python control_panel.py --policy policies/POLICY.onnx --model model/rm_training_arena.xml --runtime-config runtime_profile.json
```

## Isaac physics with live MuJoCo graphics

The `Isaac 实况操控...` launcher button selects an authorized **local compatibility
bundle**, its `.pt` checkpoint and the Python interpreter with Isaac Lab installed.
It runs deterministic native Isaac PhysX and streams all body world poses to a
MuJoCo display made from the source USD. No PPO, remote SSH or training writes
occur. This mode **does not run MuJoCo physics and is not a sim2sim test**.

Install optional display dependencies in the launcher's Python environment:

```powershell
python -m pip install -r requirements-live-display.txt
python control_panel.py --engine isaac-live --bundle LOCAL_BUNDLE --isaac-python ISAAC_ENV/python.exe --checkpoint LOCAL_BUNDLE/model_N.pt
```

Required bundle layout (kept outside this public source repository):

```text
LOCAL_BUNDLE/
  model_N.pt
  DOWNLOAD_RECEIPT.json          # files: relative path -> SHA256
  run_manifest.remote.json      # env: full training RM_* configuration
  src_snapshot/robot.usd        # embedded or resolvable USD visuals
  isaac/mod4/mod4_task.py
  isaac/mod4/mod4_env.py
  isaac/mod4/...                # compatible task dependencies, contract, reset bank
```

Checkpoint, manifest and USD hashes must match the receipt. The bridge targets
the locally verified **Isaac Sim 5.1 / Isaac Lab 2.3.2 compatibility port** and the
35→256→128→64→6 ELU actor state layout; an arbitrary upstream task or a different
Lab API is not interchangeable. The source task determines hardware, spring,
contact integration and complete closed-chain reset poses. It must be compatible
with that local Isaac environment. The bridge explicitly uses the Lab 2.x
substep loop. It does not import a generic `.pt` using guessed observation semantics.

Playback is straight forward/reverse, at root-height command 0.25 m, with a
0.6 m/s² command ramp and no exploration or balance/yaw assistance. CPU is the
default for one robot; the panel reports actual playback ratio, which may be below
real time. No untrained yaw command is injected into this straight-line policy.

USD visuals are cached by SHA256 under `.playback/display/`. The cached scene has
no generalized coordinates, actuators or dynamics; mocap bodies receive live
XYZ + WXYZ poses. Body-name sets and unit quaternions are checked before display.
The adapter requires meter units and Z-up USD; it rejects a mismatched stage.

## Legacy direct Viewer controls

`python drive_wasd.py --policy ... --model ... --yaw-assist 0` retains the previous
direct Viewer control scheme below. P means a push in this legacy mode, whereas
P pauses in the new independent driver window.

| Key | Vehicle command |
|---|---|
| W / S | Increase / decrease forward speed |
| A / D | Increase left / right yaw-rate command |
| X | Stop velocity commands |
| Q / E | Lower / raise body-height command |
| T | Toggle automatic terrain mode |
| V | Cycle manual task mode |
| F | Cycle test location |
| C | Cycle policy |
| Y | Toggle MuJoCo yaw assist |
| P | Apply lateral test push |
| R | Reset at current test location |
| H | Print help |

MuJoCo keeps `Space`, `Tab`, digits, and `F1` through `F8` for pause, UI panels, visibility groups, help, profiler, sensors, fullscreen, frames, and labels. The smoke test asserts that vehicle keys do not intersect those direct Viewer bindings.

## Validation

After adding the authorized model and policy files:

```powershell
python launcher.py inspect --policy policies/POLICY.onnx --model model/rm_training_arena.xml
python smoke_test.py
```

`robustness_test.py` runs the project-specific randomized route suite. Review its assumptions before applying it to another robot or observation contract.

Source-only protocol / display tests (no private assets required):

```powershell
python -m unittest discover -s tests -v
```

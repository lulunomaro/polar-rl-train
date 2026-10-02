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
3. Import an ONNX, select a test location, and start MuJoCo.

The launcher copies imported policies to `policies/imported/`; that directory is ignored by Git.

## Controls without MuJoCo conflicts

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

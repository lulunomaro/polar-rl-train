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

本机最新 MoE：双击 `run_latest_moe.bat`，窗口初始暂停，G 开始/暂停。
普通驾驶沿用 gate148 的 E0/W35
硬分派；J 调用最新 H1 发出 0.8 秒跳跃请求，K 调用 E3 恢复，Z/B 调用
E2 自旋（+4/−4 rad/s），N 或 X 返回普通驾驶，R 复位。最新完整专家来自
2026-10-18 三卡第三小时末模型，完整来源 SHA 见 ONNX 旁置 JSON。
这是原两专家门控加手动技能分派，不是新训练的五路门控，也不混平均权重或动作。
默认关闭地形位置自动模式和航向辅助。MuJoCo 迁移能力尚未合格验证，可能摔倒；
可用 R 复位继续试操控。远端训练不受此播放器影响。
初次直接按 J 会先运行 1 秒普通站立，再发送跳跃请求。

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
| J | Jump request for 0.8 seconds |
| K / N | Recovery expert / normal driving |
| Z / B | E2 spin at +4 / -4 rad/s |

MuJoCo keeps `Space`, `Tab`, digits, and `F1` through `F8` for pause, UI panels, visibility groups, help, profiler, sensors, fullscreen, frames, and labels. The smoke test asserts that vehicle keys do not intersect those direct Viewer bindings.

## Validation

After adding the authorized model and policy files:

```powershell
python launcher.py inspect --policy policies/POLICY.onnx --model model/rm_training_arena.xml
python smoke_test.py
```

`robustness_test.py` runs the project-specific randomized route suite. Review its assumptions before applying it to another robot or observation contract.

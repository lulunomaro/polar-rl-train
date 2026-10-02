"""Interactive MuJoCo viewer for the exported MOD4 ONNX policy."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

import mujoco
import mujoco.viewer

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from sim_runtime import MODE_NAMES, Mod4Sim, RuntimeConfig  # noqa: E402


SPAWNS = (
    ("平地/狗洞", -4.0, 0.0, 0.0, 0.0),
    ("二级台阶", -2.8, -2.5, 0.0, 0.0),
    ("25度斜坡", -3.0, 2.5, 0.0, 0.0),
    ("狗洞入口", 0.25, 0.0, 0.0, 0.0),
    ("起伏路", -5.3, 4.8, 0.0, 0.0),
    ("飞坡", -4.3, -4.8, 0.0, 0.18),
    ("中心岛", 3.4, 3.1, 0.0, 0.0),
    ("416mm挡墙", 3.4, -3.0, 0.0, 0.0),
)

# MuJoCo Simulate reserves Space, Tab, digits 0..5 and F1..F7.  Keep every
# policy-control key away from that set so one keypress has exactly one effect.
CONTROL_KEYS = {
    "forward": (ord("W"), ord("w")), "reverse": (ord("S"), ord("s")),
    "left": (ord("A"), ord("a")), "right": (ord("D"), ord("d")),
    "stop": (ord("X"), ord("x")), "lower": (ord("Q"), ord("q")),
    "raise": (ord("E"), ord("e")), "auto": (ord("T"), ord("t")),
    "next_mode": (ord("V"), ord("v")), "push": (ord("P"), ord("p")),
    "reset": (ord("R"), ord("r")), "yaw_assist": (ord("Y"), ord("y")),
    "next_spawn": (ord("F"), ord("f")), "next_policy": (ord("C"), ord("c")),
    "help": (ord("H"), ord("h")),
}
MUJOCO_DIRECT_RESERVED_KEYS = {32, 258, *range(ord("0"), ord("6") + 1), *range(290, 298)}
assert not ({key for values in CONTROL_KEYS.values() for key in values} & MUJOCO_DIRECT_RESERVED_KEYS)


HELP = """
MOD4 ONNX / MuJoCo 键盘：
  W/S  前进速度 +/−0.20 m/s       A/D  转向速度 +/−0.50 rad/s
  X    急停速度指令               Q/E  车身高度 −/+ 10 mm
  T    自动地形模式开关           V    循环手选任务模式
  P    给车身一个 10 N 侧推       R    在当前测试点复位
  Y    开/关 MuJoCo 航向辅助（默认开；补偿 Isaac→MuJoCo 的偏航漂移）
  F    循环传送：平地、台阶、斜坡、狗洞、起伏路、飞坡、中心岛、挡墙
  C    循环切换当前策略与包内对照策略
  H    再显示本帮助               关闭窗口退出 MuJoCo

Space、Tab、数字键和 F1..F8 保留给 MuJoCo Viewer，不再触发车辆命令。

黄色=平地/狗洞，蓝色=台阶，绿色=斜坡，紫色=起伏路，橙色=飞坡。
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=ROOT / "policies" / "mod4_extended_800.onnx")
    parser.add_argument("--model", type=Path, default=ROOT / "model" / "rm_training_arena.xml")
    parser.add_argument("--yaw-assist", type=float, default=80.0,
                        help="MuJoCo yaw-rate feedback gain; use 0 for the raw ONNX policy")
    parser.add_argument("--spawn", choices=[f"f{i}" for i in range(1, 9)], default="f1",
                        help="initial test location")
    args = parser.parse_args()
    model_xml = args.model.resolve()
    requested_policy = args.policy.resolve()
    policy_candidates = [requested_policy,
                         ROOT / "policies" / "mod4_extended_800.onnx",
                         ROOT / "policies" / "mod4_general_16295.onnx",
                         ROOT / "policies" / "mod4_tunnel_399_ab_only.onnx"]
    policies = []
    seen = set()
    for path in policy_candidates:
        path = path.resolve()
        if path.exists() and path not in seen:
            policies.append(path)
            seen.add(path)
    selected = 0
    sim = Mod4Sim(model_xml, requested_policy, RuntimeConfig(yaw_assist_gain=args.yaw_assist))
    current_spawn_index = int(args.spawn[1:]) - 1
    current_spawn = SPAWNS[current_spawn_index]
    label, x, y, yaw, ground = current_spawn
    sim.reset(x, y, yaw, ground)
    print(HELP, flush=True)
    print(f"当前策略：{requested_policy.name}", flush=True)
    print(f"模型：{model_xml.name}；初始位置：{label}", flush=True)

    def status(prefix=""):
        mode = MODE_NAMES[sim._auto_task()[0]] if sim.command.auto_mode else MODE_NAMES[sim.command.mode]
        print(f"{prefix} vx={sim.command.vx:+.2f} m/s  wz={sim.command.wz:+.2f} rad/s  "
              f"height={sim.command.height:.3f} m  mode={mode}  auto={sim.command.auto_mode}  "
              f"yaw_assist={sim.cfg.yaw_assist_gain:g}", flush=True)

    def key_callback(key):
        nonlocal selected, current_spawn, current_spawn_index
        if key in CONTROL_KEYS["forward"]:
            sim.command.vx += .20
        elif key in CONTROL_KEYS["reverse"]:
            sim.command.vx -= .20
        elif key in CONTROL_KEYS["left"]:
            sim.command.wz += .50
        elif key in CONTROL_KEYS["right"]:
            sim.command.wz -= .50
        elif key in CONTROL_KEYS["stop"]:
            sim.command.vx = sim.command.wz = 0.0
        elif key in CONTROL_KEYS["lower"]:
            sim.command.height -= .01
            sim.command.auto_mode = False
        elif key in CONTROL_KEYS["raise"]:
            sim.command.height += .01
            sim.command.auto_mode = False
        elif key in CONTROL_KEYS["auto"]:
            sim.command.auto_mode = not sim.command.auto_mode
        elif key in CONTROL_KEYS["next_mode"]:
            sim.command.mode = (sim.command.mode + 1) % len(MODE_NAMES)
            sim.command.auto_mode = False
            print("手动任务模式：" + MODE_NAMES[sim.command.mode], flush=True)
        elif key in CONTROL_KEYS["push"]:
            sim.push((0.0, 10.0, 0.0), .20)
            print("已施加 10 N、0.20 s 横向扰动", flush=True)
        elif key in CONTROL_KEYS["yaw_assist"]:
            sim.cfg.yaw_assist_gain = 0.0 if sim.cfg.yaw_assist_gain else 80.0
            print(f"MuJoCo 航向辅助：{'开' if sim.cfg.yaw_assist_gain else '关'}", flush=True)
        elif key in CONTROL_KEYS["reset"]:
            label, x, y, yaw, ground = current_spawn
            sim.reset(x, y, yaw, ground)
            print(f"已复位：{label}", flush=True)
        elif key in CONTROL_KEYS["next_spawn"]:
            current_spawn_index = (current_spawn_index + 1) % len(SPAWNS)
            current_spawn = SPAWNS[current_spawn_index]
            label, x, y, yaw, ground = current_spawn
            sim.reset(x, y, yaw, ground)
            print(f"已传送：{label}", flush=True)
        elif key in CONTROL_KEYS["next_policy"]:
            selected = (selected + 1) % len(policies)
            sim.set_policy(policies[selected])
            print("当前策略：" + policies[selected].name, flush=True)
        elif key in CONTROL_KEYS["help"]:
            print(HELP, flush=True)
        else:
            # Leave MuJoCo Viewer shortcuts entirely to the Viewer.
            return
        sim.command.clamp()
        status()

    with mujoco.viewer.launch_passive(sim.model, sim.data, key_callback=key_callback,
                                      show_left_ui=True, show_right_ui=False) as viewer:
        viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        viewer.cam.trackbodyid = sim.chassis_id
        viewer.cam.distance = 2.2
        viewer.cam.azimuth = 145
        viewer.cam.elevation = -22
        next_tick = time.perf_counter()
        next_report = next_tick + 2.0
        while viewer.is_running():
            sim.step_control()
            viewer.sync()
            next_tick += 1.0 / sim.cfg.policy_hz
            delay = next_tick - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            else:
                next_tick = time.perf_counter()
            if time.perf_counter() >= next_report:
                h = sim.health()
                print(f"t={h['time_s']:6.1f}s  xyz=({h['base_xyz'][0]:+.2f},"
                      f"{h['base_xyz'][1]:+.2f},{h['base_xyz'][2]:.2f})  "
                      f"upright={h['upright_cos']:.3f}  closure={h['closure_error_m']*1000:.3f}mm  "
                      f"peak_tau={max(h['max_abs_torque_nm_actuator_order']):.2f}Nm",
                      flush=True)
                next_report += 2.0


if __name__ == "__main__":
    main()

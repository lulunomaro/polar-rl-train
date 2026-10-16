"""Why does the Isaac crouch sit ~19 mm above the CAD hard stop?  (2026-09-13)

Settles the exact CAD hard-stop pose (hip/crank + the full passive solution), then prints:
  * the joint angles the mechanism actually reaches (commanded vs realised),
  * the world height of every meaningful low point: both tyres, all eight rollers, the chassis
    boxes, so it is obvious WHAT is holding the chassis up,
  * the per-body contact force of tyres / rollers / chassis.

  RM_MOD4_USD=<usd> python isaac/mod4/probe_crouch_geometry.py --num_envs 4 --settle 200
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--settle", type=int, default=200)
parser.add_argument("--sweep", type=int, default=0, help="1 = sweep the crouch command past the stop to separate actuator sag from a hard kinematic stop")
parser.add_argument("--press", type=float, default=1.0, help="1 = command the MuJoCo-style bias (hip 0.47729 / diff -1.13632) so the mechanism presses into the mechanical stop")
parser.add_argument("--x0", type=float, default=0.55)
parser.add_argument("--y", type=float, default=-5.95)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402

HIP = 0.450290972128024
CRANK = -0.6360285683080382
PASSIVE = {"rocker_pin": -0.7828279184955518, "coupler_pin": 0.9027785273324023,
           "knee": -0.7613787030122099, "distal_pin": 0.8152830434591931,
           "gas_pin": 0.15599963671374795}
GAS_SLIDE = -0.02675468436086534
FLOOR = -0.155806


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    robot = env.scene["robot"]
    dev = env.device
    names = list(robot.joint_names)
    bodies = list(robot.body_names)
    idx = {nm: i for i, nm in enumerate(mod4_task.ACTION_ORDER)}
    scale = mod4_task.LEG_ACTION_SCALE

    targets = {"left_hip": HIP, "right_hip": HIP, "left_crank": CRANK, "right_crank": CRANK,
               "left_drive_hip_spin": -HIP, "right_drive_hip_spin": -HIP,
               "left_drive_input_spin": -CRANK, "right_drive_input_spin": -CRANK,
               "left_gas_slide": GAS_SLIDE, "right_gas_slide": GAS_SLIDE}
    for side in ("left", "right"):
        for k, v in PASSIVE.items():
            targets["%s_%s" % (side, k)] = v

    env.reset()
    n = env.num_envs
    ids = torch.arange(n, device=dev)
    pos = env.scene.env_origins[ids].clone()
    pos[:, 0] += args.x0
    pos[:, 1] += args.y
    pos[:, 2] = FLOOR + float(mod4_task.CONTRACT["spawn_height_m"])
    quat = torch.zeros((n, 4), device=dev)
    quat[:, 3] = 1.0
    robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)

    q = robot.data.joint_pos.clone()
    for name, val in targets.items():
        if name in names:
            q[:, names.index(name)] = val
    robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)

    # The MuJoCo benchmark that reached the CAD pose used ordinary PD *bias* commands
    # (hip 0.47729 / difference -1.13632): the motors press the linkage into the stop and the
    # realised pose is the CAD hard stop (0.45029 / -1.08632).  Commanding the realised pose
    # instead leaves the legs 0.12 rad short under gravity.
    CMD_HIP, CMD_DIFF = 0.47729, -1.13632
    hip_cmd = CMD_HIP if args.press else HIP
    crank_cmd = (CMD_HIP + CMD_DIFF) if args.press else CRANK
    print("[geo] command mode: %s  hip_cmd=%+.5f crank_cmd=%+.5f (diff %+.5f)"
          % ("PRESS" if args.press else "realised-pose", hip_cmd, crank_cmd, crank_cmd - hip_cmd),
          flush=True)
    if args.sweep:
        for hip_cmd in (0.4503, 0.4773, 0.5503, 0.6503, 0.8003):
            crank_cmd = hip_cmd - 1.13632
            act = torch.zeros((n, 6), device=dev)
            act[:, idx["left_hip"]] = hip_cmd / scale
            act[:, idx["right_hip"]] = hip_cmd / scale
            act[:, idx["left_crank"]] = crank_cmd / scale
            act[:, idx["right_crank"]] = crank_cmd / scale
            env.reset()
            robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)
            q = robot.data.joint_pos.clone()
            for name, val in targets.items():
                if name in names:
                    q[:, names.index(name)] = val
            robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)
            for _ in range(args.settle):
                env.step(act)
            rh = float((robot.data.root_pos_w[:, 2] - env.scene.env_origins[:, 2]).mean()) - FLOOR
            hz = float(robot.data.joint_pos[:, names.index("left_hip")].mean())
            cz = float(robot.data.joint_pos[:, names.index("left_crank")].mean())
            rp = float(robot.data.joint_pos[:, names.index("left_rocker_pin")].mean())
            kn = float(robot.data.joint_pos[:, names.index("left_knee")].mean())
            f = env.scene.sensors["wheel_contact"].data.net_forces_w
            if hasattr(f, "torch"):
                f = f.torch
            wf = [round(float(v), 1) for v in f.norm(dim=-1).mean(dim=0).tolist()]
            g = env.scene.sensors["guide_contact"].data.net_forces_w
            if hasattr(g, "torch"):
                g = g.torch
            gf = round(float(g.norm(dim=-1).max(dim=1).values.mean()), 1)
            print("[sweep] hip_cmd=%+.4f diff=%+.5f -> realised hip=%+.4f crank=%+.4f "
                  "rocker=%+.4f knee=%+.4f root_h=%.4f envelope=%.4f tyreF=%s rollerF_max=%.1f"
                  % (hip_cmd, crank_cmd - hip_cmd, hz, cz, rp, kn, rh, rh + 0.066934, wf, gf),
                  flush=True)
        env.close()
        return

    act = torch.zeros((n, 6), device=dev)
    act[:, idx["left_hip"]] = hip_cmd / scale
    act[:, idx["right_hip"]] = hip_cmd / scale
    act[:, idx["left_crank"]] = crank_cmd / scale
    act[:, idx["right_crank"]] = crank_cmd / scale
    for _ in range(args.settle):
        env.step(act)

    print("[geo] --- realised joint angles (mean over %d envs) ---" % n, flush=True)
    for name in sorted(targets):
        if name in names:
            got = float(robot.data.joint_pos[:, names.index(name)].mean())
            print("[geo]   %-26s commanded %+9.5f  realised %+9.5f  delta %+8.5f"
                  % (name, targets[name], got, got - targets[name]), flush=True)

    root = robot.data.root_pos_w - env.scene.env_origins
    root_h = float((root[:, 2] - FLOOR).mean())
    print("[geo] root height above hole floor = %.4f m  (CAD hard stop: 0.1788 m)" % root_h, flush=True)

    bp = robot.data.body_pos_w - env.scene.env_origins[:, None, :]
    low = []
    for name in bodies:
        i = bodies.index(name)
        z = float(bp[:, i, 2].mean()) - FLOOR            # body origin above the floor
        if name.startswith("guide_roller_"):
            low.append((name, z - 0.015, "roller bottom"))
        elif "wheel" in name and name.startswith(("left_wheel", "right_wheel")):
            low.append((name, z - 0.0625, "tyre bottom"))
    for name in ("chassis",):
        i = bodies.index(name)
        z = float(bp[:, i, 2].mean()) - FLOOR
        low.append((name + "/core", z - 0.144, "chassis core bottom"))
        low.append((name + "/belly", z - 0.167, "chassis belly bottom"))
    low.sort(key=lambda r: r[1])
    print("[geo] --- lowest points above the hole floor ---", flush=True)
    for name, z, kind in low[:12]:
        print("[geo]   %-22s %-20s %+.4f m" % (name, kind, z), flush=True)

    for sensor in ("wheel_contact", "guide_contact", "chassis_contact"):
        s = env.scene.sensors.get(sensor)
        if s is None:
            continue
        f = s.data.net_forces_w
        if hasattr(f, "torch"):
            f = f.torch
        per = f.norm(dim=-1).mean(dim=0)
        print("[geo] %-15s per-body force: %s" % (sensor, [round(float(v), 1) for v in per.tolist()]),
              flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
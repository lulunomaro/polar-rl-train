"""Can the Isaac plant HOLD the verified low pose if the leg loop has enough authority?

2026-09-13: the MuJoCo work (user-provided) reaches the 247.2 mm tunnel with
hip=+0.470170 / crank=-0.595844 (diff -1.066014), envelope 245.634 mm, drive wheels carrying
~41 N each.  The Isaac task runs the legs at DELIVERY_CONTRACT LEG_KP=60, which leaves a
0.13-0.22 rad steady-state sag under the crouch load, so the same pose is never reached.
This probe sweeps the leg position-loop stiffness (controller parameter, not a model change)
and reports the realised pose, root height, CAD envelope and the tyre/roller load split.

  RM_MOD4_USD=<usd> python isaac/mod4/probe_crouch_kp.py --num_envs 4 --kps 60,200,500,1000
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--settle", type=int, default=200)
parser.add_argument("--kps", default="60,200,500,1000")
parser.add_argument("--hip", type=float, default=0.470170)
parser.add_argument("--crank", type=float, default=-0.595844)
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

FLOOR = -0.155806
PASSIVE = {"rocker_pin": -0.788, "coupler_pin": 0.889, "knee": -0.767,
           "distal_pin": 0.800, "gas_pin": 0.156}
GAS_SLIDE = -0.0268


def main() -> None:
    for kp in [float(k) for k in args.kps.split(",") if k.strip()]:
        mod4_task.LEG_KP = kp                     # controller parameter (nothing in the USD)
        cfg = mod4_task.Mod4EnvCfg()
        cfg.scene.num_envs = args.num_envs
        # The cfgclass builds the robot cfg at import time, so assigning the module global above
        # changes NOTHING on its own - rebuild the articulation cfg here (first sweep showed
        # byte-identical poses for kp 60..1000, which was that bug, not a kinematic limit).
        cfg.scene.robot = mod4_task.mod4_robot_cfg()
        mod4_task.attach_rmuc2026_terrain(cfg)
        env = Mod4Env(cfg=cfg)
        robot = env.scene["robot"]
        dev = env.device
        names = list(robot.joint_names)
        idx = {nm: i for i, nm in enumerate(mod4_task.ACTION_ORDER)}
        scale = mod4_task.LEG_ACTION_SCALE
        n = env.num_envs
        env.reset()
        ids = torch.arange(n, device=dev)
        pos = env.scene.env_origins[ids].clone()
        pos[:, 0] += args.x0
        pos[:, 1] += args.y
        pos[:, 2] = FLOOR + float(mod4_task.CONTRACT["spawn_height_m"])
        quat = torch.zeros((n, 4), device=dev)
        quat[:, 3] = 1.0
        robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)
        act = torch.zeros((n, 6), device=dev)
        for ch, val in (("left_hip", args.hip), ("right_hip", args.hip),
                        ("left_crank", args.crank), ("right_crank", args.crank)):
            act[:, idx[ch]] = val / scale
        for _ in range(args.settle):
            env.step(act)
        loc = robot.data.root_pos_w - env.scene.env_origins
        root_h = float((loc[:, 2] - FLOOR).mean())
        hz = float(robot.data.joint_pos[:, names.index("left_hip")].mean())
        cz = float(robot.data.joint_pos[:, names.index("left_crank")].mean())
        rp = float(robot.data.joint_pos[:, names.index("left_rocker_pin")].mean())
        kn = float(robot.data.joint_pos[:, names.index("left_knee")].mean())
        gs = float(robot.data.joint_pos[:, names.index("left_gas_slide")].mean())
        tau = float(robot.data.applied_torque[:, [names.index("left_hip"),
                                                  names.index("left_crank")]].abs().max())
        wf = env.scene.sensors["wheel_contact"].data.net_forces_w
        if hasattr(wf, "torch"):
            wf = wf.torch
        tyres = [round(float(v), 1) for v in wf.norm(dim=-1).mean(dim=0).tolist()]
        gf = env.scene.sensors["guide_contact"].data.net_forces_w
        if hasattr(gf, "torch"):
            gf = gf.torch
        rollers = [round(float(v), 1) for v in gf.norm(dim=-1).mean(dim=0).tolist()]
        env.close()
        print("[kp] kp=%6.0f hip=%+.4f (cmd %+.4f) crank=%+.4f (cmd %+.4f) diff=%+.4f "
              "rocker=%+.4f knee=%+.4f gas_slide=%+.4f | root_h=%.4f envelope=%.4f "
              "| tyreF=%s rollerF=%s legTau=%5.1f Nm"
              % (kp, hz, args.hip, cz, args.crank, cz - hz, rp, kn, gs, root_h,
                 root_h + 0.066934, tyres, rollers, tau), flush=True)


if __name__ == "__main__":
    main()
    app.close()
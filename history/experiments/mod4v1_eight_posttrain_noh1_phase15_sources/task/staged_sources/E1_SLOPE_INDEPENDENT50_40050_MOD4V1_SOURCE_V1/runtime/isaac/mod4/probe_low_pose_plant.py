"""Can the ISAAC plant reach the CAD hard-stop pose?  (2026-09-12)

MuJoCo kinematics say the CAD low pose (hip +0.4503 rad, input difference -1.0843) puts the root
0.178 m above the floor, which is what the 247 mm dog hole needs.  `probe_crouch.py`'s crude
-2..+2 sweep never got below ~0.29 m, so this probe commands the EXACT pose family the design
asks for and follows the root height over time, on the fixed plant.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_low_pose_plant.py --headless --steps 400
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=400)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    env = Mod4Env(cfg=cfg)
    env.reset()
    robot = env.scene["robot"]
    names = list(robot.joint_names)
    stop = mod4_task.CONTRACT["mechanical_stop"]
    win = mod4_task.CONTRACT["training_window"]["input_difference_min_rad"]
    hip = float(stop["hip_rad"])
    scale = mod4_task.LEG_ACTION_SCALE
    cases = {
        "cad_hardstop": (hip, hip + float(stop["input_difference_rad"])),
        "train_window": (hip, hip + float(win)),
        "hip0_diff-1.0843": (0.0, -1.0843),
    }
    act = torch.zeros((env.num_envs, 6), device=env.device)
    # The action vector is ACTION_ORDER = [left_crank, left_hip, right_crank, right_hip,
    # left_wheel, right_wheel] -- NOT hip-then-crank.  Writing hip into slot 0 (the first
    # version of this probe) sent the hip target into the crank and slammed the hip to its
    # lower limit, which looked like "the plant cannot crouch".
    idx = {n: i for i, n in enumerate(mod4_task.ACTION_ORDER)}
    for label, (h, c) in cases.items():
        act[:, idx["left_hip"]] = h / scale
        act[:, idx["left_crank"]] = c / scale
        act[:, idx["right_hip"]] = h / scale
        act[:, idx["right_crank"]] = c / scale
        env.reset()
        trace = []
        for step in range(args.steps):
            env.step(act)
            if step % max(1, args.steps // 8) == 0 or step == args.steps - 1:
                z = robot.data.root_pos_w[:, 2]
                g = robot.data.projected_gravity_b
                tilt = torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0)))
                trace.append((step, float(z.mean()), float(z.min()), float(tilt.mean())))
        print("[lowpose] %-18s targets hip %+.4f crank %+.4f" % (label, h, c), flush=True)
        for step, zmean, zmin, tilt in trace:
            print("[lowpose]    step %4d  root_z mean %.3f  min %.3f  tilt %.1f deg"
                  % (step, zmean, zmin, tilt), flush=True)
        jp = robot.data.joint_pos[0]
        for n in mod4_task.LEG_ORDER:
            print("[lowpose]    measured %-12s %+.4f rad" % (n, float(jp[names.index(n)])),
                  flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()

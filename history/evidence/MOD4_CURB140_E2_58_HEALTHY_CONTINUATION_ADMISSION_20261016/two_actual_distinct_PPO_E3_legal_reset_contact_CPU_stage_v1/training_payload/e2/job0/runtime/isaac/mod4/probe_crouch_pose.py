"""Is the delivered crouch pose geometrically reachable in the Isaac plant?  (goal 2)

MEASURED 2026-09-12 18:35 (isaac/mod4/probe_tunnel_coast.py --pose hardstop, delivered plant)
    settled root height above the trench floor = 0.1974 m, tyres carrying 71 N, chassis 0 N
while the delivered CAD/MJCF puts the SAME commanded pose (hip +0.450291 rad, input difference
-1.0843 rad) at 0.1788 m (MuJoCo settle, sim_mujoco/tunnel_crouch_traction.py config A).  With the
delivered 247.2 mm dog hole:

    CAD/MJCF  0.1788 + 0.0669 (CAD skin) = 0.2457 m  -> fits, 2.3 mm clearance
    Isaac     0.1974 + 0.0669            = 0.2643 m  -> 17 mm too tall

Either the Isaac articulation differs from CAD (link offsets / closure / limits), or the pose is
reachable and only the action path is short.  This probe decides between the two:

  * zeroes the leg actuator gains (write_joint_stiffness_to_sim / damping 0),
  * writes the FULL CAD pose -- all twelve leg joints, passive ones included, values from the STEP
    B-Rep audit in the goal -- into the articulation every step for `--steps` steps,
  * reports the resulting root height above the local floor, the per-joint tracking error and the
    chassis / guide-roller / wheel contact forces.

    python isaac/mod4/probe_crouch_pose.py --headless --num_envs 4 --steps 150
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=150)
parser.add_argument("--every", type=int, default=25)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402

# Delivered CAD crouch (STEP B-Rep + SolidWorks audit, goal section 1 / tools/crouch_window.py).
CAD_POSE = {
    "hip": 0.450290972128024,
    "crank": -0.6360285683080382,
    "rocker_pin": -0.7828279184955518,
    "coupler_pin": 0.9027785273324023,
    "knee": -0.7613787030122099,
    "distal_pin": 0.8152830434591931,
    "gas_pin": 0.15599963671374795,
    "gas_slide": -0.02675468436086534,
}


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    robot = env.scene["robot"]
    n = env.num_envs
    names = list(robot.joint_names)
    print("[pose] articulation joints (%d): %s" % (len(names), names), flush=True)

    target = robot.data.default_joint_pos.clone()
    used = {}
    for j, name in enumerate(names):
        base = name.split("_", 1)[1] if name.startswith(("left_", "right_")) else name
        if base in CAD_POSE:
            target[:, j] = CAD_POSE[base]
            used[name] = CAD_POSE[base]
    print("[pose] wrote CAD values to %d joints: %s" % (len(used), sorted(used)), flush=True)

    # zero the leg gains so the written pose is what the geometry sees, not what a PD makes of it
    zeros = torch.zeros_like(robot.data.default_joint_stiffness)
    robot.write_joint_stiffness_to_sim(zeros)
    robot.write_joint_damping_to_sim(zeros)
    print("[pose] actuator gains zeroed; writing the CAD pose every step", flush=True)

    chassis = env.scene.sensors["chassis_contact"]
    wheels = env.scene.sensors["wheel_contact"]
    act = torch.zeros((n, 6), device=env.device)
    print("[pose] step | root_h | hip_err | diff_err | wheel_N | chassis_N", flush=True)
    for step in range(args.steps):
        robot.write_joint_state_to_sim(target, torch.zeros_like(target))
        env.step(act)
        if step % args.every == 0 or step == args.steps - 1:
            loc = robot.data.root_pos_w - env.scene.env_origins
            gz = getattr(env, "_mod4_ground_z", None)
            g = float(gz.mean()) if gz is not None else float(loc[:, 2].mean()) - 0.19
            jp = robot.data.joint_pos
            hip_i = names.index("left_hip") if "left_hip" in names else 0
            crank_i = names.index("left_crank") if "left_crank" in names else 1
            hip_err = float((jp[:, hip_i] - target[:, hip_i]).abs().mean())
            diff_err = float(((jp[:, crank_i] - jp[:, hip_i])
                              - (target[:, crank_i] - target[:, hip_i])).abs().mean())
            wf = wheels.data.net_forces_w
            if hasattr(wf, "torch"):
                wf = wf.torch
            cf = chassis.data.net_forces_w
            if hasattr(cf, "torch"):
                cf = cf.torch
            print("[pose] %4d | %.4f | %.5f | %.5f | %7.1f | %9.1f"
                  % (step, float(loc[:, 2].mean()) - g, hip_err, diff_err,
                     float(wf.norm(dim=-1).max(dim=1).values.mean()),
                     float(cf.norm(dim=-1).max(dim=1).values.mean())), flush=True)
    env.close()


if __name__ == "__main__":
    main()

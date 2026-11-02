"""Rolling-idler plant probe (2026-09-13, user spec section 3).

Checks the NEW asset end to end in PhysX without any policy:
 1. inventory: bodies and joints actually loaded (expect 8 extra guide_roller bodies/joints),
 2. exact CAD hard-stop crouch: write hip/crank AND every passive closure joint, hold with the
    leg action interface, let the mechanism settle, THEN read the pose,
 3. root height, drive-tyre / roller / chassis contact forces, roller spin rates and slip,
 4. velocity injection check (does write_root_velocity_to_sim survive a step?),
 5. coast A/B: entry speeds 0.15/0.25/0.40/0.60 m/s -> travel, speed retention, roller spin,
    minimum CAD-skin clearance under the roof, whether the robot reaches x>1.10 and x>1.45.

  RM_MOD4_USD=<...>/robot.usd python isaac/mod4/probe_rolling_plant.py --num_envs 4 --settle 150
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--settle", type=int, default=150)
parser.add_argument("--steps", type=int, default=400)
parser.add_argument("--speeds", default="0.15,0.25,0.40,0.60")
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
import skills_isaac as skills  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402

# exact CAD hard stop (B-Rep + MuJoCo back-solve, 2026-09-12) and its passive joint solution
HIP = 0.450290972128024
CRANK = -0.6360285683080382
DIFF = CRANK - HIP                       # -1.0863195404360622
PASSIVE = {"rocker_pin": -0.7828279184955518,
           "coupler_pin": 0.9027785273324023,
           "knee": -0.7613787030122099,
           "distal_pin": 0.8152830434591931,
           "gas_pin": 0.15599963671374795}
GAS_SLIDE = -0.02675468436086534


def sensor_max(env, name):
    if name not in env.scene.sensors:
        return None
    f = env.scene.sensors[name].data.net_forces_w
    if hasattr(f, "torch"):
        f = f.torch
    return f.norm(dim=-1)


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    robot = env.scene["robot"]
    n, dev = env.num_envs, env.device
    names = list(robot.joint_names)
    print("[roll] usd=%s" % mod4_task.USD_PATH, flush=True)
    print("[roll] bodies=%d joints=%d num_dof=%d" % (len(robot.body_names), len(names),
                                                     robot.num_joints), flush=True)
    rollers = [b for b in robot.body_names if b.startswith("guide_roller_")]
    rjoints = [j for j in names if j.startswith("guide_roller_")]
    print("[roll] roller bodies=%d %s" % (len(rollers), rollers[:3]), flush=True)
    print("[roll] roller joints=%d %s" % (len(rjoints), rjoints[:3]), flush=True)
    print("[roll] sensors: %s" % sorted(env.scene.sensors.keys()), flush=True)

    idx = {nm: i for i, nm in enumerate(mod4_task.ACTION_ORDER)}
    scale = mod4_task.LEG_ACTION_SCALE
    act = torch.zeros((n, 6), device=dev)
    act[:, idx["left_hip"]] = HIP / scale
    act[:, idx["right_hip"]] = HIP / scale
    act[:, idx["left_crank"]] = CRANK / scale
    act[:, idx["right_crank"]] = CRANK / scale

    env.reset()
    ids = torch.arange(n, device=dev)
    pos = env.scene.env_origins[ids].clone()
    pos[:, 0] += args.x0
    pos[:, 1] += args.y
    pos[:, 2] = -0.155806 + float(mod4_task.CONTRACT["spawn_height_m"])
    quat = torch.zeros((n, 4), device=dev)
    quat[:, 3] = 1.0
    robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)

    # write the FULL joint solution (active + every passive joint) so the closure is consistent
    q = robot.data.joint_pos.clone()
    targets = {"left_hip": HIP, "right_hip": HIP, "left_crank": CRANK, "right_crank": CRANK,
               "left_drive_hip_spin": -HIP, "right_drive_hip_spin": -HIP,
               "left_drive_input_spin": -CRANK, "right_drive_input_spin": -CRANK,
               "left_gas_slide": GAS_SLIDE, "right_gas_slide": GAS_SLIDE}
    for side in ("left", "right"):
        for key, val in PASSIVE.items():
            targets["%s_%s" % (side, key)] = val
    for name, val in targets.items():
        if name in idx:
            i = names.index(name)
            q[:, i] = val
    robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)
    print("[roll] wrote %d joint targets (active + passive closure solution)" % len(targets),
          flush=True)

    for step in range(args.settle):
        env.step(act)
    loc = robot.data.root_pos_w - env.scene.env_origins
    floor = skills.HOLE_FLOOR_Z
    root_h = float((loc[:, 2] - floor).mean())
    envelope = float((loc[:, 2] - floor).mean() + skills.CAD_TOP_ABOVE_ROOT_M)
    wheel = sensor_max(env, "wheel_contact")
    guide = sensor_max(env, "guide_contact")
    chassis = sensor_max(env, "chassis_contact")
    print("[roll] settled: root_h=%.4f m  CAD envelope=%.4f m  ceiling=%.4f m  clearance=%+.4f m"
          % (root_h, envelope, skills.HOLE_CEILING_Z - floor,
             (skills.HOLE_CEILING_Z - floor) - envelope), flush=True)
    for label, s in (("tyre", wheel), ("guide roller", guide), ("chassis", chassis)):
        if s is None:
            print("[roll]   %-13s sensor missing" % label, flush=True)
        else:
            print("[roll]   %-13s per-body max force: %s" % (label, [round(float(v), 1) for v in
                                                                     s.mean(dim=0).tolist()[:12]]), flush=True)

    # --- velocity injection check -------------------------------------------------------
    vel = torch.zeros((n, 6), device=dev)
    vel[:, 0] = 0.40
    robot.write_root_velocity_to_sim(vel, env_ids=ids)
    v_after_write = robot.data.root_lin_vel_w[:, 0].clone()
    env.step(act)
    print("[roll] velocity injection: requested 0.400  after_write=%.4f  after_one_step=%.4f"
          % (float(v_after_write.mean()), float(robot.data.root_lin_vel_w[:, 0].mean())), flush=True)

    print("[roll] %6s %9s %9s %9s %8s %9s %9s %9s"
          % ("v0", "x_end", "vx_end", "vx_retain", "min_clr", "roll_rad", "roll_slip", "clear145"),
          flush=True)
    for v0 in [float(s) for s in args.speeds.split(",") if s.strip()]:
        env.reset()
        pos = env.scene.env_origins[ids].clone()
        pos[:, 0] += args.x0
        pos[:, 1] += args.y
        pos[:, 2] = floor + float(mod4_task.CONTRACT["spawn_height_m"])
        robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)
        q = robot.data.joint_pos.clone()
        for name, val in targets.items():
            if name in names:
                q[:, names.index(name)] = val
        robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)
        for _ in range(args.settle):
            env.step(act)
        vel = torch.zeros((n, 6), device=dev)
        vel[:, 0] = v0
        robot.write_root_velocity_to_sim(vel, env_ids=ids)
        x_end = torch.full((n,), args.x0, device=dev)
        min_clr = torch.full((n,), 9.9, device=dev)
        spin_sum = torch.zeros(n, device=dev)
        slip_sum = torch.zeros(n, device=dev)
        for step in range(args.steps):
            env.step(act)
            loc = robot.data.root_pos_w - env.scene.env_origins
            x, y, z = loc[:, 0], loc[:, 1], loc[:, 2]
            x_end = torch.maximum(x_end, x)
            inside = ((x.abs() >= skills.HOLE_ROOF_X[0]) & (x.abs() <= skills.HOLE_ROOF_X[1]) &
                      (y.abs() >= skills.HOLE_LANE_Y[0]) & (y.abs() <= skills.HOLE_LANE_Y[1]))
            clr = skills.HOLE_CEILING_Z - (z + skills.CAD_TOP_ABOVE_ROOT_M)
            min_clr = torch.where(inside, torch.minimum(min_clr, clr), min_clr)
            if step < 100:
                rids = [names.index(j) for j in rjoints if j in names]
                if rids:
                    w = robot.data.joint_vel[:, rids]
                    spin_sum += w.abs().mean(dim=1)
                    slip_sum += (w.mean(dim=1) * 0.015 - robot.data.root_lin_vel_b[:, 0]).abs()
        vx_end = robot.data.root_lin_vel_b[:, 0]
        cleared = float((x_end >= 1.45).float().mean())
        print("[roll] %6.2f %9.3f %9.3f %9.3f %8.4f %9.2f %9.3f %9.2f"
              % (v0, float(x_end.mean()), float(vx_end.mean()),
                 float(vx_end.mean()) / max(1e-6, v0), float(min_clr.mean()),
                 float(spin_sum.mean() / 100.0), float(slip_sum.mean() / 100.0), cleared),
              flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
"""PhysX probe for the MOD4 chassis USD: when and how do the loop closures separate?

The delivered ``isaac/smoke_test.py`` accepts the USD into PhysX correctly (masses,
armatures, joint limits and effort caps all read back), but the six spherical loop
closures separate during the bounded motion test.  This probe records *when* and *how*
instead of just raising, so the fix can be evidence driven.  It also lets the PhysX
solver type and iteration counts be switched from the command line, because loop joints
are exactly the case where TGS and PGS behave differently.

Run from the repo root (the Isaac Lab python has to launch the app itself):

  .venv-isaaclab\\Scripts\\python.exe isaac\\mod4\\probe_physx.py --motion zero --steps 2000
  .venv-isaaclab\\Scripts\\python.exe isaac\\mod4\\probe_physx.py --motion smoke --steps 6000 --solver pgs
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ISAAC_PKG = ROOT / "incoming" / "chassis_mod4_mjcf_usd_20260910" / "chassis_mod4" / "isaac"
sys.path.insert(0, str(ISAAC_PKG))

parser = argparse.ArgumentParser()
parser.add_argument("--steps", type=int, default=2000)
parser.add_argument("--motion", choices=("zero", "pd", "random", "smoke"), default="zero")
parser.add_argument("--solver", choices=("default", "pgs", "tgs"), default="default")
parser.add_argument("--pos-iters", type=int, default=0, help="0 keeps the shipped config")
parser.add_argument("--vel-iters", type=int, default=0)
parser.add_argument("--dt", type=float, default=0.0, help="0 keeps the contract dt")
parser.add_argument("--report-every", type=int, default=250)
parser.add_argument("--fail-at", type=float, default=0.05, help="closure error [m] treated as failure")
parser.add_argument("--out", default=str(ROOT / "isaac" / "mod4" / "probe_report.json"))
parser.add_argument("--dump-state", action="store_true",
                    help="print joint positions and body frames right after reset")

from isaaclab.app import AppLauncher  # noqa: E402

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402
from pxr import UsdGeom  # noqa: E402
import isaaclab.sim as sim_utils  # noqa: E402
from isaaclab.assets import Articulation  # noqa: E402
from isaaclab.utils.math import quat_apply as _quat_apply  # noqa: E402
from robot_cfg import make_robot_cfg, TorqueInterface, CONTRACT  # noqa: E402
from audit_import import audit_stage  # noqa: E402
from isaaclab_physx.physics import PhysxCfg  # noqa: E402

DT = args.dt or CONTRACT["physics_dt_s"]


TRACE = ROOT / "isaac" / "mod4" / "probe_trace.txt"


def note(msg):
    """Print and append to probe_trace.txt.

    Kit's app.close() tears the interpreter down, which can swallow a traceback, so
    progress has to reach disk before that happens.
    """
    print(msg, flush=True)
    try:
        TRACE.parent.mkdir(parents=True, exist_ok=True)
        with TRACE.open("a", encoding="utf8") as fh:
            fh.write(msg + chr(10))
    except OSError:
        pass


def main():
    sim_cfg = sim_utils.SimulationCfg(dt=DT, device=args.device, render_interval=20)
    phys = sim_cfg.physics
    if args.solver != "default" or args.pos_iters or args.vel_iters:
        # Isaac Lab 6.x leaves SimulationCfg.physics at None (= engine defaults); the
        # config object has to exist before any solver field can be set.
        phys = phys or PhysxCfg()
        if args.solver == "pgs":
            phys.solver_type = 0
        elif args.solver == "tgs":
            phys.solver_type = 1
        if args.pos_iters:
            phys.min_position_iteration_count = args.pos_iters
            phys.max_position_iteration_count = args.pos_iters
        if args.vel_iters:
            phys.min_velocity_iteration_count = args.vel_iters
            phys.max_velocity_iteration_count = args.vel_iters
        sim_cfg.physics = phys
    if sim_cfg.physics is None:
        note("[probe] physics=engine-defaults dt=%s" % DT)
    else:
        note("[probe] solver_type=%s pos_iters=%s..%s vel_iters=%s..%s dt=%s" % (
            sim_cfg.physics.solver_type,
            sim_cfg.physics.min_position_iteration_count,
            sim_cfg.physics.max_position_iteration_count,
            sim_cfg.physics.min_velocity_iteration_count,
            sim_cfg.physics.max_velocity_iteration_count, DT))

    sim = sim_utils.SimulationContext(sim_cfg)
    stage = sim_utils.get_current_stage()
    ground = sim_utils.CuboidCfg(size=(200.0, 200.0, 0.1),
        collision_props=sim_utils.CollisionPropertiesCfg(),
        physics_material=sim_utils.RigidBodyMaterialCfg(
            static_friction=0.9, dynamic_friction=0.9, restitution=0.0))
    ground.func("/World/Ground", ground, translation=(0.0, 0.0, -0.05))
    light = sim_utils.DomeLightCfg(intensity=2500.0)
    light.func("/World/Light", light)
    node = UsdGeom.Xform.Define(stage, "/World/envs/env_0")
    node.AddTranslateOp().Set((0.0, 0.0, 0.0))
    cfg = make_robot_cfg("/World/envs/env_0/Robot")
    cfg.spawn.func(cfg.prim_path, cfg.spawn, translation=cfg.init_state.pos)
    audit_stage(stage, cfg.prim_path, require_physx=True)
    cfg = make_robot_cfg("/World/envs/env_.*/Robot")
    cfg.spawn = None
    robot = Articulation(cfg)
    sim.reset()
    robot.update(DT)
    interface = TorqueInterface(robot)

    pairs = []
    for cname, spec in CONTRACT["closures"].items():
        pairs.append((
            cname,
            robot.body_names.index(spec["body0"]),
            robot.body_names.index(spec["body1"]),
            torch.tensor(spec["anchor0_m"], device=robot.device),
            torch.tensor(spec["anchor1_m"], device=robot.device)))
    mimics = [(jname, spec["reference_joint"], spec["gearing"], spec["offset"])
              for jname, spec in CONTRACT["mimics"].items()]

    def rotate(quat, vec):
        # Use the installed Isaac Lab quaternion maths instead of hard-coding an order:
        # 3.0/6.x store (x, y, z, w) and identity is [0, 0, 0, 1], while 2.x stored
        # (w, x, y, z).  The delivered guard hard-coded the 2.x order and therefore
        # reported a phantom 0.36 m closure error here.
        return _quat_apply(quat, vec.expand(quat.shape[0], 3))

    def closure_errors():
        pos = robot.data.body_pos_w
        quat = robot.data.body_quat_w
        out = {}
        for cname, a, b, pa, pb in pairs:
            err = (pos[:, a] + rotate(quat[:, a], pa) - pos[:, b]
                   - rotate(quat[:, b], pb)).norm(dim=-1).max().item()
            out[cname] = err
        return out

    def mimic_errors():
        out = {}
        for jname, ref, gearing, offset in mimics:
            i = robot.joint_names.index(jname)
            r = robot.joint_names.index(ref)
            out[jname] = (robot.data.joint_pos[:, i]
                          - (gearing * robot.data.joint_pos[:, r] + offset)).abs().max().item()
        return out

    def reset():
        state = robot.data.default_root_state.clone()
        robot.write_root_pose_to_sim(state[:, :7])
        robot.write_root_velocity_to_sim(state[:, 7:])
        robot.write_joint_state_to_sim(robot.data.default_joint_pos.clone(),
                                       robot.data.default_joint_vel.clone())
        robot.reset()
        interface.apply(torch.zeros((robot.num_instances, 6), device=sim.device))
        robot.write_data_to_sim()

    reset()
    robot.update(DT)
    if args.dump_state:
        note("[probe] joint positions after reset:")
        for i, jname in enumerate(robot.joint_names):
            note("        %-22s %+.9f" % (jname, robot.data.joint_pos[0, i].item()))
        note("[probe] body frames after reset:")
        for bname in ("chassis", "left_thigh", "left_rocker", "left_coupler",
                      "left_input", "left_shin", "left_wheel"):
            i = robot.body_names.index(bname)
            p = robot.data.body_pos_w[0, i].tolist()
            q = robot.data.body_quat_w[0, i].tolist()
            note("        %-14s pos=%s quat=%s" % (bname,
                 [round(x, 6) for x in p], [round(x, 6) for x in q]))
    err0 = closure_errors()
    mim0 = mimic_errors()
    print("[probe] after reset closures:", json.dumps({k: round(v, 9) for k, v in err0.items()}), flush=True)
    print("[probe] after reset mimics:  ", json.dumps({k: round(v, 9) for k, v in mim0.items()}), flush=True)
    root_z0 = robot.data.root_pos_w[:, 2].mean().item()
    print("[probe] after reset base height: %.6f" % root_z0, flush=True)

    series = []
    max_err = dict(err0)
    max_mim = dict(mim0)
    first_fail = None
    command = torch.zeros((robot.num_instances, 6), device=sim.device)
    start = time.perf_counter()
    for step in range(args.steps):
        if not app.is_running():
            break
        q = robot.data.joint_pos[:, interface.motor_ids]
        vel = robot.data.joint_vel[:, interface.motor_ids]
        t = step * DT
        if args.motion == "zero":
            command = torch.zeros_like(q)
        elif args.motion == "pd":
            target = torch.zeros_like(q)
            target[:, [0, 1, 3, 4]] = 0.12 * math.sin(t * 3.0)
            command = (45.0 * (target - q) - 2.0 * vel) / interface.limits
            command[:, [2, 5]] = 0.1 * math.sin(t * 5.0)
        elif args.motion == "random":
            if step % 40 == 0:
                command = torch.rand_like(q) * 2.0 - 1.0
        else:
            if step < args.steps // 3:
                target = torch.zeros_like(q)
                target[:, [0, 1, 3, 4]] = 0.12 * math.sin(t * 3.0)
                command = (45.0 * (target - q) - 2.0 * vel) / interface.limits
                command[:, [2, 5]] = 0.1 * math.sin(t * 5.0)
            elif step < 2 * args.steps // 3:
                if step % 40 == 0:
                    command = torch.rand_like(q) * 2.0 - 1.0
            else:
                if step % 200 == 0:
                    command = (torch.randint(0, 2, q.shape, device=sim.device) * 2 - 1).float()
        interface.apply(command)
        robot.write_data_to_sim()
        sim.step(render=False)
        robot.update(DT)
        if step % args.report_every == 0 or step < 3:
            errs = closure_errors()
            mims = mimic_errors()
            for k, val in errs.items():
                max_err[k] = max(max_err[k], val)
            for k, val in mims.items():
                max_mim[k] = max(max_mim[k], val)
            qd = robot.data.joint_vel.abs().max().item()
            z = robot.data.root_pos_w[:, 2].mean().item()
            worst = max(errs.items(), key=lambda kv: kv[1])
            print("[probe] step %5d t=%6.3f base_z=%.4f |qdot|max=%8.2f worst_closure=%s %.3e" % (
                step, t, z, qd, worst[0], worst[1]), flush=True)
            series.append(dict(step=step, t=t, base_z=z, qdot_max=qd,
                               closures=errs, mimics=mims))
            if first_fail is None and worst[1] > args.fail_at:
                first_fail = dict(step=step, t=t, closure=worst[0], error=worst[1],
                                  base_z=z, qdot_max=qd, closures=errs, mimics=mims)
                cname, a, b, pa, pb = [p for p in pairs if p[0] == worst[0]][0]
                print("[probe] FIRST FAILURE: %s at step %d (t=%.3f s)" % (worst[0], step, t), flush=True)
                for idx, tag in ((a, "body0"), (b, "body1")):
                    print("        %s %-16s pos=%s" % (tag, robot.body_names[idx],
                          [round(x, 6) for x in robot.data.body_pos_w[0, idx].tolist()]), flush=True)
                break
    elapsed = time.perf_counter() - start
    ph = sim_cfg.physics
    report = dict(args=vars(args), dt=DT,
                  solver_type=(ph.solver_type if ph else "engine-default"),
                  pos_iters=(ph.max_position_iteration_count if ph else None),
                  vel_iters=(ph.max_velocity_iteration_count if ph else None),
                  reset_closures=err0, reset_mimics=mim0, reset_base_z=root_z0,
                  max_closures=max_err, max_mimics=max_mim, first_failure=first_fail,
                  steps_done=step + 1, elapsed_s=elapsed,
                  steps_per_s=(step + 1) / elapsed, series=series)
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf8")
    print("[probe] steps=%d elapsed=%.1fs (%.0f steps/s) report=%s" % (
        step + 1, elapsed, (step + 1) / elapsed, args.out), flush=True)
    print("[probe] max closure error: " + json.dumps({k: round(v, 6) for k, v in max_err.items()}))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        import traceback
        note("[probe] FATAL" + chr(10) + traceback.format_exc())
        raise
    finally:
        app.close()

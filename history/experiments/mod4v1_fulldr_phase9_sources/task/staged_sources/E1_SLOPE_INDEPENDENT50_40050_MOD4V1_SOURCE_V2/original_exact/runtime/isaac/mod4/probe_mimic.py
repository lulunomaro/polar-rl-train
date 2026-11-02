"""How does PhysX actually couple the four MOD4 sprocket joints?

The delivered USD declares PhysxMimicJointAPI:rotX on the four sprocket joints
(gearing -1, offset 0), and the contract calls them "4 sprocket 1:1 couplings".
A zero-command probe run still showed the four drive links drifting 0.45-0.69 rad
away from that relation, so the coupling is either absent, sign-flipped, or much
softer than a sprocket.  This probe isolates the constraint: gravity off, no ground,
reference joints teleported to a known angle, drive joints written to zero, then the
solver is watched for a few hundred steps.

    .venv-isaaclab\Scripts\python.exe isaac\mod4\probe_mimic.py
    .venv-isaaclab\Scripts\python.exe isaac\mod4\probe_mimic.py --usd isaac\mod4\robot_mimic_tuned.usd
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ISAAC_PKG = ROOT / "incoming" / "rm2025_mod4" / "isaac"
sys.path.insert(0, str(ISAAC_PKG))

parser = argparse.ArgumentParser()
parser.add_argument("--usd", default=str(ISAAC_PKG / "robot.usd"))
parser.add_argument("--ref-angle", type=float, default=0.4, help="angle written to hip and crank")
parser.add_argument("--steps", type=int, default=400)
parser.add_argument("--damping-ratio", type=float, default=None)
parser.add_argument("--natural-frequency", type=float, default=None)
parser.add_argument("--report", default=str(ROOT / "isaac" / "mod4" / "mimic_report.json"))
AppLauncher = None

try:
    from isaaclab.app import AppLauncher  # noqa: E402
except Exception:  # pragma: no cover
    raise

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402
from pxr import Usd, UsdPhysics, Sdf  # noqa: E402
import isaaclab.sim as sim_utils  # noqa: E402
from isaaclab.assets import Articulation  # noqa: E402
from robot_cfg import make_robot_cfg, CONTRACT  # noqa: E402

try:
    from pxr import PhysxSchema  # noqa: E402
    names = [str(n) for n in PhysxSchema.PhysxMimicJointAPI.GetSchemaAttributeNames()]
    print("[mimic] PhysxMimicJointAPI attributes: " + ", ".join(names), flush=True)
except Exception as exc:  # pragma: no cover
    print("[mimic] schema introspection failed: %r" % (exc,), flush=True)


def tuned_stage(usd_path: str, natural_frequency: float | None, damping_ratio: float | None) -> str:
    """Copy the delivered stage and give the mimic joints a stiffness/damping budget."""
    if natural_frequency is None and damping_ratio is None:
        return usd_path
    src = Usd.Stage.Open(usd_path)
    out = ROOT / "isaac" / "mod4" / "robot_mimic_tuned.usd"
    src.GetRootLayer().Export(str(out))
    stage = Usd.Stage.Open(str(out))
    for prim in stage.Traverse():
        if not prim.IsA(UsdPhysics.Joint):
            continue
        raw = prim.GetMetadata("apiSchemas")
        items = list(raw.GetAppliedItems()) if raw else []
        variants = [i for i in items if i.startswith("PhysxMimicJointAPI:")]
        for variant in variants:
            prefix = "physxMimicJoint:" + variant.split(":", 1)[1] + ":"
            for suffix, value in (("naturalFrequency", natural_frequency),
                                  ("dampingRatio", damping_ratio)):
                if value is None:
                    continue
                attr = prim.GetAttribute(prefix + suffix)
                if not attr:
                    attr = prim.CreateAttribute(prefix + suffix, Sdf.ValueTypeNames.Float)
                attr.Set(float(value))
                print("[mimic] %s %s=%s" % (prim.GetName(), prefix + suffix, value), flush=True)
    stage.GetRootLayer().Save()
    return str(out)


if __name__ == "__main__":
    usd_path = tuned_stage(args.usd, args.natural_frequency, args.damping_ratio)
    dt = CONTRACT["physics_dt_s"]
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device, gravity=(0.0, 0.0, 0.0)))
    print("[mimic] gravity=%s dt=%s usd=%s" % (sim.cfg.gravity, dt, usd_path), flush=True)
    stage = sim_utils.get_current_stage()
    cfg = make_robot_cfg("/World/env_0/Robot")
    cfg.spawn.usd_path = usd_path
    cfg.spawn.func(cfg.prim_path, cfg.spawn, translation=cfg.init_state.pos)
    robot_cfg = make_robot_cfg("/World/env_.*/Robot")
    robot_cfg.spawn = None
    robot = Articulation(robot_cfg)
    sim.reset()
    robot.update(dt)

    names = robot.joint_names
    idx = {n: names.index(n) for n in names}
    pairs = [(n, v["reference_joint"], v["gearing"], v["offset"]) for n, v in CONTRACT["mimics"].items()]
    pairs = [p for p in pairs if p[0].startswith("left")]
    print("[mimic] pairs: %s" % pairs, flush=True)

    q = robot.data.default_joint_pos.clone()
    q[:] = 0.0
    for name, ref, gearing, offset in pairs:
        q[:, idx[ref]] = args.ref_angle
        q[:, idx[name]] = 0.0
    robot.write_joint_state_to_sim(q, torch.zeros_like(q))
    robot.set_joint_effort_target(torch.zeros_like(robot.data.joint_pos))
    robot.set_joint_velocity_target(torch.zeros_like(robot.data.joint_pos))
    robot.set_joint_position_target(torch.zeros_like(robot.data.joint_pos))
    robot.write_data_to_sim()

    series = []
    for step in range(args.steps):
        robot.write_data_to_sim()
        sim.step(render=False)
        robot.update(dt)
        if step in (0, 1, 2, 4, 9, 19, 49, 99, 199, args.steps - 1):
            row = {"step": step}
            for name, ref, gearing, offset in pairs:
                drive = robot.data.joint_pos[0, idx[name]].item()
                reference = robot.data.joint_pos[0, idx[ref]].item()
                row[name] = dict(drive=drive, reference=reference,
                                 err_contract=abs(drive - (gearing * reference + offset)),
                                 err_plus=abs(drive - reference))
            series.append(row)
            print("[mimic] step %4d %s" % (step, json.dumps({k: {kk: round(vv, 6) for kk, vv in v.items()}
                                                             for k, v in row.items() if k != "step"})), flush=True)

    # Sprocket sanity: a chain link must stay parallel to the link it is chained to, so
    # the relative rotation drive<->reference has to equal the authored neutral one.  A
    # mirrored sign (the contracted -1 instead of the MJCF polycoef +1) would show up as a
    # relative rotation that differs by ~2*|angle|.
    import math
    import numpy as np
    bodies = CONTRACT["bodies"]

    def to_wxyz(quat_xyzw):
        return np.array([quat_xyzw[3], quat_xyzw[0], quat_xyzw[1], quat_xyzw[2]])

    def rel_angle(qa, qb):
        d = abs(float(np.dot(qa, qb)))
        return 2.0 * math.acos(min(1.0, d))

    R = robot.data.body_quat_w[0].cpu().numpy()
    relative = {}
    for a, b in (("left_drive_hip", "left_thigh"), ("left_drive_input", "left_input")):
        sim_angle = rel_angle(to_wxyz(R[robot.body_names.index(a)]),
                              to_wxyz(R[robot.body_names.index(b)]))
        authored = rel_angle(np.array(bodies[a]["neutral_quat_wxyz"]),
                             np.array(bodies[b]["neutral_quat_wxyz"]))
        relative[a] = dict(simulated=sim_angle, authored=authored, delta=abs(sim_angle - authored))
        print("[mimic] relative %s vs %s: sim=%.6f authored=%.6f delta=%.6f rad" % (
            a, b, sim_angle, authored, abs(sim_angle - authored)), flush=True)

    report = dict(usd=usd_path, gravity=list(sim.cfg.gravity), ref_angle=args.ref_angle,
                  relative=relative,
                  natural_frequency=args.natural_frequency, damping_ratio=args.damping_ratio,
                  pairs=pairs, series=series)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
    print("[mimic] report written to %s" % args.report, flush=True)
    app.close()

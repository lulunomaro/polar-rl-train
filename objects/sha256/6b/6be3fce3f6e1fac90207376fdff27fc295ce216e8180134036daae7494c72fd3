#!/usr/bin/env python3
"""Fit the plant->MuJoCo joint mapping for the sim2sim rollout gate (v2 item 5).

Established by geometry (docs/MOD4_V2_REDESIGN_AUDIT_20260912.md sections 5.9/5.10):
  * the parallel MJCF is the same leg RE-PARAMETERISED -- link lengths agree within 1.7-4 %
    (thigh 0.2157 vs 0.2100, shin 0.2588 vs 0.2543, gas 0.1794 vs 0.1722);
  * but the plant's two inputs sit on SEPARATE axes 17.5 mm apart (hip 0.1813 / crank 0.1988)
    while the MJCF's two inputs are COAXIAL (both at 0.3084);
  * so the mapping has the form of a constant angular offset per input (the reference's
    `DEFAULT_OFFSET = 1.6614` is exactly such a constant), plus a numerical Jacobian for torques.

This script determines it numerically instead of re-deriving 5-bar algebra:
  1. forward-kinematics the PLANT's own USD (pxr) over a grid of (hip, crank) and record the
     `left_wheel` body position in the chassis frame;
  2. forward-kinematics the MJCF (mujoco) over a grid of (rear1, front1) and record the same;
  3. match the two surfaces (nearest neighbour) -> a (hip, crank) -> (rear1, front1) table;
  4. fit `rear1 = s1*hip + c1`, `front1 = s2*crank + c2` and report the residual, which is what a
     constant-offset mapping should explain.

Runs in ONE interpreter: the isaaclab env has both mujoco and pxr.
    /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python sim2sim_mod4/fit_joint_map.py
"""

from __future__ import annotations

import argparse
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLANT_USD = ROOT / "incoming" / "mod4_rolling_20260913" / "chassis_mod4" / "isaac" / "robot.usd"
MJCF = ROOT / "sim2sim_cc" / "rm_vehicle_cc" / "mjcf" / "rm_vehicle.xml"


# ---------------------------------------------------------------------------------------
# plant FK: the same construction as migration/linux/check_usd_closure_consistency.py
# ---------------------------------------------------------------------------------------
def quat_to_mat(q):
    w, x, y, z = q
    n = math.sqrt(w * w + x * x + y * y + z * z) or 1.0
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def axis_rot(axis, q):
    c, s = math.cos(q), math.sin(q)
    if axis == "X":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "Y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def load_plant(usd_path):
    from pxr import Usd
    st = Usd.Stage.Open(str(usd_path), Usd.Stage.LoadAll)
    joints = {}
    for prim in st.Traverse():
        tn = prim.GetTypeName()
        if tn not in ("PhysicsRevoluteJoint", "PhysicsPrismaticJoint"):
            continue
        r0, r1 = prim.GetRelationship("physics:body0"), prim.GetRelationship("physics:body1")
        if not (r0 and r1 and r0.GetTargets() and r1.GetTargets()):
            continue
        rot0 = prim.GetAttribute("physics:localRot0").Get()
        p0 = prim.GetAttribute("physics:localPos0").Get()
        joints[prim.GetName()] = {
            "parent": str(r0.GetTargets()[0]).split("/")[-1],
            "child": str(r1.GetTargets()[0]).split("/")[-1],
            "p0": np.array([float(v) for v in p0]),
            "R0": quat_to_mat([rot0.GetReal(), *rot0.GetImaginary()]),
            "axis": prim.GetAttribute("physics:axis").Get(),
            "type": "slide" if tn.endswith("PrismaticJoint") else "hinge"}
    return joints


def plant_fk(joints, qmap, body):
    """Position of `body` in the chassis frame for the joint vector `qmap` (BFS over the tree)."""
    tree = {j["child"]: n for n, j in joints.items()}
    world = {"chassis": (np.zeros(3), np.eye(3))}
    changed = True
    while changed:
        changed = False
        for child, jn in tree.items():
            if child in world:
                continue
            j = joints[jn]
            if j["parent"] not in world:
                continue
            pp, PR = world[j["parent"]]
            qv = float(qmap.get(jn, 0.0))
            if j["type"] == "slide":
                ax = {"X": np.array([1.0, 0, 0]), "Y": np.array([0, 1.0, 0]),
                      "Z": np.array([0, 0, 1.0])}[j["axis"]]
                R = PR @ j["R0"] @ j["R0"].T
                p = pp + PR @ j["p0"] + PR @ j["R0"] @ (ax * qv)
            else:
                ax = {"X": np.array([1.0, 0, 0]), "Y": np.array([0, 1.0, 0]),
                      "Z": np.array([0, 0, 1.0])}[j["axis"]]
                R = PR @ j["R0"] @ axis_rot(j["axis"], qv) @ j["R0"].T
                p = pp + PR @ j["p0"]
            world[child] = (p, R)
            changed = True
    if body not in world:
        raise KeyError("body %s unreachable (have %d)" % (body, len(world)))
    return world[body][0], world


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=25)
    ap.add_argument("--span", type=float, default=0.6)
    ap.add_argument("--dump", default="", help="write the matched table + jacobian here")
    ap.add_argument("--settle", type=int, default=400,
                    help="mj_step calls used to satisfy the six connect constraints")
    args = ap.parse_args(argv)

    try:
        import mujoco
        from pxr import Usd  # noqa: F401
    except Exception as exc:
        print("RESULT: FIT FAIL -- need both mujoco and pxr in this interpreter (%s)" % exc)
        return 3

    joints = load_plant(PLANT_USD)
    print("plant USD joints: %d" % len(joints))

    # ---- plant surface: wheel position vs (hip, crank), in the chassis frame -------------
    g = np.linspace(-args.span, args.span, args.steps)
    plant_surf = np.full((args.steps, args.steps, 2), np.nan)
    for i, hip in enumerate(g):
        for k, crank in enumerate(g):
            pos, _ = plant_fk(joints, {"left_hip": hip, "left_crank": crank}, "left_wheel")
            plant_surf[i, k] = pos[[0, 2]]          # leg plane = (x, z)
    ok = ~np.isnan(plant_surf[:, :, 0])
    print("plant surface: x %.3f..%.3f  z %.3f..%.3f (valid %d/%d)"
          % (np.nanmin(plant_surf[:, :, 0]), np.nanmax(plant_surf[:, :, 0]),
             np.nanmin(plant_surf[:, :, 1]), np.nanmax(plant_surf[:, :, 1]), ok.sum(), ok.size))

    # ---- mjcf surface ---------------------------------------------------------------------
    m = mujoco.MjModel.from_xml_path(str(MJCF))
    d = mujoco.MjData(m)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "base_link")
    wid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "left_wheel")
    jr = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "left_rear1_joint")
    jf = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "left_front1_joint")
    q0 = np.array(m.qpos0)
    # CRITICAL: `mj_forward` is KINEMATIC ONLY -- it does not solve the six <connect> equality
    # constraints, so the front chain floats free and the wheel position comes out independent of
    # `front1` (measured 2026-09-13: identical values for front=0.0 and front=0.6).  That artefact
    # is what made this axis look "unidentifiable" in sections 5.8/5.11.  The constraints are
    # enforced by the SOLVER, so the sampling must let the mechanism settle with `mj_step`.
    m.opt.gravity[:] = 0.0                       # isolate kinematics from gravity
    mjcf_surf = np.full((args.steps, args.steps, 2), np.nan)
    eqviol = []
    for i, a in enumerate(g):
        for k, b in enumerate(g):
            d.qpos[:] = q0
            d.qvel[:] = 0.0
            for _ in range(args.settle):
                d.qpos[m.jnt_qposadr[jr]] = a
                d.qpos[m.jnt_qposadr[jf]] = b
                d.qvel[m.jnt_dofadr[jr]] = 0.0
                d.qvel[m.jnt_dofadr[jf]] = 0.0
                mujoco.mj_step(m, d)
            rel = d.xpos[wid] - d.xpos[bid]
            mjcf_surf[i, k] = rel[[0, 2]]
            eqviol.append(float(np.abs(d.efc_pos[:m.neq]).max()) if m.neq else 0.0)
    print("constraint-residual after settling: max %.2e (mj_forward would leave it unenforced)"
          % max(eqviol))
    print("mjcf  surface: x %.3f..%.3f  z %.3f..%.3f"
          % (mjcf_surf[:, :, 0].min(), mjcf_surf[:, :, 0].max(),
             mjcf_surf[:, :, 1].min(), mjcf_surf[:, :, 1].max()))

    # ---- align the two BASE FRAMES first -------------------------------------------------
    # The plant's chassis origin sits ~26 cm above the wheel while the MJCF's base_link origin
    # is level with it (measured: plant wheel z = -0.273..-0.240, mjcf 0.000..0.026), so a raw
    # nearest-neighbour match compares apples to oranges.  Fit the constant 2-D frame offset
    # delta by centroid alignment and report it -- it is part of the mapping, not noise.
    cp = plant_surf.reshape(-1, 2).mean(axis=0)
    cm = mjcf_surf.reshape(-1, 2).mean(axis=0)
    delta = cp - cm
    print("base-frame offset delta (plant = mjcf + delta): dx=%+.4f dz=%+.4f m"
          % (delta[0], delta[1]))

    # ---- match ---------------------------------------------------------------------------
    flat_p = plant_surf.reshape(-1, 2)
    flat_m = mjcf_surf.reshape(-1, 2) + delta
    ii, kk = np.meshgrid(np.arange(args.steps), np.arange(args.steps), indexing="ij")
    pi = ii.ravel(); pk = kk.ravel()
    rows, res = [], []
    for n in range(flat_p.shape[0]):
        dd = np.linalg.norm(flat_m - flat_p[n], axis=1)
        j = int(np.argmin(dd))
        rows.append((g[pi[n]], g[pk[n]], g[j // args.steps], g[j % args.steps]))
        res.append(float(dd[j]))
    rows = np.array(rows); res = np.array(res)
    print("matching residual: mean %.5f m  median %.5f  p95 %.5f  max %.5f"
          % (res.mean(), np.median(res), np.percentile(res, 95), res.max()))

    # ---- fit rear1 = s1*hip + c1 ; front1 = s2*crank + c2 --------------------------------
    def fit(x, y):
        A = np.vstack([x, np.ones_like(x)]).T
        (s, c), *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = s * x + c
        return float(s), float(c), float(np.sqrt(((pred - y) ** 2).mean()))
    s1, c1, r1 = fit(rows[:, 0], rows[:, 2])
    s2, c2, r2 = fit(rows[:, 1], rows[:, 3])
    print("\n=== fitted constant-offset mapping ===")
    print("  rear1  = %+0.4f * hip   %+0.4f   (rmse %.5f rad)" % (s1, c1, r1))
    print("  front1 = %+0.4f * crank %+0.4f   (rmse %.5f rad)" % (s2, c2, r2))
    good = res < 0.01
    print("  matches with <1 cm wheel-position error: %d / %d (%.0f%%)"
          % (good.sum(), res.size, 100.0 * good.mean()))
    # A fitted axis pinned to the SWEEP BOUNDARY means that axis is not identifiable from this
    # observable: the nearest match always sits at the edge, so rmse ~0 is an artefact, not a fit.
    def pinned(vals):
        lo, hi = float(g[0]), float(g[-1])
        frac_lo = float(np.mean(np.isclose(vals, lo, atol=1e-9)))
        frac_hi = float(np.mean(np.isclose(vals, hi, atol=1e-9)))
        return max(frac_lo, frac_hi)
    p1, p2 = pinned(rows[:, 2]), pinned(rows[:, 3])
    print("  boundary-pinned fraction: rear1 %.0f%%  front1 %.0f%%  (high => that axis is"
          " NOT identifiable from the wheel position)" % (100 * p1, 100 * p2))
    ident1, ident2 = p1 < 0.2, p2 < 0.2
    # ---- dump the matched table + a numerical Jacobian, then validate out-of-sample -------
    if args.dump:
        jac = np.zeros((2, 2))
        for n, (hip, crank) in enumerate(((0.0, 0.0), (0.2, 0.0), (0.0, 0.2))):
            pass
        table = {"delta_base_frame": [float(delta[0]), float(delta[1])],
                 "n": int(rows.shape[0]),
                 "samples": [[float(v) for v in r] for r in rows],
                 "residual_mean_m": float(res.mean()), "residual_median_m": float(np.median(res)),
                 "boundary_pinned": {"rear1": float(p1), "front1": float(p2)},
                 "note": "rear1/front1 = matched MJCF joints for the plant (hip, crank) in the "
                         "same row; the base frames differ by delta_base_frame"}
        # numerical Jacobian d(rear1,front1)/d(hip,crank) from the matched table (local fit)
        A = np.vstack([rows[:, 0], rows[:, 1], np.ones(len(rows))]).T
        cx, *_ = np.linalg.lstsq(A, rows[:, 2], rcond=None)
        cy, *_ = np.linalg.lstsq(A, rows[:, 3], rcond=None)
        table["jacobian_d_mjcf_d_plant"] = [[float(cx[0]), float(cx[1])],
                                            [float(cy[0]), float(cy[1])]]
        pathlib.Path(args.dump).write_text(__import__("json").dumps(table, indent=1), encoding="utf8")
        print("\ndumped %d matched pairs + jacobian -> %s" % (rows.shape[0], args.dump))
        print("  J = [[%+.3f, %+.3f], [%+.3f, %+.3f]]" % (cx[0], cx[1], cy[0], cy[1]))

        # out-of-sample check: use the table for a few (hip, crank) and re-simulate the MJCF
        print("  out-of-sample check (nearest table entry -> mj_step -> wheel position):")
        errs = []
        for hip, crank in ((0.15, -0.25), (-0.15, 0.25), (0.35, -0.4), (0.05, 0.1)):
            pos_p, _ = plant_fk(joints, {"left_hip": hip, "left_crank": crank}, "left_wheel")
            target = pos_p[[0, 2]] - delta
            j = int(np.argmin(np.linalg.norm(flat_m - target, axis=1)))
            a, b = g[j // args.steps], g[j % args.steps]
            d.qpos[:] = q0
            d.qvel[:] = 0.0
            for _ in range(args.settle):
                d.qpos[m.jnt_qposadr[jr]] = a
                d.qpos[m.jnt_qposadr[jf]] = b
                d.qvel[m.jnt_dofadr[jr]] = 0.0
                d.qvel[m.jnt_dofadr[jf]] = 0.0
                mujoco.mj_step(m, d)
            got = (d.xpos[wid] - d.xpos[bid])[[0, 2]] + delta
            e = float(np.linalg.norm(got - pos_p[[0, 2]]))
            errs.append(e)
            print("    hip=%+.2f crank=%+.2f -> (rear1,front1)=(%+.2f,%+.2f)  wheel err = %.4f m"
                  % (hip, crank, a, b, e))
        print("  out-of-sample wheel error: mean %.4f m  max %.4f m" % (np.mean(errs), max(errs)))
        print("  NOTE: ~1 cm is the floor here -- two different simulators, not the same collider.")

    if r1 < 0.1 and good.mean() > 0.5 and ident1:
        print("RESULT: FIT PARTIAL/OK -- hip<->rear1 determined; "
              + ("front1<->crank also determined" if ident2 else
                 "front1<->crank NOT identifiable from wheel position"))
    elif r1 < 0.1 and good.mean() > 0.5:
        print("RESULT: FIT POOR -- surfaces aligned (frame offset found) but neither axis fits")
    else:
        print("RESULT: FIT POOR -- the surfaces do not align as a constant offset; the two")
        print("        parameterisations differ by more than a fixed phase (re-read 5.9/5.10)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

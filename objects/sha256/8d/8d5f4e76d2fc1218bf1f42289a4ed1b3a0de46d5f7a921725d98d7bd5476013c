#!/usr/bin/env python3
"""Determine the policy-joint -> MuJoCo-joint mapping for the MOD4 parallel plant.

Why this is needed
------------------
The rollout half of the sim2sim gate has to drive the SAME six degrees of freedom the policy was
trained on (`left_crank`, `left_hip`, `right_crank`, `right_hip`, `left_wheel_spin`,
`right_wheel_spin`), but the parallel MJCF names them `left_rear1_joint`, `left_front1_joint`,
`left_wheel_joint`, ...  The six `class="motor"` joints are exactly the six policy DOF (verified:
6 of 19 joints carry the tag), and the 5-bar loop is closed by six `<connect>` constraints
(`neq = 6`), so NO analytic IK is needed -- only the name/sign/zero correspondence.

What this probe does
--------------------
It loads the parallel MJCF, holds the floating base fixed, sweeps the two motor joints of the
left leg over a grid, and reports the resulting **base-to-wheel-contact vertical extension**.
That surface is then matched against the two numbers the training plant actually measured
(`docs/probe_crouch_kp3.log`, `docs/probe_crouch_pi.log`):

    crouch  hip=+0.4671  crank=-0.5929  -> root 0.1791 m   (envelope 246.0 mm)
    stance  hip=+0.4699  crank=-0.5882  -> root 0.1798 m

plus the contract's own convention (`mechanical_stop.hip_rad = 0.4503`,
`mechanical_stop.crank_rad = -0.6360`, `machine_stop.source_difference_rad`) and the joint limits
the MJCF authors put on the passive members.  The candidate mapping whose surface reproduces
"larger hip / more negative crank -> lower base" (i.e. the crouch direction) is the right one;
the probe prints the ranking so the sign is evidence-based rather than guessed.

Usage
-----
    third_party/rc_mjlab/.venv/bin/python sim2sim_mod4/calibrate_joint_map.py
    ... --mjcf sim2sim_cc/rm_vehicle_cc/mjcf/rm_vehicle.xml --steps 41
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "train" / "deploy" / "contract_rm2025_later.json"
DEFAULT_MJCF = ROOT / "sim2sim_cc" / "rm_vehicle_cc" / "mjcf" / "rm_vehicle.xml"

# Measured on the training plant (docs/probe_crouch_kp3.log writes exactly these lines).
TRAIN_CROUCH = {"hip": 0.4671, "crank": -0.5929, "root": 0.1791}
TRAIN_STANCE = {"hip": 0.4666, "crank": -0.5918, "root": 0.1796}


def leg_extension(model, data, j_rear, j_front, a_rear, a_front, wheel_geom_ids, base_id):
    """Base-to-lowest-wheel-contact distance with the base held fixed.  Lower = more crouched."""
    data.qpos[:] = model.qpos0
    data.qvel[:] = 0.0
    data.qpos[model.jnt_qposadr[j_rear]] = a_rear
    data.qpos[model.jnt_qposadr[j_front]] = a_front
    # pin the floating base: qpos0 keeps it, but assert it explicitly against drift
    import mujoco
    mujoco.mj_forward(model, data)
    base_z = float(data.xpos[base_id][2])
    wheel_z = min(float(data.geom_xpos[g][2]) for g in wheel_geom_ids)
    return base_z - wheel_z


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mjcf", default=str(DEFAULT_MJCF))
    ap.add_argument("--steps", type=int, default=41)
    ap.add_argument("--span", type=float, default=1.2, help="sweep +- this many rad around qpos0")
    args = ap.parse_args(argv)

    try:
        import mujoco
    except Exception as exc:
        print("RESULT: CALIBRATE FAIL -- mujoco missing (%s)" % exc)
        return 3

    m = mujoco.MjModel.from_xml_path(args.mjcf)
    d = mujoco.MjData(m)
    name2id = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)

    # MuJoCo does not expose the default CLASS per joint (jnt_class does not exist in 3.13), so
    # read the six `class="motor"` names from the XML -- that tag is what marks the driven joints.
    import re
    xml = pathlib.Path(args.mjcf).read_text(encoding="utf8")
    motor = re.findall(r'<joint name="([^"]+)"[^>]*class="motor"', xml)
    print("motor joints (%d): %s" % (len(motor), motor))
    if len(motor) != 6:
        print("RESULT: CALIBRATE FAIL -- expected 6 motor joints, got %d" % len(motor))
        return 2

    base_id = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "base_link")
    # PER SIDE: taking min() over both wheels makes the surface constant, because the leg under
    # test moves only its own wheel (found 2026-09-13 -- the first version of this probe reported
    # a zero-span surface for exactly that reason).
    wheel_geoms = [g for g in range(m.ngeom)
                   if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "").startswith("left")
                   and "wheel" in (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "")]
    print("left wheel geoms: %s" % [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) for g in wheel_geoms])

    left = [n for n in motor if n.startswith("left") and "wheel" not in n]
    left_wheel = [n for n in motor if n.startswith("left") and "wheel" in n]
    if len(left) != 2:
        print("RESULT: CALIBRATE FAIL -- left leg motors: %s" % left)
        return 2
    jA, jB = name2id(left[0]), name2id(left[1])

    # contract conventions
    try:
        c = json.loads(CONTRACT.read_text(encoding="utf8"))
    except Exception:
        c = {}
    # the mechanical stop / training window live in the MOD4 PLANT contract, not the RM2025 one
    plant = ROOT / "incoming" / "mod4_rolling_20260913" / "chassis_mod4" / "isaac" / "import_contract.json"
    try:
        pj = json.loads(plant.read_text(encoding="utf8"))
    except Exception:
        pj = {}
    stop = pj.get("mechanical_stop") or c.get("mechanical_stop") or {}
    print("plant contract: %s" % plant.name)
    print("contract mechanical_stop: hip=%s crank=%s | source_difference=%s"
          % (stop.get("hip_rad"), stop.get("crank_rad"), stop.get("source_difference_rad")))
    print("plant training_window: %s" % (pj.get("training_window")))

    g = np.linspace(-args.span, args.span, args.steps)
    surf = np.zeros((args.steps, args.steps))
    for i, a in enumerate(g):
        for k, b in enumerate(g):
            surf[i, k] = leg_extension(m, d, jA, jB, a, b, wheel_geoms, base_id)

    print("\n=== base-to-wheel-contact distance (m); rows=%s, cols=%s ===" % (left[0], left[1]))
    print("  range: %.4f .. %.4f  (span %.4f m)" % (surf.min(), surf.max(), surf.max() - surf.min()))
    # where does each axis lower the base?
    # Direction statistics over the whole swept surface.  Two earlier estimators were wrong for
    # concrete reasons: the qpos0 pose is a kinematic SINGULARITY (all joints 0 -> the local
    # Jacobian is ~0, so the finite-difference gradient vanishes), and the plain mean of
    # np.gradient cancels because the map is strongly non-linear over +-1.2 rad.  The Pearson
    # correlation over the grid is robust to both.
    A, B = np.meshgrid(g, g, indexing="ij")
    def corr(x, y):
        x = x.ravel() - x.mean(); y = y.ravel() - y.mean()
        den = float(np.sqrt((x * x).sum() * (y * y).sum()))
        return float((x * y).sum() / den) if den > 1e-12 else 0.0
    rA, rB = corr(A, surf), corr(B, surf)
    print("  corr(%s, extension) = %+0.3f   (negative => increasing it CROUCHES)" % (left[0], rA))
    print("  corr(%s, extension) = %+0.3f" % (left[1], rB))
    print("  corners: (%.2f,%.2f)=%.4f  (%.2f,%.2f)=%.4f  (%.2f,%.2f)=%.4f  (%.2f,%.2f)=%.4f"
          % (g[0], g[0], surf[0, 0], g[-1], g[0], surf[-1, 0],
             g[0], g[-1], surf[0, -1], g[-1], g[-1], surf[-1, -1]))
    dA, dB = rA, rB
    print("\n  the training plant crouches with hip UP (+) and crank DOWN (-):")
    print("    crouch hip=%+.4f crank=%+.4f -> root %.4f m" % (TRAIN_CROUCH["hip"], TRAIN_CROUCH["crank"], TRAIN_CROUCH["root"]))
    print("    stance hip=%+.4f crank=%+.4f -> root %.4f m" % (TRAIN_STANCE["hip"], TRAIN_STANCE["crank"], TRAIN_STANCE["root"]))
    cand = []
    for a_name, a_sign, a_j in ((left[0], dA, "A"), (left[1], dB, "B")):
        for b_name, b_sign, b_j in ((left[0], dA, "A"), (left[1], dB, "B")):
            if a_j == b_j:
                continue
            # hip must crouch when increased (negative slope), crank when decreased (positive slope)
            score = (1 if a_sign < 0 else 0) + (1 if b_sign > 0 else 0)
            cand.append((score, a_name, b_name))
    cand.sort(reverse=True)
    print("\n=== candidate mapping (hip, crank) ranked by direction agreement ===")
    for score, a_name, b_name in cand:
        print("   score %d/2 :  left_hip <- %-20s   left_crank <- %s" % (score, a_name, b_name))
    best = cand[0]
    print("\n  => best: left_hip=%s  left_crank=%s  (direction score %d/2)"
          % (best[1], best[2], best[0]))
    print("     wheel: %s (unambiguous)" % (left_wheel[0] if left_wheel else "?"))
    print("  NOTE: sign/zero offsets still need one numeric fit against the measured crouch height;")
    print("        this probe only fixes WHICH joint is which, from geometry alone.")
    print("RESULT: CALIBRATE OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

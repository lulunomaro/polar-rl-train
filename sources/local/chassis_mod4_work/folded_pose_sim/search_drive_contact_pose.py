"""Search the near-stop MOD4 pose space for drive-wheel ground contact and tunnel fit.

Reads the corrected audit MJCF and original CAD meshes.  It does not edit either source.
The floor is z=0 and both main-wheel treads are placed on that floor.  A feasible row must
also keep every visual CAD vertex and all eight guide rollers out of the floor while keeping
the complete visual envelope below the 247.2 mm tunnel ceiling.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import mujoco
import numpy as np
from scipy.optimize import differential_evolution, minimize, minimize_scalar
from scipy.spatial import ConvexHull


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "chassis_mod4"
HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "scene_hard_stop_audit.xml"
OUT_PATH = HERE / "drive_contact_pose_search.json"
sys.path.insert(0, str(MODEL_DIR))
from kinematics import leg_configuration  # noqa: E402


model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
data = mujoco.MjData(model)
wheel_radius = 0.0625
tunnel_height = 0.2472
hard_stop = -1.0863195404360622
training_stop = -1.0843


def mesh_hulls():
    grouped = {}
    rot = np.empty(9)
    for geom_id in range(model.ngeom):
        if model.geom_type[geom_id] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        mesh_id = int(model.geom_dataid[geom_id])
        first = int(model.mesh_vertadr[mesh_id])
        last = first + int(model.mesh_vertnum[mesh_id])
        vertices = model.mesh_vert[first:last].astype(float)
        mujoco.mju_quat2Mat(rot, model.geom_quat[geom_id])
        vertices = vertices @ rot.reshape(3, 3).T + model.geom_pos[geom_id]
        grouped.setdefault(int(model.geom_bodyid[geom_id]), []).append(vertices)
    return {
        body: np.concatenate(chunks)[ConvexHull(np.concatenate(chunks)[:, (0, 2)]).vertices][:, (0, 2)]
        for body, chunks in grouped.items()
    }


hulls = mesh_hulls()
wheel_bodies = [model.body("left_wheel").id, model.body("right_wheel").id]
guide_geoms = [model.geom(f"guide_roller_collision_{i}").id for i in range(8)]
joint_ids = {
    side: {name: model.joint(f"{side}_{name}").id for name in leg_configuration(0, 0, side)[0]}
    for side in ("left", "right")
}


def apply_pose(hip: float, difference: float, pitch: float):
    data.qpos[:] = model.qpos0
    data.qvel[:] = 0
    data.qpos[:3] = 0
    data.qpos[3:7] = (math.cos(pitch / 2), 0, math.sin(pitch / 2), 0)
    joint_values = {}
    for side in ("left", "right"):
        values, _ = leg_configuration(hip, difference, side)
        joint_values[side] = values
        for name, value in values.items():
            jid = joint_ids[side][name]
            if model.jnt_limited[jid]:
                lo, hi = model.jnt_range[jid]
                if value < lo - 1e-9 or value > hi + 1e-9:
                    raise ValueError(f"{side}_{name} outside [{lo}, {hi}]")
            data.qpos[model.jnt_qposadr[jid]] = value
    mujoco.mj_forward(model, data)
    # Symmetric planar legs give identical wheel centre heights.
    data.qpos[2] += wheel_radius - float(data.xpos[wheel_bodies[0], 2])
    mujoco.mj_forward(model, data)
    return joint_values


def evaluate(x):
    hip, difference, pitch = map(float, x)
    try:
        joint_values = apply_pose(hip, difference, pitch)
    except (ValueError, FloatingPointError):
        return None
    low = float("inf")
    top = -float("inf")
    low_body = top_body = ""
    for body, hull in hulls.items():
        mat = data.xmat[body].reshape(3, 3)
        z = hull @ mat[2, (0, 2)] + data.xpos[body, 2]
        if float(z.min()) < low:
            low, low_body = float(z.min()), model.body(body).name
        if float(z.max()) > top:
            top, top_body = float(z.max()), model.body(body).name
    guide_gaps = [float(data.geom(gid).xpos[2] - model.geom_size[gid, 0]) for gid in guide_geoms]
    wheel_gaps = [float(data.xpos[body, 2] - wheel_radius) for body in wheel_bodies]
    return {
        "hip_rad": hip,
        "crank_rad": hip + difference,
        "difference_rad": difference,
        "pitch_rad": pitch,
        "pitch_deg": math.degrees(pitch),
        "root_height_m": float(data.qpos[2]),
        "wheel_gaps_m": wheel_gaps,
        "guide_gaps_m": guide_gaps,
        "minimum_guide_gap_m": min(guide_gaps),
        "minimum_visual_z_m": low,
        "minimum_visual_body": low_body,
        "full_height_m": top,
        "full_top_body": top_body,
        "tunnel_margin_m": tunnel_height - top,
        "joint_values_rad": joint_values,
    }


def violation(x):
    row = evaluate(x)
    if row is None:
        return 1e4
    # Millimetre-scaled squared hinge losses. Main-wheel contact is exact by construction.
    floor_v = max(0.0, -row["minimum_visual_z_m"])
    guide_v = max(0.0, -row["minimum_guide_gap_m"])
    roof_v = max(0.0, -row["tunnel_margin_m"])
    # Prefer the training-safe side of the CAD stop and modest pitch when several fits exist.
    return 1e6 * (floor_v * floor_v + guide_v * guide_v + roof_v * roof_v) + 0.02 * x[2] * x[2]


bounds = [(-0.5, 0.5), (hard_stop, -0.70), (-math.radians(8), math.radians(8))]
solutions = []
for seed in (17, 29, 43, 22336):
    result = differential_evolution(violation, bounds, seed=seed, popsize=10, maxiter=60,
                                    tol=1e-11, polish=False, workers=1, updating="immediate")
    polished = minimize(violation, result.x, method="Nelder-Mead",
                        options={"maxiter": 6000, "xatol": 1e-12, "fatol": 1e-14})
    row = evaluate(polished.x)
    row.update(seed=seed, objective=float(polished.fun), optimizer_success=bool(polished.success))
    row["feasible"] = bool(
        row["minimum_visual_z_m"] >= -1e-5
        and row["minimum_guide_gap_m"] >= -1e-5
        and row["tunnel_margin_m"] >= 0.001
        and row["difference_rad"] >= hard_stop - 1e-9
    )
    solutions.append(row)
    print(f"seed={seed} objective={row['objective']:.9g} feasible={row['feasible']}", flush=True)

grid_best = None
for difference in np.linspace(hard_stop, -0.94, 15):
    for hip in np.linspace(0.25, 0.5, 26):
        for pitch in np.linspace(-math.radians(3), math.radians(3), 5):
            row = evaluate((hip, difference, pitch))
            if row is None:
                continue
            score = violation((hip, difference, pitch))
            if grid_best is None or score < grid_best[0]:
                grid_best = (score, row)

# The global optimizer above answers whether *some* wheel-supported folded pose exists.
# This second sweep answers the practical question: how little must the measured CAD
# hard-stop pose move to put load back on the drive wheels?  Keep the chassis level,
# reserve 2 mrad from the hip limit, and solve the crank/hip difference for several
# central-guide clearances.  A few tenths of a millimetre are deliberately not treated
# as useful clearance because compliant contact can consume them.
near_stop_candidates = []
for hip in np.linspace(hip_target := 0.450290972128024, 0.498, 49):
    for desired_guide_gap in (0.0003, 0.0005, 0.0007, 0.0009, 0.0011):
        result = minimize_scalar(
            lambda difference: abs(
                evaluate((float(hip), float(difference), 0.0))["minimum_guide_gap_m"]
                - desired_guide_gap
            ),
            bounds=(hard_stop, -0.92),
            method="bounded",
            options={"xatol": 1e-13, "maxiter": 1000},
        )
        row = evaluate((float(hip), float(result.x), 0.0))
        if row is None:
            continue
        row["desired_guide_gap_m"] = desired_guide_gap
        row["guide_gap_error_m"] = row["minimum_guide_gap_m"] - desired_guide_gap
        row["delta_from_hard_stop"] = {
            "hip_rad": row["hip_rad"] - hip_target,
            "difference_rad": row["difference_rad"] - hard_stop,
            "crank_rad": row["crank_rad"] - (hip_target + hard_stop),
        }
        row["feasible"] = bool(
            abs(row["guide_gap_error_m"]) <= 1e-6
            and row["minimum_visual_z_m"] >= -1e-5
            and row["tunnel_margin_m"] >= 0.001
            and row["difference_rad"] >= hard_stop - 1e-9
            and row["hip_rad"] <= 0.498 + 1e-12
        )
        if row["feasible"]:
            # Prefer minimum angular motion, then larger contact and roof margins.
            row["near_stop_score"] = float(
                (row["delta_from_hard_stop"]["hip_rad"] / 0.05) ** 2
                + (row["delta_from_hard_stop"]["difference_rad"] / 0.02) ** 2
                - 0.05 * row["minimum_guide_gap_m"] / 0.001
                - 0.02 * row["tunnel_margin_m"] / 0.001
            )
            near_stop_candidates.append(row)

near_stop_candidates.sort(key=lambda row: row["near_stop_score"])
recommended_by_guide_gap = {}
for row in near_stop_candidates:
    key = f"{row['desired_guide_gap_m'] * 1000:.1f}mm"
    if key not in recommended_by_guide_gap:
        recommended_by_guide_gap[key] = row

report = {
    "scope": "symmetric planar near-stop search; both 125 mm main wheels tangent to a rigid floor",
    "constraints": {
        "tunnel_height_m": tunnel_height,
        "required_tunnel_margin_m": 0.001,
        "hard_stop_difference_rad": hard_stop,
        "training_stop_difference_rad": training_stop,
        "visual_floor_tolerance_m": 1e-5,
    },
    "solutions": solutions,
    "grid_best": grid_best[1] if grid_best else None,
    "recommended_near_hard_stop": near_stop_candidates[0] if near_stop_candidates else None,
    "recommended_by_guide_gap": recommended_by_guide_gap,
    "near_hard_stop_candidates": near_stop_candidates[:20],
    "feasible_count": sum(row["feasible"] for row in solutions),
}
OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))

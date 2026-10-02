"""Solve the level MOD4 crouch at the exact CAD hard stop and common ground."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import mujoco
import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "chassis_mod4"
OUT_DIR = ROOT / "chassis_mod4_work" / "folded_pose_sim"
sys.path.insert(0, str(MODEL_DIR))
sys.path.insert(0, str(ROOT / "chassis_mod4_work"))
from kinematics import leg_configuration  # noqa: E402
import simulate_folded_pose as folded  # noqa: E402

hard_stop = json.loads((OUT_DIR / "hard_stop_brep.json").read_text(encoding="utf8"))
difference = float(hard_stop["selected_contact"]["packaged_difference_rad"])

model = folded.model
data = folded.data
wheel_id = model.body("left_wheel").id
guide_radius = 0.015
guide_centre_z = -0.163
root_height = -(guide_centre_z - guide_radius)  # fixed centre minus radius at ground
wheel_radius = 0.0625


def set_unchecked(hip: float, pitch: float = 0.0, height: float = root_height):
    data.qpos[:] = model.qpos0
    data.qvel[:] = 0
    data.qpos[:3] = (0, 0, height)
    data.qpos[3:7] = (math.cos(pitch / 2), 0, math.sin(pitch / 2), 0)
    values_by_side = {}
    for side in ("left", "right"):
        values, _ = leg_configuration(hip, difference, side)
        values_by_side[side] = values
        for name, value in values.items():
            data.qpos[model.joint(f"{side}_{name}").qposadr[0]] = value
    mujoco.mj_forward(model, data)
    return values_by_side


def wheel_gap(hip: float) -> float:
    set_unchecked(hip)
    return float(data.xpos[wheel_id, 2] - wheel_radius)


def set_main_wheel_grounded(hip: float):
    values = set_unchecked(hip, height=0.0)
    required_height = wheel_radius - float(data.xpos[wheel_id, 2])
    values = set_unchecked(hip, height=required_height)
    return values, required_height


def envelope_row(hip: float):
    values, required_height = set_main_wheel_grounded(hip)
    full_low = float("inf")
    full_top = -float("inf")
    leg_top = -float("inf")
    leg_top_body = None
    low_body = None
    for body_id, hull in folded.HULLS.items():
        mat = data.xmat[body_id].reshape(3, 3)
        z = hull @ mat[2, (0, 2)] + data.xpos[body_id, 2]
        if float(z.min()) < full_low:
            full_low = float(z.min())
            low_body = model.body(body_id).name
        full_top = max(full_top, float(z.max()))
        if body_id != folded.CHASSIS and float(z.max()) > leg_top:
            leg_top = float(z.max())
            leg_top_body = model.body(body_id).name
    return {
        "hip_rad": hip,
        "difference_rad": difference,
        "root_height_m": required_height,
        "wheel_center_xz_m": data.xpos[wheel_id, (0, 2)].tolist(),
        "wheel_ground_gap_m": float(data.xpos[wheel_id, 2] - wheel_radius),
        "central_guide_ground_gap_m": required_height - root_height,
        "leg_height_m": leg_top,
        "leg_height_error_vs_solidworks_m": leg_top - 0.22336,
        "leg_top_body": leg_top_body,
        "full_height_m": full_top,
        "lowest_visual_m": full_low,
        "lowest_visual_body": low_body,
        "joint_values_rad": values,
        "current_hip_limit_ok": bool(-0.5 <= hip <= 0.5),
        "current_difference_limit_ok": bool(-0.7 <= difference <= 0.4),
    }


samples = []
grid = np.linspace(-1.5, 1.2, 271)
previous = (float(grid[0]), wheel_gap(float(grid[0])))
for value in grid[1:]:
    current = (float(value), wheel_gap(float(value)))
    if previous[1] == 0 or current[1] == 0 or previous[1] * current[1] < 0:
        root = brentq(wheel_gap, previous[0], current[0], xtol=1e-13, rtol=1e-13)
        if not samples or abs(root - samples[-1]) > 1e-7:
            samples.append(root)
    previous = current

co_ground_solutions = []
for hip in samples:
    values = set_unchecked(hip)
    # Use the exact visual CAD mesh envelope. Main wheel and central guide rollers
    # are on the floor by construction; this exposes any other ground collision.
    row = {"hip_rad": hip, "difference_rad": difference}
    full_low = float("inf")
    full_top = -float("inf")
    leg_top = -float("inf")
    leg_top_body = None
    low_body = None
    for body_id, hull in folded.HULLS.items():
        mat = data.xmat[body_id].reshape(3, 3)
        z = hull @ mat[2, (0, 2)] + data.xpos[body_id, 2]
        if float(z.min()) < full_low:
            full_low = float(z.min())
            low_body = model.body(body_id).name
        full_top = max(full_top, float(z.max()))
        if body_id != folded.CHASSIS and float(z.max()) > leg_top:
            leg_top = float(z.max())
            leg_top_body = model.body(body_id).name
    row.update(
        root_height_m=root_height,
        wheel_center_xz_m=data.xpos[wheel_id, (0, 2)].tolist(),
        wheel_ground_gap_m=wheel_gap(hip),
        central_guide_ground_gap_m=0.0,
        leg_height_m=leg_top,
        leg_height_error_vs_solidworks_m=leg_top - 0.22336,
        leg_top_body=leg_top_body,
        full_height_m=full_top,
        lowest_visual_m=full_low,
        lowest_visual_body=low_body,
        joint_values_rad=values,
        current_hip_limit_ok=bool(-0.5 <= hip <= 0.5),
        current_difference_limit_ok=bool(-0.7 <= difference <= 0.4),
    )
    co_ground_solutions.append(row)

# The screenshot says the drive wheel grazes the floor and provides an explicit
# 223.36 mm leg envelope. These two constraints determine hip at the BRep stop.
height_solutions = []
grid = np.linspace(-1.5, 1.2, 541)
previous = (float(grid[0]), envelope_row(float(grid[0]))["leg_height_error_vs_solidworks_m"])
for value in grid[1:]:
    current_row = envelope_row(float(value))
    current = (float(value), current_row["leg_height_error_vs_solidworks_m"])
    if previous[1] == 0 or current[1] == 0 or previous[1] * current[1] < 0:
        root = brentq(
            lambda hip: envelope_row(hip)["leg_height_error_vs_solidworks_m"],
            previous[0], current[0], xtol=1e-13, rtol=1e-13,
        )
        if not height_solutions or abs(root - height_solutions[-1]["hip_rad"]) > 1e-7:
            height_solutions.append(envelope_row(root))
    previous = current

report = {
    "constraint": "level chassis; exact B-Rep hard stop; main drive-wheel tangent is the SolidWorks 223.36 mm datum",
    "solidworks_measured_leg_height_m": 0.22336,
    "hard_stop": hard_stop["selected_contact"],
    "exact_co_ground_solutions": co_ground_solutions,
    "main_wheel_ground_and_223mm_solutions": height_solutions,
}
OUT = OUT_DIR / "grounded_hard_stop_pose.json"
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")
print(json.dumps(report, ensure_ascii=False, indent=2))

# Render the root that is closest to the measured 223.36 mm envelope.
if height_solutions:
    # Screenshot has the wheel nearly centred under the chassis. Prefer the root
    # with smallest wheel-centre X displacement from chassis origin.
    chosen = min(height_solutions, key=lambda row: abs(row["wheel_center_xz_m"][0]))
    set_main_wheel_grounded(chosen["hip_rad"])
    folded.render(OUT_DIR / "grounded_hard_stop_pose.png")

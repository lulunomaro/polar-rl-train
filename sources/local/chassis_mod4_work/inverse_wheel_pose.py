"""Inverse-fit MOD4 leg inputs from the SolidWorks crouch wheel centre."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import mujoco
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "chassis_mod4"
sys.path.insert(0, str(MODEL_DIR))
from kinematics import leg_configuration  # noqa: E402

model = mujoco.MjModel.from_xml_path(str(MODEL_DIR / "scene.xml"))
data = mujoco.MjData(model)
wheel = model.body("left_wheel").id


def wheel_xz(q):
    hip, difference = map(float, q)
    data.qpos[:] = model.qpos0
    data.qpos[:3] = 0
    for side in ("left", "right"):
        values, _ = leg_configuration(hip, difference, side)
        for name, value in values.items():
            joint = model.joint(f"{side}_{name}")
            data.qpos[joint.qposadr[0]] = value
    mujoco.mj_kinematics(model, data)
    return data.xpos[wheel, (0, 2)].copy()


# Estimated from the central fixed guide rollers in the supplied side screenshot.
# The uncertainty deliberately covers a few pixels of occlusion/perspective.
targets = {
    "central_guides_fit": np.array([0.014, -0.119]),
    "far_guides_fit": np.array([0.0334, -0.1167]),
}
results = {}
for name, target in targets.items():
    sol = least_squares(
        lambda q: wheel_xz(q) - target,
        x0=np.array([-0.4, -0.2]),
        bounds=([-1.6, -1.1], [1.0, 0.8]),
        xtol=1e-14,
        ftol=1e-14,
        gtol=1e-14,
        max_nfev=2000,
    )
    results[name] = {
        "target_wheel_xz_m": target.tolist(),
        "hip_rad": float(sol.x[0]),
        "input_difference_rad": float(sol.x[1]),
        "fit_wheel_xz_m": wheel_xz(sol.x).tolist(),
        "residual_m": (wheel_xz(sol.x) - target).tolist(),
        "within_current_limits": bool(-0.5 <= sol.x[0] <= 0.5 and -0.7 <= sol.x[1] <= 0.4),
    }
print(json.dumps(results, indent=2))

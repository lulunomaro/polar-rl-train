"""Render candidate SolidWorks hard-stop poses, including out-of-date limits."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "chassis_mod4"
OUT = ROOT / "chassis_mod4_work" / "folded_pose_sim"
sys.path.insert(0, str(MODEL_DIR))
from kinematics import leg_configuration  # noqa: E402

model = mujoco.MjModel.from_xml_path(str(MODEL_DIR / "scene.xml"))
data = mujoco.MjData(model)
chassis = model.body("chassis").id
wheel = model.body("left_wheel").id


def mesh_hulls():
    grouped = {}
    rot9 = np.empty(9)
    for gid in range(model.ngeom):
        if model.geom_type[gid] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        mid = int(model.geom_dataid[gid])
        lo = int(model.mesh_vertadr[mid])
        hi = lo + int(model.mesh_vertnum[mid])
        verts = model.mesh_vert[lo:hi].astype(float)
        mujoco.mju_quat2Mat(rot9, model.geom_quat[gid])
        verts = verts @ rot9.reshape(3, 3).T + model.geom_pos[gid]
        grouped.setdefault(int(model.geom_bodyid[gid]), []).append(verts)
    return {bid: np.concatenate(vs)[:, (0, 2)] for bid, vs in grouped.items()}


hulls = mesh_hulls()


def set_unchecked(hip, difference):
    data.qpos[:] = model.qpos0
    data.qvel[:] = 0
    data.qpos[:3] = (0, 0, 0.178)  # central guide rollers: z=-.163, r=.015
    data.qpos[3:7] = (1, 0, 0, 0)
    for side in ("left", "right"):
        values, _ = leg_configuration(hip, difference, side)
        for name, value in values.items():
            data.qpos[model.joint(f"{side}_{name}").qposadr[0]] = value
    mujoco.mj_forward(model, data)


def extrema():
    leg_top = -1e9
    full_top = -1e9
    full_low = 1e9
    for bid, xz in hulls.items():
        mat = data.xmat[bid].reshape(3, 3)
        z = xz @ mat[2, (0, 2)] + data.xpos[bid, 2]
        full_low = min(full_low, float(z.min()))
        full_top = max(full_top, float(z.max()))
        if bid != chassis:
            leg_top = max(leg_top, float(z.max()))
    wheel_bottom = float(data.xpos[wheel, 2] - 0.0625)
    return leg_top, full_top, full_low, wheel_bottom


def render_one(path):
    renderer = mujoco.Renderer(model, height=520, width=860)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = data.xpos[chassis]
    cam.distance = 0.92
    cam.azimuth = 90
    cam.elevation = 0
    renderer.update_scene(data, camera=cam)
    image = renderer.render()
    renderer.close()
    Image.fromarray(image).save(path)


candidates = [
    (-0.50, -0.70),
    (0.30, -1.03),
    (0.40, -1.05),
    (0.48, -1.042),
    (0.50, -1.06),
]
panels = []
for i, (hip, difference) in enumerate(candidates):
    set_unchecked(hip, difference)
    metrics = extrema()
    path = OUT / f"stop_candidate_{i}.png"
    render_one(path)
    panel = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, 0, 860, 34), fill="black")
    draw.text(
        (8, 8),
        f"hip {hip:+.3f}  diff {difference:+.3f}  leg {metrics[0]*1000:.1f} mm  "
        f"wheel gap {metrics[3]*1000:+.1f} mm  low {metrics[2]*1000:+.1f} mm",
        fill=(255, 220, 0),
    )
    panels.append(panel)

grid = Image.new("RGB", (860, 520 * len(panels)), "black")
for i, panel in enumerate(panels):
    grid.paste(panel, (0, i * 520))
grid.save(OUT / "stop_candidates.png")
print(OUT / "stop_candidates.png")

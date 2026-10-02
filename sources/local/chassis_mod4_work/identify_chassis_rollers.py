"""Identify chassis-mounted CAD meshes that can act as tunnel support rollers.

Read-only audit: no STEP, MJCF, or package file is modified.
"""
from __future__ import annotations

import json
from pathlib import Path

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "chassis_mod4"
OUT = ROOT / "chassis_mod4_work" / "folded_pose_sim" / "chassis_mesh_audit.json"

model = mujoco.MjModel.from_xml_path(str(MODEL_DIR / "scene.xml"))
parts = json.loads((MODEL_DIR / "reports" / "cad_parts.json").read_text(encoding="utf8"))
part_by_id = {int(row["id"]): row for row in parts}
chassis_id = model.body("chassis").id


def mesh_vertices_in_body(geom_id: int) -> np.ndarray:
    mesh_id = int(model.geom_dataid[geom_id])
    first = int(model.mesh_vertadr[mesh_id])
    last = first + int(model.mesh_vertnum[mesh_id])
    verts = model.mesh_vert[first:last].astype(float)
    rot9 = np.empty(9)
    mujoco.mju_quat2Mat(rot9, model.geom_quat[geom_id])
    return verts @ rot9.reshape(3, 3).T + model.geom_pos[geom_id]


rows = []
for geom_id in range(model.ngeom):
    if int(model.geom_bodyid[geom_id]) != chassis_id:
        continue
    if model.geom_type[geom_id] != mujoco.mjtGeom.mjGEOM_MESH:
        continue
    geom_name = model.geom(geom_id).name
    try:
        part_id = int(geom_name.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        part_id = -1
    vertices = mesh_vertices_in_body(geom_id)
    low = vertices.min(axis=0)
    high = vertices.max(axis=0)
    size = high - low
    centre = (low + high) / 2
    part = part_by_id.get(part_id, {})
    cylinders = part.get("cylinders", [])
    rows.append(
        {
            "geom_id": geom_id,
            "geom_name": geom_name,
            "part_id": part_id,
            "part_name": part.get("name"),
            "path": part.get("path"),
            "aabb_min_m": low.tolist(),
            "aabb_max_m": high.tolist(),
            "aabb_size_m": size.tolist(),
            "aabb_centre_m": centre.tolist(),
            "cylinders": cylinders,
        }
    )

# Candidate roller discs: compact in X/Z, thin in Y, low on the chassis and away
# from the centre. The loose threshold leaves room for guards and tyre meshes.
candidates = [
    row
    for row in rows
    if row["aabb_min_m"][2] < -0.02
    and abs(row["aabb_centre_m"][0]) > 0.18
    and row["aabb_size_m"][0] < 0.10
    and row["aabb_size_m"][2] < 0.10
]
candidates.sort(key=lambda row: (row["aabb_min_m"][2], -abs(row["aabb_centre_m"][0])))
low_sorted = sorted(rows, key=lambda row: row["aabb_min_m"][2])[:80]

report = {
    "chassis_body_id": int(chassis_id),
    "chassis_mesh_count": len(rows),
    "candidate_count": len(candidates),
    "candidates": candidates,
    "lowest_80_chassis_meshes": low_sorted,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")

print(f"wrote {OUT}")
print("candidate rollers:")
for row in candidates:
    c = row["aabb_centre_m"]
    s = row["aabb_size_m"]
    print(
        f"{row['geom_name']:>12}  {row['part_name']}  "
        f"center=({c[0]:+.4f},{c[1]:+.4f},{c[2]:+.4f})  "
        f"size=({s[0]:.4f},{s[1]:.4f},{s[2]:.4f})"
    )

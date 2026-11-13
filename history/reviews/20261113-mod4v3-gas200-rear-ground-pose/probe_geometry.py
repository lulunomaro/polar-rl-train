"""Read-only MOD4v3 stop and rear-fold geometry probe; no dynamics."""
from pathlib import Path
import json
import sys

import mujoco
import numpy as np

ASSET = Path(r"F:\RMPOLAR-RL\mod4v3_scut_semantics_20261106\review_r3\corrected")
sys.path.insert(0, str(ASSET))
import kinematics

m = mujoco.MjModel.from_xml_path(str(ASSET / "mjcf/scene.xml"))
d = mujoco.MjData(m)
runtime = json.loads((ASSET / "runtime_config.json").read_text())
rear0 = runtime["initial_joint_positions"]["left_rear1_joint"]
front0 = runtime["initial_joint_positions"]["left_front1_joint"]
lo, hi = kinematics.mechanical_delta_bounds()
print(json.dumps(dict(model=mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, 1),
    delta_bounds_v3=[lo, hi], default_front=front0, default_rear=rear0,
    lower_legacy=kinematics._modules()[1].boundary_report()), indent=2))

base = m.body("base_link").id
leg_roots = {m.body(s + "_" + n + "_link").id
             for s in ("left", "right") for n in ("front1", "rear1")}
def leg_descendant(bid):
    while bid > 0:
        if bid in leg_roots:
            return True
        bid = int(m.body_parentid[bid])
    return False

fixed_geoms = [i for i in range(m.ngeom)
               if (m.geom_contype[i] or m.geom_conaffinity[i])
               and m.geom_bodyid[i] and not leg_descendant(int(m.geom_bodyid[i]))]

def min_z(gid):
    rotation = d.geom_xmat[gid].reshape(3, 3)
    if m.geom_type[gid] == mujoco.mjtGeom.mjGEOM_MESH:
        mid = m.geom_dataid[gid]
        vertices = m.mesh_vert[m.mesh_vertadr[mid]:m.mesh_vertadr[mid]+m.mesh_vertnum[mid]]
        return float((vertices @ rotation.T + d.geom_xpos[gid])[:, 2].min())
    if m.geom_type[gid] == mujoco.mjtGeom.mjGEOM_CYLINDER:
        axis = rotation[:, 2]
        dz = m.geom_size[gid, 1]*abs(axis[2]) + m.geom_size[gid, 0]*np.sqrt(max(0., 1.-axis[2]**2))
    elif m.geom_type[gid] == mujoco.mjtGeom.mjGEOM_BOX:
        dz = float(np.dot(abs(rotation[2]), m.geom_size[gid]))
    elif m.geom_type[gid] == mujoco.mjtGeom.mjGEOM_SPHERE:
        dz = m.geom_size[gid, 0]
    else:
        dz = m.geom_rbound[gid]
    return float(d.geom_xpos[gid, 2] - dz)

rows=[]
for alpha in np.linspace(-np.pi, np.pi, 13):
    rear = rear0 + float(alpha)
    front = rear + lo
    kinematics.set_configuration(m, d, left=(front, rear), right=(front, rear))
    fixed = sorted((min_z(i), m.geom(i).name, m.body(int(m.geom_bodyid[i])).name) for i in fixed_geoms)
    hip = d.xpos[m.body("left_rear1_link").id]
    wheel = d.xpos[m.body("left_wheel_link").id]
    tire = min_z(m.geom("left_tire").id)
    rows.append(dict(alpha_deg=float(np.degrees(alpha)), front=front, rear=rear,
        wheel_in_base=(wheel-d.xpos[base]).tolist(), wheel_from_hip=(wheel-hip).tolist(),
        tire_minus_chassis=tire-fixed[0][0], fixed_lowest=fixed[:3],
        ncontact=d.ncon, penetrations=[dict(g1=m.geom(c.geom1).name,g2=m.geom(c.geom2).name,dist=c.dist)
            for c in d.contact if c.dist < -1e-4][:12]))
print(json.dumps(rows,indent=2))

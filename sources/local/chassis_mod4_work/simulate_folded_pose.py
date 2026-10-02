"""Solve and dynamically check the lowest symmetric MOD4 folded pose.

This is an audit helper.  It reads the delivered MJCF/CAD meshes and writes a
JSON report plus an off-screen render; it never edits the source model.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import mujoco
import numpy as np
from scipy.optimize import differential_evolution
from scipy.spatial import ConvexHull


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "chassis_mod4"
OUT = ROOT / "chassis_mod4_work" / "folded_pose_sim"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(MODEL_DIR))
from kinematics import PARAMS, leg_configuration  # noqa: E402

TARGET_LEG_HEIGHT = 0.22336
TUNNEL_HEIGHT = 0.2472
WHEEL_RADIUS = float(PARAMS["wheel_motor"]["wheel_radius_m"])


model = mujoco.MjModel.from_xml_path(str(MODEL_DIR / "scene.xml"))
data = mujoco.MjData(model)
parts = json.loads((MODEL_DIR / "reports" / "cad_parts.json").read_text(encoding="utf8"))


def mesh_hulls():
    """Return an X/Z convex hull for every body carrying visual CAD meshes."""
    grouped: dict[int, list[np.ndarray]] = {}
    rot = np.empty(9)
    for geom_id in range(model.ngeom):
        if model.geom_type[geom_id] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        mesh_id = int(model.geom_dataid[geom_id])
        start = int(model.mesh_vertadr[mesh_id])
        stop = start + int(model.mesh_vertnum[mesh_id])
        verts = model.mesh_vert[start:stop].astype(float)
        mujoco.mju_quat2Mat(rot, model.geom_quat[geom_id])
        verts = verts @ rot.reshape(3, 3).T + model.geom_pos[geom_id]
        grouped.setdefault(int(model.geom_bodyid[geom_id]), []).append(verts)
    result = {}
    for body_id, chunks in grouped.items():
        xz = np.concatenate(chunks)[:, (0, 2)]
        result[body_id] = xz[ConvexHull(xz).vertices]
    return result


HULLS = mesh_hulls()
CHASSIS = model.body("chassis").id
WHEELS = [model.body("left_wheel").id, model.body("right_wheel").id]
LEG_BODIES = set(HULLS) - {CHASSIS}
JOINTS = {
    side: {name: model.joint(side + "_" + name).id for name in leg_configuration(0, 0, side)[0]}
    for side in ("left", "right")
}


def set_pose(hip: float, difference: float, pitch: float, ground_clearance: float):
    data.qpos[:] = model.qpos0
    data.qvel[:] = 0
    data.qpos[:3] = 0
    data.qpos[3:7] = (math.cos(pitch / 2), 0, math.sin(pitch / 2), 0)
    joint_values = {}
    for side in ("left", "right"):
        values, _ = leg_configuration(hip, difference, side)
        joint_values[side] = values
        for name, value in values.items():
            joint_id = JOINTS[side][name]
            if model.jnt_limited[joint_id]:
                lo, hi = model.jnt_range[joint_id]
                if value < lo - 1e-8 or value > hi + 1e-8:
                    raise ValueError(f"{side}_{name} outside joint limits")
            data.qpos[model.jnt_qposadr[joint_id]] = value
    mujoco.mj_kinematics(model, data)
    # Both symmetric wheel centres have the same Z.  Put their tire tread on Z=0.
    data.qpos[2] = WHEEL_RADIUS - data.xpos[WHEELS[0], 2]
    mujoco.mj_kinematics(model, data)

    def extrema(body_ids):
        lows, highs = [], []
        for body_id in body_ids:
            hull = HULLS[body_id]
            mat = data.xmat[body_id].reshape(3, 3)
            z = hull @ mat[2, (0, 2)] + data.xpos[body_id, 2]
            lows.append((float(z.min()), body_id))
            highs.append((float(z.max()), body_id))
        return min(lows), max(highs)

    nonwheel = set(HULLS) - set(WHEELS)
    low_nonwheel, _ = extrema(nonwheel)
    # Lift the whole model if a requested non-wheel clearance is not met.
    if low_nonwheel[0] < ground_clearance:
        data.qpos[2] += ground_clearance - low_nonwheel[0]
        mujoco.mj_kinematics(model, data)
        low_nonwheel, _ = extrema(nonwheel)
    low_all, top_all = extrema(set(HULLS))
    _, top_leg = extrema(LEG_BODIES)
    _, top_chassis = extrema({CHASSIS})
    return {
        "hip_rad": float(hip),
        "input_difference_rad": float(difference),
        "pitch_rad": float(pitch),
        "root_height_m": float(data.qpos[2]),
        "leg_height_m": top_leg[0],
        "leg_top_body": model.body(top_leg[1]).name,
        "full_height_m": top_all[0],
        "full_top_body": model.body(top_all[1]).name,
        "chassis_height_m": top_chassis[0],
        "lowest_m": low_all[0],
        "lowest_nonwheel_m": low_nonwheel[0],
        "lowest_nonwheel_body": model.body(low_nonwheel[1]).name,
        "joint_values_rad": joint_values,
    }


BOUNDS = [tuple(PARAMS["hip_range_rad"]), tuple(PARAMS["limits"]["left"]["input_difference_rad"]),
          (-math.radians(8), math.radians(8))]


def solve(ground_clearance: float):
    def objective(x):
        try:
            row = set_pose(*x, ground_clearance)
        except ValueError:
            return 10.0
        # Folded posture: minimize the moving leg envelope; keep pitch modest.
        return row["leg_height_m"] + 0.002 * abs(x[2])

    sol = differential_evolution(objective, BOUNDS, seed=22336, popsize=16,
                                 maxiter=220, tol=1e-10, polish=True, workers=1)
    row = set_pose(*sol.x, ground_clearance)
    row.update(search_success=bool(sol.success), evaluations=int(sol.nfev), objective=float(sol.fun),
               requested_nonwheel_clearance_m=ground_clearance,
               target_leg_height_m=TARGET_LEG_HEIGHT,
               target_error_m=row["leg_height_m"] - TARGET_LEG_HEIGHT,
               tunnel_margin_leg_m=TUNNEL_HEIGHT - row["leg_height_m"],
               tunnel_margin_full_m=TUNNEL_HEIGHT - row["full_height_m"])
    return row


def closure_errors():
    out = {}
    for name in ("left_proximal", "left_distal", "left_gas", "right_proximal", "right_distal", "right_gas"):
        a = data.site(name + "_a").xpos if name.endswith(("proximal", "distal")) else data.site(name + "_end").xpos
        b = data.site(name + "_b").xpos if name.endswith(("proximal", "distal")) else data.site(name + "_mount").xpos
        out[name] = float(np.linalg.norm(a - b))
    for side in ("left", "right"):
        for driven, source in (("drive_hip_spin", "hip"), ("drive_input_spin", "crank")):
            q0 = data.qpos[model.joint(f"{side}_{driven}").qposadr[0]]
            q1 = data.qpos[model.joint(f"{side}_{source}").qposadr[0]]
            out[f"{side}_{driven}"] = float(abs(q0 - q1))
    return out


def render(path: Path):
    mujoco.mj_forward(model, data)
    renderer = mujoco.Renderer(model, height=720, width=1100)
    camera = mujoco.MjvCamera()
    camera.type = mujoco.mjtCamera.mjCAMERA_FREE
    camera.lookat[:] = data.xpos[CHASSIS]
    camera.distance = 1.05
    camera.azimuth = 90
    camera.elevation = 0
    renderer.update_scene(data, camera=camera)
    image = renderer.render()
    try:
        from PIL import Image
        Image.fromarray(image).save(path)
    finally:
        renderer.close()


def dynamic_hold(row, duration_s=2.0):
    set_pose(row["hip_rad"], row["input_difference_rad"], row["pitch_rad"],
             row["requested_nonwheel_clearance_m"])
    mujoco.mj_forward(model, data)
    leg_targets = np.array([
        row["joint_values_rad"]["left"]["hip"],
        row["joint_values_rad"]["left"]["crank"],
        row["joint_values_rad"]["right"]["hip"],
        row["joint_values_rad"]["right"]["crank"],
    ])
    leg_actuators = [model.actuator(n).id for n in
                     ("left_hip_motor", "left_crank_motor", "right_hip_motor", "right_crank_motor")]
    leg_joints = [model.joint(n).id for n in
                  ("left_hip", "left_crank", "right_hip", "right_crank")]
    qadr = np.array([model.jnt_qposadr[j] for j in leg_joints])
    vadr = np.array([model.jnt_dofadr[j] for j in leg_joints])
    max_closure = 0.0
    max_full_height = 0.0
    min_nonwheel = float("inf")
    max_torque = 0.0
    samples = []
    steps = int(duration_s / model.opt.timestep)
    for step in range(steps):
        err = (leg_targets - data.qpos[qadr] + math.pi) % (2 * math.pi) - math.pi
        tau = np.clip(180.0 * err - 7.0 * data.qvel[vadr], -40.0, 40.0)
        data.ctrl[:] = 0
        data.ctrl[leg_actuators] = tau
        mujoco.mj_step(model, data)
        if step % 20 == 0 or step == steps - 1:
            # Reuse the transformed hull calculation without resetting the state.
            low_nonwheel = float("inf")
            full_height = -float("inf")
            for body_id, hull in HULLS.items():
                mat = data.xmat[body_id].reshape(3, 3)
                z = hull @ mat[2, (0, 2)] + data.xpos[body_id, 2]
                full_height = max(full_height, float(z.max()))
                if body_id not in WHEELS:
                    low_nonwheel = min(low_nonwheel, float(z.min()))
            ce = closure_errors()
            max_closure = max(max_closure, max(ce.values()))
            max_full_height = max(max_full_height, full_height)
            min_nonwheel = min(min_nonwheel, low_nonwheel)
            max_torque = max(max_torque, float(np.max(np.abs(tau))))
            if step % 400 == 0 or step == steps - 1:
                samples.append({"time_s": float(data.time), "root_z_m": float(data.qpos[2]),
                                "full_height_m": full_height, "lowest_nonwheel_m": low_nonwheel,
                                "max_closure_m": max(ce.values()), "ncon": int(data.ncon),
                                "max_leg_torque_nm": float(np.max(np.abs(tau)))})
    return {"duration_s": duration_s, "max_closure_error_m": max_closure,
            "max_full_height_m": max_full_height, "min_nonwheel_m": min_nonwheel,
            "max_leg_torque_nm": max_torque, "final_root_z_m": float(data.qpos[2]),
            "final_q_error_rad": float(np.max(np.abs(leg_targets - data.qpos[qadr]))),
            "samples": samples}


if __name__ == "__main__":
    report = {
        "scope": "All moving MOD4 leg CAD meshes; chassis reported separately. Symmetric legs, joint limits enforced.",
        "target_leg_height_m": TARGET_LEG_HEIGHT,
        "tunnel_height_m": TUNNEL_HEIGHT,
        "solutions": {
            "clearance_3mm": solve(0.003),
            "clearance_0mm": solve(0.0),
        },
    }
    selected = report["solutions"]["clearance_3mm"]
    set_pose(selected["hip_rad"], selected["input_difference_rad"], selected["pitch_rad"], 0.003)
    mujoco.mj_forward(model, data)
    report["selected_closure_error_m"] = closure_errors()
    render(OUT / "folded_pose.png")
    report["dynamic_hold_zero_wheel_control"] = dynamic_hold(selected)
    path = OUT / "folded_pose_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"WROTE {path}")

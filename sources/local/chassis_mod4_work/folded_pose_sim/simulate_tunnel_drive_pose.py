"""Drive the corrected MOD4 through a rigid 247.2 mm tunnel in MuJoCo.

The source MJCF/CAD assets are read-only.  This script builds a temporary scene with
an actual roof collider, starts from a near-hard-stop pose found from the full 277-mesh
CAD envelope, and checks traction, roof clearance and closed-chain integrity.
"""
from __future__ import annotations

import json
import math
import sys
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "chassis_mod4"
HERE = Path(__file__).resolve().parent
SOURCE_XML = HERE / "scene_hard_stop_audit.xml"
SCENE_XML = HERE / "scene_tunnel_247p2_drive.xml"
SEARCH_REPORT = HERE / "drive_contact_pose_search.json"
REPORT_PATH = HERE / "tunnel_drive_dynamic_report.json"
STORYBOARD_PATH = HERE / "tunnel_drive_storyboard.png"
ANIMATION_PATH = HERE / "tunnel_drive_0p18mps.gif"
TIMESERIES_PATH = HERE / "tunnel_drive_timeseries_0p18.npz"
sys.path.insert(0, str(MODEL_DIR))
from kinematics import leg_configuration  # noqa: E402


TUNNEL_HEIGHT = 0.2472
ROOF_X_MIN = -0.17
ROOF_X_MAX = 0.17
ROOF_HALF_THICKNESS = 0.020
START_X = -0.49
GUIDE_CHOICE = "0.7mm"


def build_scene() -> None:
    tree = ET.parse(SOURCE_XML)
    root = tree.getroot()
    world = root.find("worldbody")
    assert world is not None
    chassis = world.find(".//body[@name='chassis']")
    assert chassis is not None
    # The CAD parts are rollers, but the earlier audit scene attached their cylinders
    # rigidly to the chassis.  Turn them into passive hinge bodies for this locomotion
    # test; otherwise MuJoCo correctly treats them as eight skids and the test measures
    # sliding friction rather than the real rolling mechanism.
    fixed_guides = [
        geom for geom in list(chassis)
        if geom.tag == "geom" and geom.get("name", "").startswith("guide_roller_collision_")
    ]
    for geom in fixed_guides:
        index = int(geom.get("name").rsplit("_", 1)[1])
        body = ET.SubElement(chassis, "body", {
            "name": f"guide_roller_{index}", "pos": geom.get("pos")
        })
        ET.SubElement(body, "joint", {
            "name": f"guide_roller_spin_{index}", "type": "hinge", "axis": "0 1 0",
            "limited": "false", "damping": ".0002", "armature": ".00001",
        })
        ET.SubElement(body, "inertial", {
            "mass": ".01", "pos": "0 0 0", "diaginertia": ".00000065 .000001125 .00000065",
        })
        attrs = dict(geom.attrib)
        attrs["pos"] = "0 0 0"
        ET.SubElement(body, "geom", attrs)
        chassis.remove(geom)
    ET.SubElement(
        world,
        "geom",
        {
            "name": "tunnel_roof_247p2",
            "type": "box",
            "pos": f"0 0 {TUNNEL_HEIGHT + ROOF_HALF_THICKNESS}",
            "size": f"{(ROOF_X_MAX - ROOF_X_MIN) / 2} .65 {ROOF_HALF_THICKNESS}",
            "rgba": ".78 .47 .12 .45",
            "contype": "1",
            "conaffinity": "2",
            "friction": ".8 .003 .0001",
        },
    )
    ET.indent(tree, space="  ")
    tree.write(SCENE_XML, encoding="utf8", xml_declaration=True)


build_scene()
search = json.loads(SEARCH_REPORT.read_text(encoding="utf8"))
pose = search["recommended_by_guide_gap"][GUIDE_CHOICE]
hip_target = float(pose["hip_rad"])
difference_target = float(pose["difference_rad"])
crank_target = float(pose["crank_rad"])
root_target = float(pose["root_height_m"])


def make_model_data():
    model = mujoco.MjModel.from_xml_path(str(SCENE_XML))
    data = mujoco.MjData(model)
    return model, data


def set_pose(model, data):
    data.qpos[:] = model.qpos0
    data.qvel[:] = 0
    data.qpos[:3] = (START_X, 0, root_target)
    data.qpos[3:7] = (1, 0, 0, 0)
    for side in ("left", "right"):
        values, _ = leg_configuration(hip_target, difference_target, side)
        for name, value in values.items():
            data.qpos[model.joint(f"{side}_{name}").qposadr[0]] = value
    mujoco.mj_forward(model, data)


def visual_meshes(model):
    rows = []
    for geom_id in range(model.ngeom):
        if model.geom_type[geom_id] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        mesh_id = int(model.geom_dataid[geom_id])
        first = int(model.mesh_vertadr[mesh_id])
        last = first + int(model.mesh_vertnum[mesh_id])
        rows.append((geom_id, model.mesh_vert[first:last].astype(float)))
    return rows


def visual_envelope(data, meshes):
    low = float("inf")
    top = -float("inf")
    xmin = float("inf")
    xmax = -float("inf")
    for geom_id, vertices in meshes:
        world = vertices @ data.geom_xmat[geom_id].reshape(3, 3).T + data.geom_xpos[geom_id]
        low = min(low, float(world[:, 2].min()))
        top = max(top, float(world[:, 2].max()))
        xmin = min(xmin, float(world[:, 0].min()))
        xmax = max(xmax, float(world[:, 0].max()))
    return {"low": low, "top": top, "xmin": xmin, "xmax": xmax}


def roll_pitch(q):
    w, x, y, z = q
    roll = math.atan2(2 * (w*x + y*z), 1 - 2 * (x*x + y*y))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (w*y - z*x))))
    return roll, pitch


def closure_error(model, data):
    values = []
    for name in (
        "left_proximal", "left_distal", "left_gas",
        "right_proximal", "right_distal", "right_gas",
    ):
        if name.endswith(("proximal", "distal")):
            a, b = data.site(name + "_a").xpos, data.site(name + "_b").xpos
        else:
            a, b = data.site(name + "_end").xpos, data.site(name + "_mount").xpos
        values.append(float(np.linalg.norm(a - b)))
    return max(values)


def contact_forces(model, data):
    totals = {"wheel_normal_n": 0.0, "wheel_tangent_n": 0.0,
              "guide_normal_n": 0.0, "roof_normal_n": 0.0}
    force = np.zeros(6)
    for index, contact in enumerate(data.contact[: data.ncon]):
        mujoco.mj_contactForce(model, data, index, force)
        names = {model.geom(contact.geom1).name, model.geom(contact.geom2).name}
        normal = max(0.0, float(force[0]))
        if any(name in ("left_tire", "right_tire") for name in names) and "ground" in names:
            totals["wheel_normal_n"] += normal
            totals["wheel_tangent_n"] += float(np.linalg.norm(force[1:3]))
        if any(name.startswith("guide_roller_collision_") for name in names) and "ground" in names:
            totals["guide_normal_n"] += normal
        if "tunnel_roof_247p2" in names:
            totals["roof_normal_n"] += normal
    return totals


def simulate(speed_mps: float, duration_s: float = 8.5):
    model, data = make_model_data()
    set_pose(model, data)
    meshes = visual_meshes(model)
    leg_act = np.array([model.actuator(name).id for name in (
        "left_hip_motor", "left_crank_motor", "right_hip_motor", "right_crank_motor"
    )])
    wheel_act = np.array([model.actuator(name).id for name in (
        "left_wheel_spin_motor", "right_wheel_spin_motor"
    )])
    qadr = np.array([model.joint(name).qposadr[0] for name in (
        "left_hip", "left_crank", "right_hip", "right_crank"
    )])
    vadr = np.array([model.joint(name).dofadr[0] for name in (
        "left_hip", "left_crank", "right_hip", "right_crank"
    )])
    wheel_vadr = np.array([model.joint(name).dofadr[0] for name in (
        "left_wheel_spin", "right_wheel_spin"
    )])
    desired = np.array([hip_target, crank_target, hip_target, crank_target])
    # Feed-forward is taken from the measured hard-stop equilibrium. Integral action
    # removes the small configuration-dependent remainder; both stay below DM8009P limits.
    feed_forward = np.array([8.6, -7.4, 8.6, -7.4])
    integral = np.zeros(4)
    dt = float(model.opt.timestep)
    steps = round(duration_s / dt)
    drive_start_s = 1.0
    ramp_s = 0.8
    envelope_stride = max(1, round(0.025 / dt))
    max_closure = 0.0
    max_leg_torque = 0.0
    max_wheel_torque = 0.0
    max_abs_pitch = 0.0
    max_abs_roll = 0.0
    min_roof_clearance = float("inf")
    roof_contact_steps = 0
    wheel_loaded_steps = 0
    drive_steps = 0
    wheel_normal_integral = 0.0
    guide_normal_integral = 0.0
    wheel_tangent_integral = 0.0
    samples = []
    saved_states = []
    warning_text = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for step in range(steps):
            time = float(data.time)
            error = (desired - data.qpos[qadr] + math.pi) % (2 * math.pi) - math.pi
            integral = np.clip(integral + error * dt, -0.12, 0.12)
            leg_torque = np.clip(feed_forward + 320 * error - 10 * data.qvel[vadr] + 90 * integral,
                                 -40, 40)
            ramp = np.clip((time - drive_start_s) / ramp_s, 0.0, 1.0)
            target_w = ramp * speed_mps / 0.0625
            wheel_torque = np.clip(0.45 * (target_w - data.qvel[wheel_vadr]), -5.7759, 5.7759)
            data.ctrl[:] = 0
            data.ctrl[leg_act] = leg_torque
            data.ctrl[wheel_act] = wheel_torque
            mujoco.mj_step(model, data)
            if not np.isfinite(data.qpos).all():
                break
            max_leg_torque = max(max_leg_torque, float(np.abs(leg_torque).max()))
            max_wheel_torque = max(max_wheel_torque, float(np.abs(wheel_torque).max()))
            roll, pitch = roll_pitch(data.qpos[3:7])
            max_abs_roll = max(max_abs_roll, abs(roll))
            max_abs_pitch = max(max_abs_pitch, abs(pitch))
            if step % 20 == 0:
                max_closure = max(max_closure, closure_error(model, data))
            forces = contact_forces(model, data)
            if forces["roof_normal_n"] > 1e-3:
                roof_contact_steps += 1
            if time >= drive_start_s:
                drive_steps += 1
                wheel_normal_integral += forces["wheel_normal_n"] * dt
                guide_normal_integral += forces["guide_normal_n"] * dt
                wheel_tangent_integral += forces["wheel_tangent_n"] * dt
                if forces["wheel_normal_n"] > 1.0:
                    wheel_loaded_steps += 1
            if step % envelope_stride == 0 or step == steps - 1:
                envelope = visual_envelope(data, meshes)
                overlaps_roof = envelope["xmax"] >= ROOF_X_MIN and envelope["xmin"] <= ROOF_X_MAX
                if overlaps_roof:
                    min_roof_clearance = min(min_roof_clearance, TUNNEL_HEIGHT - envelope["top"])
                samples.append({
                    "time_s": float(data.time), "root_x_m": float(data.qpos[0]),
                    "root_z_m": float(data.qpos[2]), "pitch_rad": pitch,
                    "wheel_normal_n": forces["wheel_normal_n"],
                    "guide_normal_n": forces["guide_normal_n"],
                    "roof_normal_n": forces["roof_normal_n"],
                    "visual_top_m": envelope["top"], "visual_xmin_m": envelope["xmin"],
                    "visual_xmax_m": envelope["xmax"], "overlaps_roof": overlaps_roof,
                })
            if abs(speed_mps - 0.18) < 1e-9 and step % max(1, round(0.20 / dt)) == 0:
                saved_states.append(data.qpos.copy())
            elif len(saved_states) < 3:
                thresholds = (drive_start_s * 0.8, 4.2, duration_s - 0.05)
                if float(data.time) >= thresholds[len(saved_states)]:
                    saved_states.append(data.qpos.copy())
        warning_text = [str(item.message) for item in caught]
    final_envelope = visual_envelope(data, meshes)
    drive_duration = max(dt, float(data.time) - drive_start_s)
    result = {
        "speed_command_mps": speed_mps,
        "status": "PASS" if (
            not warning_text
            and final_envelope["xmin"] > ROOF_X_MAX
            and roof_contact_steps == 0
            and min_roof_clearance > 0
            and wheel_loaded_steps / max(1, drive_steps) > 0.8
            and max_closure < 0.002
        ) else "FAIL",
        "duration_s": float(data.time),
        "root_x_start_m": START_X,
        "root_x_final_m": float(data.qpos[0]),
        "forward_distance_m": float(data.qpos[0]) - START_X,
        "final_visual_xmin_m": final_envelope["xmin"],
        "fully_cleared_roof": bool(final_envelope["xmin"] > ROOF_X_MAX),
        "minimum_dynamic_roof_clearance_m": min_roof_clearance,
        "roof_contact_steps": roof_contact_steps,
        "wheel_loaded_fraction": wheel_loaded_steps / max(1, drive_steps),
        "mean_drive_wheel_normal_force_n": wheel_normal_integral / drive_duration,
        "mean_guide_normal_force_n": guide_normal_integral / drive_duration,
        "mean_wheel_tangent_force_n": wheel_tangent_integral / drive_duration,
        "max_abs_pitch_rad": max_abs_pitch,
        "max_abs_roll_rad": max_abs_roll,
        "max_closure_error_m": max_closure,
        "max_abs_leg_torque_nm": max_leg_torque,
        "max_abs_wheel_torque_nm": max_wheel_torque,
        "warnings": warning_text,
        "samples": samples,
        "saved_states": [row.tolist() for row in saved_states],
    }
    return result


cases = [simulate(0.12, duration_s=10.5), simulate(0.18), simulate(0.25)]
passed = [case for case in cases if case["status"] == "PASS"]
trace_case = next(case for case in cases if abs(case["speed_command_mps"] - 0.18) < 1e-9)
trace_keys = (
    "time_s", "root_x_m", "root_z_m", "pitch_rad", "wheel_normal_n",
    "guide_normal_n", "roof_normal_n", "visual_top_m", "visual_xmin_m",
    "visual_xmax_m", "overlaps_roof",
)
np.savez_compressed(
    TIMESERIES_PATH,
    **{key: np.asarray([sample[key] for sample in trace_case["samples"]]) for key in trace_keys},
)
report = {
    "status": "PASS" if passed else "FAIL",
    "model": str(SCENE_XML),
    "tunnel": {"height_m": TUNNEL_HEIGHT, "x_range_m": [ROOF_X_MIN, ROOF_X_MAX]},
    "pose": {
        "source": f"drive_contact_pose_search.json recommended_by_guide_gap/{GUIDE_CHOICE}",
        "hip_rad": hip_target, "crank_rad": crank_target,
        "difference_rad": difference_target, "root_height_m": root_target,
        "static_guide_clearance_m": pose["minimum_guide_gap_m"],
        "static_full_visual_height_m": pose["full_height_m"],
        "static_tunnel_margin_m": pose["tunnel_margin_m"],
        "delta_from_measured_hard_stop": pose["delta_from_hard_stop"],
    },
        "cases": [{k: v for k, v in case.items() if k not in ("samples", "saved_states")} for case in cases],
    "guide_model": "8 passive hinge rollers; 30 mm diameter, 10 g audit mass each",
    "scope": "Local MuJoCo rigid-floor/rigid-roof test using the corrected closed-chain MJCF and full CAD visual envelope.",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")

# Render a review storyboard from the first passing case (or the least slow failed case).
chosen = passed[0] if passed else cases[0]
model, data = make_model_data()
renderer = mujoco.Renderer(model, height=500, width=900)
camera = mujoco.MjvCamera()
camera.type = mujoco.mjtCamera.mjCAMERA_FREE
camera.lookat[:] = (0, 0, 0.13)
camera.distance = 1.15
camera.azimuth = 90
camera.elevation = 0
frames = []
for state in chosen["saved_states"]:
    data.qpos[:] = state
    data.qvel[:] = 0
    mujoco.mj_forward(model, data)
    renderer.update_scene(data, camera=camera)
    frames.append(Image.fromarray(renderer.render()))
renderer.close()
if frames:
    animation_frames = [frame.resize((720, 400), Image.Resampling.LANCZOS) for frame in frames]
    animation_frames[0].save(
        ANIMATION_PATH, save_all=True, append_images=animation_frames[1:],
        duration=160, loop=0, optimize=True,
    )
    review_frames = [frames[0], frames[len(frames) // 2], frames[-1]]
    canvas = Image.new("RGB", (900, 40 + 500 * len(review_frames)), "white")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 900, 40), fill="black")
    draw.text((12, 12), f"247.2 mm rigid tunnel, command {chosen['speed_command_mps']:.2f} m/s", fill="white")
    for index, frame in enumerate(review_frames):
        canvas.paste(frame, (0, 40 + index * 500))
    canvas.save(STORYBOARD_PATH)

print(json.dumps(report, ensure_ascii=False, indent=2))

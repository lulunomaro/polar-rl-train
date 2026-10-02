"""Build a temporary corrected MJCF and dynamically test the tunnel crouch.

The delivered MJCF and the STEP/SolidWorks sources stay untouched. The audit
copy expands passive joint limits to the exact B-Rep stop and gives all eight
30 mm chassis guide rollers analytic collision cylinders.
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


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "chassis_mod4"
OUT = ROOT / "chassis_mod4_work" / "folded_pose_sim"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(MODEL_DIR))
from kinematics import leg_configuration  # noqa: E402

pose_report = json.loads((OUT / "grounded_hard_stop_pose.json").read_text(encoding="utf8"))
pose = pose_report["main_wheel_ground_and_223mm_solutions"][0]
stop_difference = float(pose["difference_rad"])
hip_target = float(pose["hip_rad"])
values_at_stop, _ = leg_configuration(hip_target, stop_difference, "left")

# Build the audit XML beside its report, pointing meshdir back to the package.
tree = ET.parse(MODEL_DIR / "scene.xml")
root = tree.getroot()
compiler = root.find("compiler")
compiler.set("meshdir", (MODEL_DIR / "assets").as_posix())

for side in ("left", "right"):
    for name, stop_value in values_at_stop.items():
        if name in ("hip", "crank", "drive_hip_spin", "drive_input_spin", "wheel_spin"):
            continue
        joint = root.find(f".//joint[@name='{side}_{name}']")
        if joint is None or "range" not in joint.attrib:
            continue
        lo, hi = map(float, joint.get("range").split())
        lo = min(lo, float(stop_value))
        hi = max(hi, float(stop_value))
        joint.set("range", f"{lo:.15g} {hi:.15g}")

chassis = root.find(".//body[@name='chassis']")
assert chassis is not None
roller_centres = [
    # Four central rollers that graze the floor in the supplied crouch.
    (-0.048, -0.1005, -0.163), (-0.048, 0.1005, -0.163),
    (0.048, -0.1005, -0.163), (0.048, 0.1005, -0.163),
    # Four end rollers visible at the front and rear of the chassis.
    (-0.259, -0.131, -0.135), (-0.259, 0.131, -0.135),
    (0.259, -0.131, -0.135), (0.259, 0.131, -0.135),
]
for index, (x, y, z) in enumerate(roller_centres):
    ET.SubElement(
        chassis,
        "geom",
        {
            "name": f"guide_roller_collision_{index}",
            "type": "cylinder",
            "class": "collision",
            "pos": f"{x} {y} {z}",
            "size": ".015 .0045",
            "quat": ".7071067811865476 .7071067811865476 0 0",
            "friction": ".15 .001 .0001",
            "condim": "4",
            "rgba": ".1 .8 .2 .35",
        },
    )

audit_xml = OUT / "scene_hard_stop_audit.xml"
ET.indent(tree, space="  ")
tree.write(audit_xml, encoding="utf8", xml_declaration=True)

model = mujoco.MjModel.from_xml_path(str(audit_xml))
data = mujoco.MjData(model)


def set_pose():
    data.qpos[:] = model.qpos0
    data.qvel[:] = 0
    # Start 1 mm above the lowest rigid support and let gravity settle it.
    data.qpos[:3] = (0, 0, 0.179)
    data.qpos[3:7] = (1, 0, 0, 0)
    all_values = {}
    for side in ("left", "right"):
        vals, _ = leg_configuration(hip_target, stop_difference + 2e-4, side)
        all_values[side] = vals
        for name, value in vals.items():
            data.qpos[model.joint(f"{side}_{name}").qposadr[0]] = value
    mujoco.mj_forward(model, data)
    return all_values


initial_values = set_pose()
actuator_names = (
    "left_hip_motor", "left_crank_motor", "right_hip_motor", "right_crank_motor"
)
joint_names = ("left_hip", "left_crank", "right_hip", "right_crank")
act_ids = np.array([model.actuator(name).id for name in actuator_names])
qadr = np.array([model.joint(name).qposadr[0] for name in joint_names])
vadr = np.array([model.joint(name).dofadr[0] for name in joint_names])

# Command 0.05 rad through the stop so the passive limits, not a perfect target,
# hold the folded endpoint. This is a deliberate low-speed contact test.
# A conventional joint-position PD needs a small command offset to supply the
# static gravity torque. The physical hip target remains the fitted 0.45029 rad.
hip_command = hip_target + 0.027
targets = np.array([
    hip_command,
    hip_command + stop_difference - 0.05,
    hip_command,
    hip_command + stop_difference - 0.05,
])
wheel_act_ids = np.array([
    model.actuator("left_wheel_spin_motor").id,
    model.actuator("right_wheel_spin_motor").id,
])
base_vadr = model.joint("floating_base").dofadr[0]


def closure_errors():
    result = {}
    for name in (
        "left_proximal", "left_distal", "left_gas",
        "right_proximal", "right_distal", "right_gas",
    ):
        if name.endswith(("proximal", "distal")):
            first, second = data.site(name + "_a").xpos, data.site(name + "_b").xpos
        else:
            first, second = data.site(name + "_end").xpos, data.site(name + "_mount").xpos
        result[name] = float(np.linalg.norm(first - second))
    return result


def roll_pitch_from_quat(q):
    w, x, y, z = q
    roll = math.atan2(2 * (w*x + y*z), 1 - 2 * (x*x + y*y))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (w*y - z*x))))
    return roll, pitch


max_closure = 0.0
max_qacc = 0.0
max_torque = 0.0
min_root_z = float("inf")
contact_counts = {"drive_wheel": 0, "central_guide": 0, "end_guide": 0, "other": 0}
warning_text = []
steps = int(3.0 / model.opt.timestep)
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    for _ in range(steps):
        error = (targets - data.qpos[qadr] + math.pi) % (2 * math.pi) - math.pi
        torque = np.clip(320.0 * error - 10.0 * data.qvel[vadr], -40.0, 40.0)
        _, base_pitch = roll_pitch_from_quat(data.qpos[3:7])
        pitch_rate = float(data.qvel[base_vadr + 4])
        # Equal wheel torques use the wheel/body reaction to keep the chassis
        # level while it rests on the central guide rollers.
        wheel_torque = float(np.clip(38.0 * base_pitch + 3.2 * pitch_rate, -5.7759, 5.7759))
        data.ctrl[:] = 0
        data.ctrl[act_ids] = torque
        data.ctrl[wheel_act_ids] = wheel_torque
        mujoco.mj_step(model, data)
        max_torque = max(max_torque, float(np.max(np.abs(torque))))
        max_qacc = max(max_qacc, float(np.max(np.abs(data.qacc))))
        min_root_z = min(min_root_z, float(data.qpos[2]))
        if int(data.time / model.opt.timestep) % 20 == 0:
            max_closure = max(max_closure, max(closure_errors().values()))
        for contact in data.contact[: data.ncon]:
            names = {model.geom(contact.geom1).name, model.geom(contact.geom2).name}
            joined = " ".join(names)
            if "tire" in joined:
                contact_counts["drive_wheel"] += 1
            elif "guide_roller_collision_" in joined:
                ids = [int(name.rsplit("_", 1)[1]) for name in names if name.startswith("guide_roller_collision_")]
                if ids and ids[0] < 4:
                    contact_counts["central_guide"] += 1
                else:
                    contact_counts["end_guide"] += 1
            else:
                contact_counts["other"] += 1
    warning_text = [str(item.message) for item in caught]

roll, pitch = roll_pitch_from_quat(data.qpos[3:7])
final_closure = closure_errors()
final_difference = {
    side: float(data.qpos[model.joint(f"{side}_crank").qposadr[0]] - data.qpos[model.joint(f"{side}_hip").qposadr[0]])
    for side in ("left", "right")
}


def final_visual_envelope():
    full_low = float("inf")
    full_top = -float("inf")
    leg_top = -float("inf")
    chassis_id = model.body("chassis").id
    for geom_id in range(model.ngeom):
        if model.geom_type[geom_id] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        mesh_id = int(model.geom_dataid[geom_id])
        first = int(model.mesh_vertadr[mesh_id])
        last = first + int(model.mesh_vertnum[mesh_id])
        vertices = model.mesh_vert[first:last].astype(float)
        world = vertices @ data.geom_xmat[geom_id].reshape(3, 3).T + data.geom_xpos[geom_id]
        full_low = min(full_low, float(world[:, 2].min()))
        full_top = max(full_top, float(world[:, 2].max()))
        if int(model.geom_bodyid[geom_id]) != chassis_id:
            leg_top = max(leg_top, float(world[:, 2].max()))
    return full_low, full_top, leg_top


final_low, final_full_top, final_leg_top = final_visual_envelope()
drive_wheel_gap = float(data.xpos[model.body("left_wheel").id, 2] - 0.0625)
central_guide_gaps = [
    float(data.geom(f"guide_roller_collision_{index}").xpos[2] - 0.015)
    for index in range(4)
]
report = {
    "status": "PASS" if not warning_text and max_closure < 5e-4 and max_qacc < 1e6 else "FAIL",
    "audit_model": str(audit_xml),
    "duration_s": float(data.time),
    "timestep_s": float(model.opt.timestep),
    "target": {
        "hip_rad": hip_target,
        "commanded_hip_rad": hip_command,
        "hard_stop_difference_rad": stop_difference,
        "commanded_difference_rad": stop_difference - 0.05,
        "wheel_pitch_controller": "tau_each = clip(38*pitch + 3.2*pitch_rate, +/-5.7759 Nm)",
    },
    "final": {
        "root_xyz_m": data.qpos[:3].tolist(),
        "base_roll_rad": roll,
        "base_pitch_rad": pitch,
        "difference_rad": final_difference,
        "hip_rad": {
            side: float(data.qpos[model.joint(f"{side}_hip").qposadr[0]])
            for side in ("left", "right")
        },
        "drive_wheel_ground_gap_m": drive_wheel_gap,
        "central_guide_ground_gaps_m": central_guide_gaps,
        "leg_visual_height_m": final_leg_top,
        "leg_height_above_drive_wheel_tangent_m": final_leg_top - drive_wheel_gap,
        "leg_height_error_vs_solidworks_drive_wheel_datum_m": final_leg_top - drive_wheel_gap - 0.22336,
        "full_visual_height_m": final_full_top,
        "full_height_above_drive_wheel_tangent_m": final_full_top - drive_wheel_gap,
        "full_visual_tunnel_margin_m": 0.2472 - final_full_top,
        "lowest_visual_m": final_low,
        "max_closure_error_m": max_closure,
        "closure_errors_m": final_closure,
        "max_abs_qacc_rad_s2_or_m_s2": max_qacc,
        "max_abs_leg_torque_nm": max_torque,
        "minimum_root_height_m": min_root_z,
        "contact_sample_counts": contact_counts,
        "warnings": warning_text,
    },
    "scope": "Local MuJoCo contact/constraint test. The source STEP/SolidWorks assembly and delivered package were not edited.",
}
(OUT / "dynamic_hard_stop_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")

# Final side render.
renderer = mujoco.Renderer(model, height=720, width=1100)
camera = mujoco.MjvCamera()
camera.type = mujoco.mjtCamera.mjCAMERA_FREE
camera.lookat[:] = data.xpos[model.body("chassis").id]
camera.distance = 1.05
camera.azimuth = 90
camera.elevation = 0
renderer.update_scene(data, camera=camera)
Image.fromarray(renderer.render()).save(OUT / "dynamic_hard_stop_after_2s.png")
renderer.close()

# Review image: SolidWorks target and kinematic/dynamic MuJoCo result.
sw = Image.open(r"C:\Users\lulu\AppData\Local\Temp\codex-clipboard-d7cecd84-1371-415b-9a05-8a5a28fc6cec.png").convert("RGB")
mj = Image.open(OUT / "dynamic_hard_stop_after_2s.png").convert("RGB")
target_width = 1100
sw = sw.resize((target_width, round(sw.height * target_width / sw.width)))
canvas = Image.new("RGB", (target_width, sw.height + mj.height + 80), "white")
canvas.paste(sw, (0, 40))
canvas.paste(mj, (0, sw.height + 80))
draw = ImageDraw.Draw(canvas)
draw.rectangle((0, 0, target_width, 40), fill="black")
draw.text((12, 12), "SolidWorks target", fill=(255, 255, 255))
draw.rectangle((0, sw.height + 40, target_width, sw.height + 80), fill="black")
draw.text((12, sw.height + 52), "MuJoCo after 2.0 s: exact B-Rep stop + guide roller contacts", fill=(255, 255, 255))
canvas.save(OUT / "solidworks_vs_mujoco_hard_stop.png")

print(json.dumps(report, ensure_ascii=False, indent=2))

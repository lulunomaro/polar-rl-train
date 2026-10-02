"""Show the MOD4 hip at neutral, learned pose, and +0.5 rad hard limit in MuJoCo.

Keys in the live viewer: 1 = hip 0, 2 = learned hip 0.48, 3 = +0.50 limit,
4 = slow sweep. The crank-hip difference remains -0.92 rad in every view,
so the highlighted thigh motion isolates the hip rotation.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import glfw
import mujoco
import mujoco.viewer
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "chassis_mod4"))
from kinematics import set_configuration  # noqa: E402

MODEL = ROOT / "scene_hard_stop_audit.xml"
OUT = Path(__file__).with_name("hip_limit_mujoco_comparison.png")
DIFFERENCE = -0.92
TYRE_RADIUS = 0.0645


def make_pose(model: mujoco.MjModel, data: mujoco.MjData, hip: float) -> dict:
    mujoco.mj_resetData(model, data)
    set_configuration(model, data, left=(hip, DIFFERENCE),
                      right=(hip, DIFFERENCE), check_limits=False)
    wheel_z = min(data.site_xpos[model.site(f"{side}_wheel_center").id, 2]
                  for side in ("left", "right"))
    data.qpos[2] += TYRE_RADIUS - wheel_z
    mujoco.mj_forward(model, data)
    violations = []
    for j in range(model.njnt):
        if model.jnt_limited[j]:
            value = data.qpos[model.jnt_qposadr[j]]
            low, high = model.jnt_range[j]
            if value < low - 1e-6 or value > high + 1e-6:
                violations.append(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j))
    if violations:
        raise RuntimeError(f"pose violates joint ranges: {violations}")
    return {
        "hip": float(data.qpos[model.joint("left_hip").qposadr[0]]),
        "crank": float(data.qpos[model.joint("left_crank").qposadr[0]]),
        "closure_max_m": float(np.max(np.abs(data.efc_pos))) if data.nefc else 0.0,
    }


def camera() -> mujoco.MjvCamera:
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = (0.0, 0.0, 0.22)
    cam.distance = 1.12
    cam.azimuth = 90
    cam.elevation = -8
    return cam


def to_pixel(point: np.ndarray, cam: mujoco.MjvGLCamera,
             width: int, height: int) -> tuple[int, int]:
    relative = point - np.asarray(cam.pos)
    forward = np.asarray(cam.forward)
    up = np.asarray(cam.up)
    right = np.cross(forward, up)
    depth = float(relative @ forward)
    half_vertical = cam.frustum_top * depth / cam.frustum_near
    half_horizontal = half_vertical * width / height
    x = width / 2 + float(relative @ right) / half_horizontal * width / 2
    y = height / 2 - float(relative @ up) / half_vertical * height / 2
    return round(x), round(y)


def draw_comparison(model: mujoco.MjModel) -> None:
    width, height = 900, 620
    renderer = mujoco.Renderer(model, height, width)
    data = mujoco.MjData(model)
    panels = []
    labels = [(0.0, "髋关节 0°"), (0.48, "策略姿态 +27.5°"),
              (0.50, "模型上限 +28.65°")]
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 25)
        small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 19)
    except OSError:
        font = small = ImageFont.load_default()
    for hip, label in labels:
        state = make_pose(model, data, hip)
        renderer.update_scene(data, camera=camera())
        panel = ImageEnhance.Brightness(Image.fromarray(renderer.render())).enhance(1.55)
        draw = ImageDraw.Draw(panel)
        hip_point = data.xanchor[model.joint("left_hip").id]
        knee_point = data.xanchor[model.joint("left_knee").id]
        hp = to_pixel(hip_point, renderer.scene.camera[0], width, height)
        kp = to_pixel(knee_point, renderer.scene.camera[0], width, height)
        draw.line((hp, kp), fill=(255, 205, 35), width=6)
        draw.ellipse((hp[0]-9, hp[1]-9, hp[0]+9, hp[1]+9),
                     fill=(255, 60, 60), outline="white", width=2)
        draw.rectangle((12, 12, width - 12, 92), fill=(14, 20, 29))
        draw.text((26, 22), label, font=font, fill="white")
        draw.text((26, 58), f"hip {state['hip']:+.3f} rad   crank {state['crank']:+.3f} rad",
                  font=small, fill=(210, 224, 236))
        draw.text((hp[0]+15, hp[1]-32), "髋轴", font=small, fill=(255, 95, 75),
                  stroke_width=1, stroke_fill="black")
        panels.append(panel)
        print(f"{label}: {state}", flush=True)
    output = Image.new("RGB", (width * len(panels), height), (0, 0, 0))
    for i, panel in enumerate(panels):
        output.paste(panel, (i * width, 0))
    output.save(OUT)
    print(f"saved {OUT}", flush=True)


def run_viewer(model: mujoco.MjModel) -> None:
    data = mujoco.MjData(model)
    mode = {"value": 3}

    def on_key(key: int) -> None:
        if key in (glfw.KEY_1, glfw.KEY_2, glfw.KEY_3, glfw.KEY_4):
            mode["value"] = key - glfw.KEY_0

    with mujoco.viewer.launch_passive(model, data, key_callback=on_key) as viewer:
        viewer.cam.lookat[:] = (0, 0, 0.22)
        viewer.cam.distance = 1.12
        viewer.cam.azimuth = 90
        viewer.cam.elevation = -8
        viewer.opt.geomgroup[3] = 0
        viewer.opt.sitegroup[:] = 0
        start = time.monotonic()
        while viewer.is_running():
            mode_value = mode["value"]
            hip = {1: 0.0, 2: 0.48, 3: 0.50}.get(
                mode_value, 0.25 * (1 - np.cos((time.monotonic()-start) * 0.8)))
            make_pose(model, data, hip)
            viewer.sync()
            time.sleep(1 / 60)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-only", action="store_true")
    args = parser.parse_args()
    model = mujoco.MjModel.from_xml_path(str(MODEL))
    draw_comparison(model)
    if not args.render_only:
        print("MuJoCo live keys: 1=hip 0, 2=learned +0.48, 3=limit +0.50, 4=sweep", flush=True)
        run_viewer(model)


if __name__ == "__main__":
    main()

"""Render saved real physics states; this script never runs a policy or steps physics."""
from pathlib import Path
import argparse
import json
import math
import time

import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSET = Path(r"F:\RMPOLAR-RL\mod4v3_scut_semantics_20261106\review_r3\corrected")
FONT = "C:/Windows/Fonts/msyh.ttc"


def setup():
    m = mujoco.MjModel.from_xml_path(str(ASSET / "mjcf/scene.xml"))
    d = mujoco.MjData(m)
    m.vis.headlight.ambient[:] = (0.35, 0.35, 0.35)
    m.vis.headlight.diffuse[:] = (0.45, 0.45, 0.45)
    m.vis.headlight.specular[:] = (0.05, 0.05, 0.05)
    m.light_diffuse[:] = 0.35
    m.vis.map.fogstart = 10.0
    m.vis.map.fogend = 20.0
    m.geom_rgba[m.geom("ground").id] = (0.88, 0.90, 0.93, 1.0)
    roots = {m.body(s + "_" + n + "_link").id for s in ("left", "right") for n in ("front1", "rear1")}
    for g in range(m.ngeom):
        if m.geom_contype[g] or m.geom_conaffinity[g]:
            continue
        b = int(m.geom_bodyid[g])
        name = m.body(b).name or ""
        p = b
        while p > 0 and p not in roots:
            p = int(m.body_parentid[p])
        m.geom_matid[g] = -1
        if "wheel" in name:
            color = (0.16, 0.18, 0.21, 1.0)
        elif p in roots:
            color = (0.15, 0.48, 0.78, 1.0) if name.startswith("left_") else (0.89, 0.47, 0.17, 1.0)
        else:
            color = (0.55, 0.59, 0.64, 1.0)
        m.geom_rgba[g] = color
    opt = mujoco.MjvOption()
    opt.geomgroup[:] = 0
    opt.geomgroup[0] = 1
    opt.geomgroup[2] = 1
    return m, d, opt


def camera(x=0.45, distance=2.05):
    cam = mujoco.MjvCamera()
    cam.lookat[:] = (x, 0, 0.20)
    cam.distance = distance
    cam.azimuth = 90
    cam.elevation = -7
    return cam


def marker(scene):
    for x in np.arange(-0.25, 1.76, 0.25):
        g = scene.geoms[scene.ngeom]
        mujoco.mjv_initGeom(g, mujoco.mjtGeom.mjGEOM_BOX, np.array([0.002, 0.40, 0.0007]),
                           np.array([x, 0, 0.001]), np.eye(3).reshape(-1),
                           np.array([0.9, 0.22, 0.08, 1.0]) if x == 0 else np.array([0.48, 0.53, 0.58, 1.0]))
        scene.ngeom += 1


def annotated(pixels, title, t, qpos, tilt, *, fixed=True):
    h, w = pixels.shape[:2]
    image = Image.new("RGB", (w, h + 98), "#f7f9fc")
    image.paste(Image.fromarray(pixels), (0, 55))
    draw = ImageDraw.Draw(image)
    draw.text((18, 12), title, font=ImageFont.truetype(FONT, 21), fill="#10243c")
    label = f"t={t:5.2f}s | 机身高 {qpos[2]*100:.1f}cm | 倾角 {tilt:.1f}° | X位移 {qpos[0]:+.3f}m"
    draw.text((18, h + 65), label, font=ImageFont.truetype(FONT, 17), fill="#21364d")
    draw.text((18, 65), "真实物理轨迹回放 · R1/22959 · 零速度指令", font=ImageFont.truetype(FONT, 15), fill="#e8edf3")
    if fixed:
        draw.text((18, 88), "固定镜头；红线为起始X=0；灰线间距0.25m；车头向右", font=ImageFont.truetype(FONT, 14), fill="#e8edf3")
    return image


def render():
    m, d, opt = setup()
    series = np.load(ROOT / "02_gas200_policy.npz")
    times, qpos = series["time"], series["qpos"]
    sample_times = [0.0, 0.3, 0.74, 1.5, 3.0, 12.0]
    stills = []
    base = m.body("base_link").id
    frames = []
    # First four seconds in real time, followed by the measured 12-second endpoint.
    frame_indices = list(range(0, min(len(times), 201), 2)) + [len(times) - 1]
    with mujoco.Renderer(m, height=520, width=880) as renderer:
        def frame(i, *, fixed):
            d.qpos[:] = qpos[i]
            d.qvel[:] = series["qvel"][i]
            mujoco.mj_forward(m, d)
            cam = camera() if fixed else camera(float(qpos[i, 0]) - 0.025, 1.12)
            renderer.update_scene(d, camera=cam, scene_option=opt)
            marker(renderer.scene)
            tilt = math.degrees(math.acos(float(np.clip(d.xmat[base].reshape(3, 3)[2, 2], -1, 1))))
            title = "MOD4v3：200mm后收初态 → 同一策略自主起立" if fixed else "MOD4v3 R1/22959 · 实测起立姿态"
            return annotated(renderer.render(), title, float(times[i]), qpos[i], tilt, fixed=fixed)
        for i in frame_indices:
            frames.append(frame(i, fixed=True).resize((792, 556)))
        durations = [40] * len(frames)
        durations[0], durations[-2], durations[-1] = 700, 500, 1800
        frames[0].save(ROOT / "ACTUAL_STAND.gif", save_all=True, append_images=frames[1:],
                       duration=durations, loop=0, optimize=True)
        for t in sample_times:
            i = int(np.argmin(abs(times - t)))
            still = frame(i, fixed=False)
            still.save(ROOT / f"POSE_{times[i]:05.2f}s.png")
            stills.append(still.resize((660, 464)))
    sheet = Image.new("RGB", (660 * 3, 464 * 2), "white")
    for i, im in enumerate(stills):
        sheet.paste(im, ((i % 3) * 660, (i // 3) * 464))
    sheet.save(ROOT / "ACTUAL_SEQUENCE.png")
    record = dict(source="02_gas200_policy.npz", policy_calls=0, new_physics_steps=0,
                  animation="ACTUAL_STAND.gif", animation_time_s=[0, 4, 12],
                  final_frame_jumps_from_4s_to_12s=True, fixed_camera=True,
                  coordinate_ticks_m=0.25, red_line_world_x_m=0, still_times_s=sample_times)
    (ROOT / "RENDER.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record))


def viewer():
    import mujoco.viewer
    m, d, opt = setup()
    data = np.load(ROOT / "02_gas200_policy.npz")
    state = dict(paused=False, start=time.monotonic(), offset=0.0)
    def key(code):
        if code == ord("R"):
            state.update(start=time.monotonic(), offset=0.0)
        elif code in (ord("G"), 32):
            elapsed = state["offset"] if state["paused"] else time.monotonic() - state["start"] + state["offset"]
            state.update(paused=not state["paused"], start=time.monotonic(), offset=elapsed)
    with mujoco.viewer.launch_passive(m, d, key_callback=key) as handle:
        handle.opt.geomgroup[:] = opt.geomgroup
        handle.cam.lookat[:] = (0.45, 0, 0.20)
        handle.cam.distance = 2.05
        handle.cam.azimuth = 90
        handle.cam.elevation = -7
        while handle.is_running():
            t = state["offset"] if state["paused"] else time.monotonic() - state["start"] + state["offset"]
            t = t % (float(data["time"][-1]) + 2)
            i = min(int(np.searchsorted(data["time"], t)), len(data["time"]) - 1)
            d.qpos[:] = data["qpos"][i]
            d.qvel[:] = data["qvel"][i]
            mujoco.mj_forward(m, d)
            with handle.lock():
                handle.user_scn.ngeom = 0
                marker(handle.user_scn)
            handle.sync()
            time.sleep(0.01)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--viewer", action="store_true")
    args = parser.parse_args()
    viewer() if args.viewer else render()

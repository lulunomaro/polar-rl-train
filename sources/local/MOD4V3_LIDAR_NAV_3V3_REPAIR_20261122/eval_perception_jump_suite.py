"""100% Remote (host72) 400 Hz MuJoCo Evaluation & 1x EGL Video Renderer for Perception-Guided E_jump.

Evaluates:
1. Official `RMUL 2027 3v3` Orange-Tip Bridge Hurdle (`rmul_box_3`: 270 mm tall x 352 mm wide at x in [-2.676, -2.324], y=3.46)
   across Eastbound & Westbound approaches, manual Space press distances d_press in {0.60, 0.90, 1.25, 1.65} m,
   speeds {1.50, 1.90, 2.40} m/s, stances {0.28, 0.36} m (24 episodes).
2. Solid `380 mm` (0.380 m) 3D High Platform (24 episodes across d_press in {0.65, 1.00, 1.40, 1.80} m,
   speeds {1.50, 1.90, 2.40} m/s, stances {0.28, 0.38} m) + Official `RMUL 2027 3v3` Sheer 200 mm Highland Jump (6 episodes).
3. Optional 1x (25 fps from 400 Hz) EGL verification videos (`rmul2027_bridge_hurdle_jump_1X.mp4` & `solid_380mm_platform_jump_1X.mp4`).
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path

import imageio.v2 as imageio
import mujoco as mj
import numpy as np
from PIL import Image, ImageDraw
import torch

from nav_common import HERE, put, sha256
from nav4d_runtime import DT, PPO_TO_NATIVE, SUBSTEPS, Nav4DPolicy, Nav4DSimulation
from terrain_sensor_4d import EMPTY_NP, S_GRID_NP, extract_jump_feature_torch
from jump360_scene import JumpPlant
from jump_warp_gpu import PLAT_BOX_H, PLAT_LEN, prepare_jump_warp_scene


def run_rmul_bridge_case(case: dict, checkpoint: str | None = None, video_path: Path | None = None) -> dict:
    policy = Nav4DPolicy(jump_checkpoint=checkpoint)
    sim = Nav4DSimulation(policy)
    sim.load_scene("suite_rmul2027", height=case["height"])

    eastbound = bool(case["eastbound"])
    beam_front = -2.676 if eastbound else -2.324
    beam_back = -2.324 if eastbound else -2.676
    yaw = 0.0 if eastbound else math.pi
    # Spawn 2.25 m before beam front along North corridor centerline y=3.46 (corridor spans x in [-5.8, +5.8]!)
    start_x = (beam_front - 2.25) if eastbound else (beam_front + 2.25)
    start_y = 3.46

    length = float(np.clip(case["height"] - 0.0625, 0.14, 0.35))
    fit = sim.ik.fit(np.sqrt(length * length + sim.ik.lateral_offset**2), 0.0)["qpos"]
    sim.d.qpos[:] = fit
    sim.d.qpos[:3] = [start_x, start_y, 0.0 + case["height"] + 0.002]
    sim.d.qpos[3:7] = [math.cos(yaw / 2.0), 0.0, 0.0, math.sin(yaw / 2.0)]
    sim.d.qvel[:] = 0.0
    mj.mj_forward(sim.m, sim.d)
    policy.reset_history()

    writer = None
    renderer = None
    sub_cnt = 0
    if video_path is not None:
        video_path.parent.mkdir(parents=True, exist_ok=True)
        writer = imageio.get_writer(video_path, fps=25, codec="libx264", quality=8, macro_block_size=16)

    peak_rim = 0.0
    peak_all = 0.0
    beam_zone_min_all = 99.0
    peak_pitch = 0.0
    peak_roll = 0.0
    air_pitch = 0.0
    flipped = False
    pressed = False
    press_x = None

    def obs_cb(s):
        nonlocal peak_rim, peak_all, beam_zone_min_all, peak_pitch, peak_roll, air_pitch, flipped, sub_cnt, renderer
        m = s.measure()
        p_deg = abs(math.degrees(m["pitch"]))
        r_deg = abs(math.degrees(m["roll"]))
        peak_pitch = max(peak_pitch, p_deg)
        peak_roll = max(peak_roll, r_deg)
        flipped |= (p_deg > 62.0) or (r_deg > 55.0)
        rx = float(s.d.qpos[0])
        if m["airborne"]:
            peak_rim = max(peak_rim, m["tire_low"])
            peak_all = max(peak_all, m["lowest"])
            air_pitch = max(air_pitch, p_deg)
        if -2.66 <= rx <= -2.34:
            beam_zone_min_all = min(beam_zone_min_all, m["lowest"])
        if writer is not None:
            sub_cnt += 1
            if sub_cnt % 16 == 0:
                if renderer is None:
                    renderer = mj.Renderer(s.m, height=720, width=1280)
                opt = mj.MjvOption()
                opt.geomgroup[3] = 0
                opt.geomgroup[4] = 1
                cam = mj.MjvCamera()
                cam.type = mj.mjtCamera.mjCAMERA_FREE
                cam.lookat[:] = [float(s.d.qpos[0]), float(s.d.qpos[1]), 0.28]
                cam.distance = 2.9
                cam.azimuth = 115.0 if eastbound else 65.0
                cam.elevation = -21.0
                renderer.update_scene(s.d, camera=cam, scene_option=opt)
                img = Image.fromarray(renderer.render().copy())
                draw = ImageDraw.Draw(img)
                draw.rectangle((0, 0, 1280, 72), fill=(14, 23, 32))
                draw.text(
                    (18, 10),
                    f"RMUL2027 3v3 Orange-Tip Bridge Hurdle (270x352mm) | Manual Space @ d={case['d_press']:.2f}m | 1x",
                    fill=(247, 178, 103),
                )
                draw.text(
                    (18, 36),
                    f"t={s.d.time:.2f}s  vx={m['vx']:+.2f}m/s  clear={100.*m['lowest']:.1f}cm  pitch={math.degrees(m['pitch']):+.1f}deg  g_jump={np.round(s.last_g_jump, 2)}",
                    fill=(230, 238, 244),
                )
                writer.append_data(np.asarray(img))

    sim.physics_observer = obs_cb
    hold_left = 0
    for tick in range(210):
        rx = float(sim.d.qpos[0])
        dist_front = (beam_front - rx) if eastbound else (rx - beam_front)
        if not pressed and tick >= 25 and dist_front <= case["d_press"]:
            pressed = True
            press_x = rx
            hold_left = 6
        keys = {"w"}
        if hold_left > 0:
            keys.add("space")
            hold_left -= 1
        cmd_v = 0.0 if tick < 12 else case["speed"]
        sim.step(keys, command=(cmd_v, 0.0))
        if flipped:
            break
        past_back = (rx - beam_back) if eastbound else (beam_back - rx)
        if pressed and past_back > 0.85 and not policy.jump_active:
            # Let 15 extracruise ticks run to prove post-landing stability
            for _ in range(15):
                sim.step({"w"}, command=(case["speed"], 0.0))
            break

    if writer is not None:
        writer.close()
    if renderer is not None:
        renderer.close()

    end_x = float(sim.d.qpos[0])
    m_end = sim.measure()
    past_back = (end_x - beam_back) if eastbound else (beam_back - end_x)
    cleared_span = past_back >= 0.40
    # Valid crossing: cleared full bridge span, stayed airborne above 24.5cm over the 27cm beam (either full air-clear or clean tire tap-vault), 0 flips!
    clean_over = beam_zone_min_all >= 0.255 and beam_zone_min_all < 90.0
    passed = bool(
        pressed
        and not flipped
        and cleared_span
        and clean_over
        and m_end["body_height"] > 0.17
        and abs(math.degrees(m_end["pitch"])) < 15.0
    )
    return dict(
        case,
        pressed=pressed,
        press_x=press_x,
        end_x=end_x,
        past_back_m=round(past_back, 4),
        peak_rim_cm=round(100.0 * peak_rim, 2),
        peak_all_cm=round(100.0 * peak_all, 2),
        beam_zone_min_all_cm=round(100.0 * (beam_zone_min_all if beam_zone_min_all < 90.0 else 0.0), 2),
        air_pitch_deg=round(air_pitch, 2),
        peak_pitch_deg=round(peak_pitch, 2),
        peak_roll_deg=round(peak_roll, 2),
        flip=flipped,
        clean_over=clean_over,
        passed=passed,
    )


def run_rmul_sheer200_case(case: dict, checkpoint: str | None = None) -> dict:
    """Jump directly up the sheer 200mm Central Highland wall at y=1.25 (non-stair sheer wall!)."""
    policy = Nav4DPolicy(jump_checkpoint=checkpoint)
    sim = Nav4DSimulation(policy)
    sim.load_scene("suite_rmul2027", height=case["height"])

    wall_x = -3.49
    start_x = wall_x - 2.35
    start_y = 1.25
    length = float(np.clip(case["height"] - 0.0625, 0.14, 0.35))
    fit = sim.ik.fit(np.sqrt(length * length + sim.ik.lateral_offset**2), 0.0)["qpos"]
    sim.d.qpos[:] = fit
    sim.d.qpos[:3] = [start_x, start_y, case["height"] + 0.002]
    sim.d.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
    sim.d.qvel[:] = 0.0
    mj.mj_forward(sim.m, sim.d)
    policy.reset_history()

    flipped = False
    peak_all = 0.0
    pressed = False
    hold_left = 0

    def obs_cb(s):
        nonlocal flipped, peak_all
        m = s.measure()
        flipped |= abs(math.degrees(m["pitch"])) > 62.0 or abs(math.degrees(m["roll"])) > 55.0
        if m["airborne"]:
            peak_all = max(peak_all, m["lowest"])

    sim.physics_observer = obs_cb
    for tick in range(210):
        rx = float(sim.d.qpos[0])
        if not pressed and tick >= 25 and (wall_x - rx) <= case["d_press"]:
            pressed = True
            hold_left = 6
        keys = {"w"}
        if hold_left > 0:
            keys.add("space")
            hold_left -= 1
        sim.step(keys, command=(0.0 if tick < 12 else case["speed"], 0.0))
        if flipped:
            break
        if pressed and rx > wall_x + 0.55 and not policy.jump_active:
            for _ in range(15):
                sim.step({"w"}, command=(0.6, 0.0))
            break

    end_x = float(sim.d.qpos[0])
    m_end = sim.measure()
    on_highland = end_x > wall_x + 0.25 and m_end["ground"] >= 0.18 and m_end["body_height"] > 0.17
    return dict(
        case,
        end_x=round(end_x, 4),
        end_ground_m=round(float(m_end["ground"]), 3),
        peak_all_cm=round(100.0 * peak_all, 2),
        flip=flipped,
        passed=bool(pressed and not flipped and on_highland),
    )


def run_solid_380_platform_case(case: dict, checkpoint: str | None = None, video_path: Path | None = None) -> dict:
    """400 Hz MuJoCo evaluation jumping onto a solid 380 mm (0.380 m) 3D platform via Nav4DPolicy."""
    policy = Nav4DPolicy(jump_checkpoint=checkpoint)
    cache_dir = HERE / "cache/jump_eval_380"
    prepare_jump_warp_scene(cache_dir)
    # Build visual-enabled XML if rendering video, else lean physics XML
    if video_path is not None:
        from jump360_scene import make_scene
        import xml.etree.ElementTree as ET

        vis_xml = cache_dir / "jump360_solid_visual.xml"
        if not vis_xml.is_file():
            tmp = cache_dir / "vis_tmp.xml"
            tree = ET.parse(make_scene(tmp, True))
            world = tree.getroot().find("worldbody")
            ground = world.find("geom[@name='ground']")
            ground.set("size", "26 26 .1")
            geom = world.find("body/geom[@name='dyn_hurdle_0']")
            geom.set("size", f"{PLAT_LEN / 2.0:.4f} 8.0 {PLAT_BOX_H / 2.0:.4f}")
            geom.set("rgba", ".30 .56 .73 1")
            tree.write(vis_xml, encoding="utf-8", xml_declaration=True)
            tmp.unlink(missing_ok=True)

    plant = JumpPlant(seed=2026, visual=(video_path is not None), scene_dir=cache_dir)
    plant.setup(case["height"], dr=0.0, init_pose=(0.0, 0.0, 0.0))
    plat_h = float(case.get("plat_height", 0.380))
    edge = float(case["speed"]) * 1.45 + float(case["d_press"])
    # Position dyn_hurdle_0 so front face is at x = edge and top surface is at z = plat_h!
    gid0 = plant.hurdle_gids[0]
    mocap_id0 = plant.m.body_mocapid[plant.m.geom_bodyid[gid0]]
    plant.d.mocap_pos[mocap_id0] = [edge + PLAT_LEN * 0.5, 0.0, plat_h - PLAT_BOX_H * 0.5]
    mj.mj_forward(plant.m, plant.d)
    policy.reset_history()

    s_torch = torch.from_numpy(S_GRID_NP)
    z_ref = torch.zeros(1, dtype=torch.float32)

    writer = None
    renderer = None
    sub_cnt = 0
    if video_path is not None:
        video_path.parent.mkdir(parents=True, exist_ok=True)
        writer = imageio.get_writer(video_path, fps=25, codec="libx264", quality=8, macro_block_size=16)

    peak_all = 0.0
    face_force_max = 0.0
    air_pitch = 0.0
    flipped = False
    pressed = False
    hold_left = 0
    cmd_vx = 0.0

    for tick in range(220):
        rx = float(plant.d.qpos[0])
        r = plant.d.xmat[plant.base_id].reshape(3, 3)
        yaw = math.atan2(float(r[1, 0]), float(r[0, 0]))
        ray_x = rx + math.cos(yaw) * S_GRID_NP
        in_plat = (ray_x >= edge) & (ray_x <= edge + PLAT_LEN)
        zg = np.where(in_plat, plat_h, 0.0).astype(np.float32)
        gj = extract_jump_feature_torch(s_torch, torch.from_numpy(zg)[None, :], torch.from_numpy(zg)[None, :], z_ref=z_ref)[0].numpy()

        if not pressed and tick >= 35 and (edge - rx) <= case["d_press"]:
            pressed = True
            hold_left = 6
            policy.request_jump()

        key_held = hold_left > 0
        if hold_left > 0:
            hold_left -= 1
        goal_vx = 0.0 if tick < 15 else float(case["speed"])
        cmd_vx = cmd_vx + (goal_vx - cmd_vx) / 10.0

        obs = plant.command(cmd_vx, case["height"], key_held, 0.0)
        fr0 = plant.frame()
        pitch_rad = math.asin(float(np.clip(-r[2, 0], -1.0, 1.0)))
        roll_rad = math.atan2(float(r[2, 1]), float(r[2, 2]))
        ground_here = plat_h if rx > edge + 0.02 else 0.0
        airborne_now = (fr0.total_force < 1.0) and ((fr0.lowest - ground_here) > 0.006)
        sup_here = fr0.wheel_top_force if rx > edge + 0.02 else fr0.wheel_up_force
        stable_now = (
            min(sup_here) > 5.0
            and abs(pitch_rad) < math.radians(10.0)
            and abs(roll_rad) < math.radians(8.0)
            and abs(float(plant.d.qvel[2])) < 0.35
        )
        phys = dict(airborne=airborne_now, stable=stable_now, body_height=float(plant.d.qpos[2]) - ground_here)
        act_ppo, route = policy.act(obs, EMPTY_NP, float("inf"), phys, key_held=key_held, g_jump=gj)
        native = torch.as_tensor(act_ppo[PPO_TO_NATIVE], dtype=torch.float32).reshape(1, 6)

        for sub in range(SUBSTEPS):
            if route["e2"] > 0.5:
                tau = JumpPlant._compute_motor_torque(plant, native.numpy()[0])
            else:
                # Exact Mod4v3RLJumpEnv / Mod4v3Mujoco torque law during E0 runup
                tau = plant._compute_motor_torque(native.numpy()[0])
            if sub % 4 == 0:
                plant.d.ctrl[plant.act_ids[:4]] = tau[:4]
            plant.d.ctrl[plant.act_ids[4:]] = tau[4:]
            mj.mj_step(plant.m, plant.d)

            fr = plant.frame()
            rmat = plant.d.xmat[plant.base_id].reshape(3, 3)
            p_deg = abs(math.degrees(math.asin(float(np.clip(-rmat[2, 0], -1.0, 1.0)))))
            r_deg = abs(math.degrees(math.atan2(float(rmat[2, 1]), float(rmat[2, 2]))))
            flipped |= (p_deg > 62.0) or (r_deg > 55.0)
            if fr.total_force < 1.0 and fr.lowest > 0.006:
                peak_all = max(peak_all, fr.lowest)
                air_pitch = max(air_pitch, p_deg)
            if float(plant.d.qpos[0]) < edge + 0.15:
                face_force_max = max(face_force_max, fr.face_force)

            if writer is not None:
                sub_cnt += 1
                if sub_cnt % 16 == 0:
                    if renderer is None:
                        renderer = mj.Renderer(plant.m, height=720, width=1280)
                    cam = mj.MjvCamera()
                    cam.type = mj.mjtCamera.mjCAMERA_FREE
                    cam.lookat[:] = [float(plant.d.qpos[0]) + 0.25, 0.0, 0.30]
                    cam.distance = 2.85
                    cam.azimuth = 112.0
                    cam.elevation = -18.0
                    renderer.update_scene(plant.d, camera=cam)
                    img = Image.fromarray(renderer.render().copy())
                    draw = ImageDraw.Draw(img)
                    draw.rectangle((0, 0, 1280, 72), fill=(14, 23, 32))
                    draw.text(
                        (18, 10),
                        f"Solid {int(round(1000*plat_h))}mm 3D High Platform | Manual Space @ d={case['d_press']:.2f}m | 1x",
                        fill=(123, 230, 214),
                    )
                    draw.text(
                        (18, 36),
                        f"t={plant.d.time:.2f}s  vx={fr.vx:+.2f}m/s  lowest_z={100.*fr.lowest:.1f}cm  g_jump={np.round(gj, 2)}",
                        fill=(230, 238, 244),
                    )
                    writer.append_data(np.asarray(img))

        plant.a_prev = act_ppo.copy()
        if flipped:
            break
        if pressed and float(plant.d.qpos[0]) > edge + 0.70 and not policy.jump_active:
            break

    if writer is not None:
        writer.close()
    if renderer is not None:
        renderer.close()

    end_x = float(plant.d.qpos[0])
    end_z = float(plant.d.qpos[2])
    fr_end = plant.frame()
    on_deck = (
        end_x > edge + 0.22
        and fr_end.lowest >= plat_h - 0.012
        and (end_z - plat_h) > 0.16
        and face_force_max < 5.0
    )
    return dict(
        case,
        edge_x=round(edge, 3),
        end_x=round(end_x, 4),
        peak_all_cm=round(100.0 * peak_all, 2),
        face_force_max_N=round(face_force_max, 2),
        air_pitch_deg=round(air_pitch, 2),
        flip=flipped,
        passed=bool(pressed and not flipped and on_deck),
    )


def _worker_bridge(args):
    c, ckpt = args
    return run_rmul_bridge_case(c, ckpt)


def _worker_plat(args):
    c, ckpt = args
    return run_solid_380_platform_case(c, ckpt)


def _worker_sheer(args):
    c, ckpt = args
    return run_rmul_sheer200_case(c, ckpt)


def evaluate_checkpoint(ckpt_path: Path, workers: int = 12, quick: bool = False, render_videos: bool = False) -> dict:
    ckpt_str = str(ckpt_path)
    if quick:
        bridge_cases = [
            dict(eastbound=eb, d_press=dp, speed=sp, height=h)
            for eb in (True, False)
            for dp in (0.65, 1.15, 1.65)
            for sp, h in ((1.60, 0.28), (2.20, 0.36))
        ]  # 12 cases
        plat380_cases = [
            dict(plat_height=0.380, d_press=dp, speed=sp, height=h)
            for dp in (0.65, 1.15, 1.65)
            for sp in (1.60, 2.20)
            for h in (0.28, 0.38)
        ]  # 12 cases
    else:
        bridge_cases = [
            dict(eastbound=eb, d_press=dp, speed=sp, height=h)
            for eb in (True, False)
            for dp in (0.60, 0.90, 1.25, 1.65)
            for sp in (1.50, 1.90, 2.40)
            for h in ((0.28,) if dp in (0.90, 1.65) else (0.36,))
        ]  # 24 cases
        plat380_cases = [
            dict(plat_height=0.380, d_press=dp, speed=sp, height=h)
            for dp in (0.65, 1.00, 1.40, 1.80)
            for sp in (1.50, 1.90, 2.40)
            for h in (0.28, 0.38)
        ]  # 24 cases

    sheer_cases = [
        dict(d_press=dp, speed=sp, height=0.28)
        for dp in (0.65, 1.15, 1.65)
        for sp in (1.45, 2.00)
    ]  # 6 cases

    with ProcessPoolExecutor(max_workers=workers) as pool:
        b_res = list(pool.map(_worker_bridge, [(c, ckpt_str) for c in bridge_cases]))
        p_res = list(pool.map(_worker_plat, [(c, ckpt_str) for c in plat380_cases]))
        s_res = list(pool.map(_worker_sheer, [(c, ckpt_str) for c in sheer_cases]))

    videos = {}
    if render_videos:
        v_bridge = HERE / "media/rmul2027_bridge_hurdle_jump_1X.mp4"
        v_plat = HERE / "media/solid_380mm_platform_jump_1X.mp4"
        rb = run_rmul_bridge_case(dict(eastbound=True, d_press=1.35, speed=1.95, height=0.32), ckpt_str, video_path=v_bridge)
        rp = run_solid_380_platform_case(dict(plat_height=0.380, d_press=1.35, speed=1.95, height=0.32), ckpt_str, video_path=v_plat)
        videos = dict(bridge_video=str(v_bridge), bridge_outcome=rb, plat380_video=str(v_plat), plat380_outcome=rp)

    summary = dict(
        checkpoint=ckpt_str,
        sha256=sha256(ckpt_path),
        rmul_bridge_270x352=dict(
            passed=sum(r["passed"] for r in b_res),
            total=len(b_res),
            flips=sum(r["flip"] for r in b_res),
            mean_peak_all_cm=round(float(np.mean([r["peak_all_cm"] for r in b_res])), 2),
            cases=b_res,
        ),
        solid_platform_380mm=dict(
            passed=sum(r["passed"] for r in p_res),
            total=len(p_res),
            flips=sum(r["flip"] for r in p_res),
            mean_peak_all_cm=round(float(np.mean([r["peak_all_cm"] for r in p_res])), 2),
            cases=p_res,
        ),
        rmul_sheer_200mm=dict(
            passed=sum(r["passed"] for r in s_res),
            total=len(s_res),
            flips=sum(r["flip"] for r in s_res),
            cases=s_res,
        ),
        videos=videos,
    )
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--render-videos", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE / "evidence/PERCEPTION_JUMP_380_BRIDGE_AUDIT.json")
    args = ap.parse_args()

    res = evaluate_checkpoint(args.checkpoint, workers=args.workers, quick=args.quick, render_videos=args.render_videos)
    put(args.out, res)
    print(
        json.dumps(
            dict(
                checkpoint=res["checkpoint"],
                sha256=res["sha256"],
                rmul_bridge=f"{res['rmul_bridge_270x352']['passed']}/{res['rmul_bridge_270x352']['total']} (flips={res['rmul_bridge_270x352']['flips']}, clear={res['rmul_bridge_270x352']['mean_peak_all_cm']}cm)",
                plat380=f"{res['solid_platform_380mm']['passed']}/{res['solid_platform_380mm']['total']} (flips={res['solid_platform_380mm']['flips']}, clear={res['solid_platform_380mm']['mean_peak_all_cm']}cm)",
                rmul_sheer200=f"{res['rmul_sheer_200mm']['passed']}/{res['rmul_sheer_200mm']['total']}",
                videos={k: v for k, v in res["videos"].items() if isinstance(v, str)},
            ),
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()

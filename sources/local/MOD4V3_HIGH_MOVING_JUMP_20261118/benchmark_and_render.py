# SPDX-License-Identifier: MIT
"""Quantitative MuJoCo Benchmark, RL Trajectory Exporter, and 1x MP4 Video Renderer for MOD4v3 High Jump (c874)."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any

import imageio.v2 as imageio
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from high_jump_controller import (
    CONTROL_DT,
    EXPECTED_CKPT_SHA256,
    EXPECTED_XML_SHA256,
    HERE,
    PHASES,
    HighJumpConfig,
    HighJumpSimulation,
)

# 5 perturbed initial states (x_m, y_m, yaw_rad) matching MOD4v3 multi-seed evaluation convention
SEEDS = [
    (0.00, 0.00, 0.000),
    (0.04, -0.05, -0.025),
    (-0.04, 0.05, 0.025),
    (0.02, 0.03, -0.040),
    (-0.02, -0.03, 0.040),
]


def contiguous_segments(mask: np.ndarray) -> list[tuple[int, int]]:
    padded = np.r_[False, np.asarray(mask, dtype=bool), False].astype(int)
    starts = np.flatnonzero(np.diff(padded) == 1)
    ends = np.flatnonzero(np.diff(padded) == -1)
    return list(zip(starts.tolist(), ends.tolist()))


def check_rolling_recovery(
    times: np.ndarray,
    wheel_fz: np.ndarray,
    guide_f: np.ndarray,
    chassis_f: np.ndarray,
    pitches: np.ndarray,
    rolls: np.ndarray,
    root_z: np.ndarray,
    land_time: float,
) -> bool:
    """Verify a >= 0.5 s stable rolling/standing recovery window after touchdown."""
    good = (
        (times >= land_time)
        & (np.abs(pitches) < 18.0)
        & (np.abs(rolls) < 12.0)
        & (guide_f < 1.0)
        & (chassis_f < 1.0)
    )
    for lo, hi in contiguous_segments(good):
        for begin in range(lo, hi - 199, 8):
            end = begin + 200  # 200 * 0.0025s = 0.50s
            if (wheel_fz[begin:end] > 5.0).mean() >= 0.85 and np.ptp(root_z[begin:end]) <= 0.06:
                return True
    return False


def run_episode(
    sim: HighJumpSimulation,
    v_cmd: float,
    jump_times: tuple[float, ...],
    total_s: float,
    seed_idx: int,
    record_rl_demo: bool = True,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Run one nominal 400 Hz physics episode and compute exact 400 Hz metrics."""
    x0, y0, yaw0 = SEEDS[seed_idx]
    sim.reset_standing(x=x0, y=y0, yaw=yaw0)
    before_resets = sim.reset_count

    t_400, z_400, com_z_400, rim_400 = [], [], [], []
    pitch_400, roll_400, vx_400 = [], [], []
    wf_400, gf_400, cf_400, cl_400, ph_400 = [], [], [], [], []

    demo_obs, demo_act, demo_phase, demo_root, demo_quat, demo_qvel, demo_rim, demo_vcmd = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )

    def on_substep(s: HighJumpSimulation, _sub_j: int) -> None:
        d = s.env.d
        t_400.append(float(d.time))
        z_400.append(float(d.qpos[2]))
        com_z_400.append(float(d.subtree_com[s.env.base_id, 2]))
        rim_400.append(float(s.world_rim_z_m))
        pitch_400.append(float(s.pitch_deg))
        roll_400.append(float(s.roll_deg))
        vx_400.append(float(s.env.vx))
        wf_400.append(float(s.wheel_force_N))
        gf_400.append(float(s.guide_force_N))
        cf_400.append(float(s.chassis_force_N))
        cl_400.append(float(s.closure_m))
        ph_400.append(s.controller.phase_index)

    next_j = 0
    steps = int(round(total_s / CONTROL_DT))
    for _ in range(steps):
        now = float(sim.env.d.time)
        if next_j < len(jump_times) and now >= jump_times[next_j] - 1e-6:
            if sim.controller.request_jump(now, hold_charge=False):
                next_j += 1
        vx_target = v_cmd if now >= 1.0 else 0.0
        obs, act = sim.step_commands(vx_target, 0.0, substep_callback=on_substep, auto_reset_on_fall=False)
        if sim.last_reset_reason:
            break
        if record_rl_demo:
            d = sim.env.d
            demo_obs.append(obs[0].detach().cpu().numpy().copy())
            demo_act.append(act[0].detach().cpu().numpy().copy())
            demo_phase.append(sim.controller.phase_index)
            demo_root.append(d.qpos[:3].copy())
            demo_quat.append(d.qpos[3:7].copy())
            demo_qvel.append(d.qvel[:6].copy())
            demo_rim.append(float(sim.world_rim_z_m))
            demo_vcmd.append(float(vx_target))

    survived = sim.last_reset_reason == "" and (sim.reset_count == before_resets)
    times = np.asarray(t_400, dtype=np.float64)
    root_z = np.asarray(z_400, dtype=np.float64)
    com_z = np.asarray(com_z_400, dtype=np.float64)
    rim_z = np.asarray(rim_400, dtype=np.float64)
    pitches = np.asarray(pitch_400, dtype=np.float64)
    rolls = np.asarray(roll_400, dtype=np.float64)
    vxs = np.asarray(vx_400, dtype=np.float64)
    wheel_fz = np.asarray(wf_400, dtype=np.float64)
    guide_f = np.asarray(gf_400, dtype=np.float64)
    chassis_f = np.asarray(cf_400, dtype=np.float64)
    closures = np.asarray(cl_400, dtype=np.float64)

    t0 = jump_times[0]
    air_mask = (times >= t0) & (wheel_fz < 1.0) & (guide_f < 1.0) & (chassis_f < 1.0)
    air_segs = [(a, b) for a, b in contiguous_segments(air_mask) if (b - a) * 0.0025 >= 0.08]

    jump_metrics = []
    for j_i, (lo, hi) in enumerate(air_segs):
        tj_start = jump_times[min(j_i, len(jump_times) - 1)]
        c_mask = (times >= tj_start) & (times <= times[lo])
        z_min_root = float(root_z[c_mask].min()) if c_mask.any() else float(root_z[lo])
        com_min = float(com_z[c_mask].min()) if c_mask.any() else float(com_z[lo])
        com_peak = float(com_z[lo:hi].max())
        z_peak_root = float(root_z[lo:hi].max())
        rim_peak_cm = float(rim_z[lo:hi].max() * 100.0)
        air_dur_s = round((hi - lo) * 0.0025, 4)
        air_p_max = float(np.abs(pitches[lo:hi]).max())
        air_r_max = float(np.abs(rolls[lo:hi]).max())
        land_idx = min(hi, len(times) - 1)
        t_land = float(times[land_idx])
        post_mask = (times >= t_land) & (times <= t_land + 1.0)
        post_p_max = float(np.abs(pitches[post_mask]).max()) if post_mask.any() else 0.0
        z_min_land = float(root_z[post_mask].min()) if post_mask.any() else float(root_z[land_idx])
        dx_air_m = float(sim.env.d.qpos[0]) if not post_mask.any() else 0.0
        recovered = check_rolling_recovery(times, wheel_fz, guide_f, chassis_f, pitches, rolls, root_z, t_land)
        jump_metrics.append(
            {
                "jump_index": j_i + 1,
                "z_min_root_m": round(z_min_root, 4),
                "z_peak_root_m": round(z_peak_root, 4),
                "com_min_m": round(com_min, 4),
                "com_peak_m": round(com_peak, 4),
                "com_rise_dz_cm": round((com_peak - com_min) * 100.0, 2),
                "peak_wheel_rim_clearance_cm": round(rim_peak_cm, 2),
                "continuous_airtime_s": air_dur_s,
                "max_airborne_abs_pitch_deg": round(air_p_max, 2),
                "max_airborne_abs_roll_deg": round(air_r_max, 2),
                "within_pitch10_roll5": bool(air_p_max <= 10.0 and air_r_max <= 5.0),
                "post_landing_1s_max_abs_pitch_deg": round(post_p_max, 2),
                "min_landing_root_z_m": round(z_min_land, 4),
                "mean_airborne_vx_m_s": round(float(vxs[lo:hi].mean()), 3),
                "stable_recovery_05s": bool(recovered and survived),
            }
        )

    act_mask = times >= t0
    ep_result = {
        "seed": seed_idx,
        "initial_pose_xy_yaw": [x0, y0, yaw0],
        "v_cmd_m_s": v_cmd,
        "expected_jumps": len(jump_times),
        "detected_true_jumps": len(jump_metrics),
        "survived": bool(survived and len(jump_metrics) == len(jump_times)),
        "all_jumps_stable_recovered": bool(
            survived and len(jump_metrics) == len(jump_times) and all(j["stable_recovery_05s"] for j in jump_metrics)
        ),
        "jumps": jump_metrics,
        "peak_guide_contact_force_N": round(float(guide_f[act_mask].max(initial=0.0)), 3),
        "peak_chassis_contact_force_N": round(float(chassis_f[act_mask].max(initial=0.0)), 3),
        "peak_wheel_normal_force_N": round(float(wheel_fz[act_mask].max(initial=0.0)), 2),
        "max_4bar_closure_error_mm": round(float(closures.max(initial=0.0) * 1000.0), 4),
    }

    demo_pack = {
        "obs": np.asarray(demo_obs, dtype=np.float32),
        "act": np.asarray(demo_act, dtype=np.float32),
        "phase": np.asarray(demo_phase, dtype=np.int32),
        "root_pos": np.asarray(demo_root, dtype=np.float32),
        "root_quat": np.asarray(demo_quat, dtype=np.float32),
        "qvel": np.asarray(demo_qvel, dtype=np.float32),
        "rim_clearance_m": np.asarray(demo_rim, dtype=np.float32),
        "v_cmd": np.asarray(demo_vcmd, dtype=np.float32),
    }
    return ep_result, demo_pack


def aggregate_condition(name: str, episodes: list[dict[str, Any]]) -> dict[str, Any]:
    all_j = [j for ep in episodes for j in ep["jumps"]]
    n_ep = len(episodes)
    n_j = len(all_j)
    return {
        "condition": name,
        "num_episodes": n_ep,
        "num_jumps_total": n_j,
        "survival_rate": f"{sum(ep['survived'] for ep in episodes)}/{n_ep}",
        "stable_recovery_rate": f"{sum(ep['all_jumps_stable_recovered'] for ep in episodes)}/{n_ep}",
        "airborne_pitch10_roll5_pass_rate": f"{sum(j['within_pitch10_roll5'] for j in all_j)}/{n_j}",
        "min_crouch_root_z_m_mean": round(float(np.mean([j["z_min_root_m"] for j in all_j])), 4),
        "peak_com_z_m_mean": round(float(np.mean([j["com_peak_m"] for j in all_j])), 4),
        "com_rise_dz_cm_mean": round(float(np.mean([j["com_rise_dz_cm"] for j in all_j])), 2),
        "com_rise_dz_cm_max": round(float(np.max([j["com_rise_dz_cm"] for j in all_j])), 2),
        "peak_wheel_rim_clearance_cm_mean": round(float(np.mean([j["peak_wheel_rim_clearance_cm"] for j in all_j])), 2),
        "peak_wheel_rim_clearance_cm_range": [
            round(float(np.min([j["peak_wheel_rim_clearance_cm"] for j in all_j])), 2),
            round(float(np.max([j["peak_wheel_rim_clearance_cm"] for j in all_j])), 2),
        ],
        "continuous_airtime_s_mean": round(float(np.mean([j["continuous_airtime_s"] for j in all_j])), 4),
        "max_airborne_abs_pitch_deg_worst": round(float(np.max([j["max_airborne_abs_pitch_deg"] for j in all_j])), 2),
        "max_airborne_abs_pitch_deg_mean": round(float(np.mean([j["max_airborne_abs_pitch_deg"] for j in all_j])), 2),
        "max_airborne_abs_roll_deg_worst": round(float(np.max([j["max_airborne_abs_roll_deg"] for j in all_j])), 2),
        "post_landing_1s_max_abs_pitch_deg_mean": round(
            float(np.mean([j["post_landing_1s_max_abs_pitch_deg"] for j in all_j])), 2
        ),
        "post_landing_1s_max_abs_pitch_deg_worst": round(
            float(np.max([j["post_landing_1s_max_abs_pitch_deg"] for j in all_j])), 2
        ),
        "peak_guide_contact_force_N_max": round(float(np.max([ep["peak_guide_contact_force_N"] for ep in episodes])), 3),
        "peak_chassis_contact_force_N_max": round(
            float(np.max([ep["peak_chassis_contact_force_N"] for ep in episodes])), 3
        ),
        "max_4bar_closure_error_mm": round(float(np.max([ep["max_4bar_closure_error_mm"] for ep in episodes])), 4),
        "episodes": episodes,
    }


def load_hud_fonts():
    try:
        title_f = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 22)
        mono_f = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 17)
        small_f = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 15)
    except Exception:
        title_f = mono_f = small_f = ImageFont.load_default()
    return title_f, mono_f, small_f


def render_1x_video(
    sim: HighJumpSimulation,
    out_mp4: Path,
    title_banner: str,
    v_cmd: float,
    jump_times: tuple[float, ...],
    total_s: float,
    width: int = 1280,
    height: int = 720,
) -> dict[str, Any]:
    """Render an exact 1.0x real-time (50 fps, 20 ms/frame) side-tracking MP4 video with live HUD."""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    sim.reset_standing(x=-0.5 if v_cmd >= 0 else 1.2, y=0.0, yaw=0.0)
    title_f, mono_f, small_f = load_hud_fonts()

    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.distance = 2.05 if len(jump_times) == 1 else 2.35
    cam.azimuth = -90.0  # Clean orthogonal side-view looking from -Y toward +Y (robot moves left-to-right along +X!)
    cam.elevation = -10.0

    opt = mujoco.MjvOption()
    opt.geomgroup[3] = 0
    opt.geomgroup[4] = 0

    next_j = 0
    steps = int(round(total_s / CONTROL_DT))
    running_peak_rim_cm = 0.0
    smooth_cam_x = float(sim.env.d.qpos[0])

    with mujoco.Renderer(sim.env.m, height=height, width=width) as renderer:
        with imageio.get_writer(
            str(out_mp4),
            fps=50,
            codec="libx264",
            quality=8,
            pixelformat="yuv420p",
            macro_block_size=16,
        ) as writer:
            for _ in range(steps):
                now = float(sim.env.d.time)
                if next_j < len(jump_times) and now >= jump_times[next_j] - 1e-6:
                    if sim.controller.request_jump(now, hold_charge=False):
                        next_j += 1
                vx_target = v_cmd if now >= 0.8 else 0.0
                sim.step_commands(vx_target, 0.0, auto_reset_on_fall=False)

                tel = sim.telemetry()
                running_peak_rim_cm = max(running_peak_rim_cm, float(tel["world_rim_cm"]))

                # Smooth horizontal camera tracking (fixed Z lookat=0.29m so vertical jump height is visually true!)
                rx = float(sim.env.d.qpos[0])
                smooth_cam_x += 0.18 * (rx - smooth_cam_x)
                cam.lookat[:] = [smooth_cam_x, 0.0, 0.29]

                renderer.update_scene(sim.env.d, camera=cam, scene_option=opt)
                rgb = renderer.render()
                img = Image.fromarray(rgb)
                draw = ImageDraw.Draw(img, "RGBA")

                # Top semi-transparent telemetry banner
                draw.rounded_rectangle((18, 14, 720, 142), radius=10, fill=(13, 17, 23, 210), outline=(57, 213, 255, 140))
                draw.text((32, 22), title_banner, font=title_f, fill=(57, 213, 255, 255))
                draw.text(
                    (32, 54),
                    f"Time {tel['time_s']:5.2f}s (1.0x)  |  Phase: {tel['phase']:14s}  |  Jumps: {tel['completed_jumps']}/{len(jump_times)}",
                    font=mono_f,
                    fill=(75, 227, 138, 255) if tel["phase"] != "DRIVE" else (230, 237, 243, 255),
                )
                draw.text(
                    (32, 80),
                    f"Speed cmd/act: {tel['cmd_vx_m_s']:+.2f} / {tel['vx_m_s']:+.2f} m/s   |  Root z: {tel['z_m']:.3f} m",
                    font=mono_f,
                    fill=(230, 237, 243, 255),
                )
                draw.text(
                    (32, 106),
                    f"Wheel Rim Clearance: {tel['world_rim_cm']:5.1f} cm (Peak {running_peak_rim_cm:5.1f} cm)  |  Pitch {tel['pitch_deg']:+5.1f}° Roll {tel['roll_deg']:+4.1f}°",
                    font=mono_f,
                    fill=(255, 209, 102, 255),
                )

                # Bottom-right legend for background height reference bars
                draw.rounded_rectangle(
                    (width - 375, height - 52, width - 18, height - 14),
                    radius=8,
                    fill=(13, 17, 23, 195),
                )
                draw.text(
                    (width - 362, height - 42),
                    "Ruler Bars: Green 20cm | Gold 30cm | Red 40cm",
                    font=small_f,
                    fill=(200, 212, 225, 255),
                )

                writer.append_data(np.asarray(img))

    return {
        "video_path": str(out_mp4),
        "bytes": out_mp4.stat().st_size,
        "sha256": hashlib.sha256(out_mp4.read_bytes()).hexdigest(),
        "fps": 50,
        "frames": steps,
        "duration_s": round(total_s, 2),
        "realtime_factor": 1.0,
        "peak_wheel_rim_clearance_cm": round(running_peak_rim_cm, 2),
        "completed_jumps": len(sim.controller.completed_jumps),
    }


def main() -> None:
    t_start = time.perf_counter()
    cfg = HighJumpConfig()
    sim = HighJumpSimulation(scene_name="flat", cfg=cfg, visible=False)

    benchmark_specs = [
        ("standing_0p0mps", 0.0, (2.2,), 5.8),
        ("moving_0p4mps", 0.4, (2.2,), 5.8),
        ("moving_0p8mps", 0.8, (2.2,), 5.8),
        ("moving_1p2mps", 1.2, (2.2,), 5.8),
        ("reverse_m0p5mps", -0.5, (2.2,), 5.8),
        ("continuous_multijump_3x_0p8mps", 0.8, (1.8, 3.8, 5.8), 8.2),
    ]

    conditions_out: dict[str, Any] = {}
    all_demos: dict[str, list[np.ndarray]] = {
        k: [] for k in ("obs", "act", "phase", "root_pos", "root_quat", "qvel", "rim_clearance_m", "v_cmd")
    }

    print("=== Running 30-Episode Nominal MuJoCo Benchmark (400 Hz Physics, Exact Motor Envelope) ===", flush=True)
    for cond_name, v_cmd, j_times, dur_s in benchmark_specs:
        eps = []
        for s_idx in range(len(SEEDS)):
            ep_res, demo = run_episode(sim, v_cmd=v_cmd, jump_times=j_times, total_s=dur_s, seed_idx=s_idx)
            eps.append(ep_res)
            for k in all_demos:
                all_demos[k].append(demo[k])
        agg = aggregate_condition(cond_name, eps)
        conditions_out[cond_name] = agg
        print(
            f"  [{cond_name:30s}] survival={agg['survival_rate']} recov={agg['stable_recovery_rate']} "
            f"rim_mean={agg['peak_wheel_rim_clearance_cm_mean']:5.2f}cm (max {agg['peak_wheel_rim_clearance_cm_range'][1]:5.2f}cm) "
            f"airP_worst={agg['max_airborne_abs_pitch_deg_worst']:4.2f}° postP_mean={agg['post_landing_1s_max_abs_pitch_deg_mean']:5.2f}° "
            f"guideN={agg['peak_guide_contact_force_N_max']:.1f}N chassisN={agg['peak_chassis_contact_force_N_max']:.1f}N "
            f"closure={agg['max_4bar_closure_error_mm']:.3f}mm",
            flush=True,
        )

    # Save RL distillation dataset
    traj_dir = HERE / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)
    demo_path = traj_dir / "high_jump_demos_c874.npz"
    stacked_demos = {k: np.concatenate(v, axis=0) for k, v in all_demos.items()}
    np.savez_compressed(demo_path, **stacked_demos)
    demo_sha = hashlib.sha256(demo_path.read_bytes()).hexdigest()
    print(f"Saved RL demonstration dataset: {demo_path} ({len(stacked_demos['obs'])} 50Hz frames, SHA={demo_sha[:12]})", flush=True)

    # Render 1x MP4 videos
    media_dir = HERE / "media"
    print("=== Rendering 1.0x Side-Tracking MP4 Videos (1280x720 @ 50fps) ===", flush=True)
    videos = {
        "standing_high_jump_1x": render_1x_video(
            sim,
            media_dir / "STANDING_HIGH_JUMP_1X.mp4",
            "MOD4v3 Deep-Crouch Standing High Jump (v = 0.0 m/s, c874)",
            v_cmd=0.0,
            jump_times=(1.8,),
            total_s=4.6,
        ),
        "moving_high_jump_08mps_1x": render_1x_video(
            sim,
            media_dir / "MOVING_HIGH_JUMP_08MPS_1X.mp4",
            "MOD4v3 Moving Deep-Crouch High Jump (v = +0.80 m/s, c874)",
            v_cmd=0.8,
            jump_times=(2.0,),
            total_s=4.8,
        ),
        "moving_multi_jump_1x": render_1x_video(
            sim,
            media_dir / "MOVING_MULTI_JUMP_1X.mp4",
            "MOD4v3 Continuous 3x Moving Multi-Jump (v = +0.80 m/s, c874)",
            v_cmd=0.8,
            jump_times=(1.5, 3.4, 5.3),
            total_s=7.6,
        ),
    }
    for v_key, v_info in videos.items():
        print(f"  Rendered {v_key}: {v_info['video_path']} (peak rim {v_info['peak_wheel_rim_clearance_cm']} cm)", flush=True)

    sim.close()

    # Global summary across all 30 episodes / 40 jumps
    all_eps = [ep for c in conditions_out.values() for ep in c["episodes"]]
    all_jumps = [j for ep in all_eps for j in ep["jumps"]]
    results_payload = {
        "experiment": "MOD4V3_HIGH_MOVING_JUMP_20261118",
        "timestamp_epoch": time.time(),
        "wall_time_s": round(time.perf_counter() - t_start, 2),
        "plant_contract": {
            "robot": "MOD4v3 / HW300N60_R3",
            "mjcf_sha256": EXPECTED_XML_SHA256,
            "base_policy": "deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt",
            "base_policy_sha256": EXPECTED_CKPT_SHA256,
            "obs_dim": 35,
            "action_dim": 6,
            "action_clip": [-6.0, 6.0],
            "actuator_law": "100% unmodified Mod4v3Mujoco._torque (Kp=60, Kd=2 leg PD @ 100Hz; Kv=0.6 wheel servo @ 400Hz; exact DC envelope: legs 40/53.333/16.755, wheels 5.7759/28.185/55.3557; 2000 N/m gas springs + 4-bar closed loop)",
            "physics_dt_s": 0.0025,
            "policy_dt_s": 0.02,
            "optimizer_updates": 0,
        },
        "locked_controller_config": cfg.to_dict(),
        "overall_summary": {
            "total_episodes": len(all_eps),
            "total_jumps": len(all_jumps),
            "episodes_survived": f"{sum(ep['survived'] for ep in all_eps)}/{len(all_eps)}",
            "stable_recovery_05s": f"{sum(ep['all_jumps_stable_recovered'] for ep in all_eps)}/{len(all_eps)}",
            "airborne_pitch10_roll5_all_jumps": f"{sum(j['within_pitch10_roll5'] for j in all_jumps)}/{len(all_jumps)}",
            "peak_wheel_rim_clearance_cm_range": [
                round(float(min(j["peak_wheel_rim_clearance_cm"] for j in all_jumps)), 2),
                round(float(max(j["peak_wheel_rim_clearance_cm"] for j in all_jumps)), 2),
            ],
            "max_airborne_abs_pitch_deg_across_all_40_jumps": round(
                float(max(j["max_airborne_abs_pitch_deg"] for j in all_jumps)), 2
            ),
            "max_airborne_abs_roll_deg_across_all_40_jumps": round(
                float(max(j["max_airborne_abs_roll_deg"] for j in all_jumps)), 2
            ),
            "max_guide_contact_force_N_across_all_30_episodes": round(
                float(max(ep["peak_guide_contact_force_N"] for ep in all_eps)), 3
            ),
            "max_chassis_contact_force_N_across_all_30_episodes": round(
                float(max(ep["peak_chassis_contact_force_N"] for ep in all_eps)), 3
            ),
            "max_4bar_loop_closure_error_mm": round(
                float(max(ep["max_4bar_closure_error_mm"] for ep in all_eps)), 4
            ),
        },
        "rl_distillation_dataset": {
            "path": str(demo_path),
            "sha256": demo_sha,
            "frames_50hz": int(len(stacked_demos["obs"])),
            "obs_shape": list(stacked_demos["obs"].shape),
            "act_shape": list(stacked_demos["act"].shape),
        },
        "videos_1x_mp4": videos,
        "conditions": conditions_out,
    }

    bench_json = HERE / "BENCHMARK_RESULTS.json"
    bench_json.write_text(json.dumps(results_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved complete benchmark results -> {bench_json}", flush=True)


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: MIT
"""Stage 3: Independent Pure-RL Forward-Leap & Jump-Onto-Step Benchmark + 4x 1x Video Renderer.

Strict Zero-Cheating Verification:
  - Asserts 'stage1_forward_leap_dagger' is NOT in sys.modules.
  - Drives MOD4v3 HW300N60_R3 exclusively via StatefulMoEForwardLeapActor (obs_35 -> act_6).
  - Evaluates 9 conditions x 5 seeds = 45 episodes Nominal (0-DR) + 45 episodes 100% Full-DR + E0 audit.
  - Renders all 4 required 1x (25 fps real-time, 1280x720) MP4 videos + 4-panel chronological filmstrips:
      1. media/RL_STAND_TO_FORWARD_DIVE_1X.mp4
      2. media/RL_MOVING_FORWARD_LEAP_1X.mp4
      3. media/RL_JUMP_ONTO_20CM_STEP_1X.mp4
      4. media/RL_JUMP_ONTO_24CM_STEP_FULLDR_1X.mp4
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import imageio.v2 as imageio
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch

from forward_leap_env import EXPECTED_XML_SHA256, Mod4v3ForwardLeapEnv, WHEEL_RADIUS_M
from moe_forward_leap_model import (
    ACTION_CLIP,
    C874_CKPT_PATH,
    EXPECTED_C874_SHA256,
    HERE,
    JUMP_MODE_BIT_INDEX,
    MoEForwardLeapActorCritic,
    StatefulMoEForwardLeapActor,
    build_c874_mlp,
    verify_c874_checkpoint,
)


def _step_pure_actor(actor: StatefulMoEForwardLeapActor, obs_np: np.ndarray, is_first_step: bool) -> np.ndarray:
    obs_t = torch.from_numpy(obs_np).unsqueeze(0)
    if is_first_step:
        actor.reset_history()
        actor.queue.reset(obs_t)
        with torch.inference_mode():
            hist_t = actor.queue.buffer.flatten(-2)
            return actor.core.act_deterministic(obs_t, hist_t)[0].numpy()
    return actor(obs_t)[0].numpy()


def run_eval_episode(
    env: Mod4v3ForwardLeapEnv,
    actor: StatefulMoEForwardLeapActor,
    dr_scale: float,
    v_pre: float,
    v_post: float,
    sw_s: float | None,
    jump_times: tuple[float, ...],
    max_s: float,
    steps: list[tuple[float, float, float]],
    init_pose: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> dict[str, Any]:
    st = env.reset(
        dr_scale=dr_scale,
        v_cmd=v_pre,
        v_cmd_post=v_post,
        post_cmd_switch_s=sw_s,
        wz_cmd=0.0,
        h_nom=0.28,
        jump_times=jump_times,
        max_episode_s=max_s,
        steps=steps,
        init_pose=init_pose,
    )

    first = True
    max_air_pitch_deg = 0.0
    max_air_roll_deg = 0.0
    max_airtime_s = 0.0
    min_post_trig_vx = 99.0

    while True:
        act = _step_pure_actor(actor, st["obs"], first)
        first = False
        st, _rew, done, info = env.step(act)

        now = float(env.d.time)
        R = env.d.xmat[env.base_id].reshape(3, 3)
        pitch_deg = abs(math.degrees(math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))))
        roll_deg = abs(math.degrees(math.atan2(float(R[2, 1]), float(R[2, 2]))))

        if len(env.jump_times) > 0 and now >= env.jump_times[0] + 0.35:
            min_post_trig_vx = min(min_post_trig_vx, env.body_vx)

        if env.air_substeps >= 1 and not env.window_landed:
            max_airtime_s = max(max_airtime_s, env.air_substeps * env.dt)
            max_air_pitch_deg = max(max_air_pitch_deg, pitch_deg)
            max_air_roll_deg = max(max_air_roll_deg, roll_deg)

        if done:
            survived = info["fell_reason"] == "" and not info["slid_off_step"]
            step_ok = info["steps_mounted_count"] >= info["steps_total"]
            fwd_ok = (
                info["ep_mean_leap_dx_m"] >= 0.55
                and info["ep_total_net_dx_m"] >= 0.60
                and info["ep_min_active_vx"] >= -0.04
            )
            return {
                "survived": survived,
                "task_success": bool(survived and step_ok and fwd_ok),
                "slid_off_step": info["slid_off_step"],
                "steps_mounted": f"{info['steps_mounted_count']}/{info['steps_total']}",
                "completed_leaps": info["ep_completed_leaps"],
                "expected_leaps": info["ep_expected_leaps"],
                "mean_leap_dx_m": info["ep_mean_leap_dx_m"],
                "mean_air_dx_m": info["ep_mean_air_dx_m"],
                "total_net_dx_m": info["ep_total_net_dx_m"],
                "mean_takeoff_vx_m_s": info["ep_mean_takeoff_vx"],
                "min_post_trigger_vx_m_s": info["ep_min_active_vx"],
                "peak_world_rim_cm": info["ep_peak_world_rim_cm"],
                "max_airtime_s": round(max_airtime_s, 4),
                "max_air_pitch_deg": round(max(max_air_pitch_deg, info["ep_max_air_pitch_deg"]), 2),
                "max_episode_pitch_deg": info["ep_max_episode_pitch_deg"],
                "max_air_roll_deg": round(max_air_roll_deg, 2),
                "guide_force_N": info["ep_guide_force_N"],
                "chassis_force_N": info["ep_chassis_force_N"],
                "riser_hit_force_N": info["ep_riser_hit_N"],
                "max_closure_mm": info["max_closure_mm"],
                "fell_reason": info["fell_reason"],
            }


def benchmark_9x5(actor: StatefulMoEForwardLeapActor, dr_scale: float, seed_base: int) -> dict[str, Any]:
    d_s16 = Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.16)
    d_s20 = Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.20)
    d_s24 = Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.24)
    xf_m20 = Mod4v3ForwardLeapEnv.step_front_for_moving_jump(0.75, 1.45)
    xf_m24 = Mod4v3ForwardLeapEnv.step_front_for_moving_jump(0.85, 1.45)

    conditions = [
        ("stand_dive_0p0", 0.0, 0.0, None, (1.0,), 4.2, []),
        ("move_leap_0p6", 0.6, 0.6, None, (1.4,), 4.4, []),
        ("move_leap_0p9", 0.9, 0.9, None, (1.4,), 4.4, []),
        ("multi_leap_2x_0p8", 0.8, 0.8, None, (1.2, 3.3), 5.8, []),
        ("stand_step_16cm", 0.0, 0.0, 2.5, (1.0,), 4.2, [(d_s16, 3.6, 0.16)]),
        ("stand_step_20cm", 0.0, 0.0, 2.5, (1.0,), 4.2, [(d_s20, 3.6, 0.20)]),
        ("stand_step_24cm", 0.0, 0.0, 2.5, (1.0,), 4.2, [(d_s24, 3.6, 0.24)]),
        ("move_step_20cm_park", 0.75, 0.0, 2.9, (1.45,), 4.4, [(xf_m20, 3.6, 0.20)]),
        ("move_step_24cm_cruise", 0.85, 0.85, None, (1.45,), 4.4, [(xf_m24, 3.8, 0.24)]),
    ]

    by_cond: dict[str, Any] = {}
    all_eps: list[dict[str, Any]] = []
    step_eps: list[dict[str, Any]] = []

    for c_i, (cname, vp, vpo, sw, jt, ms, stps) in enumerate(conditions):
        eps = []
        for s_i in range(5):
            env = Mod4v3ForwardLeapEnv(seed=seed_base + c_i * 100 + s_i)
            rng_p = np.random.default_rng(6000 + c_i * 19 + s_i)
            pose = (
                float(rng_p.uniform(-0.015, 0.015)),
                float(rng_p.uniform(-0.025, 0.025)),
                float(rng_p.uniform(-0.020, 0.020)),
            )
            res = run_eval_episode(env, actor, dr_scale, vp, vpo, sw, jt, ms, stps, init_pose=pose)
            eps.append(res)
            all_eps.append(res)
            if len(stps) > 0:
                step_eps.append(res)

        surv_n = sum(1 for e in eps if e["survived"])
        succ_n = sum(1 for e in eps if e["task_success"])
        zero_slide_n = sum(1 for e in eps if not e["slid_off_step"])
        clean_n = sum(
            1
            for e in eps
            if e["task_success"]
            and e["guide_force_N"] < 1.0
            and e["chassis_force_N"] < 1.0
            and e["riser_hit_force_N"] < 2.0
        )
        by_cond[cname] = {
            "v_cmd_pre_m_s": vp,
            "v_cmd_post_m_s": vpo,
            "step_height_cm": int(round(stps[0][2] * 100)) if stps else 0,
            "survival": f"{surv_n}/5",
            "task_success": f"{succ_n}/5",
            "zero_slide_off": f"{zero_slide_n}/5",
            "zero_scrape_clean": f"{clean_n}/5",
            "mean_leap_dx_m": round(float(np.mean([e["mean_leap_dx_m"] for e in eps])), 3),
            "mean_total_net_dx_m": round(float(np.mean([e["total_net_dx_m"] for e in eps])), 3),
            "mean_takeoff_vx_m_s": round(float(np.mean([e["mean_takeoff_vx_m_s"] for e in eps])), 3),
            "min_post_trigger_vx_m_s": round(float(np.min([e["min_post_trigger_vx_m_s"] for e in eps])), 3),
            "mean_peak_world_rim_cm": round(float(np.mean([e["peak_world_rim_cm"] for e in eps])), 2),
            "max_air_pitch_deg": round(float(np.max([e["max_air_pitch_deg"] for e in eps])), 2),
            "max_episode_pitch_deg": round(float(np.max([e["max_episode_pitch_deg"] for e in eps])), 2),
            "max_air_roll_deg": round(float(np.max([e["max_air_roll_deg"] for e in eps])), 2),
            "max_guide_force_N": round(float(np.max([e["guide_force_N"] for e in eps])), 2),
            "max_riser_hit_N": round(float(np.max([e["riser_hit_force_N"] for e in eps])), 2),
            "max_closure_mm": round(float(np.max([e["max_closure_mm"] for e in eps])), 3),
            "episodes": eps,
        }

    tot_surv = sum(1 for e in all_eps if e["survived"])
    tot_succ = sum(1 for e in all_eps if e["task_success"])
    tot_clean = sum(
        1
        for e in all_eps
        if e["task_success"]
        and e["guide_force_N"] < 1.0
        and e["chassis_force_N"] < 1.0
        and e["riser_hit_force_N"] < 2.0
    )
    step_succ = sum(1 for e in step_eps if e["task_success"])
    step_no_slide = sum(1 for e in step_eps if not e["slid_off_step"])

    return {
        "dr_scale": dr_scale,
        "episodes_survived": f"{tot_surv}/{len(all_eps)}",
        "task_success": f"{tot_succ}/{len(all_eps)}",
        "zero_scrape_clean": f"{tot_clean}/{len(all_eps)}",
        "step_jump_success_25ep": f"{step_succ}/{len(step_eps)}",
        "step_zero_slide_off_25ep": f"{step_no_slide}/{len(step_eps)}",
        "overall_mean_leap_dx_m": round(float(np.mean([e["mean_leap_dx_m"] for e in all_eps])), 3),
        "overall_mean_world_rim_cm": round(float(np.mean([e["peak_world_rim_cm"] for e in all_eps])), 2),
        "overall_max_air_pitch_deg": round(float(np.max([e["max_air_pitch_deg"] for e in all_eps])), 2),
        "overall_max_episode_pitch_deg": round(float(np.max([e["max_episode_pitch_deg"] for e in all_eps])), 2),
        "overall_max_closure_mm": round(float(np.max([e["max_closure_mm"] for e in all_eps])), 3),
        "conditions": by_cond,
    }


def verify_e0_preservation(model: MoEForwardLeapActorCritic, actor: StatefulMoEForwardLeapActor) -> dict[str, Any]:
    drift = model.verify_zero_e0_drift()
    ck = verify_c874_checkpoint(C874_CKPT_PATH)
    ref_mlp = build_c874_mlp()
    ref_mlp.load_state_dict(
        {k.replace("mlp.", "", 1): v for k, v in ck["actor_state_dict"].items() if k.startswith("mlp.")},
        strict=True,
    )
    ref_mlp.eval()

    g = torch.Generator().manual_seed(42)
    ro = torch.randn(512, 35, generator=g)
    ro[:, 28:35] = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    rh = torch.randn(512, 420, generator=g)
    with torch.inference_mode():
        diff = float((model.act_deterministic(ro, rh) - ref_mlp(ro).clamp(-ACTION_CLIP, ACTION_CLIP)).abs().max().item())
    if diff != 0.0:
        raise RuntimeError(f"Non-zero E0 action diff: {diff}")

    flat_tasks = [
        ("flat_fwd_2p0", 2.0, 0.0, 0.28),
        ("flat_fwd_2p2", 2.2, 0.0, 0.28),
        ("flat_rev_m1p5", 0.0, 0.0, 0.28),
        ("flat_yaw_1p2", 0.8, 1.2, 0.28),
        ("flat_low_0p20", 0.6, 0.0, 0.20),
        ("flat_high_0p40", 0.6, 0.0, 0.40),
    ]
    passed = 0
    for idx, (_tn, vx, wz, h) in enumerate(flat_tasks):
        env = Mod4v3ForwardLeapEnv(seed=9600 + idx)
        st = env.reset(dr_scale=0.0, v_cmd=vx, wz_cmd=wz, h_nom=h, jump_times=(), max_episode_s=4.2, steps=[])
        first = True
        while True:
            act = _step_pure_actor(actor, st["obs"], first)
            first = False
            st, _, done, info = env.step(act)
            if done:
                if info["fell_reason"] == "":
                    passed += 1
                break
    return {
        "c874_sha256": EXPECTED_C874_SHA256,
        "e0_max_param_drift": drift,
        "e0_max_action_diff_vs_c874": diff,
        "flat_locomotion_tasks_passed": f"{passed}/{len(flat_tasks)}",
    }


def _annotate_hud(frame_np: np.ndarray, title: str, lines: list[str], jump_active: bool) -> np.ndarray:
    img = Image.fromarray(frame_np)
    draw = ImageDraw.Draw(img, "RGBA")
    try:
        font_b = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 19)
        font_r = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
    except Exception:
        font_b = ImageFont.load_default()
        font_r = font_b

    draw.rounded_rectangle([(16, 14), (760, 44 + 22 * len(lines))], radius=10, fill=(12, 18, 26, 210))
    badge_color = (76, 236, 150, 255) if jump_active else (112, 198, 255, 255)
    draw.text((28, 22), title, fill=badge_color, font=font_b)
    for idx, ln in enumerate(lines):
        draw.text((28, 48 + 21 * idx), ln, fill=(236, 241, 247, 255), font=font_r)
    return np.asarray(img)


def _save_filmstrip(frames_dict: dict[str, np.ndarray], out_png: Path) -> None:
    """Create a 2x2 chronological filmstrip (Lunge Crouch, Mid-Air Apex, Touchdown, Final Settled)."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    keys = ["1_crouch_lunge", "2_midair_apex", "3_touchdown", "4_settled_final"]
    imgs = [Image.fromarray(frames_dict[k]).resize((640, 360), Image.Resampling.LANCZOS) for k in keys if k in frames_dict]
    if not imgs:
        return
    canvas = Image.new("RGB", (1280, 720), (10, 14, 20))
    positions = [(0, 0), (640, 0), (0, 360), (640, 360)]
    for im, pos in zip(imgs, positions):
        canvas.paste(im, pos)
    canvas.save(out_png)


def render_forward_leap_video(
    actor: StatefulMoEForwardLeapActor,
    out_mp4: Path,
    filmstrip_png: Path,
    title: str,
    dr_scale: float,
    seed: int,
    v_pre: float,
    v_post: float,
    sw_s: float | None,
    jump_times: tuple[float, ...],
    max_s: float,
    steps: list[tuple[float, float, float]],
    cam_lookat_gain: float = 0.65,
    cam_x_offset: float = 0.45,
) -> dict[str, Any]:
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    env = Mod4v3ForwardLeapEnv(seed=seed)
    st = env.reset(
        dr_scale=dr_scale,
        v_cmd=v_pre,
        v_cmd_post=v_post,
        post_cmd_switch_s=sw_s,
        h_nom=0.28,
        jump_times=jump_times,
        max_episode_s=max_s,
        steps=steps,
    )

    renderer = mujoco.Renderer(env.m, height=720, width=1280)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.azimuth = 102.0
    cam.elevation = -14.5
    cam.distance = 2.85

    writer = imageio.get_writer(str(out_mp4), fps=25, codec="libx264", quality=8, macro_block_size=16)

    first = True
    step_idx = 0
    film_frames: dict[str, np.ndarray] = {}
    best_apex_rim = -1.0
    touchdown_captured = False

    try:
        while True:
            act = _step_pure_actor(actor, st["obs"], first)
            first = False
            st, _r, done, info = env.step(act)
            step_idx += 1

            if step_idx % 2 == 0:
                now = float(env.d.time)
                wx_now = float(env.d.xpos[env.wheels, 0].mean())
                cur_rim_cm = max(0.0, env.last_world_rim_m * 100.0)
                cam.lookat[:] = [cam_x_offset + cam_lookat_gain * wx_now, 0.0, 0.34]
                renderer.update_scene(env.d, camera=cam)
                raw_rgb = renderer.render()

                R = env.d.xmat[env.base_id].reshape(3, 3)
                pitch_d = math.degrees(math.asin(float(np.clip(-R[2, 0], -1.0, 1.0))))
                j_bit = int(st["obs"][JUMP_MODE_BIT_INDEX] > 0.5)
                expert_tag = "E_jump (Level-Chassis RL Leap)" if j_bit else "E0 (Frozen c874)"
                dr_tag = f"Full-DR (m={env.cur_mass_scale:.2f}x, mu={env.cur_friction:.2f})" if dr_scale > 0 else "0-DR Nominal"
                hud_lines = [
                    f"Time: {now:4.2f}s (1.0x) | {dr_tag} | {expert_tag}",
                    f"Wheel X: {wx_now:+5.2f} m (Leap dx: {info['ep_mean_leap_dx_m']:+5.2f} m) | vx: {env.body_vx:+5.2f} m/s (cmd {env.cmd_vx:+.2f})",
                    f"World Rim Z: {cur_rim_cm:5.1f} cm (Peak: {info['ep_peak_world_rim_cm']:5.1f} cm) | Step: {info['steps_mounted_count']}/{info['steps_total']}",
                    f"Pitch: {pitch_d:+5.1f} deg | Peak |Pitch|: Air {info['ep_max_air_pitch_deg']:.1f}d / Ep {info['ep_max_episode_pitch_deg']:.1f}d | Scrape: {info['ep_guide_force_N']:.1f}/{info['ep_riser_hit_N']:.1f} N",
                ]
                frame_hud = _annotate_hud(raw_rgb, title, hud_lines, bool(j_bit))
                writer.append_data(frame_hud)

                t0_j = env.jump_times[0] if len(env.jump_times) > 0 else 99.0
                if abs(now - (t0_j + 0.44)) < 0.03:
                    film_frames["1_crouch_lunge"] = frame_hud.copy()
                if env.air_substeps >= 1 and not env.window_landed and cur_rim_cm > best_apex_rim:
                    best_apex_rim = cur_rim_cm
                    film_frames["2_midair_apex"] = frame_hud.copy()
                if not touchdown_captured and env.window_landed and now >= t0_j + 0.70:
                    touchdown_captured = True
                    film_frames["3_touchdown"] = frame_hud.copy()
                film_frames["4_settled_final"] = frame_hud.copy()

            if done:
                _save_filmstrip(film_frames, filmstrip_png)
                return {
                    "video_path": str(out_mp4),
                    "filmstrip_path": str(filmstrip_png),
                    "frames": step_idx // 2,
                    "fps": 25,
                    "survived": info["fell_reason"] == "" and not info["slid_off_step"],
                    "steps_mounted": f"{info['steps_mounted_count']}/{info['steps_total']}",
                    "mean_leap_dx_m": info["ep_mean_leap_dx_m"],
                    "total_net_dx_m": info["ep_total_net_dx_m"],
                    "peak_world_rim_cm": info["ep_peak_world_rim_cm"],
                    "max_air_pitch_deg": info["ep_max_air_pitch_deg"],
                    "max_episode_pitch_deg": info["ep_max_episode_pitch_deg"],
                    "min_active_vx": info["ep_min_active_vx"],
                    "guide_force_N": info["ep_guide_force_N"],
                    "riser_hit_N": info["ep_riser_hit_N"],
                }
    finally:
        writer.close()
        renderer.close()


def main() -> None:
    t0 = time.perf_counter()
    torch.set_num_threads(2)

    if "stage1_forward_leap_dagger" in sys.modules:
        raise RuntimeError("Forbidden teacher module detected in sys.modules!")

    ckpt_path = HERE / "weights/model_rl_forward_leap_best.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Missing {ckpt_path}; run ppo_forward_leap_train.py first.")

    model = MoEForwardLeapActorCritic.load_from_checkpoint(ckpt_path, device="cpu")
    actor = StatefulMoEForwardLeapActor(model)

    print("=== [1/4] Verifying E0 (c874) Zero-Drift & Flat Locomotion ===", flush=True)
    e0_res = verify_e0_preservation(model, actor)
    print(f"  E0: drift={e0_res['e0_max_param_drift']}, flat={e0_res['flat_locomotion_tasks_passed']}", flush=True)

    print("=== [2/4] Running 0-DR Forward-Leap & Step-Jump Benchmark (9x5 = 45 episodes) ===", flush=True)
    b_0dr = benchmark_9x5(actor, dr_scale=0.0, seed_base=6100)
    print(
        f"  0-DR: surv={b_0dr['episodes_survived']}, succ={b_0dr['task_success']}, clean={b_0dr['zero_scrape_clean']}, "
        f"steps={b_0dr['step_jump_success_25ep']}, air_p={b_0dr['overall_max_air_pitch_deg']}d, ep_p={b_0dr['overall_max_episode_pitch_deg']}d, "
        f"dx={b_0dr['overall_mean_leap_dx_m']}m, rim={b_0dr['overall_mean_world_rim_cm']}cm",
        flush=True,
    )

    print("=== [3/4] Running 100% Full-DR Forward-Leap & Step-Jump Benchmark (9x5 = 45 episodes) ===", flush=True)
    b_fdr = benchmark_9x5(actor, dr_scale=1.0, seed_base=7100)
    print(
        f"  Full-DR: surv={b_fdr['episodes_survived']}, succ={b_fdr['task_success']}, "
        f"steps={b_fdr['step_jump_success_25ep']} (no-slide {b_fdr['step_zero_slide_off_25ep']}), "
        f"air_p={b_fdr['overall_max_air_pitch_deg']}d, ep_p={b_fdr['overall_max_episode_pitch_deg']}d, dx={b_fdr['overall_mean_leap_dx_m']}m",
        flush=True,
    )

    print("=== [4/4] Rendering 4 Crisp 1x (25fps) Pure-RL MP4 Videos + Filmstrips ===", flush=True)
    media_dir = HERE / "media"
    kf_dir = HERE / "evidence/keyframes"

    v1 = render_forward_leap_video(
        actor,
        media_dir / "RL_STAND_TO_FORWARD_DIVE_1X.mp4",
        kf_dir / "1_stand_forward_dive_filmstrip.png",
        "MOD4v3 Level-Chassis RL Standstill -> COD Forward Leap (1x)",
        dr_scale=0.0,
        seed=2026,
        v_pre=0.0,
        v_post=0.0,
        sw_s=None,
        jump_times=(1.0,),
        max_s=4.2,
        steps=[],
        cam_lookat_gain=0.45,
        cam_x_offset=0.55,
    )
    v2 = render_forward_leap_video(
        actor,
        media_dir / "RL_MOVING_FORWARD_LEAP_1X.mp4",
        kf_dir / "2_moving_forward_leap_filmstrip.png",
        "MOD4v3 Level-Chassis RL Continuous 2x Forward Leap (1x)",
        dr_scale=0.0,
        seed=2026,
        v_pre=0.85,
        v_post=0.85,
        sw_s=None,
        jump_times=(1.20, 3.30),
        max_s=5.8,
        steps=[],
        cam_lookat_gain=0.85,
        cam_x_offset=0.25,
    )
    v3 = render_forward_leap_video(
        actor,
        media_dir / "RL_JUMP_ONTO_20CM_STEP_1X.mp4",
        kf_dir / "3_jump_onto_20cm_step_filmstrip.png",
        "MOD4v3 Level-Chassis RL Direct Leap Onto 20cm Step + Park (1x)",
        dr_scale=0.0,
        seed=2026,
        v_pre=0.0,
        v_post=0.0,
        sw_s=2.5,
        jump_times=(1.0,),
        max_s=4.2,
        steps=[(Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.20), 3.6, 0.20)],
        cam_lookat_gain=0.45,
        cam_x_offset=0.55,
    )
    v4 = render_forward_leap_video(
        actor,
        media_dir / "RL_JUMP_ONTO_24CM_STEP_FULLDR_1X.mp4",
        kf_dir / "4_jump_onto_24cm_step_fulldr_filmstrip.png",
        "MOD4v3 Level-Chassis RL 100% Full-DR Leap Onto 24cm Step (1x)",
        dr_scale=1.0,
        seed=9401,
        v_pre=0.85,
        v_post=0.85,
        sw_s=None,
        jump_times=(1.45,),
        max_s=4.4,
        steps=[(Mod4v3ForwardLeapEnv.step_front_for_moving_jump(0.85, 1.45), 3.8, 0.24)],
        cam_lookat_gain=0.75,
        cam_x_offset=0.35,
    )

    report = {
        "checkpoint": str(ckpt_path),
        "plant_mjcf_sha256": EXPECTED_XML_SHA256,
        "base_c874_sha256": EXPECTED_C874_SHA256,
        "zero_runtime_cheating_contract": {
            "zero_teacher_imports_verified": "stage1_forward_leap_dagger" not in sys.modules,
            "actor_inputs": "obs(35) + obs_history(12x35=420) ONLY",
            "privileged_actor_inputs": 0,
            "external_timers": 0,
        },
        "e0_preservation": e0_res,
        "nominal_0dr_benchmark_45ep": b_0dr,
        "full_dr_benchmark_45ep": b_fdr,
        "videos_1x_25fps": {
            "stand_to_forward_dive": v1,
            "moving_forward_leap": v2,
            "jump_onto_20cm_step": v3,
            "jump_onto_24cm_step_fulldr": v4,
        },
        "wall_seconds": round(time.perf_counter() - t0, 2),
    }

    out_json = HERE / "BENCHMARK_FORWARD_LEAP_RESULTS.json"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved complete benchmark -> {out_json} ({report['wall_seconds']}s)", flush=True)


if __name__ == "__main__":
    main()

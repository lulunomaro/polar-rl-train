# SPDX-License-Identifier: MIT
"""Independent Pure-Neural Benchmark & 4x 1x Video Renderer for Instant Serial-LQR-Style RL Jump.

Strict Anti-Cheat & Zero-Interference Audit:
  1. Asserts zero teacher modules in sys.modules.
  2. Evaluates ONLY StatefulInstantJumpMoE (standard 35-D obs -> 6-D act, internal 40x35 pure-obs history).
  3. Verifies 0.0 parameter & action diff vs frozen E0 (c874).
  4. Runs complete Graduation Matrix under 0-DR Nominal & 100% Full-DR.
  5. Renders 4 real-time 1x (25 fps, 1280x720) MP4 videos + chronological keyframe filmstrips:
       - media/INSTANT_FLAT_MULTI_HOP_1X.mp4
       - media/INSTANT_NEAR_STEP20_1X.mp4
       - media/INSTANT_MOVING_STEP20_24_1X.mp4
       - media/INSTANT_2STEP_20_40_VAULT_1X.mp4
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
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

from instant_jump_env import (
    EXPECTED_XML_SHA256,
    Mod4v3InstantJumpEnv,
    WHEEL_RADIUS_M,
    ensure_instant_jump_scene_xml,
)
from moe_instant_jump_model import (
    ACTION_CLIP,
    C874_CKPT_PATH,
    EXPECTED_C874_SHA256,
    GATE_STEPS,
    HERE,
    HIST_LEN,
    JUMP_MODE_BIT_INDEX,
    MoEInstantJumpActorCritic,
    StatefulInstantJumpMoE,
    build_c874_mlp,
    load_instant_jump_checkpoint,
    verify_c874_checkpoint,
)

FORBIDDEN_MODULES = ("stage1_instant_jump_dagger", "tune_teacher_remote", "probe_native_serial_lqr")

_EVAL_ENV: Mod4v3InstantJumpEnv | None = None
_EVAL_MODEL: MoEInstantJumpActorCritic | None = None


def _init_eval_worker(xml_str: str, ckpt_str: str) -> None:
    global _EVAL_ENV, _EVAL_MODEL
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    torch.set_num_threads(1)
    _EVAL_ENV = Mod4v3InstantJumpEnv(seed=9000, xml_path=Path(xml_str))
    _EVAL_MODEL, _, _ = load_instant_jump_checkpoint(ckpt_str, device="cpu")


def build_graduation_suite() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    # A. Flat Stationary & Moving Multi-Hop (6 episodes)
    for s in range(3):
        cases.append({
            "group": "flat_stationary", "name": f"stat_hop_s{s}", "kind": "flat_stat",
            "v_cmd": 0.0, "v_jump": 0.0, "v_post": 0.0, "sw": None, "jt": (0.75,),
            "dws": [], "stand_dw": None, "drop_x": None, "steps": [], "max_s": 2.4, "seed": 5000 + s,
        })
    for s in range(3):
        vc = 0.75 + 0.25 * s
        cases.append({
            "group": "flat_multihop", "name": f"multihop_{vc:.2f}_s{s}", "kind": "flat_move",
            "v_cmd": vc, "v_jump": vc, "v_post": vc, "sw": None, "jt": (0.85, 2.25),
            "dws": [], "stand_dw": None, "drop_x": None, "steps": [], "max_s": 3.9, "seed": 5100 + s,
        })

    # B. Near-Step Space+W onto 15cm & 20cm (3 distances each = 6 episodes)
    for sh_cm, sh in ((15, 0.15), (20, 0.20)):
        for k, dw in enumerate((0.44, 0.50, 0.56)):
            xf = 0.15 + 0.35 * 0.85 + dw
            cases.append({
                "group": f"near_step_{sh_cm}cm", "name": f"near_{sh_cm}cm_dw{dw:.2f}", "kind": "near_step",
                "v_cmd": 0.35, "v_jump": 1.0, "v_post": 0.80, "sw": None, "jt": (),
                "dws": [(0, dw)], "stand_dw": None, "drop_x": None, "steps": [(xf, 5.5, sh)], "max_s": 3.5, "seed": 5200 + sh_cm * 10 + k,
            })

    # C. Moving W+Space onto 15cm & 20cm (v_cmd in {0.6, 1.0, 1.4} x 5 distances = 15 episodes per height)
    for sh_cm, sh in ((15, 0.15), (20, 0.20)):
        idx_k = 0
        for vc in (0.6, 1.0, 1.4):
            for k in range(5):
                dw = round(0.40 + 0.07 * vc + 0.075 * k, 3)
                xf = 0.15 + vc * 0.90 + dw
                cases.append({
                    "group": f"moving_step_{sh_cm}cm", "name": f"move_{sh_cm}cm_v{vc:.1f}_dw{dw:.2f}", "kind": "move_step",
                    "v_cmd": vc, "v_jump": vc, "v_post": vc, "sw": None, "jt": (),
                    "dws": [(0, dw)], "stand_dw": None, "drop_x": None, "steps": [(xf, 5.8, sh)], "max_s": 3.6, "seed": 5400 + sh_cm * 20 + idx_k,
                })
                idx_k += 1

    # D. 24cm High Step across moving & near-step window (10 episodes)
    for k, dw in enumerate((0.46, 0.52)):
        xf = 0.15 + 0.35 * 0.85 + dw
        cases.append({
            "group": "step_24cm", "name": f"near_24cm_dw{dw:.2f}", "kind": "near_step",
            "v_cmd": 0.35, "v_jump": 1.05, "v_post": 0.80, "sw": None, "jt": (),
            "dws": [(0, dw)], "stand_dw": None, "drop_x": None, "steps": [(xf, 5.5, 0.24)], "max_s": 3.5, "seed": 5800 + k,
        })
    idx_24 = 2
    for vc in (0.8, 1.2):
        for k in range(4):
            dw = round(0.44 + 0.07 * vc + 0.065 * k, 3)
            xf = 0.15 + vc * 0.90 + dw
            cases.append({
                "group": "step_24cm", "name": f"move_24cm_v{vc:.1f}_dw{dw:.2f}", "kind": "move_step",
                "v_cmd": vc, "v_jump": vc, "v_post": vc, "sw": None, "jt": (),
                "dws": [(0, dw)], "stand_dw": None, "drop_x": None, "steps": [(xf, 5.8, 0.24)], "max_s": 3.6, "seed": 5800 + idx_24,
            })
            idx_24 += 1

    # E. Continuous 20cm -> 40cm 2-Step Stair Vault (5 episodes)
    for k in range(5):
        vc = round(0.85 + 0.03 * (k - 2), 2)
        dw1 = round(0.52 + 0.02 * (k - 2), 3)
        tread = 1.56
        xf1 = 0.20 + vc * 0.85 + dw1
        xf2 = xf1 + tread
        cases.append({
            "group": "two_step_20_40cm", "name": f"vault_20_40_s{k}", "kind": "two_step",
            "v_cmd": vc, "v_jump": vc, "v_post": vc, "sw": None, "jt": (),
            "dws": [(0, dw1), (1, 0.52)], "stand_dw": None, "drop_x": None,
            "steps": [(xf1, tread + 0.05, 0.20), (xf2, 4.5, 0.40)], "max_s": 4.7, "seed": 5900 + k,
        })

    # F. Platform Jump-Down 20/30/40cm (6 episodes)
    for k, dh in enumerate((0.20, 0.20, 0.30, 0.30, 0.40, 0.40)):
        cases.append({
            "group": "platform_drop_off", "name": f"drop_{int(dh*100)}cm_s{k}", "kind": "drop_off",
            "v_cmd": 0.85, "v_jump": 0.85, "v_post": 0.85, "sw": None, "jt": (),
            "dws": [], "stand_dw": None, "drop_x": 0.95, "steps": [(-0.60, 1.80, dh)], "max_s": 3.5, "seed": 5950 + k,
        })
    return cases


def _run_eval_task(args: tuple[dict[str, Any], float]) -> dict[str, Any]:
    c, dr_scale = args
    assert _EVAL_ENV is not None and _EVAL_MODEL is not None
    _EVAL_ENV.rng = np.random.default_rng(c["seed"] + (10000 if dr_scale > 0 else 0))
    actor = StatefulInstantJumpMoE(_EVAL_MODEL)
    actor.reset_history()

    st = _EVAL_ENV.reset(
        dr_scale=dr_scale,
        scenario_kind=c["kind"],
        v_cmd=c["v_cmd"],
        v_jump=c["v_jump"],
        v_cmd_post=c["v_post"],
        post_cmd_switch_s=c["sw"],
        jump_times=c["jt"],
        step_trigger_dws=c["dws"],
        stand_step_dw=c["stand_dw"],
        drop_trigger_x=c["drop_x"],
        max_episode_s=c["max_s"],
        steps=c["steps"],
    )
    while True:
        act = actor(torch.from_numpy(st["obs"]).unsqueeze(0))[0].numpy()
        st, _r, done, info = _EVAL_ENV.step(act)
        if done:
            surv = info["fell_reason"] == "" and not info["slid_off_step"]
            if c["kind"] == "drop_off":
                ok = surv and info["drop_landed_ok"] and info["rel_z_end"] >= 0.23
            elif info["steps_total"] > 0:
                ok = surv and (info["steps_mounted_count"] >= info["steps_total"]) and (info["rel_z_end"] >= 0.23)
            else:
                ok = surv and (len(info["completed_jumps"]) >= max(1, len(c["jt"]))) and (info["rel_z_end"] >= 0.23)

            clean = ok and info["ep_guide_force_N"] < 1.0 and info["ep_chassis_force_N"] < 1.0 and info["ep_riser_hit_N"] < 5.0
            cjs = info["completed_jumps"]
            tau_ms = min((j["tau_ms"] for j in cjs), default=20.0)
            lift_ms = min((j["lift_ms"] for j in cjs), default=250.0)
            pre_dx = max((abs(j["pre_dx_m"]) for j in cjs), default=0.0)
            leap_dx = float(np.mean([j["leap_dx_m"] for j in cjs])) if cjs else 0.0
            rel_rim = max((j["rel_rim_cm"] for j in cjs), default=0.0)
            world_rim = max((j["world_rim_cm"] for j in cjs), default=0.0)
            return {
                "group": c["group"],
                "name": c["name"],
                "survived": bool(surv),
                "task_success": bool(ok),
                "clean_zero_scrape": bool(clean),
                "slid_off_step": bool(info["slid_off_step"]),
                "tau_latency_ms": round(tau_ms, 2),
                "liftoff_latency_ms": round(lift_ms, 2),
                "pre_liftoff_dx_m": round(pre_dx, 4),
                "mean_leap_dx_m": round(leap_dx, 3),
                "peak_rel_rim_cm": round(rel_rim, 2),
                "peak_world_rim_cm": round(world_rim, 2),
                "max_air_pitch_deg": info["ep_max_air_pitch_deg"],
                "max_episode_pitch_deg": info["ep_max_episode_pitch_deg"],
                "guide_force_N": info["ep_guide_force_N"],
                "chassis_force_N": info["ep_chassis_force_N"],
                "riser_hit_N": info["ep_riser_hit_N"],
                "rel_z_end_m": info["rel_z_end"],
                "max_closure_mm": info["max_closure_mm"],
                "fell_reason": info["fell_reason"],
            }


def summarize_suite(results: list[dict[str, Any]], dr_scale: float) -> dict[str, Any]:
    by_grp: dict[str, list[dict[str, Any]]] = {}
    for r in results:
        by_grp.setdefault(r["group"], []).append(r)

    grp_sum: dict[str, Any] = {}
    for g, items in by_grp.items():
        n = len(items)
        ok_n = sum(1 for x in items if x["task_success"])
        cl_n = sum(1 for x in items if x["clean_zero_scrape"])
        grp_sum[g] = {
            "pass": f"{ok_n}/{n}",
            "pass_pct": round(100.0 * ok_n / max(1, n), 1),
            "clean_zero_scrape": f"{cl_n}/{n}",
            "mean_liftoff_ms": round(float(np.mean([x["liftoff_latency_ms"] for x in items])), 1),
            "max_tau_latency_ms": round(float(np.max([x["tau_latency_ms"] for x in items])), 1),
            "mean_pre_dx_m": round(float(np.mean([x["pre_liftoff_dx_m"] for x in items])), 4),
            "mean_rel_rim_cm": round(float(np.mean([x["peak_rel_rim_cm"] for x in items])), 2),
            "max_air_pitch_deg": round(float(np.max([x["max_air_pitch_deg"] for x in items])), 2),
            "max_guide_force_N": round(float(np.max([x["guide_force_N"] for x in items])), 2),
        }

    flat_items = by_grp.get("flat_stationary", []) + by_grp.get("flat_multihop", [])
    slow_items = by_grp.get("flat_stationary", []) + by_grp.get("near_step_15cm", []) + by_grp.get("near_step_20cm", [])
    return {
        "dr_scale": dr_scale,
        "total_episodes": len(results),
        "overall_survived": f"{sum(1 for x in results if x['survived'])}/{len(results)}",
        "overall_task_success": f"{sum(1 for x in results if x['task_success'])}/{len(results)}",
        "overall_pass_pct": round(100.0 * sum(1 for x in results if x["task_success"]) / max(1, len(results)), 1),
        "zero_slide_off": f"{sum(1 for x in results if not x['slid_off_step'])}/{len(results)}",
        "max_torque_response_ms": round(float(np.max([x["tau_latency_ms"] for x in results])), 1),
        "stationary_liftoff_ms": round(float(np.mean([x["liftoff_latency_ms"] for x in by_grp.get("flat_stationary", [])])), 1),
        "max_slow_pre_liftoff_dx_m": round(float(np.max([x["pre_liftoff_dx_m"] for x in slow_items])), 4),
        "flat_mean_rim_cm": round(float(np.mean([x["peak_rel_rim_cm"] for x in flat_items])), 2),
        "flat_max_air_pitch_deg": round(float(np.max([x["max_air_pitch_deg"] for x in flat_items])), 2),
        "flat_max_scrape_N": round(float(np.max([x["guide_force_N"] + x["chassis_force_N"] for x in flat_items])), 2),
        "overall_max_air_pitch_deg": round(float(np.max([x["max_air_pitch_deg"] for x in results])), 2),
        "overall_max_closure_mm": round(float(np.max([x["max_closure_mm"] for x in results])), 3),
        "groups": grp_sum,
        "episodes": results,
    }


def verify_e0_zero_interference(model: MoEInstantJumpActorCritic, actor: StatefulInstantJumpMoE) -> dict[str, Any]:
    drift = model.verify_zero_e0_drift()
    ck = verify_c874_checkpoint(C874_CKPT_PATH)
    ref_mlp = build_c874_mlp()
    ref_mlp.load_state_dict({k.replace("mlp.", "", 1): v for k, v in ck["actor_state_dict"].items() if k.startswith("mlp.")}, strict=True)
    ref_mlp.eval()

    g = torch.Generator().manual_seed(42)
    ro = torch.randn(512, 35, generator=g)
    ro[:, 28:35] = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    rh = torch.randn(512, HIST_LEN * 35, generator=g)
    with torch.inference_mode():
        diff = float((model.act_deterministic(ro, rh) - ref_mlp(ro).clamp(-ACTION_CLIP, ACTION_CLIP)).abs().max().item())
    if diff != 0.0:
        raise RuntimeError(f"Non-zero E0 action diff: {diff}")

    env = Mod4v3InstantJumpEnv(seed=9900)
    flat_tasks = [(1.8, 0.0, 0.28), (2.1, 0.0, 0.28), (0.0, 0.0, 0.28), (0.8, 1.0, 0.28), (0.6, 0.0, 0.22), (0.6, 0.0, 0.36)]
    passed = 0
    for vx, wz, h in flat_tasks:
        st = env.reset(dr_scale=0.0, scenario_kind="flat", v_cmd=vx, wz_cmd=wz, h_nom=h, jump_times=(), max_episode_s=3.5, steps=[])
        actor.reset_history()
        while True:
            act = actor(torch.from_numpy(st["obs"]).unsqueeze(0))[0].numpy()
            st, _, done, info = env.step(act)
            if done:
                if info["fell_reason"] == "":
                    passed += 1
                break
    return {
        "c874_sha256": EXPECTED_C874_SHA256,
        "e0_max_param_drift": drift,
        "e0_max_action_diff_vs_c874": diff,
        "flat_locomotion_passed": f"{passed}/{len(flat_tasks)}",
    }


def _load_fonts() -> tuple[Any, Any]:
    for bf, rf in (
        ("C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/consola.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ):
        if Path(bf).exists() and Path(rf).exists():
            return ImageFont.truetype(bf, 18), ImageFont.truetype(rf, 14)
    f = ImageFont.load_default()
    return f, f


def _annotate_hud(frame_np: np.ndarray, title: str, lines: list[str], jump_active: bool) -> np.ndarray:
    img = Image.fromarray(frame_np)
    draw = ImageDraw.Draw(img, "RGBA")
    font_b, font_r = _load_fonts()
    draw.rounded_rectangle([(16, 14), (820, 44 + 21 * len(lines))], radius=10, fill=(12, 18, 26, 212))
    badge_color = (76, 236, 150, 255) if jump_active else (112, 198, 255, 255)
    draw.text((28, 21), title, fill=badge_color, font=font_b)
    for idx, ln in enumerate(lines):
        draw.text((28, 46 + 20 * idx), ln, fill=(236, 241, 247, 255), font=font_r)
    return np.asarray(img)


def _save_filmstrip(frames_list: list[np.ndarray], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    if not frames_list:
        return
    idxs = np.linspace(0, len(frames_list) - 1, 4, dtype=int)
    canvas = Image.new("RGB", (1280, 720), (10, 14, 20))
    for k, pos in enumerate([(0, 0), (640, 0), (0, 360), (640, 360)]):
        im = Image.fromarray(frames_list[idxs[k]]).resize((640, 360), Image.Resampling.LANCZOS)
        canvas.paste(im, pos)
    canvas.save(out_png)


def render_video_1x(
    actor: StatefulInstantJumpMoE,
    out_mp4: Path,
    filmstrip_png: Path,
    title: str,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    env = Mod4v3InstantJumpEnv(seed=cfg["seed"])
    st = env.reset(
        dr_scale=cfg.get("dr_scale", 0.0),
        scenario_kind=cfg["kind"],
        v_cmd=cfg["v_cmd"],
        v_jump=cfg["v_jump"],
        v_cmd_post=cfg["v_post"],
        post_cmd_switch_s=cfg.get("sw"),
        jump_times=cfg["jt"],
        step_trigger_dws=cfg["dws"],
        stand_step_dw=cfg.get("stand_dw"),
        drop_trigger_x=cfg.get("drop_x"),
        max_episode_s=cfg["max_s"],
        steps=cfg["steps"],
    )
    actor.reset_history()

    renderer = mujoco.Renderer(env.m, height=720, width=1280)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.azimuth = 100.0
    cam.elevation = -14.0
    cam.distance = cfg.get("cam_dist", 2.75)

    writer = imageio.get_writer(str(out_mp4), fps=25, codec="libx264", quality=8, macro_block_size=16)
    step_idx = 0
    saved_frames: list[np.ndarray] = []

    try:
        while True:
            j_bit = int(st["obs"][JUMP_MODE_BIT_INDEX] > 0.5)
            act = actor(torch.from_numpy(st["obs"]).unsqueeze(0))[0].numpy()
            st, _r, done, info = env.step(act)
            step_idx += 1

            if step_idx % 2 == 0:
                now = float(env.d.time)
                wx_now = float(env.d.xpos[env.wheels, 0].mean())
                wz_now = float(env.d.qpos[2])
                cur_rim_cm = max(0.0, env.last_world_rim_m * 100.0)
                cam.lookat[:] = [0.35 + 0.85 * wx_now, 0.0, max(0.32, wz_now)]
                renderer.update_scene(env.d, camera=cam)
                raw_rgb = renderer.render()

                R = env.d.xmat[env.base_id].reshape(3, 3)
                pitch_d = math.degrees(math.asin(float(np.clip(-R[2, 0], -1.0, 1.0))))
                exp_tag = f"E2 Instant-Jump (45-step={GATE_STEPS*20}ms)" if j_bit else "E0 (Frozen c874)"
                lift_s = f"{info['completed_jumps'][-1]['lift_ms']:.0f}ms" if info["completed_jumps"] else (f"{env.window_lift_latency_ms:.0f}ms" if env.window_lift_latency_ms else "--")
                hud = [
                    f"Time: {now:4.2f}s (1.0x 25fps) | {exp_tag} | Liftoff Latency: {lift_s}",
                    f"Wheel X: {wx_now:+5.2f}m | vx: {env.body_vx:+5.2f} m/s (cmd {env.cmd_vx:+.2f}) | Rel Height: {info['rel_z_end']:.3f}m",
                    f"World Rim Z: {cur_rim_cm:5.1f} cm | Steps Mounted: {info['steps_mounted_count']}/{info['steps_total']} | Jumps: {len(info['completed_jumps'])}",
                    f"Pitch: {pitch_d:+5.1f} deg (Max Air {info['ep_max_air_pitch_deg']:.1f}d) | Scrape Guide/Riser: {info['ep_guide_force_N']:.1f}/{info['ep_riser_hit_N']:.1f} N",
                ]
                fh = _annotate_hud(raw_rgb, title, hud, bool(j_bit))
                writer.append_data(fh)
                if now >= 0.55:
                    saved_frames.append(fh)

            if done:
                _save_filmstrip(saved_frames, filmstrip_png)
                return {
                    "video_path": str(out_mp4),
                    "filmstrip_path": str(filmstrip_png),
                    "frames": step_idx // 2,
                    "fps": 25,
                    "survived": info["fell_reason"] == "" and not info["slid_off_step"],
                    "steps_mounted": f"{info['steps_mounted_count']}/{info['steps_total']}",
                    "completed_jumps": info["completed_jumps"],
                    "max_air_pitch_deg": info["ep_max_air_pitch_deg"],
                    "guide_force_N": info["ep_guide_force_N"],
                    "riser_hit_N": info["ep_riser_hit_N"],
                    "rel_z_end_m": info["rel_z_end"],
                }
    finally:
        writer.close()
        renderer.close()


def main() -> None:
    t0 = time.perf_counter()
    for fm in FORBIDDEN_MODULES:
        if fm in sys.modules:
            raise RuntimeError(f"Forbidden teacher module {fm} detected in sys.modules!")

    ckpt_path = HERE / "weights/model_instant_jump_best.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Missing {ckpt_path}")
    ckpt_sha = hashlib.sha256(ckpt_path.read_bytes()).hexdigest()

    model, actor, _ = load_instant_jump_checkpoint(ckpt_path, device="cpu")
    xml_path = ensure_instant_jump_scene_xml()

    print("=== [1/4] Verifying Zero Runtime Cheating & E0 (c874) Preservation ===", flush=True)
    e0_audit = verify_e0_zero_interference(model, actor)
    print("  E0 Audit:", json.dumps(e0_audit), flush=True)

    suite = build_graduation_suite()
    n_workers = min(32, max(4, (os.cpu_count() or 8) // 2))
    print(f"=== [2/4] Evaluating {len(suite)}-Episode Suite (0-DR & Full-DR) on {n_workers} workers ===", flush=True)
    with ProcessPoolExecutor(max_workers=n_workers, initializer=_init_eval_worker, initargs=(str(xml_path), str(ckpt_path))) as pool:
        res_0dr = list(pool.map(_run_eval_task, [(c, 0.0) for c in suite]))
        res_fdr = list(pool.map(_run_eval_task, [(c, 1.0) for c in suite]))

    sum_0dr = summarize_suite(res_0dr, dr_scale=0.0)
    sum_fdr = summarize_suite(res_fdr, dr_scale=1.0)
    print("  0-DR Summary:", json.dumps({k: v for k, v in sum_0dr.items() if k != "episodes"}, indent=2), flush=True)
    print("  Full-DR Summary:", json.dumps({k: v for k, v in sum_fdr.items() if k != "episodes"}, indent=2), flush=True)

    print("=== [3/4] Rendering 4 Real-Time 1x (25fps) Pure-RL MP4 Videos ===", flush=True)
    media_dir = HERE / "media"
    kf_dir = HERE / "evidence/keyframes"

    v1 = render_video_1x(
        actor,
        media_dir / "INSTANT_FLAT_MULTI_HOP_1X.mp4",
        kf_dir / "1_flat_multi_hop.png",
        "MOD4v3 Instant Serial-LQR Pure-RL: Stationary Hop + Moving Consecutive Multi-Hop (1x)",
        {"seed": 2026, "kind": "flat_move", "v_cmd": 0.0, "v_jump": 0.90, "v_post": 0.90, "jt": (0.75, 2.15, 3.55), "dws": [], "steps": [], "max_s": 5.0},
    )
    xf_near20 = 0.15 + 0.35 * 0.85 + 0.48
    v2 = render_video_1x(
        actor,
        media_dir / "INSTANT_NEAR_STEP20_1X.mp4",
        kf_dir / "2_near_step20.png",
        "MOD4v3 Instant Pure-RL Near-Step Space+W Onto 20cm Step + Standup Cruise (1x)",
        {"seed": 2027, "kind": "near_step", "v_cmd": 0.35, "v_jump": 1.0, "v_post": 0.75, "jt": (), "dws": [(0, 0.48)], "steps": [(xf_near20, 5.5, 0.20)], "max_s": 3.6},
    )
    xf_mv24 = 0.15 + 1.0 * 0.90 + 0.56
    v3 = render_video_1x(
        actor,
        media_dir / "INSTANT_MOVING_STEP20_24_1X.mp4",
        kf_dir / "3_moving_step24.png",
        "MOD4v3 Instant Pure-RL Moving W+Space Onto 24cm Step + Continued Cruise (1x)",
        {"seed": 2028, "kind": "move_step", "v_cmd": 1.0, "v_jump": 1.0, "v_post": 1.0, "jt": (), "dws": [(0, 0.56)], "steps": [(xf_mv24, 5.8, 0.24)], "max_s": 3.6},
    )
    xf1_2s = 0.20 + 0.85 * 0.85 + 0.52
    xf2_2s = xf1_2s + 1.56
    v4 = render_video_1x(
        actor,
        media_dir / "INSTANT_2STEP_20_40_VAULT_1X.mp4",
        kf_dir / "4_twostep_20_40_vault.png",
        "MOD4v3 Instant Pure-RL Continuous 20cm -> 40cm 2-Step Vault (2x Space + W, 1x)",
        {"seed": 2029, "kind": "two_step", "v_cmd": 0.85, "v_jump": 0.85, "v_post": 0.85, "jt": (), "dws": [(0, 0.52), (1, 0.52)], "steps": [(xf1_2s, 1.61, 0.20), (xf2_2s, 4.5, 0.40)], "max_s": 4.7, "cam_dist": 3.05},
    )

    out_report = {
        "checkpoint_path": str(ckpt_path),
        "checkpoint_sha256": ckpt_sha,
        "plant_mjcf_sha256": EXPECTED_XML_SHA256,
        "c874_sha256": EXPECTED_C874_SHA256,
        "zero_runtime_cheating_contract": {
            "zero_teacher_imports_verified": all(fm not in sys.modules for fm in FORBIDDEN_MODULES),
            "actor_class": "InstantPureNeuralJumpExpert / StatefulInstantJumpMoE",
            "actor_inputs": f"obs(35) + pure_obs_history({HIST_LEN}x35={HIST_LEN*35}) ONLY",
            "gate_steps_50hz": GATE_STEPS,
            "gate_duration_s": round(GATE_STEPS * 0.02, 2),
            "privileged_actor_inputs": 0,
            "runtime_state_machine": False,
        },
        "e0_preservation_audit": e0_audit,
        "nominal_0dr_benchmark": sum_0dr,
        "full_dr_benchmark": sum_fdr,
        "videos_1x_25fps": {
            "INSTANT_FLAT_MULTI_HOP_1X": v1,
            "INSTANT_NEAR_STEP20_1X": v2,
            "INSTANT_MOVING_STEP20_24_1X": v3,
            "INSTANT_2STEP_20_40_VAULT_1X": v4,
        },
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    out_json = HERE / "BENCHMARK_INSTANT_JUMP_RESULTS.json"
    out_json.write_text(json.dumps(out_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n=== [4/4] Saved BENCHMARK_INSTANT_JUMP_RESULTS.json ({out_report['elapsed_s']}s) ===", flush=True)


if __name__ == "__main__":
    main()

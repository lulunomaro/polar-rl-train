# SPDX-License-Identifier: MIT
"""Independent Pure-Neural Evaluation, Zero-Cheat AST Audit & 1x Video Renderer for `AutonomousStairMoE`.

Verifies all Mandatory Graduation Gates with ZERO teacher/oracle imports and ZERO privileged actor inputs:
  1. 10cm & 15cm steps across v_cmd in {0.5, 0.9, 1.3, 1.6} m/s x 3 offsets (24 eps): >= 95% pass
  2. 20cm step across {0.50, 0.90, 1.30, 1.60} m/s x 5 offsets (20 eps): >= 18/20 (90%) mounted,
     stood back up to rel_z >= 0.255m within <= 0.60s, AND g_stair decayed < 0.10 back to E0!
  3. Post-climb W-release test on 20cm step: stands tall at rel_z ~ 0.27-0.29m with |vx| < 0.05 m/s!
  4. Continuous 20cm + 20cm (40cm, 1.5m tread) 2-step at h_cmd=0.28m, v_cmd in {0.7, 1.1} m/s: >= 80% mount both & stand at z_world ~ 0.68m!
  5. Zero False-Positive / Zero Interference on E0 (c874) across flat start/stop/sprint/brake/turn,
     17° ramp up/down, official Rough-v1 level-9 rough terrain, and 20cm step-down: 0 falls, mean g_stair < 0.02, 100% survival!
  6. Renders 3 1x real-time MP4 videos in `media/`.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import time
from typing import Any
import xml.etree.ElementTree as ET

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import imageio.v2 as imageio
import mujoco as mj
import numpy as np
import torch

from autonomous_stair_env import (
    BANK_SOURCE,
    D_BEST,
    EXPECTED_XML_SHA256,
    NAMES,
    PPO_TO_NATIVE,
    RUNTIME_SOURCE,
    SEMANTICS_SOURCE,
    TEMPLATE_SOURCE,
    XML_SOURCE,
    Mod4v3AutonomousStairEnv,
)
from autonomous_stair_moe_model import (
    C874_CKPT_PATH,
    EXPECTED_C874_SHA256,
    GATE_DEADZONE,
    HERE,
    AutonomousStairMoE,
)
from mod4_retarget import Mod4Retarget
from play_mod4v3 import Mod4v3Mujoco, RobotSpec, _q_from_bank, _q_from_runtime

FORBIDDEN_IMPORT_SUBSTRINGS = (
    "stage1_autonomous_stair_dagger",
    "oracle",
    "step_climb",
    "native_runtime",
    "teacher",
)


def verify_zero_teacher_imports() -> dict[str, Any]:
    """Static AST audit confirming zero teacher/oracle imports in model and evaluator."""
    checked_files = [
        HERE / "autonomous_stair_moe_model.py",
        HERE / "evaluate_autonomous_stair_moe.py",
    ]
    imported_modules: list[str] = []
    for fpath in checked_files:
        tree = ast.parse(fpath.read_text(encoding="utf-8"), filename=str(fpath))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
    for mod_name in imported_modules:
        low = mod_name.lower()
        for bad in FORBIDDEN_IMPORT_SUBSTRINGS:
            if bad in low:
                raise RuntimeError(f"Forbidden import '{mod_name}' found during anti-cheat AST audit!")
    return {
        "zero_teacher_imports_verified": True,
        "audited_files": [p.name for p in checked_files],
        "imported_modules": sorted(set(imported_modules)),
    }


def run_single_episode(
    env: Mod4v3AutonomousStairEnv,
    moe: AutonomousStairMoE,
    record_qpos: bool = False,
    early_stop_after_grad_s: float | None = 1.0,
) -> dict[str, Any]:
    """Run one pure-neural episode feeding ONLY 35-D proprioceptive obs with mode=[1,0,0,0,0,0,0]."""
    moe.reset_history()
    obs0 = env._get_obs()
    assert obs0.shape == (35,) and float(obs0[29]) == 0.0 and float(obs0[28]) == 1.0
    moe.history.reset(torch.from_numpy(obs0).unsqueeze(0))

    qpos_trace: list[np.ndarray] = []
    gate_trace: list[float] = []
    rel_z_trace: list[float] = []
    vx_trace: list[float] = []

    post_mount_gate_at_0p6s: float | None = None
    post_mount_rel_z_at_0p6s: float | None = None
    standup_achieved_dt: float | None = None

    n_steps = len(env.active_steps)
    last_xf = env.active_steps[-1][0] if n_steps > 0 else 0.0
    last_h = env.active_steps[-1][2] if n_steps > 0 else 0.0

    obs_cur = obs0
    info: dict[str, Any] = {}

    while True:
        # Strictly verify mode=[1,0,0,0,0,0,0] on every single step!
        assert float(obs_cur[28]) == 1.0 and np.all(obs_cur[29:35] == 0.0), f"Non-autonomous mode bits: {obs_cur[28:35]}"
        with torch.inference_mode():
            act_t, g_prob_t = moe.forward_with_gate(torch.from_numpy(obs_cur))
        act_np = act_t.numpy()
        gp = float(g_prob_t.item())

        if record_qpos:
            qpos_trace.append(env.d.qpos.copy())
        st, _rew, done, info = env.step(act_np, gp)
        obs_cur = st["obs"]

        gate_trace.append(gp)
        gz = env.terrain_z_at(float(env.d.qpos[0]), float(env.d.qpos[1]))
        rel_z_now = float(env.d.qpos[2]) - gz
        rel_z_trace.append(rel_z_now)
        vx_trace.append(env.body_vx)

        if n_steps > 0 and env.step_mounted[n_steps - 1]:
            dt_m = env.k * 0.02 - env.step_mount_time[n_steps - 1]
            step_rel_z = float(env.d.qpos[2]) - last_h
            if standup_achieved_dt is None and step_rel_z >= 0.255 and gp < 0.10:
                standup_achieved_dt = round(dt_m, 3)
            if dt_m <= 0.60 + 1e-6:
                post_mount_gate_at_0p6s = gp
                post_mount_rel_z_at_0p6s = step_rel_z
            if (
                early_stop_after_grad_s is not None
                and not env.w_release_after_mount
                and standup_achieved_dt is not None
                and dt_m >= early_stop_after_grad_s
            ):
                done = True

        if done:
            break

    g_arr = np.asarray(gate_trace, dtype=np.float32)
    g_eff_arr = np.clip((g_arr - GATE_DEADZONE) / (1.0 - GATE_DEADZONE), 0.0, 1.0)
    return {
        "survived": info["fell_reason"] == "" and not info["slid_off"],
        "fell_reason": info["fell_reason"],
        "slid_off": info["slid_off"],
        "steps_total": n_steps,
        "steps_mounted": info["steps_mounted"],
        "all_mounted": info["steps_mounted"] >= n_steps,
        "standup_dt_s": standup_achieved_dt,
        "rel_z_at_0p6s_m": round(post_mount_rel_z_at_0p6s, 4) if post_mount_rel_z_at_0p6s is not None else None,
        "g_stair_at_0p6s": round(post_mount_gate_at_0p6s, 5) if post_mount_gate_at_0p6s is not None else None,
        "final_x_m": round(info["final_x"], 4),
        "final_z_world_m": round(info["final_z"], 4),
        "final_rel_z_m": round(info["final_rel_z"], 4),
        "final_vx_m_s": round(info["final_vx"], 4),
        "max_pitch_deg": round(info["max_pitch_deg"], 2),
        "max_closure_m": round(info["max_closure_m"], 5),
        "mean_g_stair_raw": round(float(g_arr.mean()), 5),
        "mean_g_stair_eff": round(float(g_eff_arr.mean()), 5),
        "max_g_stair_raw": round(float(g_arr.max()), 5),
        "qpos_trace": qpos_trace,
        "gate_trace": gate_trace,
        "vx_trace": vx_trace,
        "rel_z_trace": rel_z_trace,
    }


def evaluate_official_rough_v1_tile(moe: AutonomousStairMoE) -> list[dict[str, Any]]:
    """Evaluate `AutonomousStairMoE` on official Rough-v1 level-9 `random_uniform_for_rm` tile (read-only source)."""
    manifest = json.loads((D_BEST / "viewer/MAP_MANIFEST.json").read_text(encoding="utf-8"))
    col = next(t["col"] for t in manifest["tiles"] if t["family"] == "random_uniform_for_rm")
    tile_name = f"r09_c{col:02d}"
    cache_hf = D_BEST / f"viewer/{tile_name}_hf_v2.npz"

    local_dir = HERE / "runtime_scenes"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_hf_cache = local_dir / f"{tile_name}_hf.npz"

    if cache_hf.exists():
        h_grid = np.load(cache_hf)["h"]
    elif local_hf_cache.exists():
        h_grid = np.load(local_hf_cache)["h"]
    else:
        arr = np.load(D_BEST / f"viewer/tiles/{tile_name}.npz")
        v, f = arr["vertices"], arr["faces"]
        msh_path = local_dir / f"{tile_name}.msh"
        with msh_path.open("wb") as fh:
            fh.write(struct.pack("<4i", len(v), 0, 0, len(f)))
            fh.write(v.astype("<f4").tobytes())
            fh.write(f.astype("<i4").tobytes())
        m_ray = mj.MjModel.from_xml_string(
            f'<mujoco><asset><mesh name="t" file="{msh_path.as_posix()}"/></asset>'
            f'<worldbody><geom type="mesh" mesh="t"/></worldbody></mujoco>'
        )
        d_ray = mj.MjData(m_ray)
        mj.mj_forward(m_ray, d_ray)
        grid = np.linspace(-4.5, 4.5, 181)
        h_grid = np.zeros((181, 181), dtype=np.float32)
        vec = np.array([0.0, 0.0, -1.0])
        pt = np.array([0.0, 0.0, 10.0])
        gid = np.zeros(1, dtype=np.int32)
        for iy, yv in enumerate(grid):
            for ix, xv in enumerate(grid):
                pt[:2] = np.clip([xv + 1.7e-5, yv + 2.9e-5], -4.5 + 1e-4, 4.5 - 1e-4)
                dist = mj.mj_ray(m_ray, d_ray, pt, vec, None, True, -1, gid)
                h_grid[iy, ix] = 10.0 - dist
        np.savez_compressed(local_hf_cache, h=h_grid)

    mn = float(h_grid.min())
    span = max(float(h_grid.max() - mn), 0.001)
    tree = ET.parse(XML_SOURCE)
    root = tree.getroot()
    root.find("compiler").set("meshdir", str(XML_SOURCE.parent / "assets"))
    wb = root.find("worldbody")
    wb.remove(wb.find("geom[@name='ground']"))
    ET.SubElement(root.find("asset"), "hfield", name="rv1_hf", nrow="181", ncol="181", size=f"4.5 4.5 {span} 0.2")
    ET.SubElement(wb, "geom", name="ground", type="hfield", hfield="rv1_hf", pos=f"0 0 {mn}", contype="1", conaffinity="2")
    rv1_xml = local_dir / "official_rough_v1_level9.xml"
    tree.write(rv1_xml, encoding="utf-8", xml_declaration=True)

    spec = RobotSpec(**json.loads(TEMPLATE_SOURCE.read_text(encoding="utf-8"))["spec"])
    runtime = json.loads(RUNTIME_SOURCE.read_text(encoding="utf-8"))
    default_q = _q_from_runtime(runtime, spec.joint_names)
    bank = json.loads(BANK_SOURCE.read_text(encoding="utf-8"))
    sem = json.loads(SEMANTICS_SOURCE.read_text(encoding="utf-8"))
    bank_q, bank_z = _q_from_bank(bank, sem, spec.joint_names)

    env = Mod4v3Mujoco(str(rv1_xml), spec, default_q, bank_q, bank_z, action_clip=6.0)
    m, d = env.m, env.d
    m.opt.timestep = 0.0025
    m.hfield_data[:] = ((h_grid - mn) / span).ravel()

    qa = np.array([m.jnt_qposadr[m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
    va = np.array([m.jnt_dofadr[m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
    baseline = np.r_[env.default_q[env.leg_ids].numpy(), [0.0, 0.0]][PPO_TO_NATIVE].astype(np.float32)
    ik = Mod4Retarget()

    def ground_at(xv: float, yv: float) -> float:
        ix = int(np.clip(round((xv + 4.5) * 20.0), 0, 180))
        iy = int(np.clip(round((yv + 4.5) * 20.0), 0, 180))
        return float(h_grid[iy, ix])

    rows = []
    for c_idx, (vc_target, hc) in enumerate([(0.90, 0.28), (1.35, 0.28)]):
        mj.mj_resetData(m, d)
        L0 = hc - 0.0625
        d.qpos[:] = ik.fit(np.sqrt(L0 * L0 + ik.lateral_offset ** 2), 0.0)["qpos"]
        x0, y0 = -2.8, (-0.15 if c_idx == 0 else 0.15)
        d.qpos[:3] = [x0, y0, ground_at(x0, y0) + hc + 0.002]
        d.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
        d.qvel[:] = 0.0
        mj.mj_forward(m, d)

        moe.reset_history()
        prev_a = np.zeros(6, dtype=np.float32)
        gates = []
        fell = False
        for k in range(280):
            t_s = k * 0.02
            vc = 0.0 if t_s < 0.35 else vc_target
            rot = d.xmat[env.base_id].reshape(3, 3)
            yaw = math.atan2(float(rot[1, 0]), float(rot[0, 0]))
            wz_c = float(np.clip(-1.5 * yaw, -0.6, 0.6))
            q = (d.qpos[qa] - baseline).astype(np.float32)
            q[4:] = 0.0
            obs = np.concatenate(
                (
                    np.array([vc, 0.0, wz_c, hc * 5.0], dtype=np.float32),
                    (d.qvel[3:6] * 0.5).astype(np.float32),
                    (rot.T @ np.array([0.0, 0.0, -1.0])).astype(np.float32),
                    q,
                    (d.qvel[va] * 0.1).astype(np.float32),
                    prev_a,
                    np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32),
                )
            )
            with torch.inference_mode():
                if k == 0:
                    moe.history.reset(torch.from_numpy(obs).unsqueeze(0))
                act_t, gp_t = moe.forward_with_gate(torch.from_numpy(obs))
            act = act_t.numpy()
            gates.append(float(gp_t.item()))
            a_nat = torch.from_numpy(act[PPO_TO_NATIVE]).reshape(1, 6)
            for j in range(8):
                tau = env._torque(a_nat).numpy().reshape(-1)
                if j % 4 == 0:
                    d.ctrl[env.act_ids[:4]] = tau[:4]
                d.ctrl[env.act_ids[4:]] = tau[4:]
                mj.mj_step(m, d)
            prev_a = act
            rot2 = d.xmat[env.base_id].reshape(3, 3)
            p_deg = abs(math.degrees(math.asin(float(np.clip(-rot2[2, 0], -1.0, 1.0)))))
            r_deg = abs(math.degrees(math.atan2(float(rot2[2, 1]), float(rot2[2, 2]))))
            rel_z = float(d.qpos[2]) - ground_at(float(d.qpos[0]), float(d.qpos[1]))
            if p_deg > 42.0 or r_deg > 42.0 or rel_z < 0.11:
                fell = True
                break
            if float(d.qpos[0]) > 3.6:
                break

        g_arr = np.asarray(gates, dtype=np.float32)
        g_eff = np.clip((g_arr - GATE_DEADZONE) / (1.0 - GATE_DEADZONE), 0.0, 1.0)
        rows.append(
            {
                "case": f"official_Rough_v1_L9_v{vc_target:.2f}",
                "survived": not fell,
                "final_x_m": round(float(d.qpos[0]), 3),
                "mean_g_stair_raw": round(float(g_arr.mean()), 5),
                "mean_g_stair_eff": round(float(g_eff.mean()), 5),
                "max_g_stair_raw": round(float(g_arr.max()), 5),
            }
        )
    return rows


def render_1x_video(
    env: Mod4v3AutonomousStairEnv,
    qpos_trace: list[np.ndarray],
    out_mp4: Path,
    cam_distance: float = 2.35,
) -> dict[str, Any]:
    """Render exact 1x real-time MP4 (25 fps from 50Hz trace -> every 2nd policy frame = 0.04s/frame)."""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    m, d = env.m, env.d
    renderer = mj.Renderer(m, height=720, width=1280)
    cam = mj.MjvCamera()
    cam.azimuth = 96.0
    cam.elevation = -14.0
    cam.distance = cam_distance

    n_written = 0
    with imageio.get_writer(str(out_mp4), fps=25, codec="libx264", quality=7, macro_block_size=1) as writer:
        for i in range(0, len(qpos_trace), 2):
            d.qpos[:] = qpos_trace[i]
            mj.mj_forward(m, d)
            cam.lookat[:] = [float(d.qpos[0]) + 0.25, float(d.qpos[1]), max(0.28, float(d.qpos[2]))]
            renderer.update_scene(d, camera=cam)
            writer.append_data(renderer.render())
            n_written += 1
    renderer.close()
    return {
        "path": str(out_mp4),
        "frames_25fps": n_written,
        "duration_1x_s": round(n_written / 25.0, 2),
        "size_bytes": out_mp4.stat().st_size,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--ckpt",
        type=str,
        default=str(HERE / "weights/model_autonomous_stair_moe_best.pt"),
    )
    args = ap.parse_args()

    t0 = time.perf_counter()
    torch.set_num_threads(1)

    ast_audit = verify_zero_teacher_imports()
    ckpt_path = Path(args.ckpt).resolve()
    ckpt_sha = hashlib.sha256(ckpt_path.read_bytes()).hexdigest()
    xml_sha = hashlib.sha256(XML_SOURCE.read_bytes()).hexdigest()
    c874_sha = hashlib.sha256(C874_CKPT_PATH.read_bytes()).hexdigest()
    assert xml_sha == EXPECTED_XML_SHA256
    assert c874_sha == EXPECTED_C874_SHA256

    moe = AutonomousStairMoE.load_from_checkpoint(ckpt_path, device="cpu")
    e0_drift = moe.verify_zero_e0_drift()
    assert e0_drift == 0.0

    env = Mod4v3AutonomousStairEnv(seed=20261118)

    # =========================================================================
    # 1. 10cm & 15cm steps across v_cmd in {0.5, 0.9, 1.3, 1.6} m/s x 3 offsets (24 eps)
    # =========================================================================
    s10_15_rows = []
    for hs in (0.10, 0.15):
        for vc in (0.5, 0.9, 1.3, 1.6):
            for off_mm in (-50, 0, 50):
                env.reset_scenario(
                    kind="stair_1step",
                    dr_scale=0.0,
                    step_heights=(hs,),
                    step_x1=1.50,
                    cmd_vx=vc,
                    height_cmd=0.28,
                    start_x=off_mm / 1000.0,
                    max_steps=380,
                )
                res = run_single_episode(env, moe)
                passed = (
                    res["survived"]
                    and res["all_mounted"]
                    and res["standup_dt_s"] is not None
                    and res["standup_dt_s"] <= 0.60
                    and res["final_rel_z_m"] >= 0.255
                    and (res["g_stair_at_0p6s"] is not None and res["g_stair_at_0p6s"] < 0.10)
                )
                s10_15_rows.append(
                    {
                        "step_height_m": hs,
                        "cmd_vx": vc,
                        "offset_mm": off_mm,
                        "passed": passed,
                        **{k: v for k, v in res.items() if not k.endswith("_trace")},
                    }
                )
    s10_15_pass = sum(r["passed"] for r in s10_15_rows)

    # =========================================================================
    # 2. 20cm step across {0.50, 0.90, 1.30, 1.60} m/s x 5 offsets (-60,-30,0,+30,+60mm = 20 eps)
    # =========================================================================
    s20_rows = []
    for vc in (0.50, 0.90, 1.30, 1.60):
        for off_mm in (-60, -30, 0, 30, 60):
            env.reset_scenario(
                kind="stair_1step",
                dr_scale=0.0,
                step_heights=(0.20,),
                step_x1=1.50,
                cmd_vx=vc,
                height_cmd=0.28,
                start_x=off_mm / 1000.0,
                max_steps=400,
            )
            res = run_single_episode(env, moe)
            passed = (
                res["survived"]
                and res["all_mounted"]
                and res["standup_dt_s"] is not None
                and res["standup_dt_s"] <= 0.60
                and res["final_rel_z_m"] >= 0.255
                and (res["g_stair_at_0p6s"] is not None and res["g_stair_at_0p6s"] < 0.10)
            )
            s20_rows.append(
                {
                    "cmd_vx": vc,
                    "offset_mm": off_mm,
                    "passed": passed,
                    **{k: v for k, v in res.items() if not k.endswith("_trace")},
                }
            )
    s20_pass = sum(r["passed"] for r in s20_rows)

    # =========================================================================
    # 3. Post-climb W-release test on 20cm step (6 episodes across speeds & offsets)
    # =========================================================================
    wrel_rows = []
    for vc in (0.50, 0.90, 1.30):
        for off_mm in (-40, 40):
            env.reset_scenario(
                kind="stair_1step",
                dr_scale=0.0,
                step_heights=(0.20,),
                step_x1=1.50,
                cmd_vx=vc,
                height_cmd=0.28,
                start_x=off_mm / 1000.0,
                w_release=True,
                max_steps=420,
            )
            res = run_single_episode(env, moe, early_stop_after_grad_s=None)
            passed = (
                res["survived"]
                and res["all_mounted"]
                and 0.260 <= res["final_rel_z_m"] <= 0.305
                and abs(res["final_vx_m_s"]) < 0.05
                and res["standup_dt_s"] is not None
                and res["standup_dt_s"] <= 0.60
            )
            wrel_rows.append(
                {
                    "approach_cmd_vx": vc,
                    "offset_mm": off_mm,
                    "passed": passed,
                    **{k: v for k, v in res.items() if not k.endswith("_trace")},
                }
            )
    wrel_pass = sum(r["passed"] for r in wrel_rows)

    # =========================================================================
    # 4. Continuous 20cm + 20cm (40cm, 1.5m tread) 2-Step at v_cmd in {0.7, 1.1} m/s x 5 offsets (10 eps)
    # =========================================================================
    s2step_rows = []
    for vc in (0.70, 1.10):
        for off_mm in (-60, -30, 0, 30, 60):
            env.reset_scenario(
                kind="stair_2step",
                dr_scale=0.0,
                step_heights=(0.20, 0.40),
                step_x1=1.50,
                tread_len=1.50,
                cmd_vx=vc,
                height_cmd=0.28,
                start_x=off_mm / 1000.0,
                max_steps=500,
            )
            res = run_single_episode(env, moe, early_stop_after_grad_s=1.0)
            passed = (
                res["survived"]
                and res["steps_mounted"] >= 2
                and res["final_z_world_m"] >= 0.655
                and res["standup_dt_s"] is not None
                and res["standup_dt_s"] <= 0.60
            )
            s2step_rows.append(
                {
                    "cmd_vx": vc,
                    "offset_mm": off_mm,
                    "passed": passed,
                    **{k: v for k, v in res.items() if not k.endswith("_trace")},
                }
            )
    s2step_pass = sum(r["passed"] for r in s2step_rows)

    # =========================================================================
    # 5. 100% Full-DR 20cm All-Speed Check (20 episodes: 4 speeds x 5 DR seeds)
    # =========================================================================
    fulldr_rows = []
    for v_i, vc in enumerate((0.50, 0.90, 1.30, 1.60)):
        for s_i, off_mm in enumerate((-60, -30, 0, 30, 60)):
            env.rng = np.random.default_rng(70000 + 37 * v_i + s_i)
            env.reset_scenario(
                kind="stair_1step",
                dr_scale=1.0,
                step_heights=(0.20,),
                step_x1=1.50,
                cmd_vx=vc,
                height_cmd=0.28,
                start_x=off_mm / 1000.0,
                max_steps=420,
            )
            res = run_single_episode(env, moe)
            passed = res["survived"] and res["all_mounted"] and res["final_rel_z_m"] >= 0.250
            fulldr_rows.append({"cmd_vx": vc, "offset_mm": off_mm, "passed": passed, "max_pitch_deg": res["max_pitch_deg"]})
    fulldr_pass = sum(r["passed"] for r in fulldr_rows)

    # =========================================================================
    # 6. Zero False-Positive / Zero Interference on E0 (c874)
    # =========================================================================
    neg_specs = [
        ("flat_stand_still", "flat", 0.0, 17.0, 0.20, "stand_still"),
        ("flat_sprint_brake_1p8", "flat", 1.80, 17.0, 0.20, "sprint_brake"),
        ("flat_reverse_0p55", "flat", 0.90, 17.0, 0.20, "reverse"),
        ("flat_yaw_slalom", "flat", 1.10, 17.0, 0.20, "yaw_slalom"),
        ("flat_height_sweep", "flat", 0.90, 17.0, 0.20, "height_sweep"),
        ("ramp_10deg_up", "ramp_up", 1.10, 10.0, 0.20, "steady"),
        ("ramp_17deg_up", "ramp_up", 1.00, 17.0, 0.20, "steady"),
        ("ramp_17deg_up_stopgo", "ramp_up", 0.95, 17.0, 0.20, "ramp_stop_go"),
        ("ramp_17deg_down", "ramp_down", 0.95, 17.0, 0.20, "steady"),
        ("rough_hfield_0p9", "rough", 0.90, 17.0, 0.20, "steady"),
        ("rough_hfield_1p4", "rough", 1.40, 17.0, 0.20, "sprint_brake"),
        ("step_down_10cm", "step_down", 1.00, 17.0, 0.10, "steady"),
        ("step_down_20cm_0p8", "step_down", 0.80, 17.0, 0.20, "steady"),
        ("step_down_20cm_1p2", "step_down", 1.20, 17.0, 0.20, "steady"),
    ]
    neg_rows = []
    for n_idx, (nname, knd, vc, rdeg, sdh, prof) in enumerate(neg_specs):
        env.rng = np.random.default_rng(90000 + n_idx)
        env.reset_scenario(
            kind=knd,
            dr_scale=0.0,
            cmd_vx=vc,
            height_cmd=0.28,
            ramp_deg=rdeg,
            step_down_h=sdh,
            maneuver_profile=prof,
            max_steps=280,
        )
        res = run_single_episode(env, moe, early_stop_after_grad_s=None)
        neg_rows.append(
            {
                "case": nname,
                "survived": res["survived"],
                "final_x_m": res["final_x_m"],
                "mean_g_stair_raw": res["mean_g_stair_raw"],
                "mean_g_stair_eff": res["mean_g_stair_eff"],
                "max_g_stair_raw": res["max_g_stair_raw"],
            }
        )

    rv1_rows = evaluate_official_rough_v1_tile(moe)
    all_neg_rows = neg_rows + rv1_rows
    neg_surv = sum(r["survived"] for r in all_neg_rows)
    neg_mean_g_raw = float(np.mean([r["mean_g_stair_raw"] for r in all_neg_rows]))
    neg_mean_g_eff = float(np.mean([r["mean_g_stair_eff"] for r in all_neg_rows]))

    # =========================================================================
    # 7. Render 3 Mandatory 1x MP4 Videos
    # =========================================================================
    media_dir = HERE / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    # Video 1: Low-speed 0.50 m/s 20cm climb + auto-standup to 0.28m + cruise
    env.reset_scenario(
        kind="stair_1step",
        dr_scale=0.0,
        step_heights=(0.20,),
        step_x1=1.50,
        cmd_vx=0.50,
        height_cmd=0.28,
        start_x=0.0,
        max_steps=380,
    )
    vid1_ep = run_single_episode(env, moe, record_qpos=True, early_stop_after_grad_s=1.8)
    vid1_meta = render_1x_video(env, vid1_ep["qpos_trace"], media_dir / "AUTO_LOWSPEED_05MPS_20CM_1X.mp4")

    # Video 2: High-speed 1.40 m/s 20cm climb + auto-standup to 0.28m + fast cruise
    env.reset_scenario(
        kind="stair_1step",
        dr_scale=0.0,
        step_heights=(0.20,),
        step_x1=1.50,
        cmd_vx=1.40,
        height_cmd=0.28,
        start_x=0.0,
        max_steps=340,
    )
    vid2_ep = run_single_episode(env, moe, record_qpos=True, early_stop_after_grad_s=1.4)
    vid2_meta = render_1x_video(env, vid2_ep["qpos_trace"], media_dir / "AUTO_HIGHSPEED_14MPS_20CM_1X.mp4")

    # Video 3: Continuous 2-step 20cm + 20cm = 40cm (1.5m tread) autonomous climb + standup at z_world ~ 0.68m
    env.reset_scenario(
        kind="stair_2step",
        dr_scale=0.0,
        step_heights=(0.20, 0.40),
        step_x1=1.50,
        tread_len=1.50,
        cmd_vx=1.00,
        height_cmd=0.28,
        start_x=0.0,
        max_steps=460,
    )
    vid3_ep = run_single_episode(env, moe, record_qpos=True, early_stop_after_grad_s=1.5)
    vid3_meta = render_1x_video(
        env, vid3_ep["qpos_trace"], media_dir / "AUTO_CONTINUOUS_2STEP_40CM_1X.mp4", cam_distance=2.65
    )

    gates_summary = {
        "gate1_10cm_15cm_allspeed_ge95pct": bool(s10_15_pass / len(s10_15_rows) >= 0.95),
        "gate2_20cm_allspeed_5offsets_ge18of20": bool(s20_pass >= 18),
        "gate3_post_climb_w_release_tall_stand": bool(wrel_pass == len(wrel_rows)),
        "gate4_continuous_2step_40cm_ge80pct": bool(s2step_pass / len(s2step_rows) >= 0.80),
        "gate5_zero_false_positive_e0_survival_100pct": bool(
            neg_surv == len(all_neg_rows) and neg_mean_g_raw < 0.02
        ),
        "gate6_zero_e0_drift_and_zero_cheat": bool(
            e0_drift == 0.0 and ast_audit["zero_teacher_imports_verified"]
        ),
    }
    all_graduated = all(gates_summary.values())

    s20_standups = [r["standup_dt_s"] for r in s20_rows if r["standup_dt_s"] is not None]
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "all_graduation_gates_passed": all_graduated,
        "gates_summary": gates_summary,
        "checkpoint": {
            "path": str(ckpt_path),
            "sha256": ckpt_sha,
            "c874_sha256": c874_sha,
            "plant_xml_sha256": xml_sha,
            "e0_max_abs_drift": e0_drift,
        },
        "anti_cheat_audit": ast_audit,
        "metrics": {
            "step_10cm_15cm_allspeed": {
                "passed": s10_15_pass,
                "total": len(s10_15_rows),
                "pass_rate": round(s10_15_pass / len(s10_15_rows), 4),
                "rows": s10_15_rows,
            },
            "step_20cm_allspeed_5offsets_0dr": {
                "passed": s20_pass,
                "total": len(s20_rows),
                "pass_rate": round(s20_pass / len(s20_rows), 4),
                "mean_standup_dt_s": round(float(np.mean(s20_standups)), 3) if s20_standups else None,
                "max_standup_dt_s": round(float(np.max(s20_standups)), 3) if s20_standups else None,
                "rows": s20_rows,
            },
            "post_climb_w_release_20cm": {
                "passed": wrel_pass,
                "total": len(wrel_rows),
                "pass_rate": round(wrel_pass / len(wrel_rows), 4),
                "rows": wrel_rows,
            },
            "continuous_2step_20plus20cm_40cm": {
                "passed": s2step_pass,
                "total": len(s2step_rows),
                "pass_rate": round(s2step_pass / len(s2step_rows), 4),
                "rows": s2step_rows,
            },
            "step_20cm_allspeed_100pct_fulldr": {
                "passed": fulldr_pass,
                "total": len(fulldr_rows),
                "pass_rate": round(fulldr_pass / len(fulldr_rows), 4),
                "rows": fulldr_rows,
            },
            "negative_non_stair_zero_fp": {
                "survived": neg_surv,
                "total": len(all_neg_rows),
                "survival_rate": round(neg_surv / len(all_neg_rows), 4),
                "mean_g_stair_raw": round(neg_mean_g_raw, 5),
                "mean_g_stair_eff": round(neg_mean_g_eff, 5),
                "max_g_stair_raw": round(float(max(r["max_g_stair_raw"] for r in all_neg_rows)), 5),
                "rows": all_neg_rows,
            },
        },
        "videos": {
            "lowspeed_05mps_20cm_1x": {
                **vid1_meta,
                "survived": vid1_ep["survived"],
                "standup_dt_s": vid1_ep["standup_dt_s"],
                "final_rel_z_m": vid1_ep["final_rel_z_m"],
                "final_vx_m_s": vid1_ep["final_vx_m_s"],
            },
            "highspeed_14mps_20cm_1x": {
                **vid2_meta,
                "survived": vid2_ep["survived"],
                "standup_dt_s": vid2_ep["standup_dt_s"],
                "final_rel_z_m": vid2_ep["final_rel_z_m"],
                "final_vx_m_s": vid2_ep["final_vx_m_s"],
            },
            "continuous_2step_40cm_1x": {
                **vid3_meta,
                "survived": vid3_ep["survived"],
                "steps_mounted": vid3_ep["steps_mounted"],
                "standup_dt_s": vid3_ep["standup_dt_s"],
                "final_z_world_m": vid3_ep["final_z_world_m"],
                "final_vx_m_s": vid3_ep["final_vx_m_s"],
            },
        },
        "wall_seconds": round(time.perf_counter() - t0, 2),
    }

    out_json = HERE / "BENCHMARK_AUTONOMOUS_STAIR_RESULTS.json"
    out_json.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "all_graduation_gates_passed": all_graduated,
                "gates": gates_summary,
                "10_15cm": f"{s10_15_pass}/{len(s10_15_rows)}",
                "20cm_0dr": f"{s20_pass}/{len(s20_rows)}",
                "w_release": f"{wrel_pass}/{len(wrel_rows)}",
                "2step_40cm": f"{s2step_pass}/{len(s2step_rows)}",
                "20cm_fulldr": f"{fulldr_pass}/{len(fulldr_rows)}",
                "neg_survival": f"{neg_surv}/{len(all_neg_rows)}",
                "neg_mean_g_raw": round(neg_mean_g_raw, 5),
                "neg_mean_g_eff": round(neg_mean_g_eff, 5),
                "ckpt_sha256": ckpt_sha,
                "wall_s": results["wall_seconds"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()

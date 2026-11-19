# SPDX-License-Identifier: MIT
"""Unified 3-Expert Pure-Neural MoE (`bed1da66`) All-Maps Interactive WASD Playground.

Integrates into a single hardware-polled WASD + HUD Console:
  - E0 (`c874`):     Full-DR Flat / Rough / Slope / Descent / Tunnel / Fall-Recovery Cruise
  - E1 (`a1acd1a8`): 5/5 Graduated Pure-RL 200mm Stair Climb + Dead-Stop Top Park (`C` to toggle, `V` to park)
  - E2 (`79e27807`): Level-Chassis (<=8.7° air pitch) COD Forward Leap & 16-24cm Step-Jump (`Space` or `J`)

Across all 6 map suites:
  1. All-Skills 3-Expert Proving Ground (5 tactical lanes)
  2. Official RoboMaster RMUC2027 Full 3D Arena (MJB-cached, 7 tactical spawns)
  3. Open-Source Sirina / rc_mjlab Parkour Arena (7 obstacle zones)
  4. Open-Source Serial_Leg_Simulation Courses (17° ramp + gravel hfield, 5..20cm steps)
  5. Stair & High-Platform Difficulty Matrix (5cm..24cm + 20+20cm continuous 2-step)
  6. SCUT Rough-v1 120m Matrix (11 terrain families x Levels 0..9 + 750-tile map overview)
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
import traceback
from typing import Any
import xml.etree.ElementTree as ET

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import mujoco as mj
import mujoco.viewer
import numpy as np
import torch

from map_builders import (
    D_BEST,
    HERE,
    PLANT_DIR,
    REPO,
    ROUGH_CN,
    ROUGH_VIEWER_DIR,
    SUITE_NAMES,
    build_parkour_sirina,
    build_proving_ground,
    build_rmuc2027,
    build_rough_v1_tile,
    build_serial_leg_course,
    build_stairs_matrix,
)

RECIPES_DIR = REPO / "sources/local/MOD4V3_POST_TRAINING_RECIPES_20261118"
STAIR_RL_DIR = REPO / "sources/local/MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118"
FORWARD_LEAP_DIR = REPO / "sources/local/MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118"
E_TEACH = REPO / "sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1"

UNIFIED_CKPT = RECIPES_DIR / "weights/model_unified_3expert_moe.pt"
EXPECTED_UNIFIED_SHA256 = "bed1da66c033293bad2db2c140b71dbee433049f7c9486fd9126df3d2caf5655"

for _p in [str(D_BEST / "runtime/core"), str(E_TEACH), str(E_TEACH / "sim"), str(E_TEACH.parent)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mod4_retarget import Mod4Retarget  # noqa: E402
from play_mod4v3 import Mod4v3Mujoco, RobotSpec, _q_from_bank, _q_from_runtime  # noqa: E402

PPO_TO_NATIVE = np.array([0, 2, 1, 3, 4, 5], dtype=np.int64)
NAMES = [
    "left_front1_joint",
    "right_front1_joint",
    "left_rear1_joint",
    "right_rear1_joint",
    "left_wheel_joint",
    "right_wheel_joint",
]

CONTROL_DT = 0.02
JUMP_DURATION_STEPS = 95  # 1.90s at 50Hz (exact JUMP_GATE_DURATION_S)
HEIGHT_MIN = 0.20
HEIGHT_MAX = 0.42
STAIR_HIGH_H = 0.4091
STAIR_CLIMB_VX = 0.47

SERIAL_SUB_SCENES = [
    "17° 陡坡 + 碎石高度场跑图",
    "7 cm 单台阶 (Serial_Leg)",
    "10 cm 单台阶 (Serial_Leg)",
    "15 cm 单台阶 (Serial_Leg)",
    "20 cm 单台阶 (Serial_Leg)",
]

STAIRS_SUB_SCENES = [
    "20 cm 标准毕业单阶 (E1攀爬 / Space直跳)",
    "24 cm 极限高台 (按 Space 原地直跳登顶)",
    "16 cm 高台 (E2直跳 / E1攀爬)",
    "15 cm 单级台阶",
    "10 cm 单级台阶",
    "5 cm 浅台阶",
    "20cm + 20cm (40cm) 连续双级台阶",
]

VK_MAP = {
    "w": 0x57,
    "a": 0x41,
    "s": 0x53,
    "d": 0x44,
    "q": 0x51,
    "e": 0x45,
    "c": 0x43,
    "v": 0x56,
    "j": 0x4A,
    "f": 0x46,
    "r": 0x52,
    "p": 0x50,
    "x": 0x58,
    "space": 0x20,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "[": 0xDB,
    "]": 0xDD,
}


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _quat_from_euler_xyz(roll: float, pitch: float, yaw: float) -> np.ndarray:
    q = np.zeros(4, dtype=np.float64)
    mj.mju_euler2Quat(q, np.array([roll, pitch, yaw], dtype=np.float64), "xyz")
    return q


def load_unified_moe_model() -> tuple[Any, str]:
    sha = hashlib.sha256(UNIFIED_CKPT.read_bytes()).hexdigest()
    if sha != EXPECTED_UNIFIED_SHA256:
        raise RuntimeError(f"Unified MoE checkpoint SHA mismatch: {sha} != {EXPECTED_UNIFIED_SHA256}")
    umod = _load_mod("unified_moe", RECIPES_DIR / "scripts/unified_all_skills_moe.py")
    stair_rc = _load_mod("stair_rc", STAIR_RL_DIR / "support/mod4v3_ppo_v1/route2_common.py")
    jump_mod = _load_mod("jump_mod", FORWARD_LEAP_DIR / "moe_forward_leap_model.py")
    unified = umod.UnifiedThreeExpertMoE(stair_rc, jump_mod)
    ck = torch.load(UNIFIED_CKPT, map_location="cpu", weights_only=False)
    unified.load_state_dict(ck["state_dict"], strict=True)
    unified.eval()
    return unified, sha


class UnifiedMoESimulation:
    """400Hz MuJoCo + 50Hz Unified 3-Expert MoE closed-loop multi-map simulator."""

    def __init__(self, unified_model: Any, ckpt_sha: str, show_viewer: bool = True):
        torch.set_num_threads(1)
        self.unified = unified_model
        self.ckpt_sha = ckpt_sha
        self.show_viewer = show_viewer

        self.spec = RobotSpec(**json.loads((D_BEST / "runtime/core/template_spec.json").read_text(encoding="utf-8"))["spec"])
        runtime = json.loads((PLANT_DIR / "runtime_config.json").read_text(encoding="utf-8"))
        self.default_q = _q_from_runtime(runtime, self.spec.joint_names)
        bank = json.loads((D_BEST / "plant/reset_bank.json").read_text(encoding="utf-8"))
        sem = json.loads((PLANT_DIR / "semantics.json").read_text(encoding="utf-8"))
        self.bank_q, self.bank_z = _q_from_bank(bank, sem, self.spec.joint_names)
        self.ik = Mod4Retarget()

        self.viewer = None
        self.env: Mod4v3Mujoco | None = None
        self.m: mj.MjModel | None = None
        self.d: mj.MjData | None = None
        self.scene_meta: dict[str, Any] = {}
        self.spawn_idx = 0

        # Command & expert states
        self.paused = False
        self.max_vx = 1.00
        self.max_wz = 1.20
        self.target_h = 0.28
        self.cmd_vx = 0.0
        self.cmd_wz = 0.0

        self.stair_mode = False
        self.stair_standup_rem = 0
        self.stair_settle_rem = 0
        self.stair_park = False
        self.auto_stair_park = True
        self.stair_entry_ground_z = 0.0
        self.stair_top_hold_steps = 0

        self.jump_rem = 0
        self.jump_count = 0
        self.jump_launch_gz = 0.0
        self.peak_rim_clearance_cm = 0.0
        self.max_air_pitch_deg = 0.0
        self.last_gate_prob = 0.0
        self.closure_mm = 0.0
        self.steps = 0
        self.resets = 0
        self.auto_recover_reset = True

        self._ray_grp = np.array([1, 1, 0, 0, 0, 1], dtype=np.uint8)
        self._ray_gid = np.zeros(1, dtype=np.int32)
        self.prev_a = np.zeros(6, dtype=np.float32)

    def load_map(self, meta: dict[str, Any], spawn_idx: int = 0) -> None:
        if self.viewer is not None:
            try:
                self.viewer.close()
            except Exception:
                pass
            self.viewer = None

        self.scene_meta = meta
        self.spawn_idx = int(np.clip(spawn_idx, 0, len(meta["spawns"]) - 1))
        if not self.stair_mode:
            self.target_h = 0.28

        xml_path = meta["xml_path"]
        mjb_path = meta.get("mjb_path")
        if mjb_path and Path(mjb_path).exists():
            orig_loader = mj.MjModel.from_xml_path
            try:
                mj.MjModel.from_xml_path = staticmethod(lambda _p: mj.MjModel.from_binary_path(str(mjb_path)))
                self.env = Mod4v3Mujoco(xml_path, self.spec, self.default_q, self.bank_q, self.bank_z, action_clip=6.0)
            finally:
                mj.MjModel.from_xml_path = orig_loader
        else:
            self.env = Mod4v3Mujoco(xml_path, self.spec, self.default_q, self.bank_q, self.bank_z, action_clip=6.0)

        self.m, self.d = self.env.m, self.env.d
        self.m.opt.timestep = 0.0025
        self.env.dt = 0.0025
        self.env.decim = 8

        hf = meta.get("hfield_array")
        if hf is not None:
            mn = float(hf.min())
            span = max(float(hf.max() - mn), 0.001)
            self.m.hfield_data[:] = ((hf - mn) / span).ravel()

        self.m.vis.headlight.ambient[:] = [0.55, 0.55, 0.58]
        self.m.vis.headlight.diffuse[:] = [0.80, 0.80, 0.82]
        self.m.vis.headlight.specular[:] = [0.10, 0.10, 0.12]

        self.qa = np.array([self.m.jnt_qposadr[self.m.joint(n).id] for n in NAMES], dtype=np.int64)[PPO_TO_NATIVE]
        self.va = np.array([self.m.jnt_dofadr[self.m.joint(n).id] for n in NAMES], dtype=np.int64)[PPO_TO_NATIVE]
        self.baseline = np.r_[self.env.default_q[self.env.leg_ids].numpy(), [0.0, 0.0]][PPO_TO_NATIVE].astype(np.float32)
        self.tire_gids = np.array([self.m.geom("left_tire").id, self.m.geom("right_tire").id], dtype=np.int64)
        self.pairs = [
            (int(self.m.site(el.get("site1")).id), int(self.m.site(el.get("site2")).id))
            for el in ET.parse(xml_path).getroot().findall("equality/connect")
        ]

        self.reset_at_spawn(self.spawn_idx)

        if self.show_viewer:
            self.viewer = mj.viewer.launch_passive(self.m, self.d, show_left_ui=False, show_right_ui=False)
            with self.viewer.lock():
                if meta.get("hide_group5"):
                    self.viewer.opt.geomgroup[5] = 0
                sp = meta["spawns"][self.spawn_idx]
                yaw_r = math.radians(float(sp["yaw_deg"]))
                self.viewer.cam.type = mj.mjtCamera.mjCAMERA_FREE
                self.viewer.cam.lookat[:] = [
                    float(self.d.qpos[0]) + 0.35 * math.cos(yaw_r),
                    float(self.d.qpos[1]) + 0.35 * math.sin(yaw_r),
                    float(self.d.qpos[2]) + 0.04,
                ]
                self.viewer.cam.distance = 2.75
                self.viewer.cam.azimuth = float(sp["yaw_deg"]) + 135.0
                self.viewer.cam.elevation = -18.0

    def ground_z(self, x: float, y: float, z_top: float | None = None) -> float:
        if z_top is None:
            z_top = float(self.d.qpos[2]) + 0.35 if self.d is not None else 4.0
        dist = mj.mj_ray(
            self.m,
            self.d,
            np.array([x, y, z_top], dtype=np.float64),
            np.array([0.0, 0.0, -1.0], dtype=np.float64),
            self._ray_grp,
            1,
            -1,
            self._ray_gid,
        )
        if dist < 0:
            return 0.0
        return float(z_top - dist)

    def reset_at_spawn(self, spawn_idx: int | None = None) -> dict[str, Any]:
        if spawn_idx is not None:
            self.spawn_idx = int(np.clip(spawn_idx, 0, len(self.scene_meta["spawns"]) - 1))
        sp = self.scene_meta["spawns"][self.spawn_idx]
        x0, y0 = float(sp["x"]), float(sp["y"])
        yaw_rad = math.radians(float(sp["yaw_deg"]))

        mj.mj_resetData(self.m, self.d)
        mj.mj_forward(self.m, self.d)
        gz = self.ground_z(x0, y0, float(sp.get("z_ray", 4.0)))

        h_init = STAIR_HIGH_H if self.stair_mode else float(np.clip(self.target_h, 0.24, 0.36))
        init_len = max(0.14, min(0.35, h_init - 0.0625))
        fit_q = self.ik.fit(np.sqrt(init_len ** 2 + self.ik.lateral_offset ** 2), 0.0)["qpos"]

        self.d.qpos[:] = fit_q
        self.d.qpos[:3] = [x0, y0, gz + h_init + 0.002]
        self.d.qpos[3:7] = _quat_from_euler_xyz(0.0, 0.0, yaw_rad)
        self.d.qvel[:] = 0.0
        mj.mj_forward(self.m, self.d)

        self.unified.reset_history()
        self.prev_a[:] = 0.0
        self.cmd_vx = 0.0
        self.cmd_wz = 0.0
        self.jump_rem = 0
        self.stair_park = False
        self.stair_standup_rem = 0
        self.stair_settle_rem = 15 if self.stair_mode else 0
        self.stair_entry_ground_z = gz
        self.stair_top_hold_steps = 0
        self.last_gate_prob = 0.0
        self.resets += 1
        return sp

    def trigger_forward_leap(self) -> bool:
        if self.jump_rem > 75:
            return False
        self.stair_mode = False
        self.stair_park = False
        self.stair_standup_rem = 0
        self.jump_launch_gz = self.ground_z(float(self.d.qpos[0]), float(self.d.qpos[1]))
        self.jump_rem = JUMP_DURATION_STEPS
        self.jump_count += 1
        self.max_air_pitch_deg = 0.0
        self.peak_rim_clearance_cm = 0.0
        return True

    def toggle_stair_mode(self, force: bool | None = None) -> bool:
        new_val = (not self.stair_mode) if force is None else bool(force)
        self.stair_mode = new_val
        self.stair_park = False
        self.stair_top_hold_steps = 0
        self.jump_rem = 0
        if self.stair_mode:
            gz = self.ground_z(float(self.d.qpos[0]), float(self.d.qpos[1]))
            self.stair_entry_ground_z = gz
            rel_z = float(self.d.qpos[2]) - gz
            if rel_z < 0.37:
                # Smoothly stand up in E0 first (~0.44s), then reset history & enter E1 cleanly!
                self.stair_standup_rem = 22
                self.stair_settle_rem = 12
            else:
                self.stair_standup_rem = 0
                self.stair_settle_rem = 10
                self.unified.reset_history()
            self.target_h = STAIR_HIGH_H
        else:
            self.stair_standup_rem = 0
            self.stair_settle_rem = 0
            self.target_h = 0.28
        return self.stair_mode

    def toggle_stair_park(self) -> bool:
        if not self.stair_mode:
            self.stair_mode = True
            self.unified.reset_history()
        self.stair_park = not self.stair_park
        if self.stair_park:
            self.target_h = 0.20
            self.cmd_vx = 0.0
        else:
            self.target_h = STAIR_HIGH_H
        return self.stair_park

    def trigger_random_fall(self) -> None:
        x_now, y_now = float(self.d.qpos[0]), float(self.d.qpos[1])
        gz = self.ground_z(x_now, y_now)
        self.stair_mode = False
        self.stair_park = False
        self.jump_rem = 0
        roll = random.uniform(-0.42, 0.42)
        pitch = random.uniform(-0.35, 0.35)
        yaw = random.uniform(-math.pi, math.pi)
        self.d.qpos[2] = gz + 0.56
        self.d.qpos[3:7] = _quat_from_euler_xyz(roll, pitch, yaw)
        self.d.qvel[0] = random.uniform(-1.2, 1.2)
        self.d.qvel[1] = random.uniform(-0.5, 0.5)
        self.d.qvel[2] = random.uniform(-0.2, 0.15)
        self.d.qvel[3:6] = [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.9, 0.9)]
        mj.mj_forward(self.m, self.d)
        self.unified.reset_history()
        self.prev_a[:] = 0.0

    def step(self, pressed: set[str]) -> None:
        if self.paused:
            return

        w_on = "w" in pressed and "s" not in pressed
        s_on = "s" in pressed and "w" not in pressed
        a_on = "a" in pressed and "d" not in pressed
        d_on = "d" in pressed and "a" not in pressed

        if "e" in pressed and "q" not in pressed and not self.stair_mode:
            self.target_h = float(np.clip(self.target_h + 0.12 * CONTROL_DT, HEIGHT_MIN, HEIGHT_MAX))
        elif "q" in pressed and "e" not in pressed and not self.stair_mode:
            self.target_h = float(np.clip(self.target_h - 0.12 * CONTROL_DT, HEIGHT_MIN, HEIGHT_MAX))

        wz_goal = (self.max_wz if a_on else 0.0) + (-self.max_wz if d_on else 0.0)
        vx_goal = (self.max_vx if w_on else 0.0) + (-min(0.85, self.max_vx) if s_on else 0.0)

        slew = min(1.0, CONTROL_DT / 0.16)
        self.cmd_vx += (vx_goal - self.cmd_vx) * slew
        self.cmd_wz += (wz_goal - self.cmd_wz) * slew

        # Determine active expert routing & command conditioning
        if self.jump_rem > 0:
            self.jump_rem -= 1
            mode = [1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
            h_cmd = 0.28
            v_c = max(0.0, vx_goal if w_on else self.cmd_vx)
            w_c = self.cmd_wz * 0.5
        elif self.stair_mode:
            if self.stair_standup_rem > 0:
                self.stair_standup_rem -= 1
                alpha_up = 1.0 - (self.stair_standup_rem / 22.0)
                h_cmd = 0.28 + alpha_up * (STAIR_HIGH_H - 0.28)
                v_c = 0.0
                w_c = self.cmd_wz
                mode = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                if self.stair_standup_rem == 0:
                    self.unified.reset_history()
            else:
                mode = [0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
                if self.stair_settle_rem > 0:
                    self.stair_settle_rem -= 1
                    v_c = 0.0
                    h_cmd = STAIR_HIGH_H
                elif self.stair_park:
                    v_c = 0.0
                    h_cmd = 0.20
                else:
                    h_cmd = STAIR_HIGH_H
                    if w_on:
                        v_c = STAIR_CLIMB_VX
                    elif s_on:
                        v_c = -0.25
                    else:
                        v_c = 0.0
                w_c = self.cmd_wz
        else:
            mode = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            h_cmd = self.target_h
            v_c = self.cmd_vx
            w_c = self.cmd_wz

        rot = self.d.xmat[self.env.base_id].reshape(3, 3).astype(np.float32)
        q = self.d.qpos[self.qa].astype(np.float32) - self.baseline
        q[4:] = 0.0
        qd = self.d.qvel[self.va].astype(np.float32) * 0.1
        ang_vel_b = self.d.qvel[3:6].astype(np.float32) * 0.5
        grav_b = rot.T @ np.array([0.0, 0.0, -1.0], dtype=np.float32)

        obs = np.concatenate(
            (
                np.array([v_c, 0.0, w_c, h_cmd * 5.0], dtype=np.float32),
                ang_vel_b,
                grav_b,
                q,
                qd,
                self.prev_a,
                np.array(mode, dtype=np.float32),
            ),
            axis=0,
        )

        obs_t = torch.from_numpy(obs).reshape(1, 35)
        hist_t = self.unified.history.append(obs_t)
        if mode[1] > 0.5:
            with torch.inference_mode():
                self.last_gate_prob = float(self.unified.e1_stair.gate_prob(hist_t).item())
        else:
            self.last_gate_prob = 0.0

        act = self.unified.forward_with_history(obs_t, hist_t)[0].numpy()
        a_t = torch.from_numpy(act[PPO_TO_NATIVE]).reshape(1, 6)

        for j in range(8):
            if j % 4 == 0:
                tau = self.env._torque(a_t).numpy().reshape(-1)
                self.d.ctrl[self.env.act_ids[:4]] = tau[:4]
                self.d.ctrl[self.env.act_ids[4:]] = tau[4:]
            else:
                tau = self.env._torque(a_t).numpy().reshape(-1)
                self.d.ctrl[self.env.act_ids[4:]] = tau[4:]
            mj.mj_step(self.m, self.d)

        self.prev_a = act
        self.steps += 1

        # Telemetry & auto-park on step top
        wheels_xyz = self.d.geom_xpos[self.tire_gids]
        gz_now = self.ground_z(float(self.d.qpos[0]), float(self.d.qpos[1]))
        R64 = self.d.xmat[self.env.base_id].reshape(3, 3)
        pitch_deg = math.degrees(math.asin(float(np.clip(-R64[2, 0], -1.0, 1.0))))
        if self.jump_rem > 0:
            rim_above_launch_cm = (float(np.min(wheels_xyz[:, 2])) - 0.0625 - self.jump_launch_gz) * 100.0
            self.peak_rim_clearance_cm = max(self.peak_rim_clearance_cm, rim_above_launch_cm)
            if rim_above_launch_cm > 3.0:
                self.max_air_pitch_deg = max(self.max_air_pitch_deg, abs(pitch_deg))

        if self.stair_mode and self.auto_stair_park and not self.stair_park and self.stair_standup_rem == 0:
            wheel_min_z = float(np.min(wheels_xyz[:, 2])) - 0.0625
            if wheel_min_z - self.stair_entry_ground_z > 0.145 and float(np.linalg.norm(self.d.qvel[:2])) <= 0.65:
                self.stair_top_hold_steps += 1
                if self.stair_top_hold_steps >= 18:
                    self.stair_park = True
                    self.target_h = 0.20
            else:
                self.stair_top_hold_steps = 0

        self.closure_mm = max(float(np.linalg.norm(self.d.site_xpos[u] - self.d.site_xpos[w])) for u, w in self.pairs) * 1000.0

        # Auto-reset only on extreme NaN or deep abyss fall
        rel_z = float(self.d.qpos[2]) - gz_now
        cos_tilt = float(R64[2, 2])
        if not np.isfinite(self.d.qpos).all() or float(self.d.qpos[2]) < -1.5:
            self.reset_at_spawn(self.spawn_idx)
        elif self.auto_recover_reset and self.jump_rem == 0 and rel_z < 0.135 and cos_tilt < 0.45:
            self.reset_at_spawn(self.spawn_idx)

    def telemetry(self) -> dict[str, Any]:
        R = self.d.xmat[self.env.base_id].reshape(3, 3)
        pitch_deg = math.degrees(math.asin(float(np.clip(-R[2, 0], -1.0, 1.0))))
        roll_deg = math.degrees(math.atan2(float(R[2, 1]), float(R[2, 2])))
        yaw_deg = math.degrees(math.atan2(float(R[1, 0]), float(R[0, 0])))
        fwd = R[:2, 0]
        fwd = fwd / max(float(np.linalg.norm(fwd)), 1e-6)
        vx_body = float(self.d.qvel[:2] @ fwd)
        x, y, z = [float(v) for v in self.d.qpos[:3]]
        gz = self.ground_z(x, y)

        if self.jump_rem > 0:
            expert_label = f"E2 · COD 平机身跳扑 ({self.jump_rem * 0.02:.2f}s)"
        elif self.stair_mode:
            if self.stair_standup_rem > 0:
                expert_label = "E0->E1 · 平顺抬高预备上阶"
            elif self.stair_park:
                expert_label = "E1 · top_head 台顶锁死驻车"
            else:
                expert_label = f"E1 · 200mm 攀爬专家 (门控 {self.last_gate_prob:.2f})"
        else:
            expert_label = "E0 · c874 全地形巡航基座"

        return {
            "expert": expert_label,
            "time_s": round(float(self.d.time), 2),
            "xyz": [round(x, 3), round(y, 3), round(z, 3)],
            "ground_z": round(gz, 3),
            "rel_z": round(z - gz, 3),
            "vx": round(vx_body, 3),
            "cmd_vx": round(self.cmd_vx, 3),
            "cmd_wz": round(self.cmd_wz, 3),
            "target_h": round(0.20 if self.stair_park else (STAIR_HIGH_H if self.stair_mode else self.target_h), 3),
            "pitch_deg": round(pitch_deg, 2),
            "roll_deg": round(roll_deg, 2),
            "yaw_deg": round(yaw_deg, 1),
            "peak_rim_cm": round(self.peak_rim_clearance_cm, 1),
            "max_air_pitch_deg": round(self.max_air_pitch_deg, 2),
            "closure_mm": round(self.closure_mm, 3),
            "jumps": self.jump_count,
            "resets": self.resets,
            "paused": self.paused,
            "stair_mode": self.stair_mode,
            "stair_park": self.stair_park,
        }

    def close(self) -> None:
        if self.viewer is not None:
            try:
                self.viewer.close()
            except Exception:
                pass
            self.viewer = None


class AllMapsPlayerApp:
    BG = "#0d1117"
    PANEL = "#161b22"
    CARD = "#1f2630"
    TEXT = "#e6edf3"
    MUTED = "#8b949e"
    CYAN = "#39d5ff"
    GREEN = "#4be38a"
    YELLOW = "#ffd166"
    ORANGE = "#ff9f43"
    PINK = "#ff6b81"

    def __init__(self, root: tk.Tk, sim: UnifiedMoESimulation):
        self.root = root
        self.sim = sim
        self.closed = False
        self.prev_vk_down: set[str] = set()
        self.mouse_held_keys: set[str] = set()
        self.last_ui_time = 0.0
        self.last_status_dump = 0.0
        self.deadline = time.perf_counter()
        self.event_msg = "已就绪：点击本控制台即可用 WASD / Space / C 畅玩！"

        # Win32 APIs: hardware async key state + disable IME popup on control console
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.GetForegroundWindow.restype = wintypes.HWND
        self.user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        self.user32.GetAncestor.restype = wintypes.HWND
        self.user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
        self.user32.GetAsyncKeyState.restype = ctypes.c_short

        self._build_ui()
        self.root.update_idletasks()
        self.control_hwnd = int(self.root.winfo_id())
        self.top_hwnd = int(self.user32.GetAncestor(self.control_hwnd, 2) or self.control_hwnd)
        try:
            imm32 = ctypes.WinDLL("imm32", use_last_error=True)
            imm32.ImmAssociateContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
            imm32.ImmAssociateContext(self.top_hwnd, 0)
            imm32.ImmAssociateContext(self.control_hwnd, 0)
        except Exception:
            pass

        self.apply_suite_selection(initial=True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(1, self.tick)
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(600, lambda: (self.root.attributes("-topmost", False), self.focus_console()))

    def _build_ui(self) -> None:
        r = self.root
        r.title("MOD4v3 三专家统一 MoE (bed1da66) · 全地形/RMUC2027/跑酷/台阶 WASD 控制台")
        r.geometry("560x930+18+25")
        r.minsize(530, 860)
        r.configure(bg=self.BG)

        o = tk.Frame(r, bg=self.BG, padx=14, pady=10)
        o.pack(fill="both", expand=True)

        tk.Label(
            o,
            text="MOD4v3  ·  3-EXPERT UNIFIED MoE",
            bg=self.BG,
            fg=self.CYAN,
            font=("Microsoft YaHei UI", 15, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            o,
            text=f"纯神经网络零干扰合成 SHA: {self.sim.ckpt_sha[:8]}  |  E0 巡航 + E1 200mm上阶(5/5) + E2 平机身跳扑(<=8.7°)",
            bg=self.BG,
            fg=self.MUTED,
            font=("Microsoft YaHei UI", 8),
            anchor="w",
        ).pack(fill="x", pady=(2, 8))

        # --- Map Suite & Sub-options Card ---
        mcard = tk.Frame(o, bg=self.PANEL, padx=10, pady=8)
        mcard.pack(fill="x", pady=(0, 8))

        tk.Label(mcard, text="1. 选择地图套件", bg=self.PANEL, fg=self.YELLOW, font=("Microsoft YaHei UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.suite_var = tk.StringVar(value=SUITE_NAMES[0])
        suite_cb = ttk.Combobox(mcard, textvariable=self.suite_var, values=SUITE_NAMES, state="readonly", font=("Microsoft YaHei UI", 9))
        suite_cb.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)
        suite_cb.bind("<<ComboboxSelected>>", lambda _e: self.on_suite_changed())

        self.sub_label = tk.Label(mcard, text="子场景 / 地形类", bg=self.PANEL, fg=self.TEXT, font=("Microsoft YaHei UI", 9))
        self.sub_label.grid(row=1, column=0, sticky="w", pady=2)
        self.sub_var = tk.StringVar(value="（综合全车道）")
        self.sub_cb = ttk.Combobox(mcard, textvariable=self.sub_var, values=["（综合全车道）"], state="disabled", font=("Microsoft YaHei UI", 9))
        self.sub_cb.grid(row=1, column=1, sticky="ew", padx=(8, 4), pady=2)
        self.sub_cb.bind("<<ComboboxSelected>>", lambda _e: self.apply_suite_selection())

        self.level_var = tk.StringVar(value="L3")
        self.level_cb = ttk.Combobox(mcard, textvariable=self.level_var, values=[f"L{i}" for i in range(10)], state="disabled", width=5, font=("Microsoft YaHei UI", 9))
        self.level_cb.grid(row=1, column=2, sticky="ew", pady=2)
        self.level_cb.bind("<<ComboboxSelected>>", lambda _e: self.apply_suite_selection())

        tk.Label(mcard, text="出生点 / 赛道切换", bg=self.PANEL, fg=self.TEXT, font=("Microsoft YaHei UI", 9)).grid(row=2, column=0, sticky="w", pady=2)
        self.spawn_var = tk.StringVar(value="")
        self.spawn_cb = ttk.Combobox(mcard, textvariable=self.spawn_var, values=[], state="readonly", font=("Microsoft YaHei UI", 9))
        self.spawn_cb.grid(row=2, column=1, sticky="ew", padx=(8, 4), pady=2)
        self.spawn_cb.bind("<<ComboboxSelected>>", lambda _e: self.on_spawn_selected())

        self._btn(mcard, "载入", self.apply_suite_selection, self.CYAN, pad=(8, 3)).grid(row=2, column=2, sticky="ew", pady=2)
        mcard.columnconfigure(1, weight=1)

        self.hint_var = tk.StringVar(value="")
        tk.Label(o, textvariable=self.hint_var, bg=self.CARD, fg=self.GREEN, font=("Microsoft YaHei UI", 9), anchor="w", padx=8, pady=5, wraplength=520, justify="left").pack(fill="x", pady=(0, 8))

        # --- Live Telemetry HUD ---
        tbox = tk.Frame(o, bg=self.PANEL, padx=12, pady=7)
        tbox.pack(fill="x", pady=(0, 8))
        self.tvars: dict[str, tk.StringVar] = {}
        rows = [
            ("当前激活专家", "expert", self.GREEN),
            ("位置 (X, Y) / 地面高", "pos", self.TEXT),
            ("离地净高 / 目标站高", "height", self.YELLOW),
            ("前进实速 / 指令速度", "speed", self.CYAN),
            ("机身俯仰 / 横滚 / 航向", "angles", self.TEXT),
            ("跳扑峰值净空 / 空中最大俯仰", "jump_stats", self.ORANGE),
            ("四连杆闭合误差 / 跳扑次数", "closure", self.MUTED),
        ]
        for idx, (label_txt, key, color) in enumerate(rows):
            tk.Label(tbox, text=label_txt, bg=self.PANEL, fg=self.MUTED, font=("Microsoft YaHei UI", 9), anchor="w").grid(row=idx, column=0, sticky="w", pady=1)
            sv = tk.StringVar(value="—")
            self.tvars[key] = sv
            tk.Label(tbox, textvariable=sv, bg=self.PANEL, fg=color, font=("Consolas", 10, "bold"), anchor="e").grid(row=idx, column=1, sticky="e", pady=1)
        tbox.columnconfigure(1, weight=1)

        # --- Expert Skill Trigger Buttons ---
        srow = tk.Frame(o, bg=self.BG)
        srow.pack(fill="x", pady=(0, 6))
        self._btn(srow, "Space / J · COD 平机身跳扑 (E2)", self.action_jump, self.GREEN).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=2)
        self.stair_btn = self._btn(srow, "C · 开启 200mm 上阶专家 (E1)", self.action_toggle_stair, self.CYAN)
        self.stair_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=2)
        self._btn(srow, "V · E1 台顶锁死驻车", self.action_park, self.YELLOW).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=2)
        self._btn(srow, "F · 随机抛落抗摔测试", self.action_fall, self.ORANGE).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=2)
        srow.columnconfigure((0, 1), weight=1)

        # --- Height & Speed Sliders ---
        sframe = tk.Frame(o, bg=self.BG)
        sframe.pack(fill="x", pady=(0, 4))
        self.h_slider_var = tk.DoubleVar(value=0.28)
        self.v_slider_var = tk.DoubleVar(value=1.00)
        h_col = tk.Frame(sframe, bg=self.BG)
        h_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(h_col, text="站高 Q↓ / E↑ (m)", bg=self.BG, fg=self.TEXT, font=("Microsoft YaHei UI", 9, "bold")).pack(anchor="w")
        h_scale = tk.Scale(h_col, from_=0.20, to=0.42, resolution=0.005, orient="horizontal", variable=self.h_slider_var, bg=self.BG, fg=self.YELLOW, troughcolor="#30363d", highlightthickness=0, takefocus=False)
        h_scale.pack(fill="x")
        for seq in ("<ButtonRelease-1>", "<B1-Motion>"):
            h_scale.bind(seq, lambda _e: self.on_height_slider())

        v_col = tk.Frame(sframe, bg=self.BG)
        v_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        tk.Label(v_col, text="W/S 速度上限 (m/s)", bg=self.BG, fg=self.TEXT, font=("Microsoft YaHei UI", 9, "bold")).pack(anchor="w")
        v_scale = tk.Scale(v_col, from_=0.30, to=2.20, resolution=0.10, orient="horizontal", variable=self.v_slider_var, command=lambda val: setattr(self.sim, "max_vx", float(val)), bg=self.BG, fg=self.CYAN, troughcolor="#30363d", highlightthickness=0, takefocus=False)
        v_scale.pack(fill="x")

        # --- Presets + Mouse D-Pad ---
        prow = tk.Frame(o, bg=self.BG)
        prow.pack(fill="x", pady=(2, 6))
        for txt, hval in [("1 低姿钻洞 0.20m", 0.20), ("2 标准巡航 0.28m", 0.28), ("3 上阶高姿 0.41m", STAIR_HIGH_H)]:
            self._btn(prow, txt, lambda hv=hval: self.set_height_preset(hv), self.MUTED, pad=(4, 4)).pack(side="left", fill="x", expand=True, padx=2)

        dpad = tk.Frame(o, bg=self.BG)
        dpad.pack(fill="x", pady=(0, 6))
        pad_left = tk.Frame(dpad, bg=self.BG)
        pad_left.pack(side="left", expand=True)
        for txt, k, r_i, c_i in [("W 前进", "w", 0, 1), ("A 左转", "a", 1, 0), ("S 后退", "s", 1, 1), ("D 右转", "d", 1, 2)]:
            b = tk.Button(pad_left, text=txt, width=9, bg=self.PANEL, fg=self.TEXT, activebackground="#30363d", activeforeground=self.CYAN, relief="flat", font=("Microsoft YaHei UI", 9, "bold"), pady=4, takefocus=False)
            b.grid(row=r_i, column=c_i, padx=2, pady=2)
            b.bind("<ButtonPress-1>", lambda _e, key=k: (self.mouse_held_keys.add(key), self.focus_console()))
            b.bind("<ButtonRelease-1>", lambda _e, key=k: self.mouse_held_keys.discard(key))
            b.bind("<Leave>", lambda _e, key=k: self.mouse_held_keys.discard(key))

        pad_right = tk.Frame(dpad, bg=self.BG)
        pad_right.pack(side="right", fill="y", padx=(8, 0))
        self._btn(pad_right, "R · 重置起点", self.action_reset, self.CYAN, pad=(10, 4)).pack(fill="x", pady=2)
        self._btn(pad_right, "P · 暂停/继续", self.action_pause, self.YELLOW, pad=(10, 4)).pack(fill="x", pady=2)

        # --- Checkboxes & Extra Tools ---
        crow = tk.Frame(o, bg=self.BG)
        crow.pack(fill="x", pady=(0, 4))
        self.follow_cam_var = tk.BooleanVar(value=True)
        self.chase_cam_var = tk.BooleanVar(value=False)
        self.auto_park_var = tk.BooleanVar(value=True)
        tk.Checkbutton(crow, text="镜头平移跟随", variable=self.follow_cam_var, bg=self.BG, fg=self.MUTED, selectcolor=self.PANEL, activebackground=self.BG, takefocus=False).pack(side="left")
        tk.Checkbutton(crow, text="车尾追尾旋转视角", variable=self.chase_cam_var, bg=self.BG, fg=self.MUTED, selectcolor=self.PANEL, activebackground=self.BG, takefocus=False).pack(side="left", padx=6)
        tk.Checkbutton(crow, text="E1登顶自动驻车", variable=self.auto_park_var, command=lambda: setattr(self.sim, "auto_stair_park", bool(self.auto_park_var.get())), bg=self.BG, fg=self.MUTED, selectcolor=self.PANEL, activebackground=self.BG, takefocus=False).pack(side="left")
        self._btn(crow, "750块全地形图", self.open_rough_overview, self.MUTED, pad=(6, 2)).pack(side="right")

        help_txt = (
            "操作热键（本控制台内置硬件按键直读，无惧中文输入法！点击本窗口即可键盘操控）：\n"
            "• W/S 前后 | A/D 转向 | Q/E 升降站高 | 1/2/3 站高预设 | 4/5/6 速度档 | [ / ] 切换出生点\n"
            "• Space 或 J：触发 E2 平机身 COD 前向跳扑 / 直跳高台  |  C：切换 E1 上台阶专家  |  V：台顶驻车  |  R：重置"
        )
        tk.Label(o, text=help_txt, bg=self.PANEL, fg=self.TEXT, font=("Microsoft YaHei UI", 8), justify="left", anchor="w", padx=9, pady=6).pack(fill="x")

        self.status_var = tk.StringVar(value=self.event_msg)
        tk.Label(o, textvariable=self.status_var, bg=self.BG, fg=self.CYAN, font=("Microsoft YaHei UI", 9), anchor="w", pady=4).pack(fill="x")

    def _btn(self, parent, text, cmd, fg_color, pad=(8, 6)) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=lambda: (cmd(), self.focus_console()),
            bg=self.PANEL,
            fg=fg_color,
            activebackground="#30363d",
            activeforeground=fg_color,
            relief="flat",
            font=("Microsoft YaHei UI", 9, "bold"),
            padx=pad[0],
            pady=pad[1],
            takefocus=False,
        )

    def focus_console(self) -> None:
        try:
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass

    def is_console_foreground(self) -> bool:
        try:
            fg = int(self.user32.GetForegroundWindow())
            top = int(self.user32.GetAncestor(self.control_hwnd, 2) or self.control_hwnd)
            return fg != 0 and fg == top
        except Exception:
            return False

    def on_suite_changed(self) -> None:
        suite = self.suite_var.get()
        if suite.startswith("4 ·"):
            self.sub_cb.configure(state="readonly", values=SERIAL_SUB_SCENES)
            self.sub_var.set(SERIAL_SUB_SCENES[0])
            self.level_cb.configure(state="disabled")
        elif suite.startswith("5 ·"):
            self.sub_cb.configure(state="readonly", values=STAIRS_SUB_SCENES)
            self.sub_var.set(STAIRS_SUB_SCENES[0])
            self.level_cb.configure(state="disabled")
        elif suite.startswith("6 ·"):
            self.sub_cb.configure(state="readonly", values=ROUGH_CN)
            self.sub_var.set(ROUGH_CN[0])
            self.level_cb.configure(state="readonly")
            self.level_var.set("L4")
        else:
            self.sub_cb.configure(state="disabled", values=["（综合全场景）"])
            self.sub_var.set("（综合全场景）")
            self.level_cb.configure(state="disabled")
        self.apply_suite_selection()

    def apply_suite_selection(self, initial: bool = False) -> None:
        suite = self.suite_var.get()
        self.status_var.set(f"正在构建并载入地图：{suite} …")
        self.root.update_idletasks()

        if suite.startswith("1 ·"):
            meta = build_proving_ground()
        elif suite.startswith("2 ·"):
            meta = build_rmuc2027()
        elif suite.startswith("3 ·"):
            meta = build_parkour_sirina()
        elif suite.startswith("4 ·"):
            meta = build_serial_leg_course(self.sub_var.get())
        elif suite.startswith("5 ·"):
            meta = build_stairs_matrix(self.sub_var.get())
        else:
            lvl = int(self.level_var.get().lstrip("L") or "3")
            meta = build_rough_v1_tile(self.sub_var.get(), lvl)

        self.sim.stair_mode = False
        self.sim.stair_park = False
        self.sim.load_map(meta, spawn_idx=0)
        spawn_names = [f"{i + 1}. {s['name']}" for i, s in enumerate(meta["spawns"])]
        self.spawn_cb.configure(values=spawn_names)
        self.spawn_var.set(spawn_names[0])
        self.hint_var.set("💡 玩法提示：" + meta["spawns"][0].get("hint", ""))
        self._update_stair_btn()
        self.deadline = time.perf_counter()
        self.event_msg = f"已载入：{suite.split('·')[1].strip()}"
        if not initial:
            self.focus_console()

    def on_spawn_selected(self) -> None:
        val = self.spawn_var.get()
        idx = int(val.split(".")[0]) - 1 if "." in val else 0
        sp = self.sim.reset_at_spawn(idx)
        if self.sim.viewer is not None:
            with self.sim.viewer.lock():
                yaw_r = math.radians(float(sp["yaw_deg"]))
                self.sim.viewer.cam.lookat[:] = [
                    float(self.sim.d.qpos[0]) + 0.35 * math.cos(yaw_r),
                    float(self.sim.d.qpos[1]) + 0.35 * math.sin(yaw_r),
                    float(self.sim.d.qpos[2]) + 0.04,
                ]
                self.sim.viewer.cam.azimuth = float(sp["yaw_deg"]) + 135.0
        self.hint_var.set("💡 玩法提示：" + sp.get("hint", ""))
        self.deadline = time.perf_counter()
        self.event_msg = f"切换出生点：{sp['name']}"
        self.focus_console()

    def cycle_spawn(self, delta: int) -> None:
        n = len(self.sim.scene_meta.get("spawns", []))
        if n <= 1:
            return
        nxt = (self.sim.spawn_idx + delta) % n
        self.spawn_var.set(f"{nxt + 1}. {self.sim.scene_meta['spawns'][nxt]['name']}")
        self.on_spawn_selected()

    def _update_stair_btn(self) -> None:
        if self.sim.stair_mode:
            self.stair_btn.configure(text="C · 退出 E1 (切回 E0 巡航)", fg=self.PINK)
        else:
            self.stair_btn.configure(text="C · 开启 200mm 上阶专家 (E1)", fg=self.CYAN)

    def action_jump(self) -> None:
        if self.sim.trigger_forward_leap():
            self._update_stair_btn()
            self.event_msg = "🚀 触发 E2 平机身 COD 前向跳扑 / 直跳高台！"

    def action_toggle_stair(self) -> None:
        on = self.sim.toggle_stair_mode()
        self._update_stair_btn()
        self.h_slider_var.set(self.sim.target_h)
        self.event_msg = "🪜 已开启 E1 上台阶专家：按住 W 以 0.47m/s 攀爬！" if on else "已切回 E0 (c874) 全地形自由巡航"

    def action_park(self) -> None:
        pk = self.sim.toggle_stair_park()
        self._update_stair_btn()
        self.event_msg = "🅿️ E1 台顶低姿锁死驻车 (v=0, h=0.20m)" if pk else "解除驻车，恢复 0.4091m 上阶高姿"

    def action_fall(self) -> None:
        self.sim.trigger_random_fall()
        self._update_stair_btn()
        self.event_msg = "💥 触发随机空中抛落抗扰恢复测试！"

    def action_reset(self) -> None:
        sp = self.sim.reset_at_spawn()
        self.deadline = time.perf_counter()
        self.event_msg = f"🔄 已重置回起点：{sp['name']}"

    def action_pause(self) -> None:
        self.sim.paused = not self.sim.paused
        self.deadline = time.perf_counter()
        self.event_msg = "⏸ 已暂停" if self.sim.paused else "▶ 继续运行"

    def set_height_preset(self, h: float) -> None:
        if self.sim.stair_mode and h < 0.35:
            self.sim.stair_mode = False
            self._update_stair_btn()
        self.sim.target_h = float(np.clip(h, HEIGHT_MIN, HEIGHT_MAX))
        self.h_slider_var.set(self.sim.target_h)
        self.event_msg = f"站高预设 -> {self.sim.target_h:.2f} m"

    def on_height_slider(self) -> None:
        if not self.sim.stair_mode:
            self.sim.target_h = float(self.h_slider_var.get())

    def open_rough_overview(self) -> None:
        log = (HERE / "rough_overview.log").open("w", encoding="utf-8")
        subprocess.Popen(
            [sys.executable, "-X", "utf8", "-u", str(ROUGH_VIEWER_DIR / "showcase.py"), "--mode", "map"],
            cwd=str(ROUGH_VIEWER_DIR),
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=0x08000000,
        )
        self.event_msg = "已在新窗口打开 750 块 Rough-v1 全地形总览图"

    def poll_keys(self) -> set[str]:
        if not self.is_console_foreground():
            self.prev_vk_down.clear()
            return set(self.mouse_held_keys)

        down_now: set[str] = set()
        for name, vk in VK_MAP.items():
            if int(self.user32.GetAsyncKeyState(vk)) & 0x8000:
                down_now.add(name)

        just_pressed = down_now - self.prev_vk_down
        self.prev_vk_down = down_now

        for k in just_pressed:
            if k in ("space", "j"):
                self.action_jump()
            elif k == "c":
                self.action_toggle_stair()
            elif k == "v":
                self.action_park()
            elif k == "f":
                self.action_fall()
            elif k == "r":
                self.action_reset()
            elif k == "p":
                self.action_pause()
            elif k == "x":
                self.sim.cmd_vx = 0.0
                self.sim.cmd_wz = 0.0
                self.event_msg = "急停清零速度"
            elif k == "1":
                self.set_height_preset(0.20)
            elif k == "2":
                self.set_height_preset(0.28)
            elif k == "3":
                self.set_height_preset(STAIR_HIGH_H)
            elif k in ("4", "5", "6"):
                spd = {"4": 0.8, "5": 1.4, "6": 2.0}[k]
                self.sim.max_vx = spd
                self.v_slider_var.set(spd)
                self.event_msg = f"速度上限 -> {spd:.1f} m/s"
            elif k == "[":
                self.cycle_spawn(-1)
            elif k == "]":
                self.cycle_spawn(1)

        return down_now | self.mouse_held_keys

    def tick(self) -> None:
        if self.closed:
            return
        if self.sim.viewer is not None and not self.sim.viewer.is_running():
            self.close()
            return
        try:
            pressed = self.poll_keys()
            now = time.perf_counter()
            sub = 0
            if self.sim.viewer is not None:
                with self.sim.viewer.lock():
                    if self.sim.paused:
                        self.deadline = now
                    else:
                        while self.deadline <= time.perf_counter() and sub < 4:
                            self.sim.step(pressed)
                            self.deadline += CONTROL_DT
                            sub += 1
                        if self.deadline < now - 0.10:
                            self.deadline = now
                    if self.follow_cam_var.get():
                        R = self.sim.d.xmat[self.sim.env.base_id].reshape(3, 3)
                        yaw = math.atan2(float(R[1, 0]), float(R[0, 0]))
                        self.sim.viewer.cam.lookat[:] = [
                            float(self.sim.d.qpos[0]) + 0.32 * math.cos(yaw),
                            float(self.sim.d.qpos[1]) + 0.32 * math.sin(yaw),
                            float(self.sim.d.qpos[2]) + 0.03,
                        ]
                        if self.chase_cam_var.get():
                            self.sim.viewer.cam.azimuth = math.degrees(yaw) + 180.0
                self.sim.viewer.sync()

            if now - self.last_ui_time >= 0.05:
                self.last_ui_time = now
                self.refresh_hud(pressed)

            self.root.after(2, self.tick)
        except Exception:
            (HERE / "PLAYER_ERROR.txt").write_text(traceback.format_exc(), encoding="utf-8")
            traceback.print_exc()
            self.close()

    def refresh_hud(self, pressed: set[str]) -> None:
        t = self.sim.telemetry()
        self.tvars["expert"].set(t["expert"])
        self.tvars["pos"].set(f"({t['xyz'][0]:+.2f}, {t['xyz'][1]:+.2f}) m  |  地高 {t['ground_z']:+.2f}m")
        self.tvars["height"].set(f"净高 {t['rel_z']:.3f} m  /  指令 {t['target_h']:.3f} m")
        self.tvars["speed"].set(f"实速 {t['vx']:+.2f} m/s  /  指令 {t['cmd_vx']:+.2f} m/s")
        self.tvars["angles"].set(f"P {t['pitch_deg']:+5.1f}° | R {t['roll_deg']:+4.1f}° | Y {t['yaw_deg']:+5.1f}°")
        self.tvars["jump_stats"].set(f"净空 {t['peak_rim_cm']:4.1f} cm  |  空中俯仰 {t['max_air_pitch_deg']:4.1f}°")
        self.tvars["closure"].set(f"{t['closure_mm']:.3f} mm  |  跳扑 {t['jumps']} 次 / 复位 {t['resets']}")
        if not self.sim.stair_mode:
            self.h_slider_var.set(self.sim.target_h)

        focus_tag = "🟢 键盘已激活" if self.is_console_foreground() else "⚪ 点击本控制台激活键盘"
        run_tag = "⏸ 暂停" if t["paused"] else "▶ 运行中"
        self.status_var.set(f"{focus_tag} | {run_tag} | {self.event_msg}")

        now = time.perf_counter()
        if now - self.last_status_dump >= 0.5:
            self.last_status_dump = now
            payload = {
                **t,
                "suite": self.suite_var.get(),
                "spawn": self.spawn_var.get(),
                "pressed": sorted(pressed),
                "pid": os.getpid(),
                "checkpoint_sha256": self.sim.ckpt_sha,
                "updated_epoch": time.time(),
            }
            (HERE / "PLAYER_STATUS.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        self.sim.close()
        try:
            self.root.destroy()
        except Exception:
            pass


def run_smoke_test() -> None:
    """Headless verification across ALL 6 map suites + all 3 experts (E0, E1, E2) before opening GUI."""
    unified, sha = load_unified_moe_model()
    sim = UnifiedMoESimulation(unified, sha, show_viewer=False)
    results = []

    suites_to_test = [
        ("proving_ground_jump20", build_proving_ground(), 1, "jump"),
        ("proving_ground_stair200", build_proving_ground(), 3, "stair"),
        ("rmuc2027_red_avenue", build_rmuc2027(), 0, "cruise"),
        ("parkour_sirina", build_parkour_sirina(), 0, "cruise"),
        ("serial_ramp17", build_serial_leg_course(SERIAL_SUB_SCENES[0]), 0, "cruise"),
        ("stairs_24cm_jump", build_stairs_matrix(STAIRS_SUB_SCENES[1]), 1, "jump"),
        ("rough_v1_L4", build_rough_v1_tile(ROUGH_CN[9], 4), 0, "cruise"),
    ]

    for name, meta, sp_idx, mode_test in suites_to_test:
        t0 = time.perf_counter()
        sim.stair_mode = False
        sim.load_map(meta, spawn_idx=sp_idx)
        load_ms = (time.perf_counter() - t0) * 1000.0
        if mode_test == "jump":
            for k in range(110):
                if k == 10:
                    sim.trigger_forward_leap()
                sim.step(set())
        elif mode_test == "stair":
            sim.toggle_stair_mode(True)
            for _ in range(320):
                sim.step({"w"})
        else:
            for _ in range(40):
                sim.step({"w"})
        tel = sim.telemetry()
        assert tel["closure_mm"] < 2.0, f"Closure error > 2mm on {name}: {tel['closure_mm']}"
        results.append({"case": name, "load_ms": round(load_ms, 1), **tel})

    out = {"unified_sha256": sha, "all_passed": True, "cases": results}
    (HERE / "PLAYER_SMOKE.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ALL_MAPS_SMOKE_PASSED", json.dumps(out, ensure_ascii=False, indent=2), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="Run headless verification across all 6 map suites")
    args = ap.parse_args()

    if args.smoke:
        run_smoke_test()
        return

    unified, sha = load_unified_moe_model()
    sim = UnifiedMoESimulation(unified, sha, show_viewer=True)
    root = tk.Tk()
    AllMapsPlayerApp(root, sim)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        (HERE / "PLAYER_ERROR.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise

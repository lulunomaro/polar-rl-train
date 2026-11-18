# SPDX-License-Identifier: MIT
"""MuJoCo RL Environment for MOD4v3 COD-Style Forward Leap & Direct Jump-Onto-Step (16/20/24 cm).

Strict Physical & Zero-Cheating Contract:
  - Plant: MOD4v3 / HW300N60_R3 (MJCF SHA256 = 77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f)
    dt = 0.0025s (400Hz), 100Hz leg PD (60/2), 400Hz wheel servo (0.6), 50Hz policy (decim=8),
    2000 N/m closed-loop 4-bar gas springs, [-6, 6] action clip.
  - Actor receives ONLY (obs_35, obs_history_420) — ZERO world-z, ZERO step height, ZERO step distance!
  - Native 3D Solid Step Platforms (16 cm / 20 cm / 24 cm + 2-step staircase) & Anti-Cheat Rewards:
      * leap_dx < 0.40 m or post-push reverse vx < -0.06 m/s -> -15.0 anti-stationary/anti-reverse penalty!
      * slid_off_step after mounting platform -> -25.0 immediate penalty & episode termination!
"""
from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import mujoco
import numpy as np
import torch

from moe_forward_leap_model import (
    ACT_DIM,
    ACTION_CLIP,
    HIST_DIM,
    HIST_LEN,
    JUMP_MODE_BIT_INDEX,
    OBS_DIM,
    PRIV_CRITIC_DIM,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD_DELIVERY = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"

XML_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/mjcf/scene.xml"
RUNTIME_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/runtime_config.json"
SEMANTICS_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/semantics.json"
BANK_SOURCE = OLD_DELIVERY / "plant/reset_bank.json"
TEMPLATE_SOURCE = OLD_DELIVERY / "runtime/core/template_spec.json"

EXPECTED_XML_SHA256 = "77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f"

if str(OLD_DELIVERY / "runtime/core") not in sys.path:
    sys.path.insert(0, str(OLD_DELIVERY / "runtime/core"))

from play_mod4v3 import (  # noqa: E402
    ACTION_SCALE_LEG,
    ACTION_SCALE_WHEEL,
    CONTROL_DT,
    LEG_DELTA_BOUNDS,
    NO_LOAD,
    PEAK,
    STALL,
    WHEEL_VEL_LIMIT,
    RobotSpec,
    _q_from_bank,
    _q_from_runtime,
)
from play_ppo_flatv1 import _map  # noqa: E402

WHEEL_RADIUS_M = 0.0625
JUMP_GATE_DURATION_S = 1.90  # 95 steps (50Hz) of binary obs[30] = 1.0 per level-chassis forward leap


def ensure_forward_leap_scene_xml(cache_dir: Path | None = None) -> Path:
    """Create local MJCF preserving exact HW300N60_R3 robot physics + 2 dynamic 3D step platforms."""
    xml_sha = hashlib.sha256(XML_SOURCE.read_bytes()).hexdigest()
    if xml_sha != EXPECTED_XML_SHA256:
        raise RuntimeError(f"MJCF SHA256 mismatch: {xml_sha}")

    if cache_dir is None:
        cache_dir = HERE / "runtime_scenes"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_xml = cache_dir / "mod4v3_forward_leap_step_arena_v3.xml"
    if out_xml.exists():
        return out_xml

    tree = ET.parse(XML_SOURCE)
    root = tree.getroot()
    root.find("compiler").set("meshdir", str(XML_SOURCE.parent / "assets"))
    vis_global = root.find("visual/global")
    if vis_global is not None:
        vis_global.set("offwidth", "1440")
        vis_global.set("offheight", "900")

    asset = root.find("asset")
    ET.SubElement(
        asset,
        "texture",
        name="leap_grid",
        type="2d",
        builtin="checker",
        rgb1=".16 .20 .25",
        rgb2=".21 .26 .32",
        width="512",
        height="512",
        mark="edge",
        markrgb=".30 .38 .46",
    )
    ET.SubElement(
        asset,
        "material",
        name="leap_floor_mat",
        texture="leap_grid",
        texrepeat="26 26",
        texuniform="true",
        reflectance="0.05",
    )

    world = root.find("worldbody")
    ground = world.find("geom[@name='ground']")
    if ground is not None:
        ground.set("size", "32 32 .1")
        ground.set("material", "leap_floor_mat")

    # Non-colliding 0.5m X distance ruler lines so horizontal forward leap dx is visually unmistakable
    for half_m in range(-2, 26):
        x_val = 0.5 * half_m
        is_zero = half_m == 0
        is_int = half_m % 2 == 0
        rgba = ".25 .86 .98 .88" if is_zero else (".42 .56 .70 .60" if is_int else ".28 .36 .45 .38")
        w_half = "0.008" if is_int else "0.004"
        ET.SubElement(
            world,
            "geom",
            name=f"x_ruler_{half_m:+d}",
            type="box",
            pos=f"{x_val:.2f} 0 0.0008",
            size=f"{w_half} 1.65 0.0008",
            contype="0",
            conaffinity="0",
            rgba=rgba,
            group="1",
        )

    # Non-colliding height reference bars at y = +0.85m (16cm, 20cm, 24cm, 34cm)
    for h_cm, rgba in (
        (16, ".38 .82 .52 .42"),
        (20, ".96 .78 .26 .48"),
        (24, ".98 .52 .28 .52"),
        (34, ".42 .78 .98 .45"),
    ):
        ET.SubElement(
            world,
            "geom",
            name=f"h_ref_{h_cm}cm",
            type="box",
            pos=f"4.0 0.85 {h_cm / 100.0:.3f}",
            size="9.0 0.006 0.003",
            contype="0",
            conaffinity="0",
            rgba=rgba,
            group="1",
        )

    # 2 dynamically positioned solid collidable 3D step platforms on mocap bodies (exact MuJoCo 3.x BVH update!)
    step_colors = (".28 .52 .68 1", ".68 .46 .28 1")
    lip_colors = (".38 .88 .98 1", ".98 .78 .32 1")
    for idx in range(2):
        s_body = ET.SubElement(
            world,
            "body",
            name=f"dyn_step_body_{idx}",
            mocap="true",
            pos=f"{14.0 + 3.0 * idx:.2f} 0 -2.0",
        )
        ET.SubElement(
            s_body,
            "geom",
            name=f"dyn_step_{idx}",
            type="box",
            pos="0 0 0",
            size="2.00 1.05 0.25",
            contype="1",
            conaffinity="2",
            rgba=step_colors[idx],
            group="1",
        )
        ET.SubElement(
            s_body,
            "geom",
            name=f"dyn_step_lip_{idx}",
            type="box",
            pos="-1.988 0 0.245",
            size="0.012 1.052 0.005",
            contype="0",
            conaffinity="0",
            rgba=lip_colors[idx],
            group="1",
        )

    tree.write(out_xml, encoding="utf-8", xml_declaration=True)
    return out_xml


class Mod4v3ForwardLeapEnv:
    """Single-instance MuJoCo RL Environment for Forward Dolphin-Dive & Direct Step-Jump."""

    def __init__(self, seed: int = 0, xml_path: Path | None = None):
        torch.set_num_threads(1)
        self.rng = np.random.default_rng(seed)
        self.xml_path = xml_path or ensure_forward_leap_scene_xml()

        template = json.loads(TEMPLATE_SOURCE.read_text(encoding="utf-8"))
        self.spec = RobotSpec(**template["spec"])
        runtime = json.loads(RUNTIME_SOURCE.read_text(encoding="utf-8"))
        semantics = json.loads(SEMANTICS_SOURCE.read_text(encoding="utf-8"))
        bank = json.loads(BANK_SOURCE.read_text(encoding="utf-8"))

        self.default_q = _q_from_runtime(runtime, self.spec.joint_names)
        self.bank_q, self.bank_z = _q_from_bank(bank, semantics, self.spec.joint_names)
        self.order = [
            "left_front1_joint",
            "left_rear1_joint",
            "right_front1_joint",
            "right_rear1_joint",
            "left_wheel_joint",
            "right_wheel_joint",
        ]
        self.ppo_to_env_np = np.array([0, 2, 1, 3, 4, 5], dtype=np.int64)
        self.default_active = _map(self.default_q, self.spec.joint_names, self.order).numpy().astype(np.float32)

        self.m = mujoco.MjModel.from_xml_path(str(self.xml_path))
        self.d = mujoco.MjData(self.m)
        self.dt = float(self.m.opt.timestep)
        self.decim = int(round(CONTROL_DT / self.dt))
        assert abs(self.dt - 0.0025) < 1e-9 and self.decim == 8

        self.joint_ids = {n: int(self.m.joint(n).id) for n in self.spec.joint_names}
        self.qadr_all = np.array([int(self.m.jnt_qposadr[self.joint_ids[n]]) for n in self.spec.joint_names], dtype=np.int64)
        self.dadr_all = np.array([int(self.m.jnt_dofadr[self.joint_ids[n]]) for n in self.spec.joint_names], dtype=np.int64)
        self.active_qadr = np.array([int(self.m.joint(n).qposadr[0]) for n in self.order], dtype=np.int64)
        self.active_dadr = np.array([int(self.m.joint(n).dofadr[0]) for n in self.order], dtype=np.int64)

        self.leg_ids = np.asarray(self.spec.act_leg_idx, dtype=np.int64)
        self.wheel_ids = np.asarray(self.spec.act_wheel_idx, dtype=np.int64)
        self.default_leg_q = self.default_q[self.leg_ids].numpy().astype(np.float32)

        act_map = {mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(self.m.nu)}
        self.act_ids = np.array([int(act_map[self.spec.joint_names[j] + "_motor"]) for j in self.spec.act_idx], dtype=np.int64)

        self.base_id = int(self.m.body("base_link").id)
        self.wheels = [int(self.m.body("left_wheel_link").id), int(self.m.body("right_wheel_link").id)]
        self.guides = sorted(
            {int(self.m.geom_bodyid[i]) for i in range(self.m.ngeom) if (self.m.geom(i).name or "").startswith("guide_wheel_")}
        )
        self.ground_gid = int(self.m.geom("ground").id)
        self.tire_gids = [int(self.m.geom("left_tire").id), int(self.m.geom("right_tire").id)]
        self.step_body_ids = [int(self.m.body(f"dyn_step_body_{i}").id) for i in range(2)]
        self.step_mocap_ids = [int(self.m.body_mocapid[b]) for b in self.step_body_ids]
        self.env_body_ids = {0, *self.step_body_ids}
        self.step_gids = [int(self.m.geom(f"dyn_step_{i}").id) for i in range(2)]
        self.step_lip_gids = [int(self.m.geom(f"dyn_step_lip_{i}").id) for i in range(2)]

        self.pairs = [
            (int(self.m.site(e.get("site1")).id), int(self.m.site(e.get("site2")).id))
            for e in ET.parse(self.xml_path).getroot().findall("equality/connect")
        ]
        self.mimics = [
            (int(self.m.joint(f"{s}_{drv}").qposadr[0]), int(self.m.joint(f"{s}_{mn}").qposadr[0]))
            for s in ("left", "right")
            for drv, mn in (("rear1_drive_joint", "rear1_joint"), ("front1_drive_joint", "front1_joint"))
        ]

        self.nom_body_mass = self.m.body_mass.copy()
        self.nom_body_ipos = self.m.body_ipos.copy()
        self.nom_geom_friction = self.m.geom_friction.copy()

        self.dr_scale = 0.0
        self.kp_scale = np.ones(4, dtype=np.float32)
        self.kd_scale = np.ones(4, dtype=np.float32)
        self.kv_scale = np.ones(2, dtype=np.float32)
        self.effort_scale = np.ones(6, dtype=np.float32)
        self.delay_substeps = 0
        self.cur_mass_scale = 1.0
        self.cur_friction = 0.90

        self._local_force = np.zeros(6, dtype=np.float64)

        # Scenario configuration: steps = [(x_front, length_x, top_z), ...]
        self.active_steps: list[tuple[float, float, float]] = []
        self.v_cmd_pre = 0.0
        self.v_cmd_post = 0.0
        self.post_cmd_switch_s: float | None = None
        self.wz_cmd_target = 0.0
        self.h_nom = 0.28
        self.jump_times: tuple[float, ...] = (1.2,)
        self.max_episode_s = 5.0

        self.reset()

    def _apply_dr(self, dr_scale: float) -> None:
        self.dr_scale = float(np.clip(dr_scale, 0.0, 1.0))
        self.m.body_mass[:] = self.nom_body_mass
        self.m.body_ipos[:] = self.nom_body_ipos
        self.m.geom_friction[:] = self.nom_geom_friction

        if self.dr_scale <= 0.0:
            self.kp_scale[:] = 1.0
            self.kd_scale[:] = 1.0
            self.kv_scale[:] = 1.0
            self.effort_scale[:] = 1.0
            self.delay_substeps = 0
            self.cur_mass_scale = 1.0
            self.cur_friction = 0.90
            mujoco.mj_setConst(self.m, self.d)
            return

        s = self.dr_scale
        non_mocap = [b for b in range(1, self.m.nbody) if b not in self.step_body_ids]
        mass_mult = self.rng.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=len(non_mocap))
        self.m.body_mass[non_mocap] = self.nom_body_mass[non_mocap] * mass_mult
        self.cur_mass_scale = float(mass_mult[0])

        com_shift = self.rng.uniform(-0.020 * s, 0.020 * s, size=3)
        self.m.body_ipos[self.base_id] = self.nom_body_ipos[self.base_id] + com_shift

        mu = float(self.rng.uniform(0.90 - 0.30 * s, 0.90 + 0.30 * s))  # [0.60, 1.20] at Full-DR
        self.cur_friction = mu
        for gid in [self.ground_gid, *self.tire_gids, *self.step_gids]:
            self.m.geom_friction[gid, 0] = mu

        self.kp_scale = self.rng.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=4).astype(np.float32)
        self.kd_scale = self.rng.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=4).astype(np.float32)
        self.kv_scale = self.rng.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=2).astype(np.float32)
        self.effort_scale = self.rng.uniform(1.0 - 0.10 * s, 1.0 + 0.10 * s, size=6).astype(np.float32)
        self.delay_substeps = int(self.rng.integers(0, int(round(8 * s)) + 1))
        mujoco.mj_setConst(self.m, self.d)

    def configure_steps(self, steps: list[tuple[float, float, float]]) -> None:
        """Position up to 2 solid 3D platforms [(x_front_m, length_x_m, top_z_m), ...] via mocap bodies."""
        self.active_steps = list(steps[:2])
        for idx in range(2):
            gid = self.step_gids[idx]
            lip_gid = self.step_lip_gids[idx]
            mid = self.step_mocap_ids[idx]
            if idx < len(self.active_steps):
                xf, lx, hz = self.active_steps[idx]
                # Keep box half-size <= XML rbound (2.00 x 1.05 x 0.25) and position via d.mocap_pos!
                half_x = min(2.00, lx / 2.0)
                half_z = max(0.08, hz / 2.0)
                self.m.geom_size[gid] = [half_x, 1.05, half_z]
                self.m.geom_rbound[gid] = math.sqrt(half_x ** 2 + 1.05 ** 2 + half_z ** 2)
                self.m.geom_pos[lip_gid] = [-half_x + 0.012, 0.0, half_z - 0.005]
                self.d.mocap_pos[mid] = [xf + half_x, 0.0, hz - half_z]
            else:
                self.d.mocap_pos[mid] = [14.0 + 3.0 * idx, 0.0, -2.0]

    def terrain_z_at(self, x: float) -> float:
        """Ground/step top height at world X (used ONLY for diagnostics/reward/critic, NEVER actor!)."""
        z = 0.0
        for xf, lx, hz in self.active_steps:
            if xf <= x <= xf + lx:
                z = max(z, float(hz))
        return z

    @staticmethod
    def step_front_for_stand_jump(step_h: float, stand_dist: float = 0.745) -> float:
        """Place step front edge so level-chassis standstill runup+leap clears lip at apex and lands deep on top."""
        if step_h >= 0.23:
            return float(stand_dist + 0.013)
        if step_h <= 0.17:
            return float(stand_dist - 0.015)
        return float(stand_dist)

    @staticmethod
    def step_front_for_moving_jump(v_cmd: float, t_jump: float, lead_dist: float = 0.9055) -> float:
        """Place step front edge so robot moving at v_cmd (slewed from t=0.5s) clears lip at apex & lands on top."""
        x_at_trig = float(v_cmd) * max(0.0, float(t_jump) - 1.06)
        return x_at_trig + float(lead_dist) + 0.57 * max(0.0, float(v_cmd) - 0.75)

    def sample_random_scenario(self, dr_scale: float) -> dict[str, Any]:
        """Sample diverse level-chassis forward-leap & jump-onto-step training episode."""
        r = float(self.rng.random())
        h_jitter = float(self.rng.uniform(-0.008, 0.008)) * dr_scale

        if r < 0.22:
            # (1) Stand-to-Forward COD Dolphin-Dive (v_cmd=0 -> leaps forward >=0.75m & stops cleanly!)
            v_pre = 0.0
            v_post = 0.0
            sw_t = None
            t_j = float(self.rng.uniform(0.95, 1.40))
            j_times = (t_j,)
            steps: list[tuple[float, float, float]] = []
            max_s = t_j + 2.9
        elif r < 0.44:
            # (2) Moving High-Speed Forward Leap (v_cmd = +0.50 .. +1.10 m/s)
            v_pre = float(self.rng.uniform(0.50, 1.10))
            v_post = v_pre if self.rng.random() < 0.75 else 0.0
            t_j = float(self.rng.uniform(1.30, 1.75))
            sw_t = (t_j + 1.35) if v_post == 0.0 else None
            j_times = (t_j,)
            steps = []
            max_s = t_j + 2.9
        elif r < 0.52:
            # (3) Continuous 2x Forward Multi-Leap (standing start or moving!)
            v_pre = 0.0 if self.rng.random() < 0.30 else float(self.rng.uniform(0.60, 1.00))
            v_post = v_pre
            sw_t = None
            t1 = float(self.rng.uniform(1.15, 1.40))
            gap = float(self.rng.uniform(2.05, 2.35))
            j_times = (t1, t1 + gap)
            steps = []
            max_s = t1 + gap + 2.6
        elif r < 0.78:
            # (4) Stand / Micro-Approach Direct Jump-Onto-Step (16 / 20 / 24 cm) + Park or Walk on Top!
            v_pre = 0.0 if self.rng.random() < 0.80 else float(self.rng.uniform(0.20, 0.35))
            v_post = 0.0 if self.rng.random() < 0.70 else float(self.rng.uniform(0.40, 0.70))
            t_j = float(self.rng.uniform(1.00, 1.30))
            sw_t = t_j + 1.45
            base_h = float(self.rng.choice([0.16, 0.20, 0.24])) + h_jitter
            dist_front = (
                self.step_front_for_stand_jump(base_h, float(self.rng.uniform(0.736, 0.754)))
                if v_pre == 0.0
                else self.step_front_for_moving_jump(v_pre, t_j, float(self.rng.uniform(0.86, 0.91)))
            )
            steps = [(dist_front, 3.60, base_h)]
            j_times = (t_j,)
            max_s = t_j + 3.0
        else:
            # (5) Moving Approach Jump-Onto-Step (16 / 20 / 24 cm) + Cruise or Park on Step Top!
            v_pre = float(self.rng.uniform(0.60, 0.92))
            v_post = 0.0 if self.rng.random() < 0.55 else v_pre
            t_j = float(self.rng.uniform(1.35, 1.70))
            sw_t = t_j + 1.45
            base_h = float(self.rng.choice([0.16, 0.20, 0.24])) + h_jitter
            lead = float(self.rng.uniform(0.890, 0.920))
            xf = self.step_front_for_moving_jump(v_pre, t_j, lead)
            steps = [(xf, 3.80, base_h)]
            j_times = (t_j,)
            max_s = t_j + 2.9

        x0 = float(self.rng.uniform(-0.02, 0.02))
        y0 = float(self.rng.uniform(-0.04, 0.04))
        yaw0 = float(self.rng.uniform(-0.03, 0.03))
        return self.reset(
            dr_scale=dr_scale,
            v_cmd=v_pre,
            v_cmd_post=v_post,
            post_cmd_switch_s=sw_t,
            wz_cmd=0.0,
            h_nom=0.28,
            jump_times=j_times,
            max_episode_s=max_s,
            steps=steps,
            init_pose=(x0, y0, yaw0),
        )

    def reset(
        self,
        dr_scale: float = 0.0,
        v_cmd: float = 0.0,
        v_cmd_post: float | None = None,
        post_cmd_switch_s: float | None = None,
        wz_cmd: float = 0.0,
        h_nom: float = 0.28,
        jump_times: tuple[float, ...] = (1.2,),
        max_episode_s: float = 4.6,
        steps: list[tuple[float, float, float]] | None = None,
        init_pose: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> dict[str, np.ndarray]:
        mujoco.mj_resetData(self.m, self.d)
        self._apply_dr(dr_scale)
        self.configure_steps(steps or [])

        x0, y0, yaw0 = init_pose
        g_z0 = self.terrain_z_at(x0)
        self.d.qpos[:] = 0.0
        self.d.qvel[:] = 0.0
        self.d.ctrl[:] = 0.0
        self.d.qpos[:3] = [x0, y0, g_z0 + self.bank_z]
        self.d.qpos[3:7] = [math.cos(yaw0 / 2.0), 0.0, 0.0, math.sin(yaw0 / 2.0)]
        self.d.qpos[self.qadr_all] = self.bank_q.numpy()
        self.d.time = 0.0
        mujoco.mj_forward(self.m, self.d)

        self.v_cmd_pre = max(0.0, float(v_cmd))  # Forward-only leap contract
        self.v_cmd_post = self.v_cmd_pre if v_cmd_post is None else max(0.0, float(v_cmd_post))
        self.post_cmd_switch_s = post_cmd_switch_s
        self.wz_cmd_target = float(wz_cmd)
        self.h_nom = float(h_nom)
        self.height_cmd = 0.28
        self.cmd_vx = 0.0
        self.cmd_vy = 0.0
        self.cmd_wz = 0.0
        self.jump_times = tuple(float(t) for t in jump_times)
        self.max_episode_s = float(max_episode_s)

        self.a_prev = np.zeros(ACT_DIM, dtype=np.float32)
        self.action_delay_fifo: deque[np.ndarray] = deque(
            [np.zeros(ACT_DIM, dtype=np.float32) for _ in range(max(1, self.delay_substeps + 1))],
            maxlen=max(1, self.delay_substeps + 1),
        )

        # Jump window & step-commitment tracking
        self.cur_window_idx = -1
        self.window_t0 = -99.0
        self.window_start_wx = float(x0)
        self.window_liftoff_wx = float(x0)
        self.window_touchdown_wx = float(x0)
        self.window_crouch_min_rel_z = 99.0
        self.window_peak_world_rim = 0.0
        self.window_peak_rel_rim = 0.0
        self.window_takeoff_vx = 0.0
        self.window_min_post_vx = 99.0
        self.window_max_air_pitch_deg = 0.0
        self.window_max_pitch_deg = 0.0
        self.window_launched = False
        self.window_landed = False
        self.window_land_time = -99.0
        self.window_evaluated = False

        self.air_substeps = 0
        self.support_substeps = 8
        self.last_world_rim_m = 0.0
        self.max_closure_m = 0.0

        # Episode-level metrics (including 400Hz substep pitch bounds!)
        self.ep_start_wx = float(self.d.xpos[self.wheels, 0].mean())
        self.ep_peak_world_rim_m = 0.0
        self.ep_max_air_pitch_deg = 0.0
        self.ep_max_episode_pitch_deg = 0.0
        self.ep_leap_dxs: list[float] = []
        self.ep_air_dxs: list[float] = []
        self.ep_takeoff_vxs: list[float] = []
        self.ep_min_active_vx = 99.0
        self.ep_completed_leaps = 0
        self.ep_guide_force_max = 0.0
        self.ep_chassis_force_max = 0.0
        self.ep_riser_hit_force_max = 0.0

        self.step_wheel_frames = [0, 0]
        self.step_committed = [False, False]
        self.step_both_on = [False, False]
        self.slid_off_step = False

        obs = self._compute_obs()
        self.hist_buf = np.repeat(obs[None, :], HIST_LEN, axis=0)
        priv = self._compute_priv()
        return {"obs": obs, "hist": self.hist_buf.reshape(-1).copy(), "priv": priv}

    @property
    def body_vx(self) -> float:
        R = self.d.xmat[self.base_id].reshape(3, 3)
        fx, fy = float(R[0, 0]), float(R[1, 0])
        n = max(math.hypot(fx, fy), 1e-6)
        return float((self.d.qvel[0] * fx + self.d.qvel[1] * fy) / n)

    @property
    def body_vy(self) -> float:
        R = self.d.xmat[self.base_id].reshape(3, 3)
        lx, ly = float(R[0, 1]), float(R[1, 1])
        n = max(math.hypot(lx, ly), 1e-6)
        return float((self.d.qvel[0] * lx + self.d.qvel[1] * ly) / n)

    @property
    def cos_tilt(self) -> float:
        return float(self.d.xmat[self.base_id].reshape(3, 3)[2, 2])

    def _is_jump_bit_on(self, now: float) -> bool:
        for idx, tj in enumerate(self.jump_times):
            if tj - 1e-6 <= now < tj + JUMP_GATE_DURATION_S - 1e-6:
                if idx != self.cur_window_idx:
                    wx_now = float(self.d.xpos[self.wheels, 0].mean())
                    g_now = self.terrain_z_at(wx_now)
                    self.cur_window_idx = idx
                    self.window_t0 = tj
                    self.window_start_wx = wx_now
                    self.window_liftoff_wx = wx_now
                    self.window_touchdown_wx = wx_now
                    self.window_crouch_min_rel_z = float(self.d.qpos[2]) - g_now
                    self.window_peak_world_rim = 0.0
                    self.window_peak_rel_rim = 0.0
                    self.window_takeoff_vx = 0.0
                    self.window_min_post_vx = 99.0
                    self.window_max_air_pitch_deg = 0.0
                    self.window_max_pitch_deg = 0.0
                    self.window_launched = False
                    self.window_landed = False
                    self.window_land_time = -99.0
                    self.window_evaluated = False
                return True
        return False

    def _compute_obs(self) -> np.ndarray:
        """Standard 35-D proprioceptive actor observation (ZERO privileged terrain/world-z info!)."""
        now = float(self.d.time)
        jump_on = self._is_jump_bit_on(now)

        q = self.d.qpos[self.active_qadr].astype(np.float32)
        qd = self.d.qvel[self.active_dadr].astype(np.float32)
        R = self.d.xmat[self.base_id].reshape(3, 3).astype(np.float32)
        gravity_b = R.T @ np.array([0.0, 0.0, -1.0], dtype=np.float32)
        ang_vel_b = self.d.qvel[3:6].astype(np.float32) * 0.5

        joint_pos = q - self.default_active
        joint_pos[4:] = 0.0
        mode = np.zeros(7, dtype=np.float32)
        mode[0] = 1.0
        mode[JUMP_MODE_BIT_INDEX - 28] = 1.0 if jump_on else 0.0

        return np.concatenate(
            (
                np.array([self.cmd_vx, self.cmd_vy, self.cmd_wz, self.height_cmd * 5.0], dtype=np.float32),
                ang_vel_b,
                gravity_b,
                joint_pos,
                qd * 0.1,
                self.a_prev,
                mode,
            ),
            axis=0,
        )

    def _compute_priv(self) -> np.ndarray:
        """16-D privileged physics vector fed ONLY to training Value Critic."""
        now = float(self.d.time)
        wx_now = float(self.d.xpos[self.wheels, 0].mean())
        g_now = self.terrain_z_at(wx_now)
        dt_trig = min(2.0, max(0.0, now - self.window_t0)) if self.cur_window_idx >= 0 else 2.0
        step_dx, step_h = 3.0, 0.0
        for xf, lx, hz in self.active_steps:
            if xf + lx > wx_now - 0.1 and hz > g_now + 0.02:
                step_dx = float(np.clip(xf - wx_now, -0.5, 3.0))
                step_h = float(hz - g_now)
                break
        cur_dx = wx_now - self.window_start_wx if self.cur_window_idx >= 0 else 0.0
        return np.array(
            [
                float(self.d.qpos[2]) - g_now,
                float(self.d.qvel[2]),
                self.body_vx,
                self.body_vy,
                self.last_world_rim_m - g_now,
                float(self.support_substeps > 0),
                float(self.air_substeps > 0),
                dt_trig,
                float(self.window_launched),
                self.window_peak_world_rim,
                cur_dx,
                step_dx,
                step_h,
                g_now,
                self.cur_mass_scale,
                self.cur_friction,
            ],
            dtype=np.float32,
        )

    def _compute_motor_torque(self, a_env: np.ndarray) -> np.ndarray:
        q_leg = self.d.qpos[self.qadr_all[self.leg_ids]].astype(np.float32)
        qd_leg = self.d.qvel[self.dadr_all[self.leg_ids]].astype(np.float32)
        qd_wheel = self.d.qvel[self.dadr_all[self.wheel_ids]].astype(np.float32)

        target = (self.default_leg_q + ACTION_SCALE_LEG * a_env[:4]).astype(np.float32)
        low, high = LEG_DELTA_BOUNDS
        two_pi = 2.0 * math.pi
        for front, rear in ((0, 2), (1, 3)):
            delta = target[front] - target[rear]
            delta = delta + round(float(q_leg[front] - q_leg[rear] - delta) / two_pi) * two_pi
            delta = float(np.clip(delta, low, high))
            hip = target[rear]
            hip = hip + round(float(q_leg[rear] - hip) / two_pi) * two_pi
            target[rear] = hip
            target[front] = hip + delta

        v_target = np.clip(ACTION_SCALE_WHEEL * a_env[4:6], -WHEEL_VEL_LIMIT, WHEEL_VEL_LIMIT)
        raw_leg = (60.0 * self.kp_scale) * (target - q_leg) - (2.0 * self.kd_scale) * qd_leg
        raw_wheel = (0.6 * self.kv_scale) * (v_target - qd_wheel)
        raw = np.concatenate((raw_leg, raw_wheel), axis=0)

        v_act = np.concatenate((qd_leg, qd_wheel), axis=0)
        stall = STALL * self.effort_scale
        peak = PEAK * self.effort_scale
        upper = np.minimum(np.maximum(stall * (1.0 - v_act / NO_LOAD), 0.0), peak)
        lower = np.maximum(np.minimum(-stall * (1.0 + v_act / NO_LOAD), 0.0), -peak)
        return np.clip(raw, lower, upper)

    def step(self, action_ppo: np.ndarray) -> tuple[dict[str, np.ndarray], float, bool, dict[str, Any]]:
        act_clipped = np.clip(np.asarray(action_ppo, dtype=np.float32).reshape(ACT_DIM), -ACTION_CLIP, ACTION_CLIP)
        a_env_now = act_clipped[self.ppo_to_env_np]

        now_start = float(self.d.time)
        if not self._is_jump_bit_on(now_start):
            h_step = np.clip(self.h_nom - self.height_cmd, -0.06 * CONTROL_DT, 0.06 * CONTROL_DT)
            self.height_cmd = float(np.clip(self.height_cmd + h_step, 0.20, 0.42))

        if now_start < 0.50:
            vx_goal = 0.0
        elif self.post_cmd_switch_s is not None and now_start >= self.post_cmd_switch_s:
            vx_goal = self.v_cmd_post
        else:
            vx_goal = self.v_cmd_pre
        wz_goal = self.wz_cmd_target if now_start >= 0.50 else 0.0

        alpha = CONTROL_DT / 0.22
        self.cmd_vx += (vx_goal - self.cmd_vx) * alpha
        self.cmd_wz += (wz_goal - self.cmd_wz) * alpha

        step_guide_f = 0.0
        step_chassis_f = 0.0
        step_riser_hit_f = 0.0
        step_air_world_rim_max = 0.0
        fell_reason = ""

        for j in range(self.decim):
            self.action_delay_fifo.append(a_env_now)
            a_applied = self.action_delay_fifo[0]
            tau = self._compute_motor_torque(a_applied)
            if j % 4 == 0:
                self.d.ctrl[self.act_ids[:4]] = tau[:4]
            self.d.ctrl[self.act_ids[4:]] = tau[4:]
            mujoco.mj_step(self.m, self.d)

            if not np.isfinite(self.d.qpos).all() or not np.isfinite(self.d.qvel).all():
                fell_reason = "nonfinite"
                break

            f_wheel = f_guide = f_chassis = f_total = f_riser = 0.0
            for ci in range(self.d.ncon):
                c = self.d.contact[ci]
                g1, g2 = int(c.geom1), int(c.geom2)
                b1, b2 = int(self.m.geom_bodyid[g1]), int(self.m.geom_bodyid[g2])
                e1, e2 = (b1 in self.env_body_ids), (b2 in self.env_body_ids)
                if e1 == e2:
                    continue
                env_g, rb = (g1, b2) if e1 else (g2, b1)
                mujoco.mj_contactForce(self.m, self.d, ci, self._local_force)
                fnorm = float(np.linalg.norm(self._local_force[:3]))
                f_total += fnorm

                if env_g in self.step_gids:
                    s_idx = self.step_gids.index(env_g)
                    top_z = self.active_steps[s_idx][2] if s_idx < len(self.active_steps) else 0.0
                    is_top_surface = abs(float(c.frame[2])) >= 0.72 and float(c.pos[2]) >= top_z - 0.018
                    if rb in self.wheels and is_top_surface:
                        f_wheel += abs(float(self._local_force[0]))
                    else:
                        f_riser += fnorm
                        if rb in self.guides:
                            f_guide += fnorm
                        elif rb == self.base_id:
                            f_chassis += fnorm
                else:
                    if rb in self.wheels:
                        f_wheel += abs(float(self._local_force[0]))
                    elif rb in self.guides:
                        f_guide += fnorm
                    elif rb == self.base_id:
                        f_chassis += fnorm
                    else:
                        f_guide += fnorm

            step_guide_f = max(step_guide_f, f_guide)
            step_chassis_f = max(step_chassis_f, f_chassis)
            step_riser_hit_f = max(step_riser_hit_f, f_riser)

            cl = max(float(np.linalg.norm(self.d.site_xpos[u] - self.d.site_xpos[v])) for u, v in self.pairs)
            mm = max(abs(float(self.d.qpos[u] - self.d.qpos[v])) for u, v in self.mimics)
            self.max_closure_m = max(self.max_closure_m, cl)
            if cl > 0.010 or mm > 0.010:
                fell_reason = "closure_limit"
                break

            w_pos = self.d.xpos[self.wheels]
            world_rim_now = float((w_pos[:, 2] - WHEEL_RADIUS_M).min())
            self.last_world_rim_m = world_rim_now

            R_sub = self.d.xmat[self.base_id].reshape(3, 3)
            sub_pitch_deg = abs(math.degrees(math.asin(float(np.clip(-R_sub[2, 0], -1.0, 1.0)))))
            self.ep_max_episode_pitch_deg = max(self.ep_max_episode_pitch_deg, sub_pitch_deg)
            if self.cur_window_idx >= 0:
                self.window_max_pitch_deg = max(self.window_max_pitch_deg, sub_pitch_deg)

            if f_total < 1.0:
                if self.air_substeps == 0 and not self.window_launched:
                    self.window_liftoff_wx = float(w_pos[:, 0].mean())
                self.air_substeps += 1
                self.support_substeps = 0
                step_air_world_rim_max = max(step_air_world_rim_max, world_rim_now)
                if not self.window_landed:
                    self.ep_max_air_pitch_deg = max(self.ep_max_air_pitch_deg, sub_pitch_deg)
                    if self.cur_window_idx >= 0:
                        self.window_max_air_pitch_deg = max(self.window_max_air_pitch_deg, sub_pitch_deg)
            else:
                self.air_substeps = 0
                if f_wheel > 5.0:
                    self.support_substeps += 1

        self.ep_guide_force_max = max(self.ep_guide_force_max, step_guide_f)
        self.ep_chassis_force_max = max(self.ep_chassis_force_max, step_chassis_f)
        self.ep_riser_hit_force_max = max(self.ep_riser_hit_force_max, step_riser_hit_f)

        da_sq = float(np.sum((act_clipped - self.a_prev) ** 2))
        self.a_prev = act_clipped.copy()

        now = float(self.d.time)
        w_pos_end = self.d.xpos[self.wheels]
        wx_mean = float(w_pos_end[:, 0].mean())
        wx_min = float(w_pos_end[:, 0].min())
        wz_min_rim = float((w_pos_end[:, 2] - WHEEL_RADIUS_M).min())
        wz_max_rim = float((w_pos_end[:, 2] - WHEEL_RADIUS_M).max())
        g_under_wheels = self.terrain_z_at(wx_mean)
        rel_root_z = float(self.d.qpos[2]) - g_under_wheels
        root_vz = float(self.d.qvel[2])

        R = self.d.xmat[self.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wx_ang, wy_ang, wz_ang = float(self.d.qvel[3]), float(self.d.qvel[4]), float(self.d.qvel[5])
        vx_now = self.body_vx

        if not fell_reason and (self.cos_tilt < 0.50 or rel_root_z < 0.12):
            fell_reason = "fall_guard"

        # ---------------- Step-Top Commitment & Anti-Slide-Off Check ----------------
        for k, (xf, lx, hz) in enumerate(self.active_steps):
            any_wheel_on_step = (
                any(
                    (xf + 0.01 <= float(w_pos_end[wi, 0]) <= xf + lx)
                    and (hz - 0.020 <= float(w_pos_end[wi, 2]) - WHEEL_RADIUS_M <= hz + 0.035)
                    for wi in (0, 1)
                )
                and (self.support_substeps >= 1)
            )
            both_wheels_on_step = all(
                (xf + 0.03 <= float(w_pos_end[wi, 0]) <= xf + lx - 0.05)
                and (hz - 0.018 <= float(w_pos_end[wi, 2]) - WHEEL_RADIUS_M <= hz + 0.035)
                for wi in (0, 1)
            ) and (self.support_substeps >= 2)

            if any_wheel_on_step:
                self.step_wheel_frames[k] += 1
                if self.step_wheel_frames[k] >= 2:
                    self.step_committed[k] = True
            if both_wheels_on_step:
                self.step_both_on[k] = True
                self.step_committed[k] = True

            # Zero-tolerance anti-cheat: once committed to step, dropping below step or sliding back = -25 & terminate!
            if self.step_committed[k] and not fell_reason:
                dropped_z = wz_min_rim < hz - 0.035
                slid_back = wx_min < xf - 0.030
                if dropped_z or slid_back:
                    self.slid_off_step = True
                    fell_reason = "slid_off_step"

        # ---------------- Level-Chassis Forward-Leap & Step-Jump Anti-Cheat Reward ----------------
        reward = 0.6 * CONTROL_DT
        reward -= 0.35 * CONTROL_DT * (roll ** 2 * 8.0 + wx_ang ** 2 * 0.08)
        reward -= 0.0022 * da_sq

        # Global rigid low-pitch constraint across crouch, takeoff, flight & landing:
        #   +0.40 * exp(-((pitch / 0.08)^2)) - 0.15 * |wy|  (scaled cleanly per step)
        #   -8.0 * relu(|pitch| - 8 deg) - 25.0 * relu(|pitch| - 12 deg)
        abs_pitch = abs(pitch)
        reward += (4.0 * CONTROL_DT) * (0.40 * math.exp(-((pitch / 0.08) ** 2)) - 0.15 * abs(wy_ang))
        pitch_over_8 = max(0.0, abs_pitch - math.radians(8.0))
        pitch_over_12 = max(0.0, abs_pitch - math.radians(12.0))
        reward -= (15.0 * CONTROL_DT) * (8.0 * pitch_over_8 + 25.0 * pitch_over_12)

        jump_on = self._is_jump_bit_on(now)
        dt_w = now - self.window_t0 if self.cur_window_idx >= 0 else 99.0

        if jump_on:
            if dt_w >= 0.45:
                self.window_min_post_vx = min(self.window_min_post_vx, vx_now)
                self.ep_min_active_vx = min(self.ep_min_active_vx, vx_now)
                # Continuous anti-reverse penalty during push, flight & landing!
                if vx_now < -0.02:
                    reward -= 16.0 * CONTROL_DT * (abs(vx_now) / 0.12)

            if not self.window_launched and not self.window_landed:
                self.window_crouch_min_rel_z = min(self.window_crouch_min_rel_z, rel_root_z)
                if dt_w < 0.65 and self.support_substeps >= 2:
                    # Reward level-chassis forward momentum buildup (vx -> >= 1.0 m/s) + crouch preload!
                    crouch_err = (rel_root_z - 0.198) / 0.032
                    target_lunge_vx = max(self.cmd_vx, 1.08)
                    reward += 1.4 * CONTROL_DT * math.exp(-(crouch_err ** 2))
                    reward += 1.6 * CONTROL_DT * math.exp(-((vx_now - target_lunge_vx) ** 2) / 0.28)

                if self.air_substeps >= 4 and root_vz > 0.25 and self.window_crouch_min_rel_z < 0.242:
                    self.window_launched = True
                    self.window_takeoff_vx = vx_now
                    self.ep_takeoff_vxs.append(vx_now)
                    fwd_bonus = float(np.clip(vx_now / 1.12, 0.0, 1.3))
                    crouch_bonus = float(np.clip((0.240 - max(0.184, self.window_crouch_min_rel_z)) / 0.046, 0.0, 1.1))
                    level_launch = math.exp(-((pitch / 0.12) ** 2))
                    reward += 2.4 * fwd_bonus * crouch_bonus * level_launch

            if self.window_launched and not self.window_landed:
                if self.air_substeps >= 1:
                    self.window_peak_world_rim = max(self.window_peak_world_rim, step_air_world_rim_max)
                    self.window_peak_rel_rim = max(
                        self.window_peak_rel_rim, step_air_world_rim_max - self.terrain_z_at(self.window_start_wx)
                    )
                    self.ep_peak_world_rim_m = max(self.ep_peak_world_rim_m, step_air_world_rim_max)
                    # Dense airborne forward progress + leg tuck clearance + strict level chassis!
                    q_l = self.d.qpos[self.active_qadr[:4]]
                    cur_delta = 0.5 * float((q_l[0] - q_l[1]) + (q_l[2] - q_l[3]))
                    tuck_factor = float(np.clip((1.25 - cur_delta) / 0.85, 0.2, 1.2))
                    fwd_factor = float(np.clip(vx_now / 1.08, 0.0, 1.3))
                    reward += 3.6 * CONTROL_DT * np.clip(step_air_world_rim_max / 0.33, 0.0, 1.25) * tuck_factor * fwd_factor
                    reward += 2.2 * CONTROL_DT * math.exp(-((pitch / 0.08) ** 2) - ((roll / 0.06) ** 2))
                elif self.support_substeps >= 2 and dt_w > 0.22:
                    self.window_landed = True
                    self.window_land_time = now
                    self.window_touchdown_wx = wx_mean
                    leap_dx = self.window_touchdown_wx - self.window_start_wx
                    air_dx = self.window_touchdown_wx - self.window_liftoff_wx
                    self.ep_leap_dxs.append(leap_dx)
                    self.ep_air_dxs.append(air_dx)

                    if (
                        leap_dx >= 0.55
                        and self.window_max_air_pitch_deg <= 12.0
                        and abs_pitch < math.radians(13.5)
                        and step_guide_f < 1.0
                        and step_chassis_f < 1.0
                        and step_riser_hit_f < 2.0
                    ):
                        self.ep_completed_leaps += 1
                        dx_score = float(np.clip((leap_dx - 0.45) / 0.45, 0.0, 1.45))
                        clr_score = float(np.clip((self.window_peak_rel_rim - 0.18) / 0.14, 0.0, 1.25))
                        pitch_q = float(np.clip(1.20 - 0.10 * max(0.0, self.window_max_air_pitch_deg - 8.0), 0.35, 1.20))
                        reward += 10.0 * dx_score * clr_score * pitch_q
                        if any(self.step_both_on):
                            reward += 13.0 * pitch_q  # Direct airborne level-chassis jump-onto-step bonus!

            if self.window_landed:
                # Smooth level-chassis post-landing coast & zero-rollback stabilization!
                reward -= 3.5 * CONTROL_DT * (math.sin(pitch) ** 2) - 0.10 * CONTROL_DT * (wy_ang ** 2)
                if now - self.window_land_time >= 0.35:
                    reward += 2.0 * CONTROL_DT * math.exp(-((vx_now - self.cmd_vx) ** 2) / 0.20)
                    if any(self.step_both_on):
                        reward += 2.6 * CONTROL_DT  # Dense bonus for holding stably on top of step!
        else:
            # Exact anti-cheat check when jump gate closes (obs[30]: 1 -> 0)
            if self.cur_window_idx >= 0 and not self.window_evaluated and dt_w >= JUMP_GATE_DURATION_S - 1e-6:
                self.window_evaluated = True
                settled_dx = wx_mean - self.window_start_wx
                min_req_dx = 0.60 if self.v_cmd_pre < 0.25 else 0.78
                if settled_dx < min_req_dx or self.window_min_post_vx < -0.03 or self.window_peak_rel_rim < 0.20:
                    reward -= 18.0  # Strict anti-stationary / anti-reverse penalty!

            # Normal cruise / step-top park tracking
            reward += 1.6 * CONTROL_DT * math.exp(-((vx_now - self.cmd_vx) ** 2) / 0.16)
            reward += 0.5 * CONTROL_DT * math.exp(-((wz_ang - self.cmd_wz) ** 2) / 0.35)
            reward -= 2.5 * CONTROL_DT * (math.sin(pitch) ** 2)
            if any(self.step_both_on):
                reward += 1.8 * CONTROL_DT

        # Smooth non-wheel / riser collision penalties
        if step_guide_f > 1.0 or step_chassis_f > 1.0:
            reward -= 0.30 + 0.0009 * min(step_guide_f + step_chassis_f, 2000.0)
        if step_riser_hit_f > 2.0:
            reward -= 0.60 + 0.0010 * min(step_riser_hit_f, 2500.0)

        done = False
        if fell_reason == "slid_off_step":
            reward -= 25.0
            done = True
        elif fell_reason:
            reward -= 10.0
            done = True
        elif now >= self.max_episode_s - 1e-6:
            done = True

        obs = self._compute_obs()
        self.hist_buf[:-1] = self.hist_buf[1:]
        self.hist_buf[-1] = obs
        hist = self.hist_buf.reshape(-1).copy()
        priv = self._compute_priv()

        info = {
            "time_s": now,
            "fell_reason": fell_reason,
            "slid_off_step": self.slid_off_step,
            "step_landed_both_wheels": bool(any(self.step_both_on)),
            "steps_mounted_count": int(sum(1 for b in self.step_both_on if b)),
            "steps_total": len(self.active_steps),
            "ep_peak_world_rim_cm": round(self.ep_peak_world_rim_m * 100.0, 2),
            "ep_max_air_pitch_deg": round(self.ep_max_air_pitch_deg, 2),
            "ep_max_episode_pitch_deg": round(self.ep_max_episode_pitch_deg, 2),
            "ep_mean_leap_dx_m": round(float(np.mean(self.ep_leap_dxs)), 3) if self.ep_leap_dxs else 0.0,
            "ep_mean_air_dx_m": round(float(np.mean(self.ep_air_dxs)), 3) if self.ep_air_dxs else 0.0,
            "ep_total_net_dx_m": round(wx_mean - self.ep_start_wx, 3),
            "ep_mean_takeoff_vx": round(float(np.mean(self.ep_takeoff_vxs)), 3) if self.ep_takeoff_vxs else 0.0,
            "ep_min_active_vx": round(self.ep_min_active_vx, 3) if self.ep_min_active_vx < 50.0 else 0.0,
            "ep_completed_leaps": self.ep_completed_leaps,
            "ep_expected_leaps": len(self.jump_times),
            "ep_guide_force_N": round(self.ep_guide_force_max, 2),
            "ep_chassis_force_N": round(self.ep_chassis_force_max, 2),
            "ep_riser_hit_N": round(self.ep_riser_hit_force_max, 2),
            "max_closure_mm": round(self.max_closure_m * 1000.0, 3),
        }
        return {"obs": obs, "hist": hist, "priv": priv}, float(reward), done, info


class ParallelLeapVecEnv:
    """GIL-releasing ThreadPool MuJoCo Vectorized Environment capped strictly at <= 5 workers."""

    def __init__(self, num_envs: int = 5, base_seed: int = 1000):
        self.num_envs = num_envs
        xml_path = ensure_forward_leap_scene_xml()
        self.envs = [Mod4v3ForwardLeapEnv(seed=base_seed + i * 97, xml_path=xml_path) for i in range(num_envs)]
        self.dr_scale = 0.0
        self.pool = ThreadPoolExecutor(max_workers=min(num_envs, 5))
        self.closed = False

    def set_dr_scale(self, dr_scale: float) -> None:
        self.dr_scale = float(dr_scale)

    def reset_random(self, dr_scale: float = 0.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        self.dr_scale = float(dr_scale)
        states = list(self.pool.map(lambda e: e.sample_random_scenario(dr_scale=self.dr_scale), self.envs))
        obs = np.stack([s["obs"] for s in states], axis=0)
        hist = np.stack([s["hist"] for s in states], axis=0)
        priv = np.stack([s["priv"] for s in states], axis=0)
        return obs, hist, priv

    def _step_one(self, pair: tuple[Mod4v3ForwardLeapEnv, np.ndarray]) -> tuple[dict[str, np.ndarray], float, bool, dict]:
        env, act = pair
        state, rew, done, info = env.step(act)
        if done:
            final_info = info
            if info["fell_reason"] == "":
                final_info["terminal_state"] = state
            state = env.sample_random_scenario(dr_scale=self.dr_scale)
            final_info["terminal_reset"] = True
            return state, rew, True, final_info
        return state, rew, False, info

    def step(self, actions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[dict]]:
        results = list(self.pool.map(self._step_one, zip(self.envs, actions)))
        obs = np.stack([r[0]["obs"] for r in results], axis=0)
        hist = np.stack([r[0]["hist"] for r in results], axis=0)
        priv = np.stack([r[0]["priv"] for r in results], axis=0)
        rews = np.array([r[1] for r in results], dtype=np.float32)
        dones = np.array([r[2] for r in results], dtype=bool)
        infos = [r[3] for r in results]
        return obs, hist, priv, rews, dones, infos

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        self.pool.shutdown(wait=True)

# SPDX-License-Identifier: MIT
"""Vectorized / Multiprocess MuJoCo RL Environment for MOD4v3 Pure-Neural High Jump & Moving Jump.

Strict Physical & Anti-Cheat Contract:
  - Plant: MOD4v3 / HW300N60_R3 (MJCF SHA256 = 77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f)
    dt = 0.0025s (400Hz), 100Hz leg PD (60/2), 400Hz wheel servo (0.6), 50Hz policy (decim=8),
    2000 N/m closed-loop 4-bar gas springs, [-6, 6] action clip.
  - Actor receives ONLY (obs_35, obs_history_420):
      obs[0:3]   = [cmd_vx, cmd_vy, cmd_wz]
      obs[3]     = height_cmd * 5.0 (nominal 0.28 * 5 = 1.40)
      obs[4:7]   = root_ang_vel_b * 0.5
      obs[7:10]  = projected_gravity_b
      obs[10:16] = joint_pos - default_active (wheel pos muted to 0)
      obs[16:22] = joint_vel * 0.1
      obs[22:28] = a_prev
      obs[28:35] = [1, 0, jump_bit, 0, 0, 0, 0]  (jump_bit ∈ {0.0, 1.0}, ZERO phase/clock/world-z!)
  - Domain Randomization (dr_scale ∈ [0.0, 1.0]):
      Body mass ±12%, base COM ±2.5cm, ground friction [0.55, 1.15], PD gains ±12%,
      motor effort ±10%, 0-20ms substep action delay, plus 14-20cm physical box hurdles.
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

import mujoco
import numpy as np
import torch

from moe_jump_model import (
    ACT_DIM,
    ACTION_CLIP,
    HIST_DIM,
    HIST_LEN,
    HistoryQueue,
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
    _continuous_leg_target,
    _q_from_bank,
    _q_from_runtime,
)
from play_ppo_flatv1 import _map  # noqa: E402

WHEEL_RADIUS_M = 0.0625
JUMP_GATE_DURATION_S = 1.44  # 72 steps of constant binary jump_bit = 1.0 per jump request


def ensure_rl_scene_xml(cache_dir: Path | None = None) -> Path:
    """Create local MJCF preserving exact HW300N60_R3 physics + repositionable hurdle geoms."""
    xml_sha = hashlib.sha256(XML_SOURCE.read_bytes()).hexdigest()
    if xml_sha != EXPECTED_XML_SHA256:
        raise RuntimeError(f"MJCF SHA256 mismatch: {xml_sha}")

    if cache_dir is None:
        cache_dir = HERE / "runtime_scenes"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_xml = cache_dir / "mod4v3_rl_jump_arena.xml"
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
        name="rl_grid",
        type="2d",
        builtin="checker",
        rgb1=".17 .21 .26",
        rgb2=".22 .27 .33",
        width="512",
        height="512",
        mark="edge",
        markrgb=".31 .38 .46",
    )
    ET.SubElement(
        asset,
        "material",
        name="rl_floor_mat",
        texture="rl_grid",
        texrepeat="24 24",
        texuniform="true",
        reflectance="0.05",
    )

    world = root.find("worldbody")
    ground = world.find("geom[@name='ground']")
    if ground is not None:
        ground.set("size", "30 30 .1")
        ground.set("material", "rl_floor_mat")

    # Visual-only X distance ticks & height reference rails (contype=0, conaffinity=0)
    for x_tick in range(-4, 16):
        ET.SubElement(
            world,
            "geom",
            name=f"x_line_{x_tick:+d}",
            type="box",
            pos=f"{x_tick:.2f} 0 0.0008",
            size="0.006 1.6 0.0008",
            contype="0",
            conaffinity="0",
            rgba=".36 .46 .56 .50" if x_tick != 0 else ".28 .82 .96 .80",
            group="1",
        )
    for h_cm, rgba in ((20, ".42 .78 .46 .45"), (30, ".95 .78 .26 .55"), (40, ".98 .40 .36 .55")):
        ET.SubElement(
            world,
            "geom",
            name=f"ruler_bar_{h_cm}cm",
            type="box",
            pos=f"3.5 0.75 {h_cm / 100.0:.3f}",
            size="8.5 0.006 0.003",
            contype="0",
            conaffinity="0",
            rgba=rgba,
            group="1",
        )

    # 3 dynamically positioned collidable box hurdles (default parked underground at z=-2.0m)
    hurdle_colors = (".28 .82 .52 1", ".96 .76 .24 1", ".96 .42 .36 1")
    for idx in range(3):
        ET.SubElement(
            world,
            "geom",
            name=f"dyn_hurdle_{idx}",
            type="box",
            pos=f"{2.0 + 2.2 * idx:.2f} 0 -2.0",
            size="0.03 0.80 0.08",
            contype="1",
            conaffinity="2",
            rgba=hurdle_colors[idx],
            group="1",
        )

    tree.write(out_xml, encoding="utf-8", xml_declaration=True)
    return out_xml


class Mod4v3RLJumpEnv:
    """Single-instance MuJoCo RL Jump Environment with full Domain Randomization & Anti-Cheat Rewards."""

    def __init__(self, seed: int = 0, xml_path: Path | None = None):
        torch.set_num_threads(1)
        self.rng = np.random.default_rng(seed)
        self.xml_path = xml_path or ensure_rl_scene_xml()

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
        self.hurdle_gids = [int(self.m.geom(f"dyn_hurdle_{i}").id) for i in range(3)]

        self.pairs = [
            (int(self.m.site(e.get("site1")).id), int(self.m.site(e.get("site2")).id))
            for e in ET.parse(self.xml_path).getroot().findall("equality/connect")
        ]
        self.mimics = [
            (int(self.m.joint(f"{s}_{drv}").qposadr[0]), int(self.m.joint(f"{s}_{mn}").qposadr[0]))
            for s in ("left", "right")
            for drv, mn in (("rear1_drive_joint", "rear1_joint"), ("front1_drive_joint", "front1_joint"))
        ]

        # Save nominal physical parameters for exact restoration before DR sampling
        self.nom_body_mass = self.m.body_mass.copy()
        self.nom_body_ipos = self.m.body_ipos.copy()
        self.nom_geom_friction = self.m.geom_friction.copy()

        # Episode DR multipliers
        self.dr_scale = 0.0
        self.kp_scale = np.ones(4, dtype=np.float32)
        self.kd_scale = np.ones(4, dtype=np.float32)
        self.kv_scale = np.ones(2, dtype=np.float32)
        self.effort_scale = np.ones(6, dtype=np.float32)
        self.delay_substeps = 0
        self.cur_mass_scale = 1.0
        self.cur_friction = 0.90

        self.hist_queue = HistoryQueue(HIST_LEN)
        self._local_force = np.zeros(6, dtype=np.float64)

        # Scenario configuration
        self.v_cmd_target = 0.0
        self.wz_cmd_target = 0.0
        self.h_nom = 0.28
        self.jump_times: tuple[float, ...] = (1.6,)
        self.max_episode_s = 5.4
        self.active_hurdles: list[tuple[float, float]] = []  # [(x_center, top_z), ...]
        self.cleared_hurdles: set[int] = set()

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
        mass_mult = self.rng.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=self.m.nbody - 1)
        self.m.body_mass[1:] = self.nom_body_mass[1:] * mass_mult
        self.cur_mass_scale = float(mass_mult[0])

        com_shift = self.rng.uniform(-0.025 * s, 0.025 * s, size=3)
        self.m.body_ipos[self.base_id] = self.nom_body_ipos[self.base_id] + com_shift

        mu = float(self.rng.uniform(0.90 - 0.35 * s, 0.90 + 0.25 * s))  # [0.55, 1.15] at s=1.0
        self.cur_friction = mu
        for gid in [self.ground_gid, *self.tire_gids, *self.hurdle_gids]:
            self.m.geom_friction[gid, 0] = mu

        self.kp_scale = self.rng.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=4).astype(np.float32)
        self.kd_scale = self.rng.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=4).astype(np.float32)
        self.kv_scale = self.rng.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=2).astype(np.float32)
        self.effort_scale = self.rng.uniform(1.0 - 0.10 * s, 1.0 + 0.10 * s, size=6).astype(np.float32)
        self.delay_substeps = int(self.rng.integers(0, int(round(8 * s)) + 1))  # 0..8 substeps = 0..20ms
        mujoco.mj_setConst(self.m, self.d)

    @staticmethod
    def hurdle_apex_x(v_cmd: float, t_jump: float) -> float:
        """Nominal world X directly beneath the moving jump apex when cmd_vx slews from t=0.6s."""
        return -0.14 + float(v_cmd) * (float(t_jump) - 0.40)

    def configure_hurdles(self, hurdles: list[tuple[float, float]]) -> None:
        """Position up to 3 physical solid floor-to-top box hurdles [(x_center_m, height_m), ...]."""
        self.active_hurdles = list(hurdles[:3])
        self.cleared_hurdles.clear()
        for idx, gid in enumerate(self.hurdle_gids):
            if idx < len(self.active_hurdles):
                hx, hz = self.active_hurdles[idx]
                # Solid floor-to-top box barrier (3.0cm thick along X, 1.6m wide along Y, height=hz)
                self.m.geom_size[gid] = [0.015, 0.80, hz / 2.0]
                self.m.geom_pos[gid] = [hx, 0.0, hz / 2.0]
            else:
                self.m.geom_size[gid] = [0.015, 0.80, 0.05]
                self.m.geom_pos[gid] = [10.0 + idx, 0.0, -2.0]

    def sample_random_scenario(self, dr_scale: float) -> dict[str, Any]:
        """Sample diverse RL training task (standing, moving, reverse, multi-jump, or hurdle jump)."""
        r = float(self.rng.random())
        if r < 0.18:
            # Standing jump
            v_cmd = 0.0
            wz_cmd = float(self.rng.uniform(-0.25, 0.25)) if self.rng.random() < 0.3 else 0.0
            j_times = (float(self.rng.uniform(1.3, 1.9)),)
            max_s = 4.6
            hurdles: list[tuple[float, float]] = []
        elif r < 0.34:
            # Reverse moving jump
            v_cmd = float(self.rng.uniform(-0.60, -0.35))
            wz_cmd = 0.0
            j_times = (float(self.rng.uniform(1.5, 2.0)),)
            max_s = 4.8
            hurdles = []
        elif r < 0.62:
            # Forward moving single jump
            v_cmd = float(self.rng.uniform(0.30, 1.25))
            wz_cmd = float(self.rng.uniform(-0.35, 0.35)) if self.rng.random() < 0.3 else 0.0
            j_times = (float(self.rng.uniform(1.4, 2.0)),)
            max_s = 4.8
            hurdles = []
        elif r < 0.82:
            # Physical 14-20cm Solid Box Hurdle Jump! Place hurdle under ballistic jump apex X!
            v_cmd = float(self.rng.uniform(1.05, 1.25))
            wz_cmd = 0.0
            t_j = float(self.rng.uniform(1.5, 1.8))
            apex_x = self.hurdle_apex_x(v_cmd, t_j) + float(self.rng.uniform(-0.025, 0.025))
            h_height = float(self.rng.uniform(0.14, 0.205))
            hurdles = [(apex_x, h_height)]
            j_times = (t_j,)
            max_s = 4.8
        else:
            # Continuous 2x or 3x Moving Multi-Jump!
            v_cmd = float(self.rng.uniform(0.55, 1.05))
            wz_cmd = 0.0
            t1 = float(self.rng.uniform(1.3, 1.6))
            gap1 = float(self.rng.uniform(1.80, 2.10))
            gap2 = float(self.rng.uniform(1.80, 2.10))
            j_times = (t1, t1 + gap1, t1 + gap1 + gap2)
            max_s = t1 + gap1 + gap2 + 2.1
            hurdles = []

        # 75% standard h=0.28m (obs[3]=1.40), 25% [0.27..0.365m] so WASD Q/E height also works smoothly
        h_nom = 0.28 if self.rng.random() < 0.75 else float(self.rng.uniform(0.27, 0.365))
        x0 = float(self.rng.uniform(-0.04, 0.04))
        y0 = float(self.rng.uniform(-0.05, 0.05))
        yaw0 = float(self.rng.uniform(-0.04, 0.04))
        return self.reset(
            dr_scale=dr_scale,
            v_cmd=v_cmd,
            wz_cmd=wz_cmd,
            h_nom=h_nom,
            jump_times=j_times,
            max_episode_s=max_s,
            hurdles=hurdles,
            init_pose=(x0, y0, yaw0),
        )

    def reset(
        self,
        dr_scale: float = 0.0,
        v_cmd: float = 0.0,
        wz_cmd: float = 0.0,
        h_nom: float = 0.28,
        jump_times: tuple[float, ...] = (1.6,),
        max_episode_s: float = 5.0,
        hurdles: list[tuple[float, float]] | None = None,
        init_pose: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> dict[str, np.ndarray]:
        mujoco.mj_resetData(self.m, self.d)
        self._apply_dr(dr_scale)
        self.configure_hurdles(hurdles or [])

        x0, y0, yaw0 = init_pose
        self.d.qpos[:] = 0.0
        self.d.qvel[:] = 0.0
        self.d.ctrl[:] = 0.0
        self.d.qpos[:3] = [x0, y0, self.bank_z]
        self.d.qpos[3:7] = [math.cos(yaw0 / 2.0), 0.0, 0.0, math.sin(yaw0 / 2.0)]
        self.d.qpos[self.qadr_all] = self.bank_q.numpy()
        self.d.time = 0.0
        mujoco.mj_forward(self.m, self.d)

        self.v_cmd_target = float(v_cmd)
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

        # Window tracking for reward shaping & diagnostics
        self.cur_window_idx = -1
        self.window_t0 = -99.0
        self.window_crouch_min_z = 99.0
        self.window_peak_rim = 0.0
        self.window_launched = False
        self.window_landed = False
        self.window_land_time = -99.0
        self.air_substeps = 0
        self.support_substeps = 8
        self.last_rim_m = 0.0
        self.max_closure_m = 0.0
        self.ep_peak_rim_m = 0.0
        self.ep_completed_jumps = 0
        self.ep_guide_force_max = 0.0
        self.ep_chassis_force_max = 0.0
        self.ep_hurdle_hit_force_max = 0.0

        obs = self._compute_obs()
        self.hist_buf = np.repeat(obs[None, :], HIST_LEN, axis=0)
        hist = self.hist_buf.reshape(-1).copy()
        priv = self._compute_priv()
        return {"obs": obs, "hist": hist, "priv": priv}

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
                    self.cur_window_idx = idx
                    self.window_t0 = tj
                    self.window_crouch_min_z = float(self.d.qpos[2])
                    self.window_peak_rim = 0.0
                    self.window_launched = False
                    self.window_landed = False
                    self.window_land_time = -99.0
                return True
        return False

    def _compute_obs(self) -> np.ndarray:
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
        mode[JUMP_MODE_BIT_INDEX - 28] = 1.0 if jump_on else 0.0  # obs[30]

        obs = np.concatenate(
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
        return obs

    def _compute_priv(self) -> np.ndarray:
        """14-D privileged physics vector for training Value Critic ONLY."""
        now = float(self.d.time)
        dt_trig = min(2.0, max(0.0, now - self.window_t0)) if self.cur_window_idx >= 0 else 2.0
        hx_dx, h_z = 3.0, 0.0
        rx = float(self.d.qpos[0])
        for hx, hz in self.active_hurdles:
            if hx - rx > -0.35:
                hx_dx = float(np.clip(hx - rx, -0.5, 3.0))
                h_z = float(hz)
                break
        return np.array(
            [
                float(self.d.qpos[2]),
                float(self.d.qvel[2]),
                self.body_vx,
                self.body_vy,
                self.last_rim_m,
                float(self.support_substeps > 0),
                float(self.air_substeps > 0),
                dt_trig,
                float(self.window_launched),
                self.window_peak_rim,
                hx_dx,
                h_z,
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
        # Smooth command slew (start moving at t=0.6s)
        if not self._is_jump_bit_on(now_start):
            h_step = np.clip(self.h_nom - self.height_cmd, -0.06 * CONTROL_DT, 0.06 * CONTROL_DT)
            self.height_cmd = float(np.clip(self.height_cmd + h_step, 0.20, 0.42))

        vx_goal = self.v_cmd_target if now_start >= 0.6 else 0.0
        wz_goal = self.wz_cmd_target if now_start >= 0.6 else 0.0
        alpha = CONTROL_DT / 0.24
        self.cmd_vx += (vx_goal - self.cmd_vx) * alpha
        self.cmd_wz += (wz_goal - self.cmd_wz) * alpha

        step_guide_f = 0.0
        step_chassis_f = 0.0
        step_hurdle_hit_f = 0.0
        step_wheel_f_sum = 0.0
        step_air_rim_max = 0.0
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

            f_wheel = f_guide = f_chassis = f_total = f_hurdle = 0.0
            for ci in range(self.d.ncon):
                c = self.d.contact[ci]
                g1, g2 = int(c.geom1), int(c.geom2)
                b1, b2 = int(self.m.geom_bodyid[g1]), int(self.m.geom_bodyid[g2])
                if (b1 == 0) == (b2 == 0):
                    continue
                env_g, rb = (g1, b2) if b1 == 0 else (g2, b1)
                mujoco.mj_contactForce(self.m, self.d, ci, self._local_force)
                fnorm = float(np.linalg.norm(self._local_force[:3]))
                f_total += fnorm
                if env_g in self.hurdle_gids:
                    f_hurdle += fnorm
                if rb in self.wheels:
                    f_wheel += abs(float(self._local_force[0]))
                elif rb in self.guides:
                    f_guide += fnorm
                elif rb == self.base_id:
                    f_chassis += fnorm

            step_guide_f = max(step_guide_f, f_guide)
            step_chassis_f = max(step_chassis_f, f_chassis)
            step_hurdle_hit_f = max(step_hurdle_hit_f, f_hurdle)
            step_wheel_f_sum += f_wheel

            cl = max(float(np.linalg.norm(self.d.site_xpos[u] - self.d.site_xpos[v])) for u, v in self.pairs)
            mm = max(abs(float(self.d.qpos[u] - self.d.qpos[v])) for u, v in self.mimics)
            self.max_closure_m = max(self.max_closure_m, cl)
            if cl > 0.010 or mm > 0.010:
                fell_reason = "closure_limit"
                break

            w_pos = self.d.xpos[self.wheels]
            rim_now = float((w_pos[:, 2] - WHEEL_RADIUS_M).min())
            self.last_rim_m = rim_now

            if f_total < 1.0:
                self.air_substeps += 1
                self.support_substeps = 0
                step_air_rim_max = max(step_air_rim_max, rim_now)
            else:
                self.air_substeps = 0
                if f_wheel > 5.0:
                    self.support_substeps += 1

        self.ep_guide_force_max = max(self.ep_guide_force_max, step_guide_f)
        self.ep_chassis_force_max = max(self.ep_chassis_force_max, step_chassis_f)
        self.ep_hurdle_hit_force_max = max(self.ep_hurdle_hit_force_max, step_hurdle_hit_f)

        # Action smoothness delta before updating a_prev
        da_sq = float(np.sum((act_clipped - self.a_prev) ** 2))
        self.a_prev = act_clipped.copy()

        now = float(self.d.time)
        root_z = float(self.d.qpos[2])
        root_vz = float(self.d.qvel[2])
        R = self.d.xmat[self.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wx, wy, wz = float(self.d.qvel[3]), float(self.d.qvel[4]), float(self.d.qvel[5])
        vx_now = self.body_vx

        if not fell_reason and (self.cos_tilt < 0.50 or root_z < 0.12):
            fell_reason = "fall_guard"

        # ---------------- Anti-Cheat RL Reward Computation ----------------
        reward = 0.0
        jump_on = self._is_jump_bit_on(now)
        dt_w = now - self.window_t0 if self.cur_window_idx >= 0 else 99.0

        # 1. Alive + Attitude & Smoothness base
        reward += 0.6 * CONTROL_DT
        reward -= 0.35 * CONTROL_DT * (roll ** 2 * 8.0 + wx ** 2 * 0.08)
        reward -= 0.0025 * da_sq

        if jump_on:
            if not self.window_launched and not self.window_landed:
                self.window_crouch_min_z = min(self.window_crouch_min_z, root_z)
                # Crouch preload window (first 0.48s with wheels grounded)
                if dt_w < 0.48 and self.support_substeps >= 2:
                    crouch_err = (root_z - 0.186) / 0.030
                    reward += 1.4 * CONTROL_DT * math.exp(-(crouch_err ** 2))
                    reward += 0.6 * CONTROL_DT * math.exp(-((vx_now - self.cmd_vx) ** 2) / 0.22)

                # Confirm genuine upward liftoff
                if self.air_substeps >= 4 and root_vz > 0.25 and self.window_crouch_min_z < 0.230:
                    self.window_launched = True
                    crouch_depth_bonus = np.clip((0.232 - max(0.182, self.window_crouch_min_z)) / 0.045, 0.0, 1.1)
                    reward += 1.6 * float(crouch_depth_bonus)

            if self.window_launched and not self.window_landed:
                if self.air_substeps >= 1:
                    self.window_peak_rim = max(self.window_peak_rim, step_air_rim_max)
                    self.ep_peak_rim_m = max(self.ep_peak_rim_m, step_air_rim_max)
                    # Dense clearance + leg tuck at apex + tight airborne pitch/roll
                    q_l = self.d.qpos[self.active_qadr[:4]]
                    cur_delta = 0.5 * float((q_l[0] - q_l[1]) + (q_l[2] - q_l[3]))
                    tuck_factor = np.clip((1.20 - cur_delta) / 0.85, 0.2, 1.2)
                    reward += 3.2 * CONTROL_DT * np.clip(step_air_rim_max / 0.34, 0.0, 1.2) * float(tuck_factor)
                    reward += 1.6 * CONTROL_DT * math.exp(-((pitch / 0.11) ** 2) - ((roll / 0.06) ** 2))
                    reward -= 0.06 * CONTROL_DT * (wy ** 2)
                elif self.support_substeps >= 2 and dt_w > 0.20:
                    # Clean bilateral wheel touchdown! Award anti-cheat peak clearance bonus ONLY upon upright wheel landing!
                    self.window_landed = True
                    self.window_land_time = now
                    if abs(pitch) < math.radians(22.0) and step_guide_f < 1.0 and step_chassis_f < 1.0:
                        self.ep_completed_jumps += 1
                        clr_score = float(np.clip((self.window_peak_rim - 0.18) / 0.16, 0.0, 1.25))
                        flat_mult = math.exp(-((pitch / 0.22) ** 2))
                        reward += 9.5 * (clr_score ** 1.2) * flat_mult

            if self.window_landed:
                # Skyhook landing absorption & cruise recovery window
                reward -= 3.5 * CONTROL_DT * (math.sin(pitch) ** 2) - 0.10 * CONTROL_DT * (wy ** 2)
                if now - self.window_land_time >= 0.22:
                    reward += 1.5 * CONTROL_DT * math.exp(-((vx_now - self.cmd_vx) ** 2) / 0.20)
        else:
            # Anti-cheat refusal-to-jump check on the exact step a jump window closes!
            if self.cur_window_idx >= 0 and (JUMP_GATE_DURATION_S <= dt_w < JUMP_GATE_DURATION_S + CONTROL_DT - 1e-6):
                if self.window_peak_rim < 0.22:
                    reward -= 8.0
            # Normal cruise tracking
            reward += 1.4 * CONTROL_DT * math.exp(-((vx_now - self.cmd_vx) ** 2) / 0.20)
            reward += 0.5 * CONTROL_DT * math.exp(-((wz - self.cmd_wz) ** 2) / 0.35)
            reward -= 2.0 * CONTROL_DT * (math.sin(pitch) ** 2)

        # Hurdle crossing bonus (zero-collision clean clear!)
        w_min_x = float(self.d.xpos[self.wheels, 0].min())
        for h_i, (hx, _hz) in enumerate(self.active_hurdles):
            if h_i not in self.cleared_hurdles and w_min_x > hx + 0.18:
                self.cleared_hurdles.add(h_i)
                if self.ep_hurdle_hit_force_max < 1.0:
                    reward += 5.0

        # Smooth proportional anti-scrape / collision penalties (avoids exploration cliff!)
        if step_guide_f > 1.0 or step_chassis_f > 1.0:
            f_nonwheel = step_guide_f + step_chassis_f
            reward -= 0.25 + 0.0008 * min(f_nonwheel, 2000.0)
        if step_hurdle_hit_f > 2.0:
            reward -= 0.50 + 0.0006 * min(step_hurdle_hit_f, 2500.0)

        done = False
        if fell_reason:
            reward -= 8.0
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
            "ep_peak_rim_cm": round(self.ep_peak_rim_m * 100.0, 2),
            "ep_completed_jumps": self.ep_completed_jumps,
            "ep_expected_jumps": len(self.jump_times),
            "ep_guide_force_N": round(self.ep_guide_force_max, 2),
            "ep_chassis_force_N": round(self.ep_chassis_force_max, 2),
            "ep_hurdle_hit_N": round(self.ep_hurdle_hit_force_max, 2),
            "hurdles_cleared": len(self.cleared_hurdles),
            "hurdles_total": len(self.active_hurdles),
            "max_closure_mm": round(self.max_closure_m * 1000.0, 3),
        }
        return {"obs": obs, "hist": hist, "priv": priv}, float(reward), done, info


class SubprocVecJumpEnv:
    """Parallel GIL-releasing ThreadPool MuJoCo environment (zero Windows spawn pagefile overhead)."""

    def __init__(self, num_envs: int = 12, base_seed: int = 1000):
        self.num_envs = num_envs
        xml_path = ensure_rl_scene_xml()
        self.envs = [Mod4v3RLJumpEnv(seed=base_seed + i * 97, xml_path=xml_path) for i in range(num_envs)]
        self.dr_scale = 0.0
        self.pool = ThreadPoolExecutor(max_workers=min(num_envs, 12))
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

    def _step_one(self, pair: tuple[Mod4v3RLJumpEnv, np.ndarray]) -> tuple[dict[str, np.ndarray], float, bool, dict]:
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

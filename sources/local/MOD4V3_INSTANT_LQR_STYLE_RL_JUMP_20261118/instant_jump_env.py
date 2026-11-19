# SPDX-License-Identifier: MIT
"""400Hz MuJoCo Environment & Persistent Multi-Process VecEnv for Instant Serial-LQR-Style Pure-RL Jump.

Exact MOD4v3_HW300N60_R3 Physics Contract:
  - scene.xml SHA256 == 77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f
  - 400 Hz physics (dt = 0.0025s), 50 Hz policy (decim = 8)
  - 100 Hz leg PD (Kp = 60, Kd = 2), 400 Hz wheel velocity damping (Kv = 0.6)
  - Action clip [-6, 6], GATE_STEPS = 45 (0.90s crisp jump window on obs[30])
  - ZERO privileged inputs in standard 35-D actor observation!
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import sys
from typing import Any
import xml.etree.ElementTree as ET

import mujoco
import numpy as np
import torch

from moe_instant_jump_model import (
    ACT_DIM,
    ACTION_CLIP,
    GATE_STEPS,
    HERE,
    JUMP_GATE_DURATION_S,
    JUMP_MODE_BIT_INDEX,
    OBS_DIM,
    PRIV_CRITIC_DIM,
    REPO,
)

OLD_DELIVERY = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
XML_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/mjcf/scene.xml"
RUNTIME_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/runtime_config.json"
SEMANTICS_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/semantics.json"
BANK_SOURCE = OLD_DELIVERY / "plant/reset_bank.json"
TEMPLATE_SOURCE = OLD_DELIVERY / "runtime/core/template_spec.json"

EXPECTED_XML_SHA256 = "77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f"
WHEEL_RADIUS_M = 0.0625
FRONT_BUMPER_OFFSET_M = 0.305

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


def verify_plant_sha256() -> str:
    raw = XML_SOURCE.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_XML_SHA256:
        raise RuntimeError(f"scene.xml SHA256 mismatch: expected {EXPECTED_XML_SHA256}, got {sha}")
    return sha


def ensure_instant_jump_scene_xml(cache_dir: Path | None = None) -> Path:
    """Create OS-local arena XML preserving 100% identical MOD4v3 robot dynamics & contacts."""
    verify_plant_sha256()
    if cache_dir is None:
        cache_dir = HERE / "runtime_scenes"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os_tag = "win" if platform.system().lower().startswith("win") else "linux"
    out_xml = cache_dir / f"mod4v3_instant_jump_arena_{os_tag}.xml"
    mesh_dir_str = str(XML_SOURCE.parent / "assets")
    if out_xml.exists():
        try:
            if mesh_dir_str in out_xml.read_text(encoding="utf-8"):
                return out_xml
        except OSError:
            pass

    tree = ET.parse(XML_SOURCE)
    root = tree.getroot()
    root.find("compiler").set("meshdir", mesh_dir_str)
    vis_global = root.find("visual/global")
    if vis_global is not None:
        vis_global.set("offwidth", "1440")
        vis_global.set("offheight", "900")

    asset = root.find("asset")
    ET.SubElement(
        asset,
        "texture",
        name="ijump_grid",
        type="2d",
        builtin="checker",
        rgb1=".15 .19 .24",
        rgb2=".20 .25 .31",
        width="512",
        height="512",
        mark="edge",
        markrgb=".29 .37 .46",
    )
    ET.SubElement(
        asset,
        "material",
        name="ijump_floor_mat",
        texture="ijump_grid",
        texrepeat="28 28",
        texuniform="true",
        reflectance="0.05",
    )

    world = root.find("worldbody")
    ground = world.find("geom[@name='ground']")
    if ground is not None:
        ground.set("size", "35 35 .1")
        ground.set("material", "ijump_floor_mat")

    for half_m in range(-2, 28):
        x_val = 0.5 * half_m
        is_zero = half_m == 0
        is_int = half_m % 2 == 0
        rgba = ".25 .86 .98 .88" if is_zero else (".42 .56 .70 .58" if is_int else ".28 .36 .45 .36")
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

    for h_cm, rgba in (
        (15, ".38 .82 .52 .42"),
        (20, ".96 .78 .26 .48"),
        (24, ".98 .52 .28 .52"),
        (40, ".42 .78 .98 .45"),
    ):
        ET.SubElement(
            world,
            "geom",
            name=f"h_ref_{h_cm}cm",
            type="box",
            pos=f"4.5 0.85 {h_cm / 100.0:.3f}",
            size="9.5 0.006 0.003",
            contype="0",
            conaffinity="0",
            rgba=rgba,
            group="1",
        )

    step_colors = (".26 .52 .70 1", ".70 .46 .26 1")
    lip_colors = (".38 .88 .98 1", ".98 .78 .32 1")
    for idx in range(2):
        s_body = ET.SubElement(
            world,
            "body",
            name=f"dyn_step_body_{idx}",
            mocap="true",
            pos=f"{18.0 + 3.0 * idx:.2f} 0 -2.0",
        )
        ET.SubElement(
            s_body,
            "geom",
            name=f"dyn_step_{idx}",
            type="box",
            pos="0 0 0",
            size="3.00 1.05 0.25",
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
            pos="-2.988 0 0.245",
            size="0.012 1.052 0.005",
            contype="0",
            conaffinity="0",
            rgba=lip_colors[idx],
            group="1",
        )

    tmp_xml = cache_dir / f"mod4v3_instant_jump_arena_{os_tag}_{os.getpid()}.tmp.xml"
    tree.write(tmp_xml, encoding="utf-8", xml_declaration=True)
    os.replace(tmp_xml, out_xml)
    return out_xml


class Mod4v3InstantJumpEnv:
    """Single-instance 400Hz MuJoCo Environment for Instant Jump, Step-Vault, 2-Step & Drop-Off."""

    def __init__(self, seed: int = 0, xml_path: Path | None = None):
        torch.set_num_threads(1)
        self.rng = np.random.default_rng(seed)
        self.xml_path = xml_path or ensure_instant_jump_scene_xml()

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

        self.active_steps: list[tuple[float, float, float]] = []
        self.scenario_kind = "flat"
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

        com_shift = self.rng.uniform(-0.018 * s, 0.018 * s, size=3)
        self.m.body_ipos[self.base_id] = self.nom_body_ipos[self.base_id] + com_shift

        mu = float(self.rng.uniform(0.90 - 0.28 * s, 0.90 + 0.28 * s))
        self.cur_friction = mu
        for gid in [self.ground_gid, *self.tire_gids, *self.step_gids]:
            self.m.geom_friction[gid, 0] = mu

        self.kp_scale = self.rng.uniform(1.0 - 0.10 * s, 1.0 + 0.10 * s, size=4).astype(np.float32)
        self.kd_scale = self.rng.uniform(1.0 - 0.10 * s, 1.0 + 0.10 * s, size=4).astype(np.float32)
        self.kv_scale = self.rng.uniform(1.0 - 0.10 * s, 1.0 + 0.10 * s, size=2).astype(np.float32)
        self.effort_scale = self.rng.uniform(1.0 - 0.08 * s, 1.0 + 0.08 * s, size=6).astype(np.float32)
        self.delay_substeps = int(self.rng.integers(0, int(round(6 * s)) + 1))
        mujoco.mj_setConst(self.m, self.d)

    def configure_steps(self, steps: list[tuple[float, float, float]]) -> None:
        self.active_steps = list(steps[:2])
        for idx in range(2):
            gid = self.step_gids[idx]
            lip_gid = self.step_lip_gids[idx]
            mid = self.step_mocap_ids[idx]
            if idx < len(self.active_steps):
                xf, lx, hz = self.active_steps[idx]
                half_x = min(3.00, lx / 2.0)
                half_z = max(0.06, hz / 2.0)
                self.m.geom_size[gid] = [half_x, 1.05, half_z]
                self.m.geom_rbound[gid] = math.sqrt(half_x**2 + 1.05**2 + half_z**2)
                self.m.geom_pos[lip_gid] = [-half_x + 0.012, 0.0, half_z - 0.005]
                self.m.geom_size[lip_gid] = [0.012, 1.052, 0.005]
                self.d.mocap_pos[mid] = [xf + half_x, 0.0, hz - half_z]
            else:
                self.d.mocap_pos[mid] = [18.0 + 3.0 * idx, 0.0, -2.0]

    def terrain_z_at(self, x: float) -> float:
        z = 0.0
        for xf, lx, hz in self.active_steps:
            if xf <= x <= xf + lx:
                z = max(z, float(hz))
        return z

    @property
    def body_vx(self) -> float:
        R = self.d.xmat[self.base_id].reshape(3, 3)
        fx, fy = float(R[0, 0]), float(R[1, 0])
        return float((self.d.qvel[0] * fx + self.d.qvel[1] * fy) / max(math.hypot(fx, fy), 1e-6))

    @property
    def body_vy(self) -> float:
        R = self.d.xmat[self.base_id].reshape(3, 3)
        lx, ly = float(R[0, 1]), float(R[1, 1])
        return float((self.d.qvel[0] * lx + self.d.qvel[1] * ly) / max(math.hypot(lx, ly), 1e-6))

    def sample_random_scenario(self, dr_scale: float) -> dict[str, np.ndarray]:
        """Diverse human-playable training curriculum across all 6 scenario families."""
        r = float(self.rng.random())
        h_jit = float(self.rng.uniform(-0.008, 0.008)) * dr_scale
        h_init = float(self.rng.choice([0.24, 0.28, 0.28, 0.28, 0.32, 0.35]))

        if r < 0.10:
            # S1: Stationary / In-Place Crisp Hop (1 or 2 hops, various heights & yaw)
            n_j = 1 if self.rng.random() < 0.65 else 2
            t1 = float(self.rng.uniform(0.65, 1.05))
            jt = (t1,) if n_j == 1 else (t1, t1 + float(self.rng.uniform(1.25, 1.55)))
            wz = float(self.rng.uniform(-0.35, 0.35)) if self.rng.random() < 0.35 else 0.0
            return self.reset(
                dr_scale=dr_scale,
                scenario_kind="flat_stat",
                v_cmd=0.0,
                v_jump=0.0,
                v_cmd_post=0.0,
                wz_cmd=wz,
                h_nom=h_init,
                jump_times=jt,
                max_episode_s=jt[-1] + 1.8,
                steps=[],
            )
        if r < 0.20:
            # S2: Moving Flat Single & Consecutive Multi-Hop
            vp = float(self.rng.uniform(0.45, 1.50))
            n_j = 2 if self.rng.random() < 0.65 else 1
            t1 = float(self.rng.uniform(0.85, 1.20))
            jt = (t1,) if n_j == 1 else (t1, t1 + float(self.rng.uniform(1.25, 1.55)))
            wz = float(self.rng.uniform(-0.40, 0.40)) if self.rng.random() < 0.30 else 0.0
            return self.reset(
                dr_scale=dr_scale,
                scenario_kind="flat_move",
                v_cmd=vp,
                v_jump=vp,
                v_cmd_post=vp,
                wz_cmd=wz,
                h_nom=h_init,
                jump_times=jt,
                max_episode_s=jt[-1] + 1.8,
                steps=[],
            )
        if r < 0.40:
            # S3: Near-Step Space+W (standstill or slow approach up to 15/20/24cm step!)
            vp = 0.0 if self.rng.random() < 0.25 else float(self.rng.uniform(0.28, 0.42))
            vj = float(self.rng.uniform(0.90, 1.15))
            vpost = vj if self.rng.random() < 0.80 else 0.0
            sh = float(self.rng.choice([0.15, 0.20, 0.20, 0.24])) + h_jit
            dw = float(self.rng.uniform(0.43, 0.58))
            if vp == 0.0:
                return self.reset(
                    dr_scale=dr_scale,
                    scenario_kind="near_step",
                    v_cmd=0.0,
                    v_jump=vj,
                    v_cmd_post=vpost,
                    post_cmd_switch_s=2.25 if vpost == 0.0 else None,
                    h_nom=0.28,
                    jump_times=(0.65,),
                    stand_step_dw=(dw, sh),
                    max_episode_s=3.4,
                    steps=[(9.0, 5.5, sh)],
                )
            xf = 0.15 + vp * 0.85 + dw
            return self.reset(
                dr_scale=dr_scale,
                scenario_kind="near_step",
                v_cmd=vp,
                v_jump=vj,
                v_cmd_post=vpost,
                post_cmd_switch_s=2.65 if vpost == 0.0 else None,
                h_nom=0.28,
                jump_times=(),
                step_trigger_dws=[(0, dw)],
                max_episode_s=3.6,
                steps=[(xf, 5.5, sh)],
            )
        if r < 0.76:
            # S4: Moving W+Space onto 15/20/24cm Step across exact human takeoff window!
            vc = float(self.rng.uniform(0.55, 1.45))
            vpost = vc if self.rng.random() < 0.85 else 0.0
            sh = float(self.rng.choice([0.15, 0.20, 0.20, 0.24, 0.24])) + h_jit
            dw_min = 0.39 + 0.07 * vc
            dw_max = 0.71 + 0.07 * vc
            dw = float(self.rng.uniform(dw_min, dw_max))
            xf = 0.15 + vc * 0.90 + dw
            return self.reset(
                dr_scale=dr_scale,
                scenario_kind="move_step",
                v_cmd=vc,
                v_jump=vc,
                v_cmd_post=vpost,
                post_cmd_switch_s=2.85 if vpost == 0.0 else None,
                h_nom=0.28,
                jump_times=(),
                step_trigger_dws=[(0, dw)],
                max_episode_s=3.6,
                steps=[(xf, 5.8, sh)],
            )
        if r < 0.92:
            # S5: Continuous 20cm -> 40cm 2-Step Stair Vault (2 consecutive Space presses!)
            vc = float(self.rng.uniform(0.78, 0.98))
            dw1 = float(self.rng.uniform(0.47, 0.59))
            dw2 = float(self.rng.uniform(0.47, 0.59))
            tread = float(self.rng.uniform(1.50, 1.66))
            xf1 = 0.20 + vc * 0.85 + dw1
            xf2 = xf1 + tread
            return self.reset(
                dr_scale=dr_scale,
                scenario_kind="two_step",
                v_cmd=vc,
                v_jump=vc,
                v_cmd_post=vc,
                post_cmd_switch_s=None,
                h_nom=0.28,
                jump_times=(),
                step_trigger_dws=[(0, dw1), (1, dw2)],
                max_episode_s=4.7,
                steps=[(xf1, tread + 0.05, 0.20 + h_jit), (xf2, 4.5, 0.40 + h_jit)],
            )
        # S6: Platform Jump-Down / Drop-Off (20 / 30 / 40 cm elevated start -> drop to 0cm ground!)
        dh = float(self.rng.choice([0.20, 0.30, 0.40]))
        vc = float(self.rng.uniform(0.65, 1.15))
        return self.reset(
            dr_scale=dr_scale,
            scenario_kind="drop_off",
            v_cmd=vc,
            v_jump=vc,
            v_cmd_post=vc,
            h_nom=0.28,
            jump_times=(),
            drop_trigger_x=0.95,
            max_episode_s=3.5,
            steps=[(-0.60, 1.80, dh)],
        )

    def reset(
        self,
        dr_scale: float = 0.0,
        scenario_kind: str = "flat",
        v_cmd: float = 0.0,
        v_jump: float | None = None,
        v_cmd_post: float | None = None,
        post_cmd_switch_s: float | None = None,
        wz_cmd: float = 0.0,
        h_nom: float = 0.28,
        jump_times: tuple[float, ...] = (0.9,),
        step_trigger_dws: list[tuple[int, float]] | None = None,
        stand_step_dw: tuple[float, float] | None = None,
        drop_trigger_x: float | None = None,
        max_episode_s: float = 3.8,
        steps: list[tuple[float, float, float]] | None = None,
        init_pose: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> dict[str, np.ndarray]:
        mujoco.mj_resetData(self.m, self.d)
        self._apply_dr(dr_scale)
        self.scenario_kind = scenario_kind
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

        self.v_cmd_pre = float(v_cmd)
        self.v_jump = float(v_cmd if v_jump is None else v_jump)
        self.v_cmd_post = float(self.v_jump if v_cmd_post is None else v_cmd_post)
        self.post_cmd_switch_s = post_cmd_switch_s
        self.wz_cmd_target = float(wz_cmd)
        self.h_nom = float(h_nom)
        self.jump_times = tuple(float(t) for t in jump_times)
        self.step_trigger_dws = list(step_trigger_dws or [])
        self.fired_step_triggers: set[int] = set()
        self.stand_step_dw = stand_step_dw
        self.drop_trigger_x = drop_trigger_x
        self.drop_fired = False
        self.max_episode_s = float(max_episode_s)

        self.cmd_vx = 0.0
        self.cmd_vy = 0.0
        self.cmd_wz = 0.0
        self.height_cmd = 0.28
        self.a_prev = np.zeros(ACT_DIM, dtype=np.float32)
        self.action_delay_fifo: deque[np.ndarray] = deque(
            [np.zeros(ACT_DIM, dtype=np.float32) for _ in range(self.delay_substeps + 1)],
            maxlen=self.delay_substeps + 1,
        )

        self.jump_rem_steps = 0
        self.jump_count = 0
        self.fired_time_triggers: set[int] = set()
        self.air_substeps = 0
        self.support_substeps = 8
        self.max_closure_m = 0.0
        self.last_world_rim_m = g_z0

        # Active jump window metrics
        self.window_active = False
        self.window_t0 = -99.0
        self.window_wx0 = x0
        self.window_g0 = g_z0
        self.window_tau0 = np.zeros(4, dtype=np.float64)
        self.window_tau_latency_ms: float | None = None
        self.window_lift_latency_ms: float | None = None
        self.window_liftoff_wx: float | None = None
        self.window_touchdown_wx: float | None = None
        self.window_land_time = -99.0
        self.window_launched = False
        self.window_landed = False
        self.window_peak_rel_rim = 0.0
        self.window_peak_world_rim = g_z0
        self.window_max_air_pitch_deg = 0.0

        # Episode aggregates
        self.completed_jumps: list[dict[str, float]] = []
        self.steps_mounted = [False for _ in self.active_steps]
        self.steps_rewarded = [False for _ in self.active_steps]
        self.slid_off_step = False
        self.drop_landed_ok = False
        self.ep_guide_force_max = 0.0
        self.ep_chassis_force_max = 0.0
        self.ep_riser_hit_force_max = 0.0
        self.ep_max_air_pitch_deg = 0.0
        self.ep_max_episode_pitch_deg = 0.0

        self.prepare_step_commands()
        return {"obs": self._compute_obs(), "priv": self._compute_priv()}

    def _trigger_jump_window(self, now: float) -> None:
        wx_now = float(self.d.xpos[self.wheels, 0].mean())
        if self.stand_step_dw is not None and self.jump_count == 0:
            dw, sh = self.stand_step_dw
            self.configure_steps([(wx_now + dw, 5.5, sh)])
            mujoco.mj_forward(self.m, self.d)
        self.jump_rem_steps = GATE_STEPS
        self.jump_count += 1
        self.window_active = True
        self.window_t0 = now
        self.window_wx0 = wx_now
        self.window_g0 = self.terrain_z_at(wx_now)
        self.window_tau0 = self.d.ctrl[self.act_ids[:4]].copy()
        self.window_tau_latency_ms = None
        self.window_lift_latency_ms = None
        self.window_liftoff_wx = None
        self.window_touchdown_wx = None
        self.window_land_time = -99.0
        self.window_launched = False
        self.window_landed = False
        self.window_peak_rel_rim = 0.0
        self.window_peak_world_rim = self.window_g0
        self.window_max_air_pitch_deg = 0.0

    def _update_triggers(self, now: float) -> bool:
        wx_now = float(self.d.xpos[self.wheels, 0].mean())
        if self.jump_rem_steps <= 0 and now >= 0.45:
            for ti, tj in enumerate(self.jump_times):
                if ti not in self.fired_time_triggers and now >= tj - 1e-6:
                    self.fired_time_triggers.add(ti)
                    self._trigger_jump_window(now)
                    break
        if self.jump_rem_steps <= 0 and now >= 0.45:
            for s_idx, dw in self.step_trigger_dws:
                if s_idx not in self.fired_step_triggers and s_idx < len(self.active_steps):
                    xf = self.active_steps[s_idx][0]
                    prev_ok = (s_idx == 0) or (wx_now >= self.active_steps[s_idx - 1][0] + 0.08)
                    if prev_ok and (xf - wx_now) <= dw:
                        self.fired_step_triggers.add(s_idx)
                        self._trigger_jump_window(now)
                        break
        if self.jump_rem_steps <= 0 and self.drop_trigger_x is not None and not self.drop_fired and now >= 0.45:
            if wx_now >= self.drop_trigger_x:
                self.drop_fired = True
                self._trigger_jump_window(now)

        if self.jump_rem_steps > 0:
            return True
        if self.window_active:
            self.window_active = False
        return False

    def _compute_obs(self) -> np.ndarray:
        """Standard 35-D proprioceptive observation (ZERO world-z / step-height / step-distance!)."""
        jump_on = self.jump_rem_steps > 0
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
        """18-D training-only privileged vector fed EXCLUSIVELY to AsymmetricInstantJumpCritic."""
        now = float(self.d.time)
        wx_now = float(self.d.xpos[self.wheels, 0].mean())
        g_now = self.terrain_z_at(wx_now)
        dt_trig = min(1.5, max(0.0, now - self.window_t0)) if self.window_t0 > -10.0 else 1.5
        step_dx, step_h = 3.0, 0.0
        for xf, lx, hz in self.active_steps:
            if xf + lx > wx_now - 0.1 and abs(hz - g_now) > 0.02:
                step_dx = float(np.clip(xf - wx_now, -1.0, 3.0))
                step_h = float(hz - g_now)
                break
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
                float(self.jump_rem_steps) / float(GATE_STEPS),
                float(self.window_launched),
                float(self.window_landed),
                self.window_peak_rel_rim,
                wx_now - self.window_wx0,
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

    def prepare_step_commands(self) -> None:
        """Advance command slews & trigger state prior to computing obs for actor."""
        now = float(self.d.time)
        self._update_triggers(now)
        if now < 0.20:
            vx_goal = 0.0
        elif self.post_cmd_switch_s is not None and now >= self.post_cmd_switch_s:
            vx_goal = self.v_cmd_post
        elif self.jump_count > 0:
            vx_goal = self.v_jump
        else:
            vx_goal = self.v_cmd_pre
        wz_goal = self.wz_cmd_target if now >= 0.25 else 0.0

        alpha = CONTROL_DT / 0.14
        self.cmd_vx += (vx_goal - self.cmd_vx) * alpha
        self.cmd_wz += (wz_goal - self.cmd_wz) * alpha
        h_step = np.clip(self.h_nom - self.height_cmd, -0.14 * CONTROL_DT, 0.14 * CONTROL_DT)
        self.height_cmd = float(np.clip(self.height_cmd + h_step, 0.20, 0.40))

    def step(self, action_ppo: np.ndarray) -> tuple[dict[str, np.ndarray], float, bool, dict[str, Any]]:
        if self.jump_rem_steps > 0:
            self.jump_rem_steps -= 1
        act_clipped = np.clip(np.asarray(action_ppo, dtype=np.float32).reshape(ACT_DIM), -ACTION_CLIP, ACTION_CLIP)
        a_env_now = act_clipped[self.ppo_to_env_np]

        step_guide_f = step_chassis_f = step_riser_f = 0.0
        fell_reason = ""
        just_launched = False
        just_landed = False

        for j in range(self.decim):
            self.action_delay_fifo.append(a_env_now)
            a_applied = self.action_delay_fifo[0]
            tau = self._compute_motor_torque(a_applied)
            if j % 4 == 0:
                self.d.ctrl[self.act_ids[:4]] = tau[:4]
                if (
                    self.window_active
                    and self.window_tau_latency_ms is None
                    and np.max(np.abs(tau[:4] - self.window_tau0)) > 4.0
                ):
                    self.window_tau_latency_ms = max(0.0, (float(self.d.time) - self.window_t0) * 1000.0)
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
                if (b1 in self.env_body_ids) == (b2 in self.env_body_ids):
                    continue
                env_g, rb = (g1, b2) if (b1 in self.env_body_ids) else (g2, b1)
                mujoco.mj_contactForce(self.m, self.d, ci, self._local_force)
                fnorm = float(np.linalg.norm(self._local_force[:3]))
                f_total += fnorm

                if env_g in self.step_gids:
                    s_idx = self.step_gids.index(env_g)
                    top_z = self.active_steps[s_idx][2] if s_idx < len(self.active_steps) else 0.0
                    is_top = abs(float(c.frame[2])) >= 0.72 and float(c.pos[2]) >= top_z - 0.018
                    if rb in self.wheels and is_top:
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
            step_riser_f = max(step_riser_f, f_riser)

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

            if f_total < 1.0:
                self.air_substeps += 1
                self.support_substeps = 0
                if self.window_active and not self.window_launched and self.air_substeps >= 2 and self.d.qvel[2] > 0.20:
                    self.window_launched = True
                    just_launched = True
                    self.window_lift_latency_ms = max(0.0, (float(self.d.time) - self.window_t0) * 1000.0)
                    self.window_liftoff_wx = float(w_pos[:, 0].mean())
                if self.window_launched and not self.window_landed and (float(self.d.time) - self.window_t0) <= 0.68:
                    self.window_peak_world_rim = max(self.window_peak_world_rim, world_rim_now)
                    self.window_peak_rel_rim = max(self.window_peak_rel_rim, world_rim_now - self.window_g0)
                    self.window_max_air_pitch_deg = max(self.window_max_air_pitch_deg, sub_pitch_deg)
                    self.ep_max_air_pitch_deg = max(self.ep_max_air_pitch_deg, sub_pitch_deg)
            else:
                if (
                    self.window_launched
                    and not self.window_landed
                    and f_wheel > 8.0
                    and (float(self.d.time) - self.window_t0) > 0.14
                ):
                    self.window_landed = True
                    just_landed = True
                    self.window_land_time = float(self.d.time)
                    self.window_touchdown_wx = float(w_pos[:, 0].mean())
                    self.completed_jumps.append(
                        {
                            "tau_ms": self.window_tau_latency_ms if self.window_tau_latency_ms is not None else 20.0,
                            "lift_ms": self.window_lift_latency_ms if self.window_lift_latency_ms is not None else 250.0,
                            "pre_dx_m": float((self.window_liftoff_wx or self.window_wx0) - self.window_wx0),
                            "leap_dx_m": float(self.window_touchdown_wx - self.window_wx0),
                            "rel_rim_cm": self.window_peak_rel_rim * 100.0,
                            "world_rim_cm": self.window_peak_world_rim * 100.0,
                            "air_pitch_deg": self.window_max_air_pitch_deg,
                        }
                    )
                self.air_substeps = 0
                if f_wheel > 5.0:
                    self.support_substeps += 1

        self.ep_guide_force_max = max(self.ep_guide_force_max, step_guide_f)
        self.ep_chassis_force_max = max(self.ep_chassis_force_max, step_chassis_f)
        self.ep_riser_hit_force_max = max(self.ep_riser_hit_force_max, step_riser_f)

        da_sq = float(np.sum((act_clipped - self.a_prev) ** 2))
        self.a_prev = act_clipped.copy()

        now = float(self.d.time)
        w_pos_end = self.d.xpos[self.wheels]
        wx_mean = float(w_pos_end[:, 0].mean())
        g_under = self.terrain_z_at(wx_mean)
        rel_z = float(self.d.qpos[2]) - g_under

        R = self.d.xmat[self.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        pitch_deg = abs(math.degrees(pitch))

        # Check step mounting & anti-cheat slide-off!
        if self.scenario_kind != "drop_off":
            for s_idx, (xf, lx, hz) in enumerate(self.active_steps):
                both_on = all(
                    (xf + 0.02 <= w_pos_end[wi, 0] <= xf + lx - 0.04)
                    and (hz - 0.018 <= w_pos_end[wi, 2] - WHEEL_RADIUS_M <= hz + 0.038)
                    for wi in (0, 1)
                )
                if both_on and self.support_substeps >= 2:
                    self.steps_mounted[s_idx] = True
                if self.steps_mounted[s_idx]:
                    if (w_pos_end[:, 2] - WHEEL_RADIUS_M).min() < hz - 0.035 or w_pos_end[:, 0].min() < xf - 0.03:
                        self.slid_off_step = True
                        fell_reason = "slid_off_step"
        else:
            if all(w_pos_end[wi, 0] >= 1.40 and abs(w_pos_end[wi, 2] - WHEEL_RADIUS_M) <= 0.03 for wi in (0, 1)) and self.support_substeps >= 3:
                self.drop_landed_ok = True

        if fell_reason == "":
            if R[2, 2] < 0.35 or abs(pitch) > 1.05 or abs(roll) > 0.95:
                fell_reason = "tipped_over"
            elif rel_z < 0.115 and self.support_substeps > 0:
                fell_reason = "collapsed"

        # Normalized, dense, well-conditioned reward shaping (episode return in [-3.5, +9.5])
        rew = 0.03
        rew -= 0.08 * max(0.0, pitch_deg - 8.0) / 10.0 + 0.28 * max(0.0, pitch_deg - 11.5) / 10.0
        rew -= 0.08 * roll * roll
        rew -= 0.0001 * da_sq
        rew -= 0.09 * min(step_riser_f / 400.0, 1.5)
        rew -= 0.10 * min((step_guide_f + step_chassis_f) / 300.0, 1.5)

        if just_launched:
            l_ms = self.window_lift_latency_ms or 250.0
            rew += 0.80 * max(0.15, min(1.0, (270.0 - l_ms) / 140.0))
            if self.v_cmd_pre <= 0.40:
                pre_dx = abs((self.window_liftoff_wx or self.window_wx0) - self.window_wx0)
                rew -= 1.20 * max(0.0, pre_dx - 0.09)

        if self.air_substeps > 0:
            rew += 0.05 * math.exp(-18.0 * pitch * pitch)
            # Dense step-lip clearance + forward vault shaping during flight!
            if self.scenario_kind != "drop_off":
                for s_idx, (xf, _lx, hz) in enumerate(self.active_steps):
                    if not self.steps_mounted[s_idx] and (xf - 0.24 <= wx_mean <= xf + 0.20):
                        lip_margin = (self.last_world_rim_m - hz + 0.04) / 0.10
                        rew += 0.20 * float(np.clip(lip_margin, -0.4, 1.2))
                        rew += 0.06 * float(np.clip(self.body_vx / max(0.8, self.v_jump), 0.0, 1.25))
                        break

        if just_landed:
            rew += 1.50 * float(np.clip((self.window_peak_rel_rim - 0.16) / 0.14, 0.0, 1.30))

        for s_idx, mnt in enumerate(self.steps_mounted):
            if mnt and not self.steps_rewarded[s_idx]:
                self.steps_rewarded[s_idx] = True
                rew += 2.80 * (1.0 + self.active_steps[s_idx][2])

        if not self.window_active or self.window_landed:
            rew += 0.05 * math.exp(-32.0 * (rel_z - self.h_nom) ** 2)
            rew += 0.05 * math.exp(-4.0 * (self.body_vx - self.cmd_vx) ** 2)

        if self.slid_off_step:
            rew -= 2.80
        elif fell_reason != "":
            rew -= 1.80

        # Prepare next step's commands & triggers BEFORE computing next obs!
        self.prepare_step_commands()
        done = (fell_reason != "") or (now >= self.max_episode_s)

        info = {
            "fell_reason": fell_reason,
            "slid_off_step": self.slid_off_step,
            "steps_mounted_count": int(sum(self.steps_mounted)),
            "steps_total": len(self.active_steps) if self.scenario_kind != "drop_off" else 0,
            "drop_landed_ok": self.drop_landed_ok,
            "completed_jumps": list(self.completed_jumps),
            "ep_guide_force_N": round(self.ep_guide_force_max, 2),
            "ep_chassis_force_N": round(self.ep_chassis_force_max, 2),
            "ep_riser_hit_N": round(self.ep_riser_hit_force_max, 2),
            "ep_max_air_pitch_deg": round(self.ep_max_air_pitch_deg, 2),
            "ep_max_episode_pitch_deg": round(self.ep_max_episode_pitch_deg, 2),
            "max_closure_mm": round(self.max_closure_m * 1000.0, 3),
            "rel_z_end": round(rel_z, 4),
            "body_vx_end": round(self.body_vx, 4),
        }
        return {"obs": self._compute_obs(), "priv": self._compute_priv()}, float(rew), bool(done), info


def _worker_loop(conn: Any, seed: int, xml_str: str) -> None:
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    torch.set_num_threads(1)
    env = Mod4v3InstantJumpEnv(seed=seed, xml_path=Path(xml_str))
    dr_scale = 0.0
    while True:
        cmd, payload = conn.recv()
        if cmd == "reset_all":
            dr_scale = float(payload)
            st = env.sample_random_scenario(dr_scale=dr_scale)
            conn.send(st)
        elif cmd == "set_dr":
            dr_scale = float(payload)
            conn.send(True)
        elif cmd == "step":
            st, rew, done, info = env.step(payload)
            if done:
                if info["fell_reason"] == "":
                    info["terminal_obs"] = st["obs"].copy()
                    info["terminal_priv"] = st["priv"].copy()
                st = env.sample_random_scenario(dr_scale=dr_scale)
            conn.send((st["obs"], st["priv"], rew, done, info))
        elif cmd == "close":
            conn.close()
            break


class ParallelInstantJumpVecEnv:
    """Persistent multi-process MuJoCo vectorized environment (bypasses GIL across 40+ CPU cores!)."""

    def __init__(self, num_envs: int = 40, base_seed: int = 1000, dr_scale: float = 0.0):
        self.num_envs = num_envs
        self.dr_scale = dr_scale
        xml_path = ensure_instant_jump_scene_xml()
        ctx = mp.get_context("spawn")
        self.conns = []
        self.procs = []
        for i in range(num_envs):
            parent_conn, child_conn = ctx.Pipe()
            p = ctx.Process(target=_worker_loop, args=(child_conn, base_seed + i * 97, str(xml_path)), daemon=True)
            p.start()
            child_conn.close()
            self.conns.append(parent_conn)
            self.procs.append(p)

    def set_dr_scale(self, dr_scale: float) -> None:
        self.dr_scale = float(dr_scale)
        for c in self.conns:
            c.send(("set_dr", self.dr_scale))
        for c in self.conns:
            c.recv()

    def reset_all(self, dr_scale: float | None = None) -> tuple[np.ndarray, np.ndarray]:
        if dr_scale is not None:
            self.dr_scale = float(dr_scale)
        for c in self.conns:
            c.send(("reset_all", self.dr_scale))
        states = [c.recv() for c in self.conns]
        obs = np.stack([s["obs"] for s in states], axis=0)
        priv = np.stack([s["priv"] for s in states], axis=0)
        return obs, priv

    def step(self, actions_np: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[dict[str, Any]]]:
        for c, act in zip(self.conns, actions_np):
            c.send(("step", act))
        res = [c.recv() for c in self.conns]
        obs = np.stack([r[0] for r in res], axis=0)
        priv = np.stack([r[1] for r in res], axis=0)
        rews = np.array([r[2] for r in res], dtype=np.float32)
        dones = np.array([r[3] for r in res], dtype=bool)
        infos = [r[4] for r in res]
        return obs, priv, rews, dones, infos

    def close(self) -> None:
        for c in self.conns:
            try:
                c.send(("close", None))
            except OSError:
                pass
        for p in self.procs:
            p.join(timeout=2.0)

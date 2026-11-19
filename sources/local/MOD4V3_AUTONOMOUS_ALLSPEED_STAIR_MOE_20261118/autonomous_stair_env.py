# SPDX-License-Identifier: MIT
"""400Hz MuJoCo Environment for Autonomous All-Speed Stair Climb & Zero-False-Positive Routing.

Exact Hardware & Physics Contract:
  - Plant: MOD4v3 / HW300N60_R3 (`scene.xml` SHA256 = `77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f`)
  - 400Hz physics (`dt = 0.0025s`), 100Hz leg PD (`60/2`), 400Hz wheel servo (`0.6`), 50Hz policy (`decim = 8`),
    `[-6.0, 6.0]` action clip, 2000 N/m closed-chain 4-bar springs.
  - Zero-reload unified MJCF arena supporting:
      * Single steps (`10cm / 15cm / 20cm` + DR heights) across `[0.40, 1.70] m/s` & `h_cmd in [0.25, 0.38] m`
      * Post-climb `W`-release (`cmd_vx -> 0.0` right after mounting)
      * Continuous 2-step (`20cm + 20cm = 40cm`, `1.5m` tread)
      * Negative scenarios (`target_gate = 0.0`): flat start/sprint/hard-brake/reverse/yaw-turn/height-sweep,
        smooth `10°` & `17°` ramps (up & down), `±3.5cm` rough wavy/gravel hfield, and `-10cm / -20cm` step-down!
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any
import xml.etree.ElementTree as ET

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import mujoco as mj
import numpy as np
import torch

from autonomous_stair_moe_model import (
    ACT_DIM,
    ACTION_CLIP,
    GATE_DEADZONE,
    HIST_DIM,
    HIST_LEN,
    OBS_DIM,
    PRIV_CRITIC_DIM,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
D_BEST = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
PLANT = D_BEST / "plant/MOD4v3_HW300N60_R3"
E_TEACH = REPO / "sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1"

XML_SOURCE = PLANT / "mjcf/scene.xml"
RUNTIME_SOURCE = PLANT / "runtime_config.json"
SEMANTICS_SOURCE = PLANT / "semantics.json"
BANK_SOURCE = D_BEST / "plant/reset_bank.json"
TEMPLATE_SOURCE = D_BEST / "runtime/core/template_spec.json"
EXPECTED_XML_SHA256 = "77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f"

for p_s in [str(D_BEST / "runtime/core"), str(E_TEACH), str(E_TEACH / "sim"), str(E_TEACH.parent)]:
    if p_s not in sys.path:
        sys.path.insert(0, p_s)

from mod4_retarget import Mod4Retarget  # noqa: E402
from play_mod4v3 import (  # noqa: E402
    Mod4v3Mujoco,
    RobotSpec,
    _q_from_bank,
    _q_from_runtime,
)

PPO_TO_NATIVE = np.array([0, 2, 1, 3, 4, 5], dtype=np.int64)
NAMES = [
    "left_front1_joint",
    "right_front1_joint",
    "left_rear1_joint",
    "right_rear1_joint",
    "left_wheel_joint",
    "right_wheel_joint",
]

STEP_HALF_X = 5.50
STEP_HALF_Y = 1.60
STEP_HALF_Z = 0.25
RAMP_HALF_X = 2.50
RAMP_HALF_Y = 1.40
RAMP_HALF_Z = 0.20

ROUGH_CENTER_X = 3.0
ROUGH_CENTER_Y = 12.0
ROUGH_HALF_X = 6.0
ROUGH_HALF_Y = 3.5
ROUGH_NROW = 71
ROUGH_NCOL = 121
ROUGH_SPAN_Z = 0.070  # ±3.5 cm peak-to-peak

_SHARED_ARENA_ASSETS: dict[str, Any] | None = None


def ensure_autonomous_stair_arena_xml(cache_dir: Path | None = None) -> Path:
    """Create local unified MJCF preserving exact HW300N60_R3 robot physics + mocap steps/ramps + rough hfield."""
    xml_sha = hashlib.sha256(XML_SOURCE.read_bytes()).hexdigest()
    if xml_sha != EXPECTED_XML_SHA256:
        raise RuntimeError(f"MJCF SHA256 mismatch: {xml_sha}")

    if cache_dir is None:
        cache_dir = HERE / "runtime_scenes"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_xml = cache_dir / f"mod4v3_autonomous_stair_arena_v2_{os.name}.xml"
    expected_meshdir = str(XML_SOURCE.parent / "assets")
    if out_xml.exists():
        try:
            if ET.parse(out_xml).getroot().find("compiler").get("meshdir") == expected_meshdir:
                return out_xml
        except Exception:
            pass

    tree = ET.parse(XML_SOURCE)
    root = tree.getroot()
    root.find("compiler").set("meshdir", str(XML_SOURCE.parent / "assets"))
    vis_global = root.find("visual/global")
    if vis_global is not None:
        vis_global.set("offwidth", "1280")
        vis_global.set("offheight", "720")

    asset = root.find("asset")
    ET.SubElement(
        asset,
        "texture",
        name="arena_grid",
        type="2d",
        builtin="checker",
        rgb1=".17 .21 .26",
        rgb2=".22 .27 .34",
        width="512",
        height="512",
        mark="edge",
        markrgb=".32 .40 .48",
    )
    ET.SubElement(
        asset,
        "material",
        name="arena_floor_mat",
        texture="arena_grid",
        texrepeat="24 12",
        texuniform="true",
        reflectance="0.04",
    )
    ET.SubElement(
        asset,
        "hfield",
        name="rough_hfield",
        nrow=str(ROUGH_NROW),
        ncol=str(ROUGH_NCOL),
        size=f"{ROUGH_HALF_X} {ROUGH_HALF_Y} {ROUGH_SPAN_Z} 0.20",
    )

    world = root.find("worldbody")
    ground = world.find("geom[@name='ground']")
    if ground is not None:
        # Keep main flat lane at y in [-6, +6] so rough hfield at y in [8.5, 15.5] is disjoint!
        ground.set("type", "box")
        ground.set("pos", "6.0 0.0 -0.10")
        ground.set("size", "22.0 6.0 0.10")
        ground.set("material", "arena_floor_mat")

    # Visual distance markers every 0.5m along the main lane
    for half_m in range(-2, 24):
        xv = 0.5 * half_m
        rgba = ".25 .85 .98 .80" if half_m == 0 else (".40 .54 .68 .50" if half_m % 2 == 0 else ".28 .35 .44 .32")
        ET.SubElement(
            world,
            "geom",
            name=f"x_mark_{half_m:+d}",
            type="box",
            pos=f"{xv:.2f} 0 0.0008",
            size="0.006 1.50 0.0008",
            contype="0",
            conaffinity="0",
            rgba=rgba,
            group="1",
        )

    # 2 Mocap solid 3D step platforms (parked underground at z=-2.0 when inactive)
    step_colors = (".28 .48 .66 1", ".36 .58 .76 1")
    lip_colors = (".38 .88 .98 1", ".98 .82 .32 1")
    for idx in range(2):
        sb = ET.SubElement(world, "body", name=f"dyn_step_body_{idx}", mocap="true", pos=f"{16.0 + 5.0 * idx:.2f} 0 -2.0")
        ET.SubElement(
            sb,
            "geom",
            name=f"dyn_step_{idx}",
            type="box",
            pos="0 0 0",
            size=f"{STEP_HALF_X} {STEP_HALF_Y} {STEP_HALF_Z}",
            contype="1",
            conaffinity="2",
            friction=".9 .005 .0001",
            rgba=step_colors[idx],
            group="1",
        )
        ET.SubElement(
            sb,
            "geom",
            name=f"dyn_step_lip_{idx}",
            type="box",
            pos=f"{-STEP_HALF_X + 0.012:.3f} 0 {STEP_HALF_Z - 0.004:.3f}",
            size=f"0.012 {STEP_HALF_Y + 0.002:.3f} 0.005",
            contype="0",
            conaffinity="0",
            rgba=lip_colors[idx],
            group="1",
        )

    # 1 Mocap smooth ramp box (tilted via mocap_quat to 10° or 17° up/down when active, parked at z=-2.0 otherwise)
    rb = ET.SubElement(world, "body", name="dyn_ramp_body", mocap="true", pos="26.0 0 -2.0")
    ET.SubElement(
        rb,
        "geom",
        name="dyn_ramp",
        type="box",
        pos="0 0 0",
        size=f"{RAMP_HALF_X} {RAMP_HALF_Y} {RAMP_HALF_Z}",
        contype="1",
        conaffinity="2",
        friction=".95 .005 .0001",
        rgba=".36 .56 .44 1",
        group="1",
    )

    # Disjoint rough hfield lane at y = +12.0m
    ET.SubElement(
        world,
        "geom",
        name="rough_ground",
        type="hfield",
        hfield="rough_hfield",
        pos=f"{ROUGH_CENTER_X} {ROUGH_CENTER_Y} {-0.5 * ROUGH_SPAN_Z:.4f}",
        contype="1",
        conaffinity="2",
        friction=".9 .005 .0001",
        rgba=".58 .54 .38 1",
        group="1",
    )

    tree.write(out_xml, encoding="utf-8", xml_declaration=True)
    return out_xml


def get_shared_arena_assets() -> dict[str, Any]:
    global _SHARED_ARENA_ASSETS
    if _SHARED_ARENA_ASSETS is not None:
        return _SHARED_ARENA_ASSETS
    xml_path = ensure_autonomous_stair_arena_xml()
    spec = RobotSpec(**json.loads(TEMPLATE_SOURCE.read_text(encoding="utf-8"))["spec"])
    runtime = json.loads(RUNTIME_SOURCE.read_text(encoding="utf-8"))
    default_q = _q_from_runtime(runtime, spec.joint_names)
    bank = json.loads(BANK_SOURCE.read_text(encoding="utf-8"))
    sem = json.loads(SEMANTICS_SOURCE.read_text(encoding="utf-8"))
    bank_q, bank_z = _q_from_bank(bank, sem, spec.joint_names)

    ik = Mod4Retarget()
    fit_cache: dict[int, np.ndarray] = {}
    for h_mm in range(200, 415, 5):
        L = max(0.130, min(0.3466, h_mm / 1000.0 - 0.0625))
        fit_cache[h_mm] = ik.fit(np.sqrt(L * L + ik.lateral_offset ** 2), 0.0)["qpos"].copy()

    connect_pairs = [(x.get("site1"), x.get("site2")) for x in ET.parse(xml_path).getroot().findall("equality/connect")]
    _SHARED_ARENA_ASSETS = {
        "xml_path": xml_path,
        "spec": spec,
        "default_q": default_q,
        "bank_q": bank_q,
        "bank_z": bank_z,
        "fit_cache": fit_cache,
        "connect_pairs": connect_pairs,
    }
    return _SHARED_ARENA_ASSETS


class Mod4v3AutonomousStairEnv:
    """Unified 400Hz closed-loop RL & DAgger environment for Autonomous All-Speed Stair MoE."""

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)
        shared = get_shared_arena_assets()
        self.fit_cache = shared["fit_cache"]

        self.env = Mod4v3Mujoco(
            str(shared["xml_path"]),
            shared["spec"],
            shared["default_q"],
            shared["bank_q"],
            shared["bank_z"],
            action_clip=ACTION_CLIP,
        )
        self.m, self.d = self.env.m, self.env.d
        self.m.opt.timestep = 0.0025

        self.qa = np.array([self.m.jnt_qposadr[self.m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
        self.va = np.array([self.m.jnt_dofadr[self.m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
        self.baseline = np.r_[self.env.default_q[self.env.leg_ids].numpy(), [0.0, 0.0]][PPO_TO_NATIVE].astype(np.float32)

        self.tire_gids = np.array([self.m.geom("left_tire").id, self.m.geom("right_tire").id], dtype=int)
        self.wheel_bids = self.m.geom_bodyid[self.tire_gids]
        self.guide_front_gids = [int(self.m.geom("guide_wheel_04").id), int(self.m.geom("guide_wheel_06").id)]
        self.guide_all_gids = [
            g for g in range(self.m.ngeom) if (self.m.geom(g).name or "").startswith("guide_wheel_")
        ]
        self.step_bids = [int(self.m.body(f"dyn_step_body_{i}").id) for i in range(2)]
        self.step_mids = [int(self.m.body_mocapid[b]) for b in self.step_bids]
        self.step_gids = [int(self.m.geom(f"dyn_step_{i}").id) for i in range(2)]
        self.ramp_bid = int(self.m.body("dyn_ramp_body").id)
        self.ramp_mid = int(self.m.body_mocapid[self.ramp_bid])
        self.ramp_gid = int(self.m.geom("dyn_ramp").id)
        self.rough_gid = int(self.m.geom("rough_ground").id)

        self.pairs = [(self.m.site(s1).id, self.m.site(s2).id) for s1, s2 in shared["connect_pairs"]]

        self.nom_body_mass = self.m.body_mass.copy()
        self.nom_body_inertia = self.m.body_inertia.copy()
        self.nom_body_ipos = self.m.body_ipos.copy()
        self.nom_geom_friction = self.m.geom_friction.copy()

        self.rough_grid = np.zeros((ROUGH_NROW, ROUGH_NCOL), dtype=np.float32)
        self._regenerate_rough_hfield(seed=seed + 17)

        # Scenario state
        self.dr_scale = 0.0
        self.kp_scale = 1.0
        self.kd_scale = 1.0
        self.wheel_scale = 1.0
        self.torque_limit_scale = 1.0
        self.action_delay = 0

        self.scenario_kind = "stair_1step"
        self.is_positive_stair = True
        self.active_steps: list[tuple[float, float, float]] = []  # [(x_front, x_back, z_top)]
        self.ramp_info: tuple[str, float, float, float] | None = None  # (dir, x0, alpha_rad, h_plat)
        self.step_down_h = 0.0

        self.cmd_vx_base = 0.80
        self.cmd_wz_base = 0.0
        self.height_cmd = 0.28
        self.w_release_after_mount = False
        self.maneuver_profile: str = "steady"
        self.max_steps = 360

        self.k = 0
        self.prev_act = np.zeros(ACT_DIM, dtype=np.float32)
        self.delayed_act = np.zeros(ACT_DIM, dtype=np.float32)
        self.hist_buf = np.zeros((HIST_LEN, OBS_DIM), dtype=np.float32)

        self.step_mounted = [False, False]
        self.step_mount_time = [-1.0, -1.0]
        self.step_graduated = [False, False]
        self.step_standup_dt: list[float | None] = [None, None]
        self.step_on_frames = [0, 0]
        self.slid_off = False
        self.fell_reason = ""
        self.max_x_progress = 0.0
        self.max_pitch_deg = 0.0
        self.max_closure_m = 0.0
        self.gate_sum = 0.0
        self.gate_max = 0.0
        self.gate_frames = 0

    def _regenerate_rough_hfield(self, seed: int | None = None) -> None:
        r = np.random.default_rng(seed) if seed is not None else self.rng
        xs = np.linspace(-ROUGH_HALF_X, ROUGH_HALF_X, ROUGH_NCOL)
        ys = np.linspace(-ROUGH_HALF_Y, ROUGH_HALF_Y, ROUGH_NROW)
        XX, YY = np.meshgrid(xs, ys)
        # Smooth wavy hills + high-frequency gravel ripples normalized into [0, 1] (±3.5cm total span!)
        h = (
            0.36 * np.sin(2.1 * XX + float(r.uniform(0, 6.28))) * np.cos(1.8 * YY + float(r.uniform(0, 6.28)))
            + 0.28 * np.sin(4.7 * XX + 2.9 * YY + float(r.uniform(0, 6.28)))
            + 0.36 * r.uniform(-1.0, 1.0, size=(ROUGH_NROW, ROUGH_NCOL))
        )
        # Keep spawn zone around (x=0, y=12 -> XX=-3.0, YY=0.0) flat for clean initial stand!
        spawn_dist = np.hypot(XX - (0.0 - ROUGH_CENTER_X), YY)
        taper = np.clip((spawn_dist - 0.55) / 0.65, 0.0, 1.0)
        h = h * taper
        h_norm = np.clip(0.5 + 0.48 * h, 0.0, 1.0).astype(np.float32)
        self.rough_grid = (h_norm - 0.5) * ROUGH_SPAN_Z
        self.m.hfield_data[:] = h_norm.ravel()

    def terrain_z_at(self, x: float, y: float) -> float:
        if self.scenario_kind == "rough":
            u = (x - (ROUGH_CENTER_X - ROUGH_HALF_X)) / (2.0 * ROUGH_HALF_X) * (ROUGH_NCOL - 1)
            v = (y - (ROUGH_CENTER_Y - ROUGH_HALF_Y)) / (2.0 * ROUGH_HALF_Y) * (ROUGH_NROW - 1)
            ix = int(np.clip(round(u), 0, ROUGH_NCOL - 1))
            iy = int(np.clip(round(v), 0, ROUGH_NROW - 1))
            return float(self.rough_grid[iy, ix])
        if self.scenario_kind == "step_down":
            return self.step_down_h if x <= 1.50 else 0.0
        if self.scenario_kind in ("ramp_up", "ramp_down") and self.ramp_info is not None:
            rdir, x0, alpha, h_plat = self.ramp_info
            span_x = 2.0 * RAMP_HALF_X * math.cos(alpha)
            if rdir == "up":
                if x <= x0:
                    return 0.0
                if x <= x0 + span_x:
                    return (x - x0) * math.tan(alpha)
                return h_plat
            else:
                if x <= x0:
                    return h_plat
                if x <= x0 + span_x:
                    return max(0.0, h_plat - (x - x0) * math.tan(alpha))
                return 0.0
        z = 0.0
        for xf, xb, hz in self.active_steps:
            if xf <= x <= xb:
                z = max(z, hz)
        return z

    def _apply_dr(self, dr_scale: float) -> None:
        s = float(np.clip(dr_scale, 0.0, 1.0))
        self.dr_scale = s
        if s <= 1e-8:
            self.m.body_mass[:] = self.nom_body_mass
            self.m.body_inertia[:] = self.nom_body_inertia
            self.m.body_ipos[:] = self.nom_body_ipos
            self.m.geom_friction[:] = self.nom_geom_friction
            self.kp_scale = 1.0
            self.kd_scale = 1.0
            self.wheel_scale = 1.0
            self.torque_limit_scale = 1.0
            self.action_delay = 0
            mj.mj_setConst(self.m, self.d)
            return

        r = self.rng
        m_scales = r.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=self.m.nbody)
        m_scales[0] = 1.0
        for b in (*self.step_bids, self.ramp_bid):
            m_scales[b] = 1.0
        self.m.body_mass[:] = self.nom_body_mass * m_scales
        self.m.body_inertia[:] = self.nom_body_inertia * m_scales[:, None]
        self.m.body_ipos[:] = self.nom_body_ipos
        self.m.body_ipos[self.env.base_id] = self.nom_body_ipos[self.env.base_id] + r.uniform(-0.020 * s, 0.020 * s, size=3)

        f_scale = float(r.uniform(1.0 - 0.32 * s, 1.0 + 0.25 * s))
        self.m.geom_friction[:] = self.nom_geom_friction
        for g in [0, *self.tire_gids, *self.step_gids, self.ramp_gid, self.rough_gid]:
            self.m.geom_friction[g, 0] = max(0.38, self.nom_geom_friction[g, 0] * f_scale)

        self.kp_scale = float(r.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s))
        self.kd_scale = float(r.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s))
        self.wheel_scale = float(r.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s))
        self.torque_limit_scale = float(r.uniform(1.0 - 0.10 * s, 1.0 + 0.10 * s))
        self.action_delay = int(r.random() < 0.35 * s)
        mj.mj_setConst(self.m, self.d)

    def _park_all_mocap(self) -> None:
        for i, mid in enumerate(self.step_mids):
            self.d.mocap_pos[mid] = [18.0 + 5.0 * i, 0.0, -2.0]
            self.d.mocap_quat[mid] = [1.0, 0.0, 0.0, 0.0]
        self.d.mocap_pos[self.ramp_mid] = [28.0, 0.0, -2.0]
        self.d.mocap_quat[self.ramp_mid] = [1.0, 0.0, 0.0, 0.0]

    def reset_scenario(
        self,
        kind: str = "stair_1step",
        dr_scale: float = 0.0,
        step_heights: tuple[float, ...] = (0.20,),
        step_x1: float = 1.50,
        tread_len: float = 1.50,
        cmd_vx: float = 0.90,
        height_cmd: float = 0.28,
        start_x: float = 0.0,
        start_yaw: float = 0.0,
        w_release: bool = False,
        ramp_deg: float = 17.0,
        step_down_h: float = 0.20,
        maneuver_profile: str = "steady",
        max_steps: int = 360,
    ) -> dict[str, np.ndarray]:
        self._apply_dr(dr_scale)
        mj.mj_resetData(self.m, self.d)
        self._park_all_mocap()

        self.scenario_kind = kind
        self.is_positive_stair = kind in ("stair_1step", "stair_2step")
        self.active_steps = []
        self.ramp_info = None
        self.step_down_h = float(step_down_h)
        self.cmd_vx_base = float(cmd_vx)
        self.cmd_wz_base = 0.0
        self.height_cmd = float(height_cmd)
        self.w_release_after_mount = bool(w_release)
        self.maneuver_profile = maneuver_profile
        self.max_steps = int(max_steps)

        spawn_x = float(start_x)
        spawn_y = 0.0
        spawn_ground_z = 0.0

        if kind == "stair_1step":
            dh = float(self.rng.uniform(-0.006 * self.dr_scale, 0.006 * self.dr_scale))
            h1 = max(0.06, float(step_heights[0]) + dh)
            xb = step_x1 + 2.0 * STEP_HALF_X
            self.active_steps = [(step_x1, xb, h1)]
            self.d.mocap_pos[self.step_mids[0]] = [step_x1 + STEP_HALF_X, 0.0, h1 - STEP_HALF_Z]
        elif kind == "stair_2step":
            dh1 = float(self.rng.uniform(-0.005 * self.dr_scale, 0.005 * self.dr_scale))
            dh2 = float(self.rng.uniform(-0.005 * self.dr_scale, 0.005 * self.dr_scale))
            h1 = max(0.08, float(step_heights[0]) + dh1)
            h2 = max(h1 + 0.08, float(step_heights[1]) + dh2)
            x2 = step_x1 + tread_len
            self.active_steps = [(step_x1, x2, h1), (x2, x2 + 2.0 * STEP_HALF_X, h2)]
            self.d.mocap_pos[self.step_mids[0]] = [step_x1 + STEP_HALF_X, 0.0, h1 - STEP_HALF_Z]
            self.d.mocap_pos[self.step_mids[1]] = [x2 + STEP_HALF_X, 0.0, h2 - STEP_HALF_Z]
        elif kind == "step_down":
            hd = float(step_down_h)
            x_drop = 1.50
            self.d.mocap_pos[self.step_mids[0]] = [x_drop - STEP_HALF_X, 0.0, hd - STEP_HALF_Z]
            spawn_ground_z = hd
        elif kind == "ramp_up":
            alpha = math.radians(float(ramp_deg))
            x0 = 1.15
            # Rotate around +Y by -alpha so top surface (-Lx, +Lz) sits cleanly at (x0, 0.0) with 0mm lip!
            dx = -RAMP_HALF_X * math.cos(alpha) - RAMP_HALF_Z * math.sin(alpha)
            dz = +RAMP_HALF_X * math.sin(alpha) + RAMP_HALF_Z * math.cos(alpha)
            # Wait: verify exact R_y(-alpha)@[x_loc, 0, z_loc]:
            # For q = [cos(-a/2), 0, sin(-a/2), 0], R[0,0]=cos(a), R[0,2]=-sin(a), R[2,0]=+sin(a), R[2,2]=cos(a)!
            # So corner (-Lx, 0, +Lz) has world offset:
            # off_x = cos(a)*(-Lx) - sin(a)*(+Lz)
            # off_z = +sin(a)*(-Lx) + cos(a)*(+Lz) = -Lx*sin(a) + Lz*cos(a)
            # And corner (+Lx, 0, +Lz) has off_z = +Lx*sin(a) + Lz*cos(a) > off_z!
            off_x = -RAMP_HALF_X * math.cos(alpha) - RAMP_HALF_Z * math.sin(alpha)
            off_z = -RAMP_HALF_X * math.sin(alpha) + RAMP_HALF_Z * math.cos(alpha)
            self.d.mocap_pos[self.ramp_mid] = [x0 - off_x, 0.0, 0.0 - off_z]
            self.d.mocap_quat[self.ramp_mid] = [math.cos(-0.5 * alpha), 0.0, math.sin(-0.5 * alpha), 0.0]
            h_plat = min(2.0 * STEP_HALF_Z, 2.0 * RAMP_HALF_X * math.sin(alpha))
            x_top = x0 + 2.0 * RAMP_HALF_X * math.cos(alpha)
            self.d.mocap_pos[self.step_mids[0]] = [x_top + STEP_HALF_X - 0.02, 0.0, h_plat - STEP_HALF_Z]
            self.ramp_info = ("up", x0, alpha, h_plat)
        elif kind == "ramp_down":
            alpha = math.radians(float(ramp_deg))
            x0 = 1.00
            h_plat = min(0.48, 2.0 * RAMP_HALF_X * math.sin(alpha))
            # Start on level plateau dyn_step_0 spanning [-3.8, x0], then slope DOWN at +alpha!
            self.d.mocap_pos[self.step_mids[0]] = [x0 - STEP_HALF_X, 0.0, h_plat - STEP_HALF_Z]
            # For q = [cos(+a/2), 0, sin(+a/2), 0], R[0,0]=cos(a), R[0,2]=+sin(a), R[2,0]=-sin(a), R[2,2]=cos(a)
            # Corner (-Lx, 0, +Lz) has world offset:
            off_x = -RAMP_HALF_X * math.cos(alpha) + RAMP_HALF_Z * math.sin(alpha)
            off_z = +RAMP_HALF_X * math.sin(alpha) + RAMP_HALF_Z * math.cos(alpha)
            self.d.mocap_pos[self.ramp_mid] = [x0 - off_x, 0.0, h_plat - off_z]
            self.d.mocap_quat[self.ramp_mid] = [math.cos(0.5 * alpha), 0.0, math.sin(0.5 * alpha), 0.0]
            self.ramp_info = ("down", x0, alpha, h_plat)
            spawn_ground_z = h_plat
        elif kind == "rough":
            if self.rng.random() < 0.25:
                self._regenerate_rough_hfield()
            spawn_y = ROUGH_CENTER_Y
            spawn_ground_z = self.terrain_z_at(spawn_x, spawn_y)

        h_key = int(np.clip(round(self.height_cmd * 1000.0 / 5.0) * 5, 200, 410))
        self.d.qpos[:] = self.fit_cache[h_key]
        L_spawn = max(0.130, min(0.3466, self.height_cmd - 0.0625))
        self.d.qpos[:3] = [spawn_x, spawn_y, spawn_ground_z + L_spawn + 0.0625 + 0.0015]
        self.d.qpos[3:7] = [math.cos(0.5 * start_yaw), 0.0, 0.0, math.sin(0.5 * start_yaw)]
        self.d.qvel[:] = 0.0
        mj.mj_forward(self.m, self.d)

        self.k = 0
        self.prev_act = np.zeros(ACT_DIM, dtype=np.float32)
        self.delayed_act = np.zeros(ACT_DIM, dtype=np.float32)
        self.step_mounted = [False, False]
        self.step_mount_time = [-1.0, -1.0]
        self.step_graduated = [False, False]
        self.step_standup_dt = [None, None]
        self.step_on_frames = [0, 0]
        self.slid_off = False
        self.fell_reason = ""
        self.max_x_progress = float(self.d.qpos[0])
        self.max_pitch_deg = 0.0
        self.max_closure_m = 0.0
        self.gate_sum = 0.0
        self.gate_max = 0.0
        self.gate_frames = 0

        obs = self._get_obs()
        self.hist_buf = np.repeat(obs[None, :], HIST_LEN, axis=0)
        return {
            "obs": obs,
            "hist": self.hist_buf.reshape(-1).copy(),
            "priv": self._get_priv(),
        }

    def sample_random_training_scenario(self, dr_scale: float = 0.0, neg_prob: float = 0.30) -> dict[str, np.ndarray]:
        r = self.rng
        if r.random() < neg_prob:
            neg_choice = float(r.random())
            if neg_choice < 0.40:
                prof = str(r.choice(["sprint_brake", "reverse", "yaw_slalom", "height_sweep", "stand_still"]))
                return self.reset_scenario(
                    kind="flat",
                    dr_scale=dr_scale,
                    cmd_vx=float(r.uniform(0.6, 1.8)),
                    height_cmd=float(r.uniform(0.24, 0.38)),
                    start_yaw=float(r.uniform(-0.10, 0.10)),
                    maneuver_profile=prof,
                    max_steps=300,
                )
            elif neg_choice < 0.65:
                rkind = "ramp_up" if r.random() < 0.55 else "ramp_down"
                rdeg = float(r.choice([10.0, 14.0, 17.0]))
                return self.reset_scenario(
                    kind=rkind,
                    dr_scale=dr_scale,
                    cmd_vx=float(r.uniform(0.55, 1.45)),
                    height_cmd=float(r.uniform(0.26, 0.34)),
                    ramp_deg=rdeg,
                    maneuver_profile="ramp_stop_go" if r.random() < 0.35 else "steady",
                    max_steps=320,
                )
            elif neg_choice < 0.85:
                return self.reset_scenario(
                    kind="rough",
                    dr_scale=dr_scale,
                    cmd_vx=float(r.uniform(0.55, 1.55)),
                    height_cmd=float(r.uniform(0.26, 0.36)),
                    maneuver_profile="sprint_brake" if r.random() < 0.35 else "steady",
                    max_steps=300,
                )
            else:
                hd = float(r.choice([0.10, 0.15, 0.20]))
                return self.reset_scenario(
                    kind="step_down",
                    dr_scale=dr_scale,
                    cmd_vx=float(r.uniform(0.55, 1.35)),
                    height_cmd=float(r.uniform(0.26, 0.34)),
                    step_down_h=hd,
                    max_steps=280,
                )

        # Positive stair scenarios (70% of training episodes)
        if r.random() < 0.24:
            # Continuous 2-step (20cm + 20cm = 40cm or 15+15cm)
            h_unit = 0.20 if r.random() < 0.80 else 0.15
            tread = float(r.uniform(1.42, 1.62))
            return self.reset_scenario(
                kind="stair_2step",
                dr_scale=dr_scale,
                step_heights=(h_unit, 2.0 * h_unit),
                step_x1=float(r.uniform(1.35, 1.65)),
                tread_len=tread,
                cmd_vx=float(r.uniform(0.55, 1.35)),
                height_cmd=float(r.uniform(0.26, 0.33)),
                start_x=float(r.uniform(-0.15, 0.15)),
                start_yaw=float(r.uniform(-0.06, 0.06)),
                w_release=bool(r.random() < 0.15),
                max_steps=460,
            )

        # Single-step climb across {0.10, 0.15, 0.20}m (weighted heavily on 0.20m) & full speed [0.42, 1.68] m/s!
        hs = float(r.choice([0.10, 0.15, 0.20, 0.20, 0.20]))
        vc = float(r.uniform(0.42, 1.68))
        hc = 0.28 if r.random() < 0.50 else float(r.uniform(0.25, 0.37))
        w_rel = bool(r.random() < 0.20)
        return self.reset_scenario(
            kind="stair_1step",
            dr_scale=dr_scale,
            step_heights=(hs,),
            step_x1=float(r.uniform(1.35, 1.65)),
            cmd_vx=vc,
            height_cmd=hc,
            start_x=float(r.uniform(-0.12, 0.12)),
            start_yaw=float(r.uniform(-0.06, 0.06)),
            w_release=w_rel,
            max_steps=380,
        )

    def _current_commands(self) -> tuple[float, float, float]:
        t_s = self.k * 0.02
        rot = self.d.xmat[self.env.base_id].reshape(3, 3)
        yaw = math.atan2(float(rot[1, 0]), float(rot[0, 0]))
        wz_track = float(np.clip(-1.5 * yaw, -0.65, 0.65))

        if self.scenario_kind == "flat":
            p = self.maneuver_profile
            if p == "stand_still":
                return 0.0, 0.0, self.height_cmd
            if p == "sprint_brake":
                # 0..0.4s stand -> 0.4..2.0s sprint up to 1.8m/s -> 2.0..3.4s hard brake 0.0 -> 3.4..4.8s sprint -> 4.8..end brake
                if t_s < 0.40 or (2.00 <= t_s < 3.40) or t_s >= 4.80:
                    return 0.0, wz_track, self.height_cmd
                return self.cmd_vx_base, wz_track, self.height_cmd
            if p == "reverse":
                vc = 0.0 if t_s < 0.40 else (-0.55 if t_s < 3.20 else 0.70)
                return vc, wz_track, self.height_cmd
            if p == "yaw_slalom":
                vc = 0.0 if t_s < 0.35 else self.cmd_vx_base
                wz = 1.25 * math.sin(2.4 * t_s)
                return vc, wz, self.height_cmd
            if p == "height_sweep":
                vc = 0.0 if t_s < 0.50 else (0.85 if t_s < 3.80 else 0.0)
                hc = 0.305 + 0.095 * math.sin(2.8 * t_s)
                return vc, wz_track, float(np.clip(hc, 0.205, 0.405))

        if self.maneuver_profile == "ramp_stop_go":
            vc = 0.0 if (t_s < 0.30 or (2.20 <= t_s < 3.20)) else self.cmd_vx_base
            return vc, wz_track, self.height_cmd

        if self.maneuver_profile == "sprint_brake":
            vc = 0.0 if (t_s < 0.30 or (2.30 <= t_s < 3.50)) else self.cmd_vx_base
            return vc, wz_track, self.height_cmd

        vc = 0.0 if t_s < 0.25 else self.cmd_vx_base
        if self.w_release_after_mount and self.active_steps:
            last_idx = len(self.active_steps) - 1
            if self.step_mounted[last_idx] and (t_s - self.step_mount_time[last_idx]) >= 0.08:
                vc = 0.0
        return vc, wz_track, self.height_cmd

    @property
    def body_vx(self) -> float:
        R = self.d.xmat[self.env.base_id].reshape(3, 3)
        fx, fy = float(R[0, 0]), float(R[1, 0])
        n = max(math.hypot(fx, fy), 1e-6)
        return float((self.d.qvel[0] * fx + self.d.qvel[1] * fy) / n)

    def _get_obs(self) -> np.ndarray:
        vc, wz_c, h_c = self._current_commands()
        rot = self.d.xmat[self.env.base_id].reshape(3, 3)
        q = (self.d.qpos[self.qa] - self.baseline).astype(np.float32)
        q[4:] = 0.0
        gyro = (self.d.qvel[3:6] * 0.5).astype(np.float32)
        grav = (rot.T @ np.array([0.0, 0.0, -1.0])).astype(np.float32)
        dq = (self.d.qvel[self.va] * 0.1).astype(np.float32)

        if self.dr_scale > 1e-8:
            s = self.dr_scale
            gyro = gyro + self.rng.normal(0.0, 0.012 * s, size=3).astype(np.float32)
            grav = grav + self.rng.normal(0.0, 0.008 * s, size=3).astype(np.float32)
            q[:4] = q[:4] + self.rng.normal(0.0, 0.006 * s, size=4).astype(np.float32)
            dq = dq + self.rng.normal(0.0, 0.010 * s, size=6).astype(np.float32)

        return np.concatenate(
            (
                np.array([vc, 0.0, wz_c, h_c * 5.0], dtype=np.float32),
                gyro,
                grav,
                q,
                dq,
                self.prev_act,
                np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32),
            ),
            axis=0,
        )

    def _get_priv(self) -> np.ndarray:
        """20-D privileged state fed ONLY to AsymmetricStairValueCritic during Stage-2 PPO."""
        wpos = self.d.geom_xpos[self.tire_gids]
        wx_mean = float(np.mean(wpos[:, 0]))
        wx_min = float(np.min(wpos[:, 0]))
        wz_min = float(np.min(wpos[:, 2]))
        gz = self.terrain_z_at(float(self.d.qpos[0]), float(self.d.qpos[1]))
        rel_z = float(self.d.qpos[2]) - gz

        next_dx = 3.0
        next_dh = 0.0
        cur_mounted = 0.0
        t_on_step = 0.0
        for idx, (xf, _xb, hs) in enumerate(self.active_steps):
            if not self.step_mounted[idx]:
                next_dx = float(np.clip(xf - wx_mean, -0.6, 3.0))
                prev_h = self.active_steps[idx - 1][2] if idx > 0 else 0.0
                next_dh = float(hs - prev_h)
                break
            else:
                cur_mounted = float(idx + 1)
                t_on_step = min(2.0, max(0.0, self.k * 0.02 - self.step_mount_time[idx]))

        rot = self.d.xmat[self.env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-rot[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(rot[2, 1]), float(rot[2, 2]))

        return np.array(
            [
                rel_z,
                float(self.d.qvel[0]),
                float(self.d.qvel[1]),
                float(self.d.qvel[2]),
                pitch,
                roll,
                next_dx,
                next_dh,
                wx_min - (self.active_steps[-1][0] if self.active_steps else 0.0),
                wz_min - gz,
                cur_mounted,
                t_on_step,
                float(self.is_positive_stair),
                float(self.k) / max(1.0, float(self.max_steps)),
                self.kp_scale - 1.0,
                self.kd_scale - 1.0,
                self.wheel_scale - 1.0,
                self.torque_limit_scale - 1.0,
                float(self.action_delay),
                self.dr_scale,
            ],
            dtype=np.float32,
        )

    def _compute_torque_dr(self, a_nat_t: torch.Tensor) -> np.ndarray:
        tau = self.env._torque(a_nat_t).numpy().reshape(-1)
        if self.dr_scale <= 1e-8:
            return tau
        tau[:4] *= self.kp_scale
        tau[4:] *= self.wheel_scale
        lim_leg = 40.0 * self.torque_limit_scale
        lim_whl = 5.775909774436091 * self.torque_limit_scale
        tau[:4] = np.clip(tau[:4], -lim_leg, lim_leg)
        tau[4:] = np.clip(tau[4:], -lim_whl, lim_whl)
        return tau

    def step(self, action_ppo: np.ndarray, g_prob_val: float = 0.0) -> tuple[dict[str, np.ndarray], float, bool, dict[str, Any]]:
        a = np.clip(np.asarray(action_ppo, dtype=np.float32), -ACTION_CLIP, ACTION_CLIP).copy()
        exec_a = self.delayed_act.copy() if (self.action_delay > 0 and self.k > 0) else a.copy()
        self.delayed_act = a.copy()
        a_delta_norm = float(np.sum((a - self.prev_act) ** 2))

        a_t = torch.from_numpy(exec_a[PPO_TO_NATIVE]).reshape(1, 6)
        for j in range(8):
            tau = self._compute_torque_dr(a_t)
            if j % 4 == 0:
                self.d.ctrl[self.env.act_ids[:4]] = tau[:4]
            self.d.ctrl[self.env.act_ids[4:]] = tau[4:]
            mj.mj_step(self.m, self.d)

        self.k += 1
        t_s = self.k * 0.02
        self.prev_act = a

        g_p = float(np.clip(g_prob_val, 0.0, 1.0))
        g_eff = max(0.0, (g_p - GATE_DEADZONE) / (1.0 - GATE_DEADZONE))
        self.gate_sum += g_p
        self.gate_max = max(self.gate_max, g_p)
        self.gate_frames += 1

        if not np.isfinite(self.d.qpos).all() or not np.isfinite(self.d.qvel).all():
            self.fell_reason = "nonfinite"
            st = self._pack_state()
            return st, -25.0, True, self._make_info(timeout=False)

        closure = max(float(np.linalg.norm(self.d.site_xpos[l] - self.d.site_xpos[r])) for l, r in self.pairs)
        self.max_closure_m = max(self.max_closure_m, closure)
        if closure > 1.0:
            self.fell_reason = "catastrophic_closure"
            st = self._pack_state()
            return st, -25.0, True, self._make_info(timeout=False)

        rot = self.d.xmat[self.env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-rot[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(rot[2, 1]), float(rot[2, 2]))
        p_deg = abs(math.degrees(pitch))
        r_deg = abs(math.degrees(roll))
        self.max_pitch_deg = max(self.max_pitch_deg, p_deg)

        gz = self.terrain_z_at(float(self.d.qpos[0]), float(self.d.qpos[1]))
        rel_z = float(self.d.qpos[2]) - gz
        if p_deg > 42.0 or r_deg > 42.0 or rel_z < 0.105:
            self.fell_reason = "fell_attitude_or_height"
            st = self._pack_state()
            return st, -25.0, True, self._make_info(timeout=False)

        vc, wz_c, h_c = self._current_commands()
        bvx = self.body_vx
        wpos = self.d.geom_xpos[self.tire_gids]
        wx_min = float(np.min(wpos[:, 0]))
        wz_min = float(np.min(wpos[:, 2]))

        rew = 0.0
        if self.is_positive_stair:
            prev_max_x = self.max_x_progress
            self.max_x_progress = max(self.max_x_progress, float(self.d.qpos[0]))
            dx_prog = self.max_x_progress - prev_max_x
            rew += 2.2 * dx_prog

            # Check mounting, regression anti-cheat, auto-standup, and router decay
            all_grad = True
            currently_climbing = False
            for idx, (xf, _xb, hs) in enumerate(self.active_steps):
                on_this = wx_min > xf + 0.030 and wz_min > hs + 0.045
                if on_this:
                    self.step_on_frames[idx] += 1
                if not self.step_mounted[idx] and on_this:
                    self.step_mounted[idx] = True
                    self.step_mount_time[idx] = t_s
                    rew += 10.0  # Milestone 1: Step mounted!

                # Zero-tolerance slide-off / drop anti-cheat (front/side drop, never far +11m finish line)!
                if (
                    (self.step_mounted[idx] or self.step_on_frames[idx] >= 4)
                    and float(self.d.qpos[0]) < _xb - 0.35
                    and (wz_min < hs + 0.025 or wx_min < xf - 0.035)
                ):
                    self.slid_off = True
                    self.fell_reason = f"slid_off_step_{idx}"
                    st = self._pack_state()
                    return st, -25.0, True, self._make_info(timeout=False)

                if not self.step_mounted[idx]:
                    all_grad = False
                    if wx_min > xf - 0.42:
                        currently_climbing = True
                else:
                    dt_m = t_s - self.step_mount_time[idx]
                    # Only evaluate standup on step idx if not yet engaging step idx+1
                    next_engaged = (idx + 1 < len(self.active_steps)) and (
                        wx_min > self.active_steps[idx + 1][0] - 0.38
                    )
                    if not next_engaged:
                        step_rel_z = float(self.d.qpos[2]) - hs
                        rew += 0.25 * math.exp(-35.0 * (step_rel_z - h_c) ** 2)
                        rew += 0.18 * math.exp(-3.5 * (bvx - vc) ** 2)
                        if dt_m >= 0.35 and step_rel_z < h_c - 0.035:
                            # Anti-crouch penalty: must NOT stay crouched at 0.20m!
                            rew -= 0.60 * (h_c - step_rel_z)
                        if dt_m >= 0.32 and abs(step_rel_z - h_c) < 0.035:
                            # Reward handing back to E0 (g_prob -> 0) once standing tall on tread!
                            rew += 0.14 * (1.0 - g_p) - 0.55 * g_p
                        if (
                            self.step_standup_dt[idx] is None
                            and step_rel_z >= max(0.240, h_c - 0.025)
                            and g_p < 0.10
                        ):
                            self.step_standup_dt[idx] = round(dt_m, 3)
                            if dt_m <= 0.60:
                                self.step_graduated[idx] = True
                                rew += 12.0  # Milestone 2: Stood up <=0.6s & returned to E0!
                    if not self.step_graduated[idx]:
                        all_grad = False

            if not currently_climbing and not any(
                self.step_mounted[i] and (t_s - self.step_mount_time[i] < 0.35)
                for i in range(len(self.active_steps))
            ):
                # Far before the step (>0.42m away) or well after standing up: penalize premature/lingering gate!
                if wx_min < self.active_steps[0][0] - 0.45:
                    rew -= 2.5 * g_p + 5.0 * (g_eff ** 2)
                rew += 0.10 * math.exp(-2.5 * (bvx - vc) ** 2)

            rew -= 0.08 * max(0.0, abs(pitch) - 0.36) ** 2 + 0.05 * (roll ** 2) + 0.0015 * a_delta_norm
        else:
            # Negative (non-stair) scenario: reward E0 tracking + strict penalty for ANY non-zero g_stair!
            rew += 0.15 + 0.12 * math.exp(-2.5 * (bvx - vc) ** 2) + 0.08 * math.exp(-20.0 * (rel_z - h_c) ** 2)
            rew -= 3.5 * g_p + 8.0 * (g_eff ** 2) + 0.001 * a_delta_norm

        far_finish = bool(self.active_steps and float(self.d.qpos[0]) > self.active_steps[-1][1] - 0.55)
        timeout = self.k >= self.max_steps or abs(float(self.d.qpos[0])) > 16.0 or far_finish
        st = self._pack_state()
        return st, float(rew), bool(timeout), self._make_info(timeout=timeout)

    def _pack_state(self) -> dict[str, np.ndarray]:
        obs = self._get_obs()
        self.hist_buf = np.concatenate((self.hist_buf[1:], obs[None, :]), axis=0)
        return {
            "obs": obs,
            "hist": self.hist_buf.reshape(-1).copy(),
            "priv": self._get_priv(),
        }

    def _make_info(self, timeout: bool) -> dict[str, Any]:
        n_steps = len(self.active_steps)
        last_h = self.active_steps[-1][2] if n_steps > 0 else self.terrain_z_at(float(self.d.qpos[0]), float(self.d.qpos[1]))
        return {
            "scenario_kind": self.scenario_kind,
            "is_positive_stair": self.is_positive_stair,
            "timeout": timeout,
            "fell_reason": self.fell_reason,
            "slid_off": self.slid_off,
            "steps_total": n_steps,
            "steps_mounted": sum(self.step_mounted[:n_steps]),
            "steps_graduated": sum(self.step_graduated[:n_steps]),
            "last_standup_dt": self.step_standup_dt[n_steps - 1] if n_steps > 0 else None,
            "final_x": float(self.d.qpos[0]),
            "final_z": float(self.d.qpos[2]),
            "final_rel_z": float(self.d.qpos[2]) - last_h,
            "final_vx": self.body_vx,
            "max_pitch_deg": self.max_pitch_deg,
            "max_closure_m": self.max_closure_m,
            "mean_g_stair": self.gate_sum / max(1, self.gate_frames),
            "max_g_stair": self.gate_max,
        }


class ParallelStairVecEnv:
    """Thread-pooled multi-environment runner (<= 8 workers on shared local Windows, <= 48 on remote 128-core Linux)."""

    def __init__(self, num_envs: int = 6, base_seed: int = 20261118):
        max_cap = 8 if os.name == "nt" else 48
        assert 1 <= num_envs <= max_cap, f"num_envs={num_envs} exceeds CPU budget cap {max_cap}!"
        self.num_envs = num_envs
        get_shared_arena_assets()  # Pre-build arena XML once before spawning threads
        self.envs = [Mod4v3AutonomousStairEnv(seed=base_seed + 101 * i) for i in range(num_envs)]
        self.pool = ThreadPoolExecutor(max_workers=num_envs)

    def reset_random(self, dr_scale: float = 0.0, neg_prob: float = 0.30) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        sts = list(self.pool.map(lambda e: e.sample_random_training_scenario(dr_scale=dr_scale, neg_prob=neg_prob), self.envs))
        obs = np.stack([s["obs"] for s in sts], axis=0)
        hist = np.stack([s["hist"] for s in sts], axis=0)
        priv = np.stack([s["priv"] for s in sts], axis=0)
        return obs, hist, priv

    def step(
        self,
        actions: np.ndarray,
        g_probs: np.ndarray,
        dr_scale: float = 0.0,
        neg_prob: float = 0.30,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[dict[str, Any]]]:
        def _step_one(args):
            env, act_i, gp_i = args
            st, rew, done, info = env.step(act_i, float(gp_i))
            if done:
                info["terminal_obs"] = st["obs"].copy()
                info["terminal_hist"] = st["hist"].copy()
                info["terminal_priv"] = st["priv"].copy()
                st = env.sample_random_training_scenario(dr_scale=dr_scale, neg_prob=neg_prob)
            return st, rew, done, info

        results = list(self.pool.map(_step_one, zip(self.envs, actions, g_probs)))
        obs = np.stack([r[0]["obs"] for r in results], axis=0)
        hist = np.stack([r[0]["hist"] for r in results], axis=0)
        priv = np.stack([r[0]["priv"] for r in results], axis=0)
        rews = np.array([r[1] for r in results], dtype=np.float32)
        dones = np.array([r[2] for r in results], dtype=np.float32)
        infos = [r[3] for r in results]
        return obs, hist, priv, rews, dones, infos

    def close(self) -> None:
        self.pool.shutdown(wait=True)

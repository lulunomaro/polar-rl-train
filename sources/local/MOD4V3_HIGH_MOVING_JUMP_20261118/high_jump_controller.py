# SPDX-License-Identifier: MIT
"""MOD4v3 Deep-Crouch High Jump & Moving Jump Controller layered over frozen c874 PPO.

Physical & Control Contract (100% Preserved):
  - Plant: MOD4v3 / HW300N60_R3 (MJCF SHA256 = 77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f)
    with closed-loop 4-bar linkages and 2000 N/m gas springs intact.
  - Base locomotion policy: Low-pitch comprehensive PPO c874
    (deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt, SHA256 = c874a1af..., 35-D obs -> 6-D action).
  - Rates: dt = 0.0025s (400 Hz physics), 100 Hz leg PD (Kp=60, Kd=2), 400 Hz wheel servo (Kv=0.6),
    50 Hz policy/controller (decimation = 8).
  - Actuation path: 100% unmodified Mod4v3Mujoco._torque with action_clip = [-6.0, 6.0],
    _continuous_leg_target delta bounds [0.17265, 1.75089] rad, and exact DC motor envelope
    (legs: 40.0 / 53.333 / 16.755; wheels: 5.7759 / 28.185 / 55.3557).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import mujoco
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

OLD_DELIVERY = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
LOW_PITCH_DELIVERY = REPO / "deliveries/MOD4V3_LOW_PITCH_20261116"

XML_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/mjcf/scene.xml"
RUNTIME_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/runtime_config.json"
SEMANTICS_SOURCE = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/semantics.json"
BANK_SOURCE = OLD_DELIVERY / "plant/reset_bank.json"
TEMPLATE_SOURCE = OLD_DELIVERY / "runtime/core/template_spec.json"
CKPT_SOURCE = LOW_PITCH_DELIVERY / "model_full_ppo.pt"

EXPECTED_XML_SHA256 = "77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f"
EXPECTED_CKPT_SHA256 = "c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617"

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
    Mod4v3Mujoco,
    RobotSpec,
    _q_from_bank,
    _q_from_runtime,
)
from play_ppo_flatv1 import ActorMLP, _map  # noqa: E402

ACTION_CLIP = 6.0
WHEEL_RADIUS_M = 0.0625

PHASES = (
    "DRIVE",           # 0: Normal c874 locomotion
    "CROUCH",          # 1: Stage 1 - Gravity-synced deep crouch charge (compressing 2000 N/m gas springs)
    "PUSH",            # 2: Stage 2 - Speed-compensated explosive full-stroke takeoff
    "FLIGHT_EXTEND",   # 3: Brief liftoff confirmation window
    "FLIGHT_TUCK",     # 4: Stage 3a - Rapid apex leg tuck + active wheel/leg attitude control
    "LANDING_EXTEND",  # 5: Stage 3b - World-frame Raibert pre-touchdown foot placement + air balance
    "SKYHOOK_ABSORB",  # 6: Stage 4 - Unidirectional skyhook touchdown absorption + c874 balance handoff
)

# Measured 4-bar kinematic lookup on HW300N60_R3: actual_delta (rad) -> neutral_mean (rad) where wheel_x == com_x at pitch = 0
DELTA_NEUTRAL_GRID = np.array(
    [0.348, 0.503, 0.659, 0.809, 0.952, 1.086, 1.210, 1.325, 1.432, 1.532, 1.625, 1.712, 1.752],
    dtype=np.float64,
)
MEAN_NEUTRAL_GRID = np.array(
    [0.4674, 0.4217, 0.3800, 0.3451, 0.3172, 0.2953, 0.2780, 0.2645, 0.2538, 0.2454, 0.2386, 0.2332, 0.2317],
    dtype=np.float64,
)


def neutral_4bar_mean(actual_delta: float) -> float:
    """Return neutral hip mean 0.5*(q_front + q_rear) placing wheel center directly below COM at zero pitch."""
    return float(np.interp(actual_delta, DELTA_NEUTRAL_GRID, MEAN_NEUTRAL_GRID))


def verify_source_identities() -> dict[str, str]:
    """Assert SHA256 integrity of frozen MOD4v3 MJCF and c874 checkpoint (read-only)."""
    xml_sha = hashlib.sha256(XML_SOURCE.read_bytes()).hexdigest()
    ckpt_sha = hashlib.sha256(CKPT_SOURCE.read_bytes()).hexdigest()
    if xml_sha != EXPECTED_XML_SHA256:
        raise RuntimeError(f"MJCF SHA256 mismatch: expected {EXPECTED_XML_SHA256}, got {xml_sha}")
    if ckpt_sha != EXPECTED_CKPT_SHA256:
        raise RuntimeError(f"c874 checkpoint SHA256 mismatch: expected {EXPECTED_CKPT_SHA256}, got {ckpt_sha}")
    return {"mjcf_sha256": xml_sha, "c874_sha256": ckpt_sha}


@dataclass
class HighJumpConfig:
    """Locked optimal parameters from systematic MuJoCo parameter sweeps."""
    # Cruise & command smoothing
    default_cruise_height_m: float = 0.365
    height_slew_m_s: float = 0.06
    cmd_slew_s: float = 0.24

    # Stage 1: Deep Crouch Charge ("深蹲压低姿态蓄力")
    crouch_delta_rad: float = 0.21
    crouch_speed_delta_k: float = 0.03
    crouch_rate_rad_s: float = 1.80
    compress_s: float = 0.48
    max_compress_wait_s: float = 0.16
    min_crouch_support_substeps: int = 4

    # Stage 2: Explosive Full-Stroke Takeoff ("极限爆发蹬伸大跳")
    push_delta_rad: float = LEG_DELTA_BOUNDS[1]
    push_s: float = 0.30
    push_mean_bias_rad: float = -0.285
    push_speed_mean_k: float = 0.055
    air_confirm_substeps: int = 4
    liftoff_min_vz_m_s: float = 0.20

    # Stage 3: Rapid Mid-Air Leg Tuck + Active Balance + Pre-Touchdown Raibert Foot Placement
    extend_air_s: float = 0.0
    tuck_delta_rad: float = 0.173
    tuck_ramp_s: float = 0.025
    tuck_min_s: float = 0.14
    tuck_max_s: float = 0.28
    tuck_mean_bias_rad: float = -0.145
    preland_vz_m_s: float = -0.35
    land_delta_rad: float = 1.54
    land_ramp_s: float = 0.07
    air_pitch_ref_rad: float = 0.075
    pitch_kp: float = 10.0
    pitch_kd: float = 1.10
    leg_pitch_kp: float = 2.60
    leg_pitch_kd: float = 0.21
    roll_kp: float = 0.65
    roll_kd: float = 0.08
    air_raibert_w_base: float = 0.75
    air_raibert_w_speed_k: float = 0.07
    air_raibert_pitch_k: float = 0.55
    air_raibert_vx_k: float = 0.14
    air_raibert_err_k: float = 0.08
    air_raibert_bias_rad: float = 0.0

    # Stage 4: Unidirectional Skyhook Compliant Touchdown + Immediate c874 Handoff
    skyhook_s: float = 0.32
    skyhook_kd: float = 0.42
    z_guard_kp: float = 12.0
    z_guard_ref_m: float = 0.285

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_jump_scene_xml(scene_name: str = "flat", cache_dir: Path | None = None) -> Path:
    """Build a local MuJoCo scene XML preserving exact MOD4v3 HW300N60_R3 robot physics & contacts.

    Scenes:
      - 'flat': Clean flat benchmark arena with visual distance grid & height ruler posts (non-colliding).
      - 'hurdles': Multi-hurdle jump course (14 cm, 20 cm, 25 cm crossbars spaced along +X).
      - 'platforms': Stepped 18 cm & 34 cm wide jump/park platforms.
    """
    verify_source_identities()
    if cache_dir is None:
        cache_dir = HERE / "runtime_scenes"
    cache_dir.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(XML_SOURCE)
    root = tree.getroot()
    root.find("compiler").set("meshdir", str(XML_SOURCE.parent / "assets"))
    vis_global = root.find("visual/global")
    if vis_global is not None:
        vis_global.set("offwidth", "1600")
        vis_global.set("offheight", "1000")

    asset = root.find("asset")
    ET.SubElement(
        asset,
        "texture",
        name="grid_tex",
        type="2d",
        builtin="checker",
        rgb1=".18 .22 .27",
        rgb2=".23 .28 .34",
        width="512",
        height="512",
        mark="edge",
        markrgb=".32 .39 .47",
    )
    ET.SubElement(
        asset,
        "material",
        name="arena_floor",
        texture="grid_tex",
        texrepeat="20 20",
        texuniform="true",
        reflectance="0.06",
    )

    world = root.find("worldbody")
    ground = world.find("geom[@name='ground']")
    if ground is not None:
        ground.set("size", "25 25 .1")
        ground.set("material", "arena_floor")
        # Exact native friction/contact preserved (contype=1, conaffinity=2, default friction=.9 .003 .0001)

    # Non-colliding visual distance lines every 1.0m along X for clear motion & jump-height perception
    for x_tick in range(-4, 15):
        ET.SubElement(
            world,
            "geom",
            name=f"x_marker_{x_tick:+d}",
            type="box",
            pos=f"{x_tick:.2f} 0 0.0008",
            size="0.006 1.6 0.0008",
            contype="0",
            conaffinity="0",
            rgba=".38 .48 .58 .55" if x_tick != 0 else ".30 .82 .95 .80",
            group="1",
        )
    # Non-colliding background height reference rail (20cm, 30cm, 40cm bars at y = +0.75m)
    for h_cm, color in ((20, ".45 .75 .45 .45"), (30, ".95 .78 .28 .55"), (40, ".98 .42 .38 .55")):
        ET.SubElement(
            world,
            "geom",
            name=f"height_ruler_{h_cm}cm",
            type="box",
            pos=f"3.0 0.72 {h_cm / 100.0:.3f}",
            size="7.5 0.006 0.003",
            contype="0",
            conaffinity="0",
            rgba=color,
            group="1",
        )

    if scene_name == "hurdles":
        hurdles = [
            ("hurdle_1", 1.80, 0.14, ".28 .80 .52 1"),
            ("hurdle_2", 4.10, 0.20, ".95 .74 .24 1"),
            ("hurdle_3", 6.50, 0.25, ".96 .42 .36 1"),
        ]
        for hname, hx, hz, rgba in hurdles:
            # Crossbar + side posts (collidable with robot contype=1 conaffinity=2)
            ET.SubElement(
                world,
                "geom",
                name=hname,
                type="box",
                pos=f"{hx:.2f} 0 {hz - 0.015:.3f}",
                size="0.025 0.75 0.015",
                contype="1",
                conaffinity="2",
                rgba=rgba,
                group="1",
            )
            for side_s, sy in (("L", 0.77), ("R", -0.77)):
                ET.SubElement(
                    world,
                    "geom",
                    name=f"{hname}_post_{side_s}",
                    type="box",
                    pos=f"{hx:.2f} {sy:.2f} {hz / 2.0:.3f}",
                    size=f"0.025 0.025 {hz / 2.0:.3f}",
                    contype="0",
                    conaffinity="0",
                    rgba=".35 .40 .46 1",
                    group="1",
                )
    elif scene_name == "platforms":
        platforms = [
            ("plat_step1", 2.40, 1.60, 0.18, ".35 .62 .76 1"),
            ("plat_step2", 4.80, 1.80, 0.34, ".78 .52 .30 1"),
        ]
        for pname, px, plen, pz, rgba in platforms:
            ET.SubElement(
                world,
                "geom",
                name=pname,
                type="box",
                pos=f"{px:.2f} 0 {pz / 2.0:.3f}",
                size=f"{plen / 2.0:.2f} 1.10 {pz / 2.0:.3f}",
                contype="1",
                conaffinity="2",
                rgba=rgba,
                group="1",
            )
    elif scene_name != "flat":
        raise ValueError(f"Unknown scene_name: {scene_name!r}")

    out_xml = cache_dir / f"mod4v3_high_jump_{scene_name}.xml"
    tree.write(out_xml, encoding="utf-8", xml_declaration=True)
    return out_xml


class HighJumpController:
    """4-stage Deep-Crouch High Jump & Moving Jump state machine layered seamlessly over c874."""

    def __init__(self, default_active: torch.Tensor, cfg: HighJumpConfig | None = None):
        self.cfg = cfg or HighJumpConfig()
        self.default = default_active.detach().cpu().numpy().astype(np.float64)
        self.reset()

    def reset(self) -> None:
        self.phase: str = "DRIVE"
        self.phase_t0: float = 0.0
        self.hold_charge: bool = False
        self.crouch_cmd_delta = np.full(2, 1.0, dtype=np.float64)
        self.push_vx: float = 0.0
        self.air_substeps: int = 0
        self.support_substeps: int = 8
        self.jump_requests: int = 0
        self.completed_jumps: list[dict[str, Any]] = []
        self._cur_jump: dict[str, Any] | None = None

    @property
    def phase_index(self) -> int:
        return PHASES.index(self.phase)

    @property
    def active(self) -> bool:
        return self.phase != "DRIVE"

    def request_jump(self, now: float, hold_charge: bool = False) -> bool:
        """Trigger a high jump (works from DRIVE or near the end of SKYHOOK_ABSORB for continuous multi-jump!)."""
        can_retrigger = (
            self.phase == "DRIVE"
            or (self.phase == "SKYHOOK_ABSORB" and (now - self.phase_t0) >= 0.18 and self.support_substeps >= 4)
        )
        if not can_retrigger:
            return False
        if self._cur_jump is not None:
            self._finalize_jump(now, "chained_into_next_jump")
        self.hold_charge = bool(hold_charge)
        self.phase = "CROUCH"
        self.phase_t0 = float(now)
        self._crouch_initialized = False
        self.jump_requests += 1
        self._cur_jump = {
            "jump_id": self.jump_requests,
            "t_request": round(float(now), 4),
            "z_min_m": 999.0,
            "rim_peak_m": 0.0,
            "com_min_m": 999.0,
            "com_peak_m": 0.0,
            "air_s": 0.0,
            "air_pitch_deg": 0.0,
            "air_roll_deg": 0.0,
            "post_pitch_deg": 0.0,
        }
        return True

    def release_charge(self, now: float) -> bool:
        """Release manual Hold-Crouch charge so compute_action fires PUSH cleanly with current push_vx."""
        if not self.hold_charge:
            return False
        self.hold_charge = False
        return True

    def _enter_phase(self, new_phase: str, now: float) -> None:
        self.phase = new_phase
        self.phase_t0 = float(now)

    def _finalize_jump(self, now: float, status: str) -> None:
        if self._cur_jump is None:
            return
        rec = self._cur_jump
        rec["t_end"] = round(float(now), 4)
        rec["status"] = status
        rec["rim_peak_cm"] = round(rec["rim_peak_m"] * 100.0, 2)
        rec["com_rise_cm"] = round(max(0.0, rec["com_peak_m"] - rec["com_min_m"]) * 100.0, 2)
        self.completed_jumps.append(rec)
        self._cur_jump = None

    def update_substep_contacts(
        self,
        total_force_N: float,
        wheel_normal_N: float,
        rim_clearance_m: float,
        root_z_m: float,
        com_z_m: float,
        pitch_deg: float,
        roll_deg: float,
        dt_sub: float,
    ) -> None:
        """Update 400 Hz contact/airborne counters and per-jump telemetry."""
        if total_force_N < 1.0:
            self.air_substeps += 1
            self.support_substeps = 0
        else:
            self.air_substeps = 0
            if wheel_normal_N > 5.0:
                self.support_substeps += 1

        if self._cur_jump is not None:
            j = self._cur_jump
            if self.phase in ("CROUCH", "PUSH"):
                j["z_min_m"] = min(j["z_min_m"], float(root_z_m))
                j["com_min_m"] = min(j["com_min_m"], float(com_z_m))
            if self.air_substeps >= 1 and self.phase in ("PUSH", "FLIGHT_EXTEND", "FLIGHT_TUCK", "LANDING_EXTEND"):
                j["air_s"] = round(j["air_s"] + dt_sub, 6)
                j["rim_peak_m"] = max(j["rim_peak_m"], float(rim_clearance_m))
                j["com_peak_m"] = max(j["com_peak_m"], float(com_z_m))
                j["air_pitch_deg"] = max(j["air_pitch_deg"], abs(float(pitch_deg)))
                j["air_roll_deg"] = max(j["air_roll_deg"], abs(float(roll_deg)))
            elif self.phase == "SKYHOOK_ABSORB":
                j["post_pitch_deg"] = max(j["post_pitch_deg"], abs(float(pitch_deg)))

    def compute_action(
        self,
        now: float,
        raw_action: torch.Tensor,
        q_legs: np.ndarray,
        qd_wheels: np.ndarray,
        root_z: float,
        root_vz: float,
        body_vx: float,
        cmd_vx_slewed: float,
        pitch: float,
        roll: float,
        wx: float,
        wy: float,
    ) -> torch.Tensor:
        """Overlay 4-stage high-jump commands onto c874's raw 6-D PPO action within [-6, 6]."""
        cfg = self.cfg
        default = self.default
        raw_np = raw_action[0].detach().cpu().numpy().astype(np.float64)

        raw_mean = np.array(
            [
                0.5 * (default[0] + 0.5 * raw_np[0] + default[1] + 0.5 * raw_np[1]),
                0.5 * (default[2] + 0.5 * raw_np[2] + default[3] + 0.5 * raw_np[3]),
            ],
            dtype=np.float64,
        )
        raw_delta = np.clip(
            [
                (default[0] + 0.5 * raw_np[0]) - (default[1] + 0.5 * raw_np[1]),
                (default[2] + 0.5 * raw_np[2]) - (default[3] + 0.5 * raw_np[3]),
            ],
            *LEG_DELTA_BOUNDS,
        )

        if self.phase == "CROUCH" and not getattr(self, "_crouch_initialized", True):
            self.crouch_cmd_delta = raw_delta.copy()
            self._crouch_initialized = True

        elapsed = float(now) - self.phase_t0

        # Advance 4-stage state machine
        if self.phase == "CROUCH":
            if not self.hold_charge:
                ready = (
                    elapsed >= cfg.compress_s and self.support_substeps >= cfg.min_crouch_support_substeps
                ) or (elapsed >= cfg.compress_s + cfg.max_compress_wait_s)
                if ready:
                    self.push_vx = float(body_vx)
                    self._enter_phase("PUSH", now)
                    elapsed = 0.0
        elif self.phase == "PUSH":
            if (
                self.air_substeps >= cfg.air_confirm_substeps
                and root_vz > cfg.liftoff_min_vz_m_s
                and elapsed >= 0.04
            ):
                next_ph = "FLIGHT_EXTEND" if cfg.extend_air_s > 0.0 else "FLIGHT_TUCK"
                self._enter_phase(next_ph, now)
                elapsed = 0.0
            elif elapsed >= cfg.push_s:
                self._finalize_jump(now, "push_timeout_aborted")
                self._enter_phase("DRIVE", now)
                elapsed = 0.0
        elif self.phase == "FLIGHT_EXTEND":
            if elapsed >= cfg.extend_air_s:
                self._enter_phase("FLIGHT_TUCK", now)
                elapsed = 0.0
        elif self.phase == "FLIGHT_TUCK":
            if elapsed >= cfg.tuck_min_s and (root_vz <= cfg.preland_vz_m_s or elapsed >= cfg.tuck_max_s):
                self._enter_phase("LANDING_EXTEND", now)
                elapsed = 0.0
        elif self.phase == "LANDING_EXTEND":
            if self.support_substeps >= 1 and elapsed >= 0.02:
                self._enter_phase("SKYHOOK_ABSORB", now)
                elapsed = 0.0
            elif elapsed > 0.65:
                self._finalize_jump(now, "air_timeout")
                self._enter_phase("DRIVE", now)
                elapsed = 0.0
        elif self.phase == "SKYHOOK_ABSORB":
            if elapsed >= cfg.skyhook_s:
                self._finalize_jump(now, "completed")
                self._enter_phase("DRIVE", now)
                elapsed = 0.0

        if self.phase == "DRIVE":
            return raw_action.clamp(-ACTION_CLIP, ACTION_CLIP)

        act = raw_action.clone()
        cur_actual_delta = 0.5 * float((q_legs[0] - q_legs[1]) + (q_legs[2] - q_legs[3]))

        # 1. Symmetric leg extension/compression delta
        if self.phase == "CROUCH":
            base_c = cfg.crouch_delta_rad + (0.10 if self.hold_charge else 0.0)
            c_target = base_c + cfg.crouch_speed_delta_k * abs(float(body_vx))
            max_step = cfg.crouch_rate_rad_s * CONTROL_DT
            self.crouch_cmd_delta = self.crouch_cmd_delta + np.clip(
                c_target - self.crouch_cmd_delta, -max_step, max_step
            )
            delta = self.crouch_cmd_delta.copy()
        elif self.phase in ("PUSH", "FLIGHT_EXTEND"):
            delta = np.full(2, cfg.push_delta_rad, dtype=np.float64)
        elif self.phase == "FLIGHT_TUCK":
            alpha = min(1.0, elapsed / max(cfg.tuck_ramp_s, 0.01))
            delta = np.full(
                2, cfg.push_delta_rad + (cfg.tuck_delta_rad - cfg.push_delta_rad) * alpha, dtype=np.float64
            )
        elif self.phase == "LANDING_EXTEND":
            alpha = min(1.0, elapsed / max(cfg.land_ramp_s, 0.02))
            delta = np.full(
                2, cfg.tuck_delta_rad + (cfg.land_delta_rad - cfg.tuck_delta_rad) * alpha, dtype=np.float64
            )
        else:  # SKYHOOK_ABSORB
            fade = max(0.0, 1.0 - elapsed / max(cfg.skyhook_s, 0.02))
            down_vz = max(0.0, -float(root_vz))
            skyhook_add = cfg.skyhook_kd * down_vz
            z_guard = fade * cfg.z_guard_kp * max(0.0, cfg.z_guard_ref_m - float(root_z))
            delta = raw_delta + skyhook_add + z_guard

        delta = np.asarray(delta, dtype=np.float64).clip(*LEG_DELTA_BOUNDS)

        # 2. Hip swing mean (preserving c874 balance on ground, speed-compensated angular momentum in air)
        mean = raw_mean.copy()
        if self.phase == "PUSH":
            k_spd = cfg.push_speed_mean_k if self.push_vx >= 0.0 else 0.044
            mean = mean + cfg.push_mean_bias_rad + k_spd * self.push_vx
        elif self.phase == "FLIGHT_TUCK":
            mean = mean + cfg.tuck_mean_bias_rad
        elif self.phase == "LANDING_EXTEND":
            raibert_air = (
                neutral_4bar_mean(cur_actual_delta)
                - cfg.air_raibert_pitch_k * pitch
                - cfg.air_raibert_vx_k * float(body_vx)
                - cfg.air_raibert_err_k * (float(body_vx) - float(cmd_vx_slewed))
                + cfg.air_raibert_bias_rad
            )
            w_r_max = np.clip(
                cfg.air_raibert_w_base - cfg.air_raibert_w_speed_k * max(0.0, float(body_vx)),
                0.50,
                0.82,
            )
            w_r = float(w_r_max) * min(1.0, elapsed / 0.06)
            mean = (1.0 - w_r) * raw_mean + w_r * np.full(2, raibert_air)
        # Note: in CROUCH and SKYHOOK_ABSORB, mean == raw_mean so c874 controls ground traction/pitch seamlessly!

        for i, (f_idx, r_idx) in enumerate(((0, 1), (2, 3))):
            act[0, f_idx] = float(2.0 * (mean[i] + 0.5 * delta[i] - default[f_idx]))
            act[0, r_idx] = float(2.0 * (mean[i] - 0.5 * delta[i] - default[r_idx]))

        # 3. Active mid-air wheel + 4-bar leg attitude stabilization
        if self.phase in ("FLIGHT_EXTEND", "FLIGHT_TUCK", "LANDING_EXTEND") and self.air_substeps >= 1:
            p_ref = cfg.air_pitch_ref_rad if self.phase == "FLIGHT_TUCK" else 0.0
            p_err = float(pitch) - p_ref
            body_pitch_tau = -cfg.pitch_kp * p_err - cfg.pitch_kd * float(wy)
            motor_tau_each = -0.5 * body_pitch_tau
            w_target = qd_wheels + motor_tau_each / 0.6
            act[0, 4:] = torch.as_tensor(w_target / ACTION_SCALE_WHEEL, dtype=act.dtype, device=act.device)

            roll_corr = float(np.clip(cfg.roll_kp * float(roll) + cfg.roll_kd * float(wx), -0.15, 0.15))
            new_delta = np.clip(delta + np.array([-roll_corr, roll_corr]), *LEG_DELTA_BOUNDS)
            for i, (f_idx, r_idx) in enumerate(((0, 1), (2, 3))):
                chg = float(new_delta[i] - delta[i])
                act[0, f_idx] += chg
                act[0, r_idx] -= chg

            leg_pitch = float(np.clip(cfg.leg_pitch_kp * p_err + cfg.leg_pitch_kd * float(wy), -0.42, 0.42))
            act[:, :4] += 2.0 * leg_pitch

        return act.clamp(-ACTION_CLIP, ACTION_CLIP)


class HighJumpSimulation:
    """Complete MuJoCo simulation binding MOD4v3 HW300N60_R3 + frozen c874 + HighJumpController."""

    def __init__(
        self,
        scene_name: str = "flat",
        cfg: HighJumpConfig | None = None,
        visible: bool = False,
        cache_dir: Path | None = None,
    ):
        self.identities = verify_source_identities()
        self.cfg = cfg or HighJumpConfig()
        self.scene_name = scene_name
        self.cache_dir = cache_dir or (HERE / "runtime_scenes")
        self.xml_path = build_jump_scene_xml(scene_name, self.cache_dir)

        torch.set_num_threads(1)
        ck = torch.load(CKPT_SOURCE, map_location="cpu", weights_only=False)
        template = json.loads(TEMPLATE_SOURCE.read_text(encoding="utf-8"))
        self.spec = RobotSpec(**template["spec"])
        runtime = json.loads(RUNTIME_SOURCE.read_text(encoding="utf-8"))
        semantics = json.loads(SEMANTICS_SOURCE.read_text(encoding="utf-8"))
        bank = json.loads(BANK_SOURCE.read_text(encoding="utf-8"))

        self.default_q = _q_from_runtime(runtime, self.spec.joint_names)
        self.bank_q, self.bank_z = _q_from_bank(bank, semantics, self.spec.joint_names)
        self.order = list(ck["action_order"])
        expected_order = [
            "left_front1_joint",
            "left_rear1_joint",
            "right_front1_joint",
            "right_rear1_joint",
            "left_wheel_joint",
            "right_wheel_joint",
        ]
        if self.order != expected_order:
            raise ValueError(f"Unexpected action_order: {self.order}")

        self.actor = ActorMLP()
        missing, unexpected = self.actor.load_state_dict(ck["actor_state_dict"], strict=False)
        if missing or not (set(unexpected) <= {"distribution.std_param"}):
            raise RuntimeError(f"Unexpected actor state dict keys: missing={missing}, unexpected={unexpected}")
        self.actor.eval()

        self.env = Mod4v3Mujoco(
            str(self.xml_path),
            self.spec,
            self.default_q,
            self.bank_q,
            self.bank_z,
            device="cpu",
            action_clip=ACTION_CLIP,
        )
        assert abs(self.env.dt - 0.0025) < 1e-9 and self.env.decim == 8

        self.ppo_to_env = torch.tensor([0, 2, 1, 3, 4, 5], dtype=torch.long)
        self.default_active = _map(self.default_q, self.spec.joint_names, self.order)
        self.controller = HighJumpController(self.default_active, self.cfg)

        m = self.env.m
        self.pairs = [
            (m.site(e.get("site1")).id, m.site(e.get("site2")).id)
            for e in ET.parse(self.xml_path).getroot().findall("equality/connect")
        ]
        self.mimics = [
            (m.joint(f"{s}_{drv}").qposadr[0], m.joint(f"{s}_{mn}").qposadr[0])
            for s in ("left", "right")
            for drv, mn in (("rear1_drive_joint", "rear1_joint"), ("front1_drive_joint", "front1_joint"))
        ]
        self.wheels = [m.body("left_wheel_link").id, m.body("right_wheel_link").id]
        self.guides = sorted(
            {int(m.geom_bodyid[i]) for i in range(m.ngeom) if (m.geom(i).name or "").startswith("guide_wheel_")}
        )
        self.wheel_dofs = [int(m.joint("left_wheel_joint").dofadr[0]), int(m.joint("right_wheel_joint").dofadr[0])]
        self.leg_qadr = [int(m.joint(n).qposadr[0]) for n in self.order[:4]]
        self.leg_dadr = [int(m.joint(n).dofadr[0]) for n in self.order[:4]]
        self._ray_geomid = np.zeros(1, dtype=np.int32)
        self._local_force = np.zeros(6, dtype=np.float64)

        m.vis.headlight.ambient[:] = [0.62, 0.62, 0.64]
        m.vis.headlight.diffuse[:] = [0.80, 0.80, 0.82]
        m.vis.headlight.specular[:] = [0.10, 0.10, 0.12]

        self.target_height = float(self.cfg.default_cruise_height_m)
        self.height_cmd = 0.28
        self.cmd_vx = 0.0
        self.cmd_vy = 0.0
        self.cmd_wz = 0.0
        self.drive_speed = 0.80
        self.turn_speed = 1.10
        self.paused = False
        self.steps = 0
        self.reset_count = 0
        self.last_reset_reason = ""

        self.a_prev = torch.zeros(1, 6, dtype=torch.float32)
        self.closure_m = 0.0
        self.max_closure_m = 0.0
        self.mimic_rad = 0.0
        self.rim_clearance_m = 0.0
        self.world_rim_z_m = 0.0
        self.pitch_deg = 0.0
        self.roll_deg = 0.0
        self.wheel_force_N = 0.0
        self.guide_force_N = 0.0
        self.chassis_force_N = 0.0

        self.viewer = None
        self.reset_standing()
        if visible:
            import mujoco.viewer

            self.viewer = mujoco.viewer.launch_passive(m, self.env.d)
            self.viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
            self.viewer.cam.trackbodyid = self.env.base_id
            self.viewer.cam.distance = 2.15
            self.viewer.cam.azimuth = 105.0
            self.viewer.cam.elevation = -14.0
            self.viewer.opt.geomgroup[3] = 0
            self.viewer.opt.geomgroup[4] = 0

    def ground_height_at(self, x: float, y: float) -> float:
        """Return exact terrain surface height z (m) below world (x, y) for flat/platforms/hurdles."""
        if self.scene_name == "platforms":
            if abs(y) <= 1.10:
                if 1.60 <= x <= 3.20:
                    return 0.18
                if 3.90 <= x <= 5.70:
                    return 0.34
        elif self.scene_name == "hurdles":
            if abs(y) <= 0.75:
                for hx, hz in ((1.80, 0.14), (4.10, 0.20), (6.50, 0.25)):
                    if abs(x - hx) <= 0.025:
                        return hz
        return 0.0

    def reset_standing(self, x: float = 0.0, y: float = 0.0, yaw: float = 0.0) -> None:
        m, d = self.env.m, self.env.d
        mujoco.mj_resetData(m, d)
        self.env.reset()
        g_z = self.ground_height_at(x, y)
        d.qpos[:3] = [float(x), float(y), g_z + self.bank_z]
        d.qpos[3:7] = [math.cos(yaw / 2.0), 0.0, 0.0, math.sin(yaw / 2.0)]
        d.qvel[:] = 0.0
        d.ctrl[:] = 0.0
        d.time = 0.0
        mujoco.mj_forward(m, d)

        self.a_prev.zero_()
        self.env.a_prev.zero_()
        self.controller.reset()
        self.height_cmd = 0.28
        self.cmd_vx = 0.0
        self.cmd_vy = 0.0
        self.cmd_wz = 0.0
        self.closure_m = max(float(np.linalg.norm(d.site_xpos[u] - d.site_xpos[v])) for u, v in self.pairs)
        self.mimic_rad = max(abs(float(d.qpos[u] - d.qpos[v])) for u, v in self.mimics)
        self.rim_clearance_m = 0.0
        self.world_rim_z_m = 0.0
        self.pitch_deg = 0.0
        self.roll_deg = 0.0
        self.wheel_force_N = 0.0
        self.guide_force_N = 0.0
        self.chassis_force_N = 0.0
        self.reset_count += 1

    def set_target_height(self, h: float) -> None:
        self.target_height = float(np.clip(h, 0.22, 0.42))

    def build_observation(self) -> torch.Tensor:
        """Construct the exact 35-D observation expected by c874."""
        d = self.env.d
        q_all = torch.tensor(d.qpos[self.env.qadr_all], dtype=torch.float32)
        qd_all = torch.tensor(d.qvel[self.env.dadr_all], dtype=torch.float32)
        q = _map(q_all, self.spec.joint_names, self.order)
        qd = _map(qd_all, self.spec.joint_names, self.order)
        R = torch.tensor(np.array(d.xmat[self.env.base_id], dtype=np.float64).reshape(3, 3), dtype=torch.float32)
        gravity_b = R.T @ torch.tensor([0.0, 0.0, -1.0], dtype=torch.float32)
        root_ang_vel_b = torch.tensor(d.qvel[3:6], dtype=torch.float32)
        joint_pos = q - self.default_active
        joint_pos[4:] = 0.0
        mode = torch.zeros(7, dtype=torch.float32)
        mode[0] = 1.0
        return torch.cat(
            (
                torch.tensor([self.cmd_vx, self.cmd_vy, self.cmd_wz], dtype=torch.float32),
                torch.tensor([self.height_cmd * 5.0], dtype=torch.float32),
                root_ang_vel_b * 0.5,
                gravity_b,
                joint_pos,
                qd[:4] * 0.1,
                qd[4:] * 0.1,
                self.a_prev[0],
                mode,
            ),
            0,
        ).unsqueeze(0)

    def step_commands(
        self,
        vx_target: float,
        wz_target: float,
        substep_callback=None,
        auto_reset_on_fall: bool = True,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Execute one 50 Hz policy + HighJumpController step (8 x 2.5 ms = 20 ms MuJoCo physics)."""
        m, d = self.env.m, self.env.d
        now = float(d.time)

        # Slew height command at <= 0.06 m/s (frozen while jump state machine is active so obs[3] never step-jumps)
        if not self.controller.active:
            h_diff = np.clip(
                self.target_height - self.height_cmd,
                -self.cfg.height_slew_m_s * CONTROL_DT,
                self.cfg.height_slew_m_s * CONTROL_DT,
            )
            self.height_cmd = float(np.clip(self.height_cmd + h_diff, 0.20, 0.42))

        alpha = min(1.0, CONTROL_DT / max(self.cfg.cmd_slew_s, 0.02))
        self.cmd_vx += (float(vx_target) - self.cmd_vx) * alpha
        self.cmd_wz += (float(wz_target) - self.cmd_wz) * alpha

        obs = self.build_observation()
        with torch.inference_mode():
            raw_act = self.actor(obs).clamp(-ACTION_CLIP, ACTION_CLIP)

        R = d.xmat[self.env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wx, wy = float(d.qvel[3]), float(d.qvel[4])
        local_g = self.ground_height_at(float(d.qpos[0]), float(d.qpos[1]))
        local_root_z = float(d.qpos[2]) - local_g

        act = self.controller.compute_action(
            now=now,
            raw_action=raw_act,
            q_legs=d.qpos[self.leg_qadr],
            qd_wheels=d.qvel[self.wheel_dofs],
            root_z=local_root_z,
            root_vz=float(d.qvel[2]),
            body_vx=float(self.env.vx),
            cmd_vx_slewed=self.cmd_vx,
            pitch=pitch,
            roll=roll,
            wx=wx,
            wy=wy,
        )

        a_env = act[:, self.ppo_to_env]
        fell_reason = ""
        for j in range(self.env.decim):
            tau = self.env._torque(a_env).detach().numpy().reshape(-1)
            if j % 4 == 0:
                d.ctrl[self.env.act_ids[:4]] = tau[:4]  # 100 Hz leg PD
            d.ctrl[self.env.act_ids[4:]] = tau[4:]      # 400 Hz wheel servo
            mujoco.mj_step(m, d)

            if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():
                fell_reason = "nonfinite_state"
                break

            # Measure contacts & loop closure at 400 Hz
            f_wheel = f_guide = f_chassis = f_total = 0.0
            for ci in range(d.ncon):
                c = d.contact[ci]
                b1, b2 = int(m.geom_bodyid[c.geom1]), int(m.geom_bodyid[c.geom2])
                if (b1 == 0) == (b2 == 0):
                    continue
                rb = b2 if b1 == 0 else b1
                mujoco.mj_contactForce(m, d, ci, self._local_force)
                fnorm = float(np.linalg.norm(self._local_force[:3]))
                f_total += fnorm
                if rb in self.wheels:
                    f_wheel += abs(float(self._local_force[0]))
                elif rb in self.guides:
                    f_guide += fnorm
                elif rb == self.env.base_id:
                    f_chassis += fnorm

            self.wheel_force_N = f_wheel
            self.guide_force_N = f_guide
            self.chassis_force_N = f_chassis

            cl = max(float(np.linalg.norm(d.site_xpos[u] - d.site_xpos[v])) for u, v in self.pairs)
            mm = max(abs(float(d.qpos[u] - d.qpos[v])) for u, v in self.mimics)
            self.closure_m = cl
            self.max_closure_m = max(self.max_closure_m, cl)
            self.mimic_rad = mm
            if cl > 0.010 or mm > 0.010:
                fell_reason = f"closure_exceeded_{cl*1e3:.2f}mm"
                break

            R_sub = d.xmat[self.env.base_id].reshape(3, 3)
            self.pitch_deg = math.degrees(math.asin(float(np.clip(-R_sub[2, 0], -1.0, 1.0))))
            self.roll_deg = math.degrees(math.atan2(float(R_sub[2, 1]), float(R_sub[2, 2])))

            w_pos = d.xpos[self.wheels]
            self.world_rim_z_m = float((w_pos[:, 2] - WHEEL_RADIUS_M).min())
            if self.scene_name == "flat":
                self.rim_clearance_m = self.world_rim_z_m
                sub_g = 0.0
            else:
                g_wheels = [self.ground_height_at(float(w[0]), float(w[1])) for w in w_pos]
                self.rim_clearance_m = float((w_pos[:, 2] - np.asarray(g_wheels) - WHEEL_RADIUS_M).min())
                sub_g = self.ground_height_at(float(d.qpos[0]), float(d.qpos[1]))

            self.controller.update_substep_contacts(
                total_force_N=f_total,
                wheel_normal_N=f_wheel,
                rim_clearance_m=self.world_rim_z_m if self.scene_name == "flat" else max(self.rim_clearance_m, 0.0),
                root_z_m=float(d.qpos[2]) - sub_g,
                com_z_m=float(d.subtree_com[self.env.base_id, 2]) - sub_g,
                pitch_deg=self.pitch_deg,
                roll_deg=self.roll_deg,
                dt_sub=self.env.dt,
            )
            if substep_callback is not None:
                substep_callback(self, j)

        self.a_prev = act.detach()
        self.env.a_prev = a_env.detach()
        self.steps += 1

        local_z_now = float(d.qpos[2]) - self.ground_height_at(float(d.qpos[0]), float(d.qpos[1]))
        if not fell_reason and (self.env.cos_tilt < 0.50 or local_z_now < 0.12):
            fell_reason = "fall_guard"

        if fell_reason:
            self.last_reset_reason = fell_reason
            if auto_reset_on_fall:
                self.reset_standing()

        return obs, act

    def step_keys(self, pressed: set[str]) -> dict[str, Any]:
        """Step simulation from interactive WASD/QE/Jump key set."""
        if self.paused:
            return self.telemetry()
        if "q" in pressed:
            self.set_target_height(self.target_height - 0.14 * CONTROL_DT)
        if "e" in pressed:
            self.set_target_height(self.target_height + 0.14 * CONTROL_DT)

        vx_t = self.drive_speed * (float("w" in pressed) - float("s" in pressed))
        wz_t = self.turn_speed * (float("a" in pressed) - float("d" in pressed))
        self.step_commands(vx_t, wz_t, auto_reset_on_fall=True)
        return self.telemetry()

    def telemetry(self) -> dict[str, Any]:
        d = self.env.d
        last_jump = self.controller.completed_jumps[-1] if self.controller.completed_jumps else None
        cur_jump = self.controller._cur_jump
        peak_cm = (
            cur_jump["rim_peak_m"] * 100.0
            if cur_jump is not None and cur_jump["rim_peak_m"] > 0
            else (last_jump["rim_peak_cm"] if last_jump else 0.0)
        )
        return {
            "time_s": round(float(d.time), 3),
            "scene": self.scene_name,
            "phase": self.controller.phase,
            "hold_charge": self.controller.hold_charge,
            "z_m": round(float(d.qpos[2]), 3),
            "vx_m_s": round(float(self.env.vx), 2),
            "cmd_vx_m_s": round(self.cmd_vx, 2),
            "cmd_wz_rad_s": round(self.cmd_wz, 2),
            "height_cmd_m": round(self.height_cmd, 3),
            "target_height_m": round(self.target_height, 3),
            "pitch_deg": round(self.pitch_deg, 2),
            "roll_deg": round(self.roll_deg, 2),
            "rim_clearance_cm": round(max(0.0, self.rim_clearance_m) * 100.0, 1),
            "world_rim_cm": round(max(0.0, self.world_rim_z_m) * 100.0, 1),
            "peak_rim_cm": round(float(peak_cm), 1),
            "closure_mm": round(self.closure_m * 1000.0, 3),
            "max_closure_mm": round(self.max_closure_m * 1000.0, 3),
            "jump_requests": self.controller.jump_requests,
            "completed_jumps": len(self.controller.completed_jumps),
            "last_jump": last_jump,
            "resets": self.reset_count - 1,
            "paused": self.paused,
        }

    def close(self) -> None:
        if self.viewer is not None:
            try:
                self.viewer.close()
            except Exception:
                pass
            self.viewer = None

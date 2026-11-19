# SPDX-License-Identifier: MIT
"""Use the existing MOD4v3 plant and maps with autonomous deployment inference."""
from __future__ import annotations

import sys
from typing import Any

import mujoco as mj
import numpy as np
import torch

from autonomous_three_expert import HERE, LOCAL, SOURCE_SHA, jump

LEGACY_PLAYER = LOCAL / "MOD4V3_UNIFIED_MOE_ALL_MAPS_PLAYER_20261118"
sys.path.insert(0, str(LEGACY_PLAYER))
import map_builders as maps  # noqa: E402
from play_unified_moe_all_maps import (  # noqa: E402
    CONTROL_DT, HEIGHT_MAX, HEIGHT_MIN, PPO_TO_NATIVE, SERIAL_SUB_SCENES,
    UnifiedMoESimulation,
)

maps.CACHE_DIR = HERE / "runtime_cache"
STAIR_SCENES = (
    "20 cm 单阶", "24 cm 高台", "16 cm 高台", "15 cm 单阶",
    "10 cm 单阶", "5 cm 单阶", "20 + 20 cm 连续双阶",
)
MOTION_KEYS = {"w", "s", "a", "d", "q", "e"}


def map_for(suite: int, scene: str = "", level: int = 4) -> dict[str, Any]:
    if suite == 0:
        meta = maps.build_proving_ground()
        labels = (
            ("20 / 40 cm 连续双阶", "按住 W。路由器自动上阶，登顶起身后继续前进。"),
            ("20 cm 高台跳跃道", "可以在不同距离按空格试跳。保持 W 可在落地后接着前进。"),
            ("24 cm 高台跳跃道", "可以在不同距离按空格试跳。"),
            ("20 cm 单阶自动攀爬", "保持标准站高，按住 W 直行，留意 E1 权重和登顶后回到 E0。"),
            ("限高杆与连续阶梯", "按 1 压低车身钻杆，按 2 恢复标准站高。"),
        )
        for spawn, (name, hint) in zip(meta["spawns"], labels, strict=True):
            spawn.update(name=name, hint=hint)
        return meta
    if suite == 1:
        return maps.build_rmuc2027()
    if suite == 2:
        return maps.build_parkour_sirina()
    if suite == 3:
        meta = maps.build_serial_leg_course(scene or SERIAL_SUB_SCENES[0])
        if len(meta["spawns"]) == 1:
            meta["spawns"][0]["hint"] = "按住 W 自动判断攀爬，空格发出跳跃指令。"
        return meta
    if suite == 4:
        meta = maps.build_stairs_matrix(scene or STAIR_SCENES[0])
        meta["spawns"][0]["hint"] = "按住 W 自动判断攀爬，空格发出跳跃指令。"
        meta["spawns"][1].update(
            name="近阶跳跃试验起点", hint="空格跳跃，也可以调整距离或助跑再跳。"
        )
        return meta
    if suite == 5:
        return maps.build_rough_v1_tile(scene or maps.ROUGH_CN[0], level)
    raise ValueError(f"Unknown map suite {suite}")


class AutonomousMapSimulation(UnifiedMoESimulation):
    def __init__(self, policy, sha: str, *, show_viewer: bool = True) -> None:
        super().__init__(policy, sha, show_viewer=show_viewer)
        self.route = {"e0": 1.0, "e1": 0.0, "e2": 0.0}
        self.max_vx = 0.90
        self.last_obs: np.ndarray | None = None

    def reset_at_spawn(self, spawn_idx: int | None = None) -> dict[str, Any]:
        spawn = super().reset_at_spawn(spawn_idx)
        self.route = {"e0": 1.0, "e1": 0.0, "e2": 0.0}
        self.last_obs = None
        self.peak_rim_clearance_cm = 0.0
        self.max_air_pitch_deg = 0.0
        return spawn

    def request_jump(self) -> bool:
        if self.jump_rem:
            return False
        # The key issues the same 45-frame request used during E2 training.
        self.jump_rem = jump.GATE_STEPS
        self.jump_count += 1
        self.jump_launch_gz = self.ground_z(*self.d.qpos[:2])
        self.peak_rim_clearance_cm = 0.0
        self.max_air_pitch_deg = 0.0
        return True

    def _observe(self, jump_requested: bool) -> np.ndarray:
        rotation = self.d.xmat[self.env.base_id].reshape(3, 3)
        q = self.d.qpos[self.qa] - self.baseline
        q[4:] = 0.0  # Wheel position is cyclic and masked in both experts.
        return np.concatenate((
            [self.cmd_vx, 0.0, self.cmd_wz, self.target_h * 5.0],
            self.d.qvel[3:6] * 0.5,
            -rotation[2, :],
            q,
            self.d.qvel[self.va] * 0.1,
            self.prev_a,
            [1.0, 0.0, float(jump_requested), 0.0, 0.0, 0.0, 0.0],
        ), dtype=np.float32)

    def step(self, pressed: set[str]) -> None:
        if self.paused:
            return
        forward = int("w" in pressed) - int("s" in pressed)
        turn = int("a" in pressed) - int("d" in pressed)
        raise_lower = int("e" in pressed) - int("q" in pressed)
        self.target_h = float(np.clip(self.target_h + raise_lower * 0.12 * CONTROL_DT, HEIGHT_MIN, HEIGHT_MAX))
        vx_goal = self.max_vx if forward > 0 else min(self.max_vx, 0.85) * forward
        self.cmd_vx += (vx_goal - self.cmd_vx) * CONTROL_DT / 0.14
        self.cmd_wz += (self.max_wz * turn - self.cmd_wz) * CONTROL_DT / 0.14

        jump_requested = self.jump_rem > 0
        obs = self._observe(jump_requested)
        self.last_obs = obs
        action, self.route = self.unified.act(obs)
        if not np.isfinite(action).all():
            raise RuntimeError("Non-finite MOD4v3 policy action")
        native_action = torch.from_numpy(action[PPO_TO_NATIVE]).reshape(1, 6)
        for substep in range(self.env.decim):
            torque = self.env._torque(native_action).numpy().reshape(-1)
            if substep % 4 == 0:
                self.d.ctrl[self.env.act_ids[:4]] = torque[:4]
            self.d.ctrl[self.env.act_ids[4:]] = torque[4:]
            mj.mj_step(self.m, self.d)

        # There is no action-delay in the interactive plant. Store the action that was applied.
        self.prev_a = action
        self.steps += 1
        if jump_requested:
            self.jump_rem -= 1
            rim = min(self.d.geom_xpos[self.tire_gids, 2]) - 0.0625 - self.jump_launch_gz
            self.peak_rim_clearance_cm = max(self.peak_rim_clearance_cm, 100.0 * float(rim))
            if rim > 0.03:
                r = self.d.xmat[self.env.base_id].reshape(3, 3)
                pitch = np.degrees(np.arcsin(np.clip(-r[2, 0], -1.0, 1.0)))
                self.max_air_pitch_deg = max(self.max_air_pitch_deg, abs(float(pitch)))

        self.closure_mm = 1000.0 * max(float(np.linalg.norm(self.d.site_xpos[a] - self.d.site_xpos[b])) for a, b in self.pairs)
        if (not np.isfinite(self.d.qpos).all() or not np.isfinite(self.d.qvel).all()
                or self.closure_mm > 1000.0 or self.d.qpos[2] < -1.5):
            self.reset_at_spawn()

    def telemetry(self) -> dict[str, Any]:
        data = super().telemetry()
        data.pop("stair_mode")
        data.pop("stair_park")
        e1 = self.route["e1"]
        if self.route["e2"]:
            expert = "E2 跳跃"
        elif e1 > 0:
            expert = f"E0 / E1 上阶混合 · E1 {e1:.0%}"
        else:
            expert = "E0 巡航"
        data.update(
            expert=expert,
            router={key: round(value, 5) for key, value in self.route.items()},
            source_sha256=SOURCE_SHA,
        )
        return data

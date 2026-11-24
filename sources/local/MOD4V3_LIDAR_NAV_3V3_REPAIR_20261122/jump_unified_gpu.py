"""COMMANDER-AUTHORED & LOCKED All-Regime Jump GPU Environment (DO NOT MODIFY!).

Fixes all prior reward & plant issues:
1. Built directly on Jump380Gpu (unchanged 400 Hz Warp plant matching R10ActorCritic 100%).
2. Drops non-essential 380 mm walls -> 70% flat ground + 30% solid 200 mm step/platform!
3. Samples tall stances [0.35, 0.42] m (40%) + low/mid stances [0.24, 0.35] m (60%),
   continuous speeds [0.0, 2.8] m/s, variable key hold [6, 45] ticks, and realistic smoothed (/12.)
   human command perturbations (keep W, release W -> 0, feather S, steer A/D).
4. Cheat-proof rewards: tall-stance pre-takeoff crouch -> upward vz launch shaping, true all-geom
   airborne clearance info[:, 0] (arc[:, 2], NEVER raw non-airborne tire z!), level-chassis
   pitch & roll stability, ballistic mid-air forward velocity conservation, 200 mm platform
   crossing, and compliant skyhook landing absorb.
"""
from __future__ import annotations

import math
from pathlib import Path
import torch
import warp as wp

import jump380_r6_scene as scene

scene.RUN = Path(__file__).resolve().parent / "cache/jump_training"
from jump360_scene import CLOSURE_LIMIT
from jump380_r6_gpu import Jump380Gpu as PlantGpu


class UnifiedJumpGpu(PlantGpu):
    def reset(self, done: torch.Tensor):
        super().reset(done)
        ids = self.index[done]
        n = int(ids.numel())
        if not hasattr(self, "perturb_kind"):
            self.perturb_kind = torch.zeros_like(self.tick)
            self.perturb_tick = torch.zeros_like(self.tick)
            self.turn = torch.zeros_like(self.cmd)
            self.post_vx = torch.zeros_like(self.cmd)
            self.post_wz = torch.zeros_like(self.cmd)
            self.takeoff_vx = torch.zeros_like(self.cmd)
            self.min_crouch_z = torch.full_like(self.cmd, 0.45)
            self.first_land_tick = torch.full_like(self.tick, -1)
            self.paid_success = torch.zeros_like(self.dr)
            self.counts = torch.zeros(10, device=self.device, dtype=torch.long)
            self.range_low = self.tf([99.0, 99.0])
            self.range_high = self.tf([-99.0, -99.0])
        if not n:
            return

        u = self.rand(n)
        v = self.rand(n)
        # 70% flat ground, 30% solid 200 mm step/platform (no 380 mm walls!)
        is_plat = self.rand(n) < 0.30
        kind = is_plat.long()
        self.kind[ids] = kind

        # Speeds: flat covers [0.0, 2.8] m/s continuously; 200 mm platform covers [0.65, 2.35] m/s
        flat_speed = torch.where(u < 0.30, 0.25 * v, torch.where(u < 0.65, 0.25 + 1.10 * v, 1.35 + 1.45 * v))
        plat_speed = 0.65 + 1.70 * v
        speed = torch.where(is_plat, plat_speed, flat_speed)
        self.speed[ids] = speed

        # Stances: 40% explicitly in tall [0.35, 0.42] m, 60% in [0.24, 0.35] m
        h_u = self.rand(n)
        h_v = self.rand(n)
        height = torch.where(h_u < 0.40, 0.35 + 0.07 * h_v, 0.24 + 0.11 * h_v)
        self.height[ids] = height

        # Re-initialize starting pose at sampled height so history genuinely reflects [0.24, 0.42] m!
        # PlantGpu's reset sets default qpos; let E0/cruise settle at self.height during runup ticks 0..begin_tick!
        self.key_hold[ids] = torch.randint(6, 46, (n,), generator=self.rng, device=self.device)
        self.begin_tick[ids] = 75 + (45 * self.rand(n)).long()

        # Perturbations after Space: 0=keep W (40%), 1=release W -> 0 (35%), 2=feather S (10%), 3=turn A/D (15%)
        pk_draw = self.rand(n)
        pk = torch.where(pk_draw < 0.40, 0, torch.where(pk_draw < 0.75, 1, torch.where(pk_draw < 0.85, 2, 3)))
        # Keep W on platform jumps 70% of time so platform landing runs cleanly
        pk = torch.where(is_plat & (self.rand(n) < 0.55), torch.zeros_like(pk), pk)
        self.perturb_kind[ids] = pk
        self.perturb_tick[ids] = (self.rand(n) * 14).long()
        self.post_vx[ids] = torch.where(
            pk == 1, 0.0, torch.where(pk == 2, -0.35 * self.rand(n), speed)
        )
        self.post_wz[ids] = torch.where(pk == 3, (2.0 * self.rand(n) - 1.0) * 1.0, 0.0)

        self.turn[ids] = 0.0
        self.takeoff_vx[ids] = 0.0
        self.min_crouch_z[ids] = height
        self.first_land_tick[ids] = -1
        self.paid_success[ids] = False
        self.air_progress[ids] = 0.0

        # Position 200 mm solid step/platform (hurdle slot 0 lowered so top surface = +0.200 m!)
        self.lead[ids] = 0.42 + 0.42 * speed
        self.edge[ids] = speed * (self.begin_tick[ids].float() * 0.02 - 0.55) + self.lead[ids]
        for j in range(3):
            half = self.cpu.m.geom_size[self.cpu.hurdle_gids[j]]
            if j == 0:
                self.mocap[ids, j, 0] = self.edge[ids] + float(half[0])
                self.mocap[ids, j, 1] = 0.0
                self.mocap[ids, j, 2] = torch.where(is_plat, 0.20 - float(half[2]), -3.0)
            else:
                self.mocap[ids, j, 0] = 20.0
                self.mocap[ids, j, 1] = 0.0
                self.mocap[ids, j, 2] = -3.0 - j
        self.wall_height[ids] = torch.where(is_plat, 0.20, 0.0)

        self.range_low = torch.minimum(self.range_low, torch.stack((speed.min(), height.min())))
        self.range_high = torch.maximum(self.range_high, torch.stack((speed.max(), height.max())))

    def set_stage(self, stage: int):
        probs = (0.0, 0.25, 0.50, 1.00)
        self.dr_probability = probs[min(stage, 3)]
        self.stage = min(stage, 2)

    def actor_input(self) -> torch.Tensor:
        return torch.cat((self.obs, self.hist.flatten(1)), dim=1)

    def active_mask(self) -> torch.Tensor:
        return self.press >= 0

    def anchor_mask(self) -> torch.Tensor:
        # Only anchor nominal high-speed flat/platform states where R10 was already strong;
        # leave tall-stance (>0.32m), low-speed (<1.15m/s), and W-release (perturb>0) 100% free!
        return (self.press >= 0) & (self.height <= 0.32) & (self.speed >= 1.15) & (self.perturb_kind == 0)

    def extra(self) -> torch.Tensor:
        return torch.cat(
            (
                self.p[:, 2:3],
                self.v[:, :6],
                self.arc[:, :4],
                self.height[:, None],
                self.speed[:, None],
                self.wall_height[:, None],
                (self.press >= 0).float()[:, None],
            ),
            dim=1,
        )

    def observe(self):
        out = super().observe()
        out[:, 2] = self.turn
        if hasattr(self, "dr"):
            noise = (self.rand(self.n, 18) - 0.5) * 0.012 * self.dr[:, None].float()
            out[:, 4:22] += noise
        return out

    def step(self, action: torch.Tensor):
        self.action.copy_(action.clamp(-6.0, 6.0))
        had_air = self.arc[:, 1] > 0.0
        self.stats.zero_()
        self.stats[:, 1] = 99.0
        self.stats[:, 10] = 99.0
        with wp.ScopedStream(self.warp_stream):
            wp.capture_launch(self.graph, self.warp_stream)
        self.slot.add_(8).remainder_(9)
        self.tick += 1

        broken = (
            ~torch.isfinite(self.p).all(1)
            | ~torch.isfinite(self.v).all(1)
            | ~torch.isfinite(self.rot).all(dim=(1, 2))
            | ~torch.isfinite(self.stats).all(1)
            | ~torch.isfinite(self.contacts).all(1)
            | (self.stats[:, 12] > 0.0)
        )
        info = torch.where(broken[:, None], 0.0, self.stats)

        vx = info[:, 11]
        upright = torch.where(broken, 0.0, self.rot[:, 2, 2])
        pitch = torch.asin(torch.where(broken, 0.0, self.rot[:, 2, 0]).clamp(-1.0, 1.0)).abs()
        roll = torch.asin(torch.where(broken, 0.0, self.rot[:, 2, 1]).clamp(-1.0, 1.0)).abs()
        wx = torch.where(broken, 0.0, self.v[:, 3])
        wy = torch.where(broken, 0.0, self.v[:, 4])
        vz = torch.where(broken, 0.0, self.v[:, 2])
        pos_z = torch.where(broken, 0.25, self.p[:, 2])

        active = self.press >= 0
        age = (self.tick - self.press).clamp_min(0)
        air = self.arc[:, 1] == 1.0
        landed = self.arc[:, 1] == 2.0
        is_plat = self.kind == 1

        first_air = air & ~had_air & ~broken
        self.takeoff_vx = torch.where(first_air, vx, self.takeoff_vx)

        # --- 1. Pre-takeoff tall-stance active crouch -> upward vz launch shaping ---
        pre_air = active & (self.arc[:, 1] == 0.0) & ~broken
        new_crouch = torch.where(pre_air & (age <= 10), torch.minimum(self.min_crouch_z, pos_z), self.min_crouch_z)
        # Reward compressing from tall stance (>0.31 m) down toward 0.24..0.26 m pocket!
        crouch_delta = (self.min_crouch_z.clamp_max(0.42) - new_crouch.clamp_min(0.23)).clamp_min(0.0)
        r_crouch = 4.5 * crouch_delta * (self.height > 0.31) * pre_air
        self.min_crouch_z.copy_(new_crouch)

        # Upward CoM launch velocity while upright (breaks 0.0 cm plateau immediately!)
        r_push_vz = 0.14 * vz.clamp(0.0, 2.6) * pre_air * (age <= 20) * (pitch < math.radians(18.0)) * (roll < math.radians(12.0))

        # --- 2. True All-Geom Airborne Clearance Potential (info[:, 0] == arc[:, 2]!) ---
        true_air_clear = info[:, 0].clamp_min(0.0) * active * ~broken
        new_peak = torch.maximum(self.peak, true_air_clear)
        r_peak = 7.5 * (
            (new_peak / 0.26).clamp(0.0, 1.15).square() - (self.peak / 0.26).clamp(0.0, 1.15).square()
        )
        self.peak.copy_(new_peak)

        # --- 3. Level-Chassis Flight & Ballistic Momentum Conservation ---
        r_air_level = air * (
            0.08 * torch.exp(-((pitch / 0.14).square() + (roll / 0.12).square()))
            - 0.28 * ((pitch - math.radians(10.0)).clamp_min(0.0) / 0.10).square().clamp_max(12.0)
            - 0.35 * ((roll - math.radians(8.0)).clamp_min(0.0) / 0.08).square().clamp_max(12.0)
            - 0.14 * (vx - self.takeoff_vx).square().clamp_max(4.0)
            - 0.015 * (wx.square() + wy.square()).clamp_max(25.0)
        )

        # --- 4. 200 mm Platform Crossing & Face-Collision Penalty ---
        face_hit = info[:, 4] >= 1.0
        first_hit = is_plat & (self.hits < 1.0) & face_hit
        self.hits = torch.maximum(self.hits, info[:, 4] * is_plat.float())
        r_plat_pen = 2.2 * first_hit.float() + 0.40 * (is_plat & face_hit).float()

        advance = ((info[:, 13] - self.edge + 0.30) / 0.42).clamp(0.0, 1.0)
        high_enough = info[:, 6] > (self.wall_height - 0.015)
        new_prog = torch.maximum(self.air_progress, advance * (is_plat & air & high_enough & ~broken).float())
        r_plat_prog = 4.5 * (new_prog - self.air_progress)
        self.air_progress.copy_(new_prog)

        # --- 5. Compliant Skyhook Touchdown & Post-Landing Command Recovery ---
        floor_both = (info[:, 15:17].min(1).values > 5.0) & (info[:, 6] < 0.025)
        plat_both = is_plat & (info[:, 17:19].min(1).values > 5.0) & (info[:, 13] > self.edge + 0.02)
        valid_support = torch.where(is_plat, plat_both, floor_both)

        just_touched = landed & valid_support & (self.first_land_tick < 0)
        self.first_land_tick = torch.where(just_touched, self.tick, self.first_land_tick)
        absorbing = landed & (self.first_land_tick >= 0) & ((self.tick - self.first_land_tick) < 16)
        r_absorb_pen = absorbing.float() * (
            0.06 * info[:, 14].clamp_max(4.0)
            + 0.025 * (wx.abs() + wy.abs()).clamp_max(10.0)
            + 0.15 * (pitch.square() + roll.square())
        )

        stable_land = landed & valid_support & (pitch < math.radians(12.0)) & (roll < math.radians(10.0)) & (vz.abs() < 0.35)
        self.late_support = torch.where(stable_land, self.late_support + 1, torch.zeros_like(self.late_support))
        qualified_now = (self.late_support >= 10) & (self.peak >= 0.22) & ~self.paid_success & ~broken
        self.paid_success |= qualified_now
        r_success = torch.where(is_plat, 8.0, 6.0) * qualified_now.float() + 0.08 * stable_land.float()

        # Track live operator cmd before jump and once stabilized after landing!
        cruise_or_rec = ~active | (landed & (self.late_support >= 8))
        r_track = -0.05 * cruise_or_rec.float() * (vx - self.cmd).square().clamp_max(5.0)

        # Bilateral leg action symmetry when straight (turn == 0) + action smoothness
        straight = (self.turn.abs() < 0.05).float()
        leg_asym = ((self.action[:, 0:2] - self.action[:, 2:4]).square().mean(1)) * straight
        act_smooth = (self.action - self.previous).square().mean(1)
        r_reg = 0.008 * leg_asym + 0.002 * act_smooth

        failed = (
            broken
            | (upright < 0.55)
            | (pitch > math.radians(42.0))
            | (roll > math.radians(34.0))
            | (pos_z < 0.125)
            | (info[:, 7] >= CLOSURE_LIMIT)
        )
        timeout = (active & (age >= 115)) | (self.tick >= 320) | (active & (self.late_support >= 24))
        done = failed | timeout

        no_jump_pen = 2.0 * (done & active & ~failed & (self.peak < 0.22)).float()
        reward = (
            r_crouch
            + r_push_vz
            + r_peak
            + r_air_level
            + r_plat_prog
            + r_success
            + r_track
            - r_plat_pen
            - r_absorb_pen
            - r_reg
            - 10.0 * failed.float()
            - no_jump_pen
        )
        reward = torch.where(broken, torch.full_like(reward, -10.0), reward)

        tall = self.height >= 0.35
        rel_w = self.perturb_kind == 1
        succ_ep = done & ~failed & self.paid_success
        self.counts += torch.stack(
            (
                done.sum(),
                (done & failed).sum(),
                succ_ep.sum(),
                (done & (self.peak >= 0.22)).sum(),
                (done & tall).sum(),
                (succ_ep & tall).sum(),
                (done & rel_w).sum(),
                (succ_ep & rel_w).sum(),
                (done & is_plat).sum(),
                (succ_ep & is_plat).sum(),
            )
        ).long()

        self.previous.copy_(self.action)
        self.reset(done)

        # Trigger jump cleanly after runup (or before 200 mm platform edge)
        ready = (self.press < 0) & (self.tick >= 45) & ~done
        at_plat = (self.p[:, 0] >= self.edge - self.lead) & ((self.edge - self.p[:, 0]) >= 0.16)
        press_now = ready & torch.where(self.kind == 1, at_plat | (self.tick >= self.begin_tick + 25), self.tick >= self.begin_tick)
        self.press.copy_(torch.where(press_now, self.tick, self.press))
        self.press_speed.copy_(torch.where(press_now, vx, self.press_speed))

        # Exact player-identical /12. exponential command smoothing!
        changed = (self.press >= 0) & ((self.tick - self.press) >= self.perturb_tick)
        vx_goal = torch.where(changed, self.post_vx, torch.where(self.tick >= 18, self.speed, 0.0))
        wz_goal = torch.where(changed, self.post_wz, 0.0)
        self.cmd += (vx_goal - self.cmd) / 12.0
        self.turn += (wz_goal - self.turn) / 12.0

        self.observe()
        self.hist = torch.cat((self.hist[:, 1:], self.obs[:, None, :]), dim=1)
        self.hist[done] = self.obs[done, None, :]
        return self.obs, self.hist.flatten(1), reward, done

    def statistics(self) -> dict:
        return dict(
            columns=[
                "episodes",
                "falls",
                "qualified_success",
                "liftoff22",
                "tall_eps",
                "tall_succ",
                "relW_eps",
                "relW_succ",
                "plat200_eps",
                "plat200_succ",
            ],
            counts=self.counts.tolist(),
            sample_min=self.range_low.tolist(),
            sample_max=self.range_high.tolist(),
            full_dr_envs=int(self.dr.sum()),
            key_hold_range=[int(self.key_hold.min()), int(self.key_hold.max())],
        )

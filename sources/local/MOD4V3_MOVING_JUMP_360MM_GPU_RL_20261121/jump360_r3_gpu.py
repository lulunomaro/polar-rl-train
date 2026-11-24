"""R3 rollout with operator hold variation and physically measured support."""
import math

import numpy as np
import torch
import warp as wp

from jump360_gpu import JumpGpu
from jump360_scene import CLOSURE_LIMIT, HURDLE_THICKNESS, WALL_HEIGHT

DR_LEVELS = (0., .5, 1.)
COUNTER_FIELDS = ("trials", "failures", "landed_running", "qualified", "clearance_385",
                  "forward", "whole_car_air_crossing", "held_50", "held_50_landed_running")


def training_timing(timing):
    """Place unproven cells around the observed rise boundary for active discovery."""
    tables = {kind: np.array(timing[kind]) for kind in ("platform", "hurdle")}
    for i, case in enumerate(timing["cases"]):
        row, col = divmod(i, len(timing["heights"]))
        window = case["geometry"]["whole_car_window_m"]
        if window is None:
            continue
        for kind, values in tables.items():
            measured = case[kind]
            successes = [trial for trial in measured["sweep"] if trial["obstacle_pass_physical"]]
            if successes:
                values[row, col] = max(successes, key=lambda trial: (
                    trial["wall_crossing_in_main_flight"],
                    trial["qualified"],
                    trial["wall_margin_m"] if trial["wall_margin_m"] is not None else -1.,
                ))["lead"]
            elif window[1] < window[0]:
                values[row, col] = max(values[row, col], window[0]+.04)
    return dict(timing, **{kind: matrix.tolist() for kind, matrix in tables.items()})


class Jump360R3Gpu(JumpGpu):
    def __init__(self, count, seed, timing):
        super().__init__(count, seed, timing)
        scalar = torch.zeros_like(self.cmd)
        self.stage = 0
        self.episode_stage = torch.zeros_like(self.tick)
        self.begin_tick = self.episode_stage.clone()
        self.press_speed = scalar.clone()
        self.air_progress = scalar.clone()
        self.overshoot = scalar.clone()
        self.support_history = torch.zeros((count, 15), device=self.device, dtype=torch.bool)
        self.crossed_airborne = torch.zeros(count, device=self.device, dtype=torch.bool)
        self.by_stage = torch.zeros((3, 2, 4, 8, len(COUNTER_FIELDS)), device=self.device)
        self.by_stage_speeds = torch.zeros((3, 2, 4, 8, 3), device=self.device)
        self.phase_counts = torch.zeros(6, device=self.device, dtype=torch.long)
        self.hold_samples = torch.zeros(51, device=self.device, dtype=torch.long)
        self.population_step_sum = torch.zeros((3, 2), device=self.device, dtype=torch.long)
        self.reset(torch.ones_like(self.dr))
        self.observe()
        self.hist[:] = self.obs[:, None, :]

    def set_stage(self, stage):
        self.stage = stage
        self.dr_probability = DR_LEVELS[stage]

    def reset(self, done):
        super().reset(done)
        if not hasattr(self, "by_stage"):
            return
        ids = self.index[done]
        count = len(ids)
        if not count:
            return
        self.episode_stage[ids] = self.stage
        # Balance the platform with flat jumps while retaining both solid hurdles.
        terrain = (self.rand(count)*20.).long()
        self.kind[ids] = torch.bucketize(terrain, terrain.new_tensor([7, 16, 18]), right=True)
        self.wall_height[ids] = torch.where(self.kind[ids] == 3, .340, self.kind[ids].ne(0).float()*WALL_HEIGHT)
        hold = torch.where(self.rand(count) < .5, 10+(11*self.rand(count)).long(), 30+(21*self.rand(count)).long())
        self.key_hold[ids] = hold
        self.hold_samples.scatter_add_(0, hold, torch.ones_like(hold))
        width = torch.where(self.rand(count) < .24, .25, .08)
        self.lead[ids] = (self.lead_opt(self.speed[ids], self.height[ids], self.kind[ids])
                          + width*(2.*self.rand(count)-1.)).clamp_min(.23)
        self.begin_tick[ids] = 108+(45*self.rand(count)).long()
        self.edge[ids] = (1.25+.55*self.rand(count))*self.speed[ids]+self.lead[ids]
        for j, gid in enumerate(self.cpu.hurdle_gids):
            active = self.kind[ids] == j+1
            half = self.cpu.m.geom_size[gid]
            self.mocap[ids, j, 0] = torch.where(active, self.edge[ids]+half[0], 4.)
            self.mocap[ids, j, 2] = torch.where(active, float(half[2]), -2.-j)
        self.support_history[ids] = False
        self.crossed_airborne[ids] = False
        self.press_speed[ids] = 0.
        self.air_progress[ids] = 0.
        self.overshoot[ids] = 0.

    def mode_target(self):
        # This supervisor is used only as a training target. The actor receives the raw key and history.
        return (self.press >= 0) & (self.arc[:, 1] < 2.) & ((self.tick-self.press) < 48)

    def annotate(self, done, failed, success, strict):
        speed_bin = ((self.speed-.50)*5).floor().long().clamp(0, 7)
        group = (((self.episode_stage*2+self.dr.long())*4+self.kind)*8+speed_bin)
        long = self.key_hold == 50
        values = torch.stack((done, done&failed, success, strict, done&(self.peak>=.385),
                             done&(self.worst_vx>0.)&(self.press>=0), done&self.crossed_airborne,
                             done&long, success&long), dim=1).float()
        self.by_stage.flatten(0, 3).index_add_(0, group, values)
        speed_values = torch.stack((done*self.press_speed, done*self.overshoot, success*self.press_speed), dim=1)
        self.by_stage_speeds.flatten(0, 3).index_add_(0, group, speed_values)
        self.population_step_sum.flatten().scatter_add_(0, self.episode_stage*2+self.dr.long(), torch.ones_like(group))

    def step(self, action):
        self.action.copy_(action.clamp(-6., 6.))
        self.stats.zero_()
        self.stats[:, 1] = 99.
        self.stats[:, 10] = 99.
        with wp.ScopedStream(self.warp_stream):
            wp.capture_launch(self.graph, self.warp_stream)
        self.slot.add_(8).remainder_(9)
        self.tick += 1
        broken = (~torch.isfinite(self.p).all(1) | ~torch.isfinite(self.v).all(1)
                  | ~torch.isfinite(self.rot).all(dim=(1, 2)) | ~torch.isfinite(self.stats).all(1)
                  | ~torch.isfinite(self.contacts).all(1) | (self.stats[:, 12] > 0))
        info = torch.where(broken[:, None], 0., self.stats)
        triggered = self.press >= 0
        bit = self.obs[:, 30] > .5
        age = self.tick-self.press
        platform = self.kind == 1
        obstacle = self.kind > 0
        air = self.arc[:, 1] == 1.
        landed = self.arc[:, 1] == 2.
        charge = triggered & ~broken & (info[:, 10] < 99.)
        vx = info[:, 11]
        upright = torch.where(broken, 0., self.rot[:, 2, 2])
        peak = torch.maximum(self.peak, info[:, 0])
        height_value = lambda value: 5.*(value/.385).clamp(0., 1.36).square() + 2.*((value-.385)/.11).clamp(0., 1.2)
        reward = height_value(peak)-height_value(self.peak)
        self.peak.copy_(peak)
        self.scrape = torch.maximum(self.scrape, info[:, 3]*charge)
        face = torch.where(self.kind >= 2, info[:, 9], info[:, 4])
        previous_hit = self.hits >= 1.
        self.hits = torch.maximum(self.hits, face)
        self.worst_vx = torch.minimum(self.worst_vx, torch.where(charge, info[:, 10], 99.))
        self.max_pitch = torch.maximum(self.max_pitch, info[:, 2])
        self.closure = torch.maximum(self.closure, info[:, 7])
        self.overshoot = torch.maximum(self.overshoot, (vx-self.speed).clamp_min(0.)*(self.tick>=65))

        both = self.contacts[:, 1:3].min(1).values > 1.
        on_top = self.contacts[:, 6:8].min(1).values > 1.
        beyond = info[:, 5] > self.edge + (self.kind >= 2).float()*HURDLE_THICKNESS
        self.crossed_airborne |= obstacle & beyond & air & (info[:, 6] > self.wall_height-.008)
        floor_support = both & (info[:, 6] < .020)
        proper_surface = torch.where(platform, on_top & beyond, floor_support & (~obstacle | beyond))
        landing = ~broken & landed & proper_surface & (vx>.35*self.speed) & (upright>.95)
        self.support_history[self.index, self.tick.remainder(self.support_history.shape[1])] = landing
        steady = self.support_history.sum(1) >= 9

        error = (vx-self.cmd).abs()
        cruise = ~triggered | landed
        overspeed = (vx-self.cmd-.18).clamp(0., 2.5)
        reward += .013 - (.016+.066*cruise)*error - (.036+.080*cruise)*overspeed.square()
        reward -= .09*air*((info[:, 2]-.175).clamp_min(0.)/.10).square()
        push_target = torch.where(obstacle, self.speed.clamp_min(1.55), .62*self.speed)
        reward -= charge*(.18*(push_target-info[:, 10]).clamp(0., 3.)+.40*(-info[:, 10]).clamp(0., 3.))
        reward -= charge*.23*(info[:, 3]>1.)
        reward -= obstacle*(.75*(face>=1.)+2.0*(~previous_hit&(face>=1.)))
        # Forward progress during the main flight and real support on the far side.
        progress = ((info[:, 5]-self.edge+.65)/.85).clamp(0., 1.)
        progress = torch.maximum(self.air_progress, progress*(obstacle & air & ~broken))
        reward += 3.2*(progress-self.air_progress) + landing*(.065+.15*obstacle)
        self.air_progress.copy_(progress)

        failure = broken | (upright<.5) | (self.p[:, 2]<.12) | (info[:, 7]>=CLOSURE_LIMIT)
        timeout = (triggered & (age>=115)) | (self.tick>=350)
        done = failure | timeout
        forward = (self.worst_vx>0.) & (self.press_speed>0.)
        success = done & ~failure & triggered & steady & forward & (self.scrape<1.) & (self.hits<1.)
        strict = success & (self.peak>=.385) & (self.max_pitch<=math.radians(12)) & (self.closure<CLOSURE_LIMIT)
        reward += success*(1.5+4.*obstacle) + strict*(1.+2.*obstacle) - 3.5*failure
        reward -= 1.2*(done & triggered & (self.peak<.22))
        reward = torch.where(broken, -4., reward)
        self.annotate(done, failure, success, strict)
        self.phase_counts += torch.stack((bit.sum(), (triggered & ~bit & ~landed).sum(), (bit & landed).sum(),
                                          (platform & landing).sum(), (obstacle & air).sum(), broken.sum()))
        self.immediate[0] = torch.maximum(self.immediate[0], info[:, 7].max())
        self.immediate[1] = torch.maximum(self.immediate[1], wp.to_torch(self.d.nacon)[0].float())
        self.immediate[2] = torch.maximum(self.immediate[2], wp.to_torch(self.d.nefc).max().float())
        self.immediate[5] = torch.maximum(self.immediate[5], self.peak.max())
        self.previous.copy_(self.action)
        self.reset(done)

        nominated = torch.where(self.kind==0, self.tick>=self.begin_tick, self.p[:, 0]>=self.edge-self.lead)
        press_now = (self.press<0) & (self.tick>=59) & nominated
        self.press_speed.copy_(torch.where(press_now, vx, self.press_speed))
        self.press.copy_(torch.where(press_now, self.tick, self.press))
        self.cmd += (torch.where(self.tick>=30, self.speed, 0.)-self.cmd)/12.
        self.observe()
        self.hist = torch.cat((self.hist[:, 1:], self.obs[:, None, :]), dim=1)
        self.hist[done] = self.obs[done, None, :]
        return self.obs, self.hist.flatten(1), reward, done

    def audit(self):
        return dict(
            fields=COUNTER_FIELDS, categories=["flat", "platform_360", "hurdle_360", "hurdle_340"],
            stages=DR_LEVELS, speed_centers_m_s=[round(.6+.2*i, 2) for i in range(8)],
            by_stage_dr_terrain_speed=self.by_stage.long().tolist(),
            speed_sums_fields=["press_vx_all", "overshoot_all", "press_vx_landed"],
            speed_sums=self.by_stage_speeds.tolist(),
            full_dr_envs=int(self.dr.sum()), population_env_steps_by_stage_and_dr=self.population_step_sum.tolist(),
            holds_by_ticks=self.hold_samples.tolist(),
            phase_columns=["key_down", "released_before_first_support", "held_after_first_support",
                           "platform_support", "obstacle_air", "nonfinite_world_resets"],
            phase_samples=self.phase_counts.tolist(), max_closure_m=float(self.immediate[0]),
            max_contacts_global=int(self.immediate[1]), contact_capacity=self.d.naconmax,
            max_constraints_per_world=int(self.immediate[2]), constraint_capacity=self.d.njmax,
            measured_all_car_peak_m=float(self.immediate[5]),
        )


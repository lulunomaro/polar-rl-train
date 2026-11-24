"""R9 forward-coupled height shaping and speed sampling."""

import math

import torch
import warp as wp

from jump360_scene import CLOSURE_LIMIT, HURDLE_THICKNESS
from jump380_r5_support import MIN_SUPPORT_TICKS, SUPPORT_FORCE_N, SUPPORT_WINDOW_TICKS
from jump380_r6_scene import YAW_LIMIT_DEG, Y_LIMIT
from jump380_r7_gpu import SPEED_CENTERS, measured_nose
from jump380_r8_gpu import TAKEOFF_SPEED, Jump380Gpu as R8Gpu

HEIGHT_CAP = 1.06
HEIGHT_FORWARD_SPEED = 1.75
HEIGHT_FORWARD_CAP = 1.15
CHARGE_SPEED_FRACTION = .55
CHARGE_BRAKE_WEIGHT = .65
LOW_SPEED_PROBABILITY = .70
SPEED_SPLIT = 1.80


class Jump380Gpu(R8Gpu):
    def reset(self, done):
        super().reset(done)
        ids = self.index[done]
        if ids.numel() == 0:
            return

        # Keep the parent's sampled run-up duration and press jitter when moving the wall.
        runup = (self.edge[ids] - self.lead[ids]) / self.speed[ids]
        jitter = self.lead[ids] - self.lead_center[ids]
        draw = self.rand(ids.numel())
        low_band = draw < LOW_SPEED_PROBABILITY
        slow = .80 + (SPEED_SPLIT - .80) * draw / LOW_SPEED_PROBABILITY
        fast = SPEED_SPLIT + (2. - SPEED_SPLIT) * (draw - LOW_SPEED_PROBABILITY) / (1. - LOW_SPEED_PROBABILITY)
        speed = torch.where(low_band, slow, fast)
        kind = self.kind[ids]
        center = self.lead_opt(speed, self.height[ids], kind)
        lead = center + jitter
        edge = runup * speed + lead
        shift = edge - self.edge[ids]
        self.speed[ids] = speed
        self.lead_center[ids] = center
        self.lead[ids] = lead
        self.edge[ids] = edge
        obstacles = torch.arange(1, 4, device=self.device)
        self.mocap[ids, :, 0] += (kind[:, None] == obstacles) * shift[:, None]

        if not hasattr(self, "speed_band_resets"):
            self.speed_band_resets = torch.zeros((4, 2), dtype=torch.long, device=self.device)
            self.speed_min = speed.min()
            self.speed_max = speed.max()
        self.speed_min = torch.minimum(self.speed_min, speed.min())
        self.speed_max = torch.maximum(self.speed_max, speed.max())
        band = kind * 2 + (~low_band).long()
        self.speed_band_resets.flatten().scatter_add_(0, band, torch.ones_like(band))

    def step(self, action):
        self.action.copy_(action.clamp(-6., 6.))
        had_main_flight = self.arc[:, 1] > 0.
        self.stats.zero_()
        self.stats[:, 1] = 99.
        self.stats[:, 10] = 99.
        with wp.ScopedStream(self.warp_stream):
            wp.capture_launch(self.graph, self.warp_stream)
            wp.launch(measured_nose, self.n, self.nose_args)
        self.slot.add_(8).remainder_(9)
        self.tick += 1

        broken = (~torch.isfinite(self.p).all(1) | ~torch.isfinite(self.v).all(1)
                  | ~torch.isfinite(self.rot).all(dim=(1, 2)) | ~torch.isfinite(self.stats).all(1)
                  | ~torch.isfinite(self.contacts).all(1) | (self.stats[:, 12] > 0.))
        info = torch.where(broken[:, None], 0., self.stats)
        obstacle = self.kind != 0
        platform = (self.kind == 1) | (self.kind == 2)
        hurdle = self.kind == 3
        triggered = self.press >= 0
        bit = self.obs[:, 30] > .5
        air = self.arc[:, 1] == 1.
        first_flight_ended = self.arc[:, 1] == 2.
        charge = triggered & ~broken & (info[:, 10] < 99.)
        upright = torch.where(broken, 0., self.rot[:, 2, 2])
        vx = info[:, 11]
        lateral_limit = info[:, 19] > Y_LIMIT
        yaw_limit = info[:, 20] > math.radians(YAW_LIMIT_DEG)
        course_violation = lateral_limit | yaw_limit
        approaches = torch.stack((~triggered & ~self.dr, ~triggered & self.dr))
        self.approach_max_by_dr.copy_(torch.maximum(
            self.approach_max_by_dr, (approaches[..., None] * info[None, :, 19:21]).amax(dim=1)))

        # Shaping only rewards new height on the main flight, relative to its floor.
        peak = torch.maximum(self.peak, info[:, 0])
        height_gain = (peak / .385).clamp(0., HEIGHT_CAP).square()
        height_gain -= (self.peak / .385).clamp(0., HEIGHT_CAP).square()
        forward_factor = (vx / HEIGHT_FORWARD_SPEED).clamp(0., HEIGHT_FORWARD_CAP)
        reward = ~course_violation * torch.where(obstacle, 3.2 * forward_factor, 6.) * height_gain
        self.peak.copy_(peak)
        self.scrape = torch.maximum(self.scrape, info[:, 3]*charge)
        self.worst_vx = torch.minimum(self.worst_vx, torch.where(charge, info[:, 10], 99.))
        self.max_pitch = torch.maximum(self.max_pitch, info[:, 2])
        self.closure = torch.maximum(self.closure, info[:, 7])

        face = torch.where(hurdle, info[:, 9], info[:, 4])
        first_hit = (self.hits < 1.) & (face >= 1.)
        self.face_events.scatter_add_(0, self.kind, first_hit.long())
        self.collision_counts.index_add_(0, self.kind,
            torch.stack((first_hit & ~triggered, yaw_limit, lateral_limit), dim=1).float())
        self.hits = torch.maximum(self.hits, face)
        reward -= .52*(face >= 1.) + 2.4*first_hit

        top_force = info[:, 17:19]
        on_top = top_force.min(1).values > SUPPORT_FORCE_N
        one_on_top = top_force.max(1).values > SUPPORT_FORCE_N
        wheel_beyond = info[:, 13] > self.edge + .02
        whole_car_beyond = info[:, 5] > self.edge + hurdle.float()*HURDLE_THICKNESS
        valid_platform_support = platform & on_top & wheel_beyond
        both = info[:, 15:17].min(1).values > SUPPORT_FORCE_N
        floor_support = both & (info[:, 6] < .020)
        correct_surface = torch.where(platform, valid_platform_support, floor_support & (~obstacle | whole_car_beyond))
        recovery = first_flight_ended & ~broken & ~course_violation
        forward_running = (vx > .35*self.speed) & (upright > .95)
        landing = recovery & correct_surface & forward_running
        clean = (self.hits < 1.) & (self.scrape < 1.)
        acquired = recovery & valid_platform_support & forward_running & clean
        reward += 1.8*(acquired & ~self.platform_acquired)
        self.platform_acquired |= acquired
        self.support_history[:, self.support_slot] = landing
        self.support_slot = (self.support_slot + 1) % SUPPORT_WINDOW_TICKS
        stable_now = self.support_history.sum(1) >= MIN_SUPPORT_TICKS
        first_clean_stable = stable_now & ~self.stable & clean
        reward += first_clean_stable*torch.where(platform, 3., 1.)
        self.stable |= stable_now

        # Limit speed while approaching and after the rolling landing criterion is met.
        cruise = ~triggered | self.stable
        overspeed = (vx - self.cmd - .18).clamp(0., 2.5)
        tracking_error = (vx - self.cmd).abs().clamp_max(3.)
        reward += .012 - cruise*(.079*tracking_error + .115*overspeed.square())
        push_target = torch.where(obstacle, self.speed.clamp_min(TAKEOFF_SPEED), .60*self.speed)
        reward -= charge*(.23*(push_target - info[:, 10]).clamp(0., 3.) +
                          .42*(-info[:, 10]).clamp(0., 3.) + .24*(info[:, 3] > 1.))
        braking = (CHARGE_SPEED_FRACTION * self.press_speed - vx).clamp_min(0.)
        reward -= charge * CHARGE_BRAKE_WEIGHT * braking
        launch_ramp = ((self.tick - self.press).float()/15.).clamp(0., 1.)
        impulse = (vx - self.press_speed).clamp(0., 2.2)
        reward += .38*launch_ramp*impulse*(obstacle & charge & clean & ~course_violation)
        new_takeoff = air & ~had_main_flight & ~broken & ~course_violation
        speed_fraction = (vx/push_target).clamp(0., 1.)
        reward += (obstacle & new_takeoff & clean)*(.75*speed_fraction + .55*(vx >= TAKEOFF_SPEED))
        group = self.kind*len(SPEED_CENTERS) + self.speed_bin()
        self.takeoff_sum.flatten(0, 1).index_add_(0, group, torch.stack((
            new_takeoff, torch.where(new_takeoff, vx, 0.), new_takeoff & (vx >= TAKEOFF_SPEED)), dim=1))
        reward -= .10*air*((info[:, 2] - .175).clamp_min(0.)/.10).square()

        # The wheel-centre distance gives approach credit only while clearing the wall in flight.
        advance = ((info[:, 13] - self.edge + .35)/.45).clamp(0., 1.)
        high_enough = info[:, 6] > self.wall_height - .015
        progress = torch.maximum(self.air_progress,
                                 advance*(obstacle & air & high_enough & ~broken & ~course_violation))
        reward += 5.*(progress - self.air_progress)
        self.air_progress.copy_(progress)
        reward += .08*(recovery & platform & one_on_top & clean & (vx > 0.))
        reward += landing*torch.where(platform, .24, .055)

        # Touchdown labels consume upward loads. The training objective damps rebound and pitch.
        loaded = recovery & (one_on_top | floor_support)
        first_support = loaded & (self.first_touch_tick < 0)
        self.first_touch_tick.copy_(torch.where(first_support, self.tick, self.first_touch_tick))
        absorbing = recovery & (self.first_touch_tick >= 0) & ((self.tick - self.first_touch_tick) < 18)
        pitch_rate = torch.where(broken, 0., self.v[:, 4]).abs().clamp_max(8.)
        rebound = info[:, 8].clamp(0., 4.)
        reward -= absorbing*(.057*info[:, 14].clamp_max(4.) + .10*rebound + .020*pitch_rate
                             + .10*(1. - upright).clamp(0., 1.))

        reward -= (.08*info[:, 21].abs() + .10*torch.where(broken, 0., self.p[:, 1].abs())
                   + .03*torch.where(broken, 0., self.v[:, 5].abs()))
        failed = broken | course_violation | (upright < .5) | (self.p[:, 2] < .12) | (info[:, 7] >= CLOSURE_LIMIT)
        age = self.tick - self.press
        timeout = (triggered & (age >= 115)) | (self.tick >= 345)
        done = failed | timeout
        forward = (self.worst_vx > 0.) & (self.press_speed > 0.)
        success = (done & ~failed & triggered & stable_now & forward & clean
                   & (~obstacle | whole_car_beyond))
        strict = (success & (self.peak >= .385) & (self.max_pitch <= math.radians(12.))
                  & (~platform | (self.arc[:, 6] >= 0.)))
        reward += success*torch.where(platform, 7., 2.) + strict*torch.where(platform, 2., 1.5)
        reward -= 4.*failed + 1.2*(done & triggered & (self.peak < .22))
        reward = torch.where(broken, -4., reward)
        self.annotate(done, failed, success, strict, course_violation)
        last_substep_missed = on_top & (self.contacts[:, 6:8].min(1).values <= SUPPORT_FORCE_N)
        self.phase_samples += torch.stack((
            bit.sum(), (triggered & ~bit & ~first_flight_ended).sum(), (bit & loaded).sum(),
            ((self.kind == 1) & on_top).sum(), ((self.kind == 2) & on_top).sum(),
            (acquired & ~whole_car_beyond).sum(), broken.sum(), (platform & ~triggered).sum(),
            (platform & charge).sum(), (stable_now & triggered).sum(),
            ((self.kind == 1) & last_substep_missed).sum(), ((self.kind == 2) & last_substep_missed).sum(),
            ((self.kind == 1) & first_clean_stable).sum(), ((self.kind == 2) & first_clean_stable).sum(),
        ))
        self.immediate[0] = torch.maximum(self.immediate[0], info[:, 7].max())
        self.immediate[1] = torch.maximum(self.immediate[1], wp.to_torch(self.d.nacon)[0].float())
        self.immediate[2] = torch.maximum(self.immediate[2], wp.to_torch(self.d.nefc).max().float())
        self.immediate[5] = torch.maximum(self.immediate[5], self.peak.max())
        self.previous.copy_(self.action)
        self.reset(done)

        self.press_after_runup(vx, done)
        self.cmd += (torch.where(self.tick >= 30, self.speed, 0.) - self.cmd)/12.
        self.observe()
        self.hist = torch.cat((self.hist[:, 1:], self.obs[:, None, :]), dim=1)
        self.hist[done] = self.obs[done, None, :]
        return self.obs, self.hist.flatten(1), reward, done

    def audit(self):
        stats = super().audit()
        stats["sampled_reset_min"][0] = float(self.speed_min)
        stats["sampled_reset_max"][0] = float(self.speed_max)
        stats["speed_band_bounds_m_s"] = ((.8, SPEED_SPLIT), (SPEED_SPLIT, 2.))
        stats["speed_band_target"] = (LOW_SPEED_PROBABILITY, 1. - LOW_SPEED_PROBABILITY)
        stats["speed_band_resets_by_terrain"] = self.speed_band_resets.tolist()
        band_total = self.speed_band_resets.sum(0)
        stats["speed_band_fractions"] = (band_total / band_total.sum()).tolist()
        return stats

"""Command-range curriculum for 小陀螺 (the sustained high-rate gyro spin).

WHY THIS IS NEEDED, with the numbers that prove it
The yaw-tracking reward is a Gaussian, exp(-err^2/std^2).  v12 could hold ~5.7 rad/s of yaw.
The v13 config opened the command range straight to +-14 rad/s, so most of the new command
space sat in the tail of that Gaussian: a 14 rad/s command tracked at 6 rad/s scores
exp(-64/2) ~ 1e-14 -- *no gradient at all*, only the cost of trying and falling over.  The
v13 log shows exactly that failure mode: Metrics/twist/error_vel_yaw climbed monotonically
from 0.15 to 7.0 over its first 40 iterations instead of falling.

So the window is widened only while the robot already *holds* the hardest rate it is being
asked for, and narrowed when it stops holding it -- the same idea as the terrain curriculum,
applied to the yaw axis, which is the axis the 360-degree hip exists for.

The criterion is a ratio (achieved / commanded) rather than an error, because it has to work
equally well at +-4 rad/s and at +-14 rad/s without re-tuned thresholds, and because it only
looks at the envs whose current command is near the top of the window -- which is exactly the
population that decides whether the window may grow.
"""
from __future__ import annotations

import torch

from .terrain_utils import terrain_mask


class gyro_command_range:
    """Adaptive +-ang_vel_z command window.

    Params
        command_name : twist
        target       : the window we want to end at, e.g. 14 rad/s
        start        : the window we begin at (the robot's proven capability, e.g. 4)
        floor        : never ask for less than this
        step         : rad/s added/removed per decision
        every        : policy steps between decisions
        hard_frac    : an env counts as "hard" when |cmd| >= hard_frac * window
        hi / lo      : fraction-of-hard-envs-holding-the-rate thresholds for expand / shrink
        tol          : how close to the commanded rate counts as holding it (+-25% default)
        ema          : smoothing factor of the ratio (per decision)
    """

    def __init__(self, cfg, env):
        p = cfg.params
        self.term = env.command_manager.get_term(p.get("command_name", "twist"))
        self.target = float(p["target"])
        self.floor = float(p.get("floor", 2.0))
        self.step_size = float(p.get("step", 0.4))
        self.every = int(p.get("every", 60))
        self.hard_frac = float(p.get("hard_frac", 0.75))
        self.min_envs = int(p.get("min_envs", 32))
        self.hi = float(p.get("hi", 0.55))       # >55% of the hard envs hold the rate
        self.lo = float(p.get("lo", 0.18))       # <18% do -> the window is too wide
        self.tol = float(p.get("tol", 0.25))     # +/-25% of the commanded rate
        self.ema_a = float(p.get("ema", 0.8))
        import math
        # an env is "upright" while its chassis is within `upright_deg` of vertical
        # GATES, AND WHY THEY CANNOT BE TOO STRICT.  v15's first launch used tilt<12 deg,
        # |rate|<0.6 and 3 consecutive decisions - and it collapsed the window from 13.2 down to
        # the 2.0 floor within 76 iterations, because a balancing robot is almost never that
        # quiet while it is also spinning hard.  A window that has collapsed can never re-open
        # (nothing above 6 rad/s is ever commanded, so every high-rate reward is identically
        # zero), which is a worse failure than the crash-transients the gate was meant to
        # filter.  So: a looser attitude gate, and a RATCHET below (see _set).
        self.upright_cos = math.cos(math.radians(float(p.get("upright_deg", 20.0))))
        self.max_rate = float(p.get("max_rate", 1.5))     # rad/s of roll/pitch rate
        self.streak_need = int(p.get("streak", 2))        # consecutive good decisions
        self.ratchet = float(p.get("ratchet", 0.65))      # never drop below 65% of the best
        self.streak = 0
        self.best = 0.0
        self.quantile = float(p.get("quantile", 0.75))
        self.n_up = 0
        self.robot = env.scene[p.get("entity_name", "robot")]
        self.n = 0
        self.ratio = float("nan")
        self.top = 0.0
        self._set(float(p.get("start", 4.0)))

    def _set(self, w: float) -> None:
        self.w = max(self.floor, min(self.target, w))
        self.best = max(self.best, self.w)
        # The ratchet is what makes the curriculum monotone-ish: shrinking is allowed to
        # stabilise training, but never to lock itself out of the skill it is training.
        self.w = max(self.w, self.ratchet * self.best)
        # The command term reads cfg.ranges.ang_vel_z on every resample, so mutating it is
        # the whole implementation: no sampler patching, and mjlab's own code path is used.
        self.term.cfg.ranges.ang_vel_z = (-self.w, self.w)

    def __call__(self, env, env_ids, **_ignored):
        # The manager replays cfg.params as keyword arguments on every call, so the
        # signature has to swallow them: the state lives on self, not in the arguments.
        self.n += 1
        cmd = self.term.command[:, 2]
        act = self.robot.data.root_link_ang_vel_b[:, 2]
        hard = cmd.abs() >= self.hard_frac * self.w
        # Only envs that are still UPRIGHT count.  Without this gate the statistic is
        # dominated by crashes, and in the first iterations on a new plant the ratio is ~0.2
        # everywhere -- the window collapses to its floor and the 小陀螺 never gets asked for
        # again, which is the opposite of what a curriculum is for.
        # A CRASH LOOKS LIKE SUCCESS to a naive statistic.  v14's window walked up to 13.2
        # rad/s while the policy could actually only hold 5.5, because an env that is on its
        # way down passes through a small tilt while its yaw rate spikes.  So "holding" means
        # upright AND settled: small tilt AND small pitch rate.
        g = self.robot.data.projected_gravity_b
        w = self.robot.data.root_link_ang_vel_b
        steady = (w[:, 1].abs() < self.max_rate) & (w[:, 0].abs() < self.max_rate)
        hard = hard & ((-g[:, 2]) > self.upright_cos) & steady
        held = float("nan")            # a missing measurement must never move the window
        if int(hard.sum()) >= self.min_envs:
            # What fraction of the upright, near-max-command envs actually HOLD the rate they
            # were asked for (same direction, within +-tol)?  A plain achieved/commanded
            # ratio is not good enough: right after seeding, the v12 policy + the new 55 rad/s
            # wheel unit flings the chassis to 13 rad/s while falling over, ratio 1.55, and a
            # ratio rule would call that a success and snap the window open to +-14 in ~20
            # iterations -- the exact v13 failure.  Overshoot is not tracking.
            c_abs = cmd[hard].abs()
            same_dir = torch.sign(cmd[hard]) == torch.sign(act[hard])
            a_abs = act[hard].abs()
            ok = same_dir & (a_abs > (1.0 - self.tol) * c_abs) & \
                 (a_abs < (1.0 + self.tol) * c_abs)
            # A solver blow-up in ONE env used to poison the whole log line (top_abs: nan at
            # iteration 8820 of v14, which looks like a broken curriculum and is really four
            # envs out of 10240 being reset by nan_detection).  Ignore non-finite rates.
            good = torch.isfinite(a_abs)
            if int(good.sum()) < self.min_envs:
                held = float("nan")
            else:
                ok_g = ok[good]
                c_g = cmd[hard][good]
                # BOTH SIGNs have to hold before the window widens.  Taking the plain
                # mean let v14 open the window on the strength of the clockwise direction
                # alone - and the final policy then answered a -14 rad/s command with
                # +2.27 rad/s (docs/HOWTO.md 29.2).  scripts/spin_symmetry.py proves the
                # mechanism itself is symmetric to 0.1%, so this is purely a training
                # signal problem: min() makes one-sided competence worth nothing.
                pos_h = ok_g[c_g > 0]
                neg_h = ok_g[c_g < 0]
                need = int(self.min_envs // 2)
                if pos_h.numel() < need or neg_h.numel() < need:
                    held = float("nan")        # not enough of both signs yet: no decision
                else:
                    held = min(float(pos_h.float().mean()), float(neg_h.float().mean()))
                self.top = float(a_abs[good].max())
                self.n_up = int(good.sum())
        if self.n % self.every == 0 and held == held:      # held is not NaN
            self.ratio = held if self.ratio != self.ratio else \
                self.ema_a * self.ratio + (1.0 - self.ema_a) * held
            if self.ratio > self.hi:
                self.streak += 1
                if self.streak >= self.streak_need:      # only a SUSTAINED hold widens it
                    self._set(self.w + self.step_size)
                    self.streak = 0
            elif self.ratio < self.lo:
                self.streak = 0
                self._set(self.w - 0.5 * self.step_size)   # shrink at half the expand rate
        return {"window": torch.tensor(self.w),
                "hold_ratio": torch.tensor(0.0 if self.ratio != self.ratio else self.ratio),
                "top_abs": torch.tensor(self.top),
                "n_upright_hard": torch.tensor(float(self.n_up))}

class skill_command_split:
    """Give each env ONE skill per command window instead of asking for all of them at once.

    WHY.  v15 exposed the interaction: the yaw window reached its full +-14 rad/s with
    hold_ratio 0.80 and every skill reward improved (track_ang_vel 1.42, track_lin_vel 0.87,
    jump_progress 0.91) - while `terrain_levels/mean` FELL from 0.275 back to 0.055.  The two
    curricula are fighting: the command sampler draws vx in (-1.5, 2.8) and wz in (+-14)
    independently, so most envs are asked to sprint at 2.8 m/s while spinning at 14 rad/s,
    which nobody can do.  An env that cannot do it does not traverse its terrain patch, so the
    terrain curriculum demotes it - the map skill is being starved by the gyro skill.

    WHAT.  A fixed fraction of the batch is tagged "gyro" (vx forced to ~0, wz up to +-wz_max)
    and the rest are "locomotion" (wz capped to +-wz_loco, vx full range).  The tags come from
    the env index, so they are stable across resets and need no state.  It rewrites the command
    buffer in place every step, which means both the OBSERVATION (twist_commands reads the same
    buffer) and the rewards see exactly what was actually asked - no contract change, the 35-D
    layout is untouched, and the deployment keeps sending whatever the operator commands.
    """

    def __init__(self, cfg, env):
        p = cfg.params
        self.term = env.command_manager.get_term(p.get("command_name", "twist"))
        self.fraction = float(p.get("fraction", 0.25))
        self.wz_loco = float(p.get("wz_loco", 2.0))
        self.wz_max = float(p.get("wz_max", 14.0))
        self.vx_loco = tuple(p.get("vx_loco", (-1.5, 2.8)))
        n = env.num_envs
        idx = torch.arange(n, device=env.device)
        # deterministic, reset-proof tagging: every 1/fraction-th env is a gyro env
        self.gyro = (idx % max(2, int(round(1.0 / max(1e-3, self.fraction))))) == 0
        self.n_gyro = int(self.gyro.sum())

    def __call__(self, env, env_ids, **_ignored):
        c = self.term.command
        g = self.gyro
        ng = int(g.sum())
        if ng and ng < c.shape[0]:
            # gyro envs: stand still and spin at the CURRENT curriculum window, not the
            # final target.  The 2026-09-10 run showed the bug: this term used the fixed
            # wz_max, so the gyro envs were commanded 7-13 rad/s from iteration 0 while the
            # gyro curriculum window sat at its 3.9 floor, and the skill never learned.
            w_now = min(self.wz_max, float(self.term.cfg.ranges.ang_vel_z[1]))
            c[g, 0] = 0.0
            c[g, 2] = torch.sign(c[g, 2]) * torch.empty(ng, device=c.device).uniform_(
                0.55 * w_now, w_now)
            # locomotion envs: drive at full speed, only steer gently
            cl = c[~g]
            cl[:, 2] = torch.clamp(cl[:, 2], -self.wz_loco, self.wz_loco)
            c[~g, 0] = cl[:, 0]
        return {"gyro_fraction": torch.tensor(float(ng) / float(c.shape[0]))}


class tunnel_height_command:
    """Hold a low height command on the tunnel terrain.

    The user measured the real robot at ~0.20 m in its lowest state, so the tunnel envs
    are commanded to 0.20 m every step (the reset event's random height is overridden).
    This gives the policy the observation-side signal; ``tunnel_traversal`` provides the
    reward-side signal.
    """

    def __init__(self, cfg, env):
        p = cfg.params
        self.height = float(p.get("height", 0.20))
        self.key = p.get("terrain_key", "tunnel")
        self.mask = terrain_mask(env, self.key)

    def __call__(self, env, env_ids, **_ignored):
        h = getattr(env, "_rm_height_cmd", None)
        if h is not None and bool(self.mask.any()):
            h[self.mask] = self.height
        return {"tunnel_envs": torch.tensor(float(self.mask.sum()))}

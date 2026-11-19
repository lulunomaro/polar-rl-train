# SPDX-License-Identifier: MIT
"""Training fixtures and metrics for the MOD4v3 autonomous MoE repair."""
from __future__ import annotations

import math
import os
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[2]
STAIR_DIR = LOCAL / 'MOD4V3_AUTONOMOUS_ALLSPEED_STAIR_MOE_20261118'
JUMP_DIR = LOCAL / 'MOD4V3_INSTANT_LQR_STYLE_RL_JUMP_20261118'
PLAYER_DIR = LOCAL / 'MOD4V3_AUTONOMOUS_MOE_ALL_MAPS_20261120'
PARENT_WEIGHTS = HERE / 'parents' if (HERE / 'parents').exists() else PLAYER_DIR / 'weights'
JUMP_ANCHOR = LOCAL / 'MOD4V3_RL_HIGH_MOVING_JUMP_20261118/trajectories/clean_jump_anchor.pt'
LEAP_DIR = LOCAL / 'MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118'
LEAP_PARENT = LEAP_DIR / 'weights/model_rl_forward_leap_best.pt'
for module_dir in (STAIR_DIR, JUMP_DIR, LEAP_DIR):
    sys.path.insert(0, str(module_dir))

# Keep generated arena files in the experiment. All robot parameters come from the pinned plants.
os.environ.setdefault('MUJOCO_GL', 'disable')
import autonomous_stair_env as stair_arena  # noqa: E402
from autonomous_stair_env import Mod4v3AutonomousStairEnv  # noqa: E402
from instant_jump_env import Mod4v3InstantJumpEnv, ensure_instant_jump_scene_xml  # noqa: E402
import mujoco as mj  # noqa: E402
from forward_leap_env import Mod4v3ForwardLeapEnv, ensure_forward_leap_scene_xml  # noqa: E402

DT = 0.02
RADIUS = 0.0625
RESTART_PROFILES = ('restart', 'restart_reverse', 'restart_wall')
CLIMB_PROFILES = ('climb', 'restart', 'restart_reverse')
_original_stair_scene = stair_arena.ensure_autonomous_stair_arena_xml


def _local_stair_scene(cache_dir=None):
    return _original_stair_scene(cache_dir or HERE / 'runtime_cache/stairs')


stair_arena.ensure_autonomous_stair_arena_xml = _local_stair_scene


def pitch_deg(data, body_id):
    return math.degrees(math.asin(float(np.clip(-data.xmat[body_id, 6], -1.0, 1.0))))


def forward_intent(vx, wz):
    return bool(vx > 0.10 and abs(wz) < 0.8)


class StairFixture(Mod4v3AutonomousStairEnv):
    """Same plant. Commands and target labels are prepared before computing the observation."""

    low_stance_focus = False
    high_slow_focus = False
    mid_stance_focus = False
    restart_focus = False

    def start(self, profile='climb', height=0.28, speed=0.9, offset=0.0, yaw=0.0,
              dr=0.0, rise=False, distance=1.35, wall_height=.50):
        self.profile = profile
        self.measure_substeps = getattr(self, "measure_substeps", False)
        self.request_height = float(height)
        self.rise = rise
        self.intent = speed
        self.steering = 0.0
        self.cancel_after_ticks = 0
        self.restart_after_ticks = 0
        if profile in RESTART_PROFILES:
            self.cancel_after_ticks = int(self.rng.integers(3, 11))
            self.restart_after_ticks = self.cancel_after_ticks + int(self.rng.integers(31, 64))
        self.restart_contact_tick = None
        self.restart_x = None
        self.restart_max_x = None
        self.restart_backtrack = 0.0
        self.command_vx = 0.0
        self.command_tick = -1
        self.hit_tick = None
        self.last_hit = -1000
        self.first_hit_x = None
        self.max_x_after_hit = None
        self.backtrack = 0.0
        self.contact_stall_ticks = 0
        self.support_ticks = 0
        self.ever_supported = False
        self.held_top = False
        self.recovered = False
        self.cleared_at = None
        self.p_peak = 0.0
        self.acmd = None
        self.prev_exec = np.zeros(6, np.float32)
        self.near_gate_max = 0.0
        self.invalid_gate_max = 0.0
        self.prewall_gate_max = 0.0
        self.min_reverse_vx = 0.0
        self.end_delta_after_switch = None
        self.switch_x = None
        self.support_force = np.zeros(2, np.float32)
        self.first_tire_hit = None
        self.intent_ok = False
        self.turned_start = 0.0
        self.prev_x = float(offset)
        self.next_height = float(height)
        self.last_pitch = 0.0
        self.wall_backup_m = 0.0
        self.max_hit_force = 0.0
        self.peak_forward_speed = 0.0
        step = () if profile == 'flat' else ((wall_height,) if profile in ('wall', 'restart_wall') else (0.20,))
        st = self.reset_scenario(
            kind='flat' if profile == 'flat' else 'stair_1step', dr_scale=dr,
            step_heights=step, step_x1=distance, height_cmd=0.28 if rise else height,
            cmd_vx=speed, start_x=offset, start_yaw=yaw, max_steps=410,
        )
        return st

    def sample(self, dr, role):
        r = self.rng
        p = r.random()
        if role == 'router':
            profile = 'climb' if p < 0.40 else (str(r.choice(['reverse', 'stop', 'turn', 'wall'])) if p < .80 else 'flat')
        else:
            profile = 'climb' if p < .82 else str(r.choice(['reverse', 'stop', 'wall', 'flat']))
        if self.mid_stance_focus:
            height = float(r.choice([.345, .35, .355, .36, .36, .365, .37, .375]))
            speed = float(r.choice([.81, .86, .90, .90, .90, .94, .98]))
            yaw_limit = .075
            if role == 'stair':
                profile = 'climb' if p < .94 else 'flat'
        elif self.high_slow_focus and role == 'stair':
            profile = 'climb' if p < .94 else 'flat'
            height = float(r.choice([.37, .40, .42, .42, .42]))
            speed = float(r.choice([.42, .47, .47, .47, .52, .58]))
            yaw_limit = .07
        elif self.low_stance_focus and role == 'stair':
            height = float(r.choice([.28, .28, .30, .30, .32, .34, .37, .42]))
            speed = float(r.choice([.47, .60, .78, .90, .90, 1.02]))
            yaw_limit = .35 if r.random() < .55 else .07
        else:
            height = float(r.choice([.28, .32, .36, .38, .40, .42]))
            speed = float(r.uniform(.50, 1.28))
            yaw_limit = .12
        if self.restart_focus:
            profile = ('restart' if p < .40 else 'restart_reverse' if p < .64 else
                       'restart_wall' if p < .78 else 'climb' if p < .92 else 'flat')
            if not self.mid_stance_focus:
                height = float(r.choice([.28, .29, .31, .33, .34, .36, .40, .41, .42, .42]))
            speed = float(r.choice([.77, .83, .88, .90, .90, .93, .98]))
            yaw_limit = .085
            return self.start(profile, height, speed, float(r.uniform(-.074, .074)),
                              float(r.uniform(-yaw_limit, yaw_limit)), dr, rise=False,
                              distance=float(r.uniform(1.16, 1.26)), wall_height=float(r.choice([.45, .50])))
        if self.mid_stance_focus:
            return self.start(profile, height, speed, float(r.uniform(-.075, .075)),
                              float(r.uniform(-yaw_limit, yaw_limit)), dr, rise=p > .71,
                              distance=float(r.uniform(1.16, 1.40)), wall_height=float(r.choice([.45, .50])))
        return self.start(profile, height, speed, float(r.uniform(-.08, .08)),
                          float(r.uniform(-yaw_limit, yaw_limit)), dr,
                          rise=p > (.78 if self.high_slow_focus else .27), distance=float(r.uniform(1.16, 1.40)))

    def _current_commands(self):
        # This fixture applies the same 140 ms stick slew as the WASD player.
        now = self.k * DT
        cab_h = self.request_height
        if self.rise:
            cab_h = min(self.request_height, .28 + max(now - .26, 0) * .12)
        drive_at = .40 if (self.mid_stance_focus or self.restart_focus) else (.50 if self.rise else .32)
        vx_target = self.cmd_vx_base if now >= drive_at else 0.0
        wz = 0.0
        if self.profile in ('reverse', 'stop', 'turn') and self.hit_tick is not None and self.k - self.hit_tick >= 3:
            vx_target = -.55 if self.profile == 'reverse' else 0.0
            wz = .95 if self.profile == 'turn' else 0.0
        neutral_at_riser = False
        if self.profile in RESTART_PROFILES and self.hit_tick is not None:
            since_contact = self.k - self.hit_tick
            if self.cancel_after_ticks <= since_contact < self.restart_after_ticks:
                vx_target = -min(self.cmd_vx_base, .85) if self.profile == 'restart_reverse' else 0.
                neutral_at_riser = vx_target == 0.
        if self.command_tick != self.k:
            if neutral_at_riser:
                self.command_vx = 0.
            if vx_target < 0 < self.command_vx or vx_target > 0 > self.command_vx:
                self.command_vx = 0.0
            self.command_vx += (vx_target - self.command_vx) * DT / .14
            self.command_tick = self.k
        self.intent_ok = forward_intent(vx_target, wz)
        self.intent = vx_target
        self.steering = wz
        self.next_height = cab_h
        return self.command_vx, wz, cab_h

    def sample_contact(self):
        if not self.active_steps:
            return 0., 0., np.zeros(2, np.float32)
        edge, _, top = self.active_steps[0]
        platform = self.step_gids[0]
        forces = np.zeros(6)
        riser, tire = 0.0, 0.0
        supports = np.zeros(2, np.float32)
        for i in range(self.d.ncon):
            c = self.d.contact[i]
            g1, g2 = c.geom
            if platform not in (g1, g2):
                continue
            other = int(g2 if g1 == platform else g1)
            mj.mj_contactForce(self.m, self.d, i, forces)
            force = abs(float(forces[0]))
            wheel_idx = np.flatnonzero(self.tire_gids == other)
            on_top = abs(c.frame[2]) > .70 and c.pos[0] > edge + .003 and c.pos[2] >= top - .015
            if on_top and len(wheel_idx):
                supports[wheel_idx[0]] += force
            elif c.pos[0] <= edge + .040:
                riser = max(riser, force)
                if len(wheel_idx):
                    tire = max(tire, force)
        return riser, tire, supports

    def _driver_resumed(self):
        return (self.profile in RESTART_PROFILES and self.hit_tick is not None
                and self.k - self.hit_tick >= self.restart_after_ticks)

    def target(self):
        # Classification labels only. Policy sees proprioception and commands from the normal observation.
        if self.profile not in CLIMB_PROFILES or not self.intent_ok or self.recovered:
            return False
        if self.held_top:
            return self.k - self.cleared_at < 15
        if self.hit_tick is None:
            return False
        edge = self.active_steps[0][0]
        # Proximity alone cannot label renewed forward motion as a climb.
        # Use new contact after the pause, or a riser still bearing load now.
        onset = self.hit_tick
        if self._driver_resumed():
            onset = self.restart_contact_tick
            if onset is None:
                return bool(self.k == self.last_hit)
        return bool(self.k - self.last_hit <= 16 or (self.d.geom_xpos[self.tire_gids, 0].min() > edge - .14
                    and self.k - onset <= 90))

    def step(self, action, gate, raw_gate=None):
        if raw_gate is None:
            raw_gate = gate
        intent_before = self.intent
        legal_before = self.intent_ok
        old_x = float(self.d.qpos[0])
        old_vx = self.body_vx
        old_z = self.d.geom_xpos[self.tire_gids, 2].min()
        before_target = self.target()
        resumed = self._driver_resumed() and legal_before
        if resumed and self.restart_x is None:
            self.restart_x = self.restart_max_x = old_x
        # The frozen native environment still handles integration, motor limits, delay and fall checks.
        executed = self.delayed_act.copy() if self.action_delay > 0 and self.k > 0 else action
        substep_speed = 0.0
        if self.measure_substeps:
            normal_step = mj.mj_step
            contacts = []

            def measured_step(m, d):
                nonlocal substep_speed
                normal_step(m, d)
                contacts.append(self.sample_contact())
                substep_speed = max(substep_speed, abs(float(d.qvel[0])))

            mj.mj_step = measured_step
            try:
                st, _, done, info = super().step(action, float(gate))
            finally:
                mj.mj_step = normal_step
            hit = max(c[0] for c in contacts)
            tire = max(c[1] for c in contacts)
            supports = np.mean([c[2] for c in contacts], axis=0)
            st['obs'][22:28] = executed
        else:
            st, _, done, info = super().step(action, float(gate))
            hit, tire, supports = self.sample_contact()
        x = float(self.d.qpos[0])
        vx = self.body_vx
        pitch = abs(pitch_deg(self.d, self.env.base_id))
        self.p_peak = max(self.p_peak, pitch)
        self.peak_forward_speed = max(self.peak_forward_speed, abs(vx), substep_speed)
        self.max_hit_force = max(self.max_hit_force, hit)
        self.support_force = supports
        if hit > 2.5 and not self.held_top:
            self.last_hit = self.k
            if self.hit_tick is None:
                self.hit_tick, self.first_hit_x, self.max_x_after_hit = self.k, x, x
        if resumed:
            if hit > 2.5 and self.restart_contact_tick is None:
                self.restart_contact_tick = self.k
            if not self.held_top:
                self.restart_max_x = max(self.restart_max_x, x)
                self.restart_backtrack = max(self.restart_backtrack, self.restart_max_x - x)
        if tire > 2.5 and self.first_tire_hit is None:
            self.first_tire_hit = self.k * DT
        if gate > .0 and before_target:
            self.near_gate_max = max(self.near_gate_max, float(gate))
        if not before_target:
            if not legal_before or self.profile in ('wall', 'restart_wall', 'flat'):
                self.invalid_gate_max = max(self.invalid_gate_max, float(gate))
            if self.hit_tick is None:
                self.prewall_gate_max = max(self.prewall_gate_max, float(gate))
        if self.hit_tick is not None and not self.held_top and legal_before:
            self.max_x_after_hit = max(self.max_x_after_hit, x)
            self.backtrack = max(self.backtrack, self.max_x_after_hit - x)
            self.contact_stall_ticks += int(vx < .08)
        if self.hit_tick is not None and not legal_before and self.profile in ('reverse', 'turn', 'stop') and self.switch_x is None:
            self.switch_x = x
        if self.switch_x is not None:
            self.wall_backup_m = max(self.wall_backup_m, self.switch_x - x)
            self.end_delta_after_switch = x - self.switch_x
            self.min_reverse_vx = min(self.min_reverse_vx, vx)

        on_top = bool((supports > 5.0).all())
        self.ever_supported |= on_top
        self.support_ticks = self.support_ticks + 1 if on_top else 0
        new_top = self.support_ticks == 20 and not self.held_top
        if new_top:
            self.held_top = True
            self.cleared_at = self.k
        recovered = self.held_top and on_top and float(self.d.qpos[2]) - .20 >= self.next_height - .036 and gate < .10
        new_recovered = recovered and not self.recovered
        self.recovered |= recovered

        action_delta = float(np.square(action - self.prev_exec).mean())
        self.prev_exec = executed.copy()
        is_main = self.profile in CLIMB_PROFILES and legal_before
        if is_main:
            wheel_z = float(self.d.geom_xpos[self.tire_gids, 2].min())
            progress_limit = .60 * DT if self.high_slow_focus else .035
            reward = 3.2 * min(progress_limit, x - old_x)
            if self.hit_tick is None:
                reward += .035 * math.exp(-9 * (vx - intent_before)**2)
                reward -= .12 * float(raw_gate)
            elif not self.held_top:
                reward += 3.0 * float(np.clip(wheel_z - old_z, -.025, .025))
                reward -= .06 * max(0.0, .09 - vx)
                reward -= .08 * max(0.0, -vx) + .65 * max(0.0, old_x - x)
                reward -= .03 * min(2., hit / 500.)
            else:
                reward += .05 * math.exp(-12 * (vx - self.intent)**2)
            reward += .04 if on_top else 0.0
            reward += 4.5 if new_top else 0.0
            reward += 1.0 if new_recovered else 0.0
            reward -= .003 * max(0., pitch - 15.)
            if self.high_slow_focus and self.hit_tick is not None:
                # Score physical completion first and remove the gain from
                # surging past the driving command during lift and capture.
                excess_speed = max(0.0, max(abs(vx), substep_speed) - .60)
                reward -= .18 * min(1.0, (excess_speed / .22) ** 2)
                reward -= 3.0 * max(0.0, old_x - x)
                if new_top and self.peak_forward_speed <= .60:
                    reward += 2.0
        else:
            reward = .06 * math.exp(-7 * (vx - intent_before)**2) - .25 * float(raw_gate)
        reward -= .002 * min(action_delta, 20.)
        if info['fell_reason']:
            reward -= 3.0
        info.update(profile=self.profile, requested_height_m=self.request_height, stance_rise=self.rise,
                    support_0p4=self.held_top, recovered=self.recovered,
                    backtrack_m=self.backtrack, stall_s=self.contact_stall_ticks * DT,
                    hit_s=None if self.hit_tick is None else self.hit_tick * DT,
                    mount_s=None if self.cleared_at is None else self.cleared_at * DT,
                    peak_riser_force=self.max_hit_force, peak_pitch_deg=self.p_peak,
                    prewall_gate_max=self.prewall_gate_max, invalid_gate_max=self.invalid_gate_max,
                    near_gate_max=self.near_gate_max, retreat_m=self.wall_backup_m,
                    restart_backtrack_m=self.restart_backtrack if self.restart_x is not None else None,
                    restart_contact=self.restart_contact_tick is not None,
                    final_vx=vx, min_reverse_vx=self.min_reverse_vx,
                    peak_forward_speed_m_s=self.peak_forward_speed)
        return st, reward, done, info


class JumpFixture(Mod4v3InstantJumpEnv):
    """Adds height and landing-quality objectives to Gemini's native jump plant."""

    moving_focus = False
    require_top_support = False

    def __init__(self, seed):
        super().__init__(seed=seed, xml_path=ensure_instant_jump_scene_xml(HERE / 'runtime_cache/jump'))

    def start(self, profile='stationary', height=.28, speed=0., dr=0., trigger=.90, step_distance=.50):
        self.profile = profile
        self.top_support_ticks = 0
        self.longest_top_support_ticks = 0
        self.flight_pitch = 0.0
        self.landing_pitch = 0.0
        self.backtrack = 0.0
        self.min_vx = 0.0
        self.init_x = None
        self.max_dx = 0.0
        self.clearance = 0.0
        self.target_clearance = .30
        self.landing_vx = None
        self.first_air_t = None
        self.landed = False
        near = profile == 'step'
        edge = speed * .75 + step_distance + .06
        return self.reset(dr_scale=dr, scenario_kind='move_step' if near else 'flat_stat' if speed == 0 else 'flat_move',
                          steps=[(edge, 4.5, .20)] if near else [], step_trigger_dws=[(0, step_distance)] if near else [],
                          jump_times=() if near else (trigger,), v_cmd=speed, v_jump=speed, h_nom=height,
                          max_episode_s=3.25 if near else 2.75)

    def sample(self, dr, role):
        r = self.rng
        p = r.random()
        profile = 'stationary' if p < .58 else 'moving' if p < .78 else 'step'
        speed = 0.0 if profile == 'stationary' else float(r.uniform(.62, 1.20))
        h = float(r.choice([.28,.28,.28,.30,.34,.38,.40]))
        if self.moving_focus:
            profile = 'moving' if p < .55 else 'step'
            speed = float(r.choice([.65, .80, .90, .90, 1.02]))
            h = float(r.choice([.275, .28, .28, .28, .285]))
        return self.start(profile,h,speed,dr,float(r.uniform(.65,1.20)),float(r.uniform(.52,.75)))

    def step(self, action, gate=0.0):
        active = self.jump_rem_steps > 0
        old_x = float(self.d.qpos[0])
        if active and self.init_x is None:
            self.init_x = old_x
        old_clearance = self.clearance
        was_landed = self.landed
        strict_step = self.require_top_support and self.profile == 'step'
        had_hold = self.longest_top_support_ticks >= 20
        if strict_step:
            normal_step = mj.mj_step
            load_sum = np.zeros(2)
            force = np.zeros(6)
            edge, _, top = self.active_steps[0]
            step_gid = self.step_gids[0]

            def measured_step(model, data):
                normal_step(model, data)
                for index in range(data.ncon):
                    contact = data.contact[index]
                    a, b = map(int, contact.geom)
                    if step_gid not in (a, b) or abs(contact.frame[2]) < .7:
                        continue
                    tire_gid = b if a == step_gid else a
                    if tire_gid not in self.tire_gids or contact.pos[0] <= edge + .004 or contact.pos[2] < top - .015:
                        continue
                    mj.mj_contactForce(model, data, index, force)
                    load_sum[self.tire_gids.index(tire_gid)] += abs(force[0])

            mj.mj_step = measured_step
            try:
                st, native, done, info = super().step(action)
            finally:
                mj.mj_step = normal_step
            load_mean = load_sum * self.m.opt.timestep / DT
            beyond_edge = (self.d.geom_xpos[self.tire_gids, 0] > edge + .004).all() and self.d.qpos[0] > edge + .02
            self.top_support_ticks = self.top_support_ticks + 1 if (load_mean >= 5.).all() and beyond_edge else 0
            self.longest_top_support_ticks = max(self.longest_top_support_ticks, self.top_support_ticks)
        else:
            st, native, done, info = super().step(action)
        vx = self.body_vx
        pitch = abs(pitch_deg(self.d, self.base_id))
        if self.init_x is not None:
            dx = float(self.d.qpos[0]) - self.init_x
            self.max_dx = max(self.max_dx, dx)
            self.min_vx = min(self.min_vx, vx)
            self.backtrack = max(self.backtrack, self.max_dx - dx, -dx)
            self.clearance = max(self.clearance, self.window_peak_rel_rim)
            self.flight_pitch = max(self.flight_pitch, self.window_max_air_pitch_deg)
            if self.window_launched and self.first_air_t is None:
                self.first_air_t = self.window_lift_latency_ms
            self.landed |= self.window_landed
            if self.landed:
                self.landing_pitch = max(self.landing_pitch, pitch)
                if not was_landed:
                    self.landing_vx = vx
            backwards = max(0., -vx - .04)
            drift = abs(vx) if self.profile == 'stationary' else 0.0
            # Positive clearance is based on measured BOTH-wheel rim clearance, only while airborne.
            reward = .35 * native + 9.0 * max(0., self.clearance - old_clearance)
            reward -= .32 * backwards + .12 * drift + .22 * min(.30, self.backtrack)
            if self.moving_focus:
                reward += 20. * (min(self.clearance, .375) - min(old_clearance, .375))
                reward -= .20 * backwards
            reward -= .008 * max(0., pitch - 9.) if self.landed else .004 * max(0., pitch - 9.)
            if self.landed and not was_landed:
                reward += 2.0 * np.clip((self.clearance - .23) / .12, 0., 1.)
                reward -= .25 * abs(vx - (0.0 if self.profile == 'stationary' else self.cmd_vx))
            if strict_step:
                if 0 < self.top_support_ticks <= 20 and self.landing_pitch < 15.:
                    reward += .14
                if not had_hold and self.longest_top_support_ticks >= 20 and self.backtrack <= .07:
                    reward += 4.
            if done and not info['fell_reason']:
                support_ok = not strict_step or self.longest_top_support_ticks >= 20 and not info['slid_off_step']
                if support_ok and self.landed and self.clearance >= self.target_clearance and self.backtrack <= .06 and self.landing_pitch <= 15.:
                    reward += .60
        else:
            reward = .15 * native
        if info['fell_reason']:
            reward -= 2.0
        info.update(profile=self.profile, clearance_m=self.clearance, backtrack_m=self.backtrack,
                    air_pitch_deg=self.flight_pitch, landing_pitch_deg=self.landing_pitch, landed=self.landed,
                    lift_ms=self.first_air_t, landing_vx=self.landing_vx, min_vx=self.min_vx)
        if strict_step:
            info['held_top_s'] = self.longest_top_support_ticks * DT
        return st, float(reward), done, info


class LeapFixture(Mod4v3ForwardLeapEnv):
    """Keep the validated forward-leap request and optimize measured retreat and landing."""

    stance_dr = False
    height_focus = False
    moving_focus = False

    def __init__(self, seed):
        super().__init__(seed=seed, xml_path=ensure_forward_leap_scene_xml(HERE / 'runtime_cache/leap'))

    def sample(self, dr, role):
        self.profile = 'stationary'
        self.start_x = None
        self.max_x = None
        self.backtrack = 0.
        self.landing_pitch = 0.
        trigger = float(self.rng.uniform(.82, 1.34))
        height = float(self.rng.choice([.275, .28, .28, .28, .285] if self.stance_dr else
                                       [.28, .28, .28, .30, .32, .36, .40, .42]))
        speed = 0.
        steps = []
        if self.moving_focus:
            speed = float(self.rng.choice([.57, .74, .90, .90, 1.05]))
            trigger += .35
            self.profile = 'moving'
            if self.rng.random() < .40:
                self.profile = 'step'
                edge = self.step_front_for_moving_jump(speed, trigger, lead_dist=float(self.rng.uniform(.62, .86)))
                steps = [(edge, 3., float(self.rng.choice([.16, .20, .24])))]
        return self.reset(dr_scale=dr, v_cmd=speed, h_nom=height, jump_times=(trigger,), steps=steps,
                          max_episode_s=trigger + 2.25, init_pose=(0., 0., float(self.rng.uniform(-.10, .10))))

    def step(self, action, gate=0.):
        previous_clearance = self.window_peak_rel_rim
        if self.cur_window_idx >= 0 and self.start_x is None:
            self.start_x = self.max_x = float(self.d.qpos[0])
        st, native, done, info = super().step(action)
        if self.start_x is None:
            return st, float(native), done, info | self.statistics()
        previous_retreat = self.backtrack
        x = float(self.d.qpos[0])
        self.max_x = max(self.max_x, x)
        self.backtrack = max(self.backtrack, self.max_x - x)
        pitch = abs(pitch_deg(self.d, self.base_id))
        if self.window_landed:
            self.landing_pitch = max(self.landing_pitch, pitch)
        reward = float(native) - 12. * (self.backtrack - previous_retreat)
        vx = self.body_vx
        reward -= .12 * max(0., -vx - .02)
        if self.window_landed:
            reward -= .012 * max(0., pitch - 9.)
            # Let the chassis absorb touchdown, then track the actual zero-speed stick.
            landing_age = float(self.d.time) - self.window_land_time
            if landing_age >= .18:
                reward += .12 * math.exp(-((vx - self.cmd_vx) / .22) ** 2)
                reward -= .03 * min(abs(vx - self.cmd_vx), 2.)
        if done and not info['fell_reason'] and self.window_landed:
            reward += 4. * np.clip((self.window_peak_rel_rim - .27) / .08, 0., 1.)
        if self.height_focus:
            # Reward new two-wheel apex rather than time spent above ground.
            clearance_gain = max(0., min(.38, self.window_peak_rel_rim) - min(.38, previous_clearance))
            reward += 55. * clearance_gain
            reward -= 18. * (self.backtrack - previous_retreat)
            reward -= .24 * max(0., -vx - .02)
            if self.window_landed:
                reward -= .016 * max(0., pitch - 8.)
                if landing_age >= .25:
                    speed_error = abs(vx - self.cmd_vx)
                    reward += .18 * math.exp(-((speed_error / .18) ** 2))
                    reward -= .13 * min(speed_error, 1.5)
            if done and self.window_landed and not info['fell_reason']:
                quality = (self.backtrack <= .04 and self.landing_pitch <= 13.)
                reward += 6. * quality * np.clip((self.window_peak_rel_rim - .30) / .055, 0., 1.)
        return st, float(reward), done, info | self.statistics()

    def statistics(self):
        return dict(profile=self.profile, clearance_m=float(self.window_peak_rel_rim), backtrack_m=self.backtrack,
                    landing_pitch_deg=self.landing_pitch, landed=bool(self.window_landed))

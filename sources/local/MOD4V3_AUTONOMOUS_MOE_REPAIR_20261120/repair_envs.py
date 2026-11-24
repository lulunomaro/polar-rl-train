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
    parked_retake_focus = False
    wasd_restart_focus = False
    stair_recovery_focus = False
    low_impact_focus = False

    def start(self, profile='climb', height=0.28, speed=0.9, offset=0.0, yaw=0.0,
              dr=0.0, rise=False, distance=1.35, wall_height=.50, drive_at=None):
        self.profile = profile
        self.measure_substeps = getattr(self, "measure_substeps", False)
        self.request_height = float(height)
        self.drive_at_s = drive_at
        self.rise = rise
        self.intent = speed
        self.steering = 0.0
        self.cancel_after_ticks = 0
        self.restart_after_ticks = 0
        if profile in RESTART_PROFILES:
            cancel = (2, 15) if self.wasd_restart_focus else (3, 11)
            pause = (17, 85) if self.wasd_restart_focus else (31, 64)
            self.cancel_after_ticks = int(self.rng.integers(*cancel))
            self.restart_after_ticks = self.cancel_after_ticks + int(self.rng.integers(*pause))
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
            step_heights=step, step_x1=distance, height_cmd=0.28 if rise or self.wasd_restart_focus else height,
            cmd_vx=speed, start_x=offset, start_yaw=yaw, max_steps=450 if self.wasd_restart_focus else 410,
        )
        if self.wasd_restart_focus:
            # The player starts at the standard pose and lets the policy reach the selected height.
            # Keep vertical command, spawn height and the first observation independent.
            self.d.qpos[2] = .282
            mj.mj_forward(self.m, self.d)
            st['obs'] = self._get_obs()
            st['priv'] = self._get_priv()
            self.hist_buf = np.repeat(st['obs'][None, :], self.hist_buf.shape[0], axis=0)
            st['hist'] = self.hist_buf.reshape(-1).copy()
        return st

    def sample(self, dr, role):
        r = self.rng
        p = r.random()
        if self.stair_recovery_focus:
            tall = role == 'stair' or r.random() < .43
            if role == 'router' and self.mid_stance_focus:
                height = float(r.uniform(.307, .376))
                speed = float(r.uniform(.79, .99))
            else:
                height = float(r.uniform(.394, .42) if tall else r.uniform(.276, .357))
                speed = float(r.uniform(.42, .57) if tall else r.uniform(.81, .98))
            if role == 'stair':
                profile = 'restart' if p < .55 else 'climb' if p < .84 else 'restart_reverse' if p < .95 else 'flat'
            else:
                profile = 'restart' if p < .36 else 'restart_wall' if p < .65 else 'climb' if p < .87 else 'flat'
            # Hold the selected stance across both initial approach and renewed drive.
            # Variation in departure delay, pose and dwell decouples contact from the command edge.
            delay = float(r.uniform(.42, 1.30))
            return self.start(profile, height, speed, float(r.uniform(-.075, .075)),
                              math.radians(float(r.uniform(-5., 5.))), dr, distance=1.20,
                              wall_height=float(r.choice([.45, .50])), drive_at=delay)
        if self.low_impact_focus:
            profile = ('climb' if p < .55 else 'restart' if p < .86 else
                       'restart_reverse' if p < .95 else 'flat')
            height = float(r.choice([.28, .28, .28, .28, .29, .30, .32, .34]))
            return self.start(profile, height, float(r.uniform(.83, .97)), float(r.uniform(-.072, .072)),
                              math.radians(float(r.uniform(-4., 4.))), dr, distance=1.20,
                              drive_at=float(r.uniform(.38, .56)))
        if self.wasd_restart_focus:
            if role == 'stair':
                profile = ('restart' if p < .49 else 'restart_reverse' if p < .73 else
                           'climb' if p < .93 else 'flat')
                height = float(r.choice([.28, .28, .29, .31, .32, .33, .34, .34]))
            else:
                profile = ('restart' if p < .36 else 'restart_reverse' if p < .52 else
                           'restart_wall' if p < .77 else 'climb' if p < .89 else 'flat')
                height = float(r.choice([.28, .28, .31, .34, .36, .40, .42, .42]))
            onset = .40 if r.random() < .55 else float(r.uniform(.65, 1.40))
            return self.start(profile, height, float(r.uniform(.80, 1.00)), float(r.uniform(-.075, .075)),
                              math.radians(float(r.uniform(-9., 9.))), dr, distance=1.20,
                              wall_height=float(r.choice([.45, .50])), drive_at=onset)
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
        if self.restart_focus and self.low_stance_focus:
            if self.parked_retake_focus:
                profile = 'restart' if p < .55 else 'climb' if p < .79 else 'restart_wall' if p < .94 else 'flat'
            else:
                profile = 'restart' if p < .72 else 'restart_wall' if p < .92 else 'flat'
            height = float(r.choice([.28, .29, .30, .31, .32, .33, .34]))
            speed = float(r.uniform(.83, .98))
            return self.start(profile, height, speed, float(r.uniform(-.072, .072)),
                              float(r.uniform(-.05, .05)), dr,
                              distance=float(r.uniform(1.16, 1.25)), wall_height=float(r.choice([.45, .50])))
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
        drive_at = self.drive_at_s
        if drive_at is None:
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
        if self.wasd_restart_focus and on_top:
            edge = self.active_steps[0][0]
            on_top = x > edge and float(self.d.geom_xpos[self.tire_gids, 0].min()) > edge
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
                if self.parked_retake_focus:
                    # Reward renewed forward driving by removing the impulse-then-retreat strategy.
                    # This block only runs when W is active, never during a driver-commanded reverse.
                    reward -= 7. * max(0., old_x - x) + .11 * max(0., -vx)
                    reward -= .006 * max(0., pitch - 18.)
                if self.low_impact_focus and self.k - self.hit_tick < 25:
                    # Penalize retreat during the first guide/step interaction while the driver holds W.
                    reward -= 10. * max(0., old_x - x) + .16 * max(0., -vx)
                    reward -= .009 * max(0., pitch - 16.)
            else:
                reward += .05 * math.exp(-12 * (vx - self.intent)**2)
            reward += .04 if on_top else 0.0
            reward += 4.5 if new_top else 0.0
            reward += 1.0 if new_recovered else 0.0
            reward -= .003 * max(0., pitch - 15.)
            if self.high_slow_focus:
                # The evaluation speed limit covers approach, lift and capture.
                # Reward tracking the driver's target before contact as well.
                excess_speed = max(0.0, max(abs(vx), substep_speed) - .60)
                reward -= .18 * min(1.0, (excess_speed / .22) ** 2)
                reward += .045 * math.exp(-((vx - intent_before) / .16) ** 2)
                if self.hit_tick is not None:
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
    high_takeoff_focus = False
    sustained_high_jump = False
    high_jump_apex_focus = False
    high_jump_impulse_focus = False
    clean_jump_apex = False
    min_landing_apex = 0.
    varied_jump_runup = False
    direct_jump_landing = False
    jump_lip_focus = False
    jump_airborne_height_focus = False
    jump_loaded_push = False
    jump_launch_energy = False
    wasd_crouch_speed = 0.
    direct_mid_focus = False
    touchdown_focus = 0.

    def __init__(self, seed):
        self.queued_jump_s = None
        super().__init__(seed=seed, xml_path=ensure_instant_jump_scene_xml(HERE / 'runtime_cache/jump'))
        self.wasd_spawn_q = None

    def start(self, profile='stationary', height=.28, speed=0., dr=0., trigger=.90, step_distance=.50,
              pose=(0., 0., 0.), drive_at=.40):
        self.profile = profile
        self.drive_at_s = drive_at
        self.queued_jump_s = None
        self.crouch_target = None
        self.crouch_ticks = 0
        self.crouch_pending = False
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
        self.clear_air_frames = 0
        self.clear_air_peak = 0.
        self.main_flight_seen = False
        self.compressed_body_z = .32
        self.push_vz = 0.
        self.launch_energy = 0.
        self.preflight_face_hit = False
        self.window_best_crossing_x = None
        self.lip_margin_m = None
        self.lip_checked = False
        self.first_dual_top_seen = False
        self.direct_top_landing = False
        near = profile == 'step'
        edge = 1.20 if self.high_takeoff_focus else speed * .75 + step_distance + .06
        length = 2.40 if self.high_takeoff_focus else 4.50
        if self.high_takeoff_focus and self.wasd_spawn_q is None:
            # Read the identical neutral reset geometry used by the WASD player.
            sys.path.insert(0, str(LOCAL / 'MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116'))
            from mod4_retarget import Mod4Retarget

            ik = Mod4Retarget()
            init_length = .28 - RADIUS
            self.wasd_spawn_q = ik.fit(np.sqrt(init_length**2 + ik.lateral_offset**2), 0.)['qpos']
            self.nom_geom_friction[self.step_gids] = [.9, .005, .0001]
        episode_seconds = (3.65 if near else 3.10) if self.high_takeoff_focus else (3.25 if near else 2.75)
        episode_seconds += max(0., drive_at - .40)
        if self.wasd_crouch_speed:
            episode_seconds = max(episode_seconds, 4.20 + max(0., drive_at - .40))
        packet = self.reset(dr_scale=dr, scenario_kind='move_step' if near else 'flat_stat' if speed == 0 else 'flat_move',
                            steps=[(edge, length, .20)] if near else [], step_trigger_dws=[(0, step_distance)] if near else [],
                            jump_times=() if near else (trigger,), v_cmd=speed, v_jump=speed, h_nom=height,
                            max_episode_s=episode_seconds, init_pose=pose)
        if self.high_takeoff_focus:
            self.d.qpos[2] = .282
            self.d.qpos[7:] = self.wasd_spawn_q[7:]
            mj.mj_forward(self.m, self.d)
            packet = {'obs': self._compute_obs(), 'priv': self._compute_priv()}
        return packet

    def configure_steps(self, steps):
        super().configure_steps(steps)
        if self.high_takeoff_focus and steps:
            gid = self.step_gids[0]
            self.m.geom_size[gid, 1] = 1.30
            self.m.geom_rbound[gid] = np.linalg.norm(self.m.geom_size[gid])

    def _high_jump_at_tread_speed(self):
        return bool(RADIUS * self.d.qvel[self.active_dadr[4:]].min() >= .57)

    def _trigger_jump_window(self, now):
        if self.wasd_crouch_speed:
            self.crouch_target = self.h_nom
            self.crouch_pending = True
            return
        if self.jump_airborne_height_focus and not self._high_jump_at_tread_speed():
            self.queued_jump_s = now
            return
        super()._trigger_jump_window(now)

    def _update_triggers(self, now):
        if self.queued_jump_s is not None:
            # The request frame counts as the first of 13 control ticks in the WASD player.
            if self._high_jump_at_tread_speed() or now >= self.queued_jump_s + 12 * DT - 1e-6:
                self.queued_jump_s = None
                super()._trigger_jump_window(now)
                return True
            return False
        delay = .04 if self.jump_airborne_height_focus else .16
        if self.varied_jump_runup and now < self.drive_at_s + delay - 1e-6:
            return False
        return super()._update_triggers(now)

    def prepare_step_commands(self):
        if self.wasd_crouch_speed:
            now = float(self.d.time)
            was_pending = self.crouch_pending
            if self.crouch_pending and self.crouch_target <= .280001 and self.crouch_ticks == 9:
                self.crouch_pending = False
                super()._trigger_jump_window(now)
            else:
                self._update_triggers(now)
            if self.crouch_pending:
                self.crouch_target = max(.28, self.crouch_target - .28 * DT)
                if self.crouch_target <= .280001:
                    self.crouch_ticks += 1
            elif self.crouch_target is not None and not self.jump_rem_steps:
                self.crouch_target = min(self.h_nom, self.crouch_target + .12 * DT)
            self.height_cmd = self.h_nom if self.crouch_target is None else self.crouch_target
            goal = self.v_cmd_pre if now >= self.drive_at_s - 1.e-6 else 0.
            if was_pending:
                goal = min(goal, self.wasd_crouch_speed)
            self.cmd_vx += (goal - self.cmd_vx) * DT / .14
            return
        super().prepare_step_commands()
        if self.high_takeoff_focus:
            # The interactive player applies the selected stance before pressing W.
            self.height_cmd = self.h_nom
            if self.d.time < self.drive_at_s - 1.e-6:
                self.cmd_vx = 0.

    def sample(self, dr, role):
        r = self.rng
        p = r.random()
        if self.wasd_crouch_speed:
            profile = 'step' if p < .62 else 'moving'
            height = float(r.uniform(.312, .42))
            delay = float(r.uniform(.36, .56) if r.random() < .68 else r.uniform(.95, 1.50))
            pose = (float(r.uniform(.33, .43)) if profile == 'step' else 0., 0.,
                    math.radians(float(r.uniform(-3.5, 3.5))))
            distance = float(r.uniform(.74, 1.02))
            return self.start(profile, height, float(r.uniform(.83, .98)), dr, delay + float(r.uniform(.44, .95)),
                              distance, pose, drive_at=delay)
        if self.direct_mid_focus:
            profile = 'step' if p < .55 else 'moving'
            height = float(r.uniform(.309, .376))
            delay = float(r.uniform(.36, .55) if r.random() < .72 else r.uniform(.95, 1.42))
            pose = (float(r.uniform(.32, .44)) if profile == 'step' else 0., 0.,
                    math.radians(float(r.uniform(-3.5, 3.5))))
            return self.start(profile, height, float(r.uniform(.83, .99)), dr,
                              delay + float(r.uniform(.36, .70)), float(r.uniform(.59, .87)), pose,
                              drive_at=delay)
        if self.high_takeoff_focus:
            step_fraction = .46 if self.jump_launch_energy else .56 if self.clean_jump_apex else .74
            profile = 'step' if p < step_fraction else 'moving'
            height = float(r.choice([.32, .35, .36, .38, .40, .42, .42]))
            if self.jump_lip_focus:
                if profile == 'step' and r.random() < .60:
                    delay = float(r.uniform(1.11, 1.57))
                    distance = float(r.uniform(.64, .75))
                    pose = (float(r.uniform(.44, .575)), 0., math.radians(float(r.uniform(-4., 4.))))
                    return self.start(profile, height, float(r.uniform(.81, 1.0)), dr,
                                      delay + .9, distance, pose, drive_at=delay)
            if self.varied_jump_runup:
                delay = float(r.uniform(.95, 1.55)) if r.random() < .52 else .40
                speed = float(r.uniform(.76, 1.04))
                pose = (float(r.uniform(.38, .53)) if profile == 'step' else 0., 0.,
                        math.radians(float(r.uniform(-5., 5.))))
                return self.start(profile, height, speed, dr, delay + float(r.uniform(.52, .98)),
                                  float(r.uniform(.57, .74)), pose, drive_at=delay)
            speed = float(r.uniform(.80, 1.00))
            pose = (float(r.uniform(.42, .53)) if profile == 'step' else 0., 0., math.radians(float(r.uniform(-3., 3.))))
            return self.start(profile, height, speed, dr, float(r.uniform(1.04, 1.42)),
                              float(r.uniform(.58, .72)), pose)
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
        had_face_hit = self.preflight_face_hit
        was_landed = self.landed
        previous_compression, previous_push = self.compressed_body_z, self.push_vz
        previous_launch_energy = self.launch_energy
        strict_step = self.require_top_support and self.profile == 'step'
        measure_flight = self.sustained_high_jump and self.init_x is not None
        had_hold = self.longest_top_support_ticks >= 20
        face_hit = short_hop = False
        crossing_gain = 0.
        lip_shortfall = 0.
        if strict_step or measure_flight:
            normal_step = mj.mj_step
            load_sum = np.zeros(2)
            force = np.zeros(6)
            edge, _, top = self.active_steps[0] if strict_step else (math.inf, 0., 0.)
            step_gid = self.step_gids[0] if strict_step else None
            tire_ids = set(self.tire_gids)

            def measured_step(model, data):
                nonlocal face_hit, short_hop, crossing_gain, lip_shortfall
                normal_step(model, data)
                tire_loaded = ground_contact = False
                for index in range(data.ncon):
                    contact = data.contact[index]
                    a, b = map(int, contact.geom)
                    has_step = step_gid in (a, b)
                    tire_contact = a in tire_ids or b in tire_ids
                    if not (has_step or measure_flight and tire_contact):
                        continue
                    mj.mj_contactForce(model, data, index, force)
                    normal = abs(force[0])
                    tire_loaded |= tire_contact and normal > 2.
                    ground_contact |= tire_contact and normal > 2. and abs(contact.frame[2]) >= .7
                    if has_step:
                        side = abs(contact.frame[2]) < .7
                        side_impact = side and normal > 50. and contact.pos[0] < edge + .01
                        face_hit |= side_impact
                        if self.clean_jump_apex and (active or self.crouch_pending) and side_impact and not self.main_flight_seen:
                            self.preflight_face_hit = True
                        tire_gid = b if a == step_gid else a
                        if not side and tire_gid in tire_ids and contact.pos[0] > edge + .004 and contact.pos[2] >= top - .015:
                            load_sum[self.tire_gids.index(tire_gid)] += normal
                if not measure_flight or self.landed:
                    return
                if self.high_jump_impulse_focus and active and ground_contact and not self.main_flight_seen:
                    age = float(data.time) - self.window_t0
                    compression_end = .255 if self.jump_loaded_push else .225
                    if .035 <= age < compression_end:
                        # Count only a load-bearing compression at forward rolling speed.
                        # A static or backward crouch is a poor seed for a moving jump.
                        forward_loaded = not self.jump_loaded_push or data.qvel[0] > .25
                        if forward_loaded:
                            floor = .205 if self.jump_loaded_push else .22
                            z = max(floor, float(data.qpos[2]) - self.window_g0)
                            self.compressed_body_z = min(z, self.compressed_body_z)
                    if .11 <= age < .36:
                        push_cap = 2.35 if self.jump_loaded_push else 2.1
                        self.push_vz = max(self.push_vz, min(push_cap, float(data.qvel[2])))
                rim = float(data.geom_xpos[self.tire_gids, 2].min()) - RADIUS - self.window_g0
                if self.jump_launch_energy and active and not self.preflight_face_hit and not self.main_flight_seen:
                    # A loaded extension gives the body upward velocity before the rim clears.
                    # Score this only on the upward stroke with both tires supported by level ground,
                    # so guide impacts and a momentary unloaded leg flick cannot earn impulse reward.
                    age = float(data.time) - self.window_t0
                    if .08 <= age < .36 and data.qvel[0] > .22 and data.qvel[2] > .6:
                        wheel_support = set()
                        for index in range(data.ncon):
                            contact = data.contact[index]
                            if abs(contact.frame[2]) < .7 or contact.pos[2] > self.window_g0 + .022:
                                continue
                            for geom in contact.geom:
                                if int(geom) in tire_ids:
                                    mj.mj_contactForce(model, data, index, force)
                                    if abs(force[0]) >= 5.:
                                        wheel_support.add(int(geom))
                        if wheel_support == tire_ids:
                            kinetic_apex = float(data.qvel[2])**2 / (2. * abs(model.opt.gravity[2]))
                            self.launch_energy = max(self.launch_energy, min(.30, kinetic_apex))
                # Reward forward tire clearance while there is vertical margin over the near lip.
                if (self.varied_jump_runup and strict_step and active and not tire_loaded
                        and not self.preflight_face_hit and rim > top - self.window_g0 + .015):
                    crossing = float(np.clip(data.geom_xpos[self.tire_gids, 0].min() - edge, -.30, .10))
                    before = -.30 if self.window_best_crossing_x is None else self.window_best_crossing_x
                    crossing_gain += max(0., crossing - before)
                    self.window_best_crossing_x = max(before, crossing)
                if self.jump_lip_focus and strict_step and active and self.main_flight_seen and not self.lip_checked:
                    # Score the wheel that is furthest behind at the descending lip crossing.
                    # Guide impacts and platform-supported wheel lift cannot earn flight credit.
                    top_from_launch = top - self.window_g0
                    if self.clearance > top_from_launch + .025 and (rim <= top_from_launch + .008 or ground_contact):
                        self.lip_margin_m = float(data.geom_xpos[self.tire_gids, 0].min()) - edge
                        lip_shortfall = float(np.clip(.04 - self.lip_margin_m, 0., .32))
                        self.lip_checked = True
                if active and rim > .018 and not tire_loaded:
                    self.clear_air_frames += 1
                    self.clear_air_peak = max(self.clear_air_peak, rim)
                    # A brief leg retract at the start can leave both tires unloaded.
                    # Do not close the jump window at the end of that small hop.
                    if (self.clear_air_frames * model.opt.timestep >= .12 - 1.e-7
                            and self.clear_air_peak >= self.min_landing_apex):
                        if not self.main_flight_seen:
                            self.first_air_t = max(0., 1000. * (float(data.time) - self.window_t0
                                                                - (self.clear_air_frames - 1) * model.opt.timestep))
                            self.main_flight_seen = True
                        self.clearance = max(self.clearance, self.clear_air_peak)
                        self.flight_pitch = max(self.flight_pitch, abs(pitch_deg(data, self.base_id)))
                elif tire_loaded or rim <= .018:
                    if self.main_flight_seen:
                        self.landed = bool(ground_contact)
                    else:
                        short_hop |= self.clear_air_frames * model.opt.timestep >= .02
                    self.clear_air_frames = 0
                    self.clear_air_peak = 0.

            mj.mj_step = measured_step
            try:
                st, native, done, info = super().step(action)
            finally:
                mj.mj_step = normal_step
            if strict_step:
                load_mean = load_sum * self.m.opt.timestep / DT
                beyond_edge = ((self.d.geom_xpos[self.tire_gids, 0] > edge + .004).all()
                               and self.d.qpos[0] > edge + .02)
                supported = (load_mean >= 5.).all() and beyond_edge
                if supported and not self.first_dual_top_seen:
                    self.first_dual_top_seen = True
                    self.direct_top_landing = active and self.main_flight_seen and not self.preflight_face_hit
                self.top_support_ticks = self.top_support_ticks + 1 if supported else 0
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
            if not self.sustained_high_jump:
                self.clearance = max(self.clearance, self.window_peak_rel_rim)
                self.flight_pitch = max(self.flight_pitch, self.window_max_air_pitch_deg)
                just_started_air = self.window_launched and self.first_air_t is None
                if just_started_air:
                    self.first_air_t = self.window_lift_latency_ms
                self.landed |= self.window_landed
            else:
                just_started_air = old_clearance == 0. and self.clearance > 0.
            if self.landed:
                self.landing_pitch = max(self.landing_pitch, pitch)
                if not was_landed:
                    self.landing_vx = vx
            backwards = max(0., -vx - .04)
            drift = abs(vx) if self.profile == 'stationary' else 0.0
            # Positive clearance is based on measured BOTH-wheel rim clearance, only while airborne.
            reward = .35 * native + 9.0 * max(0., self.clearance - old_clearance)
            reward -= .32 * backwards + .12 * drift + .22 * min(.30, self.backtrack)
            if self.sustained_high_jump:
                # Credit an apex only during an uninterrupted flight of at least 120 ms.
                # Ground-truth contacts and the rim height are used solely in training.
                gain = min(self.clearance, .37) - min(old_clearance, .37)
                apex_weight = 66. if self.high_jump_apex_focus else 32.
                if self.direct_jump_landing and strict_step:
                    # Keep the 30 cm jump target, while giving a much greater value to a real landing.
                    gain = min(self.clearance, .32) - min(old_clearance, .32)
                    apex_weight = 48.
                if self.jump_lip_focus:
                    gain = min(self.clearance, .38) - min(old_clearance, .38)
                    apex_weight = 58. if strict_step else 82.
                if self.jump_airborne_height_focus:
                    # Increase the value of an actual main-flight apex while retaining all lip and landing checks.
                    floor, ceiling = .22, .345
                    gain = float(np.clip(self.clearance, floor, ceiling) - np.clip(old_clearance, floor, ceiling))
                    apex_weight = 130. if strict_step else 155.
                if self.clean_jump_apex and self.preflight_face_hit:
                    gain = 0.
                reward = apex_weight * gain + .04 * float(np.clip(vx, 0., 1.3)) + 7. * crossing_gain
                if self.jump_lip_focus:
                    reward += 9. * crossing_gain - 22. * lip_shortfall
                    reward -= .35 * backwards
                if self.jump_launch_energy:
                    reward += 15. * (self.launch_energy - previous_launch_energy)
                    if self.preflight_face_hit and not had_face_hit:
                        reward -= 15. * previous_launch_energy
                if self.high_jump_impulse_focus and not self.preflight_face_hit:
                    compression_weight = 15. if self.clean_jump_apex else 26.
                    push_weight = 1.8
                    if self.jump_loaded_push:
                        # Reward progress toward the stance used by the 31 cm moving jump
                        # before the sparse main-flight height and lip rewards arrive.
                        compression_weight = 39.
                        push_weight = 4.0
                    reward += compression_weight * (previous_compression - self.compressed_body_z)
                    reward += push_weight * (self.push_vz - previous_push)
                if self.clean_jump_apex and self.preflight_face_hit and not had_face_hit:
                    reward -= 7.0
                    reward -= (39. if self.jump_loaded_push else 15.) * (.32 - previous_compression)
                    if self.jump_loaded_push:
                        reward -= 4.0 * previous_push
                reward -= .45 * backwards + .32 * min(.40, self.backtrack)
                reward -= .32 * float(short_hop) + .23 * float(face_hit)
                if just_started_air:
                    deadline_ms = 370. if self.clean_jump_apex else 400.
                    reward += .85 * float(np.clip((deadline_ms - self.first_air_t) / 220., -.5, 1.))
            if self.moving_focus:
                if not (self.direct_jump_landing and strict_step):
                    reward += 20. * (min(self.clearance, .375) - min(old_clearance, .375))
                reward -= .20 * backwards
            if self.high_takeoff_focus:
                if not self.sustained_high_jump and self.first_air_t is not None and just_started_air:
                    reward += 1.6 * float(np.clip((300. - self.first_air_t) / 170., -.5, 1.))
                if self.profile == 'step' and not self.landed:
                    distance = self.active_steps[0][0] - float(self.d.geom_xpos[self.tire_gids, 0].max())
                    if distance < .22:
                        lip_clearance = self.last_world_rim_m - self.active_steps[0][2]
                        reward -= .17 * float(np.clip(-lip_clearance / .16, 0., 1.25))
            reward -= .008 * max(0., pitch - 9.) if self.landed else .004 * max(0., pitch - 9.)
            if self.jump_airborne_height_focus and self.main_flight_seen and not self.landed:
                reward -= .006 * max(0., pitch - 10.) ** 2
            if self.touchdown_focus and self.landed:
                pitch_rate = abs(float(self.d.qvel[4]))
                reward -= self.touchdown_focus * (.008 * max(0., pitch - 7.) ** 2
                                                   + .012 * max(0., pitch_rate - .6) ** 2)
            if self.landed and not was_landed and not self.preflight_face_hit:
                reward += 2.0 * np.clip((self.clearance - .23) / .12, 0., 1.)
                reward -= .25 * abs(vx - (0.0 if self.profile == 'stationary' else self.cmd_vx))
            if strict_step:
                correct_landing = not self.direct_jump_landing or self.direct_top_landing
                if (correct_landing and 0 < self.top_support_ticks <= 20 and self.landing_pitch < 15.
                        and (self.min_landing_apex == 0. or self.landed and not self.preflight_face_hit)):
                    reward += .20 if self.direct_jump_landing else .14
                if (correct_landing and not had_hold and self.longest_top_support_ticks >= 20
                        and self.backtrack <= .07 and not self.preflight_face_hit):
                    if self.direct_jump_landing:
                        reward += 7.0 + 2.0 * float(np.clip((self.clearance - .25) / .08, 0., 1.))
                    elif self.high_jump_apex_focus and self.landed:
                        # Keep a real landing signal as the apex improves. Give no
                        # completion bonus to a short bounce or a fall onto the platform.
                        reward += 2.5 + 2.0 * float(np.clip((self.clearance - .23) / .08, 0., 1.))
                    elif not self.sustained_high_jump or self.landed and self.clearance >= .28:
                        reward += 4.
            if done and not info['fell_reason']:
                support_ok = not strict_step or (self.longest_top_support_ticks >= 20 and not info['slid_off_step']
                                                 and (not self.direct_jump_landing or self.direct_top_landing))
                if (support_ok and self.landed and self.clearance >= self.target_clearance and self.backtrack <= .06
                        and self.landing_pitch <= 15. and not self.preflight_face_hit):
                    reward += .60
        else:
            reward = .15 * native
        if info['fell_reason']:
            reward -= 2.0
        info.update(profile=self.profile, clearance_m=self.clearance, backtrack_m=self.backtrack,
                    air_pitch_deg=self.flight_pitch, landing_pitch_deg=self.landing_pitch, landed=self.landed,
                    lift_ms=self.first_air_t, landing_vx=self.landing_vx, min_vx=self.min_vx,
                    preflight_face_hit=self.preflight_face_hit, loaded_min_height_m=self.compressed_body_z,
                    loaded_push_vz_m_s=self.push_vz, loaded_launch_energy_m=self.launch_energy)
        if strict_step:
            info['held_top_s'] = self.longest_top_support_ticks * DT
            if self.direct_jump_landing:
                info['direct_held_top'] = self.direct_top_landing and self.longest_top_support_ticks >= 20
            if self.jump_lip_focus:
                info['descending_lip_margin_m'] = self.lip_margin_m
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

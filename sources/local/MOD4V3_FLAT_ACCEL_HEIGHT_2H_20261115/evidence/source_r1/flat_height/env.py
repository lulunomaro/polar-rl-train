"""Keep the strong parent's phase inputs and learn higher motor-driven flat jumps."""
import math
import torch
from isaaclab.utils.math import quat_from_euler_xyz
from mod4v1_scut.math_ops import euler_xyz_from_quat
from mod4v3_ppo_v1.scut_flat_env import tensor
from mod4v3_ppo_v1.scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
from mod4v3_ppo_v1.moving_jump_env import MovingJumpEnv
from .objective import HeightAccount
from .preload import spring_state, ready_to_push, release_fraction, MAX_PREPARATION_S
from .terrain import COLUMNS, ROWS


class FlatHeightEnv(MovingJumpEnv):
    def __init__(self, cfg, meta, bank):
        self._height_ready = False
        super().__init__(cfg, meta, bank)
        n, dev = self.num_envs, self.device
        self.account = HeightAccount(n, dev)
        self.rim_peak = self.account.rim_peak
        self.body_rise_peak = self.account.body_peak
        self.sequence_completed = self.account.settled
        self.lane = (torch.div(torch.arange(n, device=dev), COLUMNS * ROWS, rounding_mode='floor') % 9 - 4) * .55
        self.takeoff_vx = torch.zeros(n, device=dev)
        self.peak_vx = self.takeoff_vx.clone()
        self.approach_height = torch.full((n,), .36, device=dev)
        self.ramp_duration = torch.full((n,), .9, device=dev)
        self.prep_skipped = torch.zeros(n, device=dev, dtype=torch.bool)
        self.prep_duration = torch.zeros(n, device=dev)
        self.request_compression = torch.zeros(n, 2, device=dev)
        self.takeoff_compression = self.request_compression.clone()
        self.push_energy = torch.zeros(n, device=dev)
        self.spring_release = self.push_energy.clone()
        self.flight_rate = self.push_energy.clone()
        limits = tensor(self.robot.root_view.get_dof_limits())[0, self.gas_ids]
        self.spring_lower, self.spring_upper = limits[:, 0], limits[:, 1]
        self.spring_reference = self.gas_targets[0].clone()
        self.spring_stiffness = tensor(self.robot.root_view.get_dof_stiffnesses())[0, self.gas_ids]
        self.task_failure = torch.zeros(n, device=dev, dtype=torch.bool)
        self.reward_components = {}
        self.evaluation = False
        self.admission = False
        self.elapsed = 0.
        self.current_clearance_target = .35
        self.current_body_rise_target = .25
        self.command_vx = (.6, 1.)
        self._height_ready = True

    def set_training_progress(self, seconds):
        self.elapsed = float(seconds)

    def reset_distribution_summary(self):
        return dict(task='flat_accelerated_jump_height', upright_only=True,
                    reset_height_m=.26, yaw_rad=[-.04, .04], initial_velocity=0.,
                    command_vx_m_s=[.6, 1.], command_ramp_s=[.8, 1.1],
                    jump_request_age_s=[1.9, 2.5], preparation_max_s=MAX_PREPARATION_S,
                    approach_height_commands_m=[.26, .30, .36],
                    preparation='skip if already low or both springs >=30mm compressed; stop on readiness',
                    policy_controls_all_six_motors=True, old_phase_input_semantics_retained=True,
                    pose_target_rewards=False, one_flight_per_episode=True,
                    episode_seconds=6., height_reward='20pct incremental,80pct after stable recovery times flight quality',
                    spring_reward='at most2 points once on stable completion; net energy release fraction')

    def _sample_command(self, ids):
        if not self._height_ready:
            return super()._sample_command(ids)
        super(MovingJumpEnv, self)._sample_command(ids)
        self.command[ids] = 0.
        self.command[ids, 0] = self.speed[ids]
        self.height[ids] = self.approach_height[ids]
        self.heading_env[ids] = False
        self.command_timer[ids] = 1e9

    def _pre_physics_step(self, actions):
        if not self._height_ready:
            return super()._pre_physics_step(actions)
        age = self.episode_length_buf * self.step_dt
        self.command[:, 0] = self.speed * (age / self.ramp_duration).clamp(0., 1.)
        self.command[:, 1:] = 0.
        self.height.copy_(self.approach_height)
        self.heading_env.zero_()
        super(MovingJumpEnv, self)._pre_physics_step(actions)

    def _get_observations(self):
        return ScutFlatMixedRemainingDREnv._get_observations(self)

    def _advance_height_task(self, failed):
        d = self.view.data
        age = self.episode_length_buf * self.step_dt
        z = d.root_pos_w[:, 2] - self.scene.env_origins[:, 2]
        forces = tensor(self.scene['contacts'].data.net_forces_w)
        supported = forces[:, self.wheel_sensor_ids, 2] > 5.
        no_support = torch.linalg.vector_norm(forces, dim=-1).sum(-1) < 1.
        wheel = d.body_pos_w[:, self.wheel_ids]
        rim = wheel[:, :, 2].amin(-1) - self.scene.env_origins[:, 2] - .0625
        roll, pitch, _ = euler_xyz_from_quat(d.root_quat_w)
        roll, pitch = roll.abs(), pitch.abs()
        q = tensor(self.robot.data.joint_pos)[:, self.active_ids]
        delta = torch.stack((q[:, 0] - q[:, 1], q[:, 2] - q[:, 3]), -1).mean(-1)
        gas_q = tensor(self.robot.data.joint_pos)[:, self.gas_ids]
        compression, energy = spring_state(gas_q, self.spring_lower, self.spring_upper,
                                           self.spring_reference, self.spring_stiffness)
        preloaded = ready_to_push(compression, z)
        ready = (self.phase == 0) & (age >= self.cue)
        self.request_compression[ready] = compression[ready]
        self.prep_skipped[ready] = preloaded[ready]
        self.reference_height[ready] = z[ready]
        self.reference_x[ready] = d.root_pos_w[ready, 0]
        self.phase[ready], self.phase_time[ready] = 1, age[ready]
        compressed = (self.phase == 1) & preloaded
        self._count((compressed & ~self.crouched).nonzero().flatten(), 'crouched')
        self.crouched |= compressed
        push = (self.phase == 1) & (preloaded | (age - self.phase_time >= MAX_PREPARATION_S - 1e-6))
        self.prep_duration[push] = age[push] - self.phase_time[push]
        self.push_energy[push] = energy[push]
        self.phase[push], self.phase_time[push] = 2, age[push]
        extension = (self.phase == 2) & (delta > 1.25)
        self._count((extension & ~self.extended).nonzero().flatten(), 'extended')
        self.extended |= extension
        self.air_count = torch.where(no_support, self.air_count + self.step_dt, torch.zeros_like(self.air_count))
        launch = (self.phase == 2) & ~self.took_off & (self.air_count >= .04 - 1e-6)
        launch &= (d.root_lin_vel_w[:, 2] > .1) & (rim > .005) & ~failed
        releasing = (self.phase == 2) & (~no_support | (self.air_count <= .04 + 1e-6))
        net_release = (self.push_energy - energy).clamp_min(0.)
        self.spring_release = torch.where(releasing, torch.maximum(self.spring_release, net_release), self.spring_release)
        self.takeoff_compression[launch] = compression[launch]
        self._count(launch.nonzero().flatten(), 'takeoff')
        self.took_off |= launch
        self.phase[launch], self.phase_time[launch] = 3, age[launch]
        self.flight_start[launch] = age[launch]
        self.takeoff_vx[launch] = d.root_lin_vel_b[launch, 0]
        self.peak_vx = torch.maximum(self.peak_vx, d.root_lin_vel_b[:, 0].abs())
        flying = (self.phase == 3) & no_support
        self.air_total += flying * self.step_dt
        self.flight_pitch = torch.where(flying, torch.maximum(self.flight_pitch, pitch), self.flight_pitch)
        self.flight_roll = torch.where(flying, torch.maximum(self.flight_roll, roll), self.flight_roll)
        rate = torch.linalg.vector_norm(d.root_ang_vel_b[:, :2], dim=-1)
        self.flight_rate = torch.where(flying, torch.maximum(self.flight_rate, rate), self.flight_rate)
        retract = flying & (delta < .9)
        self._count((retract & ~self.retracted).nonzero().flatten(), 'retracted')
        self.retracted |= retract
        first_contact = (self.phase == 3) & ~no_support
        land = first_contact & supported.any(-1)
        self._count(land.nonzero().flatten(), 'landed')
        self.landed |= land
        self.phase[first_contact], self.phase_time[first_contact] = 4, age[first_contact]
        self.support_history[self._support_slot] = supported.float()
        self._support_slot = (self._support_slot + 1) % 25
        duty = self.support_history.mean(0).amin(-1)
        forbidden = forces[:, self.reward._reset_contact_link_idx].norm(dim=-1).amax(-1) > 1.
        stable = (self.phase == 4) & self.landed & (duty >= .8) & supported.all(-1)
        stable &= (roll < math.radians(15)) & (pitch < math.radians(15))
        stable &= (d.root_lin_vel_w[:, 2].abs() < .3) & (d.root_lin_vel_b[:, 0] > .1) & ~forbidden & ~failed
        self.stable_hold = torch.where(stable, self.stable_hold + self.step_dt, torch.zeros_like(self.stable_hold))
        balanced = (self.flight_pitch <= math.radians(10)) & (self.flight_roll <= math.radians(5))
        physical_complete = (self.stable_hold >= .5 - 1e-6) & (self.air_total >= .16 - 1e-6)
        physical_complete &= balanced & (self.account.rim_peak >= .12)
        motion = (d.root_lin_vel_b[:, 0] >= .3) & (d.root_lin_vel_b[:, 0] <= self.speed + .35)
        balance = torch.exp(-(pitch / .174533).square() - (roll / .0872665).square() - (rate / 1.5).square())
        self.height_events = self.account.update(launch=launch, airborne=flying, landed=first_contact,
            stable=physical_complete, failed=failed, rim=rim,
            body=(z - self.reference_height).clamp_min(0.), balance=balance, moving=motion)
        self._count(self.height_events['complete'].nonzero().flatten(), 'sequence_complete')
        high = self.sequence_completed & (self.rim_peak >= .35) & (self.body_rise_peak >= .25) & ~self.completed
        self._count(high.nonzero().flatten(), 'success')
        self.completed |= high
        self.task_snapshot = dict(phase=self.phase.clone(), requested=(self.phase > 0),
            takeoff=self.took_off.clone(), landed=self.landed.clone(), sequence_complete=self.sequence_completed.clone(),
            success=self.completed.clone(), failed=failed.clone(), rim_peak_m=self.rim_peak.clone(),
            body_rise_peak_m=self.body_rise_peak.clone(), air_s=self.air_total.clone(),
            air_pitch_rad=self.flight_pitch.clone(), air_roll_rad=self.flight_roll.clone(),
            stable_hold_s=self.stable_hold.clone(), command_vx=self.speed.clone(),
            takeoff_vx=self.takeoff_vx.clone(), peak_abs_vx=self.peak_vx.clone(),
            motion_valid=self.account.moving.clone(), takeoff_events=self.account.takeoffs.clone(),
            dense_height_paid=self.account.dense_paid.clone(), deferred_height_paid=self.account.deferred_paid.clone(),
            flight_quality=self.account.flight_quality.clone(), air_pitch_roll_rate_rad_s=self.flight_rate.clone(),
            approach_height_m=self.approach_height.clone(), prep_skipped=self.prep_skipped.clone(),
            prep_duration_s=self.prep_duration.clone(),
            request_compression_left_m=self.request_compression[:, 0].clone(),
            request_compression_right_m=self.request_compression[:, 1].clone(),
            takeoff_compression_left_m=self.takeoff_compression[:, 0].clone(),
            takeoff_compression_right_m=self.takeoff_compression[:, 1].clone(),
            push_spring_energy_J=self.push_energy.clone(), estimated_spring_release_J=self.spring_release.clone(),
            age_s=age.clone(), vx=d.root_lin_vel_b[:, 0].clone())

    def _get_dones(self):
        failed, timeout = ScutFlatMixedRemainingDREnv._get_dones(self)
        if not self._height_ready:
            return failed, timeout
        age = self.episode_length_buf * self.step_dt
        local = self.view.data.root_pos_w - self.scene.env_origins
        boundary = (local[:, 0].abs() > 5.5) | ((local[:, 1] - self.lane).abs() > 1.5)
        overspeed = self.view.data.root_lin_vel_b[:, 0].abs() > 2.
        push_timeout = (self.phase == 2) & (age - self.phase_time > 1.)
        failed |= boundary | overspeed | push_timeout
        self.task_failure = failed.clone()
        self.reward.reset_terminated.copy_(failed)
        self._advance_height_task(failed)
        # Reaching the recovered state is a task terminal, not a failure or bootstrap timeout.
        terminated = failed | self.sequence_completed
        timeout = (timeout | (age >= 6.)) & ~terminated
        self.task_snapshot.update(boundary=boundary, overspeed=overspeed, push_timeout=push_timeout)
        return terminated, timeout

    def _get_rewards(self):
        ScutFlatMixedRemainingDREnv._get_rewards(self)
        if not self._height_ready:
            return torch.zeros(self.num_envs, device=self.device)
        d = self.view.data
        roll, pitch, _ = euler_xyz_from_quat(d.root_quat_w)
        vx = d.root_lin_vel_b[:, 0]
        track = torch.exp(-((vx - self.command[:, 0]) / .3).square())
        balance = torch.exp(-(pitch / .174533).square() - (roll / .0872665).square())
        overspeed = (vx.abs() - self.speed - .25).clamp_min(0.).square()
        energy = (self.applied_motor_torque[:, :4] / 40.).square().mean(-1)
        dense = .5 * track + .3 * balance - .03 * energy - .03 * d.root_ang_vel_b.square().sum(-1) - 20. * overspeed
        flight = (self.phase == 3).float()
        dense -= flight * (4. * ((pitch / .174533).square() + (roll / .0872665).square())
                           + torch.linalg.vector_norm(d.root_ang_vel_b[:, :2], dim=-1).square())
        spring_bonus = 2. * release_fraction(self.push_energy, self.spring_release)
        spring_bonus *= self.height_events['complete'] * self.account.flight_quality
        result = self.height_events['reward'] + spring_bonus + self.step_dt * dense - 40. * self.task_failure
        self.reward_components = dict(height=float(self.height_events['reward'].mean()),
            dense=float((self.step_dt * dense).mean()), failure=float(self.task_failure.float().mean()))
        self.terminal_observations = self._encode()
        return result

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        if not self._height_ready:
            return
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        n = len(ids)
        self.account.reset(ids)
        self.takeoff_vx[ids] = self.peak_vx[ids] = 0.
        for name in ('prep_skipped', 'prep_duration', 'request_compression', 'takeoff_compression',
                     'push_energy', 'spring_release', 'flight_rate'):
            getattr(self, name)[ids] = 0
        self.task_failure[ids] = False
        if self.evaluation or self.admission:
            self.speed[ids] = self.speed.new_tensor([.6, .8, 1.])[torch.div(ids, 5, rounding_mode='floor') % 3]
            self.cue[ids] = 2.2
            case = torch.div(ids, 5, rounding_mode='floor')
            self.approach_height[ids] = self.speed.new_tensor([.26, .30, .36])[torch.div(case, 3, rounding_mode='floor') % 3]
            self.ramp_duration[ids] = .9
        else:
            self.speed[ids] = .6 + .4 * torch.rand(n, device=self.device, generator=self.reset_generator)
            self.cue[ids] = 1.9 + .6 * torch.rand(n, device=self.device, generator=self.reset_generator)
            choice = torch.rand(n, device=self.device, generator=self.reset_generator)
            self.approach_height[ids] = torch.where(choice < .2, .26, torch.where(choice < .4, .30, .36))
            self.ramp_duration[ids] = .8 + .3 * torch.rand(n, device=self.device, generator=self.reset_generator)
        root = tensor(self.robot.data.default_root_state)[ids].clone()
        root[:, :3] = self.scene.env_origins[ids]
        root[:, 0] -= 3.
        root[:, 1] += self.lane[ids]
        pick = int((self._bank_h - .26).abs().argmin())
        root[:, 2] += self._bank_h[pick]
        yaw = .08 * torch.rand(n, device=self.device, generator=self.reset_generator) - .04
        zero = torch.zeros_like(yaw)
        root[:, 3:7] = quat_from_euler_xyz(zero, zero, yaw)
        root[:, 7:] = 0.
        q = self._bank_q[pick, self._bank_ids].expand(n, -1).clone()
        self.robot.write_root_state_to_sim(root, env_ids=ids)
        self.robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)
        self._sample_command(ids)
        self.reward.command.copy_(self.command)
        self.reward.height_cmd.copy_(self.height)

    def summary(self):
        return dict(counts={k: v.tolist() for k, v in self.counts.items()},
            grouping=['fullDR', 'nominal'], rim_peak_max_m=float(self.rim_peak.max()),
            body_rise_peak_max_m=float(self.body_rise_peak.max()),
            max_takeoffs_per_episode=int(self.account.takeoffs.max()),
            reward_components=self.reward_components, closure_peak_m=float(self.closure_error.max()),
            done_totals=dict(self.done_totals))

"""PPO controls all six motors; only task requests and measured terrain are supplied."""
import math
import torch
from isaaclab.utils.math import quat_from_euler_xyz
from mod4v1_scut.math_ops import euler_xyz_from_quat
from mod4v3_ppo_v1.scut_flat_env import tensor
from mod4v3_ppo_v1.scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
from mod4v3_ppo_v1.stair_training_repair import install_native_done_repair
from .objective import Outcome, scan_target, task_slots
from .terrain import HEIGHTS, EDGE, NEXT_EDGE


class AutonomousStairEnv(ScutFlatMixedRemainingDREnv):
    def __init__(self, cfg, meta, bank):
        self._task_ready = False
        super().__init__(cfg, meta, bank)
        self.leg_pd_decimation, self.wheel_pd_decimation = 4, 1
        n, dev = self.num_envs, self.device
        self.outcome = Outcome(n, dev)
        self.speed = torch.full((n,), .6, device=dev)
        self.cue = torch.full((n,), 1., device=dev)
        self.requested = torch.zeros(n, device=dev, dtype=torch.bool)
        self.level = torch.ones(n, device=dev, dtype=torch.long)
        self.task_height = torch.full((n,), .04, device=dev)
        self.start_x = torch.zeros(n, device=dev)
        self.edge_distance = torch.ones(n, device=dev)
        self.observed_height = self.task_height.clone()
        self.tread = torch.full((n,), 1.5, device=dev)
        self.edge_anchor = torch.zeros(n, 2, device=dev)
        self.target_direction = torch.zeros(n, 2, device=dev)
        self.target_direction[:, 0] = 1.
        self.sensed_air = self.requested.clone()
        self.previous_action = torch.zeros(n, 6, device=dev)
        self.components = {}
        self.events = {}
        self.counts = torch.zeros(2, len(HEIGHTS), 6, device=dev, dtype=torch.long)
        self.count_columns = ['episodes', 'takeoff', 'crossed_in_air', 'both_wheels_top', 'success', 'failure']
        self.wheel_ids = self.reward._wheel_link_idx
        self.wheel_sensor_ids = [self.scene['contacts'].body_names.index(x)
                                 for x in ('left_wheel_link', 'right_wheel_link')]
        self.elapsed = 0.
        self.evaluation = False
        self.admission = False
        self.command_vx = (.4, .8)
        self.command_wz = (0., 0.)
        self.heading_fraction = self.standing_fraction = 0.
        self.height_range = (.36, .36)
        self.rough_terrain = True
        self._task_ready = True

    def _make_reward(self, meta):
        value = super()._make_reward(meta)
        install_native_done_repair(value)
        return value

    def reset_distribution_summary(self):
        return dict(task='autonomous_stair_jump', upright_only=True,
                    initial_gap_m=[1.05, 1.35], yaw_rad=[-.04, .04],
                    request_age_s=[.8, 1.3], command_vx_m_s=[.4, .8],
                    episode_seconds=8., motor_phase_schedule=False,
                    nominal_fraction=.2, full_DR_ranges_unchanged=True)

    def set_training_progress(self, elapsed):
        self.elapsed = float(elapsed)

    def _count(self, mask, column):
        ids = mask.nonzero().flatten()
        if ids.numel():
            group = self.full_dr.nominal_env_mask[ids].long()
            flat = (group * len(HEIGHTS) + self.level[ids]) * 6 + column
            self.counts.view(-1).scatter_add_(0, flat, torch.ones_like(flat))

    def _sample_command(self, ids):
        super()._sample_command(ids)
        if self._task_ready:
            self.command[ids] = 0.
            self.command[ids, 0] = self.speed[ids]
            self.height[ids] = .36
            self.heading_env[ids] = False
            self.command_timer[ids] = 1e9

    def _pre_physics_step(self, actions):
        if self._task_ready:
            age = self.episode_length_buf * self.step_dt
            self.command[:, 0] = self.speed * ((age - .2) / .3).clamp(0., 1.)
            self.command[:, 1:] = 0.
            self.height.fill_(.36)
            self.heading_env.zero_()
            new = ~self.requested & (age >= self.cue)
            self._update_perception()
            self.requested |= new
            self.previous_action.copy_(self.actions)
        super()._pre_physics_step(actions)

    def _update_perception(self):
        d = self.view.data
        yaw = euler_xyz_from_quat(d.root_quat_w)[2]
        distance, height, tread = scan_target(tensor(self.scene['terrain_scan'].data.ray_hits_w), d.root_pos_w, yaw)
        unlocked = ~self.requested
        direction = torch.stack((yaw.cos(), yaw.sin()), -1)
        self.edge_anchor[unlocked] = (d.root_pos_w[:, :2] + direction * distance[:, None])[unlocked]
        self.target_direction[unlocked] = direction[unlocked]
        self.observed_height[unlocked] = height[unlocked]
        self.tread[unlocked] = tread[unlocked]
        self.edge_distance = ((self.edge_anchor - d.root_pos_w[:, :2]) * self.target_direction).sum(-1)

    def prepare_endpoint(self):
        super().prepare_endpoint()
        if not self._task_ready:
            return
        r = self.reward
        wheels = self.view.data.body_pos_w[:, self.wheel_ids]
        grounds = []
        for side, name in enumerate(('ground_left', 'ground_right')):
            hits = tensor(self.scene[name].data.ray_hits_w)
            distance = (hits[:, :, :2] - wheels[:, side, None, :2]).square().sum(-1)
            index = distance.argmin(-1)
            value = hits[:, :, 2].gather(1, index[:, None]).squeeze(1)
            grounds.append(torch.where(torch.isfinite(value), value, self.scene.env_origins[:, 2]))
        r.ground_wheels = torch.stack(grounds, -1)
        r.ground_z_est = r.ground_wheels.amin(-1)
        r._stair_course_mask.fill_(True)
        r._stair_guide_allowed.zero_()
        r._invalidate_step_caches()

    def _get_dones(self):
        fail, timeout = super()._get_dones()
        if not self._task_ready:
            return fail, timeout
        d = self.view.data
        local = d.root_pos_w - self.scene.env_origins
        vx = d.root_lin_vel_b[:, 0]
        fail |= (local[:, 0].abs() > 4.35) | (local[:, 1].abs() > 1.5) | (vx.abs() > 2.)
        roll, pitch, _ = euler_xyz_from_quat(d.root_quat_w)
        forces = tensor(self.scene['contacts'].data.net_forces_w)
        self.events = self.outcome.update(
            requested=self.requested, wheel=d.body_pos_w[:, self.wheel_ids],
            forces=forces[:, self.wheel_sensor_ids], all_force=forces,
            edge=self.scene.env_origins[:, 0] + EDGE,
            next_edge=self.scene.env_origins[:, 0] + NEXT_EDGE,
            ground=self.scene.env_origins[:, 2], height=self.task_height,
            vz=d.root_lin_vel_w[:, 2], vx=vx, command_vx=self.speed,
            roll=roll, pitch=pitch, angular=d.root_ang_vel_b, terminated=fail)
        self.sensed_air = self.events['air']
        for key, column in (('takeoff', 1), ('crossing', 2), ('landing', 3), ('success', 4)):
            self._count(self.events[key], column)
        self._count(fail, 5)
        self.task_failure = fail.clone()
        self.reward.reset_terminated.copy_(fail)
        finished = fail | self.events['success']
        timeout = (timeout | (self.episode_length_buf * self.step_dt >= 8.)) & ~finished
        self.task_snapshot = dict(
            level=self.level.clone(), height_m=self.task_height.clone(), requested=self.requested.clone(),
            takeoff=self.outcome.took_off.clone(), crossed=self.outcome.crossed.clone(),
            landed=self.outcome.landed.clone(), success=self.outcome.success.clone(),
            max_air_s=self.outcome.max_air.clone(), rim_peak_m=self.outcome.rim_peak.clone(),
            stable_hold_s=self.outcome.max_stable.clone(), air_pitch_rad=self.outcome.air_pitch.clone(),
            air_roll_rad=self.outcome.air_roll.clone(), vx=vx.clone(), failed=fail.clone(),
            edge_distance_m=self.edge_distance.clone(), sensed_step_height_m=self.observed_height.clone())
        return finished, timeout

    def _get_rewards(self):
        super()._get_rewards()
        if not self._task_ready:
            return torch.zeros(self.num_envs, device=self.device)
        d = self.view.data
        roll, pitch, _ = euler_xyz_from_quat(d.root_quat_w)
        vx = d.root_lin_vel_b[:, 0]
        track = torch.exp(-((vx - self.command[:, 0]) / .35).square())
        balance = torch.exp(-(roll / .15).square() - (pitch / .30).square())
        torque = (self.applied_motor_torque[:, :4] / 40.).square().mean(-1)
        smooth = (self.actions - self.previous_action).square().mean(-1)
        overspeed = ((vx.abs() - self.speed - .25).clamp_min(0.) / .35).square()
        dense = track + .5 * balance - .03 * torque - .02 * smooth - 3. * overspeed
        dense -= .025 * d.root_ang_vel_b.square().sum(-1)
        opportunity = self.requested & ~self.outcome.took_off & (self.edge_distance > .05) & (self.edge_distance < 1.1)
        dense += .6 * opportunity * d.root_lin_vel_w[:, 2].clamp(0., 2.) * balance
        event = self.events
        bonus = (2. * event['takeoff'] + 8. * event['crossing'] + 6. * event['landing']
                 + 25. * event['success'] + 15. * event['clearance_gain'] * balance)
        result = self.step_dt * dense + bonus - 8. * self.task_failure
        self.components = dict(tracking=float(track.mean()), overspeed=float(overspeed.mean()),
                               reward=float(result.mean()))
        self.terminal_observations = self._encode()
        return result

    def _encode(self):
        raw = super()._encode()
        if self._task_ready:
            self._update_perception()
            slots = task_slots(self.requested, self.sensed_air, self.edge_distance,
                               self.observed_height, self.tread, self.view.data.root_lin_vel_w[:, 2])
            raw['policy'][:, 28:35] = slots
            raw['critic'][:, 32:39] = slots
        return raw

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        if not self._task_ready:
            return
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        n = len(ids)
        if self.evaluation:
            levels = 4 + torch.div(ids, 5, rounding_mode='floor') % 2
        elif self.admission:
            levels = torch.div(ids, 5, rounding_mode='floor') % len(HEIGHTS)
        else:
            maximum = 2 + int(self.elapsed >= 900.) + int(self.elapsed >= 1800.) + int(self.elapsed >= 3600.)
            levels = torch.randint(1, maximum + 1, (n,), device=self.device, generator=self.reset_generator)
            sample = torch.rand(n, device=self.device, generator=self.reset_generator)
            levels = torch.where(sample > .9, 5, torch.where(sample > .8, 4, levels))
        self.level[ids] = levels
        self.task_height[ids] = self.speed.new_tensor(HEIGHTS)[levels]
        terrain = self.scene.terrain
        terrain.terrain_levels[ids] = levels
        terrain.env_origins[ids] = terrain.terrain_origins[levels, 0]
        self.outcome.reset(ids)
        self.requested[ids] = self.sensed_air[ids] = False
        self.previous_action[ids] = 0.
        self.speed[ids] = .4 + .4 * torch.rand(n, device=self.device, generator=self.reset_generator)
        self.cue[ids] = .8 + .5 * torch.rand(n, device=self.device, generator=self.reset_generator)
        gap = 1.05 + .3 * torch.rand(n, device=self.device, generator=self.reset_generator)
        root = tensor(self.robot.data.default_root_state)[ids].clone()
        root[:, :3] = self.scene.env_origins[ids]
        root[:, 0] += EDGE - gap
        self.start_x[ids] = root[:, 0]
        pick = int((self._bank_h - .26).abs().argmin())
        root[:, 2] += self._bank_h[pick]
        yaw = .08 * torch.rand(n, device=self.device, generator=self.reset_generator) - .04
        zero = torch.zeros_like(yaw)
        root[:, 3:7] = quat_from_euler_xyz(zero, zero, yaw)
        root[:, 7:] = 0.
        q = self._bank_q[pick, self._bank_ids].expand(n, -1).clone()
        self.robot.write_root_state_to_sim(root, env_ids=ids)
        self.robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)
        self.zero_torque_remaining[ids] = 0
        self._ground_command_until[ids] = 0
        self._sample_command(ids)
        self.reward.reset(ids)
        for cause in ('contact', 'orientation', 'other'):
            for suffix in ('_counter', '_raw_buf'):
                value = getattr(self.reward, '_stair_' + cause + suffix, None)
                if value is not None:
                    value[ids] = 0
        self.reward.command.copy_(self.command)
        self.reward.height_cmd.copy_(self.height)
        mask = torch.zeros(self.num_envs, device=self.device, dtype=torch.bool)
        mask[ids] = True
        self._count(mask, 0)

    def summary(self):
        return dict(counts=self.counts.tolist(), grouping=['fullDR', 'nominal'],
                    heights_m=list(HEIGHTS), columns=self.count_columns,
                    curriculum_elapsed_s=self.elapsed, reward_components=self.components,
                    closure_peak_m=float(self.closure_error.max()), done_totals=dict(self.done_totals))

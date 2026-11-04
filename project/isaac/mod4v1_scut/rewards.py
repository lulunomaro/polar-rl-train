"""MOD4 measurements -> unchanged pinned SCUT reward and state-machine bodies.

MIT SCUT source and attribution are referenced in SOURCES.json. The adaptation
below owns name/coordinate/geometry differences; upstream.py owns exact formulas.
"""
from types import SimpleNamespace
import torch

from .config import LEGS, WHEELS, WHEEL_BODIES, GUIDE_BODIES, STRUCTURAL_BODIES, reward_config
from .math_ops import quat_apply, wrap_to_pi
from .upstream import bind_base_functions, initialize_buffers, state_classes


def indices(actual, requested):
    actual = list(actual)
    if len(set(actual)) != len(actual):
        raise ValueError('Duplicate runtime names')
    return [actual.index(name) for name in requested]


class DataView:
    def __init__(self, data, tensor=lambda x: x, quaternion_order='xyzw'):
        if quaternion_order not in ('xyzw', 'wxyz'):
            raise ValueError('Explicit runtime quaternion order required')
        self.raw, self.tensor, self.quaternion_order = data, tensor, quaternion_order

    def __getattr__(self, name):
        value = self.tensor(getattr(self.raw, name))
        if name.endswith('quat_w') and self.quaternion_order == 'xyzw':
            return value[..., [3, 0, 1, 2]]  # actual MOD4 xyzw -> pinned SCUT wxyz
        return value


class RobotView:
    def __init__(self, robot, tensor=lambda x: x, quaternion_order='xyzw'):
        self.raw, self.data = robot, DataView(robot.data, tensor, quaternion_order)


@bind_base_functions
class ScutRewards:
    def __init__(self, robot, contract, num_envs, device, profile='trained_stair',
                 tensor=lambda x: x, cfg=None, quaternion_order='xyzw'):
        self.robot, self.contract = RobotView(robot, tensor, quaternion_order), contract
        self.num_envs, self.device = num_envs, device
        self.profile = profile
        self.cfg = cfg or reward_config(profile)
        self.step_dt = .02
        self.wheel_radius = .0625
        self._leg_action_dim = 4
        self._wheel_action_dim = 2
        self._legs_act_idx = indices(robot.joint_names, LEGS)
        self._wheel_idx = indices(robot.joint_names, WHEELS)
        self._actuate_idx = self._legs_act_idx + self._wheel_idx
        self._legs_front_idx = indices(robot.joint_names, ('left_crank', 'right_crank'))
        self._legs_rear_idx = indices(robot.joint_names, ('left_hip', 'right_hip'))
        self._left_right_leg_joint_pair_idx = (
            indices(robot.joint_names, LEGS[:2]), indices(robot.joint_names, LEGS[2:]))
        self._wheel_link_idx = indices(robot.body_names, WHEEL_BODIES)
        self._left_wheel_link_idx, self._right_wheel_link_idx = (
            self._wheel_link_idx[:1], self._wheel_link_idx[1:])
        self._wheel_link_count = 2
        self._desired_contact_link_idx = self._wheel_link_idx
        self._guide_link_idx = indices(robot.body_names, GUIDE_BODIES)
        self._undesired_contact_link_idx = indices(robot.body_names, STRUCTURAL_BODIES+GUIDE_BODIES)
        # V14 overrides the base list to include guides. Strict support keeps
        # its own explicit group, independent of the training reward contract.
        self._nonwheel_contact_link_idx = indices(robot.body_names, STRUCTURAL_BODIES+GUIDE_BODIES)
        self._airborne_base_contact_link_idx = indices(robot.body_names, ('chassis',))
        # V14 env.py:134-145: without a gimbal the reset set is base + guides;
        # there is no MOD4 counterpart for either gimbal link.
        self._reset_contact_link_idx = indices(robot.body_names, ('chassis',)+GUIDE_BODIES)
        self.max_episode_length = int(round(self.cfg.episode_length_s / self.step_dt))
        self._terminate_on_obs_outlier = bool(getattr(self.cfg, 'terminate_on_obs_outlier', True))
        self._terminate_obs_abs = float(getattr(self.cfg, 'terminate_obs_abs', 0.))
        self._terminate_obs_print_interval = int(getattr(self.cfg, 'terminate_obs_print_interval', 50))
        self._terminate_obs_print_counter = 0
        self._value_debug_enabled = bool(getattr(self.cfg, 'debug_value_diagnosis', False))
        self._value_debug_step = 0
        for stream in ('policy', 'critic'):
            setattr(self, '_obs_raw_'+stream+'_max_abs', torch.zeros(num_envs, device=device))
            setattr(self, '_obs_raw_'+stream+'_has_nonfinite', torch.zeros(num_envs, dtype=torch.bool, device=device))
        self._previous_applied_torque = torch.zeros_like(self.robot.data.applied_torque)
        self._before_previous_applied_torque = self._previous_applied_torque.clone()
        self._actions = torch.zeros(num_envs, 6, device=device)
        self._previous_actions = self._actions.clone()
        self._before_previous_actions = self._actions.clone()
        self.command = torch.zeros(num_envs, 3, device=device)
        self.command_counter = torch.zeros(num_envs, dtype=torch.long, device=device)
        self.command_generator = SimpleNamespace(command=self.command,
            command_counter=self.command_counter, compute=lambda dt: None)
        self.command_height_sink = None
        self.forward_scan_provider = None
        self.height_cmd = torch.full((num_envs,), .25, device=device)
        self.ground_z_est = torch.zeros(num_envs, device=device)
        self.episode_length_buf = torch.zeros(num_envs, dtype=torch.long, device=device)
        self.reset_terminated = torch.zeros(num_envs, dtype=torch.bool, device=device)
        self._numerical_safety_reset_buf = self.reset_terminated.clone()
        self.common_step_counter = 0
        self.extras, self._episode_sums = {}, {}
        self.ground_wheels = torch.zeros(num_envs, 2, device=device)
        self.forward_points = torch.zeros(num_envs, 2, 3, device=device)
        self.forward_hits = self.forward_points.clone()
        self.near_points, self.near_hits = self.forward_points.clone(), self.forward_points.clone()
        self.contact_sensor = SimpleNamespace(data=SimpleNamespace(
            net_forces_w_history=torch.zeros(num_envs, 3, len(robot.body_names), 3, device=device),
            net_forces_w=torch.zeros(num_envs, len(robot.body_names), 3, device=device)))
        initialize_buffers(self)
        self._invalidate_step_caches()
        cls = state_classes()
        # MOD4 has no SCUT rear2 hinge. Penalize real independent motor stop margins;
        # do not pretend a roller/mimic joint is an anatomical SCUT rear2 joint.
        class MotorLimitAirborne(cls['airborne']):
            def _get_rear2_rear1_joint_limit_terms(machine, env):
                pos, _, vel = env.motor_stop_terms(airborne=True)
                return pos, vel
        selected = []
        if self.cfg.enable_state_machines:
            for key in ('airborne', 'jump_takeoff', 'step_up', 'stair'):
                key_cfg = self.cfg.wheel_forward_scan_cfg if key == 'step_up' else getattr(self.cfg, key+'_state_machine_cfg')
                if key_cfg.get('enabled', False):
                    selected.append(MotorLimitAirborne() if key == 'airborne' else cls[key]())
        self.state_machine_manager = cls['manager'](selected)

    def _get_height_measure_wheel_radius(self):
        return self.wheel_radius

    def _get_effective_height_cmd(self):
        return self.state_machine_manager.get_effective_height_cmd(self, self.height_cmd)

    def _get_wheel_motor_z_axis_align_error_sq(self):
        anchors = self.robot.data.root_pos_w.new_tensor([
            self.contract['joints'][side+'_hip']['local_pos0'] for side in ('left', 'right')])
        root = self.robot.data.root_pos_w
        q = self.robot.data.root_quat_w[:, None, :].expand(-1, 2, -1)
        start = root[:, None, :] + quat_apply(q, anchors[None].expand(self.num_envs, -1, -1))
        vector = self.robot.data.body_pos_w[:, self._wheel_link_idx] - start
        direction = vector / vector.norm(dim=-1, keepdim=True).clamp_min(1.e-6)
        g = root.new_tensor(self.cfg.sim.gravity)
        g = g / g.norm().clamp_min(1.e-6)
        error = (1 - (direction*g).sum(-1).clamp(-1, 1).square()).clamp_min(0).mean(-1)
        tolerance = float(getattr(self.cfg, 'wheel_motor_z_axis_align_tolerance', 0.))
        return (error-tolerance*tolerance).clamp_min(0)

    def motor_stop_terms(self, airborne=False):
        ids = self._legs_act_idx
        limits = self.joint_pos.new_tensor([self.contract['joints'][name]['limits_si'] for name in LEGS])
        low, high = limits.unbind(-1)
        ratio = float(getattr(self.cfg, 'rear2_rear1_joint_limit_boundary_ratio', .03))
        lo_ratio = float(getattr(self.cfg, 'rear2_rear1_joint_limit_lower_boundary_ratio', ratio)) if airborne else ratio
        hi_ratio = float(getattr(self.cfg, 'rear2_rear1_joint_limit_upper_boundary_ratio', ratio)) if airborne else ratio
        lo_margin = (high-low)*min(max(lo_ratio, 0.), .49)
        hi_margin = (high-low)*min(max(hi_ratio, 0.), .49)
        pos = wrap_to_pi(self.joint_pos[:, ids])
        lo_over = (low+lo_margin-pos).clamp_min(0)
        hi_over = (pos-high+hi_margin).clamp_min(0)
        lo = lo_over/lo_margin.clamp_min(1.e-6)
        hi = hi_over/hi_margin.clamp_min(1.e-6)
        torque, vel = self.robot.data.applied_torque[:, ids], self.joint_vel[:, ids]
        position_penalty = (lo+hi).square().sum(-1)
        torque_penalty = ((-torque).clamp_min(0)*lo+torque.clamp_min(0)*hi).square().sum(-1)
        if airborne:
            # Original airborne.py:696 uses a sum of radians, whereas the base
            # env.py:3457 uses normalized squares. Only joint geometry changes.
            position_penalty = (lo_over+hi_over).sum(-1)
            threshold = max(float(getattr(self.cfg, 'rear2_rear1_joint_limit_vel_threshold', 10.)), 0.)
            velocity_penalty = (((lo > 0) & (vel < -threshold)) |
                                ((hi > 0) & (vel > threshold))).float().sum(-1)
        else:
            velocity_penalty = ((-vel).clamp_min(0)*lo+vel.clamp_min(0)*hi).square().sum(-1)
        return position_penalty, torque_penalty, velocity_penalty

    def _get_rear2_rear1_joint_limit_terms(self):
        return self.motor_stop_terms()

    @property
    def joint_pos(self):
        return self.robot.data.joint_pos

    @property
    def joint_vel(self):
        return self.robot.data.joint_vel

    def _get_current_wheel_ground_z_raw(self):
        return self.ground_wheels

    def _get_wheel_relative_ground_heights_raw(self):
        return self.robot.data.body_pos_w[:, self._wheel_link_idx, 2] - self.ground_wheels

    def _get_wheel_forward_scan_cfg(self):
        return self.cfg.wheel_forward_scan_cfg

    def _get_wheel_forward_scan_points(self):
        return self.forward_scan(False)

    def _get_wheel_forward_stair_scan_points(self):
        return self.forward_scan(True)

    def forward_scan(self, stair):
        prefix = '_cached_wheel_forward'+('_stair' if stair else '')
        points = getattr(self, prefix+'_query_points')
        hits = getattr(self, prefix+'_hit_points')
        if points is None or hits is None:
            if self.forward_scan_provider is not None:
                points, hits = self.forward_scan_provider(stair)
            else:
                points, hits = (self.near_points, self.near_hits) if stair else (self.forward_points, self.forward_hits)
            setattr(self, prefix+'_query_points', points)
            setattr(self, prefix+'_hit_points', hits)
            setattr(self, prefix+'_scan_direction_sign', torch.where(self.command[:,0] < 0, -1., 1.))
        return points, hits

    def get_terrain_name_mask(self, names):
        if isinstance(names, str):
            names = (names,)
        return torch.full((self.num_envs,), not names or 'mod4_step270' in names,
                          dtype=torch.bool, device=self.device)

    def _update_ground_height_estimate(self):
        # SDK bridge supplies real ray hits once at this pre-reset endpoint.
        self._cached_ground_height_valid = True

    def _postprocess_reward_terms(self, terms):
        self.raw_terms = {key: value.clone() for key, value in terms.items()}
        result = self.state_machine_manager.apply_reward_term_scales(self, terms)
        if self.profile == 'jump200' and getattr(self.cfg, 'jump200_approach_progress_gate', False):
            # Use only the command and measured body velocity. This changes
            # rewards, not observations, actions, physics or acceptance.
            approaching = (self.jump_takeoff_phase == 0) & (self.command[:, 0] > 0.)
            if hasattr(self, 'jump200_landed_top'):
                approaching &= ~self.jump200_landed_top
            progress = (self.robot.data.root_lin_vel_b[:, 0]
                        / self.command[:, 0].clamp_min(1.e-6)).clamp(0., 1.)
            gate = torch.where(approaching, progress, torch.ones_like(progress))
            for name in ('flat_orientation_x_exp', 'flat_orientation_y_exp',
                         'track_lin_vel_xy', 'track_ang_vel_z', 'track_height_exp_tight'):
                result[name] = result[name] * gate
        self.state_terms = {key: value.clone() for key, value in result.items()}
        return result

    def _debug_print_undesired_contacts(self, *args):
        pass

    def _debug_print_reward_and_state_stats(self, *args):
        # Source env.py:4091-4095 advances this clock at reward tail only when
        # diagnostics are enabled. _get_dones also consumes this exact clock.
        # Keep that behavior even though this adapter omits console printing.
        if self._value_debug_enabled:
            self._value_debug_step += 1

    def _resample_custom_cmd(self, command_counter):
        # env.py:5592-5601. Optional airborne resets/height waves are disabled
        # in both profiles; the saved special velocity modes have no height wave.
        ids = (command_counter > self.command_counter).nonzero().flatten()
        if len(ids):
            self.resample_height(ids)
        self.command_counter = command_counter.clone()
        return ids

    def resample_height(self, ids):
        self.height_cmd[ids] = self._sample_height_command(ids)
        if self.command_height_sink is not None:
            self.command_height_sink(ids, self.height_cmd[ids])

    def cache_raw_observations(self, policy, critic):
        # Cache before clip/scale/sanitize, as env.py:3177 and 3236 require.
        for stream, blocks in (('policy', policy), ('critic', critic)):
            maximum, invalid = self._per_env_max_abs_from_blocks(blocks, self.num_envs, self.device)
            setattr(self, '_obs_raw_'+stream+'_max_abs', maximum)
            setattr(self, '_obs_raw_'+stream+'_has_nonfinite', invalid)

    def _on_command_updated(self):
        # Upstream invokes this at reward tail, then again at observations.
        # Temporal scan results stay cached within that control step.
        self.state_machine_manager.on_command_updated(self)
        self.state_machine_manager.apply_command_overrides(self)
        if hasattr(self, 'jump200_requested'):
            # Request the source takeoff helper only after a measured step
            # event; it cannot apply external force/velocity assistance.
            request = (self.wheel_forward_step_detect_event & ~self.jump200_landed_top
                       & (self.jump_takeoff_phase == 0) & (self.jump_takeoff_cooldown_time <= 0))
            self.jump_takeoff_request |= request
            self.jump200_requested |= request
            # The task is to land and recover, so cease forward commands once
            # both wheels have actually landed after airborne whole clearance.
            self.command[self.jump200_landed_top] = 0.
        self._sync_command_generator_command()  # final V13 hook, inherited by V14

    def _apply_predefined_reset_air_command_limits(self):
        # SCUT predefined airborne reset modes are not part of the ground-start task.
        pass

    def begin(self, actions, commands, height, terminated, bad, episode_length, contacts,
              ground_z, wheel_ground_z, forward_points, forward_hits, near_points, near_hits):
        self.common_step_counter += 1
        self._invalidate_step_caches()
        self._actions = actions.clone()
        # commands is the last returned observation command, including upstream
        # overrides. Refreshing raw generator commands here changes the return.
        self.command = commands.clone()
        self.height_cmd = height.reshape(-1).clone()
        self.reset_terminated, self._numerical_safety_reset_buf = terminated.clone(), bad.clone()
        self.episode_length_buf = episode_length.clone()
        self.contact_sensor.data.net_forces_w_history = contacts
        self.contact_sensor.data.net_forces_w = contacts[:, 0]
        self.ground_z_est, self.ground_wheels = ground_z, wheel_ground_z
        self.forward_points, self.forward_hits = forward_points, forward_hits
        self.near_points, self.near_hits = near_points, near_hits
        if isinstance(self.command_generator, SimpleNamespace):
            self.command_generator.command = self.command

    def compute(self):
        return self._get_rewards()

    def finish_observation(self):
        # env.py:3107-3108, once for each returned observation.
        self._before_previous_actions.copy_(self._previous_actions)
        self._previous_actions.copy_(self._actions)

    def refresh_reset_scans(self, ids, ground, wheel_ground, far, far_hits, near, near_hits):
        """Seed only reset envs from their new pose, without an old-episode delta."""
        for key, value in (('ground_z_est', ground), ('ground_wheels', wheel_ground),
                           ('forward_points', far), ('forward_hits', far_hits),
                           ('near_points', near), ('near_hits', near_hits)):
            getattr(self, key)[ids] = value
        direction = torch.where(self.command[ids, 0] < 0, -1., 1.)
        for prefix, hits in (('wheel_forward', far_hits), ('wheel_forward_stair', near_hits)):
            getattr(self, prefix+'_prev_ground_z')[ids] = hits[..., 2]
            getattr(self, prefix+'_prev_ground_z_valid')[ids] = True
            getattr(self, prefix+'_prev_direction_sign')[ids] = direction
            cache = getattr(self, '_cached_'+prefix+'_temporal_height_diffs', None)
            if cache is not None:
                cache[ids] = 0
            # Keep non-reset endpoints cached while replacing only reset rows.
            for suffix, value in (('_query_points', near if 'stair' in prefix else far),
                                  ('_hit_points', hits), ('_scan_direction_sign', direction)):
                cache = getattr(self, '_cached_'+prefix+suffix, None)
                if cache is not None:
                    cache[ids] = value

    def reset(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long)
        self.state_machine_manager.on_reset(self, ids)
        if hasattr(self, 'jump200_requested'):
            self.jump200_requested[ids] = False
        for name in ('_actions', '_previous_actions', '_before_previous_actions',
                     '_previous_applied_torque', '_before_previous_applied_torque'):
            getattr(self, name)[ids] = 0
        for value in self._episode_sums.values():
            value[ids] = 0
        self.contact_sensor.data.net_forces_w_history[ids] = 0
        self.contact_sensor.data.net_forces_w[ids] = 0
        self.reset_terminated[ids] = False
        self._numerical_safety_reset_buf[ids] = False
        self.episode_length_buf[ids] = 0
        self._clear_termination_duration_buffers(ids)
        for stream in ('policy', 'critic'):
            getattr(self, '_obs_raw_'+stream+'_max_abs')[ids] = 0
            getattr(self, '_obs_raw_'+stream+'_has_nonfinite')[ids] = False
        # Do not discard other environments' within-step scan deltas: upstream
        # invokes the command hook again when constructing observations.
        for key, value in vars(self).items():
            if key.startswith('_cached_') and torch.is_tensor(value) and value.ndim and value.shape[0] == self.num_envs:
                value[ids] = 0
        self._cached_wheel_kinematics_valid = False

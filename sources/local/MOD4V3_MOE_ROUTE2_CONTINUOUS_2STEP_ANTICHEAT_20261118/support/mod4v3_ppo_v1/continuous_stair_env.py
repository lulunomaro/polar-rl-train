"""Anti-cheat 1-step (20cm) + continuous 2-step (20cm+20cm=40cm) stair course with zero-tolerance slide-off termination."""
import json
import math
from pathlib import Path
import torch
from .legacy_continuous_stair_env import _OriginalContinuousStairEnv
from .scut_rough_scut_v1_env import ScutUnifiedRoughV1Env
from .stair_training_repair import ContinuousStairRepairMixin, wheel_center_ground
from .scut_flat_env import tensor
from .fixed200_reward_math import fixed200_reward
from .dense_top_reward import dense_top_support
from .start_offset_partition import OFFSETS_MM, assign_offset_indices
from .single_step_math import SPEC, COURSE, advance, supported_step_band, supported_upper, stable_completion, first_landings
from isaaclab.utils.math import quat_from_euler_xyz
from mod4v1_scut.math_ops import euler_xyz_from_quat, wrap_to_pi


class ContinuousStairEnv(ContinuousStairRepairMixin, _OriginalContinuousStairEnv):
    enforce_closure_reset = False

    def __init__(self, cfg, meta, bank):
        self._course_ready = False
        super().__init__(cfg, meta, bank)
        n = self.num_envs
        dev = self.device
        # Fixed 30% 1-step (level 0) + 70% continuous 2-step (level 1) stratified across stair envs!
        stair_ids = self.continuous_stair_mask.nonzero().flatten()
        init_levels = torch.zeros(n, dtype=torch.long, device=dev)
        if len(stair_ids):
            ordinals = torch.arange(len(stair_ids), device=dev)
            init_levels[stair_ids] = (ordinals % 10 >= 3).long()
        self.assigned_course_level = init_levels.clone()
        self.course_mastered = init_levels.clone()
        self.course_level = init_levels.clone()
        self.terrain.terrain_levels[stair_ids] = self.course_level[stair_ids]

        self.course_success_streak = torch.zeros(n, dtype=torch.long, device=dev)
        self.course_attempts = torch.zeros(2, len(SPEC.heights), dtype=torch.long, device=dev)
        self.course_successes = torch.zeros_like(self.course_attempts)
        self.course_promotions = torch.zeros_like(self.course_attempts)
        self.course_demotions = torch.zeros_like(self.course_attempts)
        self.course_speed_rejections = torch.zeros_like(self.course_attempts)
        self.course_failure_causes = torch.zeros(2, len(SPEC.heights), 3, dtype=torch.long, device=dev)
        self.course_entry_speed = torch.zeros(n, device=dev)
        self.course_speed_max = torch.zeros_like(self.course_entry_speed)
        self.course_hold = torch.zeros_like(self.course_entry_speed)
        self.course_lift_best = torch.zeros(n, 2, device=dev)
        self.course_lift2_best = torch.zeros(n, 2, device=dev)
        self.course_lift_reference = torch.zeros_like(self.course_lift_best)
        self.course_lift2_reference = torch.zeros_like(self.course_lift_best)
        self.course_landed = torch.zeros(n, 2, dtype=torch.bool, device=dev)
        self.course_s1_landed = torch.zeros(n, 2, dtype=torch.bool, device=dev)
        self.course_lift_armed = torch.zeros(n, dtype=torch.bool, device=dev)
        self.course_lift2_armed = torch.zeros(n, dtype=torch.bool, device=dev)
        self.course_entry_seen = torch.zeros(n, dtype=torch.bool, device=dev)
        self.course_success = torch.zeros_like(self.course_entry_seen)
        self.course_progress = torch.zeros(n, device=dev)
        self.course_event_reward = torch.zeros(n, device=dev)
        self.course_reward_sums = torch.zeros(4, device=dev)
        self.course_accounting = False
        self.course_evaluation = False

        # Tight speed ladder starting at 0.78 m/s -> 0.60 m/s (no 1.2 m/s sprinting!)
        self.speed_stage = torch.zeros(n, dtype=torch.long, device=dev)
        self.speed_streak = torch.zeros_like(self.speed_stage)
        self.speed_limits = self.command.new_tensor([0.78, 0.72, 0.68, 0.64, 0.62, 0.60])
        self.speed_completed = torch.zeros(6, device=dev, dtype=torch.long)
        self.speed_penalty_sum = torch.zeros((), device=dev)
        self.strict_hold = torch.zeros(n, device=dev)
        self.strict_success = torch.zeros(n, dtype=torch.bool, device=dev)
        self.strict_success_count = torch.zeros((), device=dev, dtype=torch.long)
        self.course_stop_latched = torch.zeros(n, dtype=torch.bool, device=dev)
        self.course_park_hold = torch.zeros(n, device=dev)
        self.top_latch_events = torch.zeros(2, dtype=torch.long, device=dev)
        self.step1_climb_events = torch.zeros(2, dtype=torch.long, device=dev)
        self.step2_climb_events = torch.zeros(2, dtype=torch.long, device=dev)

        # Anti-cheat step-commitment & regression tracking
        self.s1_wheel_frames = torch.zeros(n, 2, dtype=torch.long, device=dev)
        self.s2_wheel_frames = torch.zeros(n, 2, dtype=torch.long, device=dev)
        self.s1_committed = torch.zeros(n, dtype=torch.bool, device=dev)
        self.s2_committed = torch.zeros(n, dtype=torch.bool, device=dev)
        self.s1_bonus_paid = torch.zeros(n, dtype=torch.bool, device=dev)
        self.step_regressed_now = torch.zeros(n, dtype=torch.bool, device=dev)
        self.step_regression_terminations = torch.zeros((), dtype=torch.long, device=dev)

        self.previous_course_body_x = torch.zeros(n, device=dev)
        self.course_pitch_peak = torch.zeros(n, device=dev)
        self.course_quality_penalty_sum = torch.zeros(9, device=dev)
        self.bilateral_landing_seen = torch.zeros(n, dtype=torch.bool, device=dev)
        self.bilateral_top_now = torch.zeros_like(self.bilateral_landing_seen)
        self.no_progress_seconds = torch.zeros(n, device=dev)
        self.last_reward_breakdown = None
        self.true_top_completion_events = torch.zeros(2, dtype=torch.long, device=dev)

        # Pre-reset snapshots so NativeSuccessRecorder NEVER reads 0.0 after _reset_idx!
        self.replay_success_now = torch.zeros(n, dtype=torch.bool, device=dev)
        self.replay_top_support_count = torch.zeros(n, dtype=torch.long, device=dev)
        self.replay_speed_limit_at_step = torch.zeros(n, device=dev)
        self.replay_episode_max_speed_at_step = torch.zeros(n, device=dev)
        self.replay_entry_speed_at_step = torch.zeros(n, device=dev)
        self.replay_park_hold_at_step = torch.zeros(n, device=dev)
        self.replay_course_level_at_step = torch.zeros(n, dtype=torch.long, device=dev)
        self.replay_actual_DR_at_step = torch.zeros(n, dtype=torch.bool, device=dev)

        self.top_dense_reward_sum = torch.zeros((), device=dev)
        self.last_top_dense = torch.zeros(n, device=dev)
        self.replay_completion_bonus = torch.zeros(n, device=dev)
        self.start_offset_mm = torch.zeros(n, device=dev)
        self.start_offset_index = assign_offset_indices(self.continuous_stair_mask, self.full_dr.nominal_env_mask)
        self.actual_start_offset_index = self.start_offset_index.clone()
        pose = json.loads((Path(__file__).resolve().parents[2] / 'startup_pose.json').read_bytes())
        self.high_startup_q = self.command.new_tensor([pose['joint_pos'][name] for name in self.robot.joint_names])
        self.high_startup_z = float(pose['root_height_m'])
        self.height_aux_ready = torch.zeros(n, dtype=torch.bool, device=dev)
        self.offset_attempts = torch.zeros(2, 5, dtype=torch.long, device=dev)
        self.offset_completion_events = torch.zeros(2, 5, dtype=torch.long, device=dev)
        self.reference_nominal_env_mask = self.full_dr.nominal_env_mask.clone()
        self._course_ready = True

    def _set_origins(self, ids):
        ScutUnifiedRoughV1Env._set_origins(self, ids)
        special = getattr(self.terrain, 'r1_continuous_stair_mask', None)
        if special is not None:
            selected = ids[special[ids]]
            lower = self.terrain.terrain_origins[self.terrain.terrain_levels[selected], self.terrain.terrain_types[selected], 2]
            self.terrain.env_origins[selected, 2] = lower
            self.scene.env_origins[selected, 2] = lower

    def _course_scatter(self, buffer, ids, values):
        if ids.numel():
            index = self.reference_nominal_env_mask[ids].long() * len(SPEC.heights) + self.course_level[ids]
            buffer.view(-1).scatter_add_(0, index, values.long())

    def _finish_course_episodes(self, ids):
        if not self.course_accounting or self.snapshots is None:
            return
        picked = ids[self.continuous_stair_mask[ids] & (self.episode_length_buf[ids] > 0)]
        if not picked.numel():
            return
        ok = self.course_success[picked] & (~self.reset_terminated[picked])
        if not self.course_evaluation:
            self.speed_streak[picked] = torch.where(ok, self.speed_streak[picked] + 1, torch.zeros_like(self.speed_streak[picked]))
            promoted = (self.speed_streak[picked] >= 2) & (self.speed_stage[picked] < len(self.speed_limits) - 1)
            self.speed_stage[picked] += promoted.long()
            self.speed_streak[picked] = torch.where(promoted, torch.zeros_like(self.speed_streak[picked]), self.speed_streak[picked])
        attempted = torch.ones_like(ok)
        new, streak, up, down = advance(self.course_mastered[picked], self.course_level[picked], self.course_success_streak[picked], ok, attempted)
        self._course_scatter(self.course_attempts, picked, attempted)
        offset_group = self.reference_nominal_env_mask[picked].long() * 5 + self.actual_start_offset_index[picked]
        self.offset_attempts.view(-1).scatter_add_(0, offset_group, attempted.long())
        self._course_scatter(self.course_successes, picked, ok)
        self._course_scatter(
            self.course_speed_rejections,
            picked,
            self.course_entry_seen[picked] & ((self.course_entry_speed[picked] > SPEC.maximum_speed) | (self.course_speed_max[picked] > SPEC.maximum_speed)),
        )
        if not self.course_evaluation:
            self._course_scatter(self.course_promotions, picked, up)
            self._course_scatter(self.course_demotions, picked, down)
            self.course_mastered[picked] = torch.maximum(self.assigned_course_level[picked], new)
            self.course_success_streak[picked] = streak
        group = self.reference_nominal_env_mask[picked].long()
        level = self.course_level[picked]
        for k, mask in enumerate((self.reset_terminated[picked], ~self.course_landed[picked].all(1), self.course_landed[picked].all(1) & ~ok)):
            self.course_failure_causes[:, :, k].index_put_((group, level), mask.long(), accumulate=True)

    def _reset_idx(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        ready = getattr(self, '_course_ready', False)
        if ready:
            self._finish_course_episodes(ids)
            picked = ids[self.continuous_stair_mask[ids]]
            if not self.course_evaluation:
                self.course_level[picked] = self.assigned_course_level[picked]
            self.terrain.terrain_levels[picked] = self.course_level[picked]
        ScutUnifiedRoughV1Env._reset_idx(self, ids)
        if not ready:
            return
        self._flat_preservation_commands(ids)
        for cause in ('contact', 'orientation', 'other'):
            for suffix in ('_counter', '_raw_buf'):
                value = getattr(self.reward, '_stair_' + cause + suffix, None)
                if value is not None:
                    value[ids] = 0
        for name in ('_stair_guide_allowed', '_stair_contact_raw', '_stair_suppressed_guide_raw'):
            value = getattr(self.reward, name, None)
            if value is not None:
                value[ids] = False
        for buf in (
            self.course_entry_seen,
            self.course_success,
            self.course_landed,
            self.course_s1_landed,
            self.course_lift_armed,
            self.course_lift2_armed,
            self.course_stop_latched,
            self.s1_committed,
            self.s2_committed,
            self.s1_bonus_paid,
            self.step_regressed_now,
        ):
            buf[ids] = False
        for buf in (
            self.course_entry_speed,
            self.course_speed_max,
            self.course_hold,
            self.course_park_hold,
            self.course_lift_best,
            self.course_lift2_best,
            self.course_progress,
            self.course_event_reward,
            self.s1_wheel_frames,
            self.s2_wheel_frames,
        ):
            buf[ids] = 0
        picked = ids[self.continuous_stair_mask[ids]]
        self.strict_hold[ids] = 0.0
        self.strict_success[ids] = False
        self.course_pitch_peak[ids] = 0.0
        self.previous_course_body_x[ids] = (self.view.data.root_pos_w[ids, 0] - self._center()[ids, 0]) * self.stair_side[ids]
        self.stair_up[ids] = False
        self.stair_mid[ids] = False
        self.stair_goal_hold[ids] = 0.0
        self.stair_stage[ids] = 0
        if not picked.numel():
            return
        self.bilateral_landing_seen[ids] = False
        self.bilateral_top_now[ids] = False
        self.no_progress_seconds[ids] = 0.0
        n = len(picked)
        gen = self.reset_generator
        center = self._center()[picked]
        q = self.high_startup_q[None].expand(n, -1).clone()
        root = tensor(self.robot.data.default_root_state)[picked].clone()
        self.height_aux_ready[ids] = False
        side = torch.where(torch.rand(n, device=self.device, generator=gen) < 0.5, -1.0, 1.0)
        offset = self.command.new_tensor(OFFSETS_MM)[self.actual_start_offset_index[picked]] / 1000.0
        self.start_offset_mm[picked] = offset * 1000.0
        is_two = self.course_level[picked] > 0
        first_edge = torch.where(is_two, self.command.new_full((n,), SPEC.edge_2step_s1), self.command.new_full((n,), SPEC.edge))
        distance = first_edge + 1.2 - offset
        root[:, :3] = center
        root[:, 0] += side * distance
        root[:, 1] += torch.empty(n, device=self.device).uniform_(-0.15, 0.15, generator=gen)
        root[:, 2] += self.high_startup_z
        yaw = torch.where(side < 0, 0.0, math.pi)
        root[:, 3:7] = quat_from_euler_xyz(torch.zeros_like(yaw), torch.full_like(yaw, 0.02), yaw)
        root[:, 7:] = 0.0
        self.robot.write_root_state_to_sim(root, env_ids=picked)
        self.robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=picked)
        self.stair_up[picked] = True
        self.stair_side[picked] = side
        self.stair_start[picked] = distance
        # Commanded relative root height is always 0.4091m before final platform landing!
        self.stair_height[picked] = 0.4091
        self.stair_speed[picked] = torch.empty(n, device=self.device).uniform_(0.35, 0.48, generator=gen)
        self.height[picked] = 0.4091
        self.command[picked] = 0.0
        self.heading_env[picked] = False
        self.standing_env[picked] = True
        self.actions[picked] = 0.0
        self.torque[picked] = 0.0
        self.zero_torque_remaining[picked] = 0
        self._ground_command_until[picked] = 0
        self.r2_air_reset[picked] = False
        self.course_lift_reference[picked] = 0.25
        self.course_lift2_reference[picked] = 0.25
        self.previous_course_body_x[picked] = distance
        self.reward.ground_z_est[picked] = center[:, 2]
        self.reward._invalidate_step_caches()
        self._course_commands()

    def _sample_command(self, ids):
        ScutUnifiedRoughV1Env._sample_command(self, ids)
        if getattr(self, '_course_ready', False):
            self._flat_preservation_commands(ids)
            self._course_commands()

    def _course_commands(self):
        if not getattr(self, '_course_ready', False):
            return
        picked = self.continuous_stair_mask.nonzero().flatten()
        age = self.episode_length_buf[picked] * self.step_dt
        self.height[picked] = self.stair_height[picked]
        # Switch to low stance (0.20m) ONLY after bilateral landing on the FINAL target platform (Step 1 in 1-step, Step 2 in 2-step)!
        self.height[picked] = torch.where(self.bilateral_landing_seen[picked], self.height.new_full((len(picked),), 0.20), self.height[picked])
        moving_cmd = (age >= SPEC.settle_seconds) & (~self.course_stop_latched[picked])
        self.command[picked] = 0.0
        self.command[picked, 0] = torch.where(moving_cmd, self.stair_speed[picked], 0.0)
        self.command_timer[picked] = 1e9
        self.heading_env[picked] = False
        self.standing_env[picked] = ~moving_cmd
        self._ground_original_command[picked] = self.command[picked]
        self._ground_original_heading[picked] = False
        self.reward.command[picked] = self.command[picked]
        self.reward.height_cmd[picked] = self.height[picked]
        self.reward._invalidate_step_caches()

    def _get_observations(self):
        self._course_commands()
        raw = ScutUnifiedRoughV1Env._get_observations(self)
        if getattr(self, '_course_ready', False):
            mask = self.continuous_stair_mask
            for key, mode_slice in (('policy', slice(28, 35)), ('critic', slice(32, 39))):
                raw[key] = raw[key].clone()
                raw[key][mask, mode_slice] = raw[key].new_tensor([0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0])
        return raw

    def _pre_physics_step(self, actions):
        self._course_commands()
        ScutUnifiedRoughV1Env._pre_physics_step(self, actions)
        self._course_commands()

    def prepare_endpoint(self):
        ScutUnifiedRoughV1Env.prepare_endpoint(self)
        if not getattr(self, '_course_ready', False):
            return
        r = self.reward
        wheels = self.view.data.body_pos_w[:, self.stair_wheel_idx]
        ground = torch.stack(
            [wheel_center_ground(tensor(self.scene[name].data.ray_hits_w), wheels[:, side, :2], r.ground_wheels[:, side]) for side, name in enumerate(('ground_left', 'ground_right'))],
            1,
        )
        mask = self.continuous_stair_mask
        self.stair_original_root_ground = r.ground_z_est.clone()
        self.stair_wheel_ground = ground
        r.ground_z_est = torch.where(mask, ground.amin(1), r.ground_z_est)
        r.ground_wheels = torch.where(mask[:, None], ground, r.ground_wheels)
        r._invalidate_step_caches()
        x = (wheels[:, :, 0] - self._center()[:, None, 0]) * self.stair_side[:, None]
        is_two = self.course_level > 0
        near_1step = (x - SPEC.edge).abs().amin(1) < 0.45
        near_2step = ((x - SPEC.edge_2step_s1).abs().amin(1) < 0.45) | ((x - SPEC.edge_2step_s2).abs().amin(1) < 0.45)
        near_edge = torch.where(is_two, near_2step, near_1step)
        r._stair_course_mask = mask
        r._stair_guide_allowed = mask & (~self.course_success) & near_edge

    def _update_course_events(self, term):
        self.course_event_reward.zero_()
        self.step_regressed_now.zero_()
        center = self._center()
        d = self.view.data
        wheel = d.body_pos_w[:, self.stair_wheel_idx]
        forces = tensor(self.scene['contacts'].data.net_forces_w)[:, self.wheel_sensor_ids]
        x = (wheel[:, :, 0] - center[:, None, 0]) * self.stair_side[:, None]
        y = wheel[:, :, 1] - center[:, None, 1]
        z = wheel[:, :, 2] - center[:, None, 2]
        is_two = self.course_level > 0
        final_h = self.command.new_tensor(SPEC.heights)[self.course_level]
        edge1 = torch.where(is_two, self.command.new_full((self.num_envs,), SPEC.edge_2step_s1), self.command.new_full((self.num_envs,), SPEC.edge))
        edge_final = torch.where(is_two, self.command.new_full((self.num_envs,), SPEC.edge_2step_s2), self.command.new_full((self.num_envs,), SPEC.edge))

        active = self.continuous_stair_mask & (~term) & (self.episode_length_buf * self.step_dt >= SPEC.settle_seconds)
        near1 = (x - edge1[:, None]).abs().amin(1) < 0.45
        near2 = is_two & ((x - SPEC.edge_2step_s2).abs().amin(1) < 0.45)
        near = near1 | near2

        speed = tensor(self.robot.data.root_lin_vel_w)[:, :2].norm(dim=-1)
        vx_body = d.root_lin_vel_b[:, 0]
        entering = active & (~self.course_entry_seen) & (x.amin(1) < edge1 + 0.20)
        self.course_entry_speed[entering] = speed[entering]
        self.course_entry_seen |= entering
        self.course_speed_max = torch.where(self.continuous_stair_mask, torch.maximum(self.course_speed_max, speed), self.course_speed_max)

        # Measure true tread support on Step 1 (z=0.20m) and final target platform (z=0.20m for level 0, z=0.40m for level 1)
        s1_tread = torch.where(
            is_two[:, None],
            supported_step_band(x, y, z, forces[:, :, 2], SPEC.edge_2step_s1, SPEC.edge_2step_s2 + 0.02, SPEC.half_width_2step_s1, 0.20),
            supported_upper(x, y, z, forces[:, :, 2], final_h),
        )
        # On 2-step, wheels on Step 2 (z=0.40m) also count as above Step 1 so ascending Step 2 never triggers Step-1 drop!
        upper = supported_upper(x, y, z, forces[:, :, 2], final_h)
        gained_s1, self.course_s1_landed = first_landings(self.course_s1_landed, s1_tread, active)
        gained, self.course_landed = first_landings(self.course_landed, upper, active)

        body_x = (d.root_pos_w[:, 0] - center[:, 0]) * self.stair_side
        roll, pitch, _ = euler_xyz_from_quat(self.robot.data.root_quat_w)
        self.course_pitch_peak = torch.where(self.continuous_stair_mask, torch.maximum(self.course_pitch_peak, wrap_to_pi(pitch).abs()), self.course_pitch_peak)

        # === ZERO-TOLERANCE ANTI-CHEAT: Commit & Drop Detection ===
        self.s1_wheel_frames = torch.where(s1_tread & active[:, None], self.s1_wheel_frames + 1, self.s1_wheel_frames)
        self.s2_wheel_frames = torch.where(upper & active[:, None], self.s2_wheel_frames + 1, self.s2_wheel_frames)
        newly_s1_comm = (~self.s1_committed) & active & (s1_tread.all(1) & (body_x < edge1 - 0.05))
        newly_s2_comm = (~self.s2_committed) & active & (upper.all(1) & (body_x < edge_final - 0.05))
        self.s1_committed |= newly_s1_comm
        self.s2_committed |= newly_s2_comm

        if bool((newly_s1_comm & is_two).any()):
            self.step1_climb_events += torch.bincount(self.reference_nominal_env_mask[newly_s1_comm & is_two].long(), minlength=2)
        if bool((newly_s2_comm & is_two).any()):
            self.step2_climb_events += torch.bincount(self.reference_nominal_env_mask[newly_s2_comm & is_two].long(), minlength=2)

        single_drop_s1 = active & ((self.s1_wheel_frames >= 5) & ((z < 0.20 + SPEC.radius - 0.035) | (x > edge1[:, None] + 0.06))).any(1)
        single_drop_s2 = active & ((self.s2_wheel_frames >= 5) & ((z < final_h[:, None] + SPEC.radius - 0.035) | (x > edge_final[:, None] + 0.06))).any(1)
        bilat_drop_s1 = self.s1_committed & active & ((z < 0.20 + SPEC.radius - 0.035).any(1) | (x > edge1[:, None] + 0.05).any(1))
        bilat_drop_s2 = self.s2_committed & active & ((z < final_h[:, None] + SPEC.radius - 0.035).any(1) | (x > edge_final[:, None] + 0.05).any(1))
        dropped_s1 = bilat_drop_s1 | single_drop_s1
        dropped_s2 = bilat_drop_s2 | single_drop_s2
        step_regressed = dropped_s1 | dropped_s2
        self.step_regressed_now.copy_(step_regressed)
        self.step_regression_terminations += step_regressed.long().sum()
        slide_off_clawback = 25.0 * step_regressed.float()

        self.bilateral_top_now = upper.all(1) & active & (~step_regressed)
        self.bilateral_landing_seen |= self.bilateral_top_now & (body_x < edge_final - SPEC.body_margin)

        limit = self.speed_limits[self.speed_stage]
        climb_failed = term | step_regressed | self.reward._stair_contact_raw | (self.course_pitch_peak > math.radians(38))
        move_stable = stable_completion(
            upper,
            body_x,
            wrap_to_pi(pitch),
            wrap_to_pi(roll),
            d.root_ang_vel_b[:, :2].norm(dim=-1),
            tensor(self.robot.data.root_lin_vel_w)[:, 2],
            self.course_entry_speed,
            self.course_speed_max,
            self.course_entry_seen,
            climb_failed,
            active & (~self.course_stop_latched),
            maximum_allowed=limit,
            final_edge=edge_final,
        )
        self.course_hold = torch.where(self.course_stop_latched, self.course_hold, torch.where(move_stable, self.course_hold + self.step_dt, torch.zeros_like(self.course_hold)))
        newly_latched = (self.course_hold >= SPEC.hold_seconds - 1e-7) & (~self.course_stop_latched)
        self.course_stop_latched |= newly_latched
        if bool(newly_latched.any()):
            self.top_latch_events += torch.bincount(self.reference_nominal_env_mask[newly_latched].long(), minlength=2)
        latch_bonus = torch.where(self.course_speed_max <= 0.60, 12.0, 6.0) * newly_latched.float() * torch.where(is_two, 1.5, 1.0)

        park_stable = (
            upper.all(1)
            & (body_x < edge_final - SPEC.body_margin)
            & (body_x > -edge_final + 0.20)
            & (wrap_to_pi(pitch).abs() < SPEC.maximum_angle)
            & (wrap_to_pi(roll).abs() < SPEC.maximum_angle)
            & (d.root_ang_vel_b[:, :2].norm(dim=-1) < SPEC.maximum_rate)
            & (tensor(self.robot.data.root_lin_vel_w)[:, 2].abs() < 0.25)
            & (speed <= 0.20)
            & self.course_entry_seen
            & (self.course_entry_speed >= SPEC.minimum_entry_speed)
            & (self.course_entry_speed <= limit)
            & (self.course_speed_max <= limit)
            & (~climb_failed)
            & active
        )
        self.course_park_hold = torch.where(self.course_stop_latched & park_stable, self.course_park_hold + self.step_dt, torch.zeros_like(self.course_park_hold))
        completed = self.course_stop_latched & (self.course_park_hold >= 1.0 - 1e-7) & (~self.course_success)
        strict_new = completed & (self.course_entry_speed <= 0.60) & (self.course_speed_max <= 0.60)
        self.strict_hold = torch.where(self.course_stop_latched & park_stable & (self.course_entry_speed <= 0.60) & (self.course_speed_max <= 0.60), self.course_park_hold, torch.zeros_like(self.strict_hold))
        self.strict_success |= strict_new
        self.strict_success_count += strict_new.long().sum()
        self.course_success |= completed
        self.stair_goal_hold.copy_(self.course_hold + self.course_park_hold)

        # Snapshot BEFORE _reset_idx zeroes buffers inside env.step()!
        self.replay_success_now.copy_(completed)
        self.replay_top_support_count.copy_(upper.long().sum(1))
        self.replay_speed_limit_at_step.copy_(limit)
        self.replay_episode_max_speed_at_step.copy_(self.course_speed_max)
        self.replay_entry_speed_at_step.copy_(self.course_entry_speed)
        self.replay_park_hold_at_step.copy_(self.course_park_hold)
        self.replay_course_level_at_step.copy_(self.course_level)
        actual = getattr(getattr(self, 'dr_course', None), 'actual_full_dr', None)
        if actual is not None:
            self.replay_actual_DR_at_step.copy_(actual)

        # Incremental lift & progress rewards for Step 1 AND Step 2
        supported = (forces[:, :, 2] > SPEC.support_force).any(1)
        inter1 = active & near1 & supported & (~self.s1_committed)
        arm1 = inter1 & (~self.course_lift_armed)
        self.course_lift_reference[arm1] = self.reward.length[arm1]
        self.course_lift_armed |= arm1
        lift1 = ((z - SPEC.radius) / 0.20).clamp(0, 1)
        retract1 = ((self.course_lift_reference - self.reward.length) / 0.08).clamp(0, 1)
        score1 = lift1 * retract1
        lift_gain1 = (score1 - self.course_lift_best).clamp_min(0).mean(1) * inter1
        self.course_lift_best = torch.where(inter1[:, None], torch.maximum(self.course_lift_best, score1), self.course_lift_best)

        inter2 = active & near2 & supported & self.s1_committed & (~self.s2_committed)
        arm2 = inter2 & (~self.course_lift2_armed)
        self.course_lift2_reference[arm2] = self.reward.length[arm2]
        self.course_lift2_armed |= arm2
        lift2 = ((z - (0.20 + SPEC.radius)) / 0.20).clamp(0, 1)
        retract2 = ((self.course_lift2_reference - self.reward.length) / 0.08).clamp(0, 1)
        score2 = lift2 * retract2
        lift_gain2 = (score2 - self.course_lift2_best).clamp_min(0).mean(1) * inter2
        self.course_lift2_best = torch.where(inter2[:, None], torch.maximum(self.course_lift2_best, score2), self.course_lift2_best)
        lift_gain = lift_gain1 + 1.4 * lift_gain2

        max_prog = torch.where(is_two, self.command.new_full((self.num_envs,), 3.2), self.command.new_full((self.num_envs,), 1.5))
        progress = (self.stair_start - body_x).clamp_min(0.0)
        progress = torch.minimum(progress, max_prog)
        adv_step = (progress - self.course_progress).clamp(0, 0.02) * (active & supported & (vx_body > 0.02))
        self.course_progress = torch.where(active, torch.maximum(self.course_progress, progress), self.course_progress)

        # Step-1 full tread traversal & tall stand-up reward on 2-step course
        s1_full_new = is_two & s1_tread.all(1) & (body_x < SPEC.edge_2step_s1 - SPEC.body_margin) & (~self.s1_bonus_paid) & (~step_regressed) & active
        self.s1_bonus_paid |= s1_full_new
        s1_tread_walk = (
            is_two
            & s1_tread.all(1)
            & (~self.s2_committed)
            & (~step_regressed)
            & active
            & (vx_body >= 0.08)
            & (speed <= limit)
            & (wrap_to_pi(pitch).abs() < SPEC.maximum_angle)
            & (wrap_to_pi(roll).abs() < SPEC.maximum_angle)
        )
        # Bonus scales higher as robot stands back up tall (rel_height -> 0.38m+) on Step 1's tread!
        rel_h = self._height_observation()
        standup_frac = ((rel_h - 0.22) / 0.16).clamp(0.0, 1.0)
        s1_tread_dense = (0.18 + 0.22 * standup_frac) * s1_tread_walk.float() * (self.step_dt / 0.02)

        completion_scale = (self.command.new_tensor([16.0, 18.0, 21.0, 24.0, 27.0, 30.0])[self.speed_stage] + 12.0 * (self.course_speed_max <= 0.60).float()) * torch.where(is_two, 1.5, 1.0)
        self.replay_completion_bonus.copy_(completion_scale * completed.float() + latch_bonus)
        self.speed_completed += torch.bincount(self.speed_stage[completed], minlength=6)
        completed_group = self.reference_nominal_env_mask[completed].long()
        self.true_top_completion_events += torch.bincount(completed_group, minlength=2)
        idx = completed.nonzero().flatten()
        if idx.numel():
            self.offset_completion_events.view(-1).scatter_add_(0, self.reference_nominal_env_mask[idx].long() * 5 + self.actual_start_offset_index[idx], torch.ones_like(idx))

        real_forward = (self.previous_course_body_x - body_x) > 0.0001
        waiting = self.continuous_stair_mask & (self.command[:, 0] > 0.1) & (~self.bilateral_landing_seen) & (~real_forward)
        self.no_progress_seconds = torch.where(waiting, self.no_progress_seconds + self.step_dt, torch.zeros_like(self.no_progress_seconds))
        speed_penalty = 3.0 * (speed - limit).clamp_min(0).square() * active * (near | self.s1_committed) * self.step_dt
        self.previous_course_body_x.copy_(body_x)
        self.speed_penalty_sum += speed_penalty.sum()

        first_wheel_gain = torch.where(is_two[:, None], 0.15 * gained_s1.float() + 0.25 * gained.float(), 0.20 * gained.float()).sum(1) * real_forward.float()
        parts = torch.stack(
            (
                0.30 * lift_gain,
                0.25 * adv_step,
                first_wheel_gain + 2.5 * s1_full_new.float(),
                latch_bonus + completion_scale * completed.float() - speed_penalty - slide_off_clawback,
            ),
            1,
        )
        dense, top_parts = dense_top_support(
            upper,
            active & (~step_regressed),
            wrap_to_pi(pitch),
            wrap_to_pi(roll),
            self.course_pitch_peak,
            self.reward._stair_contact_raw,
            speed,
            limit,
            self.course_hold,
            self.step_dt,
            stop_latched=self.course_stop_latched,
            vx=vx_body,
            episode_speed_max=self.course_speed_max,
        )
        total_dense = dense + s1_tread_dense
        self.last_top_dense.copy_(total_dense)
        self.last_top_parts = top_parts
        self.top_dense_reward_sum += total_dense.sum()
        self.course_event_reward.copy_(parts.sum(1) + total_dense)
        self.course_reward_sums += parts.sum(0)
        self.stair_stage = torch.where(self.bilateral_landing_seen, 2, torch.where(self.s1_committed, 1, 0))

    def _get_dones(self):
        term, timeout = ScutUnifiedRoughV1Env._get_dones(self)
        if getattr(self, '_course_ready', False):
            self._update_course_events(term)
            # Anti-cheat: sliding off a committed step immediately terminates the episode as a failure!
            term |= self.step_regressed_now
            self.reset_terminated |= self.step_regressed_now
            timeout |= self.course_success & (~term)
        return term, timeout

    def _get_rewards(self):
        base = ScutUnifiedRoughV1Env._get_rewards(self)
        if not getattr(self, '_course_ready', False):
            return base
        d = self.view.data
        roll, pitch, yaw = euler_xyz_from_quat(self.robot.data.root_quat_w)
        target_yaw = torch.where(self.stair_side < 0, torch.zeros_like(yaw), torch.full_like(yaw, math.pi))
        yaw_error = wrap_to_pi(yaw - target_yaw)
        wheel_z = d.body_pos_w[:, self.stair_wheel_idx, 2] - self._center()[:, None, 2]
        # Suppress height_aux penalty while actively lifting wheels over Step 1 or Step 2
        lifting = ((wheel_z > SPEC.radius + 0.035) & (~self.s1_committed)[:, None]).any(1) | ((wheel_z > 0.20 + SPEC.radius + 0.035) & self.s1_committed[:, None] & (~self.s2_committed)[:, None]).any(1)
        current_height = self._height_observation()
        self.height_aux_ready |= (self.height - current_height).abs() < 0.03
        aux_active = self.height_aux_ready & (self.episode_length_buf * self.step_dt >= SPEC.settle_seconds)
        result, parts = fixed200_reward(
            base,
            self.course_event_reward,
            self.continuous_stair_mask,
            self.command[:, 0],
            d.root_lin_vel_b[:, 0],
            d.root_lin_vel_b[:, :2].norm(dim=-1),
            wrap_to_pi(pitch),
            yaw_error,
            self.height - current_height,
            lifting,
            self.bilateral_top_now,
            self.bilateral_landing_seen | self.s1_committed,
            self.no_progress_seconds,
            self.actions[:, 4:],
            self.speed_limits[self.speed_stage],
            self.step_dt,
            height_aux_active=aux_active,
        )
        self.course_quality_penalty_sum += parts['penalties'].sum(0)
        self.last_reward_breakdown = {k: v.detach().clone() for k, v in parts.items()}
        self.last_reward_breakdown['top_dense'] = self.last_top_dense.detach().clone()
        self.last_reward_breakdown.update({k: v.detach().clone() for k, v in self.last_top_parts.items()})
        self.last_reward_breakdown['command_vx'] = self.command[:, 0].detach().clone()
        self.last_reward_breakdown['actual_vx'] = d.root_lin_vel_b[:, 0].detach().clone()
        self.last_reward_breakdown['height_error'] = (self.height - current_height).detach().clone()
        self.last_reward_breakdown['yaw_error'] = yaw_error.detach().clone()
        self.last_reward_breakdown['actual_height'] = current_height.detach().clone()
        self.last_reward_breakdown['episode_age'] = self.episode_length_buf.detach().clone() * self.step_dt
        self.last_reward_breakdown['forward_position'] = (-(self.view.data.root_pos_w[:, 0] - self._center()[:, 0]) * self.stair_side).detach().clone()
        self.last_reward_breakdown['landing_seen'] = self.bilateral_landing_seen.detach().clone()
        return result

    def terrain_summary(self):
        out = ScutUnifiedRoughV1Env.terrain_summary(self)
        if not getattr(self, '_course_ready', False):
            return out
        mask = self.continuous_stair_mask
        out['closure_contract'] = dict(
            closure_2mm_diagnostic_only=not self.enforce_closure_reset,
            closure_2mm_reset_enabled=bool(self.enforce_closure_reset),
            catastrophic_closure_single_env_reset_m=1.0,
            single_peak_batch_stop=False,
            solver='TGS32/4',
        )
        out['course_groups'] = dict(
            continuous_stairs=int(mask.sum()),
            retained_rough=int(self.terrain.r1_retained_rough_mask.sum()),
            flat=int(self.flat_terrain_mask.sum()),
        )
        out['single_step_curriculum'] = dict(
            course=COURSE,
            heights_m=list(SPEC.heights),
            mastered_population=torch.bincount(self.course_mastered[mask], minlength=len(SPEC.heights)).tolist(),
            episode_population=torch.bincount(self.course_level[mask], minlength=len(SPEC.heights)).tolist(),
            attempts_DR_then_nominal=self.course_attempts.tolist(),
            successes_DR_then_nominal=self.course_successes.tolist(),
            step1_climb_events_DR_then_nominal=self.step1_climb_events.tolist(),
            step2_climb_events_DR_then_nominal=self.step2_climb_events.tolist(),
            step_regression_terminations=int(self.step_regression_terminations),
            promotions_DR_then_nominal=self.course_promotions.tolist(),
            demotions_DR_then_nominal=self.course_demotions.tolist(),
            entry_speed_rejections_DR_then_nominal=self.course_speed_rejections.tolist(),
            failure_causes=self.course_failure_causes.tolist(),
            failure_columns=['terminated_or_step_regressed', 'both_wheels_never_landed', 'landing_without_qualified_hold'],
            reward_sums=self.course_reward_sums.tolist(),
            reward_columns=['incremental_supported_lift', 'incremental_edge_progress', 'wheel_landing_and_s1_tread', 'qualified_completion_minus_regression'],
            review_fraction=SPEC.review_fraction,
            failures_before_demotion=SPEC.failures_to_demote,
            formal_evaluation_maximum_actual_entry_speed=SPEC.maximum_speed,
            training_maximum_actual_entry_speed=0.78,
            hold_s=SPEC.hold_seconds,
            per_env_reset_only=True,
            evaluation_only=self.course_evaluation,
            scope='stochastic training episode totals; anti-cheat slide-off termination enabled',
        )
        return out

    def terrain_checkpoint_state(self):
        state = ScutUnifiedRoughV1Env.terrain_checkpoint_state(self)
        state.update(
            course=COURSE,
            heights_m=SPEC.heights,
            training_speed_state={
                k: getattr(self, k).clone()
                for k in [
                    'speed_stage',
                    'speed_streak',
                    'speed_completed',
                    'strict_success_count',
                    'speed_penalty_sum',
                    'true_top_completion_events',
                    'top_latch_events',
                    'step1_climb_events',
                    'step2_climb_events',
                    'step_regression_terminations',
                    'offset_completion_events',
                    'offset_attempts',
                ]
            },
        )
        for name in (
            'course_mastered',
            'course_level',
            'course_success_streak',
            'course_attempts',
            'course_successes',
            'course_promotions',
            'course_demotions',
            'course_speed_rejections',
            'course_failure_causes',
            'course_reward_sums',
        ):
            state[name] = getattr(self, name).clone()
        return state

    def restore_terrain_curriculum(self, state):
        same = state.get('course') == COURSE
        if same:
            for name, value in state.get('training_speed_state', {}).items():
                if hasattr(self, name):
                    getattr(self, name).copy_(value.to(getattr(self, name)))
        self.course_accounting = False
        if same:
            assert tuple(state['heights_m']) == SPEC.heights
            for name in (
                'course_mastered',
                'course_level',
                'course_success_streak',
                'course_attempts',
                'course_successes',
                'course_promotions',
                'course_demotions',
                'course_speed_rejections',
                'course_failure_causes',
                'course_reward_sums',
            ):
                target = getattr(self, name)
                value = state[name].to(target)
                if value.shape != target.shape:
                    raise ValueError('Course resume shape differs: ' + name)
                target.copy_(value)
        self.parent_terrain_state = state
        self.snapshots = None
        self.reset()
        return dict(new_course=not same, course=COURSE, counters_restored=same, old_terrain_not_relabelled=True, fresh_physical_episodes=True)

    def begin_training_counts(self):
        self.course_accounting = True

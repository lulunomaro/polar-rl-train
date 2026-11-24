"""Native SCUT plant with shared-policy locomotion courses."""
import math
import numpy as np
import torch
import trimesh

import rough_scut_v1_terrain as terrain_source
from isaaclab.terrains import MeshPlaneTerrainCfg, TerrainImporter
from isaaclab.utils.configclass import configclass
from isaaclab.utils.math import quat_apply, quat_from_euler_xyz
from isaaclab.utils.warp import convert_to_warp_mesh
from mod4v3_ppo_v1.e0_env import e0_reward_configuration
from mod4v3_ppo_v1.scut_flat_env import tensor
from mod4v3_ppo_v1.scut_flat_mixed_dr_env import MixedRemainingDR
from mod4v3_ppo_v1.scut_flat_remaining_dr_env import RemainingDR
from mod4v3_ppo_v1.scut_flat_rewards import make_reward_class
from mod4v3_ppo_v1.scut_rough_scut_v1_env import ScutUnifiedRoughV1Env
from mod4v3_ppo_v1.stair_training_repair import install_native_done_repair, wheel_center_ground
from silky_geometry import (PHYSICS_DT, SUPPORT_FORCE_N, SUPPORT_STEPS, TRANSITION_SUPPORT_STEPS,
                            oblique_edge, rm27_profile)

COURSES = ('flat', 'rough_L9', 'curb_11', 'step_20', 'oblique_20',
           'rm27_west', 'rm27_east', 'rm27_west_400', 'rm27_east_400')
FAMILIES = (8, 9) + (0,) * (len(COURSES)-2)
COLS_PER_COURSE = 6
HISTORY_STEPS = 12
REWARD_TERMS = ('unload', 'momentum', 'repeated_retraction', 'lift_progress', 'forward_progress',
                'deck_support', 'deck_bounce', 'riser_stall', 'deck_continuous_support',
                'deck_contact_break', 'deck_leg_action_rate')
CLIMB_HOLD_TICKS = 140
FINAL_DECK_TICKS = 12
FIRST_TREAD_TICKS = 8
DECK_ABSORB_TICKS = 80
HIGH_DECK_STANCE = .38
DECK_BREAK_FORCE_N = 8.
DECK_STREAK_FORCE_N = 10.
DECK_LEG_ACTION_RATE_COEF = .06
FAST_FLAT_COMMAND_FRACTION = .30
FAST_FLAT_SPEED_RANGE = (1.8, 2.9)
OBSTACLE_SPEED_RANGE = (.60, 2.80)
HIGH_SPEED_COMMAND = 2.8
HIGH_SPEED_COMMAND_FRACTION = .10
STAIR_HEIGHTS = (.20, .28, .36, .42)
DR_LEVELS = (0., .25, .50, 1.)
SINGLE_DR_PASS_RATE = .28
DOUBLE_DR_PASS_RATE = .12


def edges(course, lateral, edge_sign):
    if course < 5:
        first = oblique_edge(lateral, edge_sign) if course == 4 else lateral * 0.
        return first, lateral * 0.0 + 3.5, lateral * 0.0 + 3.5
    # Local +x points into the course, +y points left. Center is the
    # nominal spawn frame of the published full-map collision fixture.
    floor, offset, lip = rm27_profile(course in (5, 7))
    first = (offset + .70 * lateral).clip(floor, lip-.31)
    return first, lateral * 0.0 + lip, lateral * 0.0 + lip + .15


def course_mesh(difficulty, cfg):
    width, length = cfg.size
    ys = np.linspace(-length / 2, length / 2, 91)
    first, lip, end = edges(cfg.course, ys, cfg.edge_sign)
    top = .11 if cfg.course == 2 else .20
    layers = [(first * 0 - width / 2, 0.), (first, 0.), (first, top)]
    if cfg.course >= 5:
        crest, deck = (.35, .30) if cfg.course < 7 else (.40, .36)
        layers += [(lip, top), (lip, crest), (end, crest), (end, deck), (end * 0 + width / 2, deck)]
    else:
        layers.append((first * 0 + width / 2, top))
    vertices = np.concatenate([np.column_stack((x+width/2, ys+length/2, np.full_like(ys, z)))
                               for x, z in layers])
    n = len(ys)
    faces = []
    for band in range(len(layers)-1):
        for row in range(n-1):
            a = band*n + row
            faces.extend(((a, a+n, a+1), (a+1, a+n, a+n+1)))
    return [trimesh.Trimesh(vertices=vertices, faces=faces, process=False)], np.array([width/2, length/2, 0.])


@configclass
class CourseCfg(MeshPlaneTerrainCfg):
    function = course_mesh
    course: int = 2
    edge_sign: int = 1


def install_course():
    original = terrain_source.generator

    def generator():
        cfg = original()
        rough = cfg.sub_terrains['random_uniform_for_rm']
        cfg.num_cols = len(COURSES) * COLS_PER_COURSE
        cfg.sub_terrains = dict(flat=MeshPlaneTerrainCfg(proportion=1.),
                                rough_L9=rough.replace(proportion=1.))
        for index, name in enumerate(COURSES[2:], start=2):
            if index == 4:
                cfg.sub_terrains[f'{name}_positive'] = CourseCfg(course=index, edge_sign=1, proportion=.5)
                cfg.sub_terrains[f'{name}_negative'] = CourseCfg(course=index, edge_sign=-1, proportion=.5)
            else:
                cfg.sub_terrains[name] = CourseCfg(course=index, proportion=1.)
        return cfg

    def install(_cfg):
        parent_import = TerrainImporter.import_mesh

        def remember(self, name, mesh):
            self.silky_mesh = mesh
            return parent_import(self, name, mesh)

        def origins(self, count, grid):
            device = self.device
            ids = torch.arange(count, device=device)
            group = (ids // 5) % len(COURSES)
            ordinal = ids // (5 * len(COURSES)) * 5 + ids % 5
            self.silky_group = group
            self.max_terrain_level = len(grid)
            self.terrain_types = group * COLS_PER_COURSE + ordinal % COLS_PER_COURSE
            self.terrain_levels = ordinal // COLS_PER_COURSE % len(grid)
            self.terrain_levels[group == 1] = 9
            self.r1_column_families = torch.tensor(FAMILIES, device=device).repeat_interleave(COLS_PER_COURSE)
            self.r1_nominal_mask = torch.zeros_like(group, dtype=torch.bool)
            self.r1_flat_mask = group == 0
            self.r1_pitch_rough_mask = group == 1
            self.r1_pitch_target_mask = group < 2
            self.r1_retained_rough_mask = group == 1
            self.r1_continuous_stair_mask = group >= 2
            self.r1_offsets = torch.zeros(count, 3, device=device)
            # All articulation replicas have the same collision filtering as the base task.
            self.r1_offsets[:, 1] = (ordinal // (COLS_PER_COURSE * len(grid)) % 6 - 2.5) * .38
            self.r1_offsets[group == 1, 0] = (ordinal[group == 1] // COLS_PER_COURSE % 10 - 4.5) * .48
            self.r1_wp_mesh = convert_to_warp_mesh(self.silky_mesh.vertices, self.silky_mesh.faces, device)
            result = grid[self.terrain_levels, self.terrain_types] + self.r1_offsets
            return result

        TerrainImporter.import_mesh = remember
        TerrainImporter._compute_env_origins_curriculum = origins

    terrain_source.generator = generator
    terrain_source.install_origins = install


class CourseDR(MixedRemainingDR):
    def __init__(self, env):
        # RemainingDR initializes every replica with the full randomization.
        RemainingDR.__init__(self, env)
        self.nominal_env_mask = env.scene['terrain'].r1_nominal_mask
        self.applied_dr = ~self.nominal_env_mask
        names = ('body_mass_scale', 'total_mass_scale', 'startup_com_delta',
                 'startup_materials', 'startup_joint_friction')
        self.sampled = {name: getattr(self, name).clone() for name in names}

    def apply_curriculum(self, ids, active):
        self.nominal_env_mask[ids] = ~active
        self.applied_dr[ids] = active
        self.gain_count[ids[active]] = 0
        self.body_mass_scale[ids] = torch.where(active[:, None], self.sampled['body_mass_scale'][ids], 1.)
        self.total_mass_scale[ids] = torch.where(active, self.sampled['total_mass_scale'][ids], 1.)
        self.startup_com_delta[ids] = self.sampled['startup_com_delta'][ids] * active[:, None]
        cpu = ids.cpu()
        self.startup_materials[cpu] = torch.where(active.cpu()[:, None, None],
                                                   self.sampled['startup_materials'][cpu], self.materials[cpu])
        default = torch.stack((self.static_friction_default[ids],
                               (self.dynamic_friction_default if self.dynamic_friction_default is not None
                                else self.static_friction_default)[ids],
                               (self.viscous_friction_default[ids] if self.viscous_friction_default is not None
                                else torch.zeros_like(self.static_friction_default[ids]))), -1)
        fr = torch.where(active[:, None, None], self.sampled['startup_joint_friction'][ids], default)
        self.startup_joint_friction[ids] = fr
        self.robot.write_joint_friction_coefficient_to_sim(
            joint_friction_coeff=fr[..., 0], joint_dynamic_friction_coeff=fr[..., 1],
            joint_viscous_friction_coeff=fr[..., 2], joint_ids=self.joint_ids, env_ids=ids)
        self._write_body_mass_inertia(ids)
        self._write_startup_materials(ids)


class SilkyLocoEnv(ScutUnifiedRoughV1Env):
    body_mass_dr_class = CourseDR
    enforce_closure_reset = False
    air_reset_fraction = 0.
    leg_pd_decimation = 4
    wheel_pd_decimation = 1

    def __init__(self, cfg, meta, bank, tire_geometry, landing_pool=None, standing_pose=None, initial_dr=0.):
        self.silky_ready = False
        super().__init__(cfg, meta, bank)
        self.group = self.terrain.silky_group
        self.obstacle = self.group >= 2
        self.double = self.group >= 5
        west = (self.group == 5) | (self.group == 7)
        self.edge_min, self.edge_offset, self.second_edge = (
            torch.where(west, west_value, east_value)[:, None]
            for west_value, east_value in zip(rm27_profile(True), rm27_profile(False), strict=True))
        self.edge_sign = torch.where(self.terrain.terrain_types % COLS_PER_COURSE < COLS_PER_COURSE//2, 1., -1.)
        self.crest_top = torch.where(self.group >= 7, .40, .35)[:, None]
        self.deck_top = torch.where(self.group >= 7, .36, .30)[:, None]
        self.first_top = torch.where(self.group == 2, .11, .20)[:, None]
        self.centers = self.terrain.terrain_origins[self.terrain.terrain_levels, self.terrain.terrain_types]
        names = self.scene['contacts'].body_names
        self.contact_ids = [[names.index(f'{side}_wheel_link')] +
                            [index for index, name in enumerate(names) if name.startswith(side) and 'guide_link' in name]
                            for side in ('left', 'right')]
        self.wheel_body_ids = self.reward._wheel_link_idx
        wheel_names = meta['spec']['frames']['wheel_order']
        self.tire_radius = torch.tensor([tire_geometry[name]['radius_m'] for name in wheel_names],
                                       device=self.device)
        self.tire_half_width = self.tire_radius.new_tensor([tire_geometry[name]['half_width_m']
                                                           for name in wheel_names])
        self.tire_axis = self.tire_radius.new_tensor([tire_geometry[name]['axle_local'] for name in wheel_names])
        self.history = torch.zeros(self.num_envs, HISTORY_STEPS, 35, device=self.device)
        self.history_pending = torch.ones(self.num_envs, dtype=torch.bool, device=self.device)
        self.history_tick = -1
        self.command_after_settle = self.command.clone()
        self.course_height = self.height.clone()
        self.max_progress_x = self.height.new_zeros(self.num_envs)
        self.issue_forward = self.max_progress_x.clone()
        self.runup_steps = 25
        self.target_dr = initial_dr
        self.dr_stage = DR_LEVELS.index(initial_dr)
        self.dr_history = []
        self.dr_eligible = torch.rand(self.num_envs, device=self.device, generator=self.reset_generator)
        self.dr_eligible = self.dr_eligible.argsort().argsort() / self.num_envs
        self.support_ticks = torch.zeros(self.num_envs, 2, dtype=torch.long, device=self.device)
        self.support_required = torch.full_like(self.support_ticks, SUPPORT_STEPS)
        self.support_required[self.double, 0] = TRANSITION_SUPPORT_STEPS
        self.deck_streak_ticks = torch.zeros_like(self.support_ticks)
        self.support_peak = self.support_ticks.clone()
        self.sample_count = 0
        self.support_measured = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self.flat_stand_measured = self.support_measured.clone()
        self.flat_drive_measured = self.support_measured.clone()
        self.flat_stand_ticks = torch.zeros_like(self.support_ticks[:, 0])
        self.flat_drive_ticks = self.flat_stand_ticks.clone()
        self.flat_load_samples = torch.zeros((), dtype=torch.long, device=self.device)
        self.flat_radial_error_sum = self.tire_radius.new_zeros(2)
        self.flat_normal_force_sum = self.flat_radial_error_sum.clone()
        self.flat_center_z_sum = self.flat_radial_error_sum.clone()
        self.stage = torch.zeros_like(self.support_ticks[:, 0])
        self.stage_crossed = torch.zeros(self.num_envs, 2, dtype=torch.bool, device=self.device)
        self.climb_hold_ticks = torch.zeros_like(self.stage)
        self.final_deck_ticks = torch.zeros_like(self.stage)
        self.first_tread_ticks = torch.zeros_like(self.stage)
        self.riser_climb = torch.zeros_like(self.obstacle)
        self.deck_absorb = torch.zeros_like(self.obstacle)
        self.deck_absorb_ticks = torch.zeros_like(self.stage)
        self.riser_stall_ticks = torch.zeros_like(self.stage)
        self.lip_seen = self.stage_crossed.clone()
        self.stage_retractions = torch.zeros_like(self.support_ticks)
        self.leg_retracting = torch.zeros_like(self.stage_crossed)
        self.leg_len_ema = torch.zeros(self.num_envs, 2, device=self.device)
        self.leg_ext_extreme = torch.zeros(self.num_envs, 2, device=self.device)
        self.max_feet_z = torch.zeros(self.num_envs, 2, device=self.device)
        self.smooth_reward = self.max_progress_x.clone()
        self.deck_action_step = torch.zeros_like(self.obstacle)
        self.leg_action_rate = torch.zeros_like(self.smooth_reward)
        self.rewards_total = torch.zeros(len(COURSES), len(REWARD_TERMS), device=self.device)
        self.reward_window = torch.zeros(self.num_envs, len(REWARD_TERMS), device=self.device)
        self.completed = torch.zeros(len(COURSES), dtype=torch.long, device=self.device)
        self.completed_by_replica = torch.zeros_like(self.stage)
        self.episode_counts = torch.zeros(2, len(COURSES), 2, dtype=torch.long, device=self.device)
        self.dr_window = torch.zeros_like(self.episode_counts)
        self.dr_consistent = self.support_measured.clone()
        self.landing_bank = self._load_landing_pool(landing_pool)
        self.landing_resets = torch.zeros((), device=self.device, dtype=torch.long)
        self.standing_pose = standing_pose
        self.stair_heights = self.height.new_tensor(STAIR_HEIGHTS)
        if standing_pose is not None:
            self.standing_q = self.height.new_tensor([standing_pose['joint_position'][name]
                                                      for name in self.robot.joint_names])
        self.silky_ready = True

    def _load_landing_pool(self, source):
        if source is None:
            return None
        if source['format'] != 'mod4v3_jump_landing_v1' or not source['landings']:
            raise ValueError('Expected a recorded jump landing pool')
        rows = source['landings']
        indices = [source['joint_names'].index(name) for name in self.robot.joint_names]
        state = {name: torch.tensor([row[name] for row in rows], device=self.device)
                 for name in ('root_state', 'joint_position', 'joint_velocity', 'height_cmd', 'speed_cmd')}
        if state['root_state'].shape != (len(rows), 13) or not all(torch.isfinite(v).all() for v in state.values()):
            raise ValueError('Invalid landing states')
        state['joint_position'] = state['joint_position'][:, indices]
        state['joint_velocity'] = state['joint_velocity'][:, indices]
        return state

    def _reset_jump_landings(self, ids):
        if self.landing_bank is None:
            return
        gen = self.reset_generator
        picked = ids[(self.group[ids] == 0) & (torch.rand(len(ids), device=self.device, generator=gen) < .20)]
        if not picked.numel():
            return
        bank = self.landing_bank
        sample = torch.randint(len(bank['root_state']), (len(picked),), device=self.device, generator=gen)
        root = bank['root_state'][sample].clone()
        root[:, :3] += self.scene.env_origins[picked]
        root[:, 2] += .003
        self.robot.write_root_link_state_to_sim(root, env_ids=picked)
        self.robot.write_joint_state_to_sim(bank['joint_position'][sample], bank['joint_velocity'][sample], env_ids=picked)
        self.zero_torque_remaining[picked] = 0
        self._ground_command_until[picked] = 0
        self._execution_pending[picked] = True
        self._sensor_pending[picked] = True
        self.command[picked] = 0.
        self.command[picked, 0] = bank['speed_cmd'][sample]
        self.height[picked] = bank['height_cmd'][sample]
        self.heading_env[picked] = False
        self.standing_env[picked] = bank['speed_cmd'][sample] == 0.
        self.command_timer[picked] = 1.5
        self.reward.command[picked] = self.command[picked]
        self.reward.height_cmd[picked] = self.height[picked]
        self.reward._invalidate_step_caches()
        self.landing_resets += len(picked)

    def _make_reward(self, meta):
        parent = make_reward_class(meta, cfg_factory=e0_reward_configuration)

        class CourseReward(parent):
            def _postprocess_reward_terms(reward, terms):
                terms = super()._postprocess_reward_terms(terms)
                if self.silky_ready:
                    scale = torch.where(self.riser_climb, .05, 1.)
                    for name in ('track_height_exp_tight', 'track_height_square', 'flat_orientation_y_v',
                                 'flat_orientation_y_exp', 'leg_joint_vel', 'lin_vel_z'):
                        if name in terms:
                            terms[name] = terms[name] * scale
                    for name in tuple(terms):
                        if name.startswith('airborne_'):
                            terms[name] = torch.where(self.obstacle, torch.zeros_like(terms[name]), terms[name])
                    if 'undesired_contact' in terms:
                        structural = [i for i in reward._undesired_contact_link_idx if i not in reward._guide_link_idx]
                        if structural:
                            struct_hit = (reward.contact_sensor.data.net_forces_w[:, structural].norm(dim=-1) > 1.).any(-1).float()
                        else:
                            struct_hit = torch.zeros_like(terms['undesired_contact'])
                        terms['undesired_contact'] = torch.where(self.group >= 1, struct_hit, terms['undesired_contact'])
                return terms

        inst = CourseReward(self.view, self.num_envs, self.device)
        install_native_done_repair(inst)
        return inst

    def prepare_endpoint(self):
        super().prepare_endpoint()
        if not self.silky_ready:
            return
        r = self.reward
        obs_ids = self.obstacle.nonzero().flatten()
        if obs_ids.numel() and getattr(r.cfg, 'enable_state_machines', False):
            r.state_machine_manager.on_reset(r, obs_ids)
            r.height_reward_airborne_state[obs_ids] = False
            r.airborne_current_duration[obs_ids] = 0.
        wheels = self.view.data.body_pos_w[:, r._wheel_link_idx]
        grounds = []
        for side, name in enumerate(('ground_left', 'ground_right')):
            hits = tensor(self.scene[name].data.ray_hits_w)
            grounds.append(wheel_center_ground(hits, wheels[:, side, :2], r.ground_wheels[:, side]))
        wheel_ground = torch.stack(grounds, dim=1)
        support_ground = wheel_ground.amin(1)
        r.ground_z_est = torch.where(self.obstacle, support_ground, r.ground_z_est)
        r.ground_wheels = torch.where(self.obstacle[:, None], wheel_ground, r.ground_wheels)
        r._invalidate_step_caches()
        r._stair_course_mask = self.group >= 1
        r._stair_guide_allowed = self.group >= 1

    def _get_dones(self):
        terminated, timeout = super()._get_dones()
        if self.silky_ready:
            self.record_finished(terminated, timeout)
        return terminated, timeout

    def record_finished(self, term, timeout):
        attempted = self.obstacle & (self.episode_length_buf > self.runup_steps) & (term | timeout)
        solved = self.stage_crossed[:, 1] | (self.stage_crossed[:, 0] & ~self.double)
        counts = torch.stack((attempted, attempted & solved & ~term), 1).long()
        bucket = self.group + len(COURSES)*self.full_dr.applied_dr.long()
        self.episode_counts.view(-1, 2).index_add_(0, bucket, counts)
        counts = counts * self.dr_consistent[:, None]
        self.dr_window.view(-1, 2).index_add_(0, bucket, counts)

    def promote_dr(self, elapsed):
        if self.dr_stage == len(DR_LEVELS)-1:
            return
        sample = self.dr_window[0 if self.dr_stage == 0 else 1]
        single, double = sample[2:5].sum(0), sample[5:].sum(0)
        solo, paired = single.tolist(), double.tolist()
        if (solo[0] >= 96 and solo[1] >= SINGLE_DR_PASS_RATE*solo[0]
                and paired[0] >= 96 and paired[1] >= DOUBLE_DR_PASS_RATE*paired[0]):
            self.dr_stage += 1
            self.target_dr = DR_LEVELS[self.dr_stage]
            self.dr_history.append(dict(seconds=elapsed, target=self.target_dr, single=solo, double=paired))
            self.dr_window.zero_()
            self.dr_consistent.zero_()

    def _reset_idx(self, ids):
        if not self.silky_ready:
            return super()._reset_idx(ids)
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        if not ids.numel():
            return
        desired = self.dr_eligible[ids] < self.target_dr
        changed = (desired != self.full_dr.applied_dr[ids]).nonzero().flatten()
        if changed.numel():
            self.full_dr.apply_curriculum(ids[changed], desired[changed])
        ground = self.group[ids] < 2
        picked = ids[~ground]
        n = len(picked)
        random = torch.rand(n, 6, device=self.device, generator=self.reset_generator)
        offsets = self.terrain.r1_offsets
        offsets[picked, 0] = torch.where(self.group[picked] < 5, -1.25, -.35) + .30 * random[:, 0]
        offsets[picked, 1] = torch.where(self.group[picked] < 5, 1.50, .24) * (random[:, 1] - .5)
        nominal_stance = (random[:, 2] > .85) & (self.standing_pose is not None)
        # Replay stances begin well before the riser at a measured standing pose.
        offsets[picked, 0] = torch.where(nominal_stance & (self.group[picked] < 5), -1.20+.10*random[:, 0], offsets[picked, 0])
        offsets[picked, 1] = torch.where(nominal_stance & (self.group[picked] < 5), .30*(random[:, 1]-.5), offsets[picked, 1])
        super()._reset_idx(ids)
        r_obj = getattr(self, 'reward', None)
        if r_obj is not None:
            for cause in ('contact', 'orientation', 'other'):
                for suffix in ('_counter', '_raw_buf'):
                    val = getattr(r_obj, '_stair_' + cause + suffix, None)
                    if val is not None:
                        val[ids] = 0
            r_obj._stair_course_mask = self.group >= 1
            r_obj._stair_guide_allowed = self.group >= 1
        self._reset_jump_landings(ids)
        self.history_pending[ids] = True
        self.support_ticks[ids] = 0
        self.deck_streak_ticks[ids] = 0
        self.flat_stand_ticks[ids] = 0
        self.flat_drive_ticks[ids] = 0
        self.stage[ids] = 0
        self.stage_crossed[ids] = False
        self.climb_hold_ticks[ids] = 0
        self.final_deck_ticks[ids] = 0
        self.first_tread_ticks[ids] = 0
        self.riser_climb[ids] = False
        self.deck_absorb[ids] = False
        self.deck_absorb_ticks[ids] = 0
        self.riser_stall_ticks[ids] = 0
        self.lip_seen[ids] = False
        self.stage_retractions[ids] = 0
        self.leg_retracting[ids] = False
        self.leg_len_ema[ids] = 0.
        self.leg_ext_extreme[ids] = 0.
        self.max_feet_z[ids] = 0.
        self.dr_consistent[ids] = True
        if not n:
            return
        height_sample = random[:, 5]
        discrete_height = self.stair_heights[(height_sample * len(STAIR_HEIGHTS)).long()]
        continuous_height = STAIR_HEIGHTS[0] + (STAIR_HEIGHTS[-1]-STAIR_HEIGHTS[0])*height_sample
        requested = torch.where(random[:, 2] < .425, discrete_height, continuous_height)
        # Start from an existing feasible standing pose and settle under the policy.
        pick = (self._bank_h[None, :] - requested[:, None]).abs().argmin(1)
        qpos = self._bank_q[pick][:, self._bank_ids].clone()
        root = tensor(self.robot.data.default_root_state)[picked].clone()
        root[:, :3] = self.scene.env_origins[picked]
        pose_height = self._bank_h[pick]
        yaw = (random[:, 3]-.5) * torch.where(self.group[picked] == 4, 2*math.radians(25), .10)
        low, high = OBSTACLE_SPEED_RANGE
        speed_draw = random[:, 4] / (1. - HIGH_SPEED_COMMAND_FRACTION)
        command_speed = torch.where(speed_draw < 1., low + (high-low)*speed_draw, HIGH_SPEED_COMMAND)
        if self.standing_pose is not None:
            qpos[nominal_stance] = self.standing_q
            pose_height = torch.where(nominal_stance, self.standing_pose['height_m'], pose_height)
            requested = torch.where(nominal_stance, self.standing_pose['command_height_m'], requested)
        root[:, 2] += pose_height + .003
        root[:, 3:7] = quat_from_euler_xyz(torch.zeros_like(yaw), torch.zeros_like(yaw), yaw)
        root[:, 7:] = 0.
        self.robot.write_root_state_to_sim(root, env_ids=picked)
        self.robot.write_joint_state_to_sim(qpos, torch.zeros_like(qpos), env_ids=picked)
        self.max_progress_x[picked] = root[:, 0] - self.centers[picked, 0]
        self._ground_command_until[picked] = 0
        self._execution_pending[picked] = True
        self._sensor_pending[picked] = True
        self.command_after_settle[picked] = 0.
        self.command_after_settle[picked, 0] = command_speed
        self.course_height[picked] = requested
        self._commands()

    def _sample_command(self, ids):
        super()._sample_command(ids)
        if not self.silky_ready:
            return
        ground = ids[self.group[ids] < 2]
        gen = self.reset_generator
        picked = ground[torch.rand(len(ground), device=self.device, generator=gen) < FAST_FLAT_COMMAND_FRACTION]
        speeds = torch.empty(len(picked), device=self.device).uniform_(*FAST_FLAT_SPEED_RANGE, generator=gen)
        exact_high = torch.rand(len(picked), device=self.device, generator=gen) < HIGH_SPEED_COMMAND_FRACTION
        self.command[picked, 0] = torch.where(exact_high, HIGH_SPEED_COMMAND, speeds)
        self.command[picked, 1:] = 0.
        self.heading_env[picked] = False
        self.standing_env[picked] = False

    def _commands(self):
        if not self.silky_ready:
            return
        ids = self.obstacle
        moving = self.episode_length_buf[ids] >= self.runup_steps
        self.command[ids] = self.command_after_settle[ids] * moving[:, None]
        self.height[ids] = self.course_height[ids]
        self.command_timer[ids] = 1.e9
        self.heading_env[ids] = False
        self.standing_env[ids] = ~moving
        self.reward.command[ids] = self.command[ids]
        self.reward.height_cmd[ids] = self.height[ids]
        self.reward._invalidate_step_caches()

    def _get_observations(self):
        self._commands()
        obs = super()._get_observations()
        if self.silky_ready:
            frame = obs['policy']
            tick = self._sim_step_counter
            if tick != self.history_tick:
                self.history[:, :-1] = self.history[:, 1:].clone()
                self.history[:, -1] = frame
                self.history_tick = tick
            pending = self.history_pending
            self.history[pending] = frame[pending, None]
            pending.zero_()
            obs['policy'] = torch.cat((frame, self.history.flatten(1)), -1)
        return obs

    def _pre_physics_step(self, actions):
        if not self.silky_ready:
            return super()._pre_physics_step(actions)
        self._commands()
        self.issue_forward.copy_(self.command[:, 0])
        self.smooth_reward.zero_()
        self.reward_window.zero_()
        self.deck_action_step.zero_()
        previous_legs = self.actions[:, :4].clone()
        super()._pre_physics_step(actions)
        self.leg_action_rate.copy_((self.actions[:, :4] - previous_legs).square().sum(1))

    def sample_physics(self, dt):
        """Run after scene.update at each completed integration step."""
        self.sample_count += 1
        data = self.view.data
        wheels = data.body_pos_w[:, self.wheel_body_ids] - self.centers[:, None]
        force = tensor(self.scene['contacts'].data.net_forces_w)
        main = force[:, [ids[0] for ids in self.contact_ids]]
        active = self.obstacle & (self.issue_forward >= .55)
        ordinary = oblique_edge(wheels[..., 1], self.edge_sign[:, None]) * (self.group == 4)[:, None]
        double_front = (self.edge_offset+.70*wheels[..., 1]).maximum(self.edge_min).minimum(self.second_edge-.31)
        first = torch.where(self.double[:, None], double_front, ordinary)
        second = self.second_edge
        lip_end = second+.15
        double = self.double
        next_edge = torch.where((self.stage > 0)[:, None], second, first)
        first_top = self.first_top
        face_height = torch.where((self.stage > 0)[:, None], self.crest_top, first_top)
        dx = wheels[..., 0] - next_edge
        dx_min, dx_max = dx.amin(1), dx.amax(1)
        final_crossed = torch.where(double, self.stage_crossed[:, 1], self.stage_crossed[:, 0])
        in_zone = active & (dx_min < .38) & (dx_max > -.38) & ~final_crossed
        # A load directed horizontally against travel, near a riser and below
        # its top, with wheel or guide contact from the same side.
        riser_load = torch.stack([((-force[:, ids, 0]) > (force[:, ids, 2].abs() + 4.)).any(1)
                                  for ids in self.contact_ids], 1)
        impact = riser_load & (dx.abs() < .28) & (wheels[..., 2] < face_height) & in_zone[:, None]
        torque = self.applied_motor_torque[:, 4:].abs()
        unload = ((torque - 1.0).clamp_min(0.).square() * impact).sum(1)
        com_velocity = data.root_com_lin_vel_w if hasattr(data, 'root_com_lin_vel_w') else data.root_lin_vel_w
        vx = com_velocity[:, 0]
        course_end = torch.where(double, lip_end[:, 0], 0.) + .60
        current = data.root_pos_w[:, 0] - self.centers[:, 0]
        next_peak = self.max_progress_x.maximum(current.minimum(course_end))
        past_first = current > (first.mean(1) - .05)
        prog_gain = torch.where(past_first, 10., 2.5)
        progress_reward = prog_gain * (next_peak - self.max_progress_x) * active
        self.max_progress_x.copy_(next_peak)
        travel = active & (self.max_progress_x < course_end)
        runup_momentum = (vx/.20).clamp(0., 1.) - (.10-vx).clamp(0., .10)*3.
        climb_momentum = 2.*((vx-.18)/(.40-.18)).clamp(0., 1.) - ((.18-vx)/.18).clamp(0., 1.)
        momentum = (torch.where(in_zone, climb_momentum, runup_momentum)
                    - (-vx).clamp(0., .30)*3.) * travel
        self.riser_stall_ticks.copy_(torch.where(in_zone & (vx < .12), self.riser_stall_ticks + 1, 0))
        stall_penalty = -3. * ((.12-vx)/.12).clamp(0., 1.5) * dt * (self.riser_stall_ticks > round(.15/dt))
        leg = data.body_pos_w[:, self.wheel_body_ids] - data.root_pos_w[:, None]
        leg_len = leg.norm(dim=-1).clamp_min(.05)
        alpha = min(1., dt / .015)
        ema_init = (self.leg_len_ema == 0.) | (~in_zone[:, None])
        self.leg_len_ema.copy_(torch.where(ema_init, leg_len, self.leg_len_ema + alpha * (leg_len - self.leg_len_ema)))
        length = self.leg_len_ema
        extreme = torch.where(self.leg_retracting, self.leg_ext_extreme.minimum(length),
                              self.leg_ext_extreme.maximum(length))
        retracted = ~ema_init & ~self.leg_retracting & (extreme-length >= .014)
        recovered = self.leg_retracting & (length-extreme >= .008)
        self.stage_retractions += retracted
        repeated_retractions = (retracted & (self.stage_retractions >= 2)).sum(1)
        self.leg_retracting.copy_(~ema_init & ((self.leg_retracting & ~recovered) | retracted))
        self.leg_ext_extreme.copy_(torch.where(ema_init | retracted | recovered, length, extreme))
        axis_z = quat_apply(data.body_quat_w[:, self.wheel_body_ids], self.tire_axis.expand_as(wheels))[..., 2].abs()
        extent = self.tire_radius * (1.-axis_z.square()).clamp_min(0.).sqrt() + self.tire_half_width * axis_z
        feet = wheels[..., 2] - extent
        near_edge = (dx_max > -.12) & (dx_min < .36)
        climb_motion = ((feet[:, 0]-feet[:, 1]).abs() > .025) | (data.projected_gravity_b[:, 0].abs() > .10)
        current_floor = torch.where(self.stage[:, None] >= 1, first_top, 0.)
        climb_motion |= (feet - current_floor).amax(1) > .025
        climb_event = active & ~final_crossed & (riser_load.any(1) | (near_edge & climb_motion))
        self.climb_hold_ticks.copy_(torch.where(climb_event, CLIMB_HOLD_TICKS,
                                                (self.climb_hold_ticks - 1).clamp_min(0)))
        near_face = active[:, None] & (dx > -.28)
        target_cap = torch.where(double[:, None], self.crest_top + .02, first_top + .02)
        next_feet_z = torch.where(near_face, self.max_feet_z.maximum(feet.clamp(0., 1.).minimum(target_cap)), self.max_feet_z)
        lift_potential = 18. * (next_feet_z - self.max_feet_z).mean(1)
        self.max_feet_z.copy_(next_feet_z)
        load = main[..., 2] >= SUPPORT_FORCE_N
        on_tread = (wheels[..., 0] >= first) & ((feet - first_top).abs() < .032)
        on_tread &= (~double[:, None]) | (wheels[..., 0] < second)
        on_upper = double[:, None] & (wheels[..., 0] >= second) & (
            (feet - torch.where(wheels[..., 0] < lip_end, self.crest_top, self.deck_top)).abs() < .035)
        on_step = on_tread | on_upper
        self.deck_action_step |= self.obstacle & on_step.any(1)
        support1, support2 = load & on_tread, load & on_upper
        both_on_first, both_on_upper = support1.all(1), support2.all(1)
        final_footprint = torch.where(double, (wheels[..., 0] > lip_end - .02).all(1),
                                      (wheels[..., 0] >= first).all(1))
        final_on_deck = final_footprint & torch.where(double, on_upper.all(1), on_tread.all(1))
        first_footprint = double & (wheels[..., 0] >= first).all(1) & (wheels[..., 0].amax(1) < second[:, 0] - .22)
        self.final_deck_ticks.copy_(torch.where(active & final_on_deck, self.final_deck_ticks + 1, 0))
        self.first_tread_ticks.copy_(torch.where(active & first_footprint & on_tread.all(1), self.first_tread_ticks + 1, 0))
        settled_final = self.final_deck_ticks >= FINAL_DECK_TICKS
        between_faces = self.first_tread_ticks >= FIRST_TREAD_TICKS
        start_absorb = (self.final_deck_ticks == FINAL_DECK_TICKS) | (self.first_tread_ticks == FIRST_TREAD_TICKS)
        deck_footprint = active & (final_footprint | first_footprint)
        absorb_ticks = torch.where(start_absorb, DECK_ABSORB_TICKS, (self.deck_absorb_ticks - 1).clamp_min(0))
        self.deck_absorb_ticks.copy_(absorb_ticks * deck_footprint)
        # At high stance a brief bounce should neither switch the expert nor evade the force cost.
        high_final_deck = final_footprint & (self.course_height >= HIGH_DECK_STANCE) & (settled_final | self.deck_absorb)
        self.deck_absorb.copy_(deck_footprint & ((self.deck_absorb_ticks > 0) | high_final_deck))
        self.climb_hold_ticks.masked_fill_(settled_final | between_faces | self.deck_absorb, 0)
        self.riser_climb.copy_(active & (self.climb_hold_ticks > 0))
        compact_support = (both_on_first | both_on_upper) & (main[..., 2] >= 12.).all(1) & active
        deck_reward = 3.5 * dt * compact_support
        normal = main[..., 2].amin(1)
        deck_geometry = torch.stack((on_tread.all(1), on_upper.all(1)), 1) & active[:, None]
        streak_loaded = deck_geometry & (normal[:, None] >= DECK_STREAK_FORCE_N)
        self.deck_streak_ticks.copy_(torch.where(streak_loaded, self.deck_streak_ticks + 1, 0))
        continuous_reward = 6. * dt * (self.deck_streak_ticks / self.support_required).clamp_max(1.).sum(1)
        on_deck = deck_geometry.any(1) | self.deck_absorb
        contact_break = -2.5 * dt * (on_deck & (normal < DECK_BREAK_FORCE_N))
        wheel_vz = data.body_link_lin_vel_w[:, self.wheel_body_ids, 2]
        deck_bounce = -.75 * dt * (wheel_vz.square().clamp_max(4.) * on_step).mean(1) * active
        self.lip_seen |= support2 & (wheels[..., 0] < lip_end) & double[:, None] & active[:, None]
        ground = ~self.obstacle & load.all(1)
        flat_loaded = ground & (self.group == 0)
        ground_stand = flat_loaded & (self.issue_forward.abs() < .05) & (self.command[:, 2].abs() < .05)
        ground_drive = flat_loaded & (self.issue_forward.abs() >= .55)
        self.flat_stand_ticks.copy_(torch.where(ground_stand, self.flat_stand_ticks + 1, 0))
        self.flat_drive_ticks.copy_(torch.where(ground_drive, self.flat_drive_ticks + 1, 0))
        self.flat_load_samples += flat_loaded.sum()
        self.flat_center_z_sum += (wheels[..., 2] * flat_loaded[:, None]).sum(0)
        self.flat_radial_error_sum += (feet.abs() * flat_loaded[:, None]).sum(0)
        self.flat_normal_force_sum += (main[..., 2] * flat_loaded[:, None]).sum(0)
        first_good = (both_on_first & active) | ground
        second_good = both_on_upper & active & self.stage_crossed[:, 0]
        good = torch.stack((first_good, second_good), 1)
        self.support_ticks.copy_(torch.where(good, self.support_ticks + 1, 0))
        self.support_peak.copy_(self.support_peak.maximum(self.support_ticks))
        self.support_measured |= (self.support_ticks[:, 0] >= SUPPORT_STEPS) & ~self.obstacle
        new = (self.support_ticks >= self.support_required) & ~self.stage_crossed & active[:, None]
        self.stage_crossed |= new
        self.stage.copy_(self.stage_crossed.sum(1))
        advanced = new.any(1)[:, None]
        self.stage_retractions.masked_fill_(advanced, 0)
        self.leg_retracting.masked_fill_(advanced, False)
        self.leg_len_ema.masked_fill_(advanced, 0.)
        reached = new[:, 1] | (new[:, 0] & ~double)
        self.completed.scatter_add_(0, self.group, reached.long())
        self.completed_by_replica += reached
        lift_progress = ((feet - (face_height-.20)).clamp(0., .22) * (dx > -.24)).mean(1) * in_zone
        terms = torch.stack((-.12*unload*dt, momentum*dt, -1.2*repeated_retractions,
                             8.0*lift_progress*dt + lift_potential, progress_reward,
                             deck_reward, deck_bounce, stall_penalty, continuous_reward, contact_break), 1)
        self.reward_window[:, :terms.shape[1]] += terms
        self.smooth_reward += terms.sum(1) + 8.*new.sum(1)

    def _get_rewards(self):
        base = super()._get_rewards()
        if not self.silky_ready:
            return base
        leg_smooth = -DECK_LEG_ACTION_RATE_COEF * self.leg_action_rate * self.deck_action_step
        self.reward_window[:, -1] = leg_smooth
        self.smooth_reward += leg_smooth
        self.rewards_total.index_add_(0, self.group, self.reward_window)
        return base + self.smooth_reward

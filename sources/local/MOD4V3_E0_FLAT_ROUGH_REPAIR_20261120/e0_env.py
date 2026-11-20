"""E0-only command/reward adaptation on the existing SCUT flat and rough-v1 plant."""
import torch

import rough_scut_v1_terrain as terrain_source
from isaaclab.terrains import TerrainImporter
from isaaclab.utils.warp import raycast_mesh
from .pitch_brake_math import heading_velocity, horizontal_reward_terms
from .pitch_stability_math import body_pitch, stability_active_mask, stability_components
from .scut_flat_env import tensor
from .scut_flat_rewards import make_reward_class
from .scut_rough_scut_v1_env import ScutUnifiedRoughV1Env, configuration_scut_v1


def install_e0_origins():
    """Keep the original mesh and reuse the 200mm lane allocation for plane/L9."""
    original = terrain_source.install_origins

    def install(cfg):
        original(cfg)
        original_origins = TerrainImporter._compute_env_origins_curriculum

        def origins(terrain, num_envs, terrain_origins):
            original_origins(terrain, num_envs, terrain_origins)
            special = terrain.r1_continuous_stair_mask.clone()
            if not bool(special.any()):
                raise RuntimeError('Expected the original fixed-stair allocation')
            flat = terrain.r1_flat_mask
            l9 = terrain.r1_pitch_rough_mask
            for group in (terrain.r1_nominal_mask, ~terrain.r1_nominal_mask):
                population = (special & group).nonzero().flatten()
                flat[population[::2]] = True
                l9[population[1::2]] = True
            columns = terrain.r1_column_families
            flat_columns = (columns == 8).nonzero().flatten()
            moved_to_plane = (special & flat).nonzero().flatten()
            terrain.terrain_types[moved_to_plane] = flat_columns[torch.arange(
                len(moved_to_plane), device=terrain.device) % len(flat_columns)]
            terrain.terrain_types[l9] = (columns == 9).nonzero().flatten()[0]
            terrain.terrain_levels[l9] = 9
            terrain.terrain_levels[moved_to_plane] = terrain.terrain_levels[moved_to_plane] % 10
            # Centers and collision mesh are unchanged. Spread the larger L9 group
            # over the same tile, leaving room for the 2.2m/s start/stop samples.
            for column in torch.cat((flat_columns, (columns == 9).nonzero().flatten())):
                rows = (terrain.terrain_types == column).nonzero().flatten()
                width = max(1, int(len(rows)**.5 + .9999))
                k = torch.arange(len(rows), device=terrain.device)
                spacing = min(.45, 3.0 / width)
                terrain.r1_offsets[rows, 0] = (k % width - (width-1)*.5) * spacing
                terrain.r1_offsets[rows, 1] = (k // width - (width-1)*.5) * spacing
            terrain.r1_continuous_stair_mask.zero_()
            terrain.r1_retained_rough_mask.copy_(~flat)
            terrain.r1_pitch_target_mask.copy_(flat | l9)
            result = terrain_origins[terrain.terrain_levels, terrain.terrain_types].clone() + terrain.r1_offsets
            downward = torch.zeros_like(result)
            downward[:, 2] = -1.
            result[:, 2] = raycast_mesh(result - 5.*downward, downward,
                                        terrain.r1_wp_mesh, max_dist=10.)[0][:, 2]
            if not bool(torch.isfinite(result).all()):
                raise RuntimeError('Flat/rough origin ray missed')
            return result

        TerrainImporter._compute_env_origins_curriculum = origins

    terrain_source.install_origins = install


def e0_reward_configuration():
    cfg = configuration_scut_v1()
    cfg.rewards['track_lin_vel_xy'] = 1.2
    cfg.rewards['track_lin_vel_xy_square'] = -1.5
    cfg.lin_vel_xy_square_sigma = 1.
    return cfg


def start_stop(ticks, speed, low_speed):
    # Lower gears need time to reach steady speed before the next key change.
    active_ticks = torch.where(low_speed, 125, 55)
    period = active_ticks + 100
    elapsed = (ticks - 100).clamp_min(0)
    phase = torch.remainder(elapsed, period)
    sign = torch.where(elapsed // period % 2 == 0, 1., -1.)
    moving = (ticks >= 100) & (phase < active_ticks)
    return torch.where(moving, speed * sign, 0.), moving


class NormalDriveEnv(ScutUnifiedRoughV1Env):
    enforce_closure_reset = False
    leg_pd_decimation = 4
    wheel_pd_decimation = 1

    def __init__(self, cfg, meta, bank):
        self.drive_ready = False
        super().__init__(cfg, meta, bank)
        self.drive_enabled = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self.drive_low = self.drive_enabled.clone()
        self.support_seen = self.drive_enabled.clone()
        self.drive_speed = torch.ones_like(self.height)
        self.drive_height = self.height.clone()
        self.drive_issued_ticks = torch.zeros_like(self.episode_length_buf)
        self.drive_issued_vx = self.drive_speed.clone()
        self.drive_stats = torch.zeros(2, 2, 5, device=self.device, dtype=torch.float64)
        self.wheel_sensor_ids = [self.scene['contacts'].body_names.index(name)
                                 for name in ('left_wheel_link', 'right_wheel_link')]
        self.drive_ready = True
        original = self.reward._postprocess_reward_terms

        def use_horizontal_speed(terms):
            data = self.view.data
            corrections = horizontal_reward_terms(data.root_lin_vel_b, data.projected_gravity_b,
                                                  self.reward.command, self.reward.cfg)
            for key, value in corrections.items():
                if key in terms:
                    terms[key] = torch.where(self.drive_enabled, value, terms[key])
            return original(terms)

        self.reward._postprocess_reward_terms = use_horizontal_speed

    def _make_reward(self, meta):
        return make_reward_class(meta, cfg_factory=e0_reward_configuration)(self.view, self.num_envs, self.device)

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        if not self.drive_ready:
            return
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        self.support_seen[ids] = False
        self.drive_enabled[ids] = False
        group = ids[self.terrain.r1_pitch_target_mask[ids]]
        generator = self.reset_generator
        picked = group[torch.rand(len(group), device=self.device, generator=generator) < .78]
        self.drive_enabled[picked] = True
        n = len(picked)
        low = torch.rand(n, device=self.device, generator=generator) < .68
        choice = torch.randint(4, (n,), device=self.device, generator=generator)
        self.drive_low[picked] = low
        self.drive_speed[picked] = torch.where(low, self.height.new_tensor([.20, .35, .50, .90])[choice],
                                              self.height.new_tensor([1.20, 1.50, 2.00, 2.20])[choice])
        self.drive_speed[picked] *= torch.where(torch.rand(n, device=self.device, generator=generator)<.50, 1., -1.)
        self.drive_height[picked] = torch.where(low, self.height.new_tensor([.40, .42, .42, .40])[choice],
                                               self.height.new_tensor([.28, .40, .28, .42])[choice])
        self._ground_command_until[picked] = 0
        self._apply_drive_commands()

    def _apply_drive_commands(self):
        if not self.drive_ready:
            return
        picked = self.drive_enabled.nonzero().flatten()
        vx, moving = start_stop(self.episode_length_buf[picked], self.drive_speed[picked], self.drive_low[picked])
        self.command[picked] = 0.
        self.command[picked, 0] = vx
        self.height[picked] = self.drive_height[picked]
        self.command_timer[picked] = 1e9
        self.heading_env[picked] = False
        self.standing_env[picked] = ~moving
        self._ground_original_command[picked] = self.command[picked]
        self._ground_original_heading[picked] = False
        self.reward.command[picked] = self.command[picked]
        self.reward.height_cmd[picked] = self.height[picked]
        self.reward._invalidate_step_caches()

    def _get_observations(self):
        self._apply_drive_commands()
        return super()._get_observations()

    def _pre_physics_step(self, actions):
        self._apply_drive_commands()
        self.drive_issued_ticks.copy_(self.episode_length_buf)
        self.drive_issued_vx.copy_(self.command[:, 0])
        return super()._pre_physics_step(actions)

    def _get_rewards(self):
        base = super()._get_rewards()
        if not self.drive_ready:
            return base
        data = self.view.data
        gravity = data.projected_gravity_b
        pitch = body_pitch(gravity)
        rate = data.root_ang_vel_b[:, 1]
        forces = tensor(self.scene['contacts'].data.net_forces_w)[:, self.wheel_sensor_ids, 2]
        self.support_seen, active = stability_active_mask(self.drive_enabled, (forces > 5.).any(1),
            self.support_seen, self.reset_terminated, self.drive_issued_ticks * self.step_dt)
        vx = heading_velocity(data.root_lin_vel_b, gravity)[:, 0]
        error = (vx - self.drive_issued_vx).abs()
        low_speed_cost = .4 * (torch.exp(-error.square() / .04) - 1.) * self.step_dt * active * self.drive_low
        pitch_terms = stability_components(pitch, rate, active, self.step_dt, command_vx=self.drive_issued_vx)
        for index, surface in enumerate((self.terrain.r1_flat_mask, self.terrain.r1_pitch_rough_mask)):
            for moving in (False, True):
                mask = active & self.drive_low & surface & ((self.drive_issued_vx != 0.) == moving)
                self.drive_stats[index, int(moving)] += torch.stack((mask.sum(), (error*mask).sum(),
                    (pitch.abs()*mask).sum(), (vx*mask).sum(), (self.drive_issued_vx*mask).sum())).double()
        return base + pitch_terms.sum(1) + low_speed_cost

    def drive_summary(self):
        columns = ('samples', 'sum_abs_error', 'sum_abs_pitch_rad', 'sum_vx', 'sum_command_vx')
        return {name: {phase: dict(zip(columns, row)) for phase, row in zip(('stop', 'move'), values)}
                for name, values in zip(('flat', 'rough_L9'), self.drive_stats.tolist())}

"""COMMANDER-AUTHORED & LOCKED Generalized 4D-Terrain Stair RL Environment (DO NOT MODIFY!).

Key guarantees:
1. Exact sensor twin: computes g_step = [d1, h1, d2, h2] on GPU using the exact same
   extract_profile_torch(s, z) function as CPU TerrainSensor4D (zero Sim2Player formula gap),
   plus +-4 cm distance noise, +-2 cm height noise, and 0..2 tick latency in DR/training.
2. Exact E0 <-> E_stair_nav4d handoff: outside the stair zone (d1 > 1.00 m or after deck
   stabilization), frozen SymmetricE0 drives the robot so handoff distributions match 100%.
3. Fixed cumulative step elevation: z_step_base + h1_true works identically on single stairs
   (0 -> 0.20 m) and continuous double stairs (0.20 -> 0.35/0.40 m), never collapsing on tread 1!
4. 84% 200 mm focus (step_20, +-22 deg oblique_20, RMUL 2027 3v3 200/400 mm, RMUC 2027 5v5
   surveyed West/East corridors) + 8% 110 mm curbs + 8% RMUL 250 mm steps.
"""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
import trimesh

import fsm_isaac_env as donor
from isaaclab.utils.math import quat_apply, quat_from_euler_xyz
from fsm_geometry import oblique_edge, rm27_profile
from fsm_reset_sensors import refresh_reset_sensors
from terrain_sensor_4d import S_GRID_NP, extract_profile_torch

COURSES = donor.COURSES


def nav4d_course_mesh(difficulty, cfg):
    """Build exact training meshes for courses 2..8."""
    width, length = cfg.size
    c = cfg.course
    if c in (5, 6):
        survey_path = Path(__file__).with_name("RM27_SURVEY.npz")
        with np.load(survey_path) as survey:
            sx, sy = survey["xs"][::4], survey["ys"][::2]
            source = survey["heights"][c - 5, ::2, ::4]
        xs = np.r_[-width / 2, sx[(sx > -width / 2) & (sx < width / 2)], width / 2]
        ys = np.r_[-length / 2, sy[(sy > -length / 2) & (sy < length / 2)], length / 2]
        along = np.array([np.interp(xs, sx, row) for row in source])
        heights = np.stack([np.interp(ys, sy, along[:, i]) for i in range(len(xs))], 1)
        xx, yy = np.meshgrid(xs, ys)
        vertices = np.column_stack((xx.ravel() + width / 2, yy.ravel() + length / 2, heights.ravel()))
        yyid, xxid = np.meshgrid(np.arange(len(ys) - 1), np.arange(len(xs) - 1), indexing="ij")
        a = (yyid * len(xs) + xxid).ravel()
        faces = np.concatenate(
            (np.stack((a, a + 1, a + len(xs)), 1), np.stack((a + 1, a + len(xs) + 1, a + len(xs)), 1))
        )
        return [trimesh.Trimesh(vertices=vertices, faces=faces, process=False)], np.array([width / 2, length / 2, 0.0])

    ys = np.linspace(-length / 2, length / 2, 81)
    zeros = np.zeros_like(ys)
    if c == 2:
        # 110 mm single curb
        layers = [(zeros - width / 2, 0.0), (zeros, 0.0), (zeros, 0.11), (zeros + width / 2, 0.11)]
    elif c == 3:
        # 200 mm straight single stair (core benchmark + RMUL 2027 3v3 main 200 mm highland)
        layers = [(zeros - width / 2, 0.0), (zeros, 0.0), (zeros, 0.20), (zeros + width / 2, 0.20)]
    elif c == 4:
        # 200 mm +-22 deg oblique single stair
        first = oblique_edge(ys, cfg.edge_sign)
        layers = [(zeros - width / 2, 0.0), (first, 0.0), (first, 0.20), (zeros + width / 2, 0.20)]
    elif c == 7:
        # RMUL 2027 3v3 200 mm + 200 mm = 400 mm crisp double highland (tread 1.15 m / 1.45 m)
        tread = 1.15 if cfg.edge_sign > 0 else 1.45
        layers = [
            (zeros - width / 2, 0.0),
            (zeros, 0.0),
            (zeros, 0.20),
            (zeros + tread, 0.20),
            (zeros + tread, 0.40),
            (zeros + width / 2, 0.40),
        ]
    else:
        # course 8: RMUL 2027 3v3 250 mm crisp single highland step
        layers = [(zeros - width / 2, 0.0), (zeros, 0.0), (zeros, 0.25), (zeros + width / 2, 0.25)]

    vertices = np.concatenate(
        [np.column_stack((x + width / 2, ys + length / 2, np.full_like(ys, z))) for x, z in layers]
    )
    faces = []
    n = len(ys)
    for k in range(len(layers) - 1):
        for j in range(n - 1):
            a = k * n + j
            faces.extend([(a, a + n, a + 1), (a + 1, a + n, a + n + 1)])
    return [trimesh.Trimesh(vertices=vertices, faces=faces, process=False)], np.array([width / 2, length / 2, 0.0])


def install_course():
    donor.course_mesh = nav4d_course_mesh
    donor.CourseCfg.function = staticmethod(nav4d_course_mesh)
    donor.install_course()
    base_install = donor.terrain_source.install_origins

    def install_with_200mm_priority(cfg):
        base_install(cfg)
        importer = donor.TerrainImporter

        def origins(self, count, grid):
            device = self.device
            ids = torch.arange(count, device=device)
            # 25-slot deterministic pattern -> 84% 200mm (single, oblique, RMUC 5v5, RMUL 3v3) + 8% 110mm + 8% 250mm:
            # 2:curb11(2), 3:step20(7), 4:oblique20(4), 5:rm27_west(3), 6:rm27_east(3), 7:rmul_double200(4), 8:rmul_250(2)
            pattern = torch.tensor(
                (3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 7, 2, 2, 8, 8),
                device=device,
            )
            group = pattern[ids % len(pattern)]
            ordinal = ids // len(pattern)
            self.silky_group = group
            self.max_terrain_level = len(grid)
            self.terrain_types = group * donor.COLS_PER_COURSE + (ordinal % donor.COLS_PER_COURSE)
            self.terrain_levels = (ordinal // donor.COLS_PER_COURSE) % len(grid)
            self.r1_column_families = torch.tensor(donor.FAMILIES, device=device).repeat_interleave(donor.COLS_PER_COURSE)
            self.r1_nominal_mask = torch.zeros(count, device=device, dtype=torch.bool)
            self.r1_flat_mask = group == 0
            self.r1_pitch_rough_mask = group == 1
            self.r1_pitch_target_mask = group < 2
            self.r1_retained_rough_mask = group == 1
            self.r1_continuous_stair_mask = group >= 2
            self.r1_offsets = torch.zeros(count, 3, device=device)
            self.r1_offsets[:, 1] = ((ordinal // (donor.COLS_PER_COURSE * len(grid))) % 5 - 2.0) * 0.22
            self.r1_wp_mesh = donor.convert_to_warp_mesh(self.silky_mesh.vertices, self.silky_mesh.faces, device)
            return grid[self.terrain_levels, self.terrain_types] + self.r1_offsets

        importer._compute_env_origins_curriculum = origins

    donor.terrain_source.install_origins = install_with_200mm_priority


class Nav4DIsaacEnv(donor.FSMStairEnv):
    def __init__(self, *args, **kwargs):
        self.nav_ready = False
        super().__init__(*args, **kwargs)
        device = self.device

        # Load exact RM27_SURVEY height grids onto GPU for exact height queries on courses 5 & 6
        with np.load(Path(__file__).with_name("RM27_SURVEY.npz")) as survey:
            self.rm27_xs = torch.tensor(survey["xs"], dtype=torch.float32, device=device)
            self.rm27_ys = torch.tensor(survey["ys"], dtype=torch.float32, device=device)
            # shape (2, 1, Ny, Nx) for grid_sample
            self.rm27_grid = torch.tensor(survey["heights"], dtype=torch.float32, device=device).unsqueeze(1)

        self.s_ray = torch.tensor(S_GRID_NP, dtype=torch.float32, device=device)
        scanx, scany = torch.meshgrid(
            torch.linspace(-0.40, 1.20, 17, device=device),
            torch.linspace(-0.40, 0.40, 9, device=device),
            indexing="ij",
        )
        self.scanx = scanx.flatten()
        self.scany = scany.flatten()

        # Course parameters: first_edge_x, first_top_z, second_edge_x, final_top_z, is_double
        self.is_double = (self.group == 5) | (self.group == 6) | (self.group == 7)
        self.tread_7 = torch.where(self.edge_sign > 0, 1.15, 1.45)
        w_lip = rm27_profile(True)[2]
        e_lip = rm27_profile(False)[2]
        self.first_nominal_x = torch.where(
            self.group == 5, 0.872, torch.where(self.group == 6, 0.825, 0.0)
        )
        self.final_lip_x = torch.where(
            self.group == 5,
            w_lip + 0.15,
            torch.where(self.group == 6, e_lip + 0.15, torch.where(self.group == 7, self.tread_7, 0.0)),
        )
        self.stage1_top_z = torch.where(
            self.group == 2, 0.11, torch.where(self.group == 8, 0.25, 0.20)
        )
        self.final_top_z = torch.where(
            (self.group == 5) | (self.group == 6),
            0.30,
            torch.where(self.group == 7, 0.40, self.stage1_top_z),
        )
        self.peak_crest_z = torch.where(
            (self.group == 5) | (self.group == 6), 0.35, self.final_top_z
        )

        # Body contact indices excluding main wheels and guide wheels (chassis/leg collision penalty)
        allowed = {idx for pair in self.contact_ids for idx in pair}
        self.body_undesired_ids = [
            i for i in range(len(self.scene["contacts"].body_names)) if i not in allowed
        ]
        self.guide_ids_flat = [i for ids in self.contact_ids for i in ids[1:]]

        self.g_delay = torch.zeros(self.num_envs, 3, 4, device=device)
        self.g_pending = torch.ones(self.num_envs, device=device, dtype=torch.bool)
        self.g_tick = -1
        self.g_step_true = torch.zeros(self.num_envs, 4, device=device)
        self.g_step = torch.zeros(self.num_envs, 4, device=device)

        self.stair_hold_ticks = torch.zeros(self.num_envs, dtype=torch.long, device=device)
        self.stair_active_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=device)

        self.nav_step_reward = torch.zeros(self.num_envs, device=device)
        self.nav_failed = torch.zeros(self.num_envs, device=device, dtype=torch.bool)
        self.nav_crossed1 = torch.zeros(self.num_envs, device=device, dtype=torch.bool)
        self.nav_crossed2 = torch.zeros(self.num_envs, device=device, dtype=torch.bool)
        self.nav_stage1_bonus_paid = torch.zeros(self.num_envs, device=device, dtype=torch.bool)
        self.nav_final_bonus_paid = torch.zeros(self.num_envs, device=device, dtype=torch.bool)
        self.nav_deck_substeps = torch.zeros(self.num_envs, dtype=torch.long, device=device)
        self.nav_max_x = torch.zeros(self.num_envs, device=device)
        self.nav_max_lift_stage = torch.zeros(self.num_envs, device=device)
        self.prev_policy_action = torch.zeros(self.num_envs, 6, device=device)
        self.action_smooth_cost = torch.zeros(self.num_envs, device=device)

        # Stats: [episodes, falls_or_reg, final_deck_success, stage1_crossed, step20_eps, step20_succ, rmul_eps, rmul_succ]
        self.nav_stats = torch.zeros(8, dtype=torch.long, device=device)
        self.nav_ready = True
        # Re-reset all envs cleanly with Nav4D initial states
        self._reset_idx(torch.arange(self.num_envs, device=device))

    def local_pose(self):
        data = self.view.data
        q = data.root_quat_w
        w, x, y, z = q.unbind(1)
        yaw = torch.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
        pos = data.root_pos_w - self.centers
        return pos, yaw

    def terrain_height(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Exact vectorized terrain elevation z(x, y) for arbitrary query points (N, K)."""
        g = self.group[:, None]
        z = torch.zeros_like(x)

        # Analytic courses 2, 3, 4, 7, 8
        z = torch.where((g == 2) & (x >= 0.0), 0.11, z)
        z = torch.where((g == 3) & (x >= 0.0), 0.20, z)
        ob_edge = oblique_edge(y, self.edge_sign[:, None])
        z = torch.where((g == 4) & (x >= ob_edge), 0.20, z)
        t7 = self.tread_7[:, None]
        z7 = torch.where(x >= t7, 0.40, torch.where(x >= 0.0, 0.20, 0.0))
        z = torch.where(g == 7, z7, z)
        z = torch.where((g == 8) & (x >= 0.0), 0.25, z)

        # Surveyed RMUC 2027 courses 5 (West) & 6 (East) via bilinear grid_sample
        for c_id, grid_idx in ((5, 0), (6, 1)):
            mask = self.group == c_id
            if bool(mask.any()):
                xm = x[mask]
                ym = y[mask]
                nx = 2.0 * (xm - self.rm27_xs[0]) / (self.rm27_xs[-1] - self.rm27_xs[0]) - 1.0
                ny = 2.0 * (ym - self.rm27_ys[0]) / (self.rm27_ys[-1] - self.rm27_ys[0]) - 1.0
                sample_coords = torch.stack((nx, ny), dim=-1).unsqueeze(0)  # (1, M_env, K, 2)
                sampled = F.grid_sample(
                    self.rm27_grid[grid_idx : grid_idx + 1],
                    sample_coords,
                    mode="bilinear",
                    padding_mode="border",
                    align_corners=True,
                )[0, 0]
                z[mask] = sampled
        return z

    def compute_true_g_step(self) -> torch.Tensor:
        pos, yaw = self.local_pose()
        c = torch.cos(yaw)[:, None]
        s = torch.sin(yaw)[:, None]
        rx = pos[:, 0:1] + c * self.s_ray[None, :]
        ry = pos[:, 1:2] + s * self.s_ray[None, :]
        rz = self.terrain_height(rx, ry)
        return extract_profile_torch(self.s_ray, rz)

    def update_nav_features(self):
        if not self.nav_ready or self.g_tick == self._sim_step_counter:
            return
        raw = self.compute_true_g_step()
        self.g_step_true.copy_(raw)

        # Apply LiDAR relocalization + gimbal encoder noise (+-3.5 cm dist, +-1.5 cm height) & 0..2 tick latency
        # On 0-DR nominal rows during evaluation/stage0, keep small realistic jitter (1 cm) and full jitter on DR rows
        dr_scale = torch.where(self.full_dr.nominal_env_mask, 0.25, 1.0)[:, None]
        noise = (torch.rand_like(raw) * 2.0 - 1.0) * raw.new_tensor([0.035, 0.015, 0.035, 0.015]) * dr_scale
        noisy = raw + noise
        has1 = raw[:, 1] > 0.05
        has2 = raw[:, 3] > 0.05
        noisy[:, 0] = torch.where(has1, noisy[:, 0].clamp(-0.35, 1.60), 1.60)
        noisy[:, 1] = torch.where(has1, noisy[:, 1].clamp(0.06, 0.28), 0.0)
        noisy[:, 2] = torch.where(has2, noisy[:, 2].clamp(0.00, 1.60), 1.60)
        noisy[:, 3] = torch.where(has2, noisy[:, 3].clamp(0.06, 0.28), 0.0)

        self.g_delay[:, :-1] = self.g_delay[:, 1:].clone()
        self.g_delay[:, -1] = noisy
        self.g_delay[self.g_pending] = noisy[self.g_pending, None, :]
        self.g_pending.zero_()

        max_delay = torch.where(self.full_dr.nominal_env_mask, 0, 2)
        rand_d = (torch.rand(self.num_envs, device=self.device) * (max_delay.float() + 0.99)).long()
        self.g_step = self.g_delay[torch.arange(self.num_envs, device=self.device), 2 - rand_d]

        # Exact objective stair-zone routing gate (identical to deployment bridge!)
        step_ahead = (self.g_step[:, 1] > 0.06) & (self.g_step[:, 0] <= 1.00)
        fwd_intent = self.command[:, 0] > 0.12
        self.stair_hold_ticks = torch.where(
            step_ahead & fwd_intent,
            torch.full_like(self.stair_hold_ticks, 32),
            (self.stair_hold_ticks - 1).clamp_min(0),
        )
        self.stair_hold_ticks = torch.where(self.command[:, 0] < -0.05, 0, self.stair_hold_ticks)
        self.stair_active_mask = self.stair_hold_ticks > 0
        self.g_tick = self._sim_step_counter

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        if not self.nav_ready:
            return
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long)
        n = len(ids)
        if not n:
            return
        u = torch.rand(n, 6, device=self.device, generator=self.reset_generator)
        # Wide operator height [0.26, 0.40] m & speed [0.50, 2.15] m/s & yaw [-26, +26] deg
        height = 0.26 + 0.14 * u[:, 0]
        max_yaw = torch.where(self.group[ids] == 4, math.radians(24.0), math.radians(22.0))
        yaw = (u[:, 1] - 0.5) * 2.0 * max_yaw

        pick = (self._bank_h[None, :] - height[:, None]).abs().argmin(1)
        qpos = self._bank_q[pick][:, self._bank_ids].clone()

        root = donor.tensor(self.robot.data.default_root_state)[ids].clone()
        root[:, :3] = self.centers[ids]
        # Spawn 0.85..1.65 m before first riser so robot smoothly accelerates on E0 and crosses the 1.00 m handoff!
        first_x = self.first_nominal_x[ids]
        root[:, 0] += first_x - (0.85 + 0.80 * u[:, 2])
        root[:, 1] += (u[:, 3] - 0.5) * 0.36
        query_xy = self.view.data.root_pos_w[:, :2] - self.centers[:, :2]
        query_xy[ids] = root[:, :2] - self.centers[ids, :2]
        z0 = self.terrain_height(query_xy[:, :1], query_xy[:, 1:2])[ids, 0]
        root[:, 2] = self.centers[ids, 2] + z0 + self._bank_h[pick] + 0.004
        root[:, 3:7] = quat_from_euler_xyz(torch.zeros_like(yaw), torch.zeros_like(yaw), yaw)
        root[:, 7:] = 0.0

        self.robot.write_root_state_to_sim(root, env_ids=ids)
        self.robot.write_joint_state_to_sim(qpos, torch.zeros_like(qpos), env_ids=ids)

        cmd_speed = 0.50 + 1.65 * u[:, 4]
        self.command_after_settle[ids] = 0.0
        self.command_after_settle[ids, 0] = cmd_speed
        self.course_height[ids] = height
        self.command[ids] = 0.0
        self.runup_steps = 12

        local_x0 = root[:, 0] - self.centers[ids, 0]
        self.nav_max_x[ids] = local_x0
        self.nav_max_lift_stage[ids] = 0.0
        self.nav_failed[ids] = False
        self.nav_crossed1[ids] = False
        self.nav_crossed2[ids] = False
        self.nav_stage1_bonus_paid[ids] = False
        self.nav_final_bonus_paid[ids] = False
        self.nav_deck_substeps[ids] = 0
        self.stair_hold_ticks[ids] = 0
        self.stair_active_mask[ids] = False
        self.prev_policy_action[ids] = 0.0
        self.action_smooth_cost[ids] = 0.0
        self.g_pending[ids] = True
        self.history_pending[ids] = True

        refresh_reset_sensors(self, ids)
        self._commands()
        self.update_nav_features()

    def _get_observations(self):
        obs = super()._get_observations()
        self.update_nav_features()
        return obs

    def _pre_physics_step(self, actions):
        if self.nav_ready:
            self.nav_step_reward.zero_()
            diff = actions - self.prev_policy_action
            self.action_smooth_cost.copy_(
                0.010 * diff[:, :4].square().mean(1) + 0.003 * diff[:, 4:].square().mean(1)
            )
            self.prev_policy_action.copy_(actions.detach())
        return super()._pre_physics_step(actions)

    def sample_physics(self, dt):
        if not self.nav_ready:
            return
        self.sample_count += 1
        data = self.view.data
        pos, yaw = self.local_pose()

        gb = data.projected_gravity_b
        pitch = torch.asin(gb[:, 0].clamp(-1.0, 1.0)).abs()
        roll = torch.asin(gb[:, 1].clamp(-1.0, 1.0)).abs()
        ang_vel = data.root_ang_vel_b
        vx_b = data.root_lin_vel_b[:, 0]
        com_vel = data.root_com_lin_vel_w if hasattr(data, "root_com_lin_vel_w") else data.root_lin_vel_w
        vx_course = com_vel[:, 0]

        wheels = data.body_pos_w[:, self.wheel_body_ids] - self.centers[:, None]
        axis_z = quat_apply(
            data.body_quat_w[:, self.wheel_body_ids], self.tire_axis.expand_as(wheels)
        )[..., 2].abs()
        extent = (
            self.tire_radius * (1.0 - axis_z.square()).clamp_min(0.0).sqrt()
            + self.tire_half_width * axis_z
        )
        feet = wheels[..., 2] - extent  # (N, 2) world/local Z of bottom of left & right tires

        forces = donor.tensor(self.scene["contacts"].data.net_forces_w)
        main_f = forces[:, [ids[0] for ids in self.contact_ids]]
        main_fz = main_f[..., 2]

        # True upcoming step distance & height
        d1 = self.g_step_true[:, 0]
        h1 = self.g_step_true[:, 1]
        has_step = h1 > 0.06

        # Exact floor elevation right at the base of the upcoming riser (works for BOTH step 1 & step 2!)
        c_yaw = torch.cos(yaw)
        s_yaw = torch.sin(yaw)
        foot_probe_s = (d1 - 0.18).clamp(-0.30, 1.20)
        z_step_base = self.terrain_height(
            (pos[:, 0] + foot_probe_s * c_yaw).unsqueeze(1),
            (pos[:, 1] + foot_probe_s * s_yaw).unsqueeze(1),
        )[:, 0]
        z_step_top = z_step_base + h1
        z_under_base = self.terrain_height(pos[:, 0:1], pos[:, 1:2])[:, 0]

        # 1. Approach phase (0.14 < d1 <= 0.98): raise stance so front guide wheel clears step top + self-regulate speed!
        approach = has_step & (d1 > 0.14) & (d1 <= 0.98) & (self.command[:, 0] > 0.12)
        guide_pos = data.body_pos_w[:, self.guide_ids_flat] - self.centers[:, None]
        rel_gx = (guide_pos[..., 0] - pos[:, None, 0]) * c_yaw[:, None] + (
            guide_pos[..., 1] - pos[:, None, 1]
        ) * s_yaw[:, None]
        front_guide = rel_gx > 0.02
        guide_low = torch.where(front_guide, guide_pos[..., 2] - 0.025, 10.0).amin(1)
        z_guide_des = z_step_top + 0.038
        r_guide = (
            2.6 * torch.exp(-((guide_low - z_guide_des) / 0.045).square())
            + 1.4 * ((guide_low - z_step_top).clamp(-0.12, 0.035) / 0.035)
        ) * approach

        r_speed_prep = (
            2.0 * torch.exp(-((vx_b - 0.88) / 0.35).square())
            - 2.2 * (vx_b - 1.25).clamp_min(0.0).square()
            - 1.5 * (0.35 - vx_b).clamp_min(0.0)
        ) * approach

        # 2. Active riser climb (-0.22 <= d1 <= 0.22): rapid main-wheel lift above z_step_base & forward pull
        at_riser = has_step & (d1 >= -0.22) & (d1 <= 0.22) & (self.command[:, 0] > 0.12)
        wheel_lift_rel = ((feet - z_step_base[:, None]) / h1.clamp_min(0.10)[:, None]).clamp(0.0, 1.10)
        r_lift_dense = (3.6 * wheel_lift_rel.mean(1) + 1.6 * vx_course.clamp(-0.20, 0.85)) * at_riser

        # Per-stage monotonic wheel-lift potential (resets when stage 1 completes so stage 2 gets fresh potential!)
        cur_target_top = torch.where(self.nav_crossed1 & self.is_double, self.peak_crest_z, self.stage1_top_z)
        cur_floor = torch.where(self.nav_crossed1 & self.is_double, self.stage1_top_z, torch.zeros_like(self.stage1_top_z))
        norm_lift = ((feet.mean(1) - cur_floor) / (cur_target_top - cur_floor).clamp_min(0.10)).clamp(0.0, 1.05)
        new_lift_max = torch.where(
            at_riser | (has_step & (d1 <= 0.30)),
            torch.maximum(self.nav_max_lift_stage, norm_lift),
            self.nav_max_lift_stage,
        )
        r_lift_pot = 8.5 * (new_lift_max - self.nav_max_lift_stage)
        self.nav_max_lift_stage.copy_(new_lift_max)

        # Penalize wheel-torque ramming into riser while wheels are still below step top
        riser_hit = torch.stack(
            [((-forces[:, ids, 0]) > (forces[:, ids, 2].abs() + 5.0)).any(1) for ids in self.contact_ids],
            dim=1,
        )
        wheel_torque_abs = self.applied_motor_torque[:, 4:].abs()
        unload_pen = (
            0.08 * ((wheel_torque_abs - 1.2).clamp_min(0.0).square() * riser_hit).sum(1) * at_riser
        )

        # 3. Forward course progress (capped per substep so ballistic launch cannot farm reward)
        course_goal_x = self.final_lip_x + 0.55
        capped_x = pos[:, 0].minimum(course_goal_x)
        next_max_x = torch.maximum(self.nav_max_x, capped_x)
        dx_prog = (next_max_x - self.nav_max_x).clamp(0.0, 0.025)
        self.nav_max_x.copy_(next_max_x)
        r_prog = 7.0 * dx_prog * (self.command[:, 0] > 0.12)

        # 4. Stage crossing & anti-regression detection
        loaded_both = (main_fz >= 8.0).all(1)
        past_first_x = (wheels[..., 0] > self.first_nominal_x[:, None] + 0.06).all(1)
        on_stage1_z = ((feet - self.stage1_top_z[:, None]).abs() < 0.042).all(1)
        newly_c1 = past_first_x & on_stage1_z & loaded_both & ~self.nav_crossed1
        self.nav_crossed1 |= newly_c1
        # Reset lift potential when stage 1 completes on double stairs so step 2 gets full lift potential!
        self.nav_max_lift_stage = torch.where(newly_c1 & self.is_double, 0.0, self.nav_max_lift_stage)

        past_final_x = (wheels[..., 0] > self.final_lip_x[:, None] + 0.12).all(1)
        on_final_z = ((feet - self.final_top_z[:, None]).abs() < 0.042).all(1)
        upright_deck = (pitch < math.radians(10.0)) & (roll < math.radians(8.0))
        on_final_deck = past_final_x & on_final_z & loaded_both & upright_deck & (
            ~self.is_double | self.nav_crossed1
        )
        self.nav_crossed2 |= on_final_deck
        self.nav_deck_substeps = torch.where(
            on_final_deck, self.nav_deck_substeps + 1, torch.zeros_like(self.nav_deck_substeps)
        )

        # Strict anti-cheat step regression termination
        reg1 = self.nav_crossed1 & ~self.nav_crossed2 & (feet.amin(1) < self.stage1_top_z - 0.085)
        reg2 = self.nav_crossed2 & (feet.amin(1) < self.final_top_z - 0.085)

        # Undesired belly/chassis collision force
        if self.body_undesired_ids:
            belly_f = forces[:, self.body_undesired_ids, :].norm(dim=-1).amax(1)
        else:
            belly_f = torch.zeros_like(vx_b)

        rel_base_z = pos[:, 2] - z_under_base
        bad_pose = (
            (pitch > math.radians(40.0))
            | (roll > math.radians(32.0))
            | (gb[:, 2] > -0.55)
            | (pos[:, 1].abs() > 1.35)
            | (rel_base_z < 0.130)
        )
        self.nav_failed |= bad_pose | reg1 | reg2

        # Post-climb deck settle & cruise reward
        r_deck = (
            4.0 * on_final_deck * torch.exp(-((rel_base_z - 0.31) / 0.055).square())
            + 1.2 * (newly_c1 & self.is_double).float() / dt
        )
        free_cruise = ~approach & ~at_riser
        r_vel_track = -0.25 * (vx_b - self.command[:, 0].clamp_max(1.5)).square().clamp_max(4.0) * free_cruise

        # Attitude, angular rate, rollback & belly contact penalties
        r_att_pen = (
            6.5 * ((pitch - math.radians(22.0)).clamp_min(0.0) / 0.12).square()
            + 4.5 * (roll / 0.15).square()
            + 0.05 * (ang_vel[:, 0].square() + ang_vel[:, 1].square() + 0.5 * ang_vel[:, 2].square())
            + 1.2 * (-vx_b).clamp_min(0.0)
            + 0.015 * (belly_f - 5.0).clamp_min(0.0).clamp_max(40.0)
        )

        step_r = (
            r_prog
            + r_lift_pot
            + dt * (r_guide + r_speed_prep + r_lift_dense + r_deck + r_vel_track - unload_pen - r_att_pen - 0.15)
        )
        self.nav_step_reward += step_r

    def _get_rewards(self):
        if not self.nav_ready:
            return super()._get_rewards()
        stage1_bonus = 6.0 * (self.nav_crossed1 & ~self.nav_stage1_bonus_paid).float()
        self.nav_stage1_bonus_paid |= self.nav_crossed1

        deck_done = (self.nav_deck_substeps >= 160) & ~self.nav_failed
        final_bonus = 14.0 * (deck_done & ~self.nav_final_bonus_paid).float()
        self.nav_final_bonus_paid |= deck_done

        total = (
            self.nav_step_reward
            + stage1_bonus
            + final_bonus
            - self.action_smooth_cost
            - 25.0 * self.nav_failed.float()
        )
        return torch.nan_to_num(total, nan=-25.0, posinf=20.0, neginf=-25.0)

    def _get_dones(self):
        if not self.nav_ready:
            return super()._get_dones()
        nonfinite = ~torch.isfinite(self.view.data.root_pos_w).all(1) | ~torch.isfinite(
            self.view.data.root_lin_vel_w
        ).all(1)
        failed = self.nav_failed | nonfinite
        deck_graduated = self.nav_deck_substeps >= 200  # 0.50 s solid support on final deck
        timeout = (self.episode_length_buf >= 320) | deck_graduated
        ended = failed | timeout
        if bool(ended.any()):
            succ = ended & ~failed & (self.nav_deck_substeps >= 160)
            s20 = self.group == 3
            rmul = (self.group == 7) | (self.group == 8)
            self.nav_stats += torch.stack(
                (
                    ended.sum(),
                    (ended & failed).sum(),
                    succ.sum(),
                    (ended & self.nav_crossed1).sum(),
                    (ended & s20).sum(),
                    (succ & s20).sum(),
                    (ended & rmul).sum(),
                    (succ & rmul).sum(),
                )
            ).long()
        return failed, timeout


class TrainingAdapter:
    def __init__(self, env: Nav4DIsaacEnv, e0_model):
        self.env = env
        self.device = env.device
        self.e0 = e0_model.to(self.device).eval()
        raw = env._get_observations()["policy"]
        self.obs = raw[:, :35]
        self.hist = raw[:, 35:455].reshape(-1, 12, 35)

    def actor_input(self) -> torch.Tensor:
        return torch.cat((self.obs, self.hist.flatten(1), self.env.g_step), dim=1)

    def active_mask(self) -> torch.Tensor:
        return self.env.stair_active_mask

    def anchor_mask(self) -> torch.Tensor:
        # Only lightly anchor near-riser low-speed states early in training; NEVER anchor approach or high speed!
        d1 = self.env.g_step_true[:, 0]
        return self.env.stair_active_mask & (d1 >= -0.10) & (d1 <= 0.18) & (self.env.command[:, 0] <= 1.15)

    def extra(self) -> torch.Tensor:
        e = self.env
        pos, yaw = e.local_pose()
        c, s = torch.cos(yaw)[:, None], torch.sin(yaw)[:, None]
        qx = pos[:, 0:1] + c * e.scanx[None, :] - s * e.scany[None, :]
        qy = pos[:, 1:2] + s * e.scanx[None, :] + c * e.scany[None, :]
        scan = (e.terrain_height(qx, qy) - pos[:, 2:3]).clamp(-1.0, 1.0)
        force = donor.tensor(e.scene["contacts"].data.net_forces_w)
        contacts = torch.stack([force[:, ids, 2].clamp_min(0.0).sum(1) for ids in e.contact_ids], dim=1) * 0.01
        return torch.cat((e.view.data.root_lin_vel_b, scan, contacts, e.g_step_true), dim=1)

    def set_stage(self, stage: int):
        levels = (0.0, 0.25, 0.50, 1.00)
        target = levels[min(stage, len(levels) - 1)]
        if abs(target - self.env.target_dr) > 1e-6:
            self.env.target_dr = target
            ids = torch.arange(self.env.num_envs, device=self.device)
            active = self.env.dr_eligible < target
            self.env.full_dr.apply_curriculum(ids, active)

    def statistics(self) -> dict:
        e = self.env
        c = e.nav_stats.tolist()
        return dict(
            columns=[
                "episodes",
                "falls_or_reg",
                "final_deck_success",
                "stage1_crossed",
                "step20_eps",
                "step20_succ",
                "rmul_eps",
                "rmul_succ",
            ],
            counts=c,
            group_population=torch.bincount(e.group, minlength=9).tolist(),
            full_dr_envs=int(e.full_dr.applied_dr.sum()),
            target_dr=float(e.target_dr),
            active_stair_envs=int(e.stair_active_mask.sum()),
            command_range=[float(e.command_after_settle[:, 0].min()), float(e.command_after_settle[:, 0].max())],
            stance_range=[float(e.course_height.min()), float(e.course_height.max())],
        )

    def step(self, stair_action: torch.Tensor):
        with torch.no_grad():
            e0_act = self.e0(self.obs)
        active = self.active_mask()
        applied = torch.where(active[:, None], stair_action, e0_act)
        raw, reward, term, timeout, _ = self.env.step(applied)
        frame = raw["policy"]
        self.obs = frame[:, :35]
        self.hist = frame[:, 35:455].reshape(-1, 12, 35)
        return self.obs, self.hist.flatten(1), reward, term | timeout

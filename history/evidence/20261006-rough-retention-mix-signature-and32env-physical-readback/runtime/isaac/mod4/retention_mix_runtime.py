"""Isolated candidate: flat retained skills plus gentle low-speed terrain.

No PPO or production controller is launched by importing this component.
The old plant, reward formulae, observations and physical DR remain unchanged.
"""
import copy
import hashlib
import numpy as np
import torch
import trimesh
from isaaclab.terrains import TerrainImporter
from isaaclab.managers import TerminationTermCfg
from directional_spin_runtime import DirectionalSpinCommand
from rough_intro_chunked_terrain import ChunkedTerrainImporter
from rough_intro_runtime import RoughIntroEnv, configure_intro
from rough_intro_reset import full_reset as rough_full_reset, query
from rolling_consistency import spin_contact_consistency
from retention_mix_math import (
    rough_mask, spawn_xy, route_timeout, flat_surface,
    assert_surface_separation, FLAT_SHIFT_X,
)
import mod4_task as task


def material_config(material):
    return {name: getattr(material, name) for name in (
        'static_friction', 'dynamic_friction', 'restitution',
        'friction_combine_mode', 'restitution_combine_mode',
    )}


class RetentionTerrainImporter(ChunkedTerrainImporter):
    def import_mesh(self, name, mesh):
        assert_surface_separation(mesh.vertices)
        # All rough triangles/winding and existing partitioning remain exact.
        super().import_mesh(name, mesh)
        rough_receipt = copy.deepcopy(self.exact_partition_receipt)
        vertices, faces = flat_surface()
        flat = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        before = self.cfg.physics_material
        try:
            # Use the actual original flat material, separately declared/read back.
            self.cfg.physics_material = copy.deepcopy(self.cfg.retained_flat_material)
            TerrainImporter.import_mesh(self, 'retained_flat', flat)
        finally:
            self.cfg.physics_material = before
        combined = hashlib.sha256()
        for first in range(0, len(mesh.faces), 25000):
            combined.update(np.asarray(mesh.vertices, dtype='<f4')[mesh.faces[first:first+25000]].tobytes())
        flat_bytes = np.asarray(vertices, dtype='<f4')[faces].tobytes()
        combined.update(flat_bytes)
        self.retention_geometry_receipt = dict(
            profile='flat75_gentle25_retention_candidate_v1',
            rough_partition=rough_receipt,
            flat_vertices_w=vertices.tolist(), flat_faces=faces.tolist(),
            flat_triangle_f32_sha256=hashlib.sha256(flat_bytes).hexdigest(),
            combined_authored_triangle_f32_sha256=combined.hexdigest(),
            expected_total_faces=len(mesh.faces)+2,
            flat_shift_x_m=FLAT_SHIFT_X, hidden_plane=False,
            rough_triangles_removed_or_simplified=False,
            flat_material=material_config(self.cfg.retained_flat_material),
            rough_material=material_config(before),
        )


class RetentionMixCommand(DirectionalSpinCommand):
    def _resample_command(self, env_ids):
        # Flat groups keep the original standing/straight/pure/world sampler.
        super()._resample_command(env_ids)
        ids = torch.as_tensor(env_ids, device=self.device, dtype=torch.long)
        terrain_ids = ids[rough_mask(ids)]
        self.is_pure_spin[terrain_ids] = False
        self.is_moving_spin[terrain_ids] = False
        self.is_transition_spin[terrain_ids] = False
        self.signed_yaw[terrain_ids] = 0.
        self.vel_command_b[terrain_ids] = 0.
        draws = torch.rand((len(terrain_ids), 2), device=self.device, generator=self._mode_rng)
        self.is_standing_env[terrain_ids] = draws[:, 0] < .2
        self.vel_command_b[terrain_ids, 0] = .6 * draws[:, 1] - .3
        self.vel_command_b[self.is_standing_env] = 0.


def mixed_reset(env, env_ids):
    ids = torch.arange(env.num_envs, device=env.device) if env_ids is None else env_ids
    if not len(ids):
        return
    terrain_ids = ids[rough_mask(ids)]
    flat_ids = ids[~rough_mask(ids)]
    if len(terrain_ids):
        rough_full_reset(env, terrain_ids)
    if len(flat_ids):
        # Preserve the actual old flat full-pose library and reset velocities.
        task.scut_rescue.consistent_reset(env, flat_ids)
        robot = env.scene['robot']
        root = robot.data.root_state_w[flat_ids].clone()
        root[:, :2] = spawn_xy(env.scene.env_origins, flat_ids)
        robot.write_root_state_to_sim(root, env_ids=flat_ids)
        if not hasattr(env, '_mod4_ground_z'):
            env._mod4_ground_z = torch.zeros(env.num_envs, device=env.device)
        env._mod4_ground_z[flat_ids] = 0.
        if not hasattr(env, '_rough_spawn_xy'):
            env._rough_spawn_xy = torch.zeros((env.num_envs, 2), device=env.device)
        env._rough_spawn_xy[flat_ids] = root[:, :2]
        if not hasattr(env, '_rough_probe_expected_q'):
            env._rough_probe_expected_q = torch.zeros((env.num_envs, 30), device=env.device)
        env._rough_probe_expected_q[flat_ids] = env._rescue_reset_q[flat_ids]
    env._rough_query_tick = None
    env._retention_reset_groups = dict(flat_ids=flat_ids.cpu().tolist(), rough_ids=terrain_ids.cpu().tolist())


def mixed_boundary_timeout(env):
    xy = env.scene['robot'].data.root_pos_w[:, :2]
    ids = torch.arange(env.num_envs, device=env.device)
    return route_timeout(xy, env._rough_spawn_xy, ids)


def mixed_rolling(env, speed_scale=.15, yaw_min=3.5, support_weight=.25):
    ids = torch.arange(env.num_envs, device=env.device)
    terrain = rough_mask(ids)
    command = env.command_manager.get_command('twist')
    if bool((command[terrain, 1:].abs() > 1e-6).any()):
        raise RuntimeError('Pure/moving yaw or lateral request escaped onto gentle terrain')
    cost = spin_contact_consistency(env, speed_scale, yaw_min, support_weight)
    if bool((cost[terrain] != 0.).any()):
        raise RuntimeError('Flat rolling proxy unexpectedly active on gentle terrain')
    return cost


def configure_retention(cfg):
    flat_material = copy.deepcopy(cfg.scene.ground.spawn.physics_material)
    saved_command = copy.deepcopy(cfg.commands.twist)
    recipe = configure_intro(cfg)
    cfg.scene.terrain.class_type = RetentionTerrainImporter
    cfg.scene.terrain.retained_flat_material = flat_material
    cfg.commands.twist = saved_command
    cfg.commands.twist.class_type = RetentionMixCommand
    cfg.events.consistent_start.func = mixed_reset
    cfg.rewards.spin_contact_consistency.func = mixed_rolling
    cfg.terminations.rough_route_boundary = TerminationTermCfg(func=mixed_boundary_timeout, time_out=True)
    recipe.update(
        profile='mod4_flat75_gentle25_retention_candidate_v1',
        assignment='env_id mod4 ==3 gentle; all other IDs declared finite flat Mesh',
        flat_fraction=.75, rough_fraction=.25,
        flat_command_mix=dict(stand=.1, straight=.4, pure=.3, world=.2),
        rough_command_mix=dict(stand=.2, body_vx=[-.3,.3], vy=0., yaw=0.),
        flat_route_limit_m=48., rough_route_limit_m=2.,
        reward_formulas_unchanged=True, terrain_pure_world_spin=False,
        source_selection='Exact23509 full old-skill anchor;23624 retained as separate rough candidate',
        repair_training_started=False,
    )
    return recipe


class RetentionMixEnv(RoughIntroEnv):
    """Reuse actual same-tick ground/termination/reward and contact lifecycle."""
    pass

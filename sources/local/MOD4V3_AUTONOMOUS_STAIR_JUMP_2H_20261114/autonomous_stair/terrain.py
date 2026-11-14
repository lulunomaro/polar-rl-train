"""Use saved Isaac Lab stair meshes, including unscaled target tiles."""
from pathlib import Path
import numpy as np
import torch
import trimesh

HEIGHTS = (0., .04, .08, .12, .165, .22)
COLUMNS = 8
EDGE = -2.9000000953674316
NEXT_EDGE = -1.4000000953674316


def saved_stair(difficulty, cfg):
    level = min(int(difficulty * len(HEIGHTS)), len(HEIGHTS) - 1)
    height = HEIGHTS[level]
    name = 'r03_c00.npz' if level == 5 else 'r00_c00.npz'
    with np.load(Path(__file__).parents[1] / 'terrain' / name) as data:
        vertices, faces = data['vertices'].copy(), data['faces'].copy()
    if level < 4:
        vertices[:, 2] *= height / .165
    vertices[:, :2] += 4.5
    return [trimesh.Trimesh(vertices=vertices, faces=faces, process=False)], np.array([4.5, 4.5, 0.])


def configuration(meta, bank, n, seed):
    from isaaclab.terrains import TerrainGeneratorCfg, TerrainImporter, SubTerrainBaseCfg
    from isaaclab.sensors import RayCasterCfg, patterns
    from mod4v3_ppo_v1.scut_flat_env import configuration as base_configuration
    cfg = base_configuration(meta, bank, n, seed, terrain_selection='flat')
    cfg.episode_length_s = 8.
    cfg.scene.terrain.terrain_generator = TerrainGeneratorCfg(
        seed=seed, curriculum=True, size=(9., 9.), border_width=0.,
        num_rows=len(HEIGHTS), num_cols=COLUMNS, color_scheme='none',
        difficulty_range=(0., 1.), use_cache=False,
        sub_terrains={'saved_stair': SubTerrainBaseCfg(function=saved_stair, proportion=1.)})
    cfg.scene.terrain.max_init_terrain_level = 0
    cfg.scene.terrain_scan = RayCasterCfg(
        prim_path='{ENV_REGEX_NS}/Robot/links/base_link',
        offset=RayCasterCfg.OffsetCfg(pos=(1.2, 0., 5.)), ray_alignment='yaw',
        pattern_cfg=patterns.GridPatternCfg(resolution=.05, size=(2.4, 0.)),
        mesh_prim_paths=['/World/ground/terrain'], max_distance=20., update_period=.02)

    def origins(self, num_envs, all_origins):
        self.max_terrain_level = all_origins.shape[0]
        self.terrain_levels = torch.zeros(num_envs, device=self.device, dtype=torch.long)
        self.terrain_types = torch.arange(num_envs, device=self.device) % COLUMNS
        # Spread filtered robot clones over tiles; reset adds separate approach lanes.
        return all_origins[self.terrain_levels, self.terrain_types].clone()

    TerrainImporter._compute_env_origins_curriculum = origins
    return cfg

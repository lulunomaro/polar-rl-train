"""Flat lanes spread over small shared planes to avoid overlapping aggregates."""
import torch

COLUMNS = 16
ROWS = 4


def configuration(meta, bank, n, seed):
    from isaaclab.terrains import TerrainGeneratorCfg, TerrainImporter, MeshPlaneTerrainCfg
    from mod4v3_ppo_v1.scut_flat_env import configuration as original
    cfg = original(meta, bank, n, seed, terrain_selection='flat')
    cfg.episode_length_s = 6.
    cfg.scene.terrain.terrain_generator = TerrainGeneratorCfg(
        seed=seed, curriculum=True, size=(12., 10.), border_width=2.,
        num_rows=ROWS, num_cols=COLUMNS, color_scheme='none', use_cache=False,
        sub_terrains={'flat': MeshPlaneTerrainCfg(proportion=1.)})
    cfg.scene.terrain.max_init_terrain_level = ROWS - 1

    def origins(self, num_envs, all_origins):
        ids = torch.arange(num_envs, device=self.device)
        self.max_terrain_level = all_origins.shape[0]
        self.terrain_levels = torch.div(ids, COLUMNS, rounding_mode='floor') % ROWS
        self.terrain_types = ids % COLUMNS
        return all_origins[self.terrain_levels, self.terrain_types].clone()

    TerrainImporter._compute_env_origins_curriculum = origins
    return cfg

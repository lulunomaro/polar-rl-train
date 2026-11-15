"""Flat-only Isaac Lab terrain for the one-hour SCUT flat run."""
def generator():
    import isaaclab.terrains as t
    from isaaclab.terrains.config.rough import ROUGH_TERRAINS_CFG
    cfg = ROUGH_TERRAINS_CFG.copy()
    cfg.seed = 9137
    cfg.num_rows = 4
    cfg.num_cols = 20
    cfg.curriculum = False
    cfg.difficulty_range = (0.0, 0.0)
    cfg.vertical_scale = 0.0
    cfg.sub_terrains = {'flat': t.MeshPlaneTerrainCfg(proportion=1.0)}
    return cfg

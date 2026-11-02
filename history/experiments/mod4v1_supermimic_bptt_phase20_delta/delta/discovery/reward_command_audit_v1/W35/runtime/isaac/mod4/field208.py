"""Deferred SDK adapter: reference the original complete CAD arena unchanged.

No NPZ/USD is read by importing this source. Actual target geometry reads require
root's separate typed task. The local CPU fixture never calls these SDK paths.
"""
from pathlib import Path
import json, math
from course_math208 import layout_origins, COLLISION_USDC_SHA, COLLISION_NPZ_SHA


def checked_assets(root, receipt):
    root = Path(root).resolve()
    if receipt.get('actual_postcopy_fullSHA_verified') is not True:
        raise ValueError('Need actual root-owned binary installation receipt')
    expected = {'assets/arena_collision.usdc': COLLISION_USDC_SHA,
                'data/arena_collision.npz': COLLISION_NPZ_SHA}
    rows = {r['relative']: r for r in receipt['files']}
    for relative, digest in expected.items():
        row = rows[relative]; path = root / relative
        if row['SHA'] != digest or path.stat().st_size != row['bytes']:
            raise ValueError('Wrong original CAD asset: ' + relative)
    return root


def make_terrain_cfg(root, receipt, num_envs, output):
    """Create only a new layout, preserving source collision coordinates/shape."""
    import torch
    from pxr import Usd, UsdGeom, Gf
    from isaaclab.terrains import TerrainImporter, TerrainImporterCfg
    from isaaclab.utils.configclass import configclass
    root = checked_assets(root, receipt); output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    origins = layout_origins(num_envs)
    path = output / 'full_RM70_layout.usda'
    stage = Usd.Stage.CreateNew(str(path)); UsdGeom.SetStageUpAxis(stage, 'Z')
    UsdGeom.SetStageMetersPerUnit(stage, 1.)
    world = UsdGeom.Xform.Define(stage, '/Terrain'); stage.SetDefaultPrim(world.GetPrim())
    for index, origin in enumerate(origins):
        obj = UsdGeom.Xform.Define(stage, '/Terrain/env_' + str(index).zfill(5))
        obj.GetPrim().GetReferences().AddReference(str(root / 'assets/arena_collision.usdc'))
        obj.AddTranslateOp().Set(Gf.Vec3d(*origin)); obj.GetPrim().SetInstanceable(True)
    stage.GetRootLayer().Save()
    (output / 'layout.json').write_text(json.dumps(dict(num_envs=num_envs, origins=origins,
        original_collision_SHA=COLLISION_USDC_SHA, translation_only=True,
        source_slope_and_all_three_coordinates_retained=True), indent=2), encoding='utf8')

    class OriginalArenaImporter208(TerrainImporter):
        def __init__(self, cfg):
            super().__init__(cfg)
            self.env_origins = torch.tensor(origins, device=self.device, dtype=torch.float32)
            self.terrain_origins = None
            self.retention_assignment_sha = COLLISION_USDC_SHA
            self.retention_radius = None  # no old G3 plane-cell certification in this course
            self.original_arena_asset_root208 = str(root)
            self.original_arena_receipt208 = receipt

    @configclass
    class OriginalArenaCfg208(TerrainImporterCfg):
        class_type = OriginalArenaImporter208

    return OriginalArenaCfg208(prim_path='/World/ground', terrain_type='usd',
        usd_path=str(path), num_envs=num_envs, collision_group=-1,
        env_spacing=34., debug_vis=False)


class SharedQuery208:
    """Same original static NPZ as original USD, translated per environment."""
    def __init__(self, env):
        import numpy as np
        from isaaclab.utils.warp import convert_to_warp_mesh, raycast_mesh
        terrain = env.scene.terrain
        root = checked_assets(terrain.original_arena_asset_root208,
                              terrain.original_arena_receipt208)
        with np.load(root / 'data/arena_collision.npz') as data:
            self.mesh = convert_to_warp_mesh(data['vertices'], data['faces'], device=str(env.device))
        self.origins = env.scene.env_origins
        self.cast_mesh = raycast_mesh
        self.ceiling208 = 4.  # ray start only, never a support plane or robot reset height

    def cast(self, starts, max_distance=10., env_ids=None):
        import torch
        origins = self.origins if env_ids is None else self.origins[env_ids]
        if starts.ndim != 3 or starts.shape[-1] != 3 or len(starts) != len(origins):
            raise ValueError('Explicit environment IDs required for partial terrain query')
        directions = torch.zeros_like(starts); directions[..., 2] = -1.
        hits, distance, normal, face = self.cast_mesh((starts - origins[:, None]).contiguous(),
            directions, self.mesh, max_dist=float(max_distance), return_distance=True,
            return_normal=True, return_face_id=True)
        return dict(height=hits[..., 2] + origins[:, None, 2], normal=normal,
                    hit=torch.isfinite(distance), face_id=face)

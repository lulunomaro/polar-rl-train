"""Use the published SCUT inverse-stair generator and report actual traversal.

No jump state machine or extra reward is introduced. The robot, its physics,
and DR remain MOD4; the generator parameters come from the pinned saved YAML.
"""
from copy import deepcopy
from functools import lru_cache
import torch
from .config import read_yaml
from .math_ops import euler_xyz_from_quat

BRANCH = 'inv_stair_slope_for_rm_mid'
MESH = '/World/ground/terrain/mesh'


def recipe():
    raw = read_yaml('trained_env')
    return deepcopy(raw['terrain']['terrain_generator']), deepcopy(
        raw['terrain']['terrain_generator']['sub_terrains'][BRANCH])


def metadata():
    generator, stair = recipe()
    return dict(kind='SCUT_SAVED_INVERSE_STAIR_BRANCH', branch=BRANCH,
        generator_function=stair['function'], step_height_range_m=stair['step_height_range'],
        step_width_m=stair['step_width'], centre_width_m=stair['platform_width'],
        size_m=stair['size'], border_width_m=stair['border_width'],
        horizontal_scale=stair['horizontal_scale'], vertical_scale=stair['vertical_scale'],
        difficulty_range=generator['difficulty_range'], rows=generator['num_rows'],
        columns=generator['num_cols'], curriculum_mesh=generator['curriculum'],
        origin='Original generator origin, including its height; not centre-bottom shifted',
        scope='Only the saved inverse-stair branch; other rough tasks omitted',
        height_command_range_m=list(read_yaml('trained_env')['height_range']), root_height_above_origin_m=.38,
        requires_270mm=False, requires_first_flight=False,
        physical_MOD4_model_and_DR_preserved=True)


@lru_cache(maxsize=1)
def boundary_limits():
    raw = read_yaml('trained_env')
    cfg = raw['rough_terrain_boundary_reset_cfg']
    if not cfg['enabled']:
        return None
    generator = raw['terrain']['terrain_generator']
    half_x = .5*generator['num_rows']*generator['size'][0]
    half_y = .5*generator['num_cols']*generator['size'][1]
    if not cfg['use_inner_terrain_area']:
        half_x += generator['border_width']
        half_y += generator['border_width']
    margin = max(float(cfg['margin']), 0.)
    return max(half_x-margin, 0.), max(half_y-margin, 0.)


def boundary_timeout(root_pos_w):
    """V14 env.py541-566, using the saved enabled boundary-reset settings."""
    limits = boundary_limits()
    if limits is None:
        return torch.zeros(len(root_pos_w), dtype=torch.bool, device=root_pos_w.device)
    return ((root_pos_w[:, 0].abs() > limits[0]) |
            (root_pos_w[:, 1].abs() > limits[1]))


def terrain_cfg(seed):
    from isaaclab.terrains import TerrainImporter, TerrainImporterCfg, TerrainGeneratorCfg
    from isaaclab.terrains.height_field.hf_terrains_cfg import HfPyramidStairsTerrainCfg
    from isaaclab.sim import RigidBodyMaterialCfg
    generator, stair = recipe()
    sub = HfPyramidStairsTerrainCfg(**{k: v for k, v in stair.items() if k != 'function'})
    sub.proportion = 1.
    selected = {k: generator[k] for k in ('curriculum', 'size', 'border_width', 'border_height',
        'num_rows', 'num_cols', 'color_scheme', 'horizontal_scale', 'vertical_scale',
        'slope_threshold', 'difficulty_range', 'use_cache')}
    gen = TerrainGeneratorCfg(seed=seed, sub_terrains={BRANCH: sub}, **selected)
    class RecordedTerrain(TerrainImporter):
        def import_mesh(self, name, mesh):
            self.scut_vertices = mesh.vertices.copy()
            self.scut_faces = mesh.faces.copy()
            return super().import_mesh(name, mesh)

        def __init__(self, cfg):
            super().__init__(cfg)
            self.scut_stair_branch = BRANCH
    return TerrainImporterCfg(class_type=RecordedTerrain, prim_path='/World/ground',
        terrain_type='generator', terrain_generator=gen, use_terrain_origins=True,
        collision_group=-1, max_init_terrain_level=None, debug_vis=False,
        physics_material=RigidBodyMaterialCfg(static_friction=1., dynamic_friction=1.,
            restitution=0., friction_combine_mode='multiply', restitution_combine_mode='multiply'))


class StairTraversal:
    """Measure raised-surface support after both wheels leave the birth platform.

These are reported locomotion metrics, not a claim of first-flight270mm success.
Stability permits horizontal travel; SCUT commands are locomotion commands.
"""
    def __init__(self, n, device):
        self.birth = torch.full((n, 3), torch.nan, device=device)
        self.birth_support = torch.full((n, 2), torch.nan, device=device)
        self.success = torch.zeros(n, dtype=torch.bool, device=device)
        self.wholeclear = self.success.clone()
        self.leading = self.success.clone()
        self.stable_peak = torch.zeros(n, dtype=torch.long, device=device)
        self.support_peak = self.stable_peak.clone()
        self.stable_count = self.stable_peak.clone()
        self.support_count = self.stable_peak.clone()
        self.max_rise = torch.zeros(n, device=device)

    def reset(self, ids):
        self.birth[ids] = torch.nan
        self.birth_support[ids] = torch.nan
        for name in ('success', 'wholeclear', 'leading', 'stable_peak', 'support_peak',
                     'stable_count', 'support_count', 'max_rise'):
            getattr(self, name)[ids] = 0

    def update(self, wheel_pos, support_height, support_force, nonwheel, velocity, root_quat, root_pos, ground_height):
        unset = torch.isnan(self.birth[:, 0])
        self.birth[unset] = root_pos[unset]
        # The first endpoint can be airborne. Its downward ray gives the birth
        # surface even when the contact manifold has no support point yet.
        self.birth_support[unset] = ground_height[unset, None].expand(-1, 2)
        # Use actual vertical manifold support and movement beyond the original
        # central1m platform. A narrow tread need not fit a whole tire footprint.
        travel = (wheel_pos[..., :2]-self.birth[:, None, :2]).abs().amax(-1)
        rise = support_height-self.birth_support
        supported = (support_force > 1) & (rise >= .005-1.e-4) & (travel > .5)
        any_up, both_up = supported.any(-1), supported.all(-1)
        self.leading |= any_up
        self.wholeclear |= both_up
        self.max_rise = torch.maximum(self.max_rise, torch.where(supported, rise, 0.).amax(-1))
        self.support_count = torch.where(both_up, self.support_count+1, 0)
        roll, pitch, _ = euler_xyz_from_quat(root_quat)
        recovered = both_up & (nonwheel <= 1) & (abs(roll) <= torch.pi/18) & (
            abs(pitch) <= torch.pi/18) & (abs(velocity[:, 2]) <= .1)
        self.stable_count = torch.where(recovered, self.stable_count+1, 0)
        self.stable_peak = torch.maximum(self.stable_peak, self.stable_count)
        self.support_peak = torch.maximum(self.support_peak, self.support_count)
        self.success |= self.stable_count >= 200

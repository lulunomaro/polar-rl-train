"""Isaac Lab 2.x terrain integration. Import AFTER AppLauncher starts Isaac Sim."""
from pathlib import Path
import json,sys
import torch
from isaaclab.terrains import TerrainImporter,TerrainImporterCfg
from isaaclab.utils import configclass

ROOT=Path(__file__).resolve().parents[1]

class RMUC2026TerrainImporter(TerrainImporter):
    def __init__(self,cfg):
        self.layout=json.loads(Path(cfg.layout_manifest).read_text(encoding='utf8'))
        if cfg.num_envs!=self.layout['num_envs']:
            raise ValueError('Map instance count does not match num_envs. Call make_terrain_cfg(num_envs=...).')
        super().__init__(cfg)
        # The arena grid is rectangular (34 x 20 m), so Isaac's square default
        # origin grid is WRONG for this asset. This is also scene.env_origins.
        self.env_origins=torch.tensor(self.layout['origins'],device=self.device,dtype=torch.float32)
        self.terrain_origins=None
        self.set_debug_vis(cfg.debug_vis)

@configclass
class RMUC2026TerrainCfg(TerrainImporterCfg):
    class_type=RMUC2026TerrainImporter
    prim_path='/World/RMUC2026'
    terrain_type='usd'
    collision_group=-1
    env_spacing=34.
    layout_manifest: str=''
    debug_vis=False

def make_terrain_cfg(num_envs=1024,prim_path='/World/RMUC2026'):
    usd=ROOT/f'maps/arena_{num_envs}.usda'
    manifest=usd.with_suffix('.json')
    if not usd.exists() or not manifest.exists():
        sys.path.insert(0,str(ROOT/'tools'))
        from build_layout import build_layout
        build_layout(num_envs)
    return RMUC2026TerrainCfg(num_envs=num_envs,prim_path=prim_path,usd_path=str(usd),layout_manifest=str(manifest))

def route_reset_states(terrain,route_indices,base_height_m,device=None):
    """Root states [pos, quat(wxyz), linear/angular velocity] for a closed pose.

    base_height_m must match the ROBOT's base-to-wheel-ground reset geometry.
    It is not the chassis overall height. Reset joint states using the robot's
    own closed-loop reset function as well; this helper only places its root.
    """
    routes=json.loads((ROOT/'data/routes.json').read_text(encoding='utf8'))
    dev=terrain.device if device is None else device
    ids=torch.as_tensor(route_indices,dtype=torch.long,device=dev)
    if ids.ndim!=1 or len(ids)!=len(terrain.env_origins):
        raise ValueError('Provide one route index per environment.')
    xyz=torch.tensor([r['spawn_ground_m'] for r in routes],device=dev,dtype=torch.float32)[ids]
    yaw=torch.tensor([r['spawn_yaw_rad'] for r in routes],device=dev,dtype=torch.float32)[ids]
    state=torch.zeros((len(ids),13),device=dev)
    state[:,:3]=xyz+terrain.env_origins
    state[:,2]+=base_height_m
    state[:,3]=torch.cos(yaw/2);state[:,6]=torch.sin(yaw/2)
    return state

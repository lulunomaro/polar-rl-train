"""Small isolated terrain audit: authored mesh, Warp and PhysX downward rays.

No policy, robot, PPO, budget mutation, or change to the active training task.
The reduced 2x5 grid is a diagnostic, not the selected production curriculum.
"""
import argparse
import json
from pathlib import Path
import time
import faulthandler
faulthandler.enable()

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import numpy as np
import torch
import omni.physx
from isaaclab.sim import SimulationCfg, SimulationContext
from isaaclab_physx.physics import PhysxCfg
from isaaclab.terrains import TerrainImporter
from rough_recipe import make_terrain_cfg
from rough_ground import AuthoredTerrainRaycast, VerticalMeshOracle


def run():
    print('TERRAIN_PROBE_MILESTONE simulation_context', flush=True)
    sim = SimulationContext(SimulationCfg(dt=.005, device=args.device,
        enable_scene_query_support=True,
        physics=PhysxCfg(enable_scene_query_support=True, enable_external_forces_every_iteration=True)))
    cfg, receipt = make_terrain_cfg(5, profile='intro_v1')
    cfg.terrain_generator.num_rows = 2
    cfg.terrain_generator.num_cols = 5
    cfg.terrain_generator.use_cache = False
    receipt['probe_only_grid'] = [2, 5]
    terrain = TerrainImporter(cfg)
    print('TERRAIN_PROBE_MILESTONE imported', flush=True)
    sim.reset()
    print('TERRAIN_PROBE_MILESTONE reset', flush=True)
    for _ in range(3):
        sim.step(render=False)
    print('TERRAIN_PROBE_MILESTONE stepped', flush=True)
    stage = sim.stage
    query = AuthoredTerrainRaycast(stage, sim.device)
    print('TERRAIN_PROBE_MILESTONE warp_mesh', flush=True)
    oracle = VerticalMeshOracle(query.geometry)
    # Test deterministic points in all tiles, including off-platform patches.
    origins = terrain.terrain_origins.detach().cpu().numpy().reshape(-1, 3)
    rng = np.random.default_rng(20261002)
    rays = np.repeat(origins, 8, axis=0)
    rays[:, :2] += rng.uniform(-2.7, 2.7, (len(rays), 2))
    rays[:, 2] = float(query.geometry.vertices[:, 2].max()) + 2.
    low, high = query.geometry.vertices.min(0), query.geometry.vertices.max(0)
    rays = np.concatenate([rays, [[high[0]+3, high[1]+3, rays[0, 2]]]])
    reference = oracle.cast(rays, 10.)
    print('TERRAIN_PROBE_MILESTONE cpu_reference', flush=True)
    measured = query.cast(torch.as_tensor(rays, device=sim.device, dtype=torch.float32)[None], 10.)
    wp_hit = measured['hit'][0].cpu().numpy()
    wp_z = measured['height'][0].cpu().numpy()
    physx = omni.physx.get_physx_scene_query_interface()
    px_hit = np.zeros(len(rays), bool)
    px_z = np.full(len(rays), np.nan)
    normals, paths = [], []
    for i, ray in enumerate(rays):
        hit = physx.raycast_closest(tuple(float(x) for x in ray), (0., 0., -1.), 10.)
        px_hit[i] = bool(hit.get('hit', False))
        if px_hit[i]:
            px_z[i] = float(hit['position'][2])
            paths.append(str(hit.get('collision', hit.get('rigidBody', ''))))
            normals.append(list(hit['normal']))
    common = reference['hit'] & wp_hit & px_hit
    wp_err = float(np.max(np.abs(wp_z[common]-reference['height'][common]))) if common.any() else float('inf')
    px_err = float(np.max(np.abs(px_z[common]-reference['height'][common]))) if common.any() else float('inf')
    hit_match = bool(np.array_equal(wp_hit, reference['hit']) and np.array_equal(px_hit, reference['hit']))
    terrain_only = bool(paths and all(path.startswith('/World/ground') for path in paths))
    result = dict(
        stage='ISOLATED_TERRAIN_RUNTIME_RAY_AUDIT', created_epoch=time.time(),
        pass_=hit_match and terrain_only and wp_err < 2e-4 and px_err < 2e-4,
        recipe=receipt, geometry=query.geometry.receipt(), rays=len(rays), hits=int(common.sum()),
        miss_semantics_match=hit_match, terrain_only_paths=terrain_only,
        warp_cpu_max_height_difference_m=wp_err, physx_cpu_max_height_difference_m=px_err,
        physx_paths=sorted(set(paths)), upward_normal_min_z=min((n[2] for n in normals), default=None),
        environment_origins=terrain.env_origins.cpu().tolist(), terrain_origins=origins.tolist(),
        production_modified=False, ppo_started=False, robot_reset_verified=False,
        scope='Geometry/ray query only; not contact, reset, policy or Rough skill acceptance',
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('TERRAIN_PROBE_RESULT', json.dumps({k:v for k,v in result.items() if k not in ['geometry','recipe','environment_origins','terrain_origins']}), flush=True)
    if not result['pass_']:
        raise RuntimeError('Terrain ray audit failed; candidate must not be deployed')


try:
    run()
except Exception as error:
    import traceback
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix('.error.json').write_text(json.dumps(dict(
        error=repr(error), traceback=traceback.format_exc(), production_modified=False)), encoding='utf-8')
    traceback.print_exc()
    raise
finally:
    app.close()

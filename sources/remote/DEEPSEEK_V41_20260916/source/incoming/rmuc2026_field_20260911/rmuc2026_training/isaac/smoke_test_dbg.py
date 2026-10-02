"""Target-machine map collision test and 1024-environment throughput measurement.

This uses one dynamic contact probe per environment, not a robot or PPO policy.
Run from Isaac Lab: ./isaaclab.sh -p /path/to/isaac/smoke_test.py --headless --num-envs 1024
"""
import argparse,time,json,sys
from pathlib import Path
from isaaclab.app import AppLauncher
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--num-envs',type=int,default=1024)
ap.add_argument('--steps',type=int,default=500)
ap.add_argument('--output',type=Path)
AppLauncher.add_app_launcher_args(ap)
args=ap.parse_args();app=AppLauncher(args).app
import torch
import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObjectCfg
from isaaclab.scene import InteractiveScene,InteractiveSceneCfg
from isaaclab.utils import configclass
from terrain_cfg import make_terrain_cfg,route_reset_states,ROOT

@configclass
class ProbeSceneCfg(InteractiveSceneCfg):
    terrain=make_terrain_cfg(args.num_envs)
    probe=RigidObjectCfg(
        prim_path='{ENV_REGEX_NS}/Probe',
        spawn=sim_utils.SphereCfg(radius=.0625,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=1.),
            collision_props=sim_utils.CollisionPropertiesCfg(contact_offset=.002,rest_offset=0.),
            physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=.9,dynamic_friction=.8,restitution=0.),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(.95,.7,.15))),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0,0,1.)))

def main():
    if args.steps<100:raise ValueError('Use at least 100 measured steps for settling/collision validation.')
    sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=.005,device=args.device))
    started=time.perf_counter()
    scene=InteractiveScene(ProbeSceneCfg(num_envs=args.num_envs,env_spacing=34.,replicate_physics=True))
    sim.reset()
    origin=scene.env_origins[0].cpu().numpy()
    sim.set_camera_view(origin+[15.,-15.,13.],origin+[0.,0.,0.])
    probe=scene['probe']
    routes=torch.zeros(args.num_envs,dtype=torch.long,device=scene.device)
    states=route_reset_states(scene.terrain,routes,.0625+.08)
    probe.write_root_state_to_sim(states);scene.reset()
    setup_s=time.perf_counter()-started
    dt=sim.get_physics_dt()
    for _ in range(100):
        scene.write_data_to_sim();sim.step(render=not args.headless);scene.update(dt)
    if str(scene.device).startswith('cuda'):
        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    started=time.perf_counter()
    for _ in range(args.steps):
        scene.write_data_to_sim();sim.step(render=not args.headless);scene.update(dt)
    if str(scene.device).startswith('cuda'):torch.cuda.synchronize()
    duration=time.perf_counter()-started
    p=probe.data.root_pos_w-scene.env_origins
    route=json.loads((ROOT/'data/routes.json').read_text(encoding='utf8'))[0]
    n=torch.tensor(route['spawn_surface_normal'],device=scene.device)
    ground=torch.tensor(route['spawn_ground_m'],device=scene.device)
    # Signed distance to the measured flat-start CAD plane, including floor slope.
    distance=(p-ground)@n
    error=(distance-.0625).abs()
    passed=bool(torch.isfinite(probe.data.root_state_w).all() and torch.all(error<.012))
    ray_checks=[]
    from omni.physx import get_physx_scene_query_interface
    query=get_physx_scene_query_interface()
    checks=json.loads((ROOT/'data/runtime_ray_checks.json').read_text(encoding='utf8'))
    for check in checks:
        start=[float(origin[i]+check['origin_m'][i]) for i in range(3)]
        result=query.raycast_closest(tuple(start),tuple(check['direction']),check['max_distance_m'])
        print("[raydbg]", check["id"], [round(v, 2) for v in start], check["direction"], "->", result, flush=True)
        hit=bool(result.get('hit',False))
        err=abs(float(result.get('distance',1e6))-check['expected_distance_m'])
        ok=hit and err<check['tolerance_m']
        ray_checks.append(dict(id=check['id'],passed=ok,hit=hit,distance_error_m=err))
        passed=passed and ok
    # Query every environment through the shared mesh. This catches origin bugs
    # in terrain observations as well as testing the target Warp helper API.
    from shared_raycast import SharedTerrainRaycast
    sensor=SharedTerrainRaycast(scene.env_origins)
    starts=torch.tensor([c['origin_m'] for c in checks],device=scene.device)
    directions=torch.tensor([c['direction'] for c in checks],device=scene.device)
    rays=sensor.cast(starts[None,:,:]+scene.env_origins[:,None,:],
                     directions[None,:,:].expand(args.num_envs,-1,-1),max_distance=5.)
    expected=torch.tensor([c['expected_distance_m'] for c in checks],device=scene.device)
    ray_error=(rays['distance']-expected[None,:]).abs()
    shared_ray_ok=bool(rays['hit'].all() and (ray_error<.008).all())
    passed=passed and shared_ray_ok
    report=dict(status='PASS_RUNTIME_MAP' if passed else 'FAIL_RUNTIME_MAP',num_envs=args.num_envs,
                steps=args.steps,physics_dt_s=dt,setup_seconds=setup_s,step_wall_seconds=duration,
                environment_steps_per_second=args.num_envs*args.steps/duration,
                physics_steps_per_second=args.steps/duration,max_probe_contact_error_m=float(error.max()),
                mean_probe_contact_error_m=float(error.mean()),runtime_ray_checks=ray_checks,
                shared_mesh_raycast_passed=shared_ray_ok,shared_rays_checked=args.num_envs*len(checks),
                shared_mesh_raycast_max_error_m=float(ray_error.max()),
                torch_peak_allocated_bytes=torch.cuda.max_memory_allocated() if str(scene.device).startswith('cuda') else None,
                memory_note='Torch allocation is not total Isaac/PhysX/render GPU memory; also record nvidia-smi.',
                scope='Static map plus 1 sphere per environment. Does not validate the robot articulation, training convergence, or 1024 robot throughput.')
    path=args.output or ROOT/'reports'/f'isaac_runtime_{args.num_envs}.json'
    path.write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2),flush=True)
    if not passed:raise RuntimeError('Map runtime verification failed. Inspect the saved report before training.')

try:main()
finally:app.close()

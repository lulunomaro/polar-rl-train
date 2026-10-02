"""Which layer eats the PhysX ray query: the arena's instanced USD, or the call itself?

Spawns a plain cube next to the arena and casts identical downward rays at both.
"""
import argparse, sys
from pathlib import Path
from isaaclab.app import AppLauncher
ap = argparse.ArgumentParser(); ap.add_argument("--steps", type=int, default=40)
AppLauncher.add_app_launcher_args(ap); args = ap.parse_args(); app = AppLauncher(args).app
import torch  # noqa: E402
import isaaclab.sim as sim_utils  # noqa: E402
from isaaclab.assets import RigidObjectCfg  # noqa: E402
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg  # noqa: E402
from isaaclab.utils import configclass  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from terrain_cfg import make_terrain_cfg  # noqa: E402


@configclass
class ProbeSceneCfg(InteractiveSceneCfg):
    terrain = make_terrain_cfg(1)
    cue = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Cue",
        spawn=sim_utils.CuboidCfg(size=(1.0, 1.0, 0.4),
                                  rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True),
                                  collision_props=sim_utils.CollisionPropertiesCfg(),
                                  visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.9, 0.2, 0.2))),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.0, 0.0, 0.6)))


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=0.005, device="cuda:0"))
    scene = InteractiveScene(ProbeSceneCfg(num_envs=1, env_spacing=34.0, replicate_physics=True))
    sim.reset()
    for _ in range(args.steps):
        sim.step()
        scene.update(0.005)
    from omni.physx import get_physx_scene_query_interface
    q = get_physx_scene_query_interface()
    cues = {
        "cue_cube(0,0,z=0.6)":          (0.0, 0.0, 1.8),
        "arena_floor(-1.8,0)":          (-1.8, 0.0, 1.8),
        "arena_floor(7.54,6.45)":       (7.54, 6.45, 1.8),
    }
    for name, start in cues.items():
        for kw in ({}, {"both_sides": True}):
            try:
                r = q.raycast_closest(start, (0.0, 0.0, -1.0), 4.0, **kw)
            except Exception as exc:
                r = "EXC %r" % (exc,)
            print("[q] %-24s %-18s -> %s" % (name, kw, r), flush=True)
    origins = scene.env_origins
    print("[q] env_origins[0] =", [round(float(v), 2) for v in origins[0]], flush=True)
    sim.clear_instance()


if __name__ == "__main__":
    main(); app.close()

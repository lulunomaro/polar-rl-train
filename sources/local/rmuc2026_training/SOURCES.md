# Sources and interface scope

Geometry: user-provided `RMUC2026_V2.0.0.stp`, SHA-256 in `reports/source.json`.
Source metadata names the finals assembly `00_RMUC2026_FINALS_ASM`. Source geometry takes precedence over schematic rulebook dimensions in this conversion. We have not certified that this supplied CAD matches any later rules revision.

Official primary sources consulted for integration, pinned where possible:

- [Isaac Lab v2.3.0 TerrainImporter](https://github.com/isaac-sim/IsaacLab/blob/v2.3.0/source/isaaclab/isaaclab/terrains/terrain_importer.py): USD spawning and default origin setup.
- [Isaac Lab v2.3.0 InteractiveScene](https://github.com/isaac-sim/IsaacLab/blob/v2.3.0/source/isaaclab/isaaclab/scene/interactive_scene.py): terrain construction and `scene.env_origins` delegation to terrain.
- [Isaac Lab v2.3.0 RayCaster](https://github.com/isaac-sim/IsaacLab/blob/v2.3.0/source/isaaclab/isaaclab/sensors/ray_caster/ray_caster.py): first-matching static mesh behavior. The packaged shared-query wrapper avoids this hierarchy assumption.
- [Isaac Lab v2.3.0 Warp helpers](https://github.com/isaac-sim/IsaacLab/blob/v2.3.0/source/isaaclab/isaaclab/utils/warp/ops.py): `convert_to_warp_mesh` and `raycast_mesh` public APIs used by the wrapper.
- [NVIDIA PhysX Python scene queries](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/extensions/runtime/source/omni.physx/docs/api/python.html): target-machine `raycast_closest` interface.
- [Isaac Lab scene tutorial](https://isaac-sim.github.io/IsaacLab/v2.3.0/source/tutorials/02_scene/create_scene.html): AppLauncher and InteractiveScene lifecycle.

No third-party source implementation is vendored. Third-party runtime packages retain their respective licenses. Geometry is supplied by the user; this package does not grant new redistribution rights to that CAD. The adapter scripts are generated for this delivery.

API review is not a substitute for execution. Local validation used usd-core, NumPy, trimesh and Torch; Isaac/PhysX/Warp execution is reserved for the supplied target-machine smoke test.

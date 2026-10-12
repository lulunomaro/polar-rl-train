"""Isolated memory candidate: custom authored-Warp queries remain authoritative."""
from e1_terrain_runtime import configure_intro as original_configure_intro

def configure_intro(cfg):
    recipe=original_configure_intro(cfg)
    # E1 uses its own authored-mesh Warp BVH, not PhysX scene query APIs.
    # Contact solving and all authored colliders remain enabled and unchanged.
    cfg.sim.enable_scene_query_support=False
    cfg.sim.physx.enable_scene_query_support=False
    recipe['resource_candidate']={
        'unused_PhysX_scene_query_support':False,
        'actual_authored_Warp_ground_query_retained':True,
        'collision_geometry_and_contact_solving_unchanged':True,
        'not_yet_native20k_or_PPO_accepted':True,
    }
    return recipe

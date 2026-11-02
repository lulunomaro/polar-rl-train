"""Explicit independent full RM70 lesson; original physical terms/reward retained."""
import os, json
from pathlib import Path
import torch
from course_math208 import COURSE_X, COURSE_Y, COURSE_PROFILE


def boundary208(env):
    xy = env.scene['robot'].data.root_pos_w[:, :2] - env.scene.env_origins[:, :2]
    return (xy[:, 0] < COURSE_X[0]) | (xy[:, 0] > COURSE_X[1]) | (
        xy[:, 1] < COURSE_Y[0]) | (xy[:, 1] > COURSE_Y[1])


def configure208(cfg):
    from e1_scene_query_resource import configure_intro
    from field214 import make_terrain_cfg
    from command208_v3 import RM70Command208
    from reset208_v3 import full_reset
    from terrain208_v3 import inactive_rolling
    recipe = configure_intro(cfg)
    # Freeze every physical term before replacing only the spatial curriculum
    # boundary and the arena/reset/command-domain adapters.
    from isaaclab.managers import TerminationTermCfg
    physical = {k: repr(v) for k, v in vars(cfg.terminations).items()
                if k != 'rough_route_boundary'}
    old_material = cfg.scene.terrain.physics_material
    root = Path(os.environ['MOD4_RM70_ORIGINAL_ASSET_ROOT'])
    receipt = json.loads(Path(os.environ['MOD4_RM70_ASSET_RECEIPT']).read_text())
    cfg.scene.terrain = make_terrain_cfg(root, receipt, cfg.scene.num_envs,
        os.environ['MOD4_RM70_NEW_LAYOUT_ROOT'])
    cfg.scene.terrain.physics_material = old_material
    cfg.scene.ground = None
    cfg.events.consistent_start.func = full_reset
    cfg.commands.twist.class_type = RM70Command208
    cfg.rewards.spin_contact_consistency.func = inactive_rolling
    cfg.terminations.rough_route_boundary = TerminationTermCfg(func=boundary208, time_out=True)
    if physical != {k: repr(v) for k, v in vars(cfg.terminations).items()
                    if k != 'rough_route_boundary'}:
        raise RuntimeError('Physical guard changed while configuring the new course')
    return dict(profile=COURSE_PROFILE, original_geometry='whole shared CAD arena collision',
        original_physics_and_reward_terms_unchanged=True,
        original_observation_dimensions=[35, 38], original_action_dimension=6,
        original_rough_commands='20% actual stand; BODY vx[-.3,.3]; vy=yaw=0; 12..16s',
        old_G3_plane_retained_modes_not_run_on_RM70=True,
        new_course_boundary=dict(world_local_x=list(COURSE_X), world_local_y=list(COURSE_Y),
            term='rough_route_boundary', time_out=True,
            old_2m_boundary_is_preserved_only_in_frozen_W35=True),
        old_source_not_overwritten=True, full_route_success_not_inferred=True)

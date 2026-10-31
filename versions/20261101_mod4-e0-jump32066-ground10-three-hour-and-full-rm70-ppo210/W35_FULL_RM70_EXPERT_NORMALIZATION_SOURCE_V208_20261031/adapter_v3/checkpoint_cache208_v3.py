from source_cache208_v3 import cached_load,cached_H
"""Full PPO/D0-D7 preservation across an explicit NEW CAD lesson, never rename."""
import os, json, time, hashlib
from pathlib import Path
import torch
from course_math208 import COURSE_PROFILE, COLLISION_USDC_SHA, SOURCE_MODEL_SHA
from chassis_pd_checkpoint208_v3 import install_chassis_pd_save_contract, resume_chassis_pd_new_episode
from spring_pressure_checkpoint208_v3 import exact


def current_state(env):
    return dict(version=1, profile=COURSE_PROFILE, num_envs=env.num_envs,
        collision_SHA=COLLISION_USDC_SHA, layout=[34., 20.],
        spawn_xy=env._rough_spawn_xy.clone(), reset_expected_q=env._rough_probe_expected_q.clone(),
        episode=env._e1_episode.clone(), course_boundary_version='208_original_route_extent',
        per_episode_reset_no_PhysX_exact_resume=True)


def identity(value):
    return {k: v for k, v in value.items() if k not in ('spawn_xy', 'reset_expected_q', 'episode')}


def _restore_bookkeeping(env, value):
    if value['num_envs'] != env.num_envs:
        raise ValueError('No unapproved slice/repeat of saved per-env full state')
    for key, name in (('spawn_xy', '_rough_spawn_xy'),
                      ('reset_expected_q', '_rough_probe_expected_q'), ('episode', '_e1_episode')):
        destination = getattr(env, name)
        if destination.shape != value[key].shape or destination.dtype != value[key].dtype:
            raise ValueError('Saved full-state shape or dtype differs: ' + key)
        destination.copy_(value[key].to(env.device))


def resume_e1_new_episode(runner, env, path, log_dir):
    ck = cached_load(path, map_location='cpu', weights_only=False)
    previous = ck['E1_terrain_state']; cmd = env.command_manager.get_term('twist')
    same = previous['profile'] == COURSE_PROFILE
    if same:
        if identity(previous) != identity(current_state(env)):
            raise ValueError('Wrong original CAD/layout/boundary identity')
        cmd.load_state_retention(ck['E1_retained_flat_command_state'])
    else:
        from g3_terrain_checkpoint import validate as validate_g3
        from retention_command_state import validate as validate_old, FIELDS
        validate_g3(previous, env.num_envs)
        source_digest = cached_H(path)
        if source_digest != SOURCE_MODEL_SHA:
            raise ValueError('Initial NEW208 fork must use selected formal W35 final78')
        old = ck['E1_retained_flat_command_state']; validate_old(old, env.num_envs)
        # Restore all old command fields/private RNG first. The one original
        # new-episode reset then samples the new rough-only domain naturally.
        for key in FIELDS:
            getattr(cmd, key).copy_(old[key].to(env.device))
        cmd._retention_rng.set_state(old['rng'].cpu())
        cmd.vel_command_b.copy_(old['BODY_command'].to(env.device))
        cmd.world_direction.copy_(cmd.direction); cmd.is_moving_spin.copy_(cmd.moving)
    _restore_bookkeeping(env, previous)
    before_episode = env._e1_episode.clone()
    restored = dict(terrain_bookkeeping=True, command_private_rng=True,
                    original_terrain_restored_exact=same,
                    explicitly_new_CAD_RM70_terrain=not same)
    result = resume_chassis_pd_new_episode(runner, env, path, log_dir)
    if not torch.equal(env._e1_episode, before_episode + 1):
        raise RuntimeError('Original complete D0-D7 restore must perform exactly one episode reset')
    if env._rough_query_tick is not None:
        raise RuntimeError('New physical episode kept a stale ground query')
    assert env.scene.terrain.retention_assignment_sha == COLLISION_USDC_SHA
    assert cmd.state_dict_retention()['assignment_sha256'] == COLLISION_USDC_SHA
    proof = dict(epoch=time.time(), source_sha256=result['source_sha256'],
        **restored, one_new_physical_episode=True, PhysX_exact_resume_claimed=False,
        full_D1_D7_original_restore=result, identity=identity(current_state(env)),
        actual_command_audit=cmd.audit_retention())
    for name in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED.json', 'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):
        Path(log_dir, name).write_text(json.dumps(proof, indent=2), encoding='utf8')
    return proof


def install_e1_save_contract(runner, env):
    install_chassis_pd_save_contract(runner, env); original = runner.save
    def save(path, *args, **kwargs):
        original(path, *args, **kwargs)
        ck = cached_load(path, map_location='cpu', weights_only=False)
        ck['E1_terrain_state'] = current_state(env)
        ck['E1_retained_flat_command_state'] = env.command_manager.get_term('twist').state_dict_retention()
        ck['E1_current_command_profile'] = COURSE_PROFILE
        ck['RM70_full208_lineage'] = dict(initial_W35_formal_SHA=SOURCE_MODEL_SHA,
            new_independent_terrain_course=True, legacy_W35_frozen_untouched=True,
            complete_SuperMimic_conversion=False, full_skill_graduation=False)
        torch.save(ck, path); env.write_retention_trace(Path(path).parent)
    runner.save = save

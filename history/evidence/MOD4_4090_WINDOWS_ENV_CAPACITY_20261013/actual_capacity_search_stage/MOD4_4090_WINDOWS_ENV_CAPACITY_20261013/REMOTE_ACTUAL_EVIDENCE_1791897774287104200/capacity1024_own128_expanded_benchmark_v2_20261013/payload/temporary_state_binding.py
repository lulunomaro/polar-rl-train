"""Own128 dimension expansion, independent of the immutable128 validator."""
from pathlib import Path
import copy, json, os, time, hashlib
import torch
import expanded_source_projection as ex
from expanded_source_projection import same, H, floating_count, DONOR_SHA, GEOMETRY_SHA, PARTITION_SHA, ASSIGNMENT_SHA
from selected_source_projection import bind_selected_entry
N = 1024
PARENT_SHA = 'f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3'
STATES = ex.STATES

def perenv_inventory(v, path='', n=N):
    return [('/' + '/'.join(map(str, row['tokens'])), tuple(row['shape']), row['dtype']) for row in ex.inventory(v, n)]

def validate(ck, source_sha):
    if 'WINDOWS4090_EXPANDED_ENV_BRANCH' not in ck:
        assert source_sha == PARENT_SHA, 'Only actual current own128 final can expand'
        return ex.validate_parent128(ck)
    ex.validate_expanded(ck, target_n=N)
    assert ck['WINDOWS4090_EXPANDED_ENV_BRANCH']['parent_checkpoint_SHA'] == PARENT_SHA
    return ck

def initialize_selected_env(env, args):
    assert env.num_envs == N and H(args.source_checkpoint) == args.source_sha
    original = validate(torch.load(args.source_checkpoint, map_location='cpu', weights_only=False), args.source_sha)
    fresh = 'WINDOWS4090_EXPANDED_ENV_BRANCH' not in original
    projected, proof = ex.expand_tree(original, source_sha=args.source_sha, target_n=N) if fresh else (copy.deepcopy(original), {})
    ids = torch.arange(N)
    bind_selected_entry(env, ids, projected)
    env._local_projection_original_ids = torch.tensor(projected['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids'])
    env._temporary_source_ids = ids
    env._temporary_family_quota = projected['WINDOWS4090_TEMPORARY_BRANCH']['family_counts']
    env._capacity_expansion_proof = proof
    env._capacity_fresh_expansion = fresh
    env.reset()
    env.command_manager.get_term('twist')._write_dynamic(torch.arange(N, device=env.device))
    return projected

def bound_tree(env, args):
    from wave50_entry_current_state_v2 import current_state, identity, KEY
    from wave50_route_runtime import state_dict as route
    from wave50_lifetime_runtime import state_dict as lifetime
    projected = initialize_selected_env(env, args)
    actual = current_state(env)
    term = env.command_manager.get_term('twist')
    states = {'E1_terrain_state': actual, KEY: identity(actual), 'E1_WAVE50_episode_direction_state': term.state_dict_direction(), 'E1_WAVE50_route_lifecycle_state': route(env, refresh=True), 'E1_WAVE50_episode_lifetime_state': lifetime(env, refresh=True)}
    if env._capacity_fresh_expansion:
        approved = {k: {} for k in STATES}
        projected, changes = ex.bind_runtime_metadata_once(projected, target_n=N, actual_states=states, approved_code_changes=approved)
    else:
        ex.require_same_runtime_metadata(projected, target_n=N, actual_states=states)
        changes = []
    assert same(projected['E1_terrain_state']['spawn_xy'], env._local_projection_reset_xy.cpu())
    assert same(projected['E1_terrain_state']['reset_expected_q'], actual['reset_expected_q'])
    validate(projected, args.source_sha)
    return (projected, dict(expansion_from_own128=env._capacity_fresh_expansion, explicit_parent_slot_copies=projected['WINDOWS4090_EXPANDED_ENV_BRANCH']['parent_slot_ids'], unique_child_slot_ids=projected['WINDOWS4090_EXPANDED_ENV_BRANCH']['child_slot_ids'], metadata_bindings=changes, parent_SHA=PARENT_SHA, exact99_paths=True, no_new_RNG_in_CPU_projection=True, new_physical_episode_required=True, PhysX_exact_resume=False))

def probe_source(env, args):
    return bound_tree(env, args)[0]

def materialize(env, output, args, write):
    projected, proof = bound_tree(env, args)
    p = Path(output) / 'WINDOWS4090_BOUND_FULLSTATE_SOURCE.pt'
    assert not p.exists()
    torch.save(projected, p)
    with p.open('r+b') as f:
        f.flush()
        os.fsync(f.fileno())
    assert same(projected, torch.load(p, map_location='cpu', weights_only=False))
    proof.update(epoch=time.time(), pid=os.getpid(), passed=True, source_sha256=args.source_sha, bound_source_sha256=H(p), num_envs=N, floating107=True, explicit_environment_count_expansion=True, no_source_actor_DR_splice=True, parent128_final_SHA=PARENT_SHA)
    write('WINDOWS4090_FULLSTATE_CPU_BINDING_ACTUAL.json', proof)
    return (p, proof)

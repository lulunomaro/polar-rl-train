"""Explicit learned Windows512 -> Linux20000 full-state dimension/ABI port.

This is not old20k DR, resampling, a policy initializer, or PhysX exact resume.
The fixed99 schema projects only per-env tensors. Every other tensor, Adam,
global histogram and saved RNG byte is copied exactly. Production first source
is the actual learned model32411 SHA; subsequent Linux saves use strict identity.
Only the separately planned code ABI SHA fields can bind once at first birth.
"""
from pathlib import Path
import copy
import hashlib
import json
import os
import time

import numpy as np
import torch

import expanded_source_projection as ex
from expanded_source_projection import H, same, floating_count, DONOR_SHA
from selected_source_projection import bind_selected_entry

N = 20000
SOURCE_N = 512
SOURCE_SHA = '17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9'
PROFILE = 'linux4090_learned_windows512_to_full20000_family_cyclic_v1'
KEY = 'LINUX4090_FULLSCALE_BRANCH'
STATES = ex.STATES
FAMILY_COUNTS = [6000, 4000, 4000, 3000, 3000]
SOURCE_FAMILY_COUNTS = [152, 104, 104, 76, 76]
FAMILIES = ('plane_for_rm', 'tiny_step', 'slope_for_rm_high',
            'inv_slope_for_rm_low', 'random_uniform_for_rm')
HISTORICAL_KEYS = ('WINDOWS4090_TEMPORARY_BACKEND_BINDING',
                   'WINDOWS4090_TEMPORARY_BRANCH',
                   'WINDOWS4090_EXPANDED_ENV_BRANCH',
                   'WINDOWS4090_CAPACITY_ATTEMPT',
                   'WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL')
CODE_BIND_FIELDS = {
    'E1_terrain_state': {'entry_runtime_sha256', 'entry_full_pose_sha256'},
    'E1_WAVE50_entry_reset_identity': {'entry_runtime_sha256', 'entry_full_pose_sha256'},
    'E1_WAVE50_episode_direction_state': set(),
    'E1_WAVE50_route_lifecycle_state': {'parent_boundary_source_sha256'},
    'E1_WAVE50_episode_lifetime_state': {'parent_timeout_source_sha256'},
}


def _metadata(state):
    return {k: v for k, v in state.items() if not torch.is_tensor(v)}


def _rows(path=None):
    p = Path(path) if path else Path(__file__).with_name('ACTUAL_GLOBAL1600_ASSIGNMENT.json')
    rows = json.loads(p.read_bytes())
    assert len(rows) == 1600
    assert len({(r['row'], r['column']) for r in rows}) == 1600
    actual = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert actual == ex.ASSIGNMENT_SHA, 'Actual complete static1600 assignment identity'
    table = torch.full((40, 40), -1, dtype=torch.long)
    for r in rows:
        assert 0 <= r['row'] < 40 and 0 <= r['column'] < 40
        table[r['row'], r['column']] = FAMILIES.index(r['family'])
    return rows, table, H(p)


def birth_family(ck, assignment_path=None):
    """Saved birth XY -> actual static cell assignment, never dynamic commands."""
    rows, table, row_sha = _rows(assignment_path)
    xy = ck['E1_terrain_state']['spawn_xy']
    assert xy.device.type == 'cpu' and xy.dtype == torch.float32 and xy.shape == (SOURCE_N, 2)
    rc = torch.floor(xy / 9 + 20).long()
    assert ((rc >= 0) & (rc < 40)).all()
    family = table[rc[:, 0], rc[:, 1]].clone()
    assert torch.bincount(family, minlength=5).tolist() == SOURCE_FAMILY_COUNTS
    assert ck['WINDOWS4090_TEMPORARY_BRANCH']['family_counts'] == SOURCE_FAMILY_COUNTS
    return family, dict(actual_saved_spawn_cell_family=True,
                        static1600_assignment_sha256=ex.ASSIGNMENT_SHA,
                        assignment_file_sha256=row_sha,
                        birth_cell_rc=rc.tolist(), source_family=family.tolist(),
                        source_family_counts=SOURCE_FAMILY_COUNTS,
                        dynamic_command_family_not_used=True)


def family_mapping(family):
    assert family.shape == (SOURCE_N,) and family.dtype == torch.long
    assert torch.bincount(family, minlength=5).tolist() == SOURCE_FAMILY_COUNTS
    parts = []
    for f, quota in enumerate(FAMILY_COUNTS):
        candidates = torch.nonzero(family == f).flatten()
        assert len(candidates) == SOURCE_FAMILY_COUNTS[f]
        parts.append(candidates[torch.arange(quota, dtype=torch.long) % len(candidates)])
    mapping = torch.cat(parts)
    assert mapping.shape == (N,)
    assert torch.bincount(family[mapping], minlength=5).tolist() == FAMILY_COUNTS
    return mapping


def _expected_fields(n):
    fields, sh = ex.schema()
    return [dict(row, shape=[n if i == row['axis'] else k
                            for i, k in enumerate(row['shape'])]) for row in fields], sh


def validate_source512(ck, source_sha):
    assert source_sha == SOURCE_SHA, 'Exact latest learned Windows512 source only'
    ex.validate_expanded(ck, target_n=SOURCE_N)
    b = ck['WINDOWS4090_EXPANDED_ENV_BRANCH']
    assert b['actual_runtime_metadata_bound'] and not b['CPU_prepared_only']
    assert b['actual_current_GPU_restore_verified']
    assert int(ck['iter']) == 32411, 'Exact learned28-update source iteration'
    assert KEY not in ck
    birth_family(ck)
    return ck


def _mapping_sha(mapping):
    return hashlib.sha256(mapping.numpy().astype('<i8').tobytes()).hexdigest()


def _input_sha(map_sha):
    # Saved-selected-entry receipt uses original complete20k donor ancestry.
    return hashlib.sha256((map_sha + ex.ASSIGNMENT_SHA + DONOR_SHA).encode()).hexdigest()


def validate(ck, source_sha):
    if KEY not in ck:
        return validate_source512(ck, source_sha)
    b = ck[KEY]
    assert b['profile'] == PROFILE and b['num_envs'] == N
    assert b['source_num_envs'] == SOURCE_N and b['source_checkpoint_SHA'] == SOURCE_SHA
    assert b['original20k_donor_SHA'] == DONOR_SHA
    assert b['initial35_accepted_source_SHA'] == ex.INITIAL35_SHA
    assert b['family_counts'] == FAMILY_COUNTS and b['source_family_counts'] == SOURCE_FAMILY_COUNTS
    assert b['child_slot_ids'] == list(range(N)), 'Unique current child slot IDs'
    family = torch.tensor(b['source_birth_family'], dtype=torch.long)
    source_xy = torch.tensor(b['source512_spawn_xy'], dtype=torch.float32)
    assert source_xy.shape == (SOURCE_N, 2)
    _, family_table, assignment_file_sha = _rows()
    assert b['actual_assignment_file_sha256'] == assignment_file_sha
    source_rc = torch.floor(source_xy / 9 + 20).long()
    assert ((source_rc >= 0) & (source_rc < 40)).all()
    assert b['source_birth_cell_rc'] == source_rc.tolist()
    assert torch.equal(family, family_table[source_rc[:, 0], source_rc[:, 1]])
    mapping = family_mapping(family)
    assert b['source512_slot_ids'] == mapping.tolist()
    assert b['source512_slot_map_sha256'] == _mapping_sha(mapping)
    assert len(b['source512_original20k_ancestor_ids']) == SOURCE_N
    expected_ancestors = [b['source512_original20k_ancestor_ids'][i] for i in mapping.tolist()]
    assert b['child_original20k_ancestor_ids'] == expected_ancestors
    assert all(type(i) is int and 0 <= i < 20000 for i in expected_ancestors)
    assert b['static1600_assignment_sha256'] == ex.ASSIGNMENT_SHA
    assert b['left_initializer_repeated'] is False
    assert b['original99_perenv_family_cyclic_copy_exact']
    assert b['global_command_histograms_retained_not_multiplied']
    assert b['saved_generators_retained_not_independently_resampled']
    assert b['correlated_copies_and_new_vector_draw_layout_disclosed']
    assert b['not_original20k_DR_or_PhysX_exact_resume']
    ex._common(ck, N)
    fields, sh = _expected_fields(N)
    assert b['fixed99_schema_SHA'] == sh and ex.inventory(ck, N) == fields
    for tokens in ex.COUNT_PATHS:
        assert ex.at(ck, tokens) == N, tokens
    t = ck['E1_terrain_state']
    assert torch.equal(t['spawn_xy'], source_xy[mapping]), 'Physical selected origins cannot drift from source512 mapping'
    assert t['entry_input_sha256'] == _input_sha(t['entry_map_sha256'])
    # Historical Windows branch remains genuinely512, not relabelled as Linux.
    assert ck['WINDOWS4090_TEMPORARY_BRANCH']['num_envs'] == SOURCE_N
    assert ck['WINDOWS4090_EXPANDED_ENV_BRANCH']['num_envs'] == SOURCE_N
    assert ck['WINDOWS4090_TEMPORARY_BRANCH']['family_counts'] == SOURCE_FAMILY_COUNTS
    assert len(ck['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids']) == SOURCE_N
    for key in HISTORICAL_KEYS:
        assert H_json(ck[key]) == b['historical_windows_metadata_sha256'][key], key
    assert type(b['CPU_prepared_only']) is bool and type(b['actual_runtime_metadata_bound']) is bool
    assert b['CPU_prepared_only'] is not b['actual_runtime_metadata_bound']
    if b['actual_runtime_metadata_bound']:
        assert set(b['bound_Linux_runtime_metadata']) == set(STATES)
        for state in STATES:
            assert same(_metadata(ck[state]), b['bound_Linux_runtime_metadata'][state]), (state, 'Bound Linux metadata anchor')
    return ck


def H_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def expand_learned_source(source, source_sha):
    validate_source512(source, source_sha)
    family, family_proof = birth_family(source)
    mapping = family_mapping(family)
    fields, schema_sha = _expected_fields(SOURCE_N)
    by_path = {tuple(r['tokens']): r for r in fields}
    changes = []

    def visit(v, path=()):
        if torch.is_tensor(v):
            if path in by_path:
                row = by_path[path]
                assert list(v.shape) == row['shape'] and str(v.dtype) == row['dtype']
                assert row['axis'] == 0
                out = v.index_select(0, mapping).clone()
                assert out.data_ptr() != v.data_ptr()
                changes.append(dict(tokens=list(path), axis=0, parent_shape=list(v.shape),
                                    child_shape=list(out.shape), dtype=str(v.dtype)))
                return out
            return v.clone()
        if isinstance(v, dict):
            return {k: visit(x, path + (k,)) for k, x in v.items()}
        if isinstance(v, list):
            return [visit(x, path + (i,)) for i, x in enumerate(v)]
        if isinstance(v, tuple):
            return tuple(visit(x, path + (i,)) for i, x in enumerate(v))
        return copy.deepcopy(v)

    out = visit(source)
    assert len(changes) == 99
    for tokens in ex.COUNT_PATHS:
        assert ex.at(source, tokens) == SOURCE_N
        ex.put(out, tokens, N)
    map_sha = hashlib.sha256(out['E1_terrain_state']['spawn_xy'].numpy().astype('<f4').tobytes()).hexdigest()
    identity_changes = []
    for state in STATES:
        for field, value in [('entry_map_sha256', map_sha), ('entry_origin_sha256', map_sha),
                             ('entry_input_sha256', _input_sha(map_sha))]:
            if field in out[state]:
                identity_changes.append(dict(state=state, field=field, old=out[state][field], new=value))
                out[state][field] = value
    assert same(out['E1_WAVE50_entry_reset_identity'], _metadata(out['E1_terrain_state']))
    ancestors = source['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids']
    for key in ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict',
                'sensor_global_rng_state', 'sensor_command_DR_rng_state', 'sensor_physical_DR_rng_state'):
        assert same(out[key], source[key]), key
    for key in ('sample_histogram', 'control_histogram', 'rng'):
        assert same(out['E1_retained_flat_command_state'][key], source['E1_retained_flat_command_state'][key])
    for key in HISTORICAL_KEYS:
        assert same(out[key], source[key])
    out[KEY] = dict(
        profile=PROFILE, num_envs=N, source_num_envs=SOURCE_N,
        source_checkpoint_SHA=SOURCE_SHA, source_iteration=int(source['iter']),
        original20k_donor_SHA=DONOR_SHA, initial35_accepted_source_SHA=ex.INITIAL35_SHA,
        family_counts=FAMILY_COUNTS, source_family_counts=SOURCE_FAMILY_COUNTS,
        source_birth_family=family.tolist(), source_birth_cell_rc=family_proof['birth_cell_rc'],
        source512_spawn_xy=source['E1_terrain_state']['spawn_xy'].tolist(),
        static1600_assignment_sha256=ex.ASSIGNMENT_SHA,
        actual_assignment_file_sha256=family_proof['assignment_file_sha256'],
        child_slot_ids=list(range(N)), source512_slot_ids=mapping.tolist(),
        source512_slot_map_sha256=_mapping_sha(mapping),
        source512_original20k_ancestor_ids=list(ancestors),
        child_original20k_ancestor_ids=[ancestors[i] for i in mapping.tolist()],
        fixed99_schema_SHA=schema_sha,
        historical_windows_metadata_sha256={key: H_json(source[key]) for key in HISTORICAL_KEYS},
        CPU_prepared_only=True, actual_runtime_metadata_bound=False,
        original99_perenv_family_cyclic_copy_exact=True,
        actor_critic_std_Adam_globalnamed_private_CPUCUDA_initial_exact=True,
        global_command_histograms_retained_not_multiplied=True,
        saved_generators_retained_not_independently_resampled=True,
        correlated_copies_and_new_vector_draw_layout_disclosed=True,
        duplicate_ancestor_ids_not_duplicate_child_ids=True,
        source_Windows_backend_metadata_historical_only=True,
        no_old20k_DR_splice=True, left_initializer_repeated=False,
        not_original20k_DR_or_PhysX_exact_resume=True,
        new_physical_episode_source_slot_plus_one_required=True,
        all12_own_CPUCUDA_restore_disk_roundtrip_pending=True,
    )
    validate(out, source_sha)
    return out, dict(source_checkpoint_SHA=source_sha, source_iteration=int(source['iter']),
                     source_num_envs=SOURCE_N, target_num_envs=N,
                     source_birth_family_review=family_proof,
                     exact99_paths=changes, scalar_count_paths=[list(p) for p in ex.COUNT_PATHS],
                     map_origin_input_changes=identity_changes,
                     no_new_RNG=True, no_initializer=True, CPU_prepared_only=True)


def perenv_inventory(v, path='', n=N):
    return [('/' + '/'.join(map(str, r['tokens'])), tuple(r['shape']), r['dtype'])
            for r in ex.inventory(v, n)]


def bind_runtime_metadata_once(ck, actual_states, approved_code_changes, *, timeout_math_equivalence_reviewed=False):
    validate(ck, SOURCE_SHA)
    b = ck[KEY]
    assert b['CPU_prepared_only'] and not b['actual_runtime_metadata_bound'], 'First Linux ABI binding only'
    assert set(actual_states) == set(STATES) and set(approved_code_changes) == set(STATES)
    for field in ('spawn_xy', 'reset_expected_q'):
        assert same(ck['E1_terrain_state'][field], actual_states['E1_terrain_state'][field]), field
    out = copy.deepcopy(ck)
    changes = []
    used = {state: set() for state in STATES}
    for state in STATES:
        before = _metadata(ck[state])
        actual = _metadata(actual_states[state])
        assert set(before) == set(actual), (state, 'Metadata key set changed')
        for field, value in actual.items():
            if same(before[field], value):
                continue
            assert field in CODE_BIND_FIELDS[state], (state, field, 'Not an ABI-only code SHA field')
            plan = approved_code_changes[state][field]
            assert plan == dict(old=before[field], new=value, explicit_frozen_code_binding_only=True)
            assert isinstance(value, str) and len(value) == 64
            if field == 'parent_timeout_source_sha256':
                assert timeout_math_equivalence_reviewed is True, 'Timeout ABI requires independent unchanged-math proof'
            out[state][field] = copy.deepcopy(value)
            changes.append(dict(state=state, field=field, old=before[field], new=value))
            used[state].add(field)
    for state in STATES:
        assert set(approved_code_changes[state]) == used[state], (state, 'Extraneous/nonexecuted code binding plan')
    out[KEY].update(CPU_prepared_only=False, actual_runtime_metadata_bound=True,
                    approved_code_binding_changes=changes, code_binding_profile='linux_Sim6_Lab6_once_v1',
                    bound_Linux_runtime_metadata={state: copy.deepcopy(_metadata(out[state])) for state in STATES})
    validate(out, SOURCE_SHA)
    return out, changes


def require_same_runtime_metadata(ck, actual_states):
    validate(ck, SOURCE_SHA)
    assert ck[KEY]['actual_runtime_metadata_bound'] and not ck[KEY]['CPU_prepared_only']
    assert set(actual_states) == set(STATES)
    for state in STATES:
        assert same(_metadata(ck[state]), _metadata(actual_states[state])), (state, 'Same Linux forbids any rebind')
    for field in ('spawn_xy', 'reset_expected_q'):
        assert same(ck['E1_terrain_state'][field], actual_states['E1_terrain_state'][field]), field
    return True


def initialize_selected_env(env, args):
    assert env.num_envs == N and H(args.source_checkpoint) == args.source_sha
    original = torch.load(args.source_checkpoint, map_location='cpu', weights_only=False)
    validate(original, args.source_sha)
    fresh = KEY not in original
    projected, proof = expand_learned_source(original, args.source_sha) if fresh else (copy.deepcopy(original), {})
    ids = torch.arange(N, dtype=torch.long)
    bind_selected_entry(env, ids, projected)
    env._local_projection_original_ids = torch.tensor(projected[KEY]['child_original20k_ancestor_ids'], dtype=torch.long)
    env._temporary_source_ids = ids
    env._temporary_family_quota = FAMILY_COUNTS
    env._linux_port_proof = proof
    env._linux_port_first_binding = fresh
    env.reset()
    env.command_manager.get_term('twist')._write_dynamic(torch.arange(N, device=env.device))
    return projected


def bound_tree(env, args):
    from wave50_entry_current_state_v2 import current_state, identity, KEY as ENTRY_KEY
    from wave50_route_runtime import state_dict as route
    from wave50_lifetime_runtime import state_dict as lifetime
    projected = initialize_selected_env(env, args)
    actual = current_state(env)
    states = {'E1_terrain_state': actual, ENTRY_KEY: identity(actual),
              'E1_WAVE50_episode_direction_state': env.command_manager.get_term('twist').state_dict_direction(),
              'E1_WAVE50_route_lifecycle_state': route(env, refresh=True),
              'E1_WAVE50_episode_lifetime_state': lifetime(env, refresh=True)}
    if env._linux_port_first_binding:
        path = Path(getattr(args, 'binding_plan', Path(__file__).with_name('LINUX_CODE_BINDING_PLAN.json')))
        plan = json.loads(path.read_bytes())
        assert plan['source_checkpoint_SHA'] == SOURCE_SHA and plan['target_num_envs'] == N
        assert plan['selected_entry_input_ancestry_SHA'] == DONOR_SHA
        assert plan['no_physics_reward_command_DR_change'] is True
        if 'parent_timeout_source_sha256' in plan['approved_code_changes']['E1_WAVE50_episode_lifetime_state']:
            assert plan['timeout_parent_math_equivalence_CPU_reviewed'] is True
        projected, changes = bind_runtime_metadata_once(projected, states, plan['approved_code_changes'],
                                                       timeout_math_equivalence_reviewed=plan.get('timeout_parent_math_equivalence_CPU_reviewed', False))
    else:
        require_same_runtime_metadata(projected, states)
        changes = []
    assert same(projected['E1_terrain_state']['spawn_xy'], env._local_projection_reset_xy.cpu())
    validate(projected, args.source_sha)
    proof = dict(explicit_windows512_to_linux20000=env._linux_port_first_binding,
                 source_checkpoint_SHA=SOURCE_SHA, exact99_family_cyclic_paths=True,
                 family_counts=FAMILY_COUNTS, unique_child_slot_ids=True,
                 repeated_ancestors_and_correlated_copies_disclosed=True,
                 global_histograms_not_multiplied=True, metadata_bindings=changes,
                 no_new_RNG_in_projection=True, initializer_repeated=False,
                 new_physical_episode_required=True, PhysX_exact_resume=False,
                 projection=env._linux_port_proof)
    return projected, proof


def probe_source(env, args):
    return bound_tree(env, args)[0]


def materialize(env, output, args, write):
    projected, proof = bound_tree(env, args)
    p = Path(output) / 'LINUX4090_BOUND_FULLSTATE_SOURCE.pt'
    assert not p.exists()
    torch.save(projected, p)
    with p.open('r+b') as f:
        f.flush()
        os.fsync(f.fileno())
    assert same(projected, torch.load(p, map_location='cpu', weights_only=False))
    proof.update(epoch=time.time(), pid=os.getpid(), passed=True, source_sha256=args.source_sha,
                 bound_source_sha256=H(p), bytes=p.stat().st_size, num_envs=N,
                 floating107=floating_count(projected) == 107,
                 no_source_actor_DR_splice=True, GPU_fullrestore_still_required=True)
    write('LINUX4090_FULLSTATE_CPU_BINDING_ACTUAL.json', proof)
    return p, proof

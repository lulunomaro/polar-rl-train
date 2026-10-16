"""Declared birth orientation state; independent of any simulator or gate input."""
import copy
import torch

SOURCE = 'e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
PROFILE = 'E1_WAVE50_balanced_birth_bodyframe_runtime_v1'
KEY = 'E1_WAVE50_balanced_birth_bodyframe_state_v1'
N = 20000
IDENTITY = dict(new_geometry=False, new_entry_pose=True,
                new_BODY_direction_identity=True, new_world_route=False,
                new_lifetime=False, new_RNG_draws=False,
                live_heading_position_correction=False)


def clone(value):
    if isinstance(value, torch.Tensor):
        return value.detach().clone()
    if isinstance(value, dict):
        return {k: clone(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return type(value)(clone(v) for v in value)
    return copy.deepcopy(value)


def validate(s, bindings=None):
    assert s['version'] == 1 and s['profile'] == PROFILE
    assert s['num_envs'] == N and s['initial_source_SHA'] == SOURCE
    assert s['declared_transition'] == IDENTITY
    assert s['World_inward_m'] == 4. and s['other_route_m'] == 2.
    assert s['Wave_seconds'] == 40. and s['other_seconds'] == 20.
    if bindings is not None:
        assert s['source_bindings'] == bindings
    device = s['source_episode'].device
    for name, dtype in (('wave_mask', torch.bool), ('world_toward_sign', torch.float32),
                        ('rank_in_side', torch.int64), ('source_episode', torch.int64),
                        ('bound_episode', torch.int64), ('flip_pi', torch.bool),
                        ('BODY_coefficient', torch.float32), ('births', torch.int64)):
        v = s[name]
        assert isinstance(v, torch.Tensor) and v.shape == (N,) and v.dtype == dtype
        assert v.device == device
    mask = s['wave_mask']; sign = s['world_toward_sign']
    assert ((sign[mask] == -1) | (sign[mask] == 1)).all()
    assert (sign[~mask] == 0).all() and (s['rank_in_side'][~mask] == -1).all()
    assert (s['source_episode'] >= 0).all() and (s['births'] >= 0).all()
    assert torch.equal(s['bound_episode'], s['source_episode'] + s['births'])
    expected = mask & (((s['rank_in_side'] + s['births']) % 2) == 1) & (s['births'] > 0)
    assert torch.equal(s['flip_pi'], expected)
    assert torch.equal(s['BODY_coefficient'], torch.where(expected, -1., 1.))
    for side in (-1., 1.):
        ids = torch.nonzero(mask & (sign == side)).flatten()
        assert torch.equal(s['rank_in_side'][ids], torch.arange(len(ids), device=device))
    histogram = s['completed_control_histogram']
    assert histogram.shape == (2, 2, 3) and histogram.dtype == torch.int64
    assert histogram.device == device and (histogram >= 0).all()
    assert type(s['completed_controls']) is int and s['completed_controls'] >= 0
    return True


def from_whole_predecessor(ck, source_sha, bindings):
    assert source_sha == SOURCE and KEY not in ck
    d = ck['E1_WAVE50_episode_direction_state']
    r = ck['E1_WAVE50_route_lifecycle_state']
    l = ck['E1_WAVE50_episode_lifetime_state']
    e = ck['E1_terrain_state']['episode']
    assert ck['sensor_DR_state']['n'] == N and e.shape == (N,)
    assert torch.equal(d['wave_mask'], r['wave_mask']) and torch.equal(d['wave_mask'], l['wave_mask'])
    assert torch.equal(d['entry_sign'], r['toward_sign'])
    assert torch.equal(d['bound_episode'], e) and torch.equal(r['bound_episode'], e) and torch.equal(l['bound_episode'], e)
    assert ck['independent_terrain_expert'] == 'E1_WAVE50'
    actual = {k: d[k] for k in ('assignment_sha256', 'entry_map_sha256', 'entry_origin_sha256')}
    actual.update(parent_boundary_source_sha256=r['parent_boundary_source_sha256'],
                  parent_timeout_source_sha256=l['parent_timeout_source_sha256'])
    assert actual == bindings
    mask = d['wave_mask'].clone(); sign = d['entry_sign'].clone()
    rank = torch.full_like(e, -1)
    for side in (-1., 1.):
        ids = torch.nonzero(mask & (sign == side)).flatten()
        rank[ids] = torch.arange(len(ids), device=e.device)
    s = dict(version=1, profile=PROFILE, num_envs=N, initial_source_SHA=SOURCE,
             source_bindings=copy.deepcopy(bindings), declared_transition=copy.deepcopy(IDENTITY),
             World_inward_m=4., other_route_m=2., Wave_seconds=40., other_seconds=20.,
             wave_mask=mask, world_toward_sign=sign, rank_in_side=rank,
             source_episode=e.clone(), bound_episode=e.clone(), births=torch.zeros_like(e),
             flip_pi=torch.zeros_like(mask), BODY_coefficient=torch.ones_like(sign),
             completed_control_histogram=torch.zeros((2, 2, 3), device=e.device, dtype=torch.int64),
             completed_controls=0)
    validate(s, bindings)
    return s


def next_birth(s, ids, actual_episode):
    validate(s)
    assert ids.dtype == torch.int64 and ids.ndim == 1 and ids.device == s['bound_episode'].device
    assert len(ids) == len(torch.unique(ids)) and ((ids >= 0) & (ids < N)).all()
    assert actual_episode.shape == (N,) and actual_episode.dtype == torch.int64
    assert actual_episode.device == ids.device
    assert torch.equal(actual_episode[ids], s['bound_episode'][ids] + 1), 'Only one actual new birth per selected environment'
    out = clone(s)
    out['births'][ids] += 1
    out['bound_episode'][ids] = actual_episode[ids]
    flip = out['wave_mask'][ids] & (((out['rank_in_side'][ids] + out['births'][ids]) % 2) == 1)
    out['flip_pi'][ids] = flip
    out['BODY_coefficient'][ids] = torch.where(flip, -1., 1.)
    validate(out)
    return out


def mapped_command(original, family, standing, s, ids=None):
    assert original.shape == (N, 3) and torch.isfinite(original).all()
    assert family.shape == (N,) and standing.shape == (N,) and standing.dtype == torch.bool
    chosen = torch.ones(N, dtype=torch.bool, device=original.device)
    if ids is not None:
        assert ids.dtype == torch.int64 and ids.ndim == 1
        assert len(ids) == len(torch.unique(ids)) and ((ids >= 0) & (ids < N)).all()
        chosen.zero_(); chosen[ids] = True
    active = chosen & s['wave_mask'] & (family == 4) & ~standing
    assert (s['births'][active] > 0).all()
    assert (original[active, 0] * s['world_toward_sign'][active] >= 0).all()
    assert (original[active, 0].abs() <= .300001).all() and (original[active, 1:] == 0).all()
    assert (original[standing & chosen] == 0).all()
    out = original.clone()
    out[active, 0] *= s['BODY_coefficient'][active]
    assert torch.equal(out[~active], original[~active])
    return out


def audit_command(actual, family, standing, episode, s):
    validate(s)
    assert torch.equal(episode, s['bound_episode'])
    assert actual.shape == (N, 3) and torch.isfinite(actual).all()
    active = s['wave_mask'] & (family == 4) & ~standing
    assert (actual[active, 0] * s['BODY_coefficient'][active] * s['world_toward_sign'][active] >= 0).all()
    assert (actual[active, 0].abs() <= .300001).all()
    assert (actual[s['wave_mask'] & (family == 4), 1:] == 0).all() and (actual[standing] == 0).all()
    return dict(profile=PROFILE, old_BODY_times_worldsign_predicate_replaced_explicitly=True,
                new_entry_pose=True, new_BODY_direction_identity=True,
                body_sign_does_not_equal_world_entry_sign=True,
                world_route_and_lifetime_unchanged=True, no_live_heading_position_input=True,
                active_moving_Wave=int(active.sum()), completed_controls=s['completed_controls'],
                completed_control_histogram=s['completed_control_histogram'].cpu().tolist(),
                histogram_axes=['WORLD entry side minus/plus', 'birth unrotated/pi', 'BODY negative/positive/standing'])


def histogram_increment(actual, family, standing, s):
    mask = s['wave_mask'] & (family == 4)
    side = (s['world_toward_sign'][mask] > 0).long()
    orientation = s['flip_pi'][mask].long()
    mode = torch.where(standing[mask], 2, torch.where(actual[mask, 0] < 0, 0, 1))
    return torch.bincount(side * 6 + orientation * 3 + mode, minlength=12).reshape(2, 2, 3)


def bind_saved_checkpoint(old_checkpoint, state):
    """Append an owned state to a just-saved complete checkpoint; never alter its old fields."""
    validate(state)
    assert torch.equal(old_checkpoint['E1_terrain_state']['episode'].cpu(), state['bound_episode'].cpu())
    d = old_checkpoint['E1_WAVE50_episode_direction_state']
    assert torch.equal(d['wave_mask'].cpu(), state['wave_mask'].cpu())
    assert torch.equal(d['entry_sign'].cpu(), state['world_toward_sign'].cpu())
    assert torch.equal(d['bound_episode'].cpu(), state['bound_episode'].cpu())
    cmd = old_checkpoint['E1_retained_flat_command_state']
    command = cmd['BODY_command']
    audit_command(command, cmd['family'], (command == 0).all(-1), old_checkpoint['E1_terrain_state']['episode'],
                  {k: v.cpu() if torch.is_tensor(v) else v for k, v in state.items()})
    out = clone(old_checkpoint)
    assert KEY not in out
    out[KEY] = {k: v.cpu() if torch.is_tensor(v) else clone(v) for k, v in state.items()}
    return out

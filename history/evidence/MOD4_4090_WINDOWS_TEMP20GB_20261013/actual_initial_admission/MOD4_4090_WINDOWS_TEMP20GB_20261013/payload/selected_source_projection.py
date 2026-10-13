from pathlib import Path
import torch,numpy as np,copy,json,hashlib
SOURCE={'sha256':'d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'}
def select(env, ck):
    n = env.num_envs
    xy = ck['E1_terrain_state']['spawn_xy']
    rc = torch.floor(xy / 9 + 20).long()
    assert ((rc >= 0) & (rc < 40)).all()
    family = env.scene.terrain.retention_family.cpu()[rc[:, 0], rc[:, 1]]
    quota = [round(n * 0.3), round(n * 0.2), round(n * 0.2), round(n * 0.15)]
    quota.append(n - sum(quota))
    ids = []
    for f, k in enumerate(quota):
        candidates = torch.nonzero(family == f).flatten()
        assert len(candidates) >= k
        index = torch.linspace(0, len(candidates) - 1, k).round().long()
        ids.append(candidates[index])
    ids = torch.cat(ids)
    assert len(torch.unique(ids)) == n
    return (ids, quota)

def project_tree(value, ids, path='', changes=None):
    if changes is None:
        changes = []
    if isinstance(value, torch.Tensor):
        axes = [i for i, n in enumerate(value.shape) if n == 20000]
        assert len(axes) <= 1
        if axes:
            out = value.index_select(axes[0], ids).clone()
            changes.append(dict(path=path, axis=axes[0], from_shape=list(value.shape), to_shape=list(out.shape)))
            return out
        return value.clone()
    if isinstance(value, dict):
        return {k: len(ids) if k in ('n', 'num_envs') and v == 20000 and isinstance(v, int) else project_tree(v, ids, path + '/' + str(k), changes) for k, v in value.items()}
    if isinstance(value, tuple):
        return tuple((project_tree(v, ids, path + '/' + str(i), changes) for i, v in enumerate(value)))
    if isinstance(value, list):
        return [project_tree(v, ids, path + '/' + str(i), changes) for i, v in enumerate(value)]
    return copy.deepcopy(value)

def bind_selected_entry(env, ids, ck):
    xy = ck['E1_terrain_state']['spawn_xy'][ids].clone().to(env.device)
    env.scene.env_origins[:, :2] = xy
    env.scene.terrain.env_origins[:, :2] = xy
    env._local_projection_reset_xy = xy
    env._local_projection_original_ids = ids.clone()
    env._local_projection_source_SHA = SOURCE['sha256']

def selected_entry(env, ids):
    from wave50_entry_runtime_v2 import A, h
    from wave50_entry_v1_math import PROFILE
    xy = env._local_projection_reset_xy
    origins = env.scene.env_origins[:, :2]
    assert env._local_projection_source_SHA == SOURCE['sha256'] and torch.equal(xy, origins)
    rows = env.scene.terrain.retention_assignment
    assignment = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert assignment == env.scene.terrain.retention_assignment_sha
    bank = A / 'MOD4_RESET_COLLISION_BANK.npz'
    profile = A / 'g4_cad_profile.json'
    with np.load(bank) as z:
        points = z['points_root'][int(np.argmin(abs(z['root_height'] - 0.25)))].copy()
    extent = np.max(abs(points[:, :2]), axis=0)
    span = json.loads(profile.read_bytes())['span_m']
    rc = torch.floor(xy / 9 + 20).long()
    assert ((rc >= 0) & (rc < 40)).all()
    bounds = env.scene.terrain.retention_bounds[rc[:, 0], rc[:, 1]]
    mask = env.scene.terrain.retention_family[rc[:, 0], rc[:, 1]] == 4
    ex = torch.tensor(extent, device=env.device)
    center = (bounds[:, 0, 0] + bounds[:, 1, 0]) * 0.5
    assert (torch.abs(xy[mask, 0] - center[mask]) - ex[0] - span * 0.5 >= 0.4 - 1e-06).all()
    assert ((xy[mask] - ex >= bounds[mask, 0, :2] + 0.004 - 1e-06) & (xy[mask] + ex <= bounds[mask, 1, :2] - 0.004 + 1e-06)).all()
    sha = hashlib.sha256(xy.cpu().numpy().astype('<f4').tobytes()).hexdigest()
    env._wave50_entry_xy = xy.clone()
    env._wave50_entry_origin_snapshot = origins.clone()
    env._wave50_entry_map_receipt = dict(profile=PROFILE, map_sha256=sha, actual_origin_sha256=sha, actual_assignment_sha256=assignment, complete_bank_sha256=h(bank), math_sha256=h(A / 'wave50_entry_v1_math.py'), full_pose_reset_sha256=h(A / 'wave50_entry_full_pose_reset_v2.py'), geometry_profile_sha256=h(profile), actual_input_identity_sha256=hashlib.sha256((sha + assignment + SOURCE['sha256']).encode()).hexdigest(), cache_builds=1, actual_origin_bound=True, collision_sample_extent_xy=extent.tolist(), ten_wave_span_m=span, Wave_environments=int(mask.sum()), other_environments_unchanged=int((~mask).sum()), changed_environments=int(mask.sum()), minimum_full_flat_front_support_m=float((torch.abs(xy[mask, 0] - center[mask]) - ex[0] - span * 0.5).min()) if mask.any() else 0.517, local_explicit_selected_source_entry_projection=True, source_original_ids=env._local_projection_original_ids.tolist(), source_SHA=SOURCE['sha256'], no_new_random_stream=True)
    return xy[ids].clone()

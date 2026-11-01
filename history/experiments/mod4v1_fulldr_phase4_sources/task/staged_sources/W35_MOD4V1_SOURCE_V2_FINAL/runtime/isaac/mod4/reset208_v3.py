"""New original-CAD route reset; only the established full-pose reset writes state.

Uses the same original nearest-.25 bank / pose34 and complete footprint. No
position/velocity/root correction runs between natural episode resets.
"""
import json, hashlib
from pathlib import Path
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from e1_rough_reset_tensor import tangent_frame, joint_permutation
from field208 import SharedQuery208
import mod4_task as task
from course_math208 import ROUTE_X, ROUTE_Y


def query(env):
    if not hasattr(env, '_rough_probe_query'):
        env._rough_probe_query = SharedQuery208(env)
    return env._rough_probe_query


def full_reset(env, env_ids):
    robot = env.scene['robot']; device = env.device
    ids = torch.arange(env.num_envs, device=device) if env_ids is None else env_ids
    if not len(ids):
        return
    mod = Path(task.__file__).resolve().parent
    if not hasattr(env, '_rough_probe_bank'):
        meta = json.loads((mod / 'MOD4_RESET_COLLISION_BANK.json').read_text())
        from mod4v1_w35_asset_compat import (
            require_mod4v1_asset_and_original_bank_geometry, verify_original_W35_selected_bank)
        env._mod4v1_asset_compatibility = require_mod4v1_asset_and_original_bank_geometry(
            meta, mod / 'MOD4_RESET_COLLISION_BANK.json', task.USD_PATH,
            task.MOD4_ISAAC / 'import_contract.json')
        with np.load(mod / 'MOD4_RESET_COLLISION_BANK.npz') as bank:
            perm = joint_permutation(list(bank['joint_names']), robot.joint_names)
            pick = int(np.argmin(abs(bank['root_height'] - .25)))
            env._w35_gas400_selected_bank_compatibility = verify_original_W35_selected_bank(bank, pick)
            env._rough_probe_bank = dict(
                q=torch.as_tensor(bank['q'][pick, perm].copy(), device=device, dtype=torch.float32),
                points=torch.as_tensor(bank['points_root'][pick].copy(), device=device, dtype=torch.float32),
                pose_index=pick, meta=meta)
    bank = env._rough_probe_bank; ray = query(env)
    origins = env.scene.env_origins[ids]
    reverse = (ids % 2).bool()
    xy = origins[:, :2].clone(); xy[:, 0] += torch.where(reverse, ROUTE_X[1], ROUTE_X[0])
    xy[:, 1] += ROUTE_Y
    heading = reverse.float() * np.pi
    ceiling = origins[:, 2] + ray.ceiling208
    starts = torch.cat((xy, ceiling[:, None]), 1)
    ground = ray.cast(starts[:, None].contiguous(), 10., env_ids=ids)
    if not bool(ground['hit'].all()) or not bool((ground['normal'][..., 2] > 0).all()):
        raise RuntimeError('Missing actual CAD root support; no cached floor')
    normals = ground['normal'][:, 0].cpu().numpy(); yaws = heading.cpu().numpy()
    frames = np.stack([tangent_frame(n, float(y)) for n, y in zip(normals, yaws)])
    rotations = torch.as_tensor(frames, device=device, dtype=torch.float32)
    z = torch.empty(len(ids), device=device); minimum_clearance = float('inf')
    for first in range(0, len(ids), 64):
        end = min(first + 64, len(ids)); current_ids = ids[first:end]
        offsets = torch.einsum('nij,pj->npi', rotations[first:end], bank['points'])
        footprint = offsets.clone(); footprint[:, :, :2] += xy[first:end, None]
        footprint[:, :, 2] = ceiling[first:end, None]
        support = ray.cast(footprint.contiguous(), 10., env_ids=current_ids)
        if not bool(support['hit'].all()):
            raise RuntimeError('Original complete collider footprint misses CAD support')
        placed = (support['height'] + .002 - offsets[:, :, 2]).amax(1)
        clear = placed[:, None] + offsets[:, :, 2] - support['height']
        if not bool(torch.isfinite(clear).all()) or float(clear.min()) < .002 - 1e-5:
            raise RuntimeError('Invalid original sampled full-pose placement')
        z[first:end] = placed; minimum_clearance = min(minimum_clearance, float(clear.min()))
    q = bank['q'][None].repeat(len(ids), 1)
    robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)
    state = robot.data.root_state_w[ids].clone()
    state[:, :2] = xy; state[:, 2] = z
    # Actual bound SDK6.1 uses xyzw, as already proven in194-209; preserve SciPy order.
    xyzw = Rotation.from_matrix(frames).as_quat()
    state[:, 3:7] = torch.as_tensor(xyzw, device=device, dtype=state.dtype)
    state[:, 7:] = 0.
    robot.write_root_state_to_sim(state, env_ids=ids)
    task.height_cmd(env)[ids] = .25
    if not hasattr(env, '_mod4_ground_z'):
        env._mod4_ground_z = torch.zeros(env.num_envs, device=device)
    if not hasattr(env, '_rough_probe_expected_q'):
        env._rough_probe_expected_q = torch.zeros(env.num_envs, 30, device=device)
    if not hasattr(env, '_rough_spawn_xy'):
        env._rough_spawn_xy = torch.zeros(env.num_envs, 2, device=device)
    env._mod4_ground_z[ids] = ground['height'][:, 0]
    env._rough_probe_expected_q[ids] = q; env._rough_spawn_xy[ids] = xy
    env._rough_query_tick = None
    env._rough_probe_reset_receipt = dict(pose_index=bank['pose_index'],
        full_joint_names=robot.joint_names, qd_all_zero_requested=True,
        root_velocity_all_zero_requested=True, sample_points=bank['points'].shape[0],
        sampled_min_clearance_m=minimum_clearance, root_quaternion_order='xyzw',
        route_assignment='original rough_forward/reverse by env parity; no extra RNG',
        source_slope_preserved=True, reset_only_no_running_state_injection=True,
        surface_sampling_not_continuous_nonpenetration=True)

"""Trainable intro reset: original full-pose geometry, chunked complete footprint."""
import hashlib, json, numpy as np, torch
from pathlib import Path
from scipy.spatial.transform import Rotation
from rough_reset_tensor import tangent_frame, joint_permutation
from rough_ground import AuthoredTerrainRaycast
import mod4_task as task
A=Path('/home/egde/rl_candidates/MOD4_SCUT_ROUGH_V1_ADAPTER_20261002')

def query(env):
    if not hasattr(env, '_rough_probe_query'):
        env._rough_probe_query = AuthoredTerrainRaycast(env.sim.stage, env.device)
    return env._rough_probe_query

def full_reset(env, env_ids):
    robot = env.scene['robot']
    ids = torch.arange(env.num_envs, device=env.device) if env_ids is None else env_ids
    if not len(ids): return
    if not hasattr(env, '_rough_probe_bank'):
        meta = json.loads((A / 'MOD4_RESET_COLLISION_BANK.json').read_text())
        assert hashlib.sha256(Path(task.USD_PATH).read_bytes()).hexdigest() == meta['usd_sha256']
        assert hashlib.sha256((task.MOD4_ISAAC / 'import_contract.json').read_bytes()).hexdigest() == meta['contract_sha256']
        bank = np.load(A / 'MOD4_RESET_COLLISION_BANK.npz')
        perm = joint_permutation(list(bank['joint_names']), robot.joint_names)
        pick = int(np.argmin(abs(bank['root_height'] - .25)))
        env._rough_probe_bank = dict(q=torch.as_tensor(bank['q'][pick, perm], device=env.device, dtype=torch.float32),
            points=torch.as_tensor(bank['points_root'][pick], device=env.device, dtype=torch.float32),
            pose_index=pick, meta=meta)
    bank = env._rough_probe_bank
    ray = query(env)
    xy = env.scene.env_origins[ids, :2].clone()
    # Odd environments deliberately move off the flat central spawn platform.
    xy[:, 0] += (ids % 2).float() * 1.7
    ceiling = float(ray.geometry.vertices[:, 2].max()) + 2.
    starts = torch.cat((xy, torch.full((len(ids), 1), ceiling, device=env.device)), dim=1)
    root_ground = ray.cast(starts[:, None].contiguous(), 10.)
    assert root_ground['hit'].all() and (root_ground['normal'][..., 2] > 0).all()
    frames = np.stack([tangent_frame(n) for n in root_ground['normal'][:, 0].cpu().numpy()])
    rotations = torch.as_tensor(frames, device=env.device, dtype=torch.float32)
    z = torch.empty(len(ids), device=env.device)
    minimum_clearance = float('inf')
    for first in range(0, len(ids), 64):
        last = min(first + 64, len(ids))
        offsets = torch.einsum('nij,pj->npi', rotations[first:last], bank['points'])
        footprint = offsets.clone()
        footprint[:, :, :2] += xy[first:last, None, :]
        footprint[:, :, 2] = ceiling
        surface = ray.cast(footprint.contiguous(), 10.)
        if not surface['hit'].all():
            raise RuntimeError('Sampled complete collider footprint outside real mesh')
        placed = (surface['height'] + .002 - offsets[:, :, 2]).amax(1)
        clear = placed[:, None] + offsets[:, :, 2] - surface['height']
        if not torch.isfinite(clear).all() or float(clear.min()) < .002 - 1e-5:
            raise RuntimeError('Sampled full-pose terrain placement is invalid')
        z[first:last] = placed
        minimum_clearance = min(minimum_clearance, float(clear.min()))
    q = bank['q'][None].repeat(len(ids), 1)
    robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)
    state = robot.data.root_state_w[ids].clone()
    state[:, :2] = xy; state[:, 2] = z
    state[:, 3:7] = torch.as_tensor(Rotation.from_matrix(frames).as_quat(), device=env.device, dtype=state.dtype)
    state[:, 7:] = 0.
    robot.write_root_state_to_sim(state, env_ids=ids)
    task.height_cmd(env)[ids] = .25
    env._mod4_ground_z = torch.zeros(env.num_envs, device=env.device) if not hasattr(env, '_mod4_ground_z') else env._mod4_ground_z
    env._mod4_ground_z[ids] = root_ground['height'][:, 0]
    if not hasattr(env, '_rough_probe_expected_q'):
        env._rough_probe_expected_q = torch.zeros((env.num_envs, 30), device=env.device)
    env._rough_probe_expected_q[ids] = q
    if not hasattr(env, '_rough_spawn_xy'):
        env._rough_spawn_xy = torch.zeros((env.num_envs, 2), device=env.device)
    env._rough_spawn_xy[ids] = xy
    env._rough_query_tick = None
    env._rough_probe_reset_receipt = dict(pose_index=bank['pose_index'], full_joint_names=robot.joint_names,
        qd_all_zero_requested=True, root_velocity_all_zero_requested=True,
        sample_points=bank['points'].shape[0], sampled_min_clearance_m=minimum_clearance,
        root_xyz=state[:, :3].cpu().tolist(), terrain_normal=root_ground['normal'][:, 0].cpu().tolist(),
        surface_sampling_not_continuous_nonpenetration=True)

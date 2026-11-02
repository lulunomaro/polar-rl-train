"""Trainable intro reset: original full-pose geometry, chunked complete footprint."""
import hashlib, json, numpy as np, torch
from pathlib import Path
from scipy.spatial.transform import Rotation
from e1_rough_reset_tensor import tangent_frame, joint_permutation
from e1_rough_ground import AuthoredTerrainRaycast
import mod4_task as task
A=Path(__file__).resolve().parent

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
    from curb20_entry_v3_runtime import reset_entry_xy
    xy = reset_entry_xy(env,ids)
    # Odd environments deliberately move off the flat central spawn platform.
    # Independent env grid already samples terrain; remove diagnostic off-platform offset.
    # No two robots are intentionally placed at the same XYZ.
    ceiling = float(ray.geometry.vertices[:, 2].max()) + 2.
    starts = torch.cat((xy, torch.full((len(ids), 1), ceiling, device=env.device)), dim=1)
    # Per-call grouping of identical reset XY only, not a persistent ground cache.
    unique_xy, inverse = torch.unique(xy,dim=0,return_inverse=True)
    unique_starts=torch.cat((unique_xy,torch.full((len(unique_xy),1),ceiling,device=env.device)),dim=1)
    unique_ground=ray.cast(unique_starts[:,None].contiguous(),10.)
    root_ground={k:v[inverse] for k,v in unique_ground.items()}
    work_xy=unique_xy
    work_ground=unique_ground
    assert root_ground['hit'].all() and (root_ground['normal'][..., 2] > 0).all()
    frames = np.stack([tangent_frame(n) for n in work_ground['normal'][:, 0].cpu().numpy()])
    rotations = torch.as_tensor(frames, device=env.device, dtype=torch.float32)
    z_unique = torch.empty(len(work_xy), device=env.device)
    minimum_clearance = float('inf')
    for first in range(0, len(work_xy), 64):
        last = min(first + 64, len(work_xy))
        offsets = torch.einsum('nij,pj->npi', rotations[first:last], bank['points'])
        footprint = offsets.clone()
        footprint[:, :, :2] += work_xy[first:last, None, :]
        footprint[:, :, 2] = ceiling
        surface = ray.cast(footprint.contiguous(), 10.)
        if not surface['hit'].all():
            raise RuntimeError('Sampled complete collider footprint outside real mesh')
        placed = (surface['height'] + .002 - offsets[:, :, 2]).amax(1)
        clear = placed[:, None] + offsets[:, :, 2] - surface['height']
        if not torch.isfinite(clear).all() or float(clear.min()) < .002 - 1e-5:
            raise RuntimeError('Sampled full-pose terrain placement is invalid')
        z_unique[first:last] = placed
        minimum_clearance = min(minimum_clearance, float(clear.min()))
    z=z_unique[inverse]
    frames=frames[inverse.cpu().numpy()]
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
    env._rough_probe_reset_receipt = dict(independent_CURB_entry=env._curb_entry_map_receipt,pose_index=bank['pose_index'], full_joint_names=robot.joint_names,
        qd_all_zero_requested=True, root_velocity_all_zero_requested=True,
        sample_points=bank['points'].shape[0], unique_reset_xy=len(unique_xy),
        reset_ray_grouping_within_current_call_only=True,persistent_ground_cache=False, sampled_min_clearance_m=minimum_clearance,
        root_xyz=state[:, :3].cpu().tolist(), terrain_normal=root_ground['normal'][:, 0].cpu().tolist(),
        surface_sampling_not_continuous_nonpenetration=True)

"""New isolated current-policy terrain reset/ground readback, not PPO.

Uses current frozen F plant without editing it. A diagnostic five-family mesh
replaces the plane only in this process. No training task or controller is installed.
"""
import argparse, json, sys, os, hashlib, time
from pathlib import Path
F = Path('/home/egde/rl_candidates/MOD4_PHYSICAL_DR_STAGE1_20261006')
A = Path('/home/egde/rl_candidates/MOD4_SCUT_ROUGH_V1_ADAPTER_20261002')
H = Path(__file__).resolve().parent
P = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
B = Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
cfg_env = json.loads((F / 'isaac/mod4/env.json').read_text())
for key, value in cfg_env.items(): os.environ[key] = str(value)
sys.path.insert(0, str(F / 'isaac/mod4')); sys.path.insert(0, str(F)); sys.path.insert(0, str(A)); sys.path.insert(0, str(H))
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app = AppLauncher(args).app

import numpy as np
import torch
from scipy.spatial.transform import Rotation
from rough_reset_tensor import tangent_frame, joint_permutation, cpu_contract
from rough_ground import AuthoredTerrainRaycast
from rough_recipe import make_terrain_cfg
import supervise_physical_dr_stage1 as owner
import mod4_task as task
from mod4_env import Mod4Env
from nominal_parameter_audit import parameter_audit
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg, RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg
from rsl_rl.runners import OnPolicyRunner
from importlib import metadata

def query(env):
    if not hasattr(env, '_rough_probe_query'):
        env._rough_probe_query = AuthoredTerrainRaycast(env.sim.stage, env.device)
    return env._rough_probe_query

def ground_update(env, env_ids=None):
    root = env.scene['robot'].data.root_pos_w
    out = query(env).cast(root[:, None, :].contiguous(), 4.)
    if not out['hit'].all(): raise RuntimeError('Actual rough root-ground ray miss; no stale-height fallback')
    env._mod4_ground_z = out['height'][:, 0]
    return env._mod4_ground_z

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
    offsets = torch.einsum('nij,pj->npi', rotations, bank['points'])
    footprint = offsets.clone(); footprint[:, :, :2] += xy[:, None, :]; footprint[:, :, 2] = ceiling
    surface = ray.cast(footprint.contiguous(), 10.)
    if not surface['hit'].all(): raise RuntimeError('Complete sampled collider footprint extends beyond real mesh')
    z = (surface['height'] + .002 - offsets[:, :, 2]).amax(1)
    clear = z[:, None] + offsets[:, :, 2] - surface['height']
    assert torch.isfinite(clear).all() and float(clear.min()) >= .002 - 1e-5
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
    env._rough_probe_reset_receipt = dict(pose_index=bank['pose_index'], full_joint_names=robot.joint_names,
        qd_all_zero_requested=True, root_velocity_all_zero_requested=True,
        sample_points=bank['points'].shape[0], sampled_min_clearance_m=float(clear.min()),
        root_xyz=state[:, :3].cpu().tolist(), terrain_normal=root_ground['normal'][:, 0].cpu().tolist(),
        surface_sampling_not_continuous_nonpenetration=True)

@torch.inference_mode()
def run():
    owner.verify(); owner.ctl.idle()
    assert owner.w.read(owner.w.STATE)['phase'] == 'physical_dr_stage1_review_ready'
    before = B.read_bytes()
    review = owner.w.read(owner.R / 'PHYSICAL_DR_STAGE1_REVIEW_READY.json')
    ck = Path(review['checkpoint']['path'])
    assert owner.base.sha(ck) == review['checkpoint']['sha256']
    cfg = task.Mod4EnvCfg(); cfg.scene.num_envs = 10; cfg.seed = 20261006
    terrain_cfg, recipe = make_terrain_cfg(10, seed=20261006, profile='intro_v1')
    terrain_cfg.terrain_generator.num_rows = 2; terrain_cfg.terrain_generator.num_cols = 5
    terrain_cfg.terrain_generator.use_cache = False
    cfg.scene.ground = None; cfg.scene.terrain = terrain_cfg
    cfg.scene.wheel_contact_scut.filter_prim_paths_expr = ['/World/ground/terrain/mesh']
    cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim = 64
    cfg.events.consistent_start.func = full_reset
    cfg.events.ground_track.func = ground_update
    cfg.sim.enable_scene_query_support = True; cfg.sim.physics.enable_scene_query_support = True
    # Process-local ground mapping only; the immutable flat module is not edited.
    task.ground_height = ground_update
    env = Mod4Env(cfg=cfg); vec = RslRlVecEnvWrapper(env, clip_actions=6.)
    robot = env.scene['robot']
    rc = RslRlOnPolicyRunnerCfg(seed=20261006, device=env.device, num_steps_per_env=24, max_iterations=1, save_interval=1,
        experiment_name='rough_reset_readback', run_name='frozen', clip_actions=6., check_for_nan=True, obs_groups={'actor':['policy'], 'critic':['critic']},
        policy=RslRlPpoActorCriticCfg(init_noise_std=.3, actor_hidden_dims=[256,128,64], critic_hidden_dims=[256,128,64], activation='elu'),
        algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2., use_clipped_value_loss=True, clip_param=.2, entropy_coef=.005, num_learning_epochs=5, num_mini_batches=4,
            learning_rate=1e-4, schedule='adaptive', gamma=.99, lam=.95, desired_kl=.01, max_grad_norm=1.))
    rc = handle_deprecated_rsl_rl_cfg(rc, metadata.version('rsl-rl-lib'))
    runner = OnPolicyRunner(vec, rc.to_dict(), log_dir=None, device=env.device); runner.load(str(ck))
    policy = runner.get_inference_policy(device=env.device)
    env.reset(); env.sim.forward(); env.scene.update(env.physics_dt)
    initial = parameter_audit(env)
    reset_receipt = env._rough_probe_reset_receipt
    q_error = float((robot.data.joint_pos - env._rough_probe_expected_q).abs().max())
    assert q_error < 1e-5
    cmd = env.command_manager.get_term('twist'); cmd.set_manual_evaluation_mode()
    alive = torch.ones(10, dtype=torch.bool, device=env.device)
    first_failure = torch.full((10,), -1, device=env.device, dtype=torch.long)
    closure = mimic = 0.; nonfinite = False
    body_scans = []; forward_scans = []; initial_xy = robot.data.root_pos_w[:, :2].clone()
    for step in range(300):
        cmd.time_left[:] = 1e9; cmd.is_standing_env[:] = False; cmd.is_heading_env[:] = False
        cmd.is_pure_spin[:] = False; cmd.is_moving_spin[:] = False; cmd.is_transition_spin[:] = False; cmd.command[:] = 0.
        cmd.command[:, 0] = torch.where(torch.arange(10, device=env.device) % 2 == 0, .3, -.3)
        task.height_cmd(env)[:] = .25
        ground_update(env)
        action = policy(vec.get_observations()); _, _, done, _ = vec.step(action)
        first_failure = torch.where(alive & done.bool(), torch.full_like(first_failure, step), first_failure)
        alive &= ~done.bool()
        nonfinite |= not bool(torch.isfinite(robot.data.joint_pos).all() and torch.isfinite(action).all())
        if step >= 10:
            closure = max(closure, float(torch.stack(list(task.closure_errors(env).values())).max()))
            mimic = max(mimic, float(torch.stack(list(task.mimic_errors(env).values())).max()))
        if step % 20 == 0:
            ids, _ = robot.find_bodies(['chassis', 'left_wheel', 'right_wheel'], preserve_order=True)
            points = robot.data.body_link_pos_w[:, ids].clone(); points[..., 2] += .5
            out = query(env).cast(points.contiguous(), 4.)
            body_scans.append(dict(step=step, hit_all=bool(out['hit'].all()), height=out['height'].cpu().tolist()))
            heading = robot.data.heading_w.torch
            grid = torch.cartesian_prod(torch.linspace(0., .8, 5, device=env.device), torch.tensor([-.25, 0., .25], device=env.device))
            starts = torch.empty((10, len(grid), 3), device=env.device)
            starts[:, :, 0] = robot.data.root_pos_w[:, 0, None] + torch.cos(heading)[:, None] * grid[None, :, 0] - torch.sin(heading)[:, None] * grid[None, :, 1]
            starts[:, :, 1] = robot.data.root_pos_w[:, 1, None] + torch.sin(heading)[:, None] * grid[None, :, 0] + torch.cos(heading)[:, None] * grid[None, :, 1]
            starts[:, :, 2] = robot.data.root_pos_w[:, 2, None] + 1.
            front = query(env).cast(starts.contiguous(), 4.)
            forward_scans.append(dict(step=step, hit_all=bool(front['hit'].all()), height=front['height'].cpu().tolist()))
        if nonfinite or not alive.all(): break
    final = parameter_audit(env)
    receipt = dict(stage='ISOLATED_ROUGH_LOW_SPEED_AND_FORWARD_SCAN_COMPONENT_READBACK', created_epoch=time.time(),
        pass_=not nonfinite and bool(alive.all()) and closure <= .002 and mimic <= .01 and all(x['hit_all'] for x in body_scans) and all(x['hit_all'] for x in forward_scans),
        checkpoint=review['checkpoint'], recipe=recipe, diagnostic_grid=[2,5], loaded_terrain=query(env).geometry.receipt(),
        all_30_joint_writeback_error=q_error, reset=reset_receipt, alive=alive.cpu().tolist(), first_failure_step=first_failure.cpu().tolist(),
        completed_steps=step+1, requested_steps=300, seconds=(step+1)*env.step_dt, nonfinite=nonfinite,
        max_closure_m=closure, max_mimic_rad=mimic, initial_parameter_audit=initial, final_parameter_audit=final,
        body_wheel_ground_readback=body_scans, forward_scan_readback=forward_scans, requested_body_vx_m_s=[.3 if i%2==0 else -.3 for i in range(10)], net_world_xy=(robot.data.root_pos_w[:, :2]-initial_xy).cpu().tolist(), cpu_contract=cpu_contract(),
        actual_ground_queries_no_plane_or_RMUC=True, canonical_bytes_unchanged=B.read_bytes()==before,
        ppo_performed=False, production_changed=False, rough_training_started=False,
        forward_scan_readback_verified_only=True, forward_scan_in_observation_or_reward=False, SCUT_airborne_reset_state_machine_installed=False,
        scope='New dynamic complete-pose reset and actual mesh root/body/wheel readback only. Three-second low-speed readback is not a complete route, terrain skill graduation, airborne reset, or training acceptance.')
    assert receipt['canonical_bytes_unchanged']
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(receipt, indent=2))
    env.close()
    print(json.dumps({k: receipt[k] for k in ('pass_', 'completed_steps', 'max_closure_m', 'max_mimic_rad', 'alive', 'canonical_bytes_unchanged')}), flush=True)

try:
    run()
except BaseException as error:
    import traceback
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix('.error.json').write_text(json.dumps(dict(error=repr(error), traceback=traceback.format_exc(), production_changed=False, ppo_performed=False)))
    raise
finally:
    app.close()

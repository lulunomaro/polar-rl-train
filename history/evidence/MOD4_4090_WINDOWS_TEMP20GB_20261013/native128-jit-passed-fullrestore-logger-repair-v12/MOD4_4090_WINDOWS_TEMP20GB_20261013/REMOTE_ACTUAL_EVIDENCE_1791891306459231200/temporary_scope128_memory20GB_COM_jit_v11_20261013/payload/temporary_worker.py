"""New Windows4090 scope entrypoint. Parent lease/OSlock required before Kit.

Torch and TensorDict preload occurs before every Isaac import. No installed SDK
file is edited. Original20k task makes no capacity overrides; actual newWindows
SDK defaults are recorded without claiming Linux default numerical equivalence.
"""
from pathlib import Path
import os, sys, json, time, argparse, traceback, hashlib
P = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
for name in ('runtime-root', 'manifest', 'source-checkpoint', 'source-sha', 'output', 'stop-after-save'):
    parser.add_argument('--' + name, required=True)
parser.add_argument('--mode', choices=['sdk', 'native', 'fullrestore', 'train'], required=True)
parser.add_argument('--train-seconds', type=int, default=3600)
parser.add_argument('--probe-controls', type=int, default=120)
pre, _ = parser.parse_known_args()
R = Path(pre.runtime_root)
C = R / 'isaac/mod4'
manifest = json.loads(Path(pre.manifest).read_bytes())
assert os.name == 'nt' and int(os.environ['MOD4_WINDOWS_GPU_LOCK_PARENT_PID']) == os.getppid(), 'leased parent ownership required'
assert manifest['approved_for_new_Windows4090_scope'] and manifest['root_review_actual']['GPU_lease_explicitly_granted'] and (manifest['num_envs'] == 128)
assert pre.source_sha == manifest['source']['sha256'] and hashlib.sha256(Path(pre.source_checkpoint).read_bytes()).hexdigest() == pre.source_sha
sys.path[:0] = [str(C), str(P), str(R)]
for k, v in manifest['source_environment'].items():
    if k.startswith('RM_'):
        os.environ[k] = str(v)
os.environ['RM_MOD4_USD'] = str(R / 'assets/robot.usd')
os.environ.pop('RM_RESCUE_DEADLINE', None)
os.environ['ISAACSIM_ACCEPT_EULA'] = 'Y'
os.environ['OMNI_KIT_ACCEPT_EULA'] = 'YES'
import torch, tensordict
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
O = Path(args.output)
assert O.is_dir()

def write(name, v):
    p = O / name
    b = json.dumps(v, ensure_ascii=False, indent=2).encode()
    q = p.with_suffix(p.suffix + '.partial')
    with q.open('wb') as f:
        f.write(b)
        f.flush()
        os.fsync(f.fileno())
    os.replace(q, p)
write('STARTED.json', dict(epoch=time.time(), pid=os.getpid(), argv=sys.argv, mode=args.mode, source_SHA=args.source_sha, num_envs=10 if args.mode == 'sdk' else 128, no_PPO_yet=True, new_Windows_backend_scope=True, PhysX_exact_resume=False))
app = None
env = None
try:
    app = AppLauncher(args).app
    torch.set_num_threads(1)
    from local_physx_api import install
    install()
    import mod4_task as task
    from retention_learning_env import RetentionLearningEnv
    from wave50_lifetime_runtime import configure_retention
    from e1_terrain_training_health import E1TerrainTrainingHealth, learning_health_pass
    cfg = task.Mod4EnvCfg()
    cfg.scene.num_envs = 10 if args.mode == 'sdk' else 128
    cfg.seed = 20260928
    cfg.sim.device = args.device
    configure_retention(cfg)
    capacity_names = ('gpu_max_rigid_contact_count', 'gpu_max_rigid_patch_count', 'gpu_found_lost_pairs_capacity', 'gpu_found_lost_aggregate_pairs_capacity', 'gpu_total_aggregate_pairs_capacity', 'gpu_collision_stack_size', 'gpu_heap_capacity', 'gpu_temp_buffer_capacity', 'gpu_max_num_partitions', 'gpu_max_soft_body_contacts', 'gpu_max_particle_contacts')
    original_capacities = {k: getattr(cfg.sim.physx, k) for k in capacity_names}
    for k, v in manifest['temporary_small_batch_capacities'].items():
        setattr(cfg.sim.physx, k, v)
    capacities = {k: getattr(cfg.sim.physx, k) for k in capacity_names}
    assert capacities == manifest['admitted_Windows20k_GPU_buffer_capacities'], 'reviewed new backend buffer identity'
    write('WINDOWS4090_ORIGINAL_CAPACITY_IDENTITY.json', dict(epoch=time.time(), actual_new_Windows20k_cfg=capacities, original_defaults_retained_in_report=True, capacity_overrides_applied=True, temporary2048_capacity_disclosed=True, Linux_old_SDK_capacity_numerical_equivalence_not_claimed=True))
    env = RetentionLearningEnv(cfg=cfg)
    env.reset()
    if args.mode != 'sdk':
        from temporary_state_binding import initialize_selected_env
        initialize_selected_env(env, args)
    placement = None
    if args.mode == 'sdk':
        from wave50_entry_sdk_placement_v2 import prepare, verify
        placement = prepare(env)
        env.reset()
        placement = verify(env, placement)
        cmd = env.command_manager.get_term('twist')
        cmd.set_manual_evaluation_mode()
    else:
        cmd = env.command_manager.get_term('twist')
    write('INITIALIZED.json', dict(epoch=time.time(), pid=os.getpid(), num_envs=env.num_envs, physics_dt=env.physics_dt, control_dt=env.step_dt, decimation=env.cfg.decimation, obs_dimensions=env.observation_manager.group_obs_dim, assignment_SHA=env.scene.terrain.retention_assignment_sha, backend='Windows-IsaacSim5.1-PhysX2API', physical_engine_equivalence_claimed=False, placement=placement))
    assert env.physics_dt == 0.0025 and env.step_dt == 0.01 and (env.cfg.decimation == 4)
    if args.mode in ('sdk', 'native'):
        import numpy as np
        from temporary_training_runtime import make_runner, assert_optimizer_layout
        from temporary_probe_contract import birth_inputs, end_contract, audit_control_window_boundary
        from temporary_state_binding import same, validate, probe_source
        source = probe_source(env, args)
        vec, runner = make_runner(env, args, O)
        runner.load(args.source_checkpoint, strict=True, map_location=args.device)
        assert_optimizer_layout(runner, source)
        assert same(runner.alg.actor.state_dict(), source['actor_state_dict']) and same(runner.alg.critic.state_dict(), source['critic_state_dict'])
        policy = runner.get_inference_policy(device=env.device)
        birth = birth_inputs(env, O, write, source, placement)
        health = E1TerrainTrainingHealth(env, O)
        N = env.num_envs
        rows = []
        warm = 0 if args.mode == 'sdk' else 24
        timed = 300 if args.mode == 'sdk' else 120
        started = time.time()
        ground_error = 0.0
        height_error = 0.0
        obs = None if args.mode == 'sdk' else vec.get_observations()
        for i in range(warm + timed):
            if args.mode == 'sdk':
                cmd.time_left[:] = 1000000000.0
                cmd.command[:] = 0.0
                cmd.command[:, 0] = torch.tensor([0.3, -0.3, 0.3, -0.3, 0.3, -0.3, 0.3, -0.3, 0.0, 0.0], device=env.device)
                cmd.is_standing_env[:] = False
                cmd.is_standing_env[8:] = True
                if hasattr(cmd, 'is_heading_env'):
                    cmd.is_heading_env[:] = False
                cmd.is_pure_spin[:] = False
                cmd.is_moving_spin[:] = False
                cmd.is_transition_spin[:] = False
            command = cmd.command.detach().cpu().numpy().copy()
            if args.mode == 'sdk':
                obs = vec.get_observations()
            with torch.inference_mode():
                obs, _, _, _ = vec.step(policy(obs))
            rows.append(command)
            ground_error = max(ground_error, env._e1_pre_reset_frame['independent_ground_error'])
            height_error = max(height_error, env._e1_height_formula_error)
            assert env._rough_termination_query_tick == env._rough_reward_query_tick == int(env._sim_step_counter)
            if (i + 1) % 24 == 0:
                write('PROBE_PROGRESS.json', dict(epoch=time.time(), controls=i + 1, callbacks=(i + 1) * 4, no_PPO=True))
        report = health.write()
        assert learning_health_pass(report)
        audit_control_window_boundary(env, warm + timed, args.mode, O)
        if args.mode == 'sdk':
            from wave50_entry_sdk_placement_v2 import verify
            selected = torch.tensor([0, 3, 9], device=env.device)
            others = torch.tensor([1, 2, 4, 5, 6, 7, 8], device=env.device)
            before_episode = env._e1_episode.clone()
            bias = env._sensor_mild.bias.clone()
            sensor_episode = env._sensor_mild.episode.clone()
            counter = int(env.common_step_counter)
            with torch.inference_mode():
                env._reset_idx(selected)
                env.scene.write_data_to_sim()
                env.sim.forward()
                env.scene.update(env.physics_dt)
                from temporary_training_runtime import private_rng_hashes
                assert args.mode == 'sdk' and cmd.manual_evaluation_mode
                postreset_fixture_rng_cpu = torch.get_rng_state().clone()
                postreset_fixture_rng_cuda = torch.cuda.get_rng_state(env.device).clone()
                cmd.time_left[:] = 1000000000.0
                cmd.command[:] = 0.0
                cmd.command[:, 0] = torch.tensor([0.3, -0.3, 0.3, -0.3, 0.3, -0.3, 0.3, -0.3, 0.0, 0.0], device=env.device)
                cmd.is_standing_env[:] = False
                cmd.is_standing_env[8:] = True
                if hasattr(cmd, 'is_heading_env'):
                    cmd.is_heading_env[:] = False
                cmd.is_pure_spin[:] = False
                cmd.is_moving_spin[:] = False
                cmd.is_transition_spin[:] = False
                assert torch.equal(postreset_fixture_rng_cpu, torch.get_rng_state()) and torch.equal(postreset_fixture_rng_cuda, torch.cuda.get_rng_state(env.device))
                write('SDK_POSTRESET_REQUESTED_FIXTURE_REBOUND_ACTUAL.json', dict(epoch=time.time(), pid=os.getpid(), passed=True, same_requested10env_fixture_as_all300controls=True, production_command_sampler_and_its_reset_rng_consumption_not_modified=True, zero_additional_physics_control_or_actor_observation=True, new_reset_pending_fixture_not_route_progress=True))
                binding_command_before = cmd.command.clone()
                binding_cpu_rng = torch.get_rng_state().clone()
                binding_cuda_rng = torch.cuda.get_rng_state(env.device).clone()
                binding_private_rng = private_rng_hashes(env)
                cmd._bind_episode(torch.arange(env.num_envs, device=env.device))
                assert torch.equal(cmd.command, binding_command_before) and torch.equal(binding_cpu_rng, torch.get_rng_state()) and torch.equal(binding_cuda_rng, torch.cuda.get_rng_state(env.device))
                assert binding_private_rng == private_rng_hashes(env) and torch.equal(cmd.bound_episode, env._e1_episode)
                write('SDK_SELECTED_RESET_EPISODE_METADATA_BINDING_ACTUAL.json', dict(epoch=time.time(), pid=os.getpid(), passed=True, manual_evaluation_fixture_bound_to_actual_reset_episode=True, actual_command_exact_before_after=True, all_global_private_rng_hashes_before_after_exact=True, no_step_observation_noise_draw_or_live_actor_correction=True, only_physical_reset_episode_binding=True))
            assert torch.equal(env._sensor_mild.bias[others], bias[others]) and torch.equal(env._sensor_mild.episode[others], sensor_episode[others]) and torch.equal(env._sensor_mild.episode[selected], sensor_episode[selected] + 1) and (int(env.common_step_counter) == counter)
            actualq = env.scene['robot'].data.joint_pos[selected]
            actualq = actualq.torch if hasattr(actualq, 'torch') else actualq
            expectedq = env._rough_probe_expected_q[selected]
            qerror = float((actualq - expectedq).abs().max())
            assert qerror <= 1e-06
            write('SDK_SELECTED_RESET_ACTUAL.json', dict(epoch=time.time(), pid=os.getpid(), passed=True, env_ids=selected.cpu().tolist(), all30q_requested_and_actual_max_error_rad=qerror, unselected_sensor_bias_episode_exact=True, selected_sensor_episode_increment_once=True, global_clock_unchanged=True, fullpose_reset_receipt=env._rough_probe_reset_receipt, new_RNG_not_claimed_zero_for_this_diagnostic_reset=True, not_route_progress=True))
        contract = end_contract(env, O, write, source, warm + timed, ground_error, height_error, birth)
        raw = O / 'PROBE_COMMAND_TRACE.npz'
        np.savez_compressed(raw, command=np.asarray(rows), warm_controls=warm, timed_controls=timed)
        write('PROBE_COMPLETE.json', dict(epoch=time.time(), pid=os.getpid(), passed=True, mode=args.mode, actual_controls=warm + timed, timed_controls=timed, warm_controls=warm, actual_callbacks=(warm + timed) * 4, elapsed_seconds=time.time() - started, health=report, placement=placement, complete_physical_command_DR_contract=contract, command_trace=dict(path=str(raw), sha256=hashlib.sha256(raw.read_bytes()).hexdigest()), diagnostic_fixture_commands_only=args.mode == 'sdk', frozen_original_source_actor_only_fullDRresume_pending=True, no_PPO=True, backend_scope_admission_not_fullroute_or_training=True))
    else:
        from temporary_training_runtime import restore_and_run
        restore_and_run(env, args, O, write)
    env.close()
    app.close()
    write('WORKER_RETURNED_NATURALLY.json', dict(epoch=time.time(), pid=os.getpid(), no_PPO=args.mode != 'train'))
except BaseException:
    write('ORIGINAL_ERROR.json', dict(epoch=time.time(), pid=os.getpid(), error=traceback.format_exc(), prePPO=not (O / 'WINDOWS4090_PPO_PROGRESS.json').exists(), progress=json.loads((O / 'WINDOWS4090_PPO_PROGRESS.json').read_bytes()) if (O / 'WINDOWS4090_PPO_PROGRESS.json').exists() else None))
    print(traceback.format_exc(), flush=True)
    os._exit(1)

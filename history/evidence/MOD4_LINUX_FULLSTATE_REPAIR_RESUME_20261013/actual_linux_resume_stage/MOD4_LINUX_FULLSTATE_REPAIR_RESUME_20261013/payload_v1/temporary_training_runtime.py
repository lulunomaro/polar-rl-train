"""Strict full20k restoration, one explicit left initializer, bounded PPO/save.

This is a new process scope. It never writes the original Linux canonical ledger.
"""
from pathlib import Path
import copy, json, os, time, hashlib
from importlib import metadata
import torch
from temporary_state_binding import materialize, same, H, validate, floating_count, DONOR_SHA
import left_head_offset_aware_migration_v3 as repair
MARKERS = {'SENSOR_RESUME_STARTUP_VERIFIED.json', 'DELAY_RESUME_STARTUP_VERIFIED.json', 'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json', 'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json', 'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json', 'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json', 'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json', 'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json', 'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json', 'E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json', 'E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json', 'E1_WAVE50_LIFETIME_RESUME_STARTUP_VERIFIED.json'}

class SavedWindowComplete(Exception):
    pass

def capture_original_first_observation(vec, is_training):
    if is_training:
        vec.episode_length_buf = torch.randint_like(vec.episode_length_buf, high=int(vec.max_episode_length))
    return vec.get_observations()

def install_first_observation_once(vec, initial_obs):
    original_get_obs = vec.get_observations
    first_obs_pending = True

    def first_observation_once():
        nonlocal first_obs_pending
        if first_obs_pending:
            first_obs_pending = False
            return initial_obs
        return original_get_obs()
    vec.get_observations = first_observation_once

def private_rng_hashes(env):
    out = {}

    def visit(v, path, depth):
        if isinstance(v, torch.Generator):
            out[path] = hashlib.sha256(v.get_state().cpu().numpy().tobytes()).hexdigest()
        elif depth > 0 and isinstance(v, dict):
            for k, x in v.items():
                visit(x, path + '/' + str(k), depth - 1)
        elif depth > 0 and isinstance(v, (list, tuple)):
            for i, x in enumerate(v):
                visit(x, path + '/' + str(i), depth - 1)
        elif depth > 0 and hasattr(v, '__dict__'):
            for k, x in vars(v).items():
                if k not in ('env', '_env', 'robot', '_asset', 'sensor', '_sensor', '_scene'):
                    visit(x, path + '/' + k, depth - 1)
    for k in ('_mild_dr', '_sensor_mild', '_feedback_delay_mild', '_physics_action_delay', '_spring_pressure', '_gas_damping', '_chassis_com', '_explicit_pd'):
        visit(getattr(env, k), k, 4)
    visit(env.command_manager.get_term('twist'), 'command_twist', 4)
    assert out, 'missing actual private generator inventory'
    return out

def CPU(v):
    if torch.is_tensor(v):
        return v.detach().cpu().clone()
    if isinstance(v, dict):
        return {k: CPU(x) for k, x in v.items()}
    if isinstance(v, list):
        return [CPU(x) for x in v]
    if isinstance(v, tuple):
        return tuple((CPU(x) for x in v))
    return copy.deepcopy(v)

def assert_optimizer_layout(runner, source):
    actor = list(runner.alg.actor.named_parameters())
    critic = list(runner.alg.critic.named_parameters())
    assert [name for name, _ in actor] == list(source['actor_state_dict'])
    assert [name for name, _ in critic] == list(source['critic_state_dict'])
    actual = runner.alg.optimizer.param_groups
    assert len(actual) == 1 and len(actual[0]['params']) == 17
    assert all((parameter is pair[1] for parameter, pair in zip(actual[0]['params'], actor + critic))), 'Adam IDs no longer map source actor then critic order'
    assert actor[0][0] == 'distribution.std_param' and actor[7][0] == 'mlp.6.weight' and (actor[8][0] == 'mlp.6.bias')

def make_runner(env, args, O):
    from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg, RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg
    from rsl_rl.runners import OnPolicyRunner
    assert env.num_envs in (10, 20000) and 0 < args.train_seconds <= 7200
    cfg = RslRlOnPolicyRunnerCfg(seed=20260928, device=args.device, num_steps_per_env=24, max_iterations=100000, obs_groups={'actor': ['policy'], 'critic': ['critic']}, save_interval=10, experiment_name='mod4_windows4090_temporary2048_repair', run_name=O.parent.name, clip_actions=6.0, check_for_nan=True, policy=RslRlPpoActorCriticCfg(init_noise_std=0.3, actor_hidden_dims=[256, 128, 64], critic_hidden_dims=[256, 128, 64], activation='elu'), algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=float(os.environ.get('RM_VALUE_LOSS_COEF', '1.0')), use_clipped_value_loss=True, clip_param=0.2, entropy_coef=float(os.environ.get('RM_ENTROPY_COEF', '.005')), num_learning_epochs=5, num_mini_batches=4, learning_rate=0.0001, schedule=os.environ.get('RM_SCHEDULE', 'adaptive'), gamma=0.99, lam=0.95, desired_kl=0.01, max_grad_norm=1.0))
    vec = RslRlVecEnvWrapper(env, clip_actions=6.0)
    cfg = handle_deprecated_rsl_rl_cfg(cfg, metadata.version('rsl-rl-lib'))
    runner = OnPolicyRunner(vec, cfg.to_dict(), log_dir=str(O), device=cfg.device)
    return (vec, runner)

def restore_and_run(env, args, O, write):
    assert env.num_envs == 20000
    max_formal_updates = json.loads(Path(args.manifest).read_bytes())['max_formal_updates']
    assert type(max_formal_updates) is int and max_formal_updates in (4, 256), 'Root approved finite save/trace resource bound'
    vec, runner = make_runner(env, args, O)
    path, binding = materialize(env, O, args, write)
    source = torch.load(path, map_location='cpu', weights_only=False)
    assert int(source['iter']) > 0
    runner.cfg['save_interval'] = int(source['iter']) + max_formal_updates + 1
    write('LINUX4090_SAVE2_RESOURCE_BOUND_ACTUAL.json', dict(max_formal_updates=max_formal_updates, legacy_automatic_save_interval_disabled_with_absolute_iteration_bound=True, runner_save_interval=runner.cfg['save_interval'], manual_fullsave_every2_updates=True, maximum_periodic_plus_final_files=129, source_iteration=int(source['iter']), no_optimizer_order_or_physics_change=True))
    runner.load(str(path), strict=True, map_location=args.device)
    assert_optimizer_layout(runner, source)
    for key, model in [('actor_state_dict', runner.alg.actor), ('critic_state_dict', runner.alg.critic)]:
        assert same(model.state_dict(), source[key]), key
    assert same(runner.alg.optimizer.state_dict(), source['optimizer_state_dict']) and runner.current_learning_iteration == source['iter']
    from wave50_lifetime_full_checkpoint import resume_e1_new_episode, install_e1_save_contract
    resume = resume_e1_new_episode(runner, env, str(path), str(O))
    files = {p.name: p for p in O.glob('*STARTUP_VERIFIED.json')}
    assert set(files) == MARKERS
    marker_rows = {k: json.loads(p.read_bytes()) for k, p in files.items()}
    for name, row in marker_rows.items():
        assert row['pid'] == os.getpid(), name
        if 'passed' in row:
            assert row['passed'], name
    assert same(runner.alg.actor.state_dict(), source['actor_state_dict']) and same(runner.alg.critic.state_dict(), source['critic_state_dict']) and same(runner.alg.optimizer.state_dict(), source['optimizer_state_dict'])
    assert torch.equal(env._e1_episode.cpu(), source['E1_terrain_state']['episode'] + 1)
    install_e1_save_contract(runner, env)
    legs = env.action_manager.get_term('legs')
    off = legs._offset.detach().clone()
    default = env.scene['robot'].data.default_joint_pos
    default = default.torch if hasattr(default, 'torch') else default
    assert off.shape == (20000, 4) and torch.equal(off, default[:, legs._joint_ids])
    admitted = json.loads(Path(args.manifest).read_bytes())['admitted_leg_offsets']
    expected = torch.tensor(admitted, device=env.device, dtype=off.dtype).expand(20000, 4)
    assert torch.equal(off, expected), 'actual API offset differs from reviewed fixture'
    repair.offsets_validate(off.cpu(), 20000)
    import mod4_task as task
    assert task.LEG_ORDER == ['left_crank', 'left_hip', 'right_crank', 'right_hip'] and task.LEG_ACTION_SCALE == repair.SCALE and (legs.diff_min == repair.LOWER) and (legs.diff_max == repair.UPPER)
    initial_obs = capture_original_first_observation(vec, args.mode == 'train')
    cpu_rng = torch.get_rng_state().clone()
    cuda_rng = torch.cuda.get_rng_state(env.device).clone()
    private_rng = private_rng_hashes(env)
    if args.source_sha == DONOR_SHA:
        obs = initial_obs
        with torch.inference_mode():
            old_mean = runner.alg.actor(obs).clone()
        candidate = repair.migrate_tree(source, source_sha=DONOR_SHA, actual_offsets=off.cpu())
        runner.alg.actor.load_state_dict(candidate['actor_state_dict'], strict=True)
        runner.alg.optimizer.load_state_dict(candidate['optimizer_state_dict'])
        with torch.inference_mode():
            new_mean = runner.alg.actor(obs).clone()
        assert torch.equal(old_mean[:, 1:], new_mean[:, 1:]) and same(runner.alg.critic.state_dict(), source['critic_state_dict'])
        oldtargets = repair.guarded_targets(old_mean, off)
        newtargets = repair.guarded_targets(new_mean, off)
        target_delta = float((oldtargets - newtargets).abs().max())
        assert target_delta <= 1e-06, 'unadmitted initial deterministic mechanical target change'
        actor_cpu = CPU(runner.alg.actor.state_dict())
        optimizer_cpu = CPU(runner.alg.optimizer.state_dict())
        assert same(actor_cpu, candidate['actor_state_dict']) and same(optimizer_cpu, candidate['optimizer_state_dict'])
        metadata_actual = dict(profile=repair.PROFILE, original_complete20k_donor_SHA=DONOR_SHA, initial_source_SHA=args.source_sha, num_envs=20000, applied_once_after_complete_source_restore=True, CPU_prepared_only=False, actual_GPU_API_offset_and_default_q_leg_order=off[0].cpu().tolist(), actual_API_offset_all_selected_exact=True, actual_initial_guarded_target_max_error_rad=target_delta, other5_means_std_and_hidden_critic_initially_exact=True, last_action_feedback_may_change_future_other5_outputs_without_weight_change=True, full_rollout_behavior_equivalence_not_claimed=True, initial_Adam_moment_row0_only_cleared_parameter_ids=[0, 7, 8], original_Adam_step_scalars_retained=True, same_repaired_resume_must_not_repeat_initializer=True, not_live_action_coupling_teacher_or_PhysX_exact_resume=True, qualification_claimed=False)
    else:
        metadata_actual = copy.deepcopy(source['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL'])
        assert metadata_actual['profile'] == repair.PROFILE
        assert metadata_actual['actual_GPU_API_offset_and_default_q_leg_order'] == off[0].cpu().tolist()
        metadata_actual['same_repaired_resume_source_SHA'] = args.source_sha
        metadata_actual['initializer_repeated_on_this_resume'] = False
    assert torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(cuda_rng, torch.cuda.get_rng_state(env.device)), 'initializer drew RNG'
    initial_actor = CPU(runner.alg.actor.state_dict())
    initial_critic = CPU(runner.alg.critic.state_dict())
    initial_opt = CPU(runner.alg.optimizer.state_dict())
    roundtrip = O / 'LEFT_HEAD_ACTUAL_CUDA_ACTOR_ADAM_ROUNDTRIP.pt'
    assert not roundtrip.exists()
    torch.save(dict(actor=initial_actor, critic=initial_critic, optimizer=initial_opt, metadata=metadata_actual), roundtrip)
    ck = torch.load(roundtrip, map_location='cpu', weights_only=False)
    runner.alg.actor.load_state_dict(ck['actor'], strict=True)
    runner.alg.critic.load_state_dict(ck['critic'], strict=True)
    runner.alg.optimizer.load_state_dict(ck['optimizer'])
    assert same(initial_actor, runner.alg.actor.state_dict()) and same(initial_critic, runner.alg.critic.state_dict()) and same(initial_opt, runner.alg.optimizer.state_dict())
    assert torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(cuda_rng, torch.cuda.get_rng_state(env.device))
    assert private_rng == private_rng_hashes(env), 'private streams changed inside initializer'
    install_first_observation_once(vec, initial_obs)
    write('LEFT_HEAD_ACTUAL_INIT_VERIFIED.json', dict(epoch=time.time(), pid=os.getpid(), passed=True, metadata=metadata_actual, roundtrip_SHA=H(roundtrip), no_RNG_draw_inside_initializer=True, private_RNG_hashes_before_and_after_exact=private_rng, normal_first_observation_captured_once_then_consumed_once=True, normal_train_initial_age_draw_once_before_first_observation=args.mode == 'train', no_extra_observation_for_proof=True, no_second_physical_reset=True, initialization_on_this_attempt=args.source_sha == DONOR_SHA))
    originalsave = runner.save
    updates = 0
    started_iteration = int(source['iter'])
    started = float(os.environ['MOD4_WINDOWS_PARENT_START_EPOCH'])
    deadline = time.monotonic() + max(0.0, args.train_seconds - (time.time() - started))
    backend_binding = copy.deepcopy(source['WINDOWS4090_TEMPORARY_BACKEND_BINDING'])

    def ownsave(path, *a, **k):
        path = Path(path)
        temp = path.with_name(path.name + '.saving.pt')
        originalsave(str(temp), *a, **k)
        saved = torch.load(temp, map_location='cpu', weights_only=False)
        saved['WINDOWS4090_TEMPORARY_BACKEND_BINDING'] = backend_binding
        saved['WINDOWS4090_TEMPORARY_BRANCH'] = copy.deepcopy(source['WINDOWS4090_TEMPORARY_BRANCH'])
        if 'WINDOWS4090_EXPANDED_ENV_BRANCH' in source:
            saved['WINDOWS4090_EXPANDED_ENV_BRANCH'] = copy.deepcopy(source['WINDOWS4090_EXPANDED_ENV_BRANCH'])
            saved['WINDOWS4090_EXPANDED_ENV_BRANCH'].update(all12_own_CPUCUDA_restore_disk_roundtrip_and_API_offsets_pending=False, actual_current_GPU_restore_verified=True)
        saved['LINUX4090_RECOVERY_ATTEMPT'] = dict(num_envs=env.num_envs, benchmark_only=json.loads(Path(args.manifest).read_bytes()).get('capacity_benchmark_only', False), original_parent128_final_SHA='f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3')
        saved['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL'] = metadata_actual
        saved['LINUX4090_FULLSCALE_BRANCH'] = copy.deepcopy(source['LINUX4090_FULLSCALE_BRANCH'])
        torch.save(saved, temp)
        with temp.open('r+b') as f:
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
        validate(saved, H(path))
        assert floating_count(saved) == 107
        changed = sum((not same(v, initial_actor[n]) for n, v in saved['actor_state_dict'].items()))
        deltas = [float(v['step'].item()) - float(initial_opt['state'][n]['step'].item()) for n, v in saved['optimizer_state_dict']['state'].items()]
        if updates:
            assert changed > 0 and min(deltas) > 0
        write('LINUX4090_LATEST_COMPLETE.json', dict(epoch=time.time(), pid=os.getpid(), path=str(path.resolve()), sha256=H(path), bytes=path.stat().st_size, source_SHA=args.source_sha, original_complete20k_donor_SHA=DONOR_SHA, finite_floating_tensors=107, perenv_tensor_fields=99, actual_updates=updates, actual_controls=updates * 24, actual_envsteps=updates * 24 * 20000, callbacks=updates * 24 * 4, actor_tensors_changed_since_postinit=len([n for n in saved['actor_state_dict'] if not same(saved['actor_state_dict'][n], initial_actor[n])]), optimizer_step_delta_min=min(deltas), complete_DR_globalnamed_dictprivate_CPUCUDA_state_saved=True, initialization_not_miscounted_as_PPO=True, formal_final=False))
    runner.save = ownsave
    runner.alg.learning_rate = runner.alg.optimizer.param_groups[0]['lr']
    write('LINUX4090_FULLSTATE_STARTUP_VERIFIED.json', dict(epoch=time.time(), pid=os.getpid(), passed=True, source_SHA=args.source_sha, num_envs=20000, all12_original_CPUCUDA_restore_markers=marker_rows, source_episode_plus_one=True, complete_original_donor_restored_before_explicit_initializer=True, source_binding=binding, backend_equivalence_not_claimed=True, PhysX_exact_resume=False))
    from e1_terrain_training_health import E1TerrainTrainingHealth, learning_health_pass
    health = E1TerrainTrainingHealth(env, O)
    if args.mode == 'fullrestore':
        runner.logger.init_logging_writer()
        assert hasattr(runner.logger, 'writer')
        from temporary_probe_contract import birth_inputs, end_contract
        birth = birth_inputs(env, O, write, source, None)
        ground_error = 0.0
        height_error = 0.0
        policy = runner.get_inference_policy(device=env.device)
        obs = vec.get_observations()
        for _ in range(args.probe_controls):
            with torch.inference_mode():
                obs, _, _, _ = vec.step(policy(obs))
            ground_error = max(ground_error, env._e1_pre_reset_frame['independent_ground_error'])
            height_error = max(height_error, env._e1_height_formula_error)
            assert env._rough_termination_query_tick == env._rough_reward_query_tick == int(env._sim_step_counter)
        report = health.write()
        assert learning_health_pass(report)
        contract = end_contract(env, O, write, source, args.probe_controls, ground_error, height_error, birth)
        runner.save(str(O / 'WINDOWS4090_REPAIRED_FULLRESTORE_COMPLETE.pt'))
        write('FULLRESTORE_PHYSICAL_PROBE_PASSED.json', dict(epoch=time.time(), pid=os.getpid(), passed=True, actual_controls=args.probe_controls, actual_callbacks=report['actual_physics_callbacks'], health=report, complete_physical_command_DR_contract=contract, no_PPO=True, latest=json.loads((O / 'LINUX4090_LATEST_COMPLETE.json').read_bytes()), initial_head_repair_not_learning_or_fullroute_certificate=True))
        runner.logger.stop_logging_writer()
        if runner.logger.writer is not None and runner.logger.logger_type == 'tensorboard':
            runner.logger.writer.flush()
            runner.logger.writer.close()
        return
    assert args.mode == 'train'
    write('LINUX4090_PPO_UNIQUE_COST_STARTED.json', dict(epoch=started, pid=os.getpid(), target_seconds=args.train_seconds, source_SHA=args.source_sha, canonical_authority_path='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json', canonical_reconciliation_pending=False, original_Linux_parent_owns_unique_canonical_segment=True))
    performance = []
    oldlog = runner.logger.log

    def measured_log(*a, **kw):
        result = oldlog(*a, **kw)
        row = dict(update=updates, collection_seconds=kw['collect_time'], learning_including_save_health_seconds=kw['learn_time'], num_envs=env.num_envs, steps=24 * env.num_envs)
        row['envsteps_per_second'] = row['steps'] / (row['collection_seconds'] + row['learning_including_save_health_seconds'])
        performance.append(row)
        write('CAPACITY_ACTUAL_PPO_TIMING.json', dict(epoch=time.time(), pid=os.getpid(), rows=performance, original_runner_loop_times_not_estimated=True, full5epochs4minibatches=True, benchmark_only=json.loads(Path(args.manifest).read_bytes()).get('capacity_benchmark_only', False)))
        return result
    runner.logger.log = measured_log
    oldupdate = runner.alg.update

    def update():
        nonlocal updates
        value = oldupdate()
        updates += 1
        runner.current_learning_iteration = started_iteration + updates - 1
        if updates % 2 == 0:
            runner.save(str(O / ('model_' + str(runner.current_learning_iteration) + '.pt')))
        report = health.write()
        write('LINUX4090_PPO_PROGRESS.json', dict(epoch=time.time(), pid=os.getpid(), actual_updates=updates, actual_controls=updates * 24, actual_envsteps=updates * 24 * 20000, physical_seconds_per_environment=updates * 0.24, health=report, formal_final=False))
        if (time.monotonic() >= deadline or Path(args.stop_after_save).exists() or health.reason is not None) or updates >= max_formal_updates:
            runner.save(str(O / ('model_' + str(runner.current_learning_iteration) + '.pt')))
            write('LINUX4090_PPO_FORMAL_FINAL_ACTUAL.json', dict(epoch=time.time(), pid=os.getpid(), passed=learning_health_pass(report), actual_updates=updates, actual_controls=updates * 24, health=report, stop_reason=health.reason or ('resource_guard_max256_updates' if updates >= max_formal_updates else 'human_or_parent_STOP_AFTER_SAVE' if Path(args.stop_after_save).exists() else 'bounded3600s_wall_window'), latest=json.loads((O / 'LINUX4090_LATEST_COMPLETE.json').read_bytes()), worker_cost_before_Kit_exit_seconds=time.time() - started, canonical_reconciliation_pending=False, max_formal_updates=max_formal_updates))
            raise SavedWindowComplete()
        return value
    runner.alg.update = update
    try:
        runner.learn(num_learning_iterations=100000, init_at_random_ep_len=False)
    except SavedWindowComplete:
        pass
    finally:
        write('LINUX4090_PPO_UNIQUE_COST_ENDED.json', dict(epoch=time.time(), pid=os.getpid(), started_epoch=started, worker_before_Kit_exit_seconds=time.time() - started, actual_updates=updates, canonical_reconciliation_pending=False, parent_EXIT_full_load_learn_save_exit_is_accounting_basis=True, no_budget_write_extension_refund_or_duplicate_charge=True))
        if hasattr(runner.logger, 'writer'):
            runner.logger.stop_logging_writer()
            writer = runner.logger.writer
            if writer is not None and getattr(runner.logger, 'logger_type', None) == 'tensorboard':
                writer.flush()
                writer.close()

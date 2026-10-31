"""Unused model-free actual MOD4/CAD admission, separate from frozen208 source.

80 fresh environments,8 controls/64 physics callbacks/16 feedback samples. No
actor,critic,optimizer,checkpoint load,training or20k fullstate slicing occurs.
Root owns target execution/private/shared/GPU/control lease and finite parent.
"""
from pathlib import Path
import argparse, hashlib, json, os, sys, time, traceback


def json_file(path):
    return json.loads(Path(path).read_bytes())


def put(path, value):
    with Path(path).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--job-root', required=True, type=Path)
    args = parser.parse_args(); job = args.job_root.resolve()
    task = json_file(job / 'ROBOT0PT208_V3_TASK.json')
    assert task['kind'] == 'NEW208_FULL_RM70_OWN_MOD4_ROBOT_ZERO_PT_V3'
    assert task['num_envs'] == 80 and task['controls'] == 8
    assert task['physics_callbacks'] == 64 and task['feedback_samples'] == 16
    assert task['model_opens'] == task['actor_calls'] == task['optimizer_updates'] == 0
    assert task['max_worker_seconds'] == 600
    assert task['actual_parent_exclusive_control_GPU_private_shared_admission'] is True
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == task['GPU_UUID']
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == task['worker_SHA']
    assert task['original_manifest_SHA'] == '0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
    manifest_path = job / 'original_run_manifest.json'
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == task['original_manifest_SHA']
    # Same original400N50Hz DR/task configuration. This is an explicitly fresh80
    # population for source/native admission, not a smaller resumed20k policy.
    original = json_file(manifest_path)
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK', 'WORLD_SIZE', 'LOCAL_RANK', 'MASTER_ADDR', 'MASTER_PORT'):
            del os.environ[key]
    actual_env = {k: str(v) for k, v in original['env'].items()
                  if k not in ('RM_RESCUE_DEADLINE', 'RM_RESCUE_STOP_FILE')}
    assert actual_env['RM_PHYSICS_DT_S'] == '0.0025'
    assert actual_env['RM_SOLVER_POS'] == '32' and actual_env['RM_SOLVER_VEL'] == '4'
    assert actual_env['RM_HEIGHT_MIN'] == actual_env['RM_HEIGHT_MAX'] == '.25'
    actual_env['RM_MOD4_USD'] = str(job / 'runtime/assets/robot.usd')
    os.environ.update(actual_env); os.environ['MOD4_RESUME_QUEUE_CONTROL_US'] = '20000'
    output = job / 'robot0pt208_v3'; output.mkdir(exist_ok=False)
    os.environ['MOD4_RM70_ORIGINAL_ASSET_ROOT'] = str(job / 'original_field')
    os.environ['MOD4_RM70_ASSET_RECEIPT'] = str(job / 'RM70_BINARY_INSTALL_ACTUAL.json')
    os.environ['MOD4_RM70_NEW_LAYOUT_ROOT'] = str(output / 'new_layout')
    os.environ['MOD4_NEW208_JOB_ROOT'] = str(job)
    storage = job / 'kit_isolation'; storage.mkdir(exist_ok=False)
    for name in ('data', 'DerivedDataCache'):
        (storage / name).mkdir()
    (storage / 'data/user.config.json').write_text('{}')
    os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT'] = str(storage)
    runtime = job / 'runtime'; mod = runtime / 'isaac/mod4'
    sys.path[:0] = [str(mod), str(runtime)]
    started = time.time(); env = None; app = None
    try:
        from launcher208 import IsolatedAppLauncher208
        launcher = IsolatedAppLauncher208(headless=True, device='cuda:0'); app = launcher.app
        import torch
        import mod4_task
        from config208_v3 import configure208
        from learning208_v3 import RetentionLearningEnv
        from e1_terrain_training_health import E1TerrainTrainingHealth, learning_health_pass
        cfg = mod4_task.Mod4EnvCfg(); cfg.scene.num_envs = 80; cfg.seed = 20260928
        recipe = configure208(cfg)
        env = RetentionLearningEnv(cfg=cfg)
        health = E1TerrainTrainingHealth(env, output)
        obs, info = env.reset()
        assert env.num_envs == 80 and env.physics_dt == .0025 and env.step_dt == .02
        assert cfg.decimation == 8 and cfg.episode_length_s == 20
        assert env._physics_action_delay.queue.control_us == 20000
        assert env.command_manager.get_term('twist')._dt == .02
        assert env.spring_pressure_recipe()['nominal_stiffness_N_m'] == 2000
        assert env._w35_gas400_selected_bank_compatibility['selected_pose_index'] == 34
        assert len(env._w35_gas400_asset_compatibility['authorized_four_scalar_changes']) == 4
        assert env.action_manager.total_action_dim == 6
        # Natural cached state and existing manager buffers, no contact getter or
        # body-force/root/velocity writes beyond the original full-pose reset.
        tick = int(env._integrated_contact.tick); fb = int(env._feedback_100hz_tick)
        apply = dict(env._physics_action_delay.calls)
        observed_reward_dt = []; original_reward = env.reward_manager.compute
        def reward(*args, **kwargs):
            dt = kwargs.get('dt', args[0] if args else None)
            assert dt == .02; observed_reward_dt.append(float(dt))
            return original_reward(*args, **kwargs)
        env.reward_manager.compute = reward
        original_terms = tuple(env.termination_manager.active_terms)
        pre_reset = []; actions = torch.zeros((80, 6), device=env.device, dtype=torch.float32)
        for control in range(8):
            if time.time() - started > 600:
                raise TimeoutError('NEW208 robot admission600s worker bound')
            before_tick = int(env._integrated_contact.tick); before_fb = int(env._feedback_100hz_tick)
            obs, rewards, terminated, truncated, extras = env.step(actions)
            assert int(env._integrated_contact.tick) - before_tick == 8
            assert int(env._feedback_100hz_tick) - before_fb == 2
            assert obs['policy'].shape == (80, 35) and obs['critic'].shape == (80, 38)
            assert all(bool(torch.isfinite(value).all()) for value in (
                obs['policy'], obs['critic'], rewards, env.scene['robot'].data.root_state_w,
                env.scene['robot'].data.joint_pos, env.scene['robot'].data.joint_vel))
            frame = env._e1_pre_reset_frame
            assert frame['root'].shape == (80, 13) and frame['q'].shape == (80, 30)
            pre_reset.append(dict(control=control, physics_tick=int(env._sim_step_counter),
                root0=frame['root'][0].detach().cpu().tolist(),
                original_non_timeout_events=int(terminated.sum()), original_timeout_events=int(truncated.sum()),
                original_reason_counts={name: int(env.termination_manager.get_term(name).sum()) for name in original_terms}))
        assert int(env._integrated_contact.tick) - tick == 64
        assert int(env._feedback_100hz_tick) - fb == 16
        delta = {name: int(env._physics_action_delay.calls[name] - apply[name]) for name in ('legs', 'wheels')}
        assert delta == {'legs': 64, 'wheels': 64}
        assert observed_reward_dt == [.02] * 8
        health_report = health.write()
        assert learning_health_pass(health_report), 'Original task health integrity rule failed; keep all ordinary resets'
        put(output / 'OWN_MOD4_ROBOT0PT208_V3_ACTUAL.json', dict(
            kind=task['kind'], passed=True, epoch=time.time(), model_opens=0, actor_calls=0,
            optimizer_updates=0, num_envs=80, controls=8, physics_callbacks=64, feedback_samples=16,
            processed_queue_calls_per_group=delta, actual_reward_dt=observed_reward_dt,
            source_configuration=recipe, actual_original_command=env.command_manager.get_term('twist').audit_retention(),
            source_physical_guards_unchanged=True, original_health_report=health_report,
            actual_complete_pose34_reset=True, actual_gas400_asset_four_scalar_compatibility=True,
            native_root_and_q_terminal_examples=pre_reset,
            actual_50Hz_queue_100Hz_feedback_400Hz_physics=True,
            actual_D0_D7_fresh80_source_native_integration=True,
            original20k_saved_DR_population_not_sliced=True,
            actual_PPO_fullstate_restore=False, actual20k_memory_admission=False,
            actual_native24_before_production_learning_still_required=True,
            full_RM70_skill=False, complete_SuperMimic_conversion=False))
    except BaseException:
        put(output / ('ORIGINAL_ROBOT0PT208_V3_ERROR_' + str(time.time_ns()) + '.json'), dict(
            traceback=traceback.format_exc(), model_opens=0, actor_calls=0, optimizer_updates=0))
        raise
    finally:
        if env is not None:
            env.close()
        if app is not None:
            app.close()


if __name__ == '__main__':
    main()

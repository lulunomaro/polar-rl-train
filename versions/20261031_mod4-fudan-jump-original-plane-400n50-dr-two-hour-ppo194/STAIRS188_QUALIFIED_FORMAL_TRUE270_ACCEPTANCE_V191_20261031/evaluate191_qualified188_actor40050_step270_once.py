"""Frozen delivered actor; existing normalized H1 plant and original 270 goal.

No learner, optimizer, state/velocity/force injection, or budget writer.
Only the first real episode of each environment is assessed.
"""
from pathlib import Path
import argparse, hashlib, io, json, os, runpy, sys, time, traceback

MODEL_SHA = 'bdd85c72b1b20c729333879e56e941b9ecc5e2d886ead345dcaf3c6bf9cd6f1d'
MODEL_PATH = '/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_STAIRS3_LITERAL_400N50_20261031v188_v2/seed27/production/model_final_complete.pt'
GPU = 'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
OUT = None


def put(name, value):
    with (OUT / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--job-root', type=Path, required=True)
    job = parser.parse_args().job_root.resolve()
    task = json.loads((job / 'FROZEN_EVAL191_TASK.json').read_bytes())
    assert task['model_SHA'] == MODEL_SHA and task['num_envs'] == 32
    assert task['max_controls'] == 1000 and task['model_GPU_decodes'] == 1
    assert task['no_learning_or_account_write'] and task['first_episode_only']
    assert os.environ['CUDA_VISIBLE_DEVICES'] == GPU
    OUT = job / 'actual_evaluation'
    OUT.mkdir()
    started = time.time()
    deadline = started + 720
    root = Path(task['qualified_existing_payload_root'])
    kit = job / 'kit_isolation'
    kit.mkdir()
    (kit / 'data').mkdir()
    (kit / 'DerivedDataCache').mkdir()
    (kit / 'data/user.config.json').write_text('{}', encoding='utf8')
    original = json.loads((root / 'job0/original_run_manifest.json').read_bytes())
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK', 'WORLD_SIZE', 'LOCAL_RANK', 'MASTER_ADDR', 'MASTER_PORT'):
            del os.environ[key]
    env = {key: str(value) for key, value in original['env'].items()
           if key not in ('RM_RESCUE_STOP_FILE', 'RM_RESCUE_DEADLINE')}
    env.update(RM_MOD4_USD=str(root / 'job0/assets/robot.usd'),
               RM_RESCUE_STOP_FILE=str(OUT / 'UNREQUESTED_STOP.json'),
               RM_RESCUE_DEADLINE=str(deadline), RM_KEEP_STD='1',
               RM_JUMP_SCRIPT_PROB='0', RM_MOD4_MAP='', RM_MOD4_TERRAIN='flat')
    os.environ.update(env)
    os.environ['MOD4_RESUME_QUEUE_CONTROL_US'] = '20000'
    os.environ['MOD4_EVAL191_OWN_KIT_STORAGE_ROOT'] = str(kit)
    put('ACTUAL_ENVIRONMENT_BEFORE_SDK.json', dict(
        original_manifest=str(root / 'job0/original_run_manifest.json'), environment=env,
        previous_H1_models_read=0, actual_selected_model=MODEL_PATH,
        source_training_policy_hz=50, target_policy_hz=50,
        source_nominal_gas_stiffness=2000, target_nominal_gas_stiffness=2000,
        goal_is_existing_original_H1_270_request_not_reward_or_policy_edit=True))
    mod = root / 'job0/runtime/isaac/mod4'
    sys.path[:0] = [str(job), str(root), str(root / 'lib'), str(mod), str(root / 'job0/runtime')]
    entry = mod / 'train_H1_ground_prelaunch_fullstate_v2.py'
    sys.argv = [str(entry), '--headless', '--device', 'cuda:0', '--num_envs', '32',
                '--seed', '20261031', '--log_root', str(OUT / 'unused_learning_logs')]
    ns = runpy.run_path(str(entry), run_name='frozen191_config_only_not_main')
    real = None
    try:
        import torch
        from spring_nominal_sdk_readback import tensor
        import h1_scut_fudan_jump_reward_v1 as old_reward_config
        import h1_step270_sdk_runtime_candidate as terrain
        old_configure = old_reward_config.configure
        old_reward_config.configure = lambda cfg: terrain.configure_rewards(cfg, old_configure)
        original_cfg = ns['Mod4EnvCfg']

        def cfg():
            c = original_cfg()
            c.scene.num_envs = 32
            c.seed = 20261031
            c.sim.device = 'cuda:0'
            c.terminations.mimic.params = {**c.terminations.mimic.params, 'threshold': .01}
            return c

        factory = ns['build_env']
        factory.__globals__.update(Mod4Env=terrain.H1Step270Env, Mod4EnvCfg=cfg)
        real = factory()
        real._physics_action_delay.queue.control_us = 20000
        assert real.num_envs == 32 and real.physics_dt == .0025 and real.step_dt == .02
        assert real.cfg.decimation == 8 and real._sim_step_counter == 0
        vec = ns['RslRlVecEnvWrapper'](real, clip_actions=6.)
        obs = vec.get_observations()
        assert obs['policy'].shape == (32, 35) and obs['critic'].shape == (32, 38)
        assert torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all()
        assert real.h1_phase.age_control.eq(0).all()
        robot = real.scene['robot']
        gas = real._spring_pressure
        drive = tensor(robot.root_view.get_dof_stiffnesses())[:, gas.ids].to(real.device)
        expected = gas.component.actual_stiffness(gas.nominal)
        damping = tensor(robot.root_view.get_dof_dampings())[:, gas.ids]
        limits = tensor(robot.root_view.get_dof_limits())[:, gas.ids]
        assert torch.equal(drive, expected) and expected.min() >= 1800 and expected.max() <= 2200
        assert real.spring_pressure_recipe()['nominal_stiffness_N_m'] == 2000
        assert real._physics_action_delay.queue.control_us == 20000
        wanted = limits.new_tensor([-.0267046843609, .020639440248416612]).expand(32, 2, 2)
        assert torch.equal(limits, wanted)
        assert list(real.cfg.events.gas_spring_preload.params['joint_names']) == ['left_gas_slide', 'right_gas_slide']
        preloads = real.cfg.events.gas_spring_preload.params['targets']
        terms = [dict(name=name, time_out=bool(real.termination_manager.get_term_cfg(name).time_out),
                      parameters=repr(real.termination_manager.get_term_cfg(name).params))
                 for name in real.termination_manager.active_terms]
        assert any(name['name'] == 'closure' and '.002' in name['parameters'] for name in terms)
        put('ACTUAL_400N50_DR_ORIGINAL_270_BEFORE_ACTOR.json', dict(
            passed=True, physics_dt=real.physics_dt, policy_dt=real.step_dt,
            decimation=real.cfg.decimation, physics_hz=400, policy_hz=50, feedback_hz=100,
            nominal_gas_stiffness_N_m=gas.nominal.cpu().tolist(), nominal_400N_each_engineering=True,
            actual_gas_stiffness_N_m=drive.cpu().tolist(), actual_gas_damping=damping.cpu().tolist(),
            actual_gas_limits=limits.cpu().tolist(), preload_targets=preloads,
            spring_profile=real.spring_pressure_recipe(), gas_damping_profile=real.gas_damping_recipe(),
            chassis_PD_profile=real.chassis_pd_recipe(), sensor_profile=real._sensor_mild.receipt(),
            feedback_profile=real.feedback_delay_recipe(), physical_action_delay=real.action_delay_recipe(),
            mild_DR_profile=real._mild_dr.profile, mild_DR_ranges=real._mild_dr.recipe,
            sampled_mass_factors=real._mild_dr.factor.cpu().tolist(), sampled_wheel_friction=real._mild_dr.mu.tolist(),
            geometry=real.step270_geometry_receipt, original_terminations=terms,
            observation_terms=list(real.observation_manager.active_terms['policy']),
            observation_dimensions=[list(map(int, x)) for x in real.observation_manager.group_obs_term_dim['policy']],
            observation_initial=obs['policy'].cpu().tolist(),
            no_learned_observation_normalizer_in_delivered_checkpoint=True,
            original_fixed_observation_scales_retained=True,
            source_adapted400N50_DR_on_original_Fudan_stairs3=True,
            reward_computation_is_existing_H1_diagnostic_only_no_learning=True))
        model = Path(MODEL_PATH)
        stat0 = model.stat()
        with model.open('rb') as f:
            raw = f.read()
        stat1 = model.stat()
        assert (stat0.st_size, stat0.st_mtime_ns) == (stat1.st_size, stat1.st_mtime_ns)
        assert len(raw) == 18137745 and hashlib.sha256(raw).hexdigest() == MODEL_SHA
        ck = torch.load(io.BytesIO(raw), map_location='cuda:0', weights_only=True)
        del raw
        assert ck['iter'] == 5065
        actor = torch.nn.Sequential(torch.nn.Linear(35, 256), torch.nn.ELU(),
                                    torch.nn.Linear(256, 128), torch.nn.ELU(),
                                    torch.nn.Linear(128, 64), torch.nn.ELU(), torch.nn.Linear(64, 6)).to(real.device)
        actor_sd = ck['actor_state_dict']
        weights = {key.removeprefix('mlp.'): value for key, value in actor_sd.items() if key.startswith('mlp.')}
        assert len(weights) == 8 and set(actor_sd) == {('mlp.' + key) for key in weights} | {'distribution.std_param'}
        actor.load_state_dict(weights, strict=True)
        assert all(torch.equal(value, actor.state_dict()[key]) for key, value in weights.items())
        assert all(torch.isfinite(value).all() for value in actor.parameters())
        actor.eval()
        put('ACTUAL_QUALIFIED188_GPU_ACTOR_LITERAL_RESTORE.json', dict(
            passed=True, source_path=MODEL_PATH, source_SHA=MODEL_SHA, bytes=stat0.st_size,
            model_file_reads=1, checkpoint_GPU_decodes=1, previous_CPU_admission_reexecuted=False,
            actor_weights_exact=True, mean_policy_no_exploration=True,
            preserved_saved_STD=actor_sd['distribution.std_param'].cpu().tolist(),
            learned_observation_normalizer_tensors=0, optimizer_constructed=False,
            source_iteration=5065, actor_input=35, actor_output=6, raw_clip=6))
        del ck, actor_sd, weights
        n = real.num_envs
        device = real.device
        active = torch.ones(n, dtype=torch.bool, device=device)
        zeros = torch.zeros(n, device=device)
        integer = torch.zeros(n, dtype=torch.long, device=device)
        seen_peak = zeros.clone()
        root_initial = tensor(robot.data.root_state_w).clone()
        root_peak = root_initial[:, 2].clone()
        flight_ticks = integer.clone()
        longest_air = integer.clone()
        flight_vz = active.clone().fill_(False)
        crossed = torch.zeros((n, 2), dtype=torch.bool, device=device)
        strict_cross = active.clone().fill_(False)
        land_ticks = integer.clone()
        landed = active.clone().fill_(False)
        stable_ticks = integer.clone()
        stable_peak = integer.clone()
        strict_success = active.clone().fill_(False)
        original_success = active.clone().fill_(False)
        original_edge = active.clone().fill_(False)
        original_landed = active.clone().fill_(False)
        original_takeoff = integer.clone()
        physical_exposure = integer.clone()
        request_exposure = integer.clone()
        action_overflow = integer.clone()
        endpoint_controls = integer.clone()
        initial_lo, initial_hi = terrain.wheel_bounds(real)
        previous_front = initial_hi[:, :, 0].clone()
        terminal_rows = {}
        samples = []
        physical_calls = 0
        original_physical = real.h1_phase.physical

        def observed_physical(**kw):
            nonlocal physical_calls, flight_ticks, longest_air, flight_vz, crossed
            nonlocal previous_front, strict_cross, land_ticks, landed, stable_ticks
            nonlocal stable_peak, strict_success, original_success, original_edge, original_landed
            value = original_physical(**kw)
            physical_calls += 1
            p = real.h1_phase
            measured = p.last_measured
            lo, hi = measured['step_wheel_min'], measured['step_wheel_max']
            root = tensor(robot.data.root_state_w)
            airborne = (kw['wheel_N'] <= 1).all(-1) & (lo[:, :, 2] > .005).all(-1)
            airborne &= (kw['nonwheel_max_N'] <= 1) & (kw['all_min_clear_m'] > 0) & active
            physical_exposure.add_(active.long())
            request_exposure.add_((p.request_for_action & active).long())
            seen_peak.copy_(torch.maximum(seen_peak, torch.where(active, lo[:, :, 2].amin(-1), zeros)))
            root_peak.copy_(torch.maximum(root_peak, torch.where(active, root[:, 2], root_initial[:, 2])))
            flight_ticks = torch.where(airborne, flight_ticks + 1, integer)
            longest_air = torch.maximum(longest_air, flight_ticks)
            flight_vz = airborne & (flight_vz | (kw['root_vz'] > .05))
            crossed &= airborne[:, None]
            edge = real.scene.env_origins[:, 0, None] + .35
            wheel_cross = (previous_front < edge) & (hi[:, :, 0] >= edge)
            crossed |= wheel_cross & airborne[:, None] & (lo[:, :, 2] >= .27)
            strict_cross |= active & crossed.all(-1) & flight_vz & (flight_ticks >= 16) & p.goal.launched
            previous_front = hi[:, :, 0].clone()
            original_takeoff.copy_(torch.maximum(original_takeoff, torch.where(active, p.takeoff_count, integer)))
            original_edge |= active & p.goal.edge
            original_landed |= active & p.goal.landed
            original_success |= active & p.goal.success
            on_top = (kw['wheel_N'] > 1).all(-1) & measured['step_platform_contact'].all(-1)
            on_top &= measured['step_footprint_inside'].all(-1) & (lo[:, :, 2] >= .269).all(-1)
            on_top &= (kw['nonwheel_max_N'] <= 1) & active
            land_ticks = torch.where(strict_cross & on_top, land_ticks + 1, integer)
            landed |= land_ticks >= 12
            heading = torch.atan2(torch.sin(kw['yaw'] - p.yaw_reference), torch.cos(kw['yaw'] - p.yaw_reference))
            stable = landed & on_top & (kw['root_vz'].abs() <= .03) & (kw['root_planar_speed'] <= .03)
            stable &= (kw['roll'].abs() < .17453292519943295) & (kw['pitch'].abs() < .17453292519943295) & (heading.abs() < .2)
            stable_ticks = torch.where(stable, stable_ticks + 1, integer)
            stable_peak = torch.maximum(stable_peak, stable_ticks)
            strict_success |= active & (stable_ticks >= 200) & p.goal.success
            return value

        real.h1_phase.physical = observed_physical
        original_terminal = real.termination_manager.compute

        def terminal(*args, **kwargs):
            result = original_terminal(*args, **kwargs)
            manager = real.termination_manager
            done = manager.terminated | manager.time_outs
            stopped = done & active
            if stopped.any():
                root = tensor(robot.data.root_state_w)
                for i in torch.nonzero(stopped, as_tuple=False).flatten().cpu().tolist():
                    terminal_rows[str(i)] = dict(
                        control=int(real.common_step_counter), physical_seconds=int(physical_exposure[i]) * .0025,
                        flags={name: bool(manager.get_term(name)[i]) for name in manager.active_terms},
                        root13=root[i].cpu().tolist(), original_public_age_100Hz=int(real.h1_phase.age_control[i]),
                        original_goal_success=bool(real.h1_phase.goal.success[i]),
                        strict_jump270_stable=bool(strict_success[i]))
                active[stopped] = False
            return result

        real.termination_manager.compute = terminal
        tick0, fb0 = int(real._integrated_contact.tick), int(real._feedback_100hz_tick)
        completed = 0
        with torch.inference_mode():
            for control in range(task['max_controls']):
                if time.time() >= deadline:
                    break
                x = obs['policy']
                assert x.shape == (n, 35) and torch.isfinite(x).all()
                action = actor(x)
                assert action.shape == (n, 6) and torch.isfinite(action).all()
                action_overflow.add_((action.abs().gt(6).any(-1) & active).long())
                endpoint_controls.add_(active.long())
                # Retired first episodes are excluded from inference outcomes. Their
                # automatic resets remain the unmodified original environment behavior.
                obs, reward, done, extras = vec.step(action)
                completed += 1
                assert torch.isfinite(obs['policy']).all() and torch.isfinite(reward).all()
                if completed in (1, 25, 50, 75, 90, 100, 200, 400, 600, 800, 1000):
                    row = dict(control=completed, physical_seconds=completed * .02,
                               first_episodes_alive=int(active.sum()), original_edge=int(original_edge.sum()),
                               strict_same_flight_cross=int(strict_cross.sum()),
                               strict_jump270_stable=int(strict_success.sum()),
                               max_both_wheel_bottom_400Hz_m=float(seen_peak.max()))
                    samples.append(row)
                    print(json.dumps(dict(stage='FROZEN_PLAN191_EVALUATION', **row)), flush=True)
                if not active.any():
                    break
        assert completed > 0 and physical_calls == completed * 8
        assert int(real._integrated_contact.tick) - tick0 == completed * 8
        assert int(real._feedback_100hz_tick) - fb0 == completed * 2
        root_final = tensor(robot.data.root_state_w).clone()
        rows = []
        for i in range(n):
            rows.append(dict(env_id=i, first_episode_terminal=terminal_rows.get(str(i)),
                             censored_at_bound=bool(active[i]), controls_observed=int(endpoint_controls[i]),
                             physical_callbacks_observed=int(physical_exposure[i]),
                             request_physics_callbacks=int(request_exposure[i]),
                             both_wheel_common_peak_400Hz_m=float(seen_peak[i]),
                             root_peak_net_m=float(root_peak[i] - root_initial[i, 2]),
                             longest_continuous_contact_clean_air_callbacks=int(longest_air[i]),
                             source_original_takeoff_counter=int(original_takeoff[i]),
                             original_both_leading_edges_cross=bool(original_edge[i]),
                             original_top_landing=bool(original_landed[i]),
                             original_goal_success=bool(original_success[i]),
                             strict_same_continuous_flight_dualwheel270_cross=bool(strict_cross[i]),
                             strict_top_landing12=bool(landed[i]), stable_top_callbacks_peak=int(stable_peak[i]),
                             strict_jump270_stable=bool(strict_success[i]),
                             raw_actor_overflow_controls=int(action_overflow[i]),
                             initial_root13=root_initial[i].cpu().tolist(),
                             current_root13_or_postreset=root_final[i].cpu().tolist()))
        flags = {}
        for value in terminal_rows.values():
            for name, flag in value['flags'].items():
                flags[name] = flags.get(name, 0) + int(flag)
        result = dict(passed_execution=True, stage='QUALIFIED188_TOTALPLAN_400N50_DR_270_EVAL191',
                      model_SHA=MODEL_SHA, model_file_reads=1, checkpoint_GPU_decodes=1,
                      optimizer_constructed=False, optimizer_steps=0, ledger_writes=0,
                      num_envs=n, policy_controls=completed, physics_callbacks=physical_calls,
                      total_physical_duration_s=completed * .02,
                      first_episodes_completed=len(terminal_rows), first_episodes_censored=int(active.sum()),
                      all_initial_cases_covered=len(terminal_rows) + int(active.sum()) == n,
                      termination_counts=flags, strict_successful_cases=int(strict_success.sum()),
                      strict_same_flight_cross_cases=int(strict_cross.sum()),
                      original_successful_cases=int(original_success.sum()),
                      maximum_common_both_wheel_peak_400Hz_m=float(seen_peak.max()),
                      source_training_max_stair_height_m=.21, source270_skill_not_previously_proved=True,
                      not_full_DR_population_skill_graduation=True, cases=rows, progress=samples,
                      wall_time_s=time.time() - started, errors=[])
        put('ACTUAL191_FROZEN188_400N50_DR_TRUE270_RESULTS.json', result)
        put('FUNCTION_RETURNED.json', dict(passed=True, actual_controls=completed,
                                         actual_physics_callbacks=physical_calls, errors=[]))
        print(json.dumps({key: value for key, value in result.items() if key not in ('cases', 'progress')}), flush=True)
    finally:
        if real is not None:
            real.close()
        put('APP_CLOSING.json', dict(epoch=time.time(), original_environment_closed=real is not None))
        ns['app'].close()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        if OUT is not None:
            put('ORIGINAL_EVALUATION_ERROR.json', dict(epoch=time.time(), traceback=traceback.format_exc(),
                                                     no_automatic_retry=True, no_policy_or_physics_patch=True))
        raise

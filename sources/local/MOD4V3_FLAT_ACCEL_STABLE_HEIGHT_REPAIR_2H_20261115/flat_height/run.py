"""Finite PPO owner and independent deterministic admission/evaluation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time
import traceback


def put(path, value):
    path = Path(path)
    temp = path.with_name(path.name + '.partial')
    with temp.open('w', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def equal_state(left, right):
    import torch
    if torch.is_tensor(left):
        return torch.is_tensor(right) and torch.equal(left.to(right.device), right)
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(equal_state(v, right[k]) for k, v in left.items())
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(equal_state(a, b) for a, b in zip(left, right))
    return left == right


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--job', required=True)
    parser.add_argument('--mode', choices=['admit', 'train', 'evaluate'], required=True)
    parser.add_argument('--num-envs', type=int, default=64)
    parser.add_argument('--checkpoint')
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_bytes())
    job = Path(args.job)
    job.mkdir(parents=True, exist_ok=False)
    storage = job / 'kit_isolation'
    (storage / 'data').mkdir(parents=True)
    (storage / 'DerivedDataCache').mkdir()
    (storage / 'data/user.config.json').write_text('{}')
    os.environ.update(MOD4V1_E0_JOB_ROOT=str(job), MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),
                      MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],
                      OMNI_KIT_ACCEPT_EULA='YES', ISAACSIM_ACCEPT_EULA='Y')
    sys.path[:0] = [plan['root'], plan['runtime'], plan['shared_package'], plan['package'], plan['base_support']]
    app = env = None
    outcome = 'failed'
    try:
        from launcher_mod4v1_e0 import IsolatedAppLauncher208
        app = IsolatedAppLauncher208(dict(headless=True, device='cuda:0', enable_cameras=False)).app
        import numpy as np
        import torch
        from tensordict import TensorDict
        from rsl_rl.runners import OnPolicyRunner
        from mod4v1_scut.config import runner_config
        from mod4v3_ppo_v1.model import metadata, reset_bank
        from mod4v3_ppo_v1.scut_flat_env import tensor
        from mod4v3_ppo_v1.sampling import Sampling
        from .env import FlatHeightEnv
        from .objective import SCHEMA, SLOTS
        from .terrain import configuration
        from .policy_repair import initialize, bound_exploration, in_bounds
        seed = plan['seed'] if args.mode == 'train' else plan['evaluation_seed']
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        verified = {}
        for name, row in plan['asset_identity']['actual_training_assets'].items():
            digest = hashlib.sha256((Path(plan['package']) / 'assets' / name).read_bytes()).hexdigest()
            assert digest == row['sha256'], name
            verified[name] = digest
        assert hashlib.sha256((Path(plan['package']) / 'mjcf/scene.xml').read_bytes()).hexdigest() == plan['asset_identity']['local_mjcf_sha256']
        for row in plan['terrain_inputs']:
            assert hashlib.sha256((Path(plan['root']) / row['path']).read_bytes()).hexdigest() == row['sha256']
        meta = metadata(plan['package'])
        bank = reset_bank(plan['package'], plan['reset_bank'])
        env = FlatHeightEnv(configuration(meta, bank, args.num_envs, seed), meta, bank)
        env.evaluation, env.admission = args.mode == 'evaluate', args.mode == 'admit'
        env.render_enabled = False
        env.reset()
        env.sample = Sampling(env)
        parity = env.sample.parity()
        assert env.enforce_closure_reset and abs(env.step_dt - .02) < 1e-9
        assert abs(env.physics_dt - .0025) < 1e-9
        assert (env.leg_pd_decimation, env.wheel_pd_decimation) == (4, 1)
        limits = tensor(env.robot.root_view.get_dof_limits())
        stiff = tensor(env.robot.root_view.get_dof_stiffnesses())
        damping = tensor(env.robot.root_view.get_dof_dampings())
        contract = json.loads((Path(plan['package']) / 'assets/import_contract.json').read_bytes())
        for name, row in contract['joints'].items():
            for wanted, actual in zip(row['limits_si'], limits[0, env.robot.joint_names.index(name)]):
                if wanted is not None:
                    assert abs(float(actual) - wanted) < 2e-6, name
        assert bool((stiff[:, env.active_ids] == 0).all())
        assert bool((damping[:, env.active_ids] == 0).all())
        assert bool((stiff[:, env.gas_ids] == 2000).all())
        assert bool(((damping[:, env.gas_ids] >= 1.5) & (damping[:, env.gas_ids] <= 4.5)).all())
        current = env._get_observations()

        class Vec:
            num_envs = env.num_envs
            num_actions = 6
            device = env.device
            max_episode_length = env.max_episode_length
            cfg = env.cfg

            @property
            def episode_length_buf(self):
                return env.episode_length_buf

            def get_observations(self):
                return TensorDict(current, batch_size=[env.num_envs])

        cfg = runner_config()
        cfg['num_steps_per_env'] = plan['training_round']['rollout']
        cfg['clip_actions'] = 6.
        for key in ('learning_rate', 'schedule', 'clip_param', 'num_learning_epochs', 'value_loss_coef', 'entropy_coef'):
            cfg['algorithm'][key] = plan['training_round'][key]
        runner = OnPolicyRunner(Vec(), cfg, log_dir=None, device=env.device)
        algorithm = runner.alg
        path = Path(args.checkpoint or plan['parent'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not args.checkpoint:
            assert digest == plan['parent_sha256']
        data = torch.load(path, map_location=env.device, weights_only=False)
        assert data['action_order'] == env.order
        algorithm.load(data, load_cfg=None, strict=True)
        for key, model in (('actor_state_dict', algorithm.actor), ('critic_state_dict', algorithm.critic)):
            actual = model.state_dict()
            assert all(torch.equal(actual[k], value) for k, value in data[key].items())
        assert len(algorithm.optimizer.state) == len(data['optimizer_state_dict']['state']) > 0
        assert equal_state(data['optimizer_state_dict'], algorithm.optimizer.state_dict())
        if args.checkpoint:
            assert data['observation_schema'] == SCHEMA
        adaptation = dict(actor_critic_STD_Adam_restored_exactly=True, parameter_transformations=False,
                          retained_old_phase_input_roles=True, producer='spring_aware_preparation_v1',
                          parent_schema=data.get('observation_schema'))
        if digest == plan['parent_sha256']:
            adaptation = initialize(algorithm)
        else:
            assert in_bounds(algorithm.actor.distribution.std_param)
        iteration = data['iter']
        physics_ticks = int(data.get('physics_ticks', 0))
        if args.mode == 'train':
            random.setstate(data['python_rng'])
            np.random.set_state(data['numpy_rng'])
            torch.set_rng_state(data['cpu_rng'].cpu())
            torch.cuda.set_rng_state_all([v.cpu() for v in data['cuda_rng']])
            env.reset_generator.set_state(data['reset_rng'].cpu())
            if 'effort_generator_rng' in data:
                env.full_dr.effort_generator.set_state(data['effort_generator_rng'].cpu())
        algorithm.learning_rate = plan['training_round']['learning_rate']
        for group in algorithm.optimizer.param_groups:
            group['lr'] = algorithm.learning_rate
        env.reset()
        current = env._get_observations()
        assert current['policy'].shape == (env.num_envs, 35)
        assert current['critic'].shape == (env.num_envs, 78)
        put(job / 'STARTUP.json', dict(epoch=time.time(), mode=args.mode, seed=seed,
            parent=str(path), parent_sha256=digest, parent_iteration=iteration,
            interface=[35, 78, 6], observation_schema=SCHEMA, task_slots=SLOTS,
            adaptation=adaptation, optimizer_entries=len(algorithm.optimizer.state),
            num_envs=env.num_envs, asset_hashes=verified, sampling=parity,
            physics_dt_s=.0025, leg_hz=100, wheel_hz=400, policy_hz=50,
            closure_reset_m=.01, mimic_reset_rad=.01, motor_phase_schedule=False,
            teacher_actions=False, task=plan['task'], source_archive_sha256=plan['source_archive_sha256'],
            DR=env.full_dr.summary(), PPO=cfg, reset=env.reset_distribution_summary()))
        obs = TensorDict(current, batch_size=[env.num_envs])

        def check_physics_log():
            console = job.parent / (job.name + '.log')
            if console.exists():
                text = console.read_text(errors='replace')
                assert 'PhysX error:' not in text, 'PhysX runtime reported an error; this segment cannot be accepted'

        if args.mode != 'train':
            algorithm.eval_mode()
            seen = torch.zeros(env.num_envs, device=env.device, dtype=torch.bool)
            rows, traces = [], []
            torque_peak = torch.zeros(6, device=env.device)
            with torch.inference_mode():
                for step in range(310):
                    action = algorithm.actor(obs, stochastic_output=args.mode == 'admit')
                    raw, reward, term, timeout, extra = env.step(action)
                    assert all(bool(torch.isfinite(v).all()) for v in raw.values())
                    assert bool(torch.isfinite(reward).all()) and bool(torch.isfinite(action).all())
                    torque_peak = torch.maximum(torque_peak, env.applied_motor_torque.abs().amax(0))
                    snap = env.task_snapshot
                    traces.append({k: v[:12].detach().cpu().numpy() for k, v in
                                   {**snap, 'policy': raw['policy'], 'action': action,
                                    'root_pos': env.snapshots['root_pos'], 'closure': env.snapshots['closure']}.items()})
                    for i in ((term | timeout) & ~seen).nonzero().flatten().tolist():
                        row = {k: v[i].item() for k, v in snap.items()}
                        row.update(env=i, nominal=bool(env.full_dr.nominal_env_mask[i]),
                                   terminated=bool(term[i]), timeout=bool(timeout[i]),
                                   closure_m=float(env.snapshots['closure'][i]), steps=step + 1)
                        rows.append(row)
                    seen |= term | timeout
                    obs = TensorDict(raw, batch_size=[env.num_envs])
                    if bool(seen.all()):
                        break
            assert bool(seen.all()), 'Missing complete evaluation episodes'
            check_physics_log()
            assert bool((torque_peak[:4] <= 40.00001).all()) and bool((torque_peak[4:] <= 5.77592).all())
            summary = {}
            for nominal in (False, True):
                group = [row for row in rows if row['nominal'] == nominal]
                recovered = [row for row in group if row['sequence_complete'] and not row['failed']]
                key = 'nominal' if nominal else 'fullDR'
                summary[key] = dict(episodes=len(group),
                    **{k: sum(bool(row[k]) for row in group) for k in
                       ('requested', 'takeoff', 'landed', 'sequence_complete', 'success', 'failed', 'prep_skipped')},
                    median_rim_m=float(np.median([r['rim_peak_m'] for r in group])),
                    median_body_rise_m=float(np.median([r['body_rise_peak_m'] for r in group])),
                    recovered_median_rim_m=float(np.median([r['rim_peak_m'] for r in recovered])) if recovered else None,
                    median_flight_quality=float(np.median([r['flight_quality'] for r in group])),
                    max_air_pitch_deg=float(max(r['air_pitch_rad'] for r in group) * 180. / np.pi),
                    max_air_roll_deg=float(max(r['air_roll_rad'] for r in group) * 180. / np.pi),
                    max_air_pitch_roll_rate_rad_s=max(r['air_pitch_roll_rate_rad_s'] for r in group),
                    median_estimated_spring_release_J=float(np.median([r['estimated_spring_release_J'] for r in group])))
            assert max(row['takeoff_events'] for row in rows) <= 1, 'Repeat-flight reward accounting regression'
            skipped = [r for r in rows if r['prep_skipped']]
            assert all(r['prep_duration_s'] < 1e-6 for r in skipped), 'Already-low request was forced to crouch'
            np.savez_compressed(job / 'trajectory.npz', **{k: np.stack([v[k] for v in traces]) for k in traces[0]})
            put(job / 'RESULT.json', dict(epoch=time.time(), mode=args.mode, independent=True,
                optimizer_updates=0, checkpoint_sha256=digest, summary=summary, episodes=rows,
                torque_peak_Nm=torque_peak.tolist(), finite=True, initial_actor_STD=algorithm.actor.distribution.std_param.tolist(),
                stochastic_policy=args.mode == 'admit',
                spring_energy_note='Maximum net potential decrease during grounded push/first40ms; estimate, not net mechanical work',
                done_totals=dict(env.done_totals)))
            if args.mode == 'admit':
                nominal = summary['nominal']
                dr = summary['fullDR']
                assert nominal['sequence_complete'] >= .25 * nominal['episodes'], 'Bounded-noise nominal recovery too sparse'
                assert dr['sequence_complete'] >= .01 * dr['episodes'], 'Bounded-noise fullDR recovery too sparse'
                put(job / 'ADMISSION.json', dict(passed=True, optimizer_updates=0,
                    source_archive_sha256=plan['source_archive_sha256'], complete_episodes=len(rows),
                    plant_and_motor_limits_verified=True, clocks_verified=True, flat_ground=True,
                    one_flight_accounting_verified=True, already_low_skip_cases=len(skipped),
                    interface=[35, 78, 6], observation_schema=SCHEMA,
                    num_envs=env.num_envs, physics_console_checked=True,
                    stochastic_rollout=True, nominal_recovered=nominal['sequence_complete'],
                    fullDR_recovered=dr['sequence_complete'], exploration_STD=algorithm.actor.distribution.std_param.tolist(),
                    note='Runtime admission; task success is reported separately'))
            outcome = 'complete'
            return

        algorithm.train_mode()
        start_iteration = iteration
        started, start = time.time(), time.monotonic()
        canonical_start = plan.get('budget_start_epoch', started)
        deadline = plan.get('budget_deadline_epoch', started + plan['training_round']['seconds'])
        seconds = deadline - started
        assert seconds > 0., 'The original training deadline has passed'
        next_checkpoint, last_print = 300., -30.
        put(job / 'TRAINING_STARTED.json', dict(epoch=started, pid=os.getpid(), target_seconds=seconds,
            deadline_epoch=deadline, canonical_start_epoch=canonical_start,
            optimizer_owners=1, automatic_extension=False,
            admission_excluded_from_window='budget_deadline_epoch' not in plan,
            prior_repair_time_counts_against_original_window='budget_deadline_epoch' in plan,
            parent_sha256=plan['parent_sha256']))

        def save(name):
            payload = algorithm.save()
            payload.update(format='MOD4V3_FLAT_ACCEL_HEIGHT_FULL_PPO_V1', observation_schema=SCHEMA,
                iter=iteration, action_order=env.order, num_envs=env.num_envs,
                physics_ticks=physics_ticks, parent_sha256=plan['parent_sha256'],
                cpu_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state_all(),
                python_rng=random.getstate(), numpy_rng=np.random.get_state(),
                reset_rng=env.reset_generator.get_state(),
                domain_randomization_state=env.full_dr.checkpoint_state(),
                effort_generator_rng=env.full_dr.effort_generator.get_state(),
                task_counts=env.counts, plan=plan, adaptation=adaptation,
                reward_tensors={k: v for k, v in vars(env.reward).items() if torch.is_tensor(v)},
                reward_sums=env.reward._episode_sums, done_totals=dict(env.done_totals),
                training_elapsed_seconds=time.time() - canonical_start,
                segment_training_elapsed_seconds=time.monotonic() - start,
                original_training_start_epoch=canonical_start, original_training_deadline_epoch=deadline,
                resume_scope='full actor/critic/STD/Adam/RNG; fresh physical episode')
            output = job / name
            temp = output.with_name(output.name + '.partial')
            with temp.open('wb') as stream:
                torch.save(payload, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, output)
            return dict(path=str(output), bytes=output.stat().st_size,
                        sha256=hashlib.sha256(output.read_bytes()).hexdigest(), iteration=iteration,
                        elapsed_seconds=time.monotonic() - start)

        last = None
        before_actor = {k: v.clone() for k, v in algorithm.actor.state_dict().items()}
        before_critic = {k: v.clone() for k, v in algorithm.critic.state_dict().items()}
        before_adam = {k: float(v['step']) for k, v in algorithm.optimizer.state.items()}
        while time.time() < deadline:
            env.set_training_progress(time.time() - canonical_start)
            reward_mean = 0.
            with torch.inference_mode():
                for _ in range(cfg['num_steps_per_env']):
                    action = algorithm.act(obs)
                    raw, reward, term, timeout, extra = env.step(action)
                    terminal = TensorDict(env.terminal_observations, batch_size=[env.num_envs])
                    reward = reward + algorithm.gamma * algorithm.critic(terminal).squeeze(-1) * timeout
                    obs = TensorDict(raw, batch_size=[env.num_envs])
                    assert all(bool(torch.isfinite(v).all()) for v in obs.values())
                    assert bool(torch.isfinite(reward).all())
                    algorithm.process_env_step(obs, reward, term | timeout, {})
                    reward_mean += float(reward.mean())
                    physics_ticks += 8
                check_physics_log()
                algorithm.compute_returns(obs)
            losses = algorithm.update()
            current_std = bound_exploration(algorithm)
            iteration += 1
            elapsed = time.monotonic() - start
            last = dict(epoch=time.time(), iteration=iteration, new_updates=iteration - start_iteration,
                training_elapsed_seconds=time.time() - canonical_start,
                segment_training_elapsed_seconds=elapsed, target_seconds=plan['training_round']['seconds'],
                reward_mean=reward_mean / cfg['num_steps_per_env'],
                losses={k: float(v) for k, v in losses.items()}, task=env.summary(),
                exploration_STD=current_std,
                total_env_steps=(iteration - start_iteration) * env.num_envs * cfg['num_steps_per_env'])
            put(job / 'LATEST_PROGRESS.json', last)
            if elapsed - last_print >= 30.:
                print(json.dumps(last), flush=True)
                last_print = elapsed
            if iteration == start_iteration + 1:
                actor_state, critic_state = algorithm.actor.state_dict(), algorithm.critic.state_dict()
                changes = dict(actor=any(not torch.equal(v, actor_state[k]) for k, v in before_actor.items() if k.startswith('mlp.')),
                    critic=any(not torch.equal(v, critic_state[k]) for k, v in before_critic.items()),
                    STD=not torch.equal(before_actor['distribution.std_param'], actor_state['distribution.std_param']),
                    STD_in_bounds=in_bounds(algorithm.actor.distribution.std_param),
                    Adam=all(float(v['step']) > before_adam[k] for k, v in algorithm.optimizer.state.items()))
                assert all(changes[k] for k in ('actor', 'critic', 'Adam', 'STD_in_bounds')), changes
                put(job / 'FIRST_UPDATE.json', dict(**last, changes=changes,
                    checkpoint=save('model_first_complete.pt')))
            if elapsed >= next_checkpoint:
                minutes = int(next_checkpoint / 60)
                put(job / f'PERIODIC_{minutes:03d}M.json', save(f'model_{minutes:03d}m.pt'))
                next_checkpoint += 300.
            if (job / 'REQUEST_STOP').exists():
                break
        final = save('model_final.pt')
        put(job / 'FINAL.json', dict(epoch=time.time(), checkpoint=final, last_progress=last,
            elapsed_seconds=time.monotonic() - start, target_training_seconds=seconds,
            original_start_epoch=canonical_start, original_deadline_epoch=deadline,
            automatic_extension=False, request_stop=(job / 'REQUEST_STOP').exists()))
        outcome = 'complete'
    except BaseException:
        put(job / 'ERROR.json', dict(epoch=time.time(), traceback=traceback.format_exc()))
        raise
    finally:
        if env is not None:
            env.close()
        put(job / 'SAFE_CLOSED.json', dict(epoch=time.time(), scene_closed=env is not None, outcome=outcome))
        if app is not None:
            app.close()


if __name__ == '__main__':
    main()

"""Bounded, native full-DR E0 PPO against a SHA-pinned parent."""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json
import os
import random
import sys
import time
import traceback


def put(path, payload):
    temp = path.with_suffix('.partial')
    temp.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temp.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = ArgumentParser()
    parser.add_argument('job', type=Path)
    parser.add_argument('--parent', required=True, type=Path)
    parser.add_argument('--parent-sha256', required=True)
    parser.add_argument('--num-envs', type=int, default=2048)
    parser.add_argument('--seconds', type=int, default=0, choices=(0, 360, 600))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    package = root / 'plant'
    dependencies = root / 'dependencies'
    job = args.job.resolve()
    job.mkdir()
    inventory = json.loads((root / 'INPUTS.json').read_text())
    if digest(args.parent) != args.parent_sha256:
        raise ValueError('Parent SHA mismatch')
    for name, sha in inventory['required_asset_sha256'].items():
        if digest(package / name) != sha:
            raise ValueError(f'Unexpected native asset digest for {name}')
    config = json.loads((dependencies / 'SOURCE_PATHS.relative.json').read_text())
    put(job / 'source_paths.json', {k: str(dependencies / v) for k, v in config.items()})
    storage = job / 'kit_isolation'
    (storage / 'data').mkdir(parents=True)
    (storage / 'DerivedDataCache').mkdir()
    (storage / 'data/user.config.json').write_text('{}')
    os.environ.update(MOD4V1_E0_JOB_ROOT=str(job), MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),
        MOD4_SCUT_SOURCE_PATHS=str(job/'source_paths.json'), OMNI_KIT_ACCEPT_EULA='YES', ISAACSIM_ACCEPT_EULA='Y',
        WARP_CACHE_PATH=str(root/'cache/warp'), JOINT_FRICTION_SCALE='1', SPRING_DAMPING_FRACTION='1',
        EXTERNAL_DR_FRACTION='1', OBS_NOISE_FRACTION='1', PHYSICAL_DELAY_QUANTUM_MS='5',
        PHYSICAL_ACTION_DELAY_MIN_MS='5', PHYSICAL_ACTION_DELAY_MAX_MS='10',
        PHYSICAL_SENSOR_DELAY_MIN_MS='5', PHYSICAL_SENSOR_DELAY_MAX_MS='15')
    sys.path[:0] = [str(dependencies/'launcher'), str(dependencies/'package'), str(package), str(root/'support')]
    app = env = None
    try:
        from launcher_mod4v1_e0 import IsolatedAppLauncher208
        launcher = IsolatedAppLauncher208(dict(headless=True, device='cuda:0', enable_cameras=False))
        app = launcher.app
        import numpy as np
        import torch
        from tensordict import TensorDict
        from rsl_rl.runners import OnPolicyRunner
        from mod4v1_scut.config import runner_config
        from mod4v3_ppo_v1.model import metadata, reset_bank
        from mod4v3_ppo_v1.scut_flat_env import configuration, tensor
        from mod4v3_ppo_v1.e0_env import NormalDriveEnv, install_e0_origins
        seed = 66
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        install_e0_origins()
        meta = metadata(package)
        bank = reset_bank(package, dependencies/'reset_bank.json')
        env = NormalDriveEnv(configuration(meta, bank, args.num_envs, seed, terrain_selection='rough_scut_v1'), meta, bank)
        env.render_enabled = False
        env.reset()
        env.snapshots = {}
        obs = TensorDict(env._get_observations(), batch_size=[env.num_envs])

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
                return obs

        cfg = runner_config()
        cfg.update(num_steps_per_env=24, clip_actions=6.)
        cfg['algorithm'].update(learning_rate=3e-5, schedule='fixed', clip_param=.1,
                                num_learning_epochs=3, value_loss_coef=4.)
        algorithm = OnPolicyRunner(Vec(), cfg, log_dir=None, device=env.device).alg
        parent = torch.load(args.parent, map_location=env.device, weights_only=False)
        algorithm.actor.load_state_dict(parent['actor_state_dict'], strict=True)
        algorithm.critic.load_state_dict(parent['critic_state_dict'], strict=True)
        # The new command distribution gets fresh Adam moments. All actor and critic
        # parameters, including the six exploration standard deviations, are trainable.
        iteration = int(parent['iter'])
        before = {k: value.detach().clone() for k, value in algorithm.actor.state_dict().items()}
        counts = 0
        def count_step(*_):
            nonlocal counts
            counts += 1
        algorithm.optimizer.register_step_post_hook(count_step)
        def drift():
            return float(torch.sqrt(sum((v-before[k]).square().sum() for k,v in algorithm.actor.state_dict().items())))
        assert obs['policy'].shape == (env.num_envs, 35) and obs['critic'].shape == (env.num_envs, 78)
        assert env.cfg.sim.dt == .0025 and env.cfg.decimation == 8
        assert env.leg_pd_decimation == 4 and env.wheel_pd_decimation == 1 and not env.enforce_closure_reset
        assert not bool(env.terrain.r1_continuous_stair_mask.any())
        view = env.robot.root_view
        assert bool((tensor(view.get_dof_stiffnesses())[:, env.active_ids] == 0.).all())
        assert bool((tensor(view.get_dof_dampings())[:, env.active_ids] == 0.).all())
        dr = env.mild_dr.summary()
        populations = {name: {'full_dr': int((mask & ~env.terrain.r1_nominal_mask).sum()),
                              'nominal': int((mask & env.terrain.r1_nominal_mask).sum())}
                       for name,mask in (('flat',env.terrain.r1_flat_mask),('rough_L9',env.terrain.r1_pitch_rough_mask),
                                        ('other_rough',~env.terrain.r1_pitch_target_mask))}
        startup = dict(envs=env.num_envs, parent=str(args.parent), parent_sha256=args.parent_sha256,
                       parent_iteration=iteration, groups=populations, dr=dr, action_order=env.order,
                       timestep_s=.0025, legs_every_substeps=4, wheels_every_substeps=1, policy_every_substeps=8,
                       dimensions=[35,78,6], reward=env.reward.cfg.rewards,
                       budget_seconds=args.seconds, checkpoint_every_s=120,
                       optimizer='Adam from fresh moments', seed=seed, policy_lr=3.e-5, clip=.1, epochs=3, rollout=24)
        put(job/'STARTUP.json', startup)

        def check(raw, reward):
            if not all(bool(torch.isfinite(value).all()) for value in raw.values()):
                raise FloatingPointError('Nonfinite observation')
            if not bool(torch.isfinite(reward).all()):
                raise FloatingPointError('Nonfinite reward')

        def inference():
            result = algorithm.actor(obs)
            if not bool(torch.isfinite(result).all()):
                raise FloatingPointError('Nonfinite actor mean')
            return result

        if not args.seconds:
            fall_counts = dict(flat=0, rough_L9=0, other_rough=0)
            low_examples = set()
            reward_min = float('inf')
            reward_max = -float('inf')
            max_closure = 0.
            with torch.inference_mode():
                for step in range(600):
                    raw, reward, term, _, _ = env.step(inference())
                    check(raw, reward)
                    obs = TensorDict(raw, batch_size=[env.num_envs])
                    reward_min = min(reward_min, float(reward.min()))
                    reward_max = max(reward_max, float(reward.max()))
                    max_closure = max(max_closure, float(env.closure_error.max()))
                    for label, mask in (('flat', env.terrain.r1_flat_mask),
                            ('rough_L9', env.terrain.r1_pitch_rough_mask), ('other_rough', ~env.terrain.r1_pitch_target_mask)):
                        fall_counts[label] += int((term & mask).sum())
                    if step % 25 == 0:
                        low_examples.update(round(x,3) for x in env.command[env.drive_enabled & env.drive_low, 0].unique().tolist())
            obs = obs.clone()
            algorithm.optimizer.zero_grad(set_to_none=True)
            probe_loss = (inference().square().mean() + algorithm.critic(obs).square().mean())
            probe_loss.backward()
            params = list(algorithm.actor.parameters()) + list(algorithm.critic.parameters())
            grads_finite = all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in params)
            nonzero_grads = sum(p.grad is not None and bool(p.grad.abs().max() > 0.) for p in params)
            passed = bool(grads_finite and nonzero_grads > 0 and counts == 0 and drift() == 0.
                          and not bool(env.closure_reset.any()) and min(low_examples) < 0. < max(low_examples))
            put(job/'PROBE.json', dict(passed=passed, envs=env.num_envs, steps=600, optimizer_steps=counts,
                actor_drift=drift(), gradients_finite=grads_finite, nonzero_parameter_gradients=nonzero_grads,
                reward_range=[reward_min, reward_max], max_closure_m=max_closure, done_totals=env.done_totals,
                terminations=fall_counts, low_commands=sorted(low_examples), drive=env.drive_summary(), groups=populations))
            if not passed:
                raise RuntimeError('E0 probe failed')
            return

        def save(name):
            checkpoint = algorithm.save()
            checkpoint.update(format=parent['format'], iter=iteration, action_order=env.order, num_envs=env.num_envs,
                learning_rate=algorithm.learning_rate, ppo_updates=iteration-int(parent['iter']),
                optimizer_steps=counts, source_asset=inventory['required_asset_sha256'],
                parent_sha256=args.parent_sha256, done_totals=dict(env.done_totals),
                cpu_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state_all(),
                reset_rng=env.reset_generator.get_state(), numpy_rng=np.random.get_state(), python_rng=random.getstate())
            final = job/name
            temp = final.with_suffix('.partial')
            with temp.open('wb') as f:
                torch.save(checkpoint, f)
                f.flush()
                os.fsync(f.fileno())
            temp.replace(final)
            return dict(checkpoint=name, sha256=digest(final), bytes=final.stat().st_size,
                        optimizer_steps=counts, ppo_updates=iteration-int(parent['iter']))

        algorithm.train_mode()
        elapsed = 0.
        budget_start_wall = time.time()
        start = time.monotonic()
        stop_at = args.seconds - 20.
        put(job/'TRAIN_START.json', dict(epoch=budget_start_wall, hard_stop_epoch=budget_start_wall+args.seconds,
                                         compute_stop_seconds=stop_at, iteration=iteration, optimizer_steps=0))
        durations = []
        due = 120.
        reward_mean = 0.
        losses = {}
        while elapsed + max([4., *durations[-6:]]) < stop_at and not (job/'REQUEST_STOP').exists():
            rollout_started = time.monotonic()
            reward_mean = 0.
            with torch.inference_mode():
                for _ in range(cfg['num_steps_per_env']):
                    action = algorithm.act(obs)
                    raw, reward, term, timeout, _ = env.step(action)
                    terminal = TensorDict(env.terminal_observations, batch_size=[env.num_envs])
                    reward = reward + algorithm.gamma * algorithm.critic(terminal).squeeze(-1) * timeout
                    check(raw, reward)
                    obs = TensorDict(raw, batch_size=[env.num_envs])
                    algorithm.process_env_step(obs, reward, term | timeout, {})
                    reward_mean += float(reward.mean()) / cfg['num_steps_per_env']
                algorithm.compute_returns(obs)
            losses = algorithm.update()
            iteration += 1
            elapsed = time.monotonic() - start
            durations.append(time.monotonic() - rollout_started)
            metrics = dict(elapsed_seconds=elapsed, iteration=iteration, ppo_updates=iteration-int(parent['iter']),
                optimizer_steps=counts, losses=losses, mean_reward=reward_mean, actor_drift_l2=drift(),
                done_totals=env.done_totals, drive=env.drive_summary())
            put(job/'LATEST.json', metrics)
            if iteration == int(parent['iter'])+1:
                put(job/'FIRST_UPDATE.json', metrics)
            if elapsed >= due and elapsed + 5. < stop_at:
                name = f'model_{int(due/60):03d}m.pt'
                record = save(name)
                put(job/f'{name}.json', dict(elapsed_seconds=elapsed, **record))
                due += 120.
                elapsed = time.monotonic()-start
        result = save('model_final.pt')
        put(job/'FINAL.json', dict(elapsed_seconds=time.monotonic()-start, epoch=time.time(),
                                  end_reason='requested' if (job/'REQUEST_STOP').exists() else 'budget',
                                  iteration=iteration, actor_drift_l2=drift(), mean_reward=reward_mean, losses=losses,
                                  drive=env.drive_summary(), **result))
    except Exception:
        (job/'ERROR.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        if env is not None:
            env.close()
        put(job/'SAFE_CLOSED.json', dict(epoch=time.time(), scene_closed=env is not None))
        if app is not None:
            app.close()


if __name__ == '__main__':
    main()

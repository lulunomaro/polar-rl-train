"""One finite native PPO owner, plus independent no-learning task evaluation."""
import argparse
import copy
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
    temp = path.with_name(path.name+'.partial')
    with temp.open('w', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--job', required=True)
    parser.add_argument('--mode', choices=['admit', 'train', 'evaluate'], required=True)
    parser.add_argument('--num-envs', type=int, default=128)
    parser.add_argument('--checkpoint')
    parser.add_argument('--control', choices=['actor', 'teacher'], default='actor')
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_bytes())
    job = Path(args.job)
    job.mkdir(parents=True, exist_ok=False)
    storage = job/'kit_isolation'
    (storage/'data').mkdir(parents=True)
    (storage/'DerivedDataCache').mkdir()
    (storage/'data/user.config.json').write_text('{}')
    os.environ.update(MOD4V1_E0_JOB_ROOT=str(job), MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),
                      MOD4_SCUT_SOURCE_PATHS=plan['source_paths'], OMNI_KIT_ACCEPT_EULA='YES', ISAACSIM_ACCEPT_EULA='Y')
    sys.path[:0] = [plan['runtime'], plan['shared_package'], plan['package'], plan['support']]
    from launcher_mod4v1_e0 import IsolatedAppLauncher208
    launcher = IsolatedAppLauncher208(dict(headless=True, device='cuda:0', enable_cameras=False))
    app = launcher.app
    env = None
    outcome = 'failed'
    try:
        import numpy as np
        import torch
        from tensordict import TensorDict
        from rsl_rl.runners import OnPolicyRunner
        from mod4v1_scut.config import runner_config
        from .model import metadata, reset_bank
        from .moving_jump_env import MovingJumpEnv
        from .scut_flat_env import configuration, tensor
        from .sampling import Sampling

        assert args.mode != 'train' or args.control == 'actor'
        seed = plan['seed']
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        verified = {}
        for name, row in plan['asset_identity']['actual_training_assets'].items():
            path = Path(plan['package'])/'assets'/name
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest == row['sha256'], 'Asset hash mismatch: '+name
            verified[name] = digest
        assert hashlib.sha256((Path(plan['package'])/'mjcf/scene.xml').read_bytes()).hexdigest() == plan['asset_identity']['local_mjcf_sha256']
        meta = metadata(plan['package'])
        bank = reset_bank(plan['package'], plan['reset_bank'])
        env_cfg = configuration(meta, bank, args.num_envs, seed, terrain_selection='flat')
        env_cfg.episode_length_s = 6.
        env = MovingJumpEnv(env_cfg, meta, bank)
        env.render_enabled = False
        env.reset()
        env.sample = Sampling(env)
        parity = env.sample.parity()
        assert env.enforce_closure_reset and abs(env.step_dt-.02) < 1e-9
        assert abs(env.physics_dt-.0025) < 1e-9
        assert (env.leg_pd_decimation, env.wheel_pd_decimation) == (4, 1)
        root = env.robot.root_view
        limits = tensor(root.get_dof_limits())
        stiff = tensor(root.get_dof_stiffnesses())
        damping = tensor(root.get_dof_dampings())
        contract = json.loads((Path(plan['package'])/'assets/import_contract.json').read_bytes())
        for name, row in contract['joints'].items():
            actual = limits[0, env.robot.joint_names.index(name)]
            for wanted, value in zip(row['limits_si'], actual):
                if wanted is not None:
                    assert abs(float(value)-wanted) < 2e-6, name
        assert bool((stiff[:, env.active_ids] == 0).all()) and bool((damping[:, env.active_ids] == 0).all())
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
        for key in ('learning_rate', 'schedule', 'clip_param', 'num_learning_epochs', 'value_loss_coef'):
            cfg['algorithm'][key] = plan['training_round'][key]
        runner = OnPolicyRunner(Vec(), cfg, log_dir=None, device=env.device)
        algorithm = runner.alg
        path = Path(args.checkpoint or plan['parent'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not args.checkpoint:
            assert digest == plan['parent_sha256'], 'Parent hash mismatch'
        data = torch.load(path, map_location=env.device, weights_only=False)
        assert data['action_order'] == env.order
        algorithm.load(data, load_cfg=None, strict=True)
        for key in ('actor_state_dict', 'critic_state_dict'):
            actual = algorithm.actor.state_dict() if key.startswith('actor') else algorithm.critic.state_dict()
            assert all(torch.equal(actual[k], v) for k, v in data[key].items())
        assert len(algorithm.optimizer.state) == len(data['optimizer_state_dict']['state']) > 0
        iteration = data['iter']
        physics_ticks = int(data.get('physics_ticks', 0))
        random.setstate(data['python_rng'])
        np.random.set_state(data['numpy_rng'])
        torch.set_rng_state(data['cpu_rng'].cpu())
        torch.cuda.set_rng_state_all([v.cpu() for v in data['cuda_rng']])
        if data.get('reset_rng') is not None:
            env.reset_generator.set_state(data['reset_rng'].cpu())
        # New task/geometry episodes are fresh; optimizer and parent RNG are retained.
        algorithm.learning_rate = plan['training_round']['learning_rate']
        for group in algorithm.optimizer.param_groups:
            group['lr'] = algorithm.learning_rate
        teacher_data = torch.load(plan['teacher_parent'], map_location=env.device, weights_only=False)
        env.teacher_net = copy.deepcopy(algorithm.actor.mlp).eval().requires_grad_(False)
        env.teacher_net.load_state_dict({k.removeprefix('mlp.'): v for k, v in teacher_data['actor_state_dict'].items() if k.startswith('mlp.')}, strict=True)
        env.reset()
        current = env._get_observations()
        assert current['policy'].shape == (env.num_envs, 35)
        assert current['critic'].shape == (env.num_envs, 78)
        assert current['jump_target'].shape == (env.num_envs, 6)
        startup = dict(epoch=time.time(),mode=args.mode,control=args.control,seed=seed,
            parent=str(path),parent_sha256=digest,parent_iteration=iteration,
            full_actor_critic_STD_Adam_restored=True,optimizer_entries=len(algorithm.optimizer.state),
            reset_rng_restored=data.get('reset_rng') is not None,physical_resume='fresh task episode',
            num_envs=env.num_envs,asset_hashes=verified,sampling=parity,physics_dt_s=env.physics_dt,
            policy_dt_s=env.step_dt,leg_pd_hz=100,wheel_pd_hz=400,policy_hz=50,
            closure_reset_m=.01,mimic_reset_rad=.01,actor35_critic78_action6=True,
            reset_distribution=env.reset_distribution_summary(),domain_randomization=env.full_dr.summary(),
            PPO_config=cfg,task_contract=plan['jump'],training_only_BC=plan['jump_bc'],
            deployment_input_compatible=False)
        put(job/'STARTUP.json',startup)
        put(job/'RESTORE.json',dict(source=str(path),sha256=digest,iteration=iteration,
            actor_critic_STD_Adam_restored=True,optimizer_entries=len(algorithm.optimizer.state)))
        obs = TensorDict(current,batch_size=[env.num_envs])
        if args.mode != 'train':
            algorithm.eval_mode()
            seen = torch.zeros(env.num_envs,device=env.device,dtype=torch.bool)
            rows = []
            traces = []
            peak_torque = torch.zeros(6,device=env.device)
            peak_closure = 0.
            with torch.inference_mode():
                for step in range(305):
                    action = algorithm.actor(obs,stochastic_output=False) if args.control == 'actor' else env.teacher_actions(obs['policy'])
                    raw,reward,term,timeout,extra = env.step(action)
                    assert all(bool(torch.isfinite(v).all()) for v in raw.values())
                    assert bool(torch.isfinite(action).all()) and bool(torch.isfinite(reward).all())
                    peak_torque = torch.maximum(peak_torque,env.applied_motor_torque.abs().amax(0))
                    peak_closure = max(peak_closure,float(env.snapshots['closure'].max()))
                    snap = env.jump_snapshot
                    traces.append({k:v[:20].detach().cpu().numpy() for k,v in {**snap,
                        'root_pos':env.snapshots['root_pos'],'root_quat':env.snapshots['root_quat'],
                        'action':action,'closure':env.snapshots['closure']}.items()})
                    for i in ((term|timeout)&~seen).nonzero().flatten().tolist():
                        row = {k:v[i].item() for k,v in snap.items()}
                        row.update(env=i,nominal=bool(env.full_dr.nominal_env_mask[i]),terminated=bool(term[i]),
                            timeout=bool(timeout[i]),closure_m=float(env.snapshots['closure'][i]),steps=step+1)
                        rows.append(row)
                    seen |= term|timeout
                    obs = TensorDict(raw,batch_size=[env.num_envs])
                    if bool(seen.all()):
                        break
            assert bool(seen.all()), 'Evaluation did not collect one complete episode per environment'
            summary = {}
            for nominal,name in ((False,'fullDR'),(True,'nominal')):
                group = [row for row in rows if row['nominal'] == nominal]
                summary[name] = dict(requested=len(group),**{k:sum(bool(row[k]) for row in group) for k in ('crouched','extended','takeoff','retracted','landed','success')},
                    air_balance_passed=int(sum(row['takeoff'] and row['air_pitch'] <= np.deg2rad(10) and row['air_roll'] <= np.deg2rad(5) for row in group)),
                    max_air_s=max((row['air_s'] for row in group),default=0.),
                    max_rim_m=max((row['rim_peak'] for row in group),default=0.))
            np.savez_compressed(job/'trajectory.npz',**{k:np.stack([v[k] for v in traces]) for k in traces[0]})
            put(job/'RESULT.json',dict(epoch=time.time(),mode=args.mode,control=args.control,
                independent=True,no_optimizer_update=True,checkpoint_sha256=digest,steps=step+1,
                summary=summary,episodes=rows,peak_torque_Nm=peak_torque.tolist(),peak_closure_m=peak_closure,
                done_totals=dict(env.done_totals),finite=True,episode_seconds=6.))
            if args.mode == 'admit':
                assert bool((peak_torque[:4] <= 40.00001).all()) and bool((peak_torque[4:] <= 5.77592).all())
                put(job/'ADMISSION.json',dict(passed=True,no_optimizer_update=True,finite=True,complete_episodes=len(rows),
                    full_episode_window_steps=step+1,interface=[35,78,6],closure_reset_m=.01,
                    asset_hashes_verified=True,native_mechanical_limits_verified=True,timing_verified=True,
                    note='Runtime admission only; jumping success is measured separately in RESULT.json'))
            outcome = 'complete'
            return

        from .jump_bc import install
        guidance = install(algorithm,plan['jump_bc'],job)
        algorithm.train_mode()
        before_actor = {k:v.detach().clone() for k,v in algorithm.actor.state_dict().items()}
        before_critic = {k:v.detach().clone() for k,v in algorithm.critic.state_dict().items()}
        before_adam = {k:float(v['step']) for k,v in algorithm.optimizer.state.items()}
        start_iteration = iteration
        start = time.monotonic()
        epoch_start = time.time()
        original_start = epoch_start
        deadline = epoch_start+plan['training_round']['seconds']
        next_checkpoint = 300.
        last_print = 0.
        last = None
        put(job/'TRAINING_STARTED.json',dict(epoch=epoch_start,pid=os.getpid(),parent_sha256=plan['parent_sha256'],
            target_seconds=7200,optimizer_owners=1,physical_gpu=0,automatic_extension=False,
            original_start_epoch=original_start,absolute_deadline_epoch=deadline,
            prior_phase_elapsed_seconds=0.,admission_excluded_from_window=True))

        def save(name):
            payload = algorithm.save()
            payload.update(format='MOD4V3_MOVING_JUMP_FULL_PPO_V1',iter=iteration,action_order=env.order,
                num_envs=env.num_envs,learning_rate=algorithm.learning_rate,parent_sha256=plan['parent_sha256'],
                physics_ticks=physics_ticks,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),
                python_rng=random.getstate(),numpy_rng=np.random.get_state(),reset_rng=env.reset_generator.get_state(),
                domain_randomization_state=env.full_dr.checkpoint_state(),
                effort_generator_rng=env.full_dr.effort_generator.get_state(),
                jump_counts=env.counts,jump_guidance=guidance.last,plan=plan,
                reward_tensors={k:v for k,v in vars(env.reward).items() if torch.is_tensor(v)},
                reward_sums=env.reward._episode_sums,done_totals=dict(env.done_totals),
                phase_training_elapsed_seconds=time.monotonic()-start,
                training_elapsed_seconds=time.time()-original_start,
                original_training_deadline_epoch=deadline,
                resume_scope='complete actor/critic/STD/Adam/RNG; fresh physical episode')
            output = job/name
            temp = output.with_name(output.name+'.partial')
            with temp.open('wb') as stream:
                torch.save(payload,stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp,output)
            return dict(path=str(output),bytes=output.stat().st_size,sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                iteration=iteration,optimizer_entries=len(algorithm.optimizer.state),elapsed_seconds=time.monotonic()-start)

        while time.monotonic()-start < plan['training_round']['seconds']:
            reward_mean = 0.
            with torch.inference_mode():
                for _ in range(cfg['num_steps_per_env']):
                    action = algorithm.act(obs)
                    raw,reward,term,timeout,extra = env.step(action)
                    terminal = TensorDict(env.terminal_observations,batch_size=[env.num_envs])
                    reward = reward + algorithm.gamma*algorithm.critic(terminal).squeeze(-1)*timeout
                    obs = TensorDict(raw,batch_size=[env.num_envs])
                    assert all(bool(torch.isfinite(v).all()) for v in obs.values()), 'Nonfinite observation'
                    assert bool(torch.isfinite(reward).all()), 'Nonfinite reward'
                    algorithm.process_env_step(obs,reward,term|timeout,{})
                    reward_mean += float(reward.mean())
                    physics_ticks += 8
                algorithm.compute_returns(obs)
            guidance.elapsed = time.monotonic()-start
            losses = algorithm.update()
            iteration += 1
            elapsed = time.monotonic()-start
            last = dict(epoch=time.time(),iteration=iteration,new_updates=iteration-start_iteration,
                training_elapsed_seconds=elapsed,phase_training_elapsed_seconds=time.monotonic()-start,
                target_seconds=7200,reward_mean=reward_mean/cfg['num_steps_per_env'],
                losses={k:float(v) for k,v in losses.items()},jump=env.jump_summary(),
                optimizer_entries=len(algorithm.optimizer.state),learning_rate=algorithm.learning_rate,
                total_env_steps=(iteration-start_iteration)*env.num_envs*cfg['num_steps_per_env'])
            put(job/'LATEST_PROGRESS.json',last)
            if elapsed-last_print >= 30. or iteration == start_iteration+1:
                print(json.dumps(last),flush=True)
                last_print = elapsed
            if iteration == start_iteration+1:
                state = algorithm.actor.state_dict()
                changes = dict(actor=any(not torch.equal(v,state[k]) for k,v in before_actor.items() if k.startswith('mlp.')),
                    critic=any(not torch.equal(v,algorithm.critic.state_dict()[k]) for k,v in before_critic.items()),
                    STD=not torch.equal(before_actor['distribution.std_param'],state['distribution.std_param']),
                    Adam=all(float(v['step']) > before_adam[k] for k,v in algorithm.optimizer.state.items()))
                assert all(changes.values()), changes
                put(job/'FIRST_UPDATE.json',dict(**last,changes=changes,checkpoint=save('model_first_complete.pt')))
            if elapsed >= next_checkpoint:
                minutes = int(next_checkpoint/60)
                receipt = save(f'model_{minutes:03d}m.pt')
                put(job/f'PERIODIC_{minutes:03d}M.json',receipt)
                next_checkpoint += 300.
            if (job/'REQUEST_STOP').exists():
                break
        final = save('model_final.pt')
        put(job/'FINAL.json',dict(epoch=time.time(),start_epoch=epoch_start,checkpoint=final,last_progress=last,
            elapsed_seconds=time.monotonic()-start,original_start_epoch=original_start,
            total_window_elapsed_seconds=time.time()-original_start,
            total_phase_elapsed_seconds=time.monotonic()-start,
            target_training_seconds=7200,automatic_extension=False,
            request_stop=(job/'REQUEST_STOP').exists(),safe_close_requested=True))
        outcome = 'complete'
    except BaseException:
        put(job/'ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()))
        raise
    finally:
        if env is not None:
            env.close()
        put(job/'SAFE_CLOSED.json',dict(epoch=time.time(),scene_closed=True,outcome=outcome))
        app.close()


if __name__ == '__main__':
    main()

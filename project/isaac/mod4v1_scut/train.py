"""Finite PPO entry for enhanced MOD4v1 and pinned SCUT stair rewards.

Launch under the existing canonical owner/resource controller, which supplies
its original absolute save deadline. This entry never creates a budget/lease,
copies a checkpoint tree, restarts a peer, or modifies an old frozen run.
"""
import argparse
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import random
import runpy
import signal
import sys
import time
import traceback


def put(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix+'.partial')
    with temporary.open('w',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary,path)


def close_application(app, error):
    """Preserve a recorded failure when the SDK closer requests exit0."""
    try:
        app.close()
    except SystemExit:
        if error is not None:
            raise SystemExit(1)
        raise


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', required=True)
    parser.add_argument('--runtime', required=True, help='Existing original MOD4 runtime directory')
    parser.add_argument('--support', action='append', default=[], help='Existing shared SDK modules directory; reference only')
    parser.add_argument('--runtime-manifest', required=True)
    parser.add_argument('--guard', required=True, help='Existing mod4v1_fresh_dr_guard.py')
    parser.add_argument('--job-root', required=True)
    parser.add_argument('--profile', choices=['trained_stair', 'jump270', 'scut_stairs'], default='trained_stair')
    parser.add_argument('--num-envs', type=int, default=80)
    parser.add_argument('--seed', type=int, default=66)
    parser.add_argument('--iterations', type=int, required=True)
    parser.add_argument('--save-deadline', type=float, required=True,
                        help='Original owner absolute epoch: full-save boundary')
    parser.add_argument('--resume')
    parser.add_argument('--resize-resume')
    parser.add_argument('--init-checkpoint')
    parser.add_argument('--init-SHA')
    parser.add_argument('--init-bytes', type=int)
    parser.add_argument('--repair-first-axis', action='store_true',
                        help='Explicitly reset the saturated left-crank output/STD for fresh-Adam finetuning')
    parser.add_argument('--repair-unclipped-v2', action='store_true',
                        help='Explicitly migrate the failed V2 execution interface to MOD4 clip6')
    parser.add_argument('--repair-target-limits', action='store_true',
                        help='Explicitly migrate V3 processed targets to contract motor limits')
    parser.add_argument('--device', default='cuda:0')
    return parser.parse_args()


def environment_settings(args):
    from .config import command_recipe, reward_config
    recipe = command_recipe(args.profile)
    reward = reward_config(args.profile)
    original = json.loads(Path(args.runtime_manifest).read_text(encoding='utf-8-sig'))['env']
    for key in list(os.environ):
        if key.startswith(('RM_', 'MOD4V1_', 'MOD4_RESUME_')):
            del os.environ[key]
    # Retain the actual D0-D7 profiles; replace task/asset settings explicitly.
    os.environ.update({key: str(value) for key, value in original.items()
                       if key.startswith(('RM_', 'MOD4_')) and 'DEADLINE' not in key})
    os.environ.update(RM_MOD4_USD=str(Path(args.assets)/'robot.usd'),
        RM_PHYSICS_DT_S='.0025', RM_SOLVER_POS='32', RM_SOLVER_VEL='4',
        RM_MOD4_TERRAIN='flat', RM_MOD4_MAP='', RM_FLAT_NATIVE_PLANE='0',
        RM_JUMP_SCRIPT_PROB='0', RM_CONTACT_INTEGRATED='0',
        RM_GYRO_CURRICULUM='0', RM_SPIN_STAGE='', RM_SPIN_ROLLING_PROFILE='off',
        RM_WORLD_DRIFT_PROFILE='off', RM_CMD_VX_MIN='.6', RM_CMD_VX_MAX='.6',
        RM_REL_STANDING='0', RM_REL_HEADING='0', RM_HEADING_CMD='0',
        RM_HEIGHT_MIN='.25', RM_HEIGHT_MAX='.25', RM_NOMINAL_HEIGHT='.25',
        RM_RANDOM_START='0', RM_EPISODE_S=str(reward.episode_length_s), RM_KEEP_STD='1',
        MOD4_RESUME_QUEUE_CONTROL_US='20000')
    # Constructor globals must agree with the selected profile. The managers
    # are replaced later, but their helpers also cache these values on import.
    ranges = recipe['ranges']
    os.environ.update(RM_CMD_VX_MIN=str(ranges['lin_vel_x'][0]),
        RM_CMD_VX_MAX=str(ranges['lin_vel_x'][1]),
        RM_CMD_WZ_MIN=str(ranges['ang_vel_z'][0]),
        RM_CMD_WZ_MAX=str(ranges['ang_vel_z'][1]),
        RM_REL_STANDING=str(recipe['rel_standing_envs']),
        RM_REL_HEADING=str(recipe['rel_heading_envs']),
        RM_HEADING_CMD=str(int(recipe['heading_command'])),
        RM_HEIGHT_MIN=str(reward.height_range[0]), RM_HEIGHT_MAX=str(reward.height_range[1]))
    # The shared Mod4Env treats gyro=0 as a straight-only command contract.
    # trained_stair contains yaw commands. cfg.curriculum=None still disables
    # the inherited gyro curriculum; this selects the correct command domain.
    os.environ['RM_GYRO_CURRICULUM'] = '1' if args.profile in ('trained_stair', 'scut_stairs') else '0'


def load_guard(path):
    spec = importlib.util.spec_from_file_location('mod4_scut_asset_guard', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ScutVecEnv:
    """RSL5 TensorDict adapter with the source infinite-horizon timeout mask."""
    def __init__(self, env, bridge, initial=None):
        self.env, self.bridge = env, bridge
        self.num_envs, self.num_actions, self.device = env.num_envs, 6, env.device
        self.max_episode_length, self.cfg = env.max_episode_length, env.cfg
        self.current = initial

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        self._current = value
        self._adapted_observations = None

    @property
    def episode_length_buf(self):
        return self.env.episode_length_buf

    @episode_length_buf.setter
    def episode_length_buf(self, value):
        self.env.episode_length_buf.copy_(value)

    def get_observations(self):
        from tensordict import TensorDict
        if self.current is None:
            self.current = self.env.observation_manager.compute()
        if self._adapted_observations is None:
            self._adapted_observations = TensorDict(self.bridge.observations(self.current), batch_size=[self.num_envs])
        return self._adapted_observations

    def step(self, action):
        from .config import ACTION_CLIP
        # Do not mutate the sampled tensor retained by RSL for its Gaussian
        # log-probability. The original MOD4 wrapper clips only the env input.
        applied = action.clamp(-ACTION_CLIP, ACTION_CLIP)
        self.bridge.pending_actions.copy_(applied)
        raw, reward, terminated, timeout, extras = self.env.step(applied)
        self.current = raw
        info = dict(extras)
        info['time_outs'] = timeout  # vecenv_wrapper.py:186; hard resets resolved upstream
        return self.get_observations(), reward, terminated | timeout, info


def build_runner(vec, directory):
    import importlib.metadata
    from rsl_rl.runners import OnPolicyRunner
    from .config import runner_config
    version = importlib.metadata.version('rsl-rl-lib')
    if version.split('.')[0] != '5':
        raise RuntimeError('This explicit adapter targets RSL5; actual version: '+version)
    return OnPolicyRunner(vec, deepcopy(runner_config()),
                          log_dir=str(directory) if directory is not None else None, device=vec.device)


def initialize_episode_lengths(vec, profile):
    """train.py:275 requests staggered initial episode clocks for saved training.

    jump270 independent first-flight episodes instead start at time zero. This
    explicit task override does not change physical states or source rewards.
    """
    if profile in ('trained_stair', 'scut_stairs'):
        import torch
        vec.episode_length_buf = torch.randint_like(vec.episode_length_buf, high=vec.max_episode_length)


def set_training_iteration(env, iteration):
    term = env.command_manager.get_term('twist')
    term.set_training_iteration(iteration)


def boot(args, job):
    """Use the existing proven isolated launcher/custom SDK extension activation."""
    environment_settings(args)
    runtime = Path(args.runtime).resolve()
    sys.path[:0] = [str(runtime), *args.support, str(runtime.parents[1])]
    storage = job/'kit_isolation'
    (storage/'data').mkdir(parents=True)
    (storage/'DerivedDataCache').mkdir()
    (storage/'data/user.config.json').write_text('{}')
    # Original E0 feasible-joint-bank validator reads this declaration under
    # its job root. Reuse the exact shared declaration; no copied asset/bank.
    declaration=runtime.parents[2]/'MOD4V1_ASSET_DIFF.json'
    (job/'MOD4V1_ASSET_DIFF.json').symlink_to(declaration)
    os.environ.update(MOD4V1_E0_ASSET_DIR=str(args.assets),
        MOD4V1_E0_JOB_ROOT=str(job),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage))
    entry = runtime/'train_mod4v1_e0.py'
    argv = sys.argv
    try:
        sys.argv = [str(entry),'--headless','--device',args.device,
            '--num_envs',str(args.num_envs),'--seed',str(args.seed),
            '--steps_per_env','24','--additional_iterations','1']
        return runpy.run_path(str(entry),run_name='scut_shared_constructor_only')
    finally:
        sys.argv = argv


def main():
    args = parse_args()
    if args.iterations <= 0 or not 0 < args.save_deadline-time.time() <= 7200:
        raise ValueError('Expected finite iterations within the original save window')
    if sum(bool(v) for v in [args.resume,args.init_checkpoint,args.resize_resume])>1:
        raise ValueError('Choose full continuation or weights-only finetune')
    job = Path(args.job_root).resolve()
    job.mkdir(parents=True, exist_ok=False)
    ns = boot(args,job)
    guard_module = load_guard(args.guard)
    identity = ns['E0_IDENTITY']
    env = bridge = None
    runner = None
    started = False
    error = None
    try:
        import torch
        import numpy as np
        random.seed(args.seed)
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)
        torch.cuda.manual_seed_all(args.seed)
        from chassis_pd_training_env import ChassisPDMod4Env
        import mod4_task as task
        from mild_dr import tensor
        from .config import model_contract
        from .sdk import configure, ScutBridge
        from .checkpoint import save, restore
        guard_module.verify_task_module(task, identity)
        contract = model_contract(args.assets)
        cfg = task.Mod4EnvCfg()
        cfg.seed = args.seed
        cfg.sim.device = args.device
        configure(cfg, args.num_envs, args.profile, contract)
        guard_module.configure_new_task(cfg, identity)
        env = ChassisPDMod4Env(cfg=cfg)
        if env.physics_dt != .0025 or env.step_dt != .02:
            raise RuntimeError('MOD4 400/100/50Hz clock mismatch')
        guard = guard_module.FreshDRNominalGuard(env, identity, torch_module=torch, tensor_converter=tensor)
        from pose_cache_runtime_adapter_v4 import install_pose_cache_runtime_adapter_v4
        pose_events=[]
        def pose_receipt(value):
            if len(pose_events)<40:pose_events.append(value)
            put(job/'POSE_CACHE_EVENTS.json',dict(events=pose_events,original_calls_preserved=True))
        install_pose_cache_runtime_adapter_v4(env.scene['robot'],receipt_callback=pose_receipt)
        bridge = ScutBridge(env, task, contract, tensor, args.profile)
        vec = ScutVecEnv(env, bridge)
        # Runner construction only needs shapes, without resetting physics or RNG.
        vec.current = env.observation_manager.compute()
        runner = build_runner(vec, job)
        if args.init_checkpoint:
            from .finetune import initialize
            receipt = initialize(runner,args.init_checkpoint,args.init_SHA,args.init_bytes,
                repair_first_axis=args.repair_first_axis,profile=args.profile)
            put(job/'FINETUNE_INITIALIZATION.json',receipt)
        if args.resize_resume:
            from .checkpoint import restore_resized_learning
            receipt=restore_resized_learning(runner,args.resize_resume,args.init_SHA,args.init_bytes,args.profile,env.num_envs,bridge.reward,
                repair_unclipped_v2=args.repair_unclipped_v2,
                repair_target_limits=args.repair_target_limits)
            put(job/'RESIZED_LEARNING_RESTORE.json',receipt)
        env._get_training_iteration = lambda: runner.current_learning_iteration
        with guard.around_original_fullstate_restore():
            reset = restore(runner, env, bridge, args.resume, args.profile,
                repair_unclipped_v2=args.repair_unclipped_v2,
                repair_target_limits=args.repair_target_limits) if args.resume else env.reset()
        vec.current = reset[0] if isinstance(reset, tuple) else reset
        initialize_episode_lengths(vec, args.profile)
        guard.check_observations(vec.current)
        guard.verify_live_parameters()
        startup = guard.receipt()
        if not (env._mild_dr.profile == 'white_v3'
                and env._sensor_mild.profile == 'noise_bias_mild_v1'
                and env._feedback_delay_mild.enabled and env._physics_action_delay.queue.enabled
                and env._spring_pressure.component.enabled and env._gas_damping.component.enabled
                and env._chassis_com.component.enabled and env._explicit_pd.component.enabled):
            raise RuntimeError('Original full D0-D7 profiles must all be active')
        bridge.ready = True
        from .course import metadata
        if args.profile == 'scut_stairs':
            from .stairs import metadata
        from .config import ACTION_CLIP, ACTION_INTERFACE, TARGET_INTERFACE
        put(job/'STARTUP.json',dict(epoch=time.time(),
            actual_native=True, profile=args.profile, usd_SHA=identity.usd_sha256,
            contract_SHA=identity.contract_sha256, D0_D7=startup, actor=35, critic=78,
            quaternion_order=bridge.quaternion_order,
            quaternion_readback=bridge.quaternion_readback,
            actions=6, action_clip=ACTION_CLIP, action_interface=ACTION_INTERFACE,
            target_interface=TARGET_INTERFACE,
            repair_unclipped_v2=args.repair_unclipped_v2,
            physics_dt=.0025, policy_hz=50, feedback_hz=100,
            closure_m=.01, mimic_rad=.01,
            course=metadata(args.num_envs) if args.profile == 'scut_stairs' else metadata(),
            trained_skill=False))
        stop = False
        def stop_after_update(*unused):
            nonlocal stop
            stop = True
        signal.signal(signal.SIGINT, stop_after_update)
        signal.signal(signal.SIGTERM, stop_after_update)
        runner.logger.init_logging_writer()
        obs = vec.get_observations().to(args.device)
        runner.alg.train_mode()
        gradient = dict(steps=0,actor_norm=0.,critic_norm=0.)
        def observe_gradient(optimizer,*unused):
            gradient['steps'] += 1
            for name in ('actor','critic'):
                values=[p.grad.detach().square().sum() for p in getattr(runner.alg,name).parameters() if p.grad is not None]
                norm=float(torch.stack(values).sum().sqrt()) if values else 0.
                gradient[name+'_norm']=max(gradient[name+'_norm'],norm)
        gradient_hook=runner.alg.optimizer.register_step_pre_hook(observe_gradient)
        started = True
        start_iteration = runner.current_learning_iteration
        total_iterations = start_iteration+args.iterations
        max_iteration_seconds = 0.
        # Same upstream rollout -> process_env_step -> GAE -> PPO.update sequence.
        # Finite boundary: stop before another rollout, then one complete atomic save.
        # The original owner retains its 300s exit reserve. Keep 30s inside its
        # save boundary as well; do not begin a rollout that cannot fit the last
        # observed full iteration. Never create a new/relative budget here.
        for iteration in range(start_iteration, total_iterations):
            if stop or (job.parent/'STOP_AFTER_SAVE.json').exists() or time.time()+max(30., 2*max_iteration_seconds) >= args.save_deadline:
                break
            collect_start = time.time()
            set_training_iteration(env, iteration)
            with torch.inference_mode():
                for _ in range(runner.cfg['num_steps_per_env']):
                    actions = runner.alg.act(obs)
                    obs, rewards, dones, extras = vec.step(actions)
                    obs, rewards, dones = obs.to(args.device), rewards.to(args.device), dones.to(args.device)
                    if not (all(bool(torch.isfinite(v).all()) for v in obs.values())
                            and bool(torch.isfinite(rewards).all())):
                        raise RuntimeError('Nonfinite environment observation/reward')
                    runner.alg.process_env_step(obs, rewards, dones, extras)
                    runner.logger.process_env_step(rewards, dones, extras, None)
                runner.alg.compute_returns(obs)
            collect_time = time.time()-collect_start
            update_start = time.time()
            losses = runner.alg.update()
            runner.current_learning_iteration = iteration+1
            if not all(torch.isfinite(torch.as_tensor(value)).all() for value in losses.values()):
                raise RuntimeError('Nonfinite PPO loss')
            runner.logger.log(it=iteration, start_it=start_iteration, total_it=total_iterations,
                collect_time=collect_time, learn_time=time.time()-update_start,
                loss_dict=losses, learning_rate=runner.alg.learning_rate,
                action_std=runner.alg.get_policy().output_std, rnd_weight=None)
            put(job/'LATEST_PROGRESS.json',dict(epoch=time.time(),
                iteration=iteration+1, physics_ticks=bridge.physics_ticks,
                actual_reward_mean=float(rewards.mean()), losses={k:float(v) for k,v in losses.items()},
                strict270_current_count=int(bridge.acceptance.success.sum()) if args.profile != 'scut_stairs' else 0,
                strict270_completed_count=bridge.completed_strict if args.profile != 'scut_stairs' else 0,
                scut_stair_recovered=bridge.completed_strict if args.profile == 'scut_stairs' else None,
                completed_episodes=bridge.completed_episodes,gradient=gradient))
            if iteration == start_iteration:
                first=save(runner, env, bridge, job/'model_first_complete.pt', args.profile)
                if gradient['actor_norm'] <= 0 or gradient['critic_norm'] <= 0:
                    raise RuntimeError('First actual PPO update has zero gradient')
                put(job/'FIRST_UPDATED.json',dict(epoch=time.time(),
                    actual_native=True,iteration=iteration+1,physics_ticks=bridge.physics_ticks,
                    PPO_updates=1,rollout_controls=runner.cfg['num_steps_per_env'],
                    actual_onpolicy_samples=env.num_envs*runner.cfg['num_steps_per_env'],
                    losses={k:float(v) for k,v in losses.items()},gradient=gradient.copy(),
                    full_save=True,checkpoint=first))
            if (iteration+1) % runner.cfg['save_interval'] == 0:
                save(runner, env, bridge, job/f'model_{iteration+1}.pt', args.profile)
            max_iteration_seconds = max(max_iteration_seconds, time.time()-collect_start)
        final=save(runner, env, bridge, job/'model_final.pt', args.profile)
        put(job/'FINAL.json',dict(epoch=time.time(),passed_execution=True,checkpoint=final,
            PPO_updates=runner.current_learning_iteration-start_iteration,
            strict270_completed=bridge.completed_strict if args.profile != 'scut_stairs' else 0,
            scut_stair_recovered=bridge.completed_strict if args.profile == 'scut_stairs' else None,
            episodes_completed=bridge.completed_episodes))
        started = False
    except BaseException:
        error=traceback.format_exc()
        put(job/'ERROR.json',dict(epoch=time.time(),error=error))
        raise
    finally:
        try:
            if started and runner is not None:
                from .checkpoint import save
                save(runner, env, bridge, job/'model_interrupted.pt', args.profile)
        finally:
            try:
                if runner is not None:
                    runner.logger.stop_logging_writer()
            finally:
                try:
                    if bridge is not None:
                        bridge.close()
                    if env is not None:
                        env.close()
                        put(job/'ENV_CLOSED.json',dict(epoch=time.time(),returned=True))
                finally:
                    put(job/'APP_CLOSE_INTENT.json',dict(epoch=time.time(),error=error,
                        env_closed=(job/'ENV_CLOSED.json').exists(),final_exists=(job/'FINAL.json').exists()))
                    close_application(ns['app'], error)


if __name__ == '__main__':
    main()

"""Run a 600-step native precheck or one deadline-bounded PPO round."""
from argparse import ArgumentParser
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time
import traceback

from silky_geometry import (PHYSICS_DT, POLICY_SUBSTEPS, SUPPORT_STEPS, TRANSITION_SUPPORT_STEPS,
                            physx_tire_geometry)

PPO_SECONDS = 1500
TRAIN_SECONDS_BY_TAG = {'softmoe_r10': 1200}
WARM_STEPS = 1400
CRITIC_WARMUP = 3
STD_LEG_MIN = .016
STD_LEG = .032
STD_LEG_MAX = .052
STD_WHEEL_MIN = .025
STD_WHEEL = .055
STD_WHEEL_MAX = .080
LR_POLICY = 8e-5
LR_E0 = 0.
LR_CRITIC = 3e-4
INITIAL_TRAIN_DR = .25
FLAT_E0_COEF = .65
CLIMB_E0_COEF = .65
DECK_E13_COEF = .65
E0_CRUISE_MAX_SPEED = 2.2
ROUTER_ENTROPY_COEF = .001
RESUME_CHECKPOINTS = {
    'softmoe_r7': ('softmoe_r6', '31ad41ee216df802906f51747900ad68e90696cce3486ee2140d097b40f3349d'),
    'softmoe_r8': ('softmoe_r7', '76c5923bfef12cc2996a2561a33c9d753233e5285d71ab4d215e421180b73f6b'),
    'softmoe_r9': ('softmoe_r8', '5e87b7d1a333475c271d3ed759b61fdd2189556d6035304cd2df8a5afa925872'),
    'softmoe_r10': ('softmoe_r9', 'c6576f8e9e4812d8f9fb2ed3e0ab8c3ad2217f516730010a84d21933377a623a'),
}


def put(path, payload):
    temporary = path.with_suffix('.partial')
    temporary.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('job', type=Path)
    parser.add_argument('--seconds', type=int, choices=(0, PPO_SECONDS, *TRAIN_SECONDS_BY_TAG.values()), default=0)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    job = args.job.resolve()
    if args.seconds and args.seconds != TRAIN_SECONDS_BY_TAG.get(job.parent.name, PPO_SECONDS):
        parser.error('Training duration must match the budget for this run tag')
    job.mkdir()
    app = env = None
    try:
        inputs = json.loads((root/'INPUTS.json').read_text())
        for path, expected in inputs.items():
            if sha256(root/path) != expected:
                raise ValueError(f'SHA mismatch for {path}')
        dependencies = root/'dependencies'
        plant = root/'plant'
        sources = json.loads((dependencies/'SOURCE_PATHS.relative.json').read_text())
        put(job/'source_paths.json', {k: str(dependencies/v) for k, v in sources.items()})
        storage = job/'kit_isolation'
        (storage/'data').mkdir(parents=True)
        (storage/'DerivedDataCache').mkdir()
        (storage/'data/user.config.json').write_text('{}')
        os.environ.update(MOD4V1_E0_JOB_ROOT=str(job), MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),
            MOD4_SCUT_SOURCE_PATHS=str(job/'source_paths.json'), OMNI_KIT_ACCEPT_EULA='YES',
            ISAACSIM_ACCEPT_EULA='Y', WARP_CACHE_PATH=str(root/'cache/warp'),
            JOINT_FRICTION_SCALE='1', SPRING_DAMPING_FRACTION='1',
            EXTERNAL_DR_FRACTION='1', OBS_NOISE_FRACTION='1', PHYSICAL_DELAY_QUANTUM_MS='5',
            PHYSICAL_ACTION_DELAY_MIN_MS='5', PHYSICAL_ACTION_DELAY_MAX_MS='10',
            PHYSICAL_SENSOR_DELAY_MIN_MS='5', PHYSICAL_SENSOR_DELAY_MAX_MS='15')
        sys.path[:0] = [str(dependencies/'launcher'), str(dependencies/'package'), str(plant), str(root/'support')]
        from launcher_mod4v1_e0 import IsolatedAppLauncher208
        launcher = IsolatedAppLauncher208(dict(headless=True, device='cuda:0', enable_cameras=False))
        app = launcher.app

        import numpy as np
        import torch
        from tensordict import TensorDict
        from rsl_rl.algorithms import PPO
        from rsl_rl.models import MLPModel
        from rsl_rl.runners import OnPolicyRunner
        from mod4v1_scut.config import runner_config
        from mod4v3_ppo_v1.model import metadata, reset_bank
        from mod4v3_ppo_v1.scut_flat_env import configuration, tensor
        from silky_loco_env import (COURSES, DECK_ABSORB_TICKS, DECK_BREAK_FORCE_N, DECK_LEG_ACTION_RATE_COEF,
                                    DECK_STREAK_FORCE_N, DOUBLE_DR_PASS_RATE,
                                    FAST_FLAT_COMMAND_FRACTION, FAST_FLAT_SPEED_RANGE,
                                    FINAL_DECK_TICKS, FIRST_TREAD_TICKS, HIGH_DECK_STANCE, HIGH_SPEED_COMMAND,
                                    HIGH_SPEED_COMMAND_FRACTION, OBSTACLE_SPEED_RANGE, REWARD_TERMS,
                                    SINGLE_DR_PASS_RATE, SilkyLocoEnv, install_course)
        from unified_soft_moe import EXPERTS, TEMPERATURE, UnifiedSoftMoEActor, distill_experts

        class ActorModel(MLPModel):
            def __init__(self, *parameters, **options):
                super().__init__(*parameters, **options)
                self.mlp = UnifiedSoftMoEActor()

        class SoftMoEPPO(PPO):
            warmup_only = False

            def update(self):
                # Single-GPU, fixed-rate PPO using RSL's storage, GAE,
                # Gaussian distribution and rollout implementation.
                assert self.schedule == 'fixed' and not (self.is_multi_gpu or self.rnd or self.symmetry)
                keys = ('value', 'surrogate', 'entropy', 'load_balance', 'router_entropy', 'flat_e0', 'climb_e0', 'deck_e13')
                means = {key: 0. for key in keys}
                batches = self.storage.mini_batch_generator(self.num_mini_batches, self.num_learning_epochs)
                for batch in batches:
                    values = self.critic(batch.observations)
                    value = (values-batch.returns).square()
                    if self.use_clipped_value_loss:
                        clipped = batch.values+(values-batch.values).clamp(-self.clip_param, self.clip_param)
                        value = torch.maximum(value, (clipped-batch.returns).square())
                    value = value.mean()
                    if self.warmup_only:
                        surrogate = entropy = balance = router_entropy = flat_e0 = climb_e0 = deck_e13 = value.new_zeros(())
                        loss = self.value_loss_coef * value
                        self.optimizer.zero_grad()
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm, error_if_nonfinite=True)
                        self.optimizer.step()
                    else:
                        self.actor(batch.observations, stochastic_output=True)
                        log_prob = self.actor.get_output_log_prob(batch.actions)
                        advantage = batch.advantages.squeeze(-1)
                        if self.normalize_advantage_per_mini_batch:
                            advantage = (advantage-advantage.mean())/(advantage.std()+1e-8)
                        ratio = (log_prob-batch.old_actions_log_prob.squeeze(-1)).exp()
                        surrogate = torch.maximum(-advantage*ratio,
                                                   -advantage*ratio.clamp(1.-self.clip_param, 1.+self.clip_param)).mean()
                        entropy = self.actor.output_entropy.mean()
                        is_flat = batch.observations['is_flat'].bool()
                        is_climb = batch.observations['is_climb'].bool()
                        is_deck = batch.observations['is_deck'].bool()
                        weights = self.actor.mlp.last_weights
                        flat_e0 = ((1.-weights[:, 0])*is_flat).sum()/is_flat.sum().clamp_min(1)
                        climb_e0 = (weights[:, 0]*is_climb).sum()/is_climb.sum().clamp_min(1)
                        deck_e13 = ((weights[:, 0]+weights[:, 2])*is_deck).sum()/is_deck.sum().clamp_min(1)
                        balance = self.actor.mlp.load_balance_loss(batch.observations['balance_routes'].bool())
                        router_entropy = self.actor.mlp.entropy()
                        loss = (surrogate+self.value_loss_coef*value-self.entropy_coef*entropy
                                +.01*balance+ROUTER_ENTROPY_COEF*router_entropy
                                +FLAT_E0_COEF*flat_e0+CLIMB_E0_COEF*climb_e0+DECK_E13_COEF*deck_e13)
                        self.optimizer.zero_grad()
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm, error_if_nonfinite=True)
                        torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm, error_if_nonfinite=True)
                        self.optimizer.step()
                        with torch.no_grad():
                            self.actor.distribution.std_param[:4].clamp_(STD_LEG_MIN, STD_LEG_MAX)
                            self.actor.distribution.std_param[4:].clamp_(STD_WHEEL_MIN, STD_WHEEL_MAX)
                    batch_losses = (value, surrogate, entropy, balance, router_entropy, flat_e0, climb_e0, deck_e13)
                    for key, item in zip(keys, batch_losses, strict=True):
                        means[key] += float(item.detach())
                self.storage.clear()
                return {key: value/(self.num_mini_batches*self.num_learning_epochs) for key, value in means.items()}

        seed = 831701
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        install_course()
        meta = metadata(plant)
        bank = reset_bank(plant, dependencies/'reset_bank.json')
        landing_name = 'JUMP_LANDING_POOL.json'
        landings = json.loads((root/landing_name).read_text()) if landing_name in inputs else None
        source = json.loads((root/'WARMSTART_SOURCE.json').read_text())
        resume = 'resume.pt' in inputs
        initial_dr = INITIAL_TRAIN_DR if resume and args.seconds else 0.
        geometry = physx_tire_geometry(plant)
        cfg_env = configuration(meta, bank, 2048, seed, terrain_selection='rough_scut_v1')
        env = SilkyLocoEnv(cfg_env, meta, bank, geometry, landing_pool=landings,
                           standing_pose=source['standing_pose'], initial_dr=initial_dr)
        env.render_enabled = False
        env.scene['contacts'].cfg.update_period = 0.
        update_scene = env.scene.update

        def update_and_sample(dt):
            update_scene(dt)
            env.sample_physics(dt)

        env.scene.update = update_and_sample
        env.reset()
        assert source['action_order'] == env.order
        initial_active_dr = int(env.full_dr.applied_dr.sum())
        assert initial_active_dr == int(initial_dr * env.num_envs)
        assert torch.equal(env.full_dr.applied_dr, ~env.full_dr.nominal_env_mask)

        def observations(raw):
            # Rollout storage receives this frame after env.step mutates the environment buffers.
            is_climb = env.riser_climb.clone()
            is_deck = env.deck_absorb.clone()
            cruise = (env.group == 0) | (env.obstacle & ~is_climb & ~is_deck)
            is_flat = cruise & (env.command[:, 0] <= E0_CRUISE_MAX_SPEED)
            balance_routes = (env.group == 1) | is_climb
            return TensorDict(dict(raw, is_flat=is_flat, is_climb=is_climb, is_deck=is_deck,
                                   balance_routes=balance_routes), batch_size=[env.num_envs])

        obs = observations(env._get_observations())

        class VectorEnv:
            num_envs = env.num_envs
            num_actions = 6
            device = env.device
            max_episode_length = env.max_episode_length
            cfg = env.cfg
            episode_length_buf = env.episode_length_buf

            def get_observations(self):
                return obs

        cfg = runner_config()
        cfg.update(num_steps_per_env=24, clip_actions=6.)
        cfg['actor']['class_name'] = ActorModel
        cfg['algorithm'].update(class_name=SoftMoEPPO, learning_rate=LR_POLICY, schedule='fixed', clip_param=.1,
                                num_learning_epochs=3, value_loss_coef=4., entropy_coef=2e-4)
        alg = OnPolicyRunner(VectorEnv(), cfg, log_dir=None, device=env.device).alg
        base = torch.load(root/'parent.pt', map_location=env.device, weights_only=False)
        warm = base['actor_state_dict']
        actor = alg.actor.mlp
        warm_path = root/'probe/model_step000.pt'
        if resume:
            assert inputs['resume.pt'] == RESUME_CHECKPOINTS[root.name][1]
            saved = torch.load(root/'resume.pt', map_location=env.device, weights_only=True)
            assert saved['format'] == 'mod4v3_unified_soft_moe_v1'
            assert saved['action_order'] == env.order and saved['actor_input'] == 455 and saved['critic_input'] == 78
            alg.actor.load_state_dict(saved['actor_state_dict'], strict=True)
            alg.critic.load_state_dict(saved['critic_state_dict'], strict=True)
            actor.experts[0].warm_start(warm)
            audit = dict(sha256=inputs['resume.pt'], selected_e0_sha256=inputs['parent.pt'],
                         starting_iteration=int(saved['iter']), inherited_ppo_updates=int(saved['ppo_updates']),
                         optimizer_steps=0, restored_actor=True, restored_critic=True, expert_0_frozen=True)
        elif args.seconds:
            alg.critic.load_state_dict(base['critic_state_dict'], strict=True)
            audit = json.loads((root/'probe/WARMSTART.json').read_text())
            if sha256(warm_path) != audit['sha256']:
                raise ValueError('Warm-start checkpoint does not match the precheck')
            warmed = torch.load(warm_path, map_location=env.device, weights_only=False)
            actor.load_state_dict(warmed['actor'])
        else:
            alg.critic.load_state_dict(base['critic_state_dict'], strict=True)
            actor.warm_start(warm)
            before_warm = time.monotonic()
            teacher = torch.load(root/'stair_teacher.pt', map_location=env.device, weights_only=False)
            assert teacher['action_order'] == env.order
            with np.load(root/'WARMSTART_DATA.npz') as examples:
                audit = distill_experts(actor, teacher['actor_state_dict'], examples, WARM_STEPS, seed)
            torch.save(dict(actor=actor.state_dict()), warm_path)
            audit.update(sha256=sha256(warm_path), seconds=time.monotonic()-before_warm,
                         teacher_sha256=inputs['stair_teacher.pt'], dataset_sha256=inputs['WARMSTART_DATA.npz'])
        put(job/'WARMSTART.json', audit)
        if not resume:
            with torch.no_grad():
                alg.actor.distribution.std_param.copy_(warm['distribution.std_param'].new_tensor(
                    [STD_LEG]*4 + [STD_WHEEL]*2))
        actor.experts[0].requires_grad_(False)
        base_params = list(actor.experts[0].parameters())
        other_params = [p for p in alg.actor.parameters() if p.requires_grad]
        alg.optimizer = torch.optim.Adam([dict(name='expert_0', params=base_params, lr=LR_E0),
                                          dict(name='adaptive_actor', params=other_params, lr=LR_POLICY),
                                          dict(name='critic', params=alg.critic.parameters(), lr=LR_CRITIC)],
                                         lr=LR_POLICY)
        modules = {'history_encoder': actor.history_encoder, 'router': actor.router,
                   **{f'expert_{k}': expert for k, expert in enumerate(actor.experts)}}
        # Compare the initialized E0 head pointwise to the released MLP.
        with torch.no_grad():
            expected = obs['policy'][:, :35]
            for layer in (0, 2, 4, 6):
                expected = torch.nn.functional.linear(expected, warm[f'mlp.{layer}.weight'], warm[f'mlp.{layer}.bias'])
                if layer != 6:
                    expected = torch.nn.functional.elu(expected)
            actual_e0 = actor.experts[0](obs['policy'][:, :35], expected.new_zeros((2048, 128)))
            e0_error = float((actual_e0-expected).abs().max())
        assert e0_error == 0.
        before = {name: val.detach().clone() for name, val in alg.actor.state_dict().items()}
        e0_before = {name: before['mlp.experts.0.'+name] for name in actor.experts[0].state_dict()}
        optimizer_steps = updates = 0
        first_step_gradients = {}

        def gradient_evidence():
            groups = {}
            for key, module in modules.items():
                parameters = list(module.parameters())
                grads = [p.grad for p in parameters if p.grad is not None]
                groups[key] = dict(l2=float(torch.stack([g.norm() for g in grads]).norm()) if grads else 0.,
                                   all_finite=len(grads) == len(parameters) and
                                   all(bool(torch.isfinite(g).all()) for g in grads),
                                   trainable=any(p.requires_grad for p in parameters))
            return groups

        def step_hook(*_):
            nonlocal optimizer_steps
            optimizer_steps += 1
            if not first_step_gradients and not alg.warmup_only:
                first_step_gradients.update(gradient_evidence())

        alg.optimizer.register_step_post_hook(step_hook)
        assert obs['policy'].shape == (2048, 455) and obs['critic'].shape == (2048, 78)
        routing_labels = {'is_flat', 'is_climb', 'is_deck', 'balance_routes'}
        assert all(routing_labels.isdisjoint(names) for names in (alg.actor.obs_groups, alg.critic.obs_groups))
        assert env.cfg.sim.dt == PHYSICS_DT and env.cfg.decimation == POLICY_SUBSTEPS and str(env.device).startswith('cuda')
        assert env.leg_pd_decimation == 4 and env.wheel_pd_decimation == 1 and not env.enforce_closure_reset
        view = env.robot.root_view
        assert bool((tensor(view.get_dof_stiffnesses())[:, env.active_ids] == 0.).all())
        assert bool((tensor(view.get_dof_dampings())[:, env.active_ids] == 0.).all())
        groups = dict(zip(COURSES, torch.bincount(env.group, minlength=len(COURSES)).tolist()))
        assert all(groups.values())
        put(job/'STARTUP.json', dict(groups=groups, envs=env.num_envs, seed=seed, device=str(env.device),
                                  gpu=torch.cuda.get_device_name(), inputs=inputs, budget_seconds=args.seconds,
                                  physics_hz=400, policy_hz=50, leg_pd_hz=100, wheel_pd_hz=400,
                                  obs=35, history=420, critic=78, actions=6, action_order=env.order,
                                  architecture='UnifiedSoftMoEActor', experts=EXPERTS, router_tau=TEMPERATURE,
                                  expert_0_max_error=e0_error, route_balance_coef=.01,
                                  route_entropy_coef=ROUTER_ENTROPY_COEF, route_balance_experts=[1, 2, 3],
                                  flat_e0_coef=FLAT_E0_COEF, climb_e0_coef=CLIMB_E0_COEF,
                                  deck_e13_coef=DECK_E13_COEF, e0_cruise_max_speed_m_s=E0_CRUISE_MAX_SPEED,
                                  anchor_weight=0., critic_warmup_updates=CRITIC_WARMUP,
                                  route_balance_samples='rough_L9_or_riser_climb',
                                  flat_label_training_only=True, climb_label_training_only=True, deck_label_training_only=True,
                                  final_deck_exit_ticks=FINAL_DECK_TICKS, first_tread_exit_ticks=FIRST_TREAD_TICKS,
                                  deck_absorb_ticks=DECK_ABSORB_TICKS, deck_absorb_high_stance_m=HIGH_DECK_STANCE,
                                  deck_break_force_n=DECK_BREAK_FORCE_N, deck_streak_force_n=DECK_STREAK_FORCE_N,
                                  deck_leg_action_rate_coef=DECK_LEG_ACTION_RATE_COEF,
                                  fast_flat_command_fraction=FAST_FLAT_COMMAND_FRACTION,
                                  fast_flat_speed_range_m_s=FAST_FLAT_SPEED_RANGE,
                                  fast_ground_courses=list(COURSES[:2]), obstacle_speed_range_m_s=OBSTACLE_SPEED_RANGE,
                                  explicit_high_speed_command_m_s=HIGH_SPEED_COMMAND,
                                  explicit_high_speed_fraction=HIGH_SPEED_COMMAND_FRACTION,
                                  initial_target_dr=initial_dr, initial_active_dr=initial_active_dr,
                                  single_dr_pass_rate=SINGLE_DR_PASS_RATE, double_dr_pass_rate=DOUBLE_DR_PASS_RATE,
                                  physics_support_ticks=SUPPORT_STEPS, double_transition_ticks=TRANSITION_SUPPORT_STEPS,
                                  contact_update_period=env.scene['contacts'].cfg.update_period,
                                  tire_geometry=geometry, reward_term_names=REWARD_TERMS,
                                  mujoco_reference_tire_radius_m=meta['spec']['measures']['wheel_radius_m'],
                                  learning_rates={row['name']: row['lr'] for row in alg.optimizer.param_groups},
                                  initial_exploration_std=alg.actor.distribution.std_param.tolist(),
                                  landing_pool_samples=len(landings['landings']) if landings else 0))

        def advance(action):
            nonlocal obs
            raw, reward, term, timeout, _ = env.step(action)
            if not all(bool(torch.isfinite(t).all()) for t in (*raw.values(), reward)):
                raise FloatingPointError('Nonfinite observation or reward')
            obs = observations(raw)
            return reward, term, timeout

        if not args.seconds:
            max_closure = 0.
            rays_finite = True
            physics_start = env.sample_count
            exploration = (torch.arange(env.num_envs, device=env.device) % 5 < 2)
            std = alg.actor.distribution.std_param
            probe_noise = torch.Generator(device=env.device).manual_seed(seed+392)
            flat_stand_seen = torch.zeros_like(exploration)
            flat_drive_seen = torch.zeros_like(exploration)
            with torch.inference_mode():
                for i in range(600):
                    if (job/'REQUEST_STOP').exists():
                        put(job/'STOPPED.json', dict(probe_steps=i, optimizer_steps=0))
                        return
                    action = alg.actor(obs)
                    noise = torch.randn(action.shape, device=env.device, generator=probe_noise) * std
                    action = action + noise*exploration[:, None]
                    assert bool(torch.isfinite(action).all())
                    advance(action)
                    flat_stand_seen |= env.flat_stand_ticks >= SUPPORT_STEPS
                    flat_drive_seen |= env.flat_drive_ticks >= SUPPORT_STEPS
                    for name in ('ground', 'ground_left', 'ground_right'):
                        rays = tensor(env.scene[name].data.ray_hits_w)
                        rays_finite &= bool(torch.isfinite(rays).all())
                    max_closure = max(max_closure, float(env.closure_error.max()))
                    if (i+1) % 100 == 0:
                        put(job/'LATEST.json', dict(probe_steps=i+1, rays_finite=rays_finite,
                            physical_samples=env.sample_count-physics_start, completed_by_course=env.completed.tolist(),
                            first_stage_events=int(((env.support_peak[:, 0] >= env.support_required[:, 0])
                                                    & env.obstacle).sum()),
                            done_totals=env.done_totals))
            obs = obs.clone()
            # Test the full graph without updating any weights. E0 stays frozen in PPO.
            actor.experts[0].requires_grad_(True)
            (alg.actor(obs).square().mean() + alg.critic(obs).square().mean()).backward()
            grads = [p.grad for p in list(alg.actor.parameters()) + list(alg.critic.parameters()) if p.grad is not None]
            gradients_finite = all(bool(torch.isfinite(g).all()) for g in grads)
            gradient_groups = gradient_evidence()
            actor.experts[0].zero_grad(set_to_none=True)
            actor.experts[0].requires_grad_(False)
            all_groups_trainable = all(v['l2'] > 0 and v['all_finite'] for v in gradient_groups.values())
            routing = actor.last_weights.detach()
            simplex_error = float((routing.sum(-1)-1.).abs().max())
            unchanged = all(torch.equal(before[k], v) for k, v in alg.actor.state_dict().items())
            mesh = env.terrain.silky_mesh
            mesh_finite = bool(np.isfinite(mesh.vertices).all() and np.isfinite(mesh.faces).all())
            active_dr = int((~env.full_dr.nominal_env_mask).sum())
            landing_resets = int(env.landing_resets)
            n_physics = env.sample_count-physics_start
            flat_stand = int((flat_stand_seen | env.flat_stand_measured).sum())
            flat_drive = int((flat_drive_seen | env.flat_drive_measured).sum())
            flat_samples = int(env.flat_load_samples)
            support_peaks = {name: env.support_peak[env.group == i].amax(0).tolist()
                             for i, name in enumerate(COURSES)}
            completed = dict(zip(COURSES, env.completed.tolist()))
            passed = (rays_finite and mesh_finite and gradients_finite and all_groups_trainable and unchanged
                      and optimizer_steps == 0 and active_dr == 0 and simplex_error < 1.e-6
                      and n_physics == 600*POLICY_SUBSTEPS and support_peaks['flat'][0] >= SUPPORT_STEPS)
            put(job/'PROBE.json', dict(passed=passed, steps=600, envs=2048, ppo_updates=0,
                optimizer_steps=optimizer_steps, actor_unchanged=unchanged, rays_finite=rays_finite,
                mesh_finite=mesh_finite, gradients_finite=gradients_finite,
                gradient_groups=gradient_groups, router_simplex_max_error=simplex_error,
                router_mean=routing.mean(0).tolist(), expert_0_max_error=e0_error, groups=groups, active_dr=active_dr,
                landing_resets=landing_resets, physics_samples=n_physics,
                stochastic_replicas=int(exploration.sum()),
                deterministic_replicas=int((~exploration).sum()),
                stochastic_completions=int(env.completed_by_replica[exploration].sum()),
                deterministic_completions=int(env.completed_by_replica[~exploration].sum()),
                flat_stand_supported_400hz=flat_stand, flat_drive_supported_400hz=flat_drive,
                flat_loaded_samples=flat_samples,
                flat_loaded_center_z_m=(env.flat_center_z_sum/max(1, flat_samples)).tolist(),
                flat_loaded_mean_geom_error_m=(env.flat_radial_error_sum/max(1, flat_samples)).tolist(),
                flat_loaded_mean_force_n=(env.flat_normal_force_sum/max(1, flat_samples)).tolist(),
                best_support_physics_steps=support_peaks,
                max_closure_m=max_closure, cuda_peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                cuda_peak_reserved_bytes=torch.cuda.max_memory_reserved(), done_totals=env.done_totals,
                completed_by_course=completed, reward_terms_by_course=env.rewards_total.tolist()))
            if not passed:
                raise RuntimeError('600-step native precheck failed')
            return

        def save(name):
            path = job/name
            temporary = path.with_suffix('.partial')
            payload = alg.save()
            e0_preserved = all(torch.equal(e0_before[key], value)
                               for key, value in actor.experts[0].state_dict().items())
            assert e0_preserved
            payload.update(format='mod4v3_unified_soft_moe_v1', ppo_updates=updates, optimizer_steps=optimizer_steps,
                           parent_sha256=inputs.get('resume.pt', inputs['parent.pt']),
                           selected_e0_sha256=inputs['parent.pt'], expert_0_preserved=e0_preserved,
                           iter=int(audit.get('starting_iteration', base['iter']))+updates,
                           action_order=env.order, num_envs=2048, actor_input=455, critic_input=78,
                           cpu_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state_all(),
                           reset_rng=env.reset_generator.get_state(), inputs=inputs, experts=EXPERTS,
                           router_temperature=TEMPERATURE)
            with temporary.open('wb') as stream:
                torch.save(payload, stream)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(path)
            return dict(checkpoint=name, sha256=sha256(path), ppo_updates=updates,
                        optimizer_steps=optimizer_steps, elapsed_seconds=time.monotonic()-start,
                        expert_0_preserved=e0_preserved)

        def stats():
            return dict(ppo_updates=updates, optimizer_steps=optimizer_steps,
                        elapsed_seconds=time.monotonic()-start, target_dr=env.target_dr,
                        active_dr=int((~env.full_dr.nominal_env_mask).sum()),
                        dr_promotions=env.dr_history,
                        dr_active_by_course=dict(zip(COURSES, torch.bincount(
                            env.group[env.full_dr.applied_dr], minlength=len(COURSES)).tolist())),
                        episode_attempt_success_counts=env.episode_counts.tolist(),
                        dr_promotion_attempt_success_counts=env.dr_window.tolist(),
                        initial_warm_start_sha256=audit['sha256'],
                        routing_flat_replicas=int(obs['is_flat'].sum()),
                        routing_climb_replicas=int(obs['is_climb'].sum()),
                        routing_deck_replicas=int(obs['is_deck'].sum()),
                        high_speed_command_replicas_by_course=dict(zip(COURSES, torch.bincount(
                            env.group[env.issue_forward == HIGH_SPEED_COMMAND], minlength=len(COURSES)).tolist())),
                        exploration_std=alg.actor.distribution.std_param.tolist(),
                        landing_resets=int(env.landing_resets),
                        completed_by_course=dict(zip(COURSES, env.completed.tolist())),
                        reward_terms_by_course=dict(zip(COURSES, env.rewards_total.tolist())),
                        done_totals=env.done_totals)

        alg.train_mode()
        start = time.monotonic()
        epoch = time.time()
        deadline = start+args.seconds
        put(job/'TRAIN_START.json', dict(epoch=epoch, hard_stop_epoch=epoch+args.seconds+15,
                                        compute_stop_seconds=args.seconds))
        due = 300
        max_optimization_seconds = 1.
        losses = {}
        pending_rollout_steps = 0
        stop_file = job/'REQUEST_STOP'
        while time.monotonic() < deadline and not stop_file.exists():
            env.promote_dr(time.monotonic()-start)
            pending_rollout_steps = 0
            with torch.inference_mode():
                for _ in range(cfg['num_steps_per_env']):
                    if time.monotonic() >= deadline or stop_file.exists():
                        break
                    action = alg.act(obs)
                    reward, term, timeout = advance(action)
                    terminal = TensorDict(env.terminal_observations, batch_size=[2048])
                    reward = reward + alg.gamma * alg.critic(terminal).squeeze(-1) * timeout
                    alg.process_env_step(obs, reward, term | timeout, {})
                    pending_rollout_steps += 1
                if pending_rollout_steps == cfg['num_steps_per_env'] and time.monotonic()+max_optimization_seconds < deadline:
                    alg.compute_returns(obs)
            if pending_rollout_steps != cfg['num_steps_per_env'] or stop_file.exists():
                break
            if time.monotonic()+max_optimization_seconds >= deadline:
                with torch.inference_mode():
                    while time.monotonic() < deadline and not stop_file.exists():
                        advance(alg.actor(obs, stochastic_output=True))
                        pending_rollout_steps += 1
                break
            opt_start = time.monotonic()
            alg.warmup_only = updates < CRITIC_WARMUP
            losses = alg.update()
            max_optimization_seconds = max(max_optimization_seconds, 1.25*(time.monotonic()-opt_start))
            updates += 1
            pending_rollout_steps = 0
            current = stats()
            put(job/'LATEST.json', dict(current, losses=losses, critic_warmup_only=alg.warmup_only))
            if updates in (1, CRITIC_WARMUP + 1):
                fname = 'FIRST_UPDATE.json' if updates == 1 else 'FIRST_ACTOR_UPDATE.json'
                put(job/fname, dict(current, losses=losses,
                    gradients=first_step_gradients,
                    changed_groups={key: any(not torch.equal(before[name], p)
                                             for name, p in alg.actor.named_parameters()
                                             if id(p) in {id(w) for w in module.parameters()})
                                    for key, module in modules.items()}))
            if current['elapsed_seconds'] >= due:
                name = f'model_{due//60:03d}m.pt'
                put(job/f'{name}.json', save(name))
                due += 300
        compute_elapsed = time.monotonic()-start
        result = save('model_final.pt')
        put(job/'FINAL.json', dict(stats(), checkpoint=result['checkpoint'], sha256=result['sha256'],
                                  expert_0_preserved=result['expert_0_preserved'],
                                  compute_elapsed_seconds=compute_elapsed, unfinished_rollout_steps=pending_rollout_steps,
                                  losses=losses, end_reason='request' if stop_file.exists() else 'budget'))
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

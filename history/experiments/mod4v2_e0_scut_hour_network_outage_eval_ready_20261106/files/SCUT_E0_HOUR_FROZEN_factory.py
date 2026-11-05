"""Binding-only SCUT frozen factory. No learner, physics, reset, obs or RNG calls.

The task still names the REAL current SCUT hour worker. Its load_original owns
all original imports, construction, D6 mapping, cmd/reward configure and cmd.bind.
This shim exposes the named original actor CONFIG function, not a PPO clone;
it adds only reward.bind at the frozen worker's existing sole-reset boundary.
"""
from pathlib import Path
import inspect

MODE = 'SCUT_V14_ORIGINAL_FINITE_WALL_CLOCK_HOUR'
TASK = 'Robotics-Wheelbipe-V14-Flat-v0'
HOUR_ROOT = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_HOUR_FULL_LEARNER_MIGRATION_20261106_062902_1793917742719982000'
WORKER = 'worker_e0_scut_v14_hour_v3.py'
ADAPTER_SHA = {'scut_v14_flat_reward_adapter_v4': 'ddb3f77f19a29c0bc047082aef774aa62b585801d539b670f69c434041828570', 'scut_v14_flat_command_termination_adapter_v1': '3f4c93437a7128677701d58c7012ab13a91d78bec727e1f0b1182f12316a1cd8'}


class Unknown(RuntimeError):
    """Absent/different source-verified field; never a guessed zero or pass."""


def require(value, message):
    if not value:
        raise Unknown(message)


def field(obj, name):
    if not hasattr(obj, name):
        raise Unknown('Required field missing: ' + type(obj).__module__ + '.' + type(obj).__qualname__ + '.' + name)
    value = getattr(obj, name)
    if value is None:
        raise Unknown('Required field is None: ' + name)
    return value


def tensor_view(value, torch, label):
    # Named actual ABI only, full zero-copy view, no reshape/cast/fill/copy.
    if isinstance(value, torch.Tensor):
        return value
    from isaaclab.utils.warp import ProxyArray
    if isinstance(value, ProxyArray):
        view = value.torch
        require(isinstance(view, torch.Tensor) and
                tuple(view.shape[:len(value.shape)]) == tuple(value.shape),
                'ProxyArray cached Torch array-shape prefix differs: ' + label)
        return view  # Warp vector/quaternion component axes MUST stay present.
    raise Unknown('Unsupported tensor ABI for ' + label + ': ' + type(value).__module__ + '.' +
                  type(value).__qualname__ + ' shape=' + str(getattr(value, 'shape', None)))


def load_original(actual, task, out):
    require(task['role'] == 'E0' and task['training_window_mode'] == actual.SCUT_MODE == MODE and
            actual.SCUT_TASK == TASK and actual.SCUT_ADAPTER_SHA == ADAPTER_SHA,
            'Exact current SCUT hour source/mode/adapters required')
    require(str(Path(actual.__file__).resolve()) == HOUR_ROOT + '/' + WORKER == task['migration_worker'],
            'Task.migration_worker must explicitly be the real current SCUT hour worker')
    ns, binding, actual_cfg = actual.load_original(task, out)
    require(task.get('_env') is None and not actual_cfg,
            'load_original must not construct/reset/advance an environment')
    wrapped = ns['runner_config']
    require(inspect.isfunction(wrapped) and wrapped.__module__ == actual.__name__,
            'Named actual-hour runner_config wrapper identity differs')
    closure = inspect.getclosurevars(wrapped).nonlocals
    require('original_runner_config' in closure, 'Source-verified original_runner_config closure absent')
    original = closure['original_runner_config']
    require(inspect.isfunction(original) and original.__globals__ is ns and
            original.__name__ == 'runner_config' and
            Path(original.__code__.co_filename).resolve() == Path(ns['__file__']).resolve(),
            'Original E0 actor configuration function identity differs')
    # Training-only wrapper pins formal6cd LR. Frozen evaluation constructs NO
    # runner/critic/optimizer; keep the original actor cfg function itself and
    # expose actual candidate FINAL.live_core LR, never fabricate formal6cd LR.
    require(task['source_LR'] == task['checkpoint_LR'] == task['candidate_live_core']['source_LR'] and
            task['source_iteration'] == task['checkpoint_iteration'] == task['candidate_live_core']['iteration'],
            'One FINAL.fullsave.live_core must own candidate LR and iteration')
    ns['args'].learning_rate = task['checkpoint_LR']
    ns['runner_config'] = original
    task['_SCUT_actor_config_binding'] = dict(
        original_function_recovered_from_named_actual_hour_closure=True,
        original_actor_configuration_function_unmodified=True,
        training_only_formal_LR_assertion_not_called=True,
        candidate_LR=task['checkpoint_LR'], candidate_iteration=task['checkpoint_iteration'],
        candidate_metadata_origin='FINAL.fullsave.live_core',
        no_PPO_implementation_or_live_critic_optimizer=True)
    return ns, binding, actual_cfg


def observed_binding(task, env, actual_cfg, torch, phase):
    require(phase in ('BEFORE_SOLE_RESET', 'AFTER_SOLE_RESET', 'AFTER_FINITE_EVAL'), 'Named binding boundary')
    cmd, reward = task['_scut_cmd'], task['_scut_reward']
    sources = task['_scut_adapter_sources']
    require(set(sources) == set(ADAPTER_SHA), 'Exact actual loader adapter source set')
    for name, wanted in ADAPTER_SHA.items():
        require(sources[name]['SHA256'] == wanted and sources[name]['path'] == HOUR_ROOT + '/' + name + '.py',
                'Pinned actual source adapter path/SHA differs: ' + name)
    require(task['_scut_cmd_configure']['task'] == task['_scut_cmd_bind']['task'] == TASK and
            actual_cfg['scut_reward_configure']['task'] == TASK,
            'Actual constructor command/reward configure and command.bind receipts required')
    cfg = field(env, 'cfg')
    require(env.num_envs == 80 and cfg.scene.num_envs == 80 and
            env.physics_dt == .0025 and env.step_dt == .02 and cfg.decimation == 8,
            'Actual original N80 physical interface')
    command = env.command_manager.get_term('twist')
    require(type(command) is cmd.ScutV14FlatCommand and cfg.commands.twist.class_type is cmd.ScutV14FlatCommand and
            command.training_iteration == task['candidate_live_core']['iteration'] == task['source_iteration'],
            'Actual SCUT command class/real candidate iteration differs')
    require(field(env, '_scut_v14_bound') is True and
            cfg.terminations.scut_v14.func is cmd.scut_termination and
            cfg.terminations.time_out.func is cmd.scut_time_out and cfg.terminations.time_out.time_out is True,
            'Actual SCUT done/timeout binding missing')
    terms = list(env.termination_manager.active_terms)
    require({'scut_v14', 'time_out', 'closure', 'mimic'} <= set(terms) and
            not ({'bad_orientation', 'base_contact', 'low_base', 'tunnel_roof_hit'} & set(terms)),
            'Original hardware rules plus SCUT performance/timeout terms required')
    require(cfg.terminations.closure.params['threshold'] == .01 and
            cfg.terminations.mimic.params['threshold'] == .01, 'Original .01 hardware gates')
    active = list(env.reward_manager.active_terms)
    require(active == list(reward.ACTIVE_WEIGHTS) and len(reward.REWARD_WEIGHTS) == 37 and len(active) == 26,
            'Actual original 37/26 reward order')
    weights = {}
    for name in active:
        term = env.reward_manager.get_term_cfg(name)
        require(term.func is reward._raw_term and term.weight == reward.ACTIVE_WEIGHTS[name] and
                term.params == {'name': name}, 'Actual SCUT reward term differs: ' + name)
        weights[name] = float(term.weight)
    controls = int(field(env, 'common_step_counter'))
    state = getattr(env, reward.STATE_NAME, None)
    reward_last_step = None
    cached_shape = None
    if phase == 'BEFORE_SOLE_RESET':
        require(state is None, 'Reward must bind once only after the sole fresh reset')
    else:
        require(type(state) is reward._RewardState and state.env is env and state.manager is env.reward_manager and
                tuple(state.prev.shape) == tuple(state.prevprev.shape) == (80, 6),
                'Actual unmodified reward.bind state/history ownership')
        require(task['_scut_reward_bind']['abi'] == 'SCUT_V14_FLAT_REWARD_V1' and
                task['_scut_reward_bind']['active_weights'] == weights,
                'Actual reward.bind receipt missing or changed')
        reward_last_step = int(state.last_step)
        require(reward_last_step == controls, 'Reward/control alignment differs')
        # Read only the already populated sensor cache, never .data/refresh/_inputs.
        data = field(state.sensor, '_data')
        history = tensor_view(field(data, 'net_forces_w_history'), torch, 'cached SCUT reward contact history')
        cached_shape = list(history.shape)
        require(tuple(history.shape) == (80, 3, len(state.sensor.body_names), 3),
                'Cached source reward contact [N,3,B,3] gate differs')
        require(state.sensor.cfg.history_length == 3 and state.sensor.cfg.update_period == .005,
                'Original reward contact-history clock')
    if phase in ('BEFORE_SOLE_RESET', 'AFTER_SOLE_RESET'):
        require(controls == 0 and int(env._sim_step_counter) == 0 and int(env._integrated_contact.tick) == 0,
                'Exactly zero precontrols at SCUT binding boundary')
    else:
        require(controls == task['controls'] == 1000, 'Original finite SCUT control count')
        # mod4_task.closure_broken/mimic_broken publish these per-env cached
        # tensors during original termination compute. Do not synthesize zeros
        # when a real observer field is absent; do not recompute the algorithms.
        for name in ('_mod4_closure_now', '_mod4_mimic_now'):
            metric = tensor_view(field(env, name), torch, 'cached original hardware observer ' + name)
            require(tuple(metric.shape) == (80,) and bool(torch.isfinite(metric).all()),
                    'Unknown: cached original hardware observer ABI differs: ' + name)
    return dict(mode=MODE, task=TASK, phase=phase, role='E0', num_envs=env.num_envs,
        actual_command_class=type(command).__module__ + '.' + type(command).__qualname__,
        real_candidate_iteration=command.training_iteration, controls=controls,
        command_done_bound=True, reward_configured=True, reward_bound=state is not None,
        active_reward_weights=weights, original_ordered_weights=list(reward.REWARD_WEIGHTS.items()),
        actual_termination_terms=terms, actual_adapter_sources=sources,
        reward_last_step=reward_last_step, cached_contact_history_shape=cached_shape,
        cached_sensor_read_only=True, no_extra_reset_observation_RNG_or_precontrol=True,
        reward_and_cached_sensor_algorithms_unmodified=True,
        actor_config_binding=task['_SCUT_actor_config_binding'], skill_grader=None, full_skill_graduation=None)


def before_sole_reset(task, env, actual_cfg, torch):
    task['_SCUT_before_reset_binding'] = observed_binding(task, env, actual_cfg, torch, 'BEFORE_SOLE_RESET')


def bind_after_sole_reset(task, env, actual_cfg, torch):
    require(task['_SCUT_before_reset_binding']['controls'] == 0 and
            getattr(env, task['_scut_reward'].STATE_NAME, None) is None,
            'Source-prescribed prebind/sole-reset boundary')
    task['_scut_reward_bind'] = task['_scut_reward'].bind(env)
    task['_SCUT_eval_binding'] = observed_binding(task, env, actual_cfg, torch, 'AFTER_SOLE_RESET')

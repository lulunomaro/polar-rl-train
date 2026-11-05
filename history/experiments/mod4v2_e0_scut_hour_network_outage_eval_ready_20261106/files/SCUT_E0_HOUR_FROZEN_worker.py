"""SOURCE ONLY: original finite N80 observers on a NEW MOD4v2 candidate.

This version admits ONLY the current E0 singleton cohort; other family source is
retained but never admitted. Parent schedules only after that E0 migration cohort
close/wait/settle/release, then owns fresh evaluation admission, start barrier and
actual child wait. Task explicitly selects worker_e0_scut_v14_hour_v3.py. No
migration/training function, native_initialized, validation zero-control, old
physical restore, saved20k projection or automatic retry is called.  Exactly one
complete candidate byte-read/hash/CPU decode; unknown/historical roots stay CPU.
Original role observers/recipes/thresholds are reused, not new skill graders.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import traceback
from types import SimpleNamespace
import SCUT_E0_HOUR_FROZEN_factory as frozen_factory

SCHEMA = 'mod4v2.original_n80_frozen_eval.v1'
KIND = 'MOD4V2_N80_FRESH_FULLDR_FROZEN_FINITE_NOT_GRADUATION'
CONTROLS = {'E0': 1000, 'E2': 1200, 'E3': 160, 'H1_normal': 1000, 'W35': 1600,
            'CURB_PROTECTED878': 750, 'CURB_INDEPENDENT113': 750,
            'SLOPE135': 750, 'SLOPE_INDEPENDENT50': 1000}
E1 = ('CURB_PROTECTED878', 'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50')
MANUAL_E1 = E1[:3]
CAPACITY = dict(gpu_max_rigid_contact_count=2**20, gpu_max_rigid_patch_count=2**16,
                gpu_found_lost_pairs_capacity=2**18, gpu_found_lost_aggregate_pairs_capacity=2**22,
                gpu_total_aggregate_pairs_capacity=2**20)


def need(value, message):
    if not value:
        raise ValueError(message)


def put(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.partial')
    need(not path.exists() and not temporary.exists(), 'Exclusive own output already exists: ' + str(path))
    raw = json.dumps(value, indent=2, allow_nan=False).encode('utf-8')
    with temporary.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    if os.name == 'posix':
        fd = os.open(str(path.parent), os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def fail(out, phase):
    error = traceback.format_exc()
    name = 'WORKER_ERROR.json'
    if (out / name).exists():
        name = 'WORKER_ERROR_%s.json' % time.time_ns()
    put(out / name, dict(schema=SCHEMA, phase=phase, epoch=time.time(), error=error,
                         no_automatic_retry=True, source_or_AppLauncher_is_not_native_proof=True))
    return error


def source_module(path, name):
    path = Path(path).resolve(strict=True)
    need(path.suffix == '.py', 'Explicit Python helper required')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_task(task, out, group):
    role = task['role']
    need(task.get('kind', KIND) == KIND and role == 'E0' and task['num_envs'] == 80 and
         task['seed'] == 20260928 and task['controls'] == CONTROLS[role], 'Only E0 original N80/1000 controls/seed admitted')
    need(task['owner_pid'] == os.getppid() and time.time() < task['absolute_worker_deadline_epoch'],
         'Actual evaluation parent and unexpired deadline required')
    need(out.is_relative_to(group) and os.environ['CUDA_VISIBLE_DEVICES'] == task['GPU_UUID'],
         'Parent-owned output/GPU binding differs')
    closed = task['migration_cohort_close_receipt']
    if isinstance(closed, str):
        path = Path(closed)
        closed = json.loads(path.read_text(encoding='utf-8'))
    need(isinstance(closed, dict) and closed['roles'] == ['E0'] and
         all(closed.get(k) is True for k in ('all_closed', 'actual_wait_complete', 'resources_released', 'GPU_settled')),
         'Current E0 singleton migration cohort actual close/wait/settle/release is required before evaluation')
    admission = task['eval_admission']
    need(admission['group_id'] == task['group_id'] and admission['GPU_UUID'] == task['GPU_UUID'] and
         admission['private_GPU_EX_held'] is True and admission['global_finite_EX_held'] is True and
         float(closed['closed_epoch']) <= float(admission['admitted_epoch']) <= time.time(),
         'Fresh post-migration evaluation admission required')
    fds = admission['inherited_lock_fds']
    need(len(fds) >= 2 and len(set(fds)) == len(fds), 'Inherited parent evaluation descriptors required')
    for fd in fds:
        need(type(fd) is int and fd >= 0, 'Invalid inherited descriptor')
        os.fstat(fd)  # Never acquire/release/replace parent locks.
    members = task['eval_members']
    need(members == ['E0'], 'Explicit E0 singleton evaluation member scope required')
    for name in ('helper_root', 'v8_helper_root', 'e1_helper_root'):
        root = Path(task[name]).resolve(strict=True)
        need(root.is_dir(), 'Missing uploaded helper root: ' + name)
        sys.path.insert(0, str(root))
    need(closed['training_root'] == frozen_factory.HOUR_ROOT and closed['training_window_mode'] == frozen_factory.MODE and
         closed['U000_exact7'] is True and closed['actual_child_semantic_qualification']['qualified'] is True and
         closed['actual_child_semantic_qualification']['errors'] == [] and
         task['migration_worker'] == frozen_factory.HOUR_ROOT + '/' + frozen_factory.WORKER,
         'Actual current SCUT CLOSED/qualified/U000 identity required')
    task['_migration_closed'] = closed
    task.setdefault('max_additional_updates', 1)  # Original entry CLI parsing only; no trainer is called.
    task.setdefault('steps_per_env', 24)
    task['_out'] = str(out)


def check_stop(task, group):
    need(os.getppid() == task['owner_pid'], 'Evaluation parent changed')
    if time.time() >= task['absolute_worker_deadline_epoch']:
        raise TimeoutError('Original finite evaluation parent deadline')
    for name in ('GROUP_ABORT.json', 'GROUP_STARTUP_ABORT.json', 'STOP_EVAL.json'):
        if (group / name).exists():
            raise RuntimeError('Parent evaluation abort: ' + name)


def wait_start(task, out, group, ready):
    put(out / 'WORKER_SCENE_READY.json', dict(schema=SCHEMA, kind=KIND, epoch=time.time(),
        role=task['role'], group_id=task['group_id'], GPU_UUID=task['GPU_UUID'], worker_pid=os.getpid(),
        zero_controls_before_barrier=True, actor_calls=0, **ready))
    deadline = min(task['absolute_worker_deadline_epoch'], time.time() + 900.)
    while time.time() < deadline:
        check_stop(task, group)
        path = group / 'GROUP_EVAL_START.json'
        if path.exists():
            value = json.loads(path.read_text(encoding='utf-8'))
            need(value['group_id'] == task['group_id'] and value['GPU_UUID'] == task['GPU_UUID'] and
                 value['all_members_ready'] is True and
                 value['members'] == ['E0'] and task['eval_members'] == ['E0'],
                 'Actual evaluation start barrier membership differs')
            put(out / 'WORKER_EVAL_STARTED.json', dict(schema=SCHEMA, epoch=time.time(), role=task['role'],
                group_id=task['group_id'], GPU_UUID=task['GPU_UUID'], zero_precontrols=True))
            return value
        time.sleep(.1)
    raise TimeoutError('Finite evaluation ready/start barrier expired without control')


def checkpoint_cache(torch, task):
    # Reuse original whole-root once-only CPU cache, not a tensor whitelist/unwrapper.
    original = importlib.import_module('parallel_eval_safe')
    descriptor = dict(source_path=task['checkpoint_path'], source_SHA=task['checkpoint_SHA'],
        source_bytes=task['checkpoint_bytes'], source_iteration=task['checkpoint_iteration'],
        source_Adam17=task['checkpoint_Adam_step'], source_LR=task['checkpoint_LR'])
    cache = original.WholeCheckpointFreshCache(torch, descriptor)
    migration = cache.state.get('mod4v2_migration')
    need(isinstance(migration, dict) and migration['role'] == task['role'] and
         migration['actual_new_updates'] > 0, 'Selected new complete MOD4v2 candidate provenance required')
    if task.get('migration_run_id') is not None:
        need(migration['run_id'] == task['migration_run_id'], 'Candidate migration run differs')
    need(migration['window_mode'] == task['training_window_mode'] == frozen_factory.MODE and
         migration['requested_effective_update_quota'] is None and migration['hour_not_started'] is False and
         migration['source_SHA'] == task['formal_source_SHA'] and migration['source_once1'] is True and
         migration['iteration_published_by_original_runner'] is True and migration['iteration_label_rewritten'] is False and
         migration['old_physical_state_restored'] is False and migration['source_env_state_applied'] is False and
         migration['source_unknowns_are_CPU_history_not_live_state'] is True,
         'Actual complete SCUT candidate metadata, not a renamed non-SCUT/probe/partial checkpoint')
    initial = migration['initial_checkpoint_acceptance']
    exact7 = ('actor_exact', 'critic_exact', 'normalization_exact', 'learned_STD_exact', 'Adam17_exact', 'LR_exact', 'iteration_exact')
    need(initial == task['initial_checkpoint_acceptance'] and initial['passed'] is True and initial['accepted'] is True and
         all(initial[k] is True for k in exact7) and initial['mode'] == frozen_factory.MODE and
         initial['source_SHA'] == task['formal_source_SHA'], 'Cached actual SCUT U000 exact7 receipt')
    need(migration['actual_new_updates'] == task['candidate_actual_updates'] and
         migration['actual_optimizer_steps'] == task['candidate_actual_optimizer_steps'] and
         migration['actual_rollout_controls'] == task['candidate_actual_rollout_controls'],
         'Candidate counters must agree with the same actual FINAL/save, never calculated labels')
    need(task['_hour_cpu_core_reader'](cache.state, torch) == task['candidate_live_core'],
         'Whole CPU candidate core must equal FINAL.fullsave.live_core directly')
    task['_candidate_SCUT_cache_binding'] = dict(mode=migration['window_mode'], same_FINAL_live_core=True,
        U000_exact7=True, actual_new_updates=migration['actual_new_updates'], physical_history_applied=False)
    def cpu_only(value):
        if torch.is_tensor(value):
            need(value.device.type == 'cpu', 'Unknown/history cached tensor escaped CPU')
        elif isinstance(value, dict):
            for item in value.values():
                cpu_only(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                cpu_only(item)
    cpu_only(cache.state)
    cache.SHA = cache.source_SHA
    cache.assert_entire_root_unchanged = cache.check
    def core(key):
        need(key in ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict', 'iter'),
             'Saved physical state is not exposed to the fresh environment')
        return cache.state[key]
    cache.core = core
    def no_other_checkpoint(*args, **kwargs):
        raise RuntimeError('Frozen eval permits only the complete already-cached candidate; no other PT or restore')
    torch.load = no_other_checkpoint
    def no_update(*args, **kwargs):
        raise RuntimeError('Frozen eval has no live optimizer/PPO update')
    torch.optim.Optimizer.step = no_update
    torch.optim.Adam.step = no_update
    return cache


def frozen_actor(ns, cache, env, torch):
    """Construct only the ORIGINAL configured actor, including its own normalizer."""
    from tensordict import TensorDict
    cfg = ns['runner_config']()
    cfg = ns['handle_deprecated_rsl_rl_cfg'](cfg, ns['metadata'].version('rsl-rl-lib')).to_dict()
    need(isinstance(cfg.get('actor'), dict), 'Actual original SDK config has no actor-only mapping')
    actor_cfg = copy.deepcopy(cfg['actor'])
    class_name = actor_cfg.pop('class_name')
    if class_name == 'MLPModel':
        module_name, attribute = 'rsl_rl.models', 'MLPModel'
    elif ':' in class_name:
        module_name, attribute = class_name.split(':', 1)
    else:
        module_name, attribute = class_name.rsplit('.', 1)
    cls = getattr(importlib.import_module(module_name), attribute)
    need(cls.__name__ == 'MLPModel' and cfg['obs_groups']['actor'] == ['policy'],
         'Actual original A0 actor-only ABI differs; no guessed SDK fallback')
    external_norm = [k for k in cache.state if 'normalizer' in k.lower() and k.endswith('state_dict')]
    need(not external_norm, 'Standalone normalizer schema needs its original actor loader: ' + repr(external_norm))
    observations = TensorDict(dict(policy=torch.zeros(80, 35), critic=torch.zeros(80, 38)), batch_size=[80])
    with torch.random.fork_rng(devices=[]):
        actor = cls(observations, cfg['obs_groups'], 'actor', 6, **actor_cfg)
        actor.load_state_dict(cache.state['actor_state_dict'], strict=True)
    need(all(p.device.type == 'cpu' for p in actor.parameters()), 'Actor constructor unexpectedly allocated a device')
    actor.to(env.device).eval().requires_grad_(False)
    cache.check_actor(actor)
    cache.live_actor_STD_loaded = True
    return actor, dict(original_actor_class=class_name, original_actor_cfg=actor_cfg,
        strict_actor_and_embedded_learned_normalizer=True, no_live_critic_or_optimizer=True,
        normalization_updated=False, mean_only=True)


class RouteV2(ast.NodeTransformer):
    """Preserve original route/query/reset/commands, adapt only D0 construction."""
    def __init__(self):
        self.constructor_calls = 0
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == 'E1ResetEvidenceLearningEnv':
            node.args.insert(0, ast.Name(id='E1ResetEvidenceLearningEnv', ctx=ast.Load()))
            node.func = ast.Name(id='_v2_route_construct', ctx=ast.Load())
            self.constructor_calls += 1
        return node


def actual_identity(ns, binding, task):
    need(binding['asset_sha256'] == task['asset_SHA'] and
         binding['contract_sha256'] == task['contract_SHA'], 'Actual target V2 asset/contract differs')
    contract = ns['mod4_task'].CONTRACT
    need(contract.get('mechanical_limits_v2') is not None, 'Actual V2 mechanical contract required')
    return SimpleNamespace(usd_path=binding['asset'], usd_sha256=binding['asset_sha256'],
        contract_path=str(Path(task['v2_package']) / 'assets/import_contract.json'),
        contract_sha256=binding['contract_sha256'], contract=contract)


def fresh_bundle(task, out, ns, migration, binding, actual_cfg, torch):
    import numpy as np
    import warp as wp
    def tensor(value):
        return frozen_factory.tensor_view(value, torch, 'original finite observer/fresh DR field')
    bridge = importlib.import_module('e1_fresh_runtime_bridge')
    identity = actual_identity(ns, binding, task)
    ns['args'].num_envs = 80
    ns['args'].seed = 20260928
    if task['role'] in MANUAL_E1:
        path = Path(task['e1_helper_root']) / 'e1_route80_factories.py'
        removed = migration.EntryV2()
        tree = removed.visit(ast.parse(path.read_text(encoding='utf-8'), filename=str(path)))
        route = RouteV2()
        tree = route.visit(tree)
        ast.fix_missing_locations(tree)
        need(route.constructor_calls == 3, 'Original three route factory constructors differ')
        namespace = dict(__name__='_mod4v2_original_route80', __file__=str(path))
        exec(compile(tree, str(path), 'exec'), namespace)
        adapter = importlib.import_module('runtime_adapter_v2')
        def construct(cls, **kwargs):
            cfg = kwargs['cfg']
            if not hasattr(cfg.sim, 'physx') and getattr(cfg.sim, 'physics', None) is not None:
                cfg.sim.physx = cfg.sim.physics
            actual_cfg['receipt'] = adapter.apply_runtime_cfg(cfg, ns['mod4_task'], prebuild=True)
            actual_cfg['cfg'] = cfg
            env = cls(**kwargs)
            task['_env'] = env
            return env
        namespace['_v2_route_construct'] = construct
        bundle = namespace['build_original_route80'](task['role'], task, out, identity, torch, np, wp, tensor)
        task['_route_derivation'] = dict(source=str(path), source_SHA=hashlib.sha256(path.read_bytes()).hexdigest(),
            removed_V1_asset_calls=removed.removed, V2_prebuild_constructor_calls=route.constructor_calls,
            original_route_recipe_queries_manual_commands_and_predicate_unchanged=True)
    else:
        original = ns['build_env'].__globals__['Mod4Env']
        def allocate(**kwargs):
            cfg = kwargs['cfg']
            need(cfg.scene.num_envs == 80, 'Fresh eval N80 before construction required')
            physics = getattr(cfg.sim, 'physics', None) or cfg.sim.physx
            before = {k: getattr(physics, k) for k in CAPACITY}
            for key, value in CAPACITY.items():
                setattr(physics, key, value)
            env = original(**kwargs)
            env._n80_allocation_only_capacity = dict(SDK_original_capacity=before,
                explicit_original_route80_preset=dict(CAPACITY), plant_solver_DR_RNG_unchanged=True)
            return env
        ns['build_env'].__globals__['Mod4Env'] = allocate
        env = ns['build_env']()
        task['_env'] = env
        guard = bridge.attach_fresh_guard(env, identity, torch, tensor)
        book = None
        if task['role'] == 'W35':
            from rm70_intervals227 import RM70Intervals227
            book = RM70Intervals227(torch, 80, env.device, out, task['checkpoint_SHA'])
            book.install(type(env.command_manager.get_term('twist')))
            task['_book'] = book
        frozen_factory.before_sole_reset(task, env, actual_cfg, torch)
        env.reset()
        frozen_factory.bind_after_sole_reset(task, env, actual_cfg, torch)
        if book is not None:
            task['_book_arm'] = book.arm(env, env.command_manager.get_term('twist'))
        if task['role'] == 'E3':
            env.e3_reset_enabled = True
            env.place_declared_fall(torch.arange(80, device=env.device))
            env.publish()
            need(set(env.recovery.recipe.tolist()) == set(range(13)) and
                 int((env.recovery.recipe == 12).sum()) == 6, 'Original E3 request74/normal6 cohort differs')
        bundle = dict(env=env, robot=env.scene['robot'], guard=guard,
            audit_before=bridge.fresh_full_dr_audit(env, guard, tensor), route_scope={},
            command=env.command_manager.get_term('twist'), manual=False, groups=None, targets=None)
    env = bundle['env']
    if task['role'] in ('CURB_INDEPENDENT113', 'SLOPE_INDEPENDENT50'):
        axis = importlib.import_module('independent_expert_axis_v1')
        state = axis.bind_after_restore(env, 'CURB20' if task['role'] == 'CURB_INDEPENDENT113' else 'SLOPE5')
        task['_fresh_axis'] = dict(kind=state['kind'], original_private_RNG_draws_unchanged=True,
            command_manual_mode=bool(getattr(bundle['command'], 'manual_evaluation_mode', False)),
            original_inward_writer_installed=task['role'] == 'CURB_INDEPENDENT113')
        if task['role'] == 'SLOPE_INDEPENDENT50':
            bundle['route_scope'] = dict(kind='OWN_SLOPE50_DEFAULT_TRAINING_AXIS_SCREEN_NOT_ORIGINAL_ACCEPTED80',
                centers=state['centers'].detach().cpu().tolist(), target_family_mask=state['target'].detach().cpu().tolist(),
                origins=state['origin'].detach().cpu().tolist(), scope='Original fullramp axis; accepted cohort/predicate GAP')
    need(env.num_envs == 80 and env.physics_dt == .0025 and env.step_dt == .02 and env.cfg.decimation == 8,
         'Actual original N80/400Hz/50Hz interface differs')
    need(int(env._sim_step_counter) == 0 and int(env._integrated_contact.tick) == 0 and
         bridge.HOLDER['explicit_reset_count'] == [1], 'Exactly one fresh reset and ZERO precontrols required')
    return bundle, tensor, np, wp


def native_static_readback(ns, env, torch):
    """Read actual fresh native DOF limits; no validation control/observation compute."""
    limits = env.scene['robot'].root_view.get_dof_limits()
    limits = frozen_factory.tensor_view(limits, torch, 'actual fresh native DOF limits')
    names = list(env.scene['robot'].joint_names)
    need(tuple(limits.shape) == (80, len(names), 2), 'Unknown: actual native DOF [80,joints,2] ABI differs')
    rows = []
    for name, spec in ns['mod4_task'].CONTRACT['joints'].items():
        if spec.get('limits_si') is None or name not in names:
            continue
        values = limits[:, names.index(name)]
        for endpoint, wanted in enumerate(spec['limits_si']):
            column = values[:, endpoint]
            if wanted is None:
                sign = -1 if endpoint == 0 else 1
                good = (torch.isinf(column) & (column * sign > 0)) | (torch.isfinite(column) & (column * sign >= 1e6))
            else:
                good = torch.isfinite(column) & ((column - wanted).abs() <= 1e-6)
            need(bool(good.all()), 'Actual V2 native mechanical limit differs: ' + name)
        rows.append(dict(name=name, expected=spec['limits_si'], actual_all_N80_verified=True))
    return dict(actual_native_mechanical_limits=rows, source_presence_not_native_proof=True,
                no_precontrol=True, not_N20000_native_admission_replay=True)


def five_loop(task, out, group, bundle, cache, actor, torch, tensor):
    from tensordict import TensorDict
    env, robot, role = bundle['env'], bundle['robot'], task['role']
    guard = bundle['guard']
    book = task.get('_book')
    cycles = None
    if role == 'E2':
        import e2_cycles213
        e2_cycles213.MODEL = task['checkpoint_SHA']  # Producer identity only, not any threshold/UID rule.
        from minimal_e2_cycles_bridge import E2FreshCycleBridge
        cycles = E2FreshCycleBridge(env, torch, tensor, out)
    reasons = {key: 0 for key in env.termination_manager.active_terms}
    terminated = torch.zeros(80, dtype=torch.bool, device=env.device)
    truncated = terminated.clone(); live = ~terminated; events = torch.zeros(80, dtype=torch.long, device=env.device)
    credit = terminated.clone(); first_term = terminated.clone(); old002 = terminated.clone()
    error_integral = torch.zeros(80, 3, device=env.device); reward_sum = torch.zeros(80, device=env.device)
    root_initial = tensor(robot.data.root_pos_w).clone(); root_last = root_initial.clone()
    first_recipe = env.recovery.recipe.clone() if role == 'E3' else None
    h1_flags = {}; command_before = None; closure_max = mimic_max = 0.; completed = 0; maxraw = maxapplied = 0.
    original_terminal = env.termination_manager.compute
    def terminal(*args, **kwargs):
        nonlocal root_last, closure_max, mimic_max
        value = original_terminal(*args, **kwargs)
        tm = env.termination_manager
        if book is not None:
            book.terminal(env._e1_pre_reset_frame, tm)
        if cycles is not None:
            cycles.terminal()
        ter, tru = tm.terminated.clone(), tm.time_outs.clone()
        terminated.logical_or_(ter); truncated.logical_or_(tru); events.add_((ter | tru).long())
        root_last = tensor(robot.data.root_pos_w).clone()
        for name in reasons:
            reasons[name] += int(tm.get_term(name).sum())
        if command_before is not None:
            vb, yaw = tensor(robot.data.root_lin_vel_b), tensor(robot.data.root_ang_vel_b)[:, 2]
            error_integral.add_(torch.stack((vb[:, 0] - command_before[:, 0], vb[:, 1] - command_before[:, 1],
                                            yaw - command_before[:, 2]), 1).abs() * .02)
        clo, mim = getattr(env, '_mod4_closure_now', None), getattr(env, '_mod4_mimic_now', None)
        if clo is not None:
            closure_max = max(closure_max, float(clo.max())); old002.logical_or_(clo > .002)
        if mim is not None:
            mimic_max = max(mimic_max, float(mim.max()))
        if role == 'E3':
            credit.logical_or_(env.recovery.credited & live); first_term.logical_or_(ter & live)
        if role == 'H1_normal':
            phase = getattr(env, 'h1_phase', None)
            for label, obj in (('phase', phase), ('goal', getattr(phase, 'goal', None)), ('events', getattr(phase, 'events', None))):
                if obj is not None:
                    for key, item in vars(obj).items():
                        if torch.is_tensor(item) and item.shape == (80,) and item.dtype == torch.bool:
                            name = label + '.' + key
                            if name not in h1_flags:
                                h1_flags[name] = item.clone()
                            else:
                                h1_flags[name].logical_or_(item)
        live.logical_and_(~(ter | tru))
        return value
    env.termination_manager.compute = terminal
    obs = env.observation_manager.compute()  # Original five-role initial compute, never an extra zero step.
    guard.check_observations(obs)
    tick, feedback = int(env._integrated_contact.tick), int(env._feedback_100hz_tick)
    delay = dict(env._physics_action_delay.calls); started = time.time()
    try:
        with torch.inference_mode():
            for i in range(task['controls']):
                check_stop(task, group)
                command_before = tensor(env.command_manager.get_term('twist').command).clone()
                if book is not None:
                    book.begin(i, tensor(robot.data.root_pos_w)[:, :2].clone(), tensor(robot.data.heading_w).clone())
                if cycles is not None:
                    cycles.begin(i)
                actor_obs = obs if isinstance(obs, TensorDict) else TensorDict(dict(obs), batch_size=[80])
                action = actor(actor_obs, stochastic_output=False)
                need(action.shape == (80, 6) and bool(torch.isfinite(action).all()), 'Actual A0 action nonfinite/shape')
                maxraw = max(maxraw, float(action.abs().max())); applied = action.clamp(-6., 6.)
                maxapplied = max(maxapplied, float(applied.abs().max()))
                obs, reward, ter, tru, extra = env.step(applied); completed += 1; task['_completed_controls'] = completed
                reward_sum.add_(reward)
                need(obs['policy'].shape == (80, 35) and obs['critic'].shape == (80, 38) and
                     all(bool(torch.isfinite(x).all()) for x in (obs['policy'], obs['critic'], reward)), 'Actual observation/reward differs')
        physics = int(env._integrated_contact.tick) - tick
        samples = int(env._feedback_100hz_tick) - feedback
        calls = {k: env._physics_action_delay.calls[k] - delay[k] for k in ('legs', 'wheels')}
        need(physics == 8 * completed and samples == 2 * completed and
             calls == dict(legs=8 * completed, wheels=8 * completed), 'Actual original cadence differs')
        skill = dict(full_skill_graduation=None, no_new_aggregate_graduation_rate=True,
            original_aggregate_graduation_rule='NONE_IN_JOINED_SOURCE_NO_NEW_PASS_RATE',
            body_velocity_absolute_error_time_integral_per_env=error_integral.cpu().tolist(),
            root_before_and_last_terminal_world_xyz_per_env=dict(before=root_initial.cpu().tolist(), last=root_last.cpu().tolist()),
            no_cross_reset_endpoint_displacement_success_claim=True)
        if role == 'E0':
            skill.update(full_grader=None, predicate_gap='Original complete binary/profile grader absent')
        if role == 'E3':
            skill.update(original_recovery_recipe_rows=[dict(recipe=r, initial_envs=int((first_recipe == r).sum()),
                original_request=r != 12, first_episode_original_stable_credit=int(((first_recipe == r) & credit).sum()),
                first_episode_physical_terminated=int(((first_recipe == r) & first_term).sum())) for r in range(13)],
                request_denominator=74, normal_recipe12_excluded=6, stable50_public100Hz_age_equals_seconds=.5,
                stable50_equals_policy_controls=25, request300_age_seconds=3., no_reset_stitched_credit=True)
        if role == 'H1_normal':
            skill.update(original_phase_natural_boolean_event_counts={k: int(v.sum()) for k, v in h1_flags.items()},
                horizon_scope='20seconds original cfg; not original accepted cohort',
                original_270mm_event_source='Original Step270 physical callbacks; no generic height replacement')
        if cycles is not None:
            skill.update(original_E2_sameUID_cycle_facts=cycles.finish(),
                cycle_rule='SameUID/episode/direction/sign full signed2pi; along .5+-.05/cross+-.05/yaw+-.2; nonterminal/nontimeout')
            cycles = None
        if book is not None:
            skill['original_RM70_interval_route_facts'] = book.finish(); book.uninstall(); task['_book'] = None; book = None
        return dict(controls=completed, seconds=.02 * completed, physics_callbacks=physics, feedback_samples=samples,
            delay_calls=calls, termination_events_by_reason=reasons, unique_envs_terminated=int(terminated.sum()),
            unique_envs_truncated=int(truncated.sum()), episode_end_events=int(events.sum()), reward_sum_per_env=reward_sum.cpu().tolist(),
            max_current_closure_m=closure_max, max_current_mimic_rad=mimic_max, old002_closure_prefix_hit_envs=int(old002.sum()),
            max_raw_action_abs=maxraw, max_applied_action_abs=maxapplied, skill=skill,
            first_eval_epoch=started, last_eval_epoch=time.time())
    finally:
        env.termination_manager.compute = original_terminal
        if cycles is not None:
            cycles.finish()
        if book is not None:
            book.finish(); book.uninstall(); task['_book'] = None


def evaluate(task, out, group, ns, binding, actual_cfg, migration):
    # Original loader prepends its source runtime paths; restore explicit eval helper priority.
    for name in ('helper_root', 'v8_helper_root', 'e1_helper_root'):
        sys.path.insert(0, str(Path(task[name]).resolve(strict=True)))
    torch = ns['torch']
    cache = checkpoint_cache(torch, task)
    task['_cache'] = cache
    bundle, tensor, np, wp = fresh_bundle(task, out, ns, migration, binding, actual_cfg, torch)
    env = bundle['env']; task['_env'] = env
    native = native_static_readback(ns, env, torch)
    actor, actor_receipt = frozen_actor(ns, cache, env, torch)
    bridge = importlib.import_module('e1_fresh_runtime_bridge')
    before = bridge.fresh_full_dr_audit(env, bundle['guard'], tensor)
    ready = dict(source_cache=cache.receipt(), fresh_fullDR_before=before,
        explicit_fresh_resets=1, precontrols=0, actual_V2_binding=binding, actual_cfg=actual_cfg['receipt'],
        actual_native_static=native, actor=actor_receipt, route_scope=bundle['route_scope'],
        actual_SCUT_binding=task['_SCUT_eval_binding'], candidate_SCUT_cache_binding=task['_candidate_SCUT_cache_binding'],
        source_saved20k_history_applied=False, original_entry=task.get('_entry_receipt'),
        reset_bank_overlay=task['_bank_loader'].rows, no_v1_pin_read_or_replayed_proof=True)
    need(int(env._sim_step_counter) == 0, 'No control before ready/start')
    start = wait_start(task, out, group, ready)
    if task['role'] in E1:
        from tensordict import TensorDict
        worker = importlib.import_module('e1_parallel_worker_safe')
        vec = bridge.A0NoResetDecisionVec(env, actor, cache.SHA, torch, TensorDict, tensor)
        bridge.HOLDER.update(actor=actor, vec=vec, cache=cache)
        original_step = vec.step
        def step(action):
            check_stop(task, group)
            result = original_step(action)
            task['_completed_controls'] = task.get('_completed_controls', 0) + 1
            return result
        vec.step = step
        result = worker._run_loop(task, out, bundle, cache, vec, vec.policy, vec, torch, np, wp, tensor)
        result['original_observer_kind'] = result.pop('kind')
        if task['role'] == 'SLOPE_INDEPENDENT50':
            result['full_grader'] = None
            result['predicate_gap'] = 'Original fullramp acceptance predicate and accepted cohort unavailable; no S135 borrowing'
    else:
        result = five_loop(task, out, group, bundle, cache, actor, torch, tensor)
    cache.check_actor(actor)
    after = bridge.fresh_full_dr_audit(env, bundle['guard'], tensor)
    scut_after = frozen_factory.observed_binding(task, env, actual_cfg, torch, 'AFTER_FINITE_EVAL')
    result.update(schema=SCHEMA, kind=KIND, execution=True, passed_execution=True,
        actual_SCUT_binding=task['_SCUT_eval_binding'], actual_SCUT_binding_after=scut_after,
        candidate_SCUT_cache_binding=task['_candidate_SCUT_cache_binding'],
        role=task['role'], group_id=task['group_id'], run_id=task['run_id'], GPU_UUID=task['GPU_UUID'],
        num_envs=80, seed=20260928, source_cache=cache.receipt(), actor=actor_receipt,
        fresh_fullDR_before=before, fresh_fullDR_after=after, source_saved20k_DR_history_applied=False,
        source20k_DR_sliced=False, whole_saved20k_resume=False, optimizer_updates=0, live_critic_optimizer_created=False,
        original_RSL_clip_actions=6., full_skill_graduation=None, single_finite_scope_not_graduation=True,
        E0_S50_missing_grader_not_fabricated=True, registry_writes=0, mother_replaced=False,
        group_start=start, actual_V2_binding=binding, actual_native_static=native,
        original_entry=task.get('_entry_receipt'), route_derivation=task.get('_route_derivation'),
        fresh_axis=task.get('_fresh_axis'), migration_cohort_closed=task['_migration_closed'],
        task_sha256=task['_task_sha256'], worker_pid=os.getpid(), parent_pid=os.getppid(),
        close_intent_required=True, actual_parent_wait_RC0=None,
        parent_actual_wait_final_intent_ERROR_and_GPU_settle_required=True)
    return result


def close_resources(task, out, ns, env, execution_error):
    failures = []
    if env is not None:
        try:
            put(out / 'PRE_CLOSE.json', dict(schema=SCHEMA, epoch=time.time(), role=task['role'],
                completed_controls=task.get('_completed_controls', 0), calling_original_env_close=True))
            env.close()
            put(out / 'ENV_CLOSE_RETURNED.json', dict(schema=SCHEMA, epoch=time.time(), original_env_close_returned=True))
        except BaseException:
            failures.append(fail(out, 'ENV_CLOSE_ERROR'))
    app = ns.get('app') if ns else None
    if app is not None:
        try:
            helper = importlib.import_module('app_close_semantics_v6')
            bound = helper._pin_original_app_close(app)
            need(bound['fast_shutdown'] is True, 'Original V6 fast_shutdown binding differs')
            if execution_error is None and not failures:
                raw = (out / 'V2_FROZEN_EVAL_FINAL.json').read_bytes()
                final = json.loads(raw)
                need(final['execution'] is True and not list(out.glob('*ERROR*.json')), 'Final/error evidence differs before App close')
                put(out / 'V2_FROZEN_EVAL_APP_CLOSE_INTENT.json', dict(schema=SCHEMA, epoch=time.time(),
                    role=task['role'], run_id=task['run_id'], worker_pid=os.getpid(), parent_pid=os.getppid(),
                    task_sha256=task['_task_sha256'], final_sha256=hashlib.sha256(raw).hexdigest(), final_bytes=len(raw),
                    original_bound_close=bound, env_close_returned=env is not None, original_app_close_arguments=[],
                    original_fast_shutdown_unchanged=True, expected_process_nonreturn=True, app_close_returned=None,
                    error_before_close=False, parent_actual_wait_RC0_final_intent_ERROR_checks_required=True,
                    publication='TEMP_FLUSH_FSYNC_ATOMIC_RENAME_DIRECTORY_FSYNC_BEFORE_ORIGINAL_APP_CLOSE'))
        except BaseException:
            failures.append(fail(out, 'APP_CLOSE_EVIDENCE_ERROR'))
        try:
            app.close()  # Original zero-argument binding; may terminate without returning.
        except BaseException:
            failures.append(fail(out, 'APP_CLOSE_ERROR'))
        else:
            put(out / 'APP_CLOSED.json', dict(schema=SCHEMA, epoch=time.time(),
                original_zero_argument_close_returned=True, parent_actual_wait_still_required=True))
    return failures


def failed_cache_receipt(task):
    if '_cache' not in task:
        return None
    try:
        return task['_cache'].receipt()
    except BaseException:
        return dict(integrity_passed=False, receipt_error=traceback.format_exc())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--group-root', type=Path)
    args = parser.parse_args()
    raw = args.task.read_bytes(); task = json.loads(raw)
    group = (args.group_root or Path(task['group_root'])).resolve(strict=True)
    out = Path(task.get('output_dir', args.task.parent)).resolve(strict=True)
    ns, env, error = {}, None, None
    task['_task_sha256'] = hashlib.sha256(raw).hexdigest()
    try:
        check_task(task, out, group)
        # Explicit E0 migration v3 factory only; never call its N20000 native initializer.
        migration_path = Path(task['migration_worker']).resolve(strict=True)
        need(migration_path.name == 'worker_e0_scut_v14_hour_v3.py',
             'Explicit reviewed E0 migration v3 factory required')
        need(str(migration_path) == frozen_factory.HOUR_ROOT + '/' + frozen_factory.WORKER and
             hashlib.sha256(migration_path.read_bytes()).hexdigest() == task['migration_worker_SHA'],
             'Unknown: exact real SCUT hour worker path/source SHA differs')
        migration = source_module(migration_path, '_mod4v2_eval_original_factory_helper')
        task['_hour_cpu_core_reader'] = migration.adam_core
        need(callable(getattr(migration, 'load_original', None)), 'Actual selected helper has no original factory')
        task['_migration_worker_source'] = dict(path=str(migration_path),
            SHA=hashlib.sha256(migration_path.read_bytes()).hexdigest(), not_native_proof=True)
        ns, binding, actual_cfg = frozen_factory.load_original(migration, task, out)
        final = evaluate(task, out, group, ns, binding, actual_cfg, migration)
        final['migration_worker_source'] = task['_migration_worker_source']
        put(out / 'V2_FROZEN_EVAL_FINAL.json', final)
    except BaseException:
        error = fail(out, 'V2_FROZEN_EVAL_EXECUTION_ERROR')
        ns = task.get('_namespace', ns)
        env = task.get('_env')
        if env is None:
            bridge = sys.modules.get('e1_fresh_runtime_bridge')
            env = bridge.HOLDER.get('env') if bridge is not None else None
        if not (out / 'V2_FROZEN_EVAL_FINAL.json').exists():
            put(out / 'V2_FROZEN_EVAL_FINAL.json', dict(schema=SCHEMA, kind=KIND, epoch=time.time(),
                role=task.get('role'), execution=False, passed_execution=False, error=error,
                completed_controls=task.get('_completed_controls', 0), full_skill_graduation=None,
                source_cache=failed_cache_receipt(task),
                task_sha256=task['_task_sha256'], actual_parent_wait_RC0=None,
                original_error_retained=True, no_automatic_retry=True))
    finally:
        ns = task.get('_namespace', ns)
        env = task.get('_env', env)
        if env is None:
            bridge = sys.modules.get('e1_fresh_runtime_bridge')
            env = bridge.HOLDER.get('env') if bridge is not None else None
        failures = close_resources(task, out, ns, env, error)
    return 1 if error is not None or failures else 0


if __name__ == '__main__':
    raise SystemExit(main())

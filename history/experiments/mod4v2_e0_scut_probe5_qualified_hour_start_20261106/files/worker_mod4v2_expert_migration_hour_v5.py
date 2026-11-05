"""Finite nine-family MOD4v1 -> HW300N60 migration, original PPO; source-only.

The owning parent supplies --task JSON and owns admission/accounting/child wait.
No old physical restore helper, source rewrite, actor slicing or new trainer is
used.  Native V2 scene + one fresh reset + one zero control precede the sole
checkpoint byte-read/hash/CPU decode.  Historical source state is preserved
under an explicit historical root, never passed off as the new V2 live state.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib
import importlib.abc
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import random
import sys
import time
import traceback
import types

ROLES = ('E0', 'E2', 'E3', 'H1_normal', 'W35', 'CURB_PROTECTED878',
         'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50')
SCHEMA = 'mod4v2.expert_migration.original_ppo.v1'
CORE_KEYS = ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict')
OLD_ASSET_CALLS = {'bind_before_task_import', 'verify_task_module', 'configure_new_task'}


def need(value, message):
    if not value:
        raise ValueError(message)


def put(path, value):
    """Publish only an own JSON, durably before original fast App.close."""
    path = Path(path)
    tmp = path.with_name(path.name + '.partial')
    need(not path.exists() and not tmp.exists(), 'Own exclusive output already exists: ' + str(path))
    raw = json.dumps(value, indent=2, allow_nan=False).encode('utf-8')
    with tmp.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)
    if os.name == 'posix':
        fd = os.open(str(path.parent), os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def error_record(out, phase):
    text = traceback.format_exc()
    name = 'WORKER_ERROR.json'
    if (out / name).exists():
        name = 'WORKER_ERROR_SECONDARY_' + str(time.time_ns()) + '.json'
    put(out / name, dict(schema=SCHEMA, epoch=time.time(), phase=phase, error=text,
                        automatic_unchanged_retry=False))
    return text


def cpu_tree(value, torch):
    if torch.is_tensor(value):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return type(value)((key, cpu_tree(item, torch)) for key, item in value.items())
    if isinstance(value, list):
        return [cpu_tree(item, torch) for item in value]
    if isinstance(value, tuple):
        return tuple(cpu_tree(item, torch) for item in value)
    return copy.deepcopy(value)


def exact(a, b, torch):
    if torch.is_tensor(a) or torch.is_tensor(b):
        return (torch.is_tensor(a) and torch.is_tensor(b) and a.shape == b.shape and
                a.dtype == b.dtype and torch.equal(a.detach().cpu(), b.detach().cpu()))
    if isinstance(a, dict) or isinstance(b, dict):
        return (isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys() and
                all(exact(a[key], b[key], torch) for key in a))
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        return (type(a) is type(b) and len(a) == len(b) and
                all(exact(x, y, torch) for x, y in zip(a, b)))
    if type(a).__module__.startswith('numpy') or type(b).__module__.startswith('numpy'):
        import numpy as np
        return type(a) is type(b) and bool(np.array_equal(a, b))
    return type(a) is type(b) and a == b


def owned_values(obj, torch):
    """Capture direct tensor/scalar/RNG fields without traversing env/SDK refs."""
    def take(value):
        if torch.is_tensor(value):
            return value.detach().cpu().clone()
        if isinstance(value, torch.Generator):
            return {'generator_device': str(value.device), 'state': value.get_state().cpu().clone()}
        if value is None or type(value) in (str, bool, int, float):
            return value
        if type(value).__name__ in ('CircularBuffer', 'DelayBuffer'):
            return {'original_class': type(value).__module__ + ':' + type(value).__name__,
                    'live_fields': {key: take(item) for key, item in vars(value).items()
                                    if key != '_device'}, 'device': str(getattr(value, '_device', ''))}
        if isinstance(value, (dict, list, tuple)):
            if isinstance(value, dict):
                return {key: take(item) for key, item in value.items()}
            return type(value)(take(item) for item in value)
        raise TypeError(type(value).__name__)
    result = {}
    for name, value in vars(obj).items():
        try:
            result[name] = take(value)
        except TypeError:
            pass  # SDK/env/manager objects are not serialized by generic traversal.
    return result


def source_io(cache):
    need(cache.physical_byte_opens == cache.decodes == 1, 'Selected source IO ceased to be once-only')
    return dict(cache.receipt(), physical_byte_opens=cache.physical_byte_opens,
                SHA_calculations=1, CPU_decodes=cache.decodes)


def adam_core(state, torch):
    opt = state['optimizer_state_dict']
    need(len(opt['state']) == 17, 'Complete original Adam17 required')
    steps = [int(row['step'].detach().cpu().item()) if torch.is_tensor(row['step'])
             else int(row['step']) for row in opt['state'].values()]
    lrs = [float(group['lr']) for group in opt['param_groups']]
    need(len(set(steps)) == 1 and lrs and len(set(lrs)) == 1 and
         math.isfinite(lrs[0]) and lrs[0] > 0, 'Adam17 steps/LR inconsistent')
    actor, critic = state['actor_state_dict'], state['critic_state_dict']
    need('distribution.std_param' in actor and actor['distribution.std_param'].numel() == 6,
         'Original learned STD6 required')
    need(len(actor) >= 9 and len(critic) >= 8, 'Full actor/critic/normalizer state required')
    return dict(iteration=int(state['iter']), Adam17_steps=steps,
                optimizer_LRs=lrs, source_Adam_step=steps[0], source_LR=lrs[0],
                STD6=actor['distribution.std_param'].detach().cpu().tolist(),
                actor_tensors=len(actor), critic_tensors=len(critic))


class EntryV2(ast.NodeTransformer):
    """Remove only V1 asset guards, not PPO/config/task/reward code."""
    def __init__(self):
        self.removed = []

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in OLD_ASSET_CALLS:
            self.removed.append(dict(line=node.lineno, original_call=node.func.id))
            return ast.copy_location(ast.Constant(None), node)
        return node


class ResetBankV2(ast.NodeTransformer):
    """Replace the old asset-only bank compatibility guard by a real V2 check."""
    def __init__(self):
        self.replaced = []

    def visit_If(self, node):
        self.generic_visit(node)
        # Original scut_flat_rescue only: actual contract != bank contract.
        if (isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name)
                and node.test.left.id == 'actual' and len(node.test.ops) == 1
                and isinstance(node.test.ops[0], ast.NotEq)
                and isinstance(node.test.comparators[0], ast.Subscript)
                and isinstance(node.test.comparators[0].value, ast.Name)
                and node.test.comparators[0].value.id == 'raw'):
            self.replaced.append(node.lineno)
            replacement = ast.parse(
                'env._mod4v2_reset_bank_compatibility = '
                '_migration_validate_v2_bank(source, raw, task)\n').body[0]
            return ast.copy_location(replacement, node)
        return node


def validate_v2_bank(source, raw, task_module):
    """No new pose/filter/RNG: validate exactly the source's selected flat library."""
    target = task_module.CONTRACT
    need(target.get('mechanical_limits_v2') is not None, 'V2 bank guard requires actual V2 contract')
    poses = [pose for pose in raw['poses'] if .24 <= pose['root_height_m'] <= .272]
    need(poses, 'Original reset height filter produced no poses')
    checked = 0
    for pose in poses:
        for name, q in pose['joint_pos'].items():
            need(name in target['joints'] and math.isfinite(float(q)), 'Unknown/nonfinite source bank joint: ' + name)
            bounds = target['joints'][name]['limits_si']
            if bounds is None:
                continue
            low, high = bounds
            need((low is None or float(q) >= low - 1e-6) and
                 (high is None or float(q) <= high + 1e-6),
                 'Original reset pose outside V2 mechanical limit: ' + name)
            checked += 1
    return dict(kind='MOD4V2_ORIGINAL_RESET_BANK_LIMIT_COMPATIBILITY', bank_path=str(source),
                source_contract_SHA=raw['contract_sha256'], target_model=target.get('model'),
                poses_total=len(raw['poses']), original_height_filtered_poses=len(poses),
                joint_values_checked=checked, pose_changes=0, new_filter_changes=0,
                added_RNG_draws=0, no_V1_compatibility_pass_claimed=True,
                closed_chain_geometry_inherited_native_gap_still_required=True)


def validate_v2_rough_bank(meta_path, *, selected_bank=None, selected_index=None):
    """Validate original nearest-.25 full pose against V2, never replace its q."""
    import numpy as np
    task_module = importlib.import_module('mod4_task')
    contract = task_module.CONTRACT
    need(contract.get('mechanical_limits_v2') is not None, 'Actual V2 rough-bank contract required')
    if selected_bank is None:
        meta_path = Path(meta_path)
        meta_raw = meta_path.read_bytes()
        meta = json.loads(meta_raw)
        need(meta['poses'] == 133 and meta['bodies'] == 31 and meta['tree_joints'] == 30,
             'Original full133/31body/30joint collision bank required')
        npz_path = meta_path.with_suffix('.npz')
        npz_raw = npz_path.read_bytes()
        with np.load(io.BytesIO(npz_raw)) as bank:
            pick = int(np.argmin(abs(bank['root_height'] - .25)))
            selected = validate_v2_rough_bank(meta_path, selected_bank=bank, selected_index=pick)
        selected.update(original_meta_SHA=hashlib.sha256(meta_raw).hexdigest(),
                        original_NPZ_SHA=hashlib.sha256(npz_raw).hexdigest())
        return selected
    bank, pick = selected_bank, int(selected_index)
    names = [str(name) for name in bank['joint_names']]
    need(pick == int(np.argmin(abs(bank['root_height'] - .25))) and len(names) == 30 and
         np.isfinite(bank['q'][pick]).all() and np.isfinite(bank['points_root'][pick]).all(),
         'Original rough selector/complete q/footprint differs')
    for name, value in zip(names, bank['q'][pick]):
        need(name in contract['joints'], 'Unknown original rough-bank joint: ' + name)
        bounds = contract['joints'][name]['limits_si']
        if bounds is None:
            continue
        low, high = bounds
        need((low is None or float(value) >= low - 1e-6) and
             (high is None or float(value) <= high + 1e-6),
             'Original rough pose outside V2 mechanical limit: ' + name)
    return dict(kind='MOD4V2_ORIGINAL_NEAREST250_ROUGH_BANK_LIMIT_CHECK', pose_index=pick,
                original_q_joint_order_footprint_unchanged=True, pose_edits=0, selector_edits=0,
                added_RNG_draws=0, old_asset_pass_not_relabelled=True,
                native_geometry_qualification_still_required=True)


class BankLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """One scoped import overlay; original source files remain byte-unchanged."""
    def __init__(self, original_mod):
        self.original_mod = original_mod
        self.rows = []

    def find_spec(self, fullname, path=None, target=None):
        if fullname in ('scut_flat_rescue', 'mod4v1_e1_collision_bank_compat', 'mod4v1_w35_asset_compat'):
            source = self.original_mod / (fullname + '.py')
            if source.is_file():
                return importlib.util.spec_from_file_location(fullname, source, loader=self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        source = Path(module.__spec__.origin)
        raw = source.read_text(encoding='utf-8-sig')
        tree = ast.parse(raw, filename=str(source))
        transform = ResetBankV2()
        if module.__name__ == 'scut_flat_rescue':
            tree = transform.visit(tree)
        ast.fix_missing_locations(tree)
        module._migration_validate_v2_bank = validate_v2_bank
        module.__file__ = str(source)
        exec(compile(tree, str(source), 'exec'), module.__dict__)
        replaced = []
        if module.__name__ == 'mod4v1_e1_collision_bank_compat':
            module.require_mod4v1_e1_collision_bank = lambda meta_path, asset_dir: validate_v2_rough_bank(meta_path)
            replaced.append('require_mod4v1_e1_collision_bank')
        elif module.__name__ == 'mod4v1_w35_asset_compat':
            def metadata(meta, meta_path, usd_path, contract_path):
                task_module = importlib.import_module('mod4_task')
                need(Path(usd_path).resolve() == Path(task_module.USD_PATH).resolve() and
                     Path(contract_path).resolve() == Path(task_module.USD_PATH).with_name('import_contract.json').resolve(),
                     'W35 V2 guard must receive actual V2 USD/contract')
                return validate_v2_rough_bank(meta_path)
            module.require_mod4v1_asset_and_original_bank_geometry = metadata
            # Keep verify_original_W35_selected_bank unchanged: it proves only
            # the original pose34 bytes/q/footprint; V2 limits are checked above.
            replaced.append('require_mod4v1_asset_and_original_bank_geometry')
        self.rows.append(dict(path=str(source), source_SHA=hashlib.sha256(raw.encode('utf-8')).hexdigest(),
                              V1_guard_lines_replaced=transform.replaced, V1_guard_functions_replaced=replaced,
                              V2_checks_are_not_V1_asset_pass_claims=True))


def original_environment(task, root):
    saved = task.get('original_env')
    if saved is None:
        path = Path(task['original_run_manifest'])
        if not path.is_absolute():
            path = root / path
        saved = json.loads(path.read_text(encoding='utf-8'))['env']
    need(isinstance(saved, dict) and saved, 'Complete original run environment required')
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK', 'WORLD_SIZE', 'LOCAL_RANK', 'LOCAL_WORLD_SIZE'):
            os.environ.pop(key, None)
    for key, value in saved.items():
        if key not in ('CUDA_VISIBLE_DEVICES', 'RANK', 'WORLD_SIZE', 'LOCAL_RANK', 'LOCAL_WORLD_SIZE'):
            os.environ[str(key)] = str(value)
    os.environ['RM_KEEP_STD'] = '1'
    # Original successful posttrain worker binds the physical queue to 50 Hz.
    os.environ['MOD4_RESUME_QUEUE_CONTROL_US'] = '20000'
    role = task['role']
    if role in ('E2', 'E3'):
        os.environ['RM_TERRAIN'] = 'flat'
        os.environ['OWN_E2_H1_KIND'] = 'E2_WORLD_MOVING_SIGNED4' if role == 'E2' else 'E3_PUBLIC_RECOVERY'
    # Storage output only; command/task/DR/clock environment remains original.
    for key in ('OWN_E0_OUTPUT', 'OWN_E2_OUTPUT', 'OWN_E3_OUTPUT', 'OWN_W35_OUTPUT', 'OWN_H1_OUTPUT'):
        if key in os.environ:
            os.environ[key] = str(Path(task['_out']))


def load_original(task, out):
    root = Path(task['original_runtime_root']).resolve(strict=True)
    entry = Path(task['original_entry'])
    if not entry.is_absolute():
        entry = root / entry
    entry = entry.resolve(strict=True)
    original_environment(task, root)
    job = root / 'job0' if task['role'] == 'H1_normal' else root
    # Legacy launchers require storage == launcher job / kit_isolation.  Bind
    # this NEW task's private output, never an immutable source or older run.
    launcher_job = out.resolve(strict=True)
    storage = launcher_job / 'kit_isolation'
    storage.mkdir(exist_ok=False)
    (storage / 'data').mkdir()
    (storage / 'DerivedDataCache').mkdir()
    with (storage / 'data/user.config.json').open('x', encoding='utf-8') as stream:
        stream.write('{}')
    warp_cache = launcher_job / 'warp_cache'
    warp_cache.mkdir(exist_ok=False)
    os.environ.update(WP_CACHE_DIR=str(warp_cache), PYTHONDONTWRITEBYTECODE='1')
    role = task['role']
    if role in ('E0', 'E2', 'E3'):
        launcher_env = {f'MOD4V1_{role}_JOB_ROOT': str(launcher_job),
                        f'MOD4V1_{role}_KIT_STORAGE_ROOT': str(storage)}
    elif role == 'W35':
        launcher_env = {'MOD4_NEW208_JOB_ROOT': str(launcher_job),
                        'MOD4_W35_OWN_KIT_STORAGE_ROOT': str(storage)}
    elif role == 'H1_normal':
        launcher_env = {'MOD4_EXPERT213_KIT_STORAGE_ROOT': str(storage)}
    else:
        launcher_env = {'MOD4V1_E1_ACTUAL_JOB_ROOT': str(launcher_job),
                        'MOD4V1_E1_KIT_STORAGE_ROOT': str(storage)}
    os.environ.update(launcher_env)
    for path in (root, job, job / 'runtime', job / 'runtime/isaac/mod4', root / 'lib', out):
        sys.path.insert(0, str(path))
    package = Path(task['v2_package']).resolve(strict=True)
    sys.path.insert(0, str(package))
    adapter = importlib.import_module('runtime_adapter_v2')
    need(Path(adapter.__file__).resolve() == package / 'runtime_adapter_v2.py', 'Actual V2 adapter source differs')
    binding = adapter.prepare_environment(opt_in=True)  # Before any task import.
    binding['asset_sha256'] = hashlib.sha256(Path(binding['asset']).read_bytes()).hexdigest()
    # Legacy names are path aliases only, never old asset-admission receipts.
    asset_key = f'MOD4V1_{role}_ASSET_DIR' if role in ('E0', 'E2', 'E3') else 'MOD4V1_ASSET_DIR'
    os.environ[asset_key] = str(Path(binding['asset']).resolve(strict=True).parent)
    bank_loader = BankLoader(entry.parent)
    sys.meta_path.insert(0, bank_loader)
    raw = entry.read_text(encoding='utf-8-sig')
    transform = EntryV2()
    tree = transform.visit(ast.parse(raw, filename=str(entry)))
    ast.fix_missing_locations(tree)
    ns = dict(__name__='_mod4v2_original_training_entry', __file__=str(entry))
    argv = sys.argv
    sys.argv = [str(entry), '--headless', '--num_envs', '20000', '--seed', str(task['seed']),
                '--steps_per_env', '24', '--additional_iterations', str(task['max_additional_updates']),
                '--save_interval', '1000000000', '--run_name', task['run_id'], '--log_root', str(out)]
    # Keep the partial namespace visible so App can still close on an import error.
    task['_namespace'] = ns
    try:
        exec(compile(tree, str(entry), 'exec'), ns)
    finally:
        sys.argv = argv
    if task['role'] == 'H1_normal':
        reward = importlib.import_module('h1_scut_fudan_jump_reward_v1')
        terrain = importlib.import_module('h1_step270_sdk_runtime_candidate')
        original_configure = reward.configure
        reward.configure = lambda cfg: terrain.configure_rewards(cfg, original_configure)
        ns['build_env'].__globals__['Mod4Env'] = terrain.H1Step270Env
    constructor = ns['build_env'].__globals__['Mod4Env']
    actual_cfg = {}
    def construct(*args, **kwargs):
        need(not args and 'cfg' in kwargs, 'Original environment constructor signature differs')
        cfg = kwargs['cfg']
        # SDK versions call the same PhysxCfg `physics` or `physx`.  Share the
        # existing object; do not substitute solver/clock configuration.
        if not hasattr(cfg.sim, 'physx') and getattr(cfg.sim, 'physics', None) is not None:
            cfg.sim.physx = cfg.sim.physics
        actual_cfg['receipt'] = adapter.apply_runtime_cfg(cfg, ns['mod4_task'], prebuild=True)
        actual_cfg['cfg'] = cfg
        return constructor(**kwargs)
    ns['build_env'].__globals__['Mod4Env'] = construct
    task['_entry_receipt'] = dict(path=str(entry), source_SHA=hashlib.sha256(raw.encode('utf-8')).hexdigest(),
        V1_asset_only_calls_removed=transform.removed, original_PPO_functions_unmodified=True,
        launcher_path_binding=dict(job=str(launcher_job), private_kit_storage=str(storage),
            environment=launcher_env, warp_cache=str(warp_cache), actual_V2_asset_alias={asset_key: os.environ[asset_key]},
            original_source_root_unchanged=True, V1_asset_pass_claimed=False))
    task['_bank_loader'] = bank_loader
    return ns, binding, actual_cfg


def native_initialized(task, ns, actual_cfg, binding, torch):
    env = ns['build_env']()
    task['_env'] = env
    need(env.num_envs == 20000 and abs(float(env.physics_dt) - .0025) < 1e-12 and
         abs(float(env.step_dt) - .02) < 1e-12 and env.cfg.decimation == 8,
         'V2 original N20000/400Hz physics/50Hz control required')
    need(sum(env.observation_manager.group_obs_dim['policy']) == 35 and
         sum(env.observation_manager.group_obs_dim['critic']) == 38 and env.action_manager.total_action_dim == 6,
         'Original 35/38/6 interface differs')
    # Exactly one explicit new physical reset, never load old env/DR/RNG/history.
    task['_fresh_reset_result'] = env.reset()
    if task['role'] == 'E3':
        env.e3_reset_enabled = True
        env.place_declared_fall(torch.arange(env.num_envs, device=env.device))
        env.publish()
    if task['role'] in ('CURB_INDEPENDENT113', 'SLOPE_INDEPENDENT50'):
        axis = importlib.import_module('independent_expert_axis_v1')
        axis.bind_after_restore(env, 'CURB20' if task['role'] == 'CURB_INDEPENDENT113' else 'SLOPE5')
    required = ('_mild_dr', '_sensor_mild', '_feedback_delay_mild', '_spring_pressure',
                '_gas_damping', '_chassis_com', '_explicit_pd')
    need(all(hasattr(env, name) for name in required), 'Full original D0-D7 components missing')
    robot = env.scene['robot']
    names = list(robot.joint_names)
    limits = robot.root_view.get_dof_limits()
    if not torch.is_tensor(limits):
        import warp as wp
        limits = wp.to_torch(limits)
    contract = ns['mod4_task'].CONTRACT
    # Publish the ONE existing native getter result before ANY native-limit
    # assertion.  Diagnostics never step physics, draw RNG, compute obs or load PT.
    def native_number(value):
        value = float(value)
        if math.isfinite(value):
            return value
        return '+inf' if value > 0 else '-inf' if value < 0 else 'nan'
    native_shape = tuple(limits.shape)
    shape_readable = len(native_shape) == 3 and native_shape[1:] == (len(names), 2)
    target_bounds = (contract.get('mechanical_limits_v2') or {}).get('per_side_joint_bounds_SI', {})
    readback_rows = []
    for side in ('left', 'right'):
        for key, hardware_expected in target_bounds.items():
            name = side + '_' + key
            expected = contract['joints'].get(name, {}).get('limits_si') or hardware_expected
            row = dict(name=name, joint_type=contract['joints'].get(name, {}).get('type'),
                hardware_expected_SI=[('-inf' if i == 0 else '+inf') if x is None else x for i,x in enumerate(hardware_expected)],
                native_implementation_endpoint_not_hardware_stop=True,
                native_API_unit='m' if key == 'gas_slide' else 'rad',
                expected_contract_unit='m' if key == 'gas_slide' else 'rad',
                expected_SI=[('-inf' if index == 0 else '+inf') if value is None else value
                             for index, value in enumerate(expected)])
            if not shape_readable or name not in names:
                row['readback_error'] = 'Native tensor shape or named DOF absent'
            else:
                row['dof_index'] = names.index(name)
                row['endpoints'] = []
                for index, wanted in enumerate(expected):
                    column = limits[:, names.index(name), index]
                    finite = torch.isfinite(column)
                    finite_values = column[finite]
                    row['endpoints'].append(dict(endpoint='lower' if index == 0 else 'upper',
                        endpoint_index=index, expected_SI=row['expected_SI'][index],
                        raw_contract_endpoint=wanted,
                        first_four_native=[native_number(value) for value in column[:4].detach().cpu().tolist()],
                        native_min=native_number(column.min().item()), native_max=native_number(column.max().item()),
                        finite_min=native_number(finite_values.min().item()) if finite_values.numel() else None,
                        finite_max=native_number(finite_values.max().item()) if finite_values.numel() else None,
                        classification=dict(finite=int(finite.sum().item()),
                            positive_infinity=int((torch.isinf(column) & (column > 0)).sum().item()),
                            negative_infinity=int((torch.isinf(column) & (column < 0)).sum().item()),
                            nan=int(torch.isnan(column).sum().item()))))
            readback_rows.append(row)
    put(Path(task['_out']) / 'V2_NATIVE_LIMIT_READBACK.json', dict(
        schema='mod4v2.native_limit_readback.v1', epoch=time.time(), role=task['role'], run_id=task['run_id'],
        worker_pid=os.getpid(), parent_pid=os.getppid(), source_weights_opens=0, source_decodes=0,
        getter='robot.root_view.get_dof_limits', native_tensor_shape=native_shape,
        native_view_type=type(robot.root_view).__module__ + '.' + type(robot.root_view).__qualname__,
        native_getter_doc=str(getattr(robot.root_view.get_dof_limits, '__doc__', '') or '')[:6000],
        units_basis='Native PhysX get_dof_limits SI interface: angular rad / linear m; raw return, no conversion',
        USD_authored_angular_unit_is_distinct='degree', native_values_are_unconverted=True,
        signed_infinity_is_text=True, native_unbounded_finite_sentinel_is_not_literal_infinity=True,
        unchanged_native_open_end_abs_SI_threshold=1e6, unchanged_finite_absolute_tolerance_SI=1e-6,
        target_joint_count=len(readback_rows), rows=readback_rows, binding=binding,
        extra_physics_steps=0, extra_RNG_draws=0, extra_observation_computes=0,
        diagnostic_only_not_native_initialization_pass=True))
    need(contract.get('mechanical_limits_v2') is not None and tuple(limits.shape[-2:]) == (len(names), 2),
         'Native V2 contract/DOF limits required')
    rows = []
    for name, spec in contract['joints'].items():
        if spec.get('limits_si') is None or name not in names:
            continue
        value = limits[:, names.index(name)]
        for endpoint, wanted in enumerate(spec['limits_si']):
            column = value[:, endpoint]
            sign = -1 if endpoint == 0 else 1
            if wanted is None:
                good = ((torch.isinf(column) & (column * sign > 0)) |
                        (torch.isfinite(column) & (column * sign >= 1e6)))
            else:
                good = torch.isfinite(column) & ((column - wanted).abs() <= 1e-6)
            if not bool(good.all()):
                wanted_text = ('-inf' if endpoint == 0 else '+inf') if wanted is None else repr(wanted)
                observed = [native_number(value) for value in column[:4].detach().cpu().tolist()]
                need(False, f'Actual V2 native mechanical limit differs: name={name} '
                     f'endpoint={endpoint} ({"lower" if endpoint == 0 else "upper"}) wanted_SI={wanted_text} '
                     f'observed_first4_native={observed} '
                     f'observed_native_min={native_number(column.min().item())} '
                     f'observed_native_max={native_number(column.max().item())}')
        rows.append(dict(name=name, first_env_native_limits=value[0].cpu().tolist(), expected=spec['limits_si']))
    package = Path(task['v2_package'])
    params = json.loads((package / 'model_parameters.json').read_text(encoding='utf-8'))
    need(params['gas_spring']['stiffness_n_m'] == 2000. and params['gas_spring']['damping_n_s_m'] == 3.,
         'Original D5/D6 nominal implementation incompatible with target')
    gas_ids = [names.index(side + '_gas_slide') for side in ('left', 'right')]
    gas = {}
    first_physics = int(env._sim_step_counter)
    first_feedback = int(env._feedback_100hz_tick)
    # Sole pretraining validation control.  It is NOT PPO experience and does
    # not call observation_manager.compute separately or cause a second reset.
    env.step(torch.zeros((20000, 6), device=env.device))
    physics_delta = int(env._sim_step_counter) - first_physics
    feedback_delta = int(env._feedback_100hz_tick) - first_feedback
    need(physics_delta == 8 and feedback_delta == 2, 'Actual 50Hz control/100Hz feedback cadence differs')
    # Original mode='step' gas_spring_preload writes the contract target during
    # this SAME validation control.  Do not assert its target before that event.
    for label, getter, expected in (
        ('stiffness', 'get_dof_stiffnesses', env._spring_pressure.component.actual_stiffness(env._spring_pressure.nominal)),
        ('damping', 'get_dof_dampings', env._gas_damping.component.actual_damping_Ns_per_m()),
        ('position_target', 'get_dof_position_targets', torch.tensor(
            [params['gas_spring']['target_position_m'][side] for side in ('left', 'right')], device=env.device).expand(env.num_envs, 2))):
        value = getattr(robot.root_view, getter)()
        if not torch.is_tensor(value):
            import warp as wp
            value = wp.to_torch(value)
        value = value.to(env.device)[:, gas_ids]
        need(value.shape == expected.shape and bool(torch.isfinite(value).all()) and
             bool(((value - expected).abs() <= 1e-5).all()), 'Actual V2 gas readback differs: ' + getter)
        gas[label] = dict(native_getter=getter, first_env=value[0].cpu().tolist(), all_N20000_verified=True)
    need(bool(torch.isfinite(robot.data.joint_pos).all()), 'Fresh V2 native joint state nonfinite')
    poses = robot.root_view.get_link_transforms()
    if not torch.is_tensor(poses):
        import warp as wp
        poses = wp.to_torch(poses)
    poses = poses.to(env.device)
    body_names = list(robot.body_names)
    need(poses.shape == (20000, len(body_names), 7), 'Actual native link transform shape differs')
    def anchor(body, local):
        pose = poses[:, body_names.index(body)]
        # Native PhysX transforms are xyzw, not the public helper's convention.
        q = pose[:, 3:7]
        v = torch.as_tensor(local, dtype=pose.dtype, device=env.device).expand(20000, 3)
        uv = 2 * torch.cross(q[:, :3], v, dim=-1)
        return pose[:, :3] + v + q[:, 3:4] * uv + torch.cross(q[:, :3], uv, dim=-1)
    closure_gaps = {}
    for name, spec in contract['closures'].items():
        gap = (anchor(spec['body0'], spec['anchor0_m']) - anchor(spec['body1'], spec['anchor1_m'])).norm(dim=-1)
        need(bool(torch.isfinite(gap).all()) and float(gap.max()) <= .01,
             'Fresh V2 original closure gap exceeds .01: ' + name)
        closure_gaps[name] = dict(maximum_m=float(gap.max()), all_N20000_verified=True)
    transmission = {}
    need(list(robot.root_view.shared_metatype.link_names)==body_names,'Actual native body order differs')
    for side in ('left','right'):
        for follower,reference in (('drive_hip','thigh'),('drive_input','input')):
            an,bn=side+'_'+follower,side+'_'+reference
            qa=poses[:,body_names.index(an),3:7];qb=poses[:,body_names.index(bn),3:7]
            na=torch.tensor(contract['bodies'][an]['neutral_quat_wxyz'],device=env.device,dtype=qa.dtype)
            nb=torch.tensor(contract['bodies'][bn]['neutral_quat_wxyz'],device=env.device,dtype=qa.dtype)
            neutral=2*torch.acos((na*nb).sum().abs().clamp(max=1.))
            error=(2*torch.acos((qa*qb).sum(-1).abs().clamp(max=1.))-neutral).abs()
            need(bool(torch.isfinite(error).all()) and float(error.max())<=.01,'Actual N20000 native continuous transmission health differs: '+an)
            transmission[an]=dict(native_original_scalar_error_max_rad=float(error.max()),all_N20000_verified=True,original_threshold_rad=.01)
    receipt = dict(schema=SCHEMA, epoch=time.time(), role=task['role'], pid=os.getpid(),
        owner_pid=os.getppid(), run_id=task['run_id'], num_envs=20000, source_weights_opens=0,
        source_decodes=0, explicit_new_environment_resets=1, old_physical_state_restores=0,
        pretraining_validation_controls=1, pretraining_validation_physics_steps=physics_delta,
        pretraining_validation_feedback_ticks=feedback_delta, PPO_rollout_controls=0,
        fresh_DR_history_queues=True, old_Native0PT_proof_replayed=False,
        binding=binding, cfg=actual_cfg['receipt'], mechanical_limits=rows, gas=gas, closure_gaps=closure_gaps, continuous_transmission_native=transmission,
        source_env_state_applied=False, cross_D0_task_state_fresh_no_environment_exactresume=True,
        original_entry=task['_entry_receipt'], reset_bank_overlay=task['_bank_loader'].rows)
    # JSON signed infinity is represented explicitly, not silently made finite.
    def finite_json(value):
        if type(value) is float and not math.isfinite(value):
            return '+inf' if value > 0 else '-inf' if value < 0 else 'nan'
        if isinstance(value, dict):
            return {k: finite_json(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [finite_json(v) for v in value]
        return value
    receipt = finite_json(receipt)
    put(Path(task['_out']) / 'V2_NATIVE_INITIALIZED.json', receipt)
    return env, receipt


def live_physical(env, role, torch):
    """Original state serializers only; no resume/load/reset/audit/noisy compute."""
    sensor = importlib.import_module('sensor_a0_runtime').state(env)
    delay = importlib.import_module('feedback_delay_runtime').delay_state(env)
    actions = {name: env.action_manager.get_term(name) for name in env.action_manager.active_terms}
    need(hasattr(env, '_physics_action_delay'), 'Original physical action queue missing')
    output = dict(sensor_DR_state=sensor.state_dict(), sensor_recipe=sensor.receipt(),
        feedback_delay_state=delay.state_dict(), feedback_delay_recipe=env.feedback_delay_recipe(),
        physical_action_delay_state=env._physics_action_delay.state_dict(),
        physical_action_delay_recipe=env.action_delay_recipe(),
        spring_pressure_state=env._spring_pressure.state_dict(), spring_pressure_recipe=env.spring_pressure_recipe(),
        gas_damping_state=env._gas_damping.state_dict(), gas_damping_recipe=env.gas_damping_recipe(),
        chassis_PD_state=importlib.import_module('chassis_pd_checkpoint').current_state(env),
        chassis_PD_recipe=env.chassis_pd_recipe(),
        sensor_global_rng_state=dict(cpu=torch.random.get_rng_state(), cuda=torch.cuda.get_rng_state_all()),
        sensor_command_DR_rng_state={k: v.get_state() for k, v in vars(env.command_manager.get_term('twist')).items()
                                     if isinstance(v, torch.Generator)},
        sensor_physical_DR_rng_state={k: v.get_state() for k, v in vars(env._mild_dr).items()
                                     if isinstance(v, torch.Generator)},
        mod4v2_live_D0=owned_values(env._mild_dr, torch),
        mod4v2_live_command=owned_values(env.command_manager.get_term('twist'), torch),
        mod4v2_live_observation_history=owned_values(env.observation_manager, torch),
        mod4v2_live_action={name: owned_values(action, torch) for name, action in actions.items()},
        mod4v2_live_robot_state=dict(root_state_w=env.scene['robot'].data.root_state_w,
            joint_pos=env.scene['robot'].data.joint_pos, joint_vel=env.scene['robot'].data.joint_vel),
        mod4v2_live_environment=owned_values(env, torch),
        mod4v2_python_rng_state=random.getstate())
    import numpy as np
    output['mod4v2_numpy_rng_state'] = np.random.get_state()
    if role == 'E2':
        output['E2_moving4_command_state'] = importlib.import_module('e2_command_checkpoint_v1').current(env.command_manager.get_term('twist'))
    elif role == 'E3':
        helper = importlib.import_module('e3_fullstate_checkpoint_v1')
        output.update(E3_public_recovery_state=helper.state(env), E3_reset_contract=env.e3_reset_receipt)
    elif role == 'H1_normal':
        helper = importlib.import_module('h1_step270_fullstate_checkpoint_candidate_uninstalled')
        output.update(H1_step270_task_state=helper.state(env), H1_step270_runtime_contract=dict(
            version=270, geometry=env.h1_phase.state_dict()['geometry'], actual_step_event_credit=True,
            new_V2_D0=True, prior_phase_CPU_history_only=True))
    elif role == 'W35':
        helper = importlib.import_module('checkpoint_cache208_v3')
        output['mod4v2_live_original_terrain_task_state'] = helper.current_state(env)
    elif role in ('CURB_PROTECTED878', 'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50'):
        module = ('curb20_entry_full_checkpoint' if role in ('CURB_PROTECTED878', 'CURB_INDEPENDENT113')
                  else 'slope5_full_checkpoint')
        helper = importlib.import_module(module)
        output['E1_terrain_state'] = helper.current_state(env)
        term = env.command_manager.get_term('twist')
        output['E1_retained_flat_command_state'] = term.state_dict_retention()
        if hasattr(env, '_independent_expert_axis_cache'):
            output['independent_expert_scope_state'] = env._independent_expert_axis_cache
        # Prior distributed-rank contract is historical, not live NCCL state.
        output['mod4v2_single_scene_contract'] = dict(num_envs=20000, world_size=1, rank=0,
                                                     historical_rank_state_not_restored=True)
    return cpu_tree(output, torch)


class SavedStop(Exception):
    pass


class Window:
    def __init__(self, task):
        self.task = task
        self.updates = self.optimizer_steps = self.rollout_controls = 0
        self.in_update = False
        self.last_saved_update = -1
        self.fullsave = None
        self.stop_reason = None
        self.ppo_started_epoch = None
        self.completed_save_wall_seconds = 0.0
        self.ppo_update_call_wall_seconds = 0.0
        self.rollout_step_call_wall_seconds = 0.0

    def boundary_reason(self):
        need(os.getppid() == self.task['owner_pid'], 'Original owner PID changed')
        if Path(self.task['stop_file']).exists():
            return 'STOP_SAVE'
        if time.time() >= self.task['save_deadline']:
            return 'save_deadline'
        return None


def run_training(task, ns, env, native, torch):
    out = Path(task['_out'])
    # Reuse the original full-source CPU cache, not a selected tensor loader.
    cache_module = importlib.import_module('source_cache208_v3')
    cache = cache_module.PinnedSource208(torch, task['source_path'], task['source_SHA'], task['source_bytes'])
    source = cache.state
    need(isinstance(source, dict) and all(k in source for k in CORE_KEYS), 'Complete selected source root required')
    source_core = adam_core(source, torch)
    need(source_core['iteration'] == task['source_iteration'], 'Selected actual source iteration differs')
    for key in ('source_Adam_step', 'source_LR'):
        if key in task:
            need(source_core[key] == task[key], 'Official metadata versus actual CPU source differs: ' + key)
    # The original constructor receives the actual selected Adam LR, not a new LR.
    ns['args'].learning_rate = source_core['source_LR']
    cfg_object = ns['runner_config']()
    cfg_object = ns['handle_deprecated_rsl_rl_cfg'](cfg_object, ns['metadata'].version('rsl-rl-lib'))
    cfg = cfg_object.to_dict()
    if task['role'] == 'H1_normal':
        cfg['algorithm']['class_name'] = 'owned_h1_public4_mean_overflow_ppo_v2:PPO'
    need(cfg['num_steps_per_env'] == 24 and cfg['algorithm']['num_learning_epochs'] == 5 and
         cfg['algorithm']['num_mini_batches'] == 4, 'Original 24 x 5 x 4 PPO required')
    original_reset = env.reset
    wrapper_reset_calls = [0]
    def already_fresh(*args, **kwargs):
        wrapper_reset_calls[0] += 1
        need(wrapper_reset_calls[0] == 1 and not args and not kwargs,
             'Unexpected redundant vector-wrapper reset arguments/count')
        return task['_fresh_reset_result']
    env.reset = already_fresh
    try:
        vec = ns['RslRlVecEnvWrapper'](env, clip_actions=cfg.get('clip_actions'))
    finally:
        env.reset = original_reset
    runner = ns['OnPolicyRunner'](vec, cfg, log_dir=str(out), device=cfg_object.device)
    task['_runner'] = runner
    window = Window(task)
    task['_window'] = window
    with cache_module.selected_source(cache):
        with cache_module.runner_source_load_scope():
            runner.load(str(cache.path), load_cfg=None, strict=True, map_location='cpu')
        runner.alg.learning_rate = source_core['source_LR']
        loaded = dict(runner.alg.save(), iter=int(runner.current_learning_iteration))
        need(all(exact(loaded[key], source[key], torch) for key in CORE_KEYS) and
             int(runner.current_learning_iteration) == source_core['iteration'],
             'Original full learner/normalizer/Adam load is not exact')
        need(cache.physical_byte_opens == cache.decodes == 1, 'Source IO must be once read / once CPU decode')
        put(out / 'V2_LEARNER_LOADED.json', dict(schema=SCHEMA, epoch=time.time(), source_IO=source_io(cache),
            source_core=source_core, full_actor_critic_learned_STD_Adam_normalizer_exact=True,
            vector_wrapper_redundant_physical_resets_suppressed=wrapper_reset_calls[0],
            physical_restore_calls=0, fresh_V2_D0_retained=True))

        def save(path, *args, **kwargs):
            save_wall_started = time.time()
            path = Path(path).resolve()
            need(path.is_relative_to(out.resolve()) and not cache.owns(path) and not window.in_update,
                 'Own complete-boundary candidate path required')
            need(window.optimizer_steps == 20 * window.updates and window.rollout_controls == 24 * window.updates,
                 'Actual PPO/Adam/control counts differ at save boundary')
            live = dict(runner.alg.save(), iter=int(runner.current_learning_iteration))
            core = adam_core(live, torch)
            need(all(step == old + window.optimizer_steps for step, old in
                     zip(core['Adam17_steps'], source_core['Adam17_steps'])), 'Actual Adam17 delta differs')
            physical = live_physical(env, task['role'], torch)
            candidate = cpu_tree(live, torch)
            candidate.update(physical)
            candidate['mod4v2_migration'] = dict(schema=SCHEMA, role=task['role'], run_id=task['run_id'],
                source_path=str(cache.path), source_SHA=cache.SHA, source_core=source_core,
                actual_new_updates=window.updates, actual_optimizer_steps=window.optimizer_steps,
                actual_rollout_controls=window.rollout_controls, pretraining_validation_controls=1,
                iteration_published_by_original_runner=True, iteration_label_rewritten=False,
                old_physical_state_restored=False, fresh_D0_DR_history_queues=True,
                source_env_state_applied=False, cross_D0_task_state_fresh_no_environment_exactresume=True,
                source_unknowns_are_CPU_history_not_live_state=True, native=native)
            # Entire unknown source tree survives exactly on CPU.  Old physical
            # roots are only historical; current known/live roots above win.
            candidate['mod4v2_migration'].update(window_mode='ORIGINAL_FINITE_WALL_CLOCK_HOUR', requested_effective_update_quota=None, ppo_started_epoch=window.ppo_started_epoch, completed_save_wall_seconds=window.completed_save_wall_seconds)
            candidate['mod4v2_historical_source_checkpoint'] = source
            candidate['mod4v2_source_unknown_CPU_fields'] = {
                key: value for key, value in source.items() if key not in candidate and key not in CORE_KEYS}
            temporary = path.with_name(path.name + '.partial')
            need(not temporary.exists() and not path.exists(), 'Own candidate already exists')
            with temporary.open('xb') as stream:
                torch.save(candidate, stream)
                stream.flush()
                os.fsync(stream.fileno())
            raw = temporary.read_bytes()
            decoded = torch.load(io.BytesIO(raw), map_location='cpu', weights_only=False)
            need(exact(decoded, candidate, torch), 'Actual own complete checkpoint roundtrip differs')
            need(all(exact(decoded[key], runner.alg.save()[key], torch) for key in CORE_KEYS),
                 'Saved original full learner differs from live')
            os.replace(temporary, path)
            if os.name == 'posix':
                fd = os.open(str(path.parent), os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            window.last_saved_update = window.updates
            window.completed_save_wall_seconds += time.time() - save_wall_started
            window.fullsave = dict(schema=SCHEMA, epoch=time.time(), checkpoint=str(path),
                SHA=hashlib.sha256(raw).hexdigest(), bytes=len(raw), source_IO=source_io(cache),
                actual_new_updates=window.updates, actual_optimizer_steps=window.optimizer_steps,
                actual_rollout_controls=window.rollout_controls, source_core=source_core, live_core=core,
                complete_original_learner=True, live_V2_D0_D7_task_rng_history_queues=True,
                unknown_and_historical_source_CPU_tree_exact=True, source_unchanged=True,
                atomic_published=True, physical_restore_calls=0, skill_graduation=False,
                latest_complete_save=dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
            name = ('V2_COMPLETE_SAVE.json' if not (out / 'V2_COMPLETE_SAVE.json').exists()
                    else 'V2_COMPLETE_SAVE_U%03d.json' % window.updates)
            put(out / name, window.fullsave)
            return None

        runner.save = save
        original_update = runner.alg.update
        original_step = runner.alg.optimizer.step
        original_log = runner.logger.log
        original_vec_step = vec.step

        def opt_step(*args, **kwargs):
            need(window.in_update, 'Adam step outside original PPO update')
            result = original_step(*args, **kwargs)
            window.optimizer_steps += 1
            return result

        def update(*args, **kwargs):
            need(not window.in_update, 'Recursive original update')
            update_wall_started = time.time()
            window.in_update = True
            try:
                result = original_update(*args, **kwargs)
            finally:
                window.in_update = False
                window.ppo_update_call_wall_seconds += time.time() - update_wall_started
            need(window.optimizer_steps == 20 * (window.updates + 1), 'Original 5 x 4 Adam update changed')
            window.updates += 1
            return result

        def vec_step(*args, **kwargs):
            need(not window.in_update, 'Environment step within optimizer update')
            rollout_wall_started = time.time()
            result = original_vec_step(*args, **kwargs)
            window.rollout_step_call_wall_seconds += time.time() - rollout_wall_started
            window.rollout_controls += 1
            return result

        def log(*args, **kwargs):
            result = original_log(*args, **kwargs)
            reason = window.boundary_reason()
            # Progress is metadata only, not an additional update, observation or checkpoint read.
            put(out / ('V2_TRAINING_PROGRESS_U%06d.json' % window.updates), dict(
                epoch=time.time(), actual_new_updates=window.updates, actual_optimizer_steps=window.optimizer_steps,
                actual_rollout_controls=window.rollout_controls, optimized_transitions=20000*window.rollout_controls,
                ppo_started_epoch=window.ppo_started_epoch, rollout_step_call_wall_seconds=window.rollout_step_call_wall_seconds,
                PPO_update_call_wall_seconds=window.ppo_update_call_wall_seconds,
                own_complete_save_wall_seconds=window.completed_save_wall_seconds,
                observed_loop_wall_seconds_excluding_complete_save=time.time()-window.ppo_started_epoch-window.completed_save_wall_seconds,
                no_skill_claim=True, parent_save_deadline=task['save_deadline']))
            if reason:
                window.stop_reason = reason
            if reason or (window.updates % 20 == 0 and window.last_saved_update != window.updates):
                runner.save(str(out / ('model_mod4v2_migration_complete_U%03d.pt' % window.updates)))
            if reason:
                raise SavedStop(reason)
            return result

        runner.alg.optimizer.step = opt_step
        runner.alg.update = update
        runner.logger.log = log
        vec.step = vec_step
        window.ppo_started_epoch = time.time()
        put(out / 'V2_PPO_LOOP_STARTED.json',dict(epoch=window.ppo_started_epoch,run_id=task['run_id'],role='E0',original_GO_epoch=task['save_deadline']-3600,native_and_load_startup_seconds=window.ppo_started_epoch-(task['save_deadline']-3600),requested_update_quota=None,original_save_deadline=task['save_deadline']))
        # Original RSL iteration labels remain unmodified; wall-clock bounds govern this window.
        # There is deliberately no iteration += 1 or save-label arithmetic.
        if window.boundary_reason():
            window.stop_reason = window.boundary_reason()
            runner.save(str(out / 'model_mod4v2_migration_complete_U000.pt'))
        else:
            try:
                runner.learn(num_learning_iterations=task['max_additional_updates'], init_at_random_ep_len=True)
            except SavedStop:
                pass
            if window.last_saved_update != window.updates:
                runner.save(str(out / ('model_mod4v2_migration_complete_U%03d.pt' % window.updates)))
        need(window.fullsave is not None, 'Complete candidate save not published')
        return dict(schema=SCHEMA, epoch=time.time(), role=task['role'], run_id=task['run_id'],
            execution=window.updates > 0, passed_execution=window.updates > 0, error=None, close_errors=[],
            completed_requested_update_window=window.updates>0 and window.stop_reason in ('STOP_SAVE','save_deadline'),
            window_mode='ORIGINAL_FINITE_WALL_CLOCK_HOUR', requested_update_quota=None,
            requested_hour_wall_window_elapsed=time.time()>=task['save_deadline'],
            training_timing=dict(ppo_started_epoch=window.ppo_started_epoch,ppo_ended_epoch=time.time(),native_and_load_startup_seconds=window.ppo_started_epoch-(task['save_deadline']-3600),observed_loop_wall_seconds_excluding_complete_save=time.time()-window.ppo_started_epoch-window.completed_save_wall_seconds,rollout_step_call_wall_seconds=window.rollout_step_call_wall_seconds,PPO_update_call_wall_seconds=window.ppo_update_call_wall_seconds,own_complete_save_wall_seconds=window.completed_save_wall_seconds),
            completed_actual_updates=window.updates, source_Adam_step=source_core['source_Adam_step'],
            final_Adam_step_set=sorted(set(window.fullsave['live_core']['Adam17_steps'])),
            target_asset_SHA=native['binding']['asset_sha256'],
            target_contract_SHA=native['binding']['contract_sha256'],
            source_env_state_applied=False, cross_D0_task_state_fresh_no_environment_exactresume=True,
            latest_complete_save=window.fullsave['latest_complete_save'],
            source_IO=source_io(cache), new_updates=window.updates, actual_optimizer_steps=window.optimizer_steps,
            actual_rollout_controls=window.rollout_controls, pretraining_validation_controls=1,
            learnedstate=dict(complete_original_actor_critic_STD6_Adam17_LR_normalizer=True,
                              source_core=source_core, live_core=window.fullsave['live_core']),
            fullsave=window.fullsave, asset_hash=native['binding'], stop_reason=window.stop_reason,
            worker_pid=os.getpid(), parent_pid=os.getppid(), owner_pid=task['owner_pid'],
            task_sha256=task['_task_sha256'], close_intent_required=True,
            parent_actual_childwait_RC0_final_intent_ERROR_checks_required=True,
            skill_graduation=False, mother_replaced=False, registry_writes=0)


def close_resources(task, out, ns, env, execution_error):
    failures = []
    if env is not None:
        try:
            put(out / 'PRE_CLOSE.json', dict(epoch=time.time(), calling_original_env_close=True))
            env.close()
            put(out / 'ENV_CLOSE_RETURNED.json', dict(epoch=time.time(), original_env_close_returned=True))
        except BaseException:
            failures.append(error_record(out, 'ENV_CLOSE_ERROR'))
    app = ns.get('app') if ns else None
    if app is not None:
        try:
            helper = importlib.import_module('app_close_semantics_v6')
            binding = helper._pin_original_app_close(app)
            need(binding['fast_shutdown'] is True, 'Original V6 fast_shutdown binding differs')
            if execution_error is None and not failures:
                raw = (out / 'V2_MIGRATION_FINAL.json').read_bytes()
                final = json.loads(raw)
                need(final['execution'] is True and not list(out.glob('*ERROR*.json')),
                     'Successful final/error evidence required before close intent')
                put(out / 'V2_APP_CLOSE_INTENT.json', dict(schema=SCHEMA, epoch=time.time(),
                    role=task['role'], run_id=task['run_id'], worker_pid=os.getpid(),
                    parent_pid=os.getppid(), task_sha256=task['_task_sha256'],
                    final_sha256=hashlib.sha256(raw).hexdigest(), final_bytes=len(raw),
                    original_bound_close=binding, env_close_returned=env is not None,
                    fullsave=final['fullsave'], original_app_close_arguments=[],
                    original_fast_shutdown_unchanged=True, expected_process_nonreturn=True,
                    app_close_returned=None, error_before_close=False,
                    parent_actual_wait_RC0_and_final_intent_ERROR_checks_required=True,
                    publication='TEMP_FLUSH_FSYNC_ATOMIC_RENAME_DIRECTORY_FSYNC_BEFORE_ORIGINAL_APP_CLOSE'))
        except BaseException:
            failures.append(error_record(out, 'APP_CLOSE_EVIDENCE_ERROR'))
        try:
            app.close()  # Original zero-argument fast shutdown may not return.
        except BaseException:
            failures.append(error_record(out, 'APP_CLOSE_ERROR'))
        else:
            put(out / 'APP_CLOSED.json', dict(epoch=time.time(), original_zero_argument_close_returned=True,
                                            parent_actual_wait_still_required=True))
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=Path, required=True)
    args = parser.parse_args()
    raw = args.task.read_bytes()
    task = json.loads(raw)
    out = Path(task.get('output_dir', args.task.resolve().parent)).resolve(strict=True)
    need(out.is_dir(), 'Parent-owned production output directory required')
    ns, env, execution_error, final = {}, None, None, None
    task['_out'] = str(out)
    task['_task_sha256'] = hashlib.sha256(raw).hexdigest()
    try:
        need(task['role'] in ROLES and task['num_envs'] == 20000 and task['steps_per_env'] == 24,
             'Nine original-family N20000/24 task required')
        need(task['role']=='E0' and task.get('window_mode')=='ORIGINAL_FINITE_WALL_CLOCK_HOUR' and type(task['max_additional_updates']) is int and task['max_additional_updates']==1000000,
             'Human E0 original finite-hour window required; original deadline/STOP remains authoritative')
        need(task['owner_pid'] == os.getppid() and time.time() < task['save_deadline'],
             'Original GO owner/deadline required before Native0PT and source IO')
        need(Path(task['source_path']).resolve() != out and str(task['run_id']), 'Source/run binding required')
        if task.get('helper_root'):
            sys.path.insert(0, str(Path(task['helper_root']).resolve(strict=True)))
        ns, binding, actual_cfg = load_original(task, out)
        torch = ns['torch']
        env, native = native_initialized(task, ns, actual_cfg, binding, torch)
        need(os.getppid() == task['owner_pid'] and time.time() < task['save_deadline'] and
             not Path(task['stop_file']).exists(), 'Owner/deadline/STOP before sole source IO')
        final = run_training(task, ns, env, native, torch)
        if not final['execution']:
            raise RuntimeError('No completed original PPO update in finite migration window')
        put(out / 'V2_MIGRATION_FINAL.json', final)
    except BaseException:
        execution_error = error_record(out, 'V2_MIGRATION_EXECUTION_ERROR')
        ns = task.get('_namespace', ns)
        env = task.get('_env', env)
        if not (out / 'V2_MIGRATION_FINAL.json').exists():
            put(out / 'V2_MIGRATION_FINAL.json', dict(schema=SCHEMA, epoch=time.time(),
                execution=False, passed_execution=False, error=execution_error, role=task.get('role'),
                run_id=task.get('run_id'), worker_pid=os.getpid(), parent_pid=os.getppid(),
                task_sha256=task['_task_sha256'], fullsave=getattr(task.get('_window'), 'fullsave', None),
                new_updates=getattr(task.get('_window'), 'updates', 0),
                close_intent_required=True, parent_actual_childwait_still_required=True))
    failures = close_resources(task, out, ns, env, execution_error)
    return 1 if execution_error is not None or failures else 0


if __name__ == '__main__':
    raise SystemExit(main())

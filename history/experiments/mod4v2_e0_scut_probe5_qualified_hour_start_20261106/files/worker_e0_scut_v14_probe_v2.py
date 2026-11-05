"""E0 SCUT V14 native + exactly one original PPO update; NOT an hour/skill run.

Source-derived from worker_mod4v2_expert_migration_hour_v5.py SHA256
2cc4edcb26befb370de2351e4380544d902d1b427658504b1c5fdf6286b8974f.
The parent exclusively owns owner/account/stage/admission and actual child wait.
One fresh reset and the same single native zero precede the once-only source
byte-read/hash/CPU decode.  Install the source command/done and reward adapters
at their distinct prebuild/postconstructor/postreset interfaces.  Save U000
before PPO, then use only original runner.learn for 24 controls / one update /
20 Adam steps.  Keep complete learner and historical source, fresh live D0 and
adapter histories.  MOD4 35/38/6 and reset/DR are explicit compatibility choices,
not numerical equivalence to the SCUT 35/78/6 environment.  No registry writes.
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

ROLES = ('E0',)
SCHEMA = 'mod4v2.expert_migration.original_ppo.v1'  # Parent FINAL/fullsave ABI retained.
SCUT_MODE = 'SCUT_V14_NATIVE_AND_ONE_PPO_PROBE_NOT_HOUR'
SCUT_TASK = 'Robotics-Wheelbipe-V14-Flat-v0'
SCUT_UPSTREAM_HEAD = 'b8ff79f3df855faf9dc92f4a282bd80c42649466'
SCUT_REFERENCE_INITIAL_LR = 1.0e-4  # Reference only; NEVER applied to the loaded learner.
E0_SOURCE = dict(source_SHA='6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693',
                 source_bytes=14035411, source_iteration=32004, source_Adam_step=641600,
                 source_LR=0.0002562890625000001)
SCUT_ALGORITHM = dict(value_loss_coef=4.0, use_clipped_value_loss=True, clip_param=0.2,
    entropy_coef=0.005, num_learning_epochs=5, num_mini_batches=4, schedule='adaptive',
    gamma=0.99, lam=0.95, desired_kl=0.01, max_grad_norm=1.0)
SCUT_ADAPTER_SHA = {
    'scut_v14_flat_reward_adapter_v3': 'c82aa2d0eb3e249afad9f439c1d8a7e5d54b628257fbb3914e802347b916fe31',
    'scut_v14_flat_command_termination_adapter_v1': '3f4c93437a7128677701d58c7012ab13a91d78bec727e1f0b1182f12316a1cd8'}
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


def config_snapshot(value, torch):
    """Read actual cfg values; name callables rather than pickling local factories."""
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        need(not math.isnan(value), 'NaN actual cfg value')
        return value if math.isfinite(value) else ('+inf' if value > 0 else '-inf')
    if isinstance(value, Path):
        return str(value)
    if torch.is_tensor(value):
        return dict(tensor=value.detach().cpu().tolist(), dtype=str(value.dtype), shape=list(value.shape))
    if isinstance(value, (torch.dtype, torch.device)):
        return str(value)
    if isinstance(value, dict):
        need(all(isinstance(key, str) for key in value), 'Actual cfg needs explicit string keys')
        return {key: config_snapshot(item, torch) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [config_snapshot(item, torch) for item in value]
    if isinstance(value, slice):
        return dict(slice=[config_snapshot(item, torch) for item in (value.start, value.stop, value.step)])
    if callable(value) and hasattr(value, '__module__') and hasattr(value, '__qualname__'):
        return dict(callable=value.__module__ + ':' + value.__qualname__)
    if hasattr(value, 'to_dict') and callable(value.to_dict):
        return config_snapshot(value.to_dict(), torch)
    if type(value).__module__.startswith('numpy') and hasattr(value, 'tolist'):
        return config_snapshot(value.tolist(), torch)
    raise TypeError('Unclassified actual cfg value: ' + type(value).__module__ + '.' + type(value).__qualname__)


def scut_model_evidence(alg, source, torch):
    """No forward/observe/reset: prove loaded module structure and norm ownership."""
    result = {}
    for label, input_dim, output_dim in (('actor', 35, 6), ('critic', 38, 1)):
        module = getattr(alg, label, None)
        need(isinstance(module, torch.nn.Module), 'Unknown original learner module ABI: ' + label)
        saved = source[label + '_state_dict']
        need(exact(module.state_dict(), saved, torch), 'Live/source module state differs: ' + label)
        linears, activations, norms = [], [], []
        for name, child in module.named_modules():
            cls = type(child).__module__ + '.' + type(child).__qualname__
            if isinstance(child, torch.nn.Linear):
                linears.append(dict(path=name, in_features=child.in_features, out_features=child.out_features))
            if isinstance(child, torch.nn.ELU):
                activations.append(dict(path=name, class_name=cls, alpha=float(child.alpha)))
            if 'normaliz' in (name + ' ' + cls).lower():
                state = child.state_dict()
                source_keys = [key for key in saved if key.startswith(name + '.')]
                is_identity = type(child) is torch.nn.Identity
                if is_identity:
                    need(not state and not source_keys, 'Identity normalizer unexpectedly owns statistics')
                else:
                    need(bool(state) and bool(source_keys), 'Nonidentity normalization has no source statistics')
                    need(all(name + '.' + key in saved and exact(value, saved[name + '.' + key], torch)
                             for key, value in state.items()), 'Normalizer statistics differ from source')
                norms.append(dict(path=name, class_name=cls,
                    semantics='identity' if is_identity else 'source_loaded_stateful_normalization',
                    source_root=label + '_state_dict', source_keys=source_keys,
                    statistics_invented=False, source_state_exact=True))
        dims = [(row['in_features'], row['out_features']) for row in linears]
        need(dims == [(input_dim, 256), (256, 128), (128, 64), (64, output_dim)] and
             len(activations) == 3 and all(row['alpha'] == 1.0 for row in activations),
             'Original 256/128/64 ELU morphology/interface differs: ' + label)
        need(norms, 'Unknown normalizer ownership; inspect original learner rather than invent statistics: ' + label)
        result[label] = dict(class_name=type(module).__module__ + '.' + type(module).__qualname__,
            linear_layers=linears, activations=activations, normalization=norms,
            state_keys=list(saved), complete_source_state_exact=True)
    return result


def scut_reward_state(env, torch):
    """Capture cached history directly; never refresh sensor/compute observations."""
    state = env._scut_v14_flat_reward_v1
    sensor = state.sensor
    data = getattr(sensor, '_data', None)
    need(data is not None and torch.is_tensor(data.net_forces_w_history),
         'Real contact history cache ABI missing')
    history = data.net_forces_w_history
    need(history.shape[0] == env.num_envs and history.shape[1] == 3 and history.shape[-1] == 3,
         'Original three-sample contact history differs')
    need(int(state.last_step) == int(env.common_step_counter), 'Reward/control history alignment differs')
    return cpu_tree(dict(version=2, prev=state.prev, prevprev=state.prevprev,
        last_step=state.last_step, raw=state.raw, last_weighted_terms=state.last_weighted_terms,
        numeric_bad=state.numeric_bad, common_step_counter=int(env.common_step_counter),
        contact_history=history, contact_sensor_cached_data=owned_values(data, torch),
        contact_sensor_clock_and_buffers=owned_values(sensor, torch),
        cfg_spec=env.cfg._scut_v14_flat_reward_v1, no_sensor_refresh=True), torch)


def scut_recipe_binding(task, env, cfg, source_core, model_evidence, torch):
    reward = task['_scut_reward']
    cmd = task['_scut_cmd']
    active = list(env.reward_manager.active_terms)
    need(active == list(reward.ACTIVE_WEIGHTS), 'Actual SCUT active reward order differs')
    weights = {name: float(env.reward_manager.get_term_cfg(name).weight) for name in active}
    need(weights == reward.ACTIVE_WEIGHTS and len(reward.REWARD_WEIGHTS) == 37 and len(active) == 26,
         'Actual original 37/26 reward weights differ')
    expected = dict(reward.EXPECTED_PPO_ALGORITHM)
    need(expected.pop('learning_rate') == SCUT_REFERENCE_INITIAL_LR and expected == SCUT_ALGORITHM,
         'SCUT PPO source reference disagrees with caller binding')
    need(all(cfg['algorithm'][key] == value for key, value in SCUT_ALGORITHM.items()) and
         cfg['algorithm']['learning_rate'] == source_core['source_LR'], 'Effective PPO recipe/LR differs')
    command = env.command_manager.get_term('twist')
    need(type(command) is cmd.ScutV14FlatCommand and command.training_iteration == source_core['iteration'],
         'Real pre-rollout command iteration/class differs')
    recipe = dict(schema='mod4v2.e0.scut_v14_recipe_binding.v1', mode=SCUT_MODE,
        task=SCUT_TASK, upstream_reported_HEAD=SCUT_UPSTREAM_HEAD, role='E0',
        original_ordered_37_weights=list(reward.REWARD_WEIGHTS.items()), active_26_weights_observed=weights,
        zero_weight_terms={key: weight for key, weight in reward.REWARD_WEIGHTS.items() if weight == 0.0},
        reward_formula='ordered sum of (raw * 0.02) * original_weight; no positive clipping',
        reward_bind_actual=task['_scut_reward_bind'], command_done_configure=task['_scut_cmd_configure'],
        command_done_bind=task['_scut_cmd_bind'], real_training_iteration=command.training_iteration,
        actual_command_class=type(command).__module__ + '.' + type(command).__qualname__,
        observation_debug_gate=dict(config=list(env._scut_v14_obs_gate_config),
                                   actual_counter=env._scut_v14_value_debug_step),
        effective_algorithm=cfg['algorithm'], reference_default_learning_rate=SCUT_REFERENCE_INITIAL_LR,
        inherited_mutable_learning_rate=source_core['source_LR'], default_LR_applied=False,
        model_source_alignment=model_evidence, source_core=source_core,
        observation_interface=dict(upstream_actor=35, upstream_critic=78, upstream_action=6,
            retained_MOD4_A0_actor=35, retained_MOD4_A0_critic=38, retained_action=6,
            reason='MOD4 morphology and existing source learner compatibility; no fabricated privileged 78',
            exact_SCUT_observation_equivalence=False),
        retained_MOD4_reset_DR=dict(original_height_resetbank_and_DR=True,
            exact_SCUT_numeric_equivalence=False, source_environment_state_applied=False),
        actual_environment_cfg=config_snapshot(env.cfg.to_dict(), torch),
        actual_runner_cfg=config_snapshot(cfg, torch), source_files=task['_scut_adapter_sources'],
        original_entry=task['_entry_receipt'], legacy_flags_removed=task['_scut_legacy_flags_removed'],
        parent_owns_actualwait=True, hour_not_started=True, skill_graduation=False, registry_writes=0,
        evidence_kind='OBSERVED_CONFIGURATION_AND_SOURCE_BINDING_NOT_SKILL_ACCEPTANCE')
    return config_snapshot(recipe, torch)


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
    # The real MOD4 step wrapper treats RM_GYRO_CURRICULUM='0' as a
    # straight-speed/no-yaw contract, not as SCUT curriculum=None.  Remove both
    # old switches after restoration; cmd.configure disables manager curricula.
    task['_scut_legacy_flags_removed'] = {
        key: os.environ.pop(key, None) for key in ('RM_SPIN_STAGE', 'RM_GYRO_CURRICULUM')}
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
    package_requirements = json.loads((package / 'runtime_requirements.json').read_text(encoding='utf-8'))
    need(binding['asset_sha256'] == '7361b6930a7270e65f3b290cfa71c50f8e1f0beccaa9cab1fa8a994f03cb35b8' and
         binding['contract_sha256'] == 'f01ffcf0f967e1c1f8dc153c9e06d73a70ab3f78e17e8b479159c14a6cf63047' and
         package_requirements['native_transmission']['implementation'] == 'HW300N60_CONTINUOUS_D6_V3',
         'Exact new HW300N60_CONTINUOUS_D6_V3 package required')
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
    adapter_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(adapter_root))
    modules, sources = {}, {}
    for name, wanted in SCUT_ADAPTER_SHA.items():
        path = adapter_root / (name + '.py')
        raw_adapter = path.read_bytes()
        need(hashlib.sha256(raw_adapter).hexdigest() == wanted, 'SCUT adapter source changed: ' + name)
        module = importlib.import_module(name)
        need(Path(module.__file__).resolve() == path, 'SCUT module resolved to a different source: ' + name)
        modules[name] = module
        sources[name] = dict(path=str(path), bytes=len(raw_adapter), SHA256=wanted)
    cmd = task['_scut_cmd'] = modules['scut_v14_flat_command_termination_adapter_v1']
    reward = task['_scut_reward'] = modules['scut_v14_flat_reward_adapter_v3']
    task['_scut_adapter_sources'] = sources
    original_runner_config = ns['runner_config']
    def runner_config():
        cfg = original_runner_config()
        for key, value in SCUT_ALGORITHM.items():
            need(hasattr(cfg.algorithm, key), 'Unknown original PPO cfg ABI: ' + key)
            setattr(cfg.algorithm, key, value)
        # ns.args.learning_rate is populated from the actual CPU source before
        # this call; never use the SCUT initial/reference LR for a continuation.
        need(ns['args'].learning_rate == E0_SOURCE['source_LR'], 'Actual inherited mutable LR required')
        cfg.algorithm.learning_rate = ns['args'].learning_rate
        return cfg
    ns['runner_config'] = runner_config
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
        task['_scut_cmd_configure'] = cmd.configure(cfg, ns['mod4_task'])
        actual_cfg['scut_reward_configure'] = reward.configure(cfg, ns['mod4_task'])
        actual_cfg['cfg'] = cfg
        env = constructor(**kwargs)
        task['_env'] = env  # Close the real constructed env even if bind fails.
        task['_scut_cmd_bind'] = cmd.bind(env)
        cmd.set_training_iteration(env, task['source_iteration'])  # Before sole reset/first resampling.
        return env
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
    task['_scut_reward_bind'] = task['_scut_reward'].bind(env)  # v2: after SOLE reset, before SAME zero.
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
    source_immutable = cpu_tree(source, torch)  # CPU-only independent baseline; no second source read/decode.
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
    need(cfg['num_steps_per_env'] == 24 and
         all(cfg['algorithm'][key] == value for key, value in SCUT_ALGORITHM.items()) and
         cfg['algorithm']['learning_rate'] == source_core['source_LR'],
         'Source-derived SCUT Flat PPO / inherited mutable LR required')
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
        need(adam_core(loaded, torch) == source_core and
             runner.alg.learning_rate == source_core['source_LR'] and exact(source, source_immutable, torch),
             'Source/current mutable LR or immutable CPU source differs')
        cmd = task['_scut_cmd']
        cmd.set_training_iteration(env, int(runner.current_learning_iteration))
        model_evidence = scut_model_evidence(runner.alg, source, torch)
        recipe = scut_recipe_binding(task, env, cfg, source_core, model_evidence, torch)
        actual_algorithm = {key: getattr(runner.alg, key) for key in SCUT_ALGORITHM}
        need(actual_algorithm == SCUT_ALGORITHM, 'Actual original PPO attributes differ from SCUT cfg')
        recipe['actual_original_PPO_class'] = type(runner.alg).__module__ + ':' + type(runner.alg).__qualname__
        recipe['actual_algorithm_attributes'] = config_snapshot(actual_algorithm, torch)
        recipe['selected_source'] = dict(path=str(cache.path), SHA=cache.SHA,
                                        bytes=len(cache.raw), source_IO=source_io(cache))
        recipe['reward_adapter_pending_elsewhere_interpretation'] = dict(
            caller_applied_now=['commands', 'termination', 'PPO'],
            still_different=['MOD4 reset distribution and DR', 'MOD4 actor35/critic38 vs SCUT actor35/critic78'],
            original_reward_only_receipt_is_not_full_environment_equivalence=True)
        task['_scut_recipe_binding'] = recipe
        put(out / 'SCUT_RECIPE_BINDING.json', recipe)
        put(out / 'V2_LEARNER_LOADED.json', dict(schema=SCHEMA, epoch=time.time(), source_IO=source_io(cache),
            source_core=source_core, full_actor_critic_learned_STD_Adam_normalizer_exact=True,
            vector_wrapper_redundant_physical_resets_suppressed=wrapper_reset_calls[0],
            physical_restore_calls=0, fresh_V2_D0_retained=True))

        def save(path, *args, **kwargs):
            save_wall_started = time.time()
            requested_path = Path(path).resolve()
            need(requested_path.is_relative_to(out.resolve()) and not cache.owns(requested_path) and
                 not window.in_update, 'Own complete-boundary candidate path required')
            need(window.updates in (0, 1) and window.optimizer_steps == 20 * window.updates and
                 window.rollout_controls == 24 * window.updates, 'Actual PPO/Adam/control counts differ at save boundary')
            path = (out / ('model_mod4v2_migration_complete_U%03d.pt' % window.updates)).resolve()
            need(not cache.owns(path) and exact(source, source_immutable, torch), 'Immutable source changed')
            cmd.set_training_iteration(env, int(runner.current_learning_iteration))
            live = dict(runner.alg.save(), iter=int(runner.current_learning_iteration))
            core = adam_core(live, torch)
            if window.updates == 0:
                need(all(exact(live[key], source[key], torch) for key in CORE_KEYS) and core == source_core,
                     'U000 full initial learner is not source-exact')
            need(all(step == old + window.optimizer_steps for step, old in
                     zip(core['Adam17_steps'], source_core['Adam17_steps'])), 'Actual Adam17 delta differs')
            physical = live_physical(env, task['role'], torch)
            candidate = cpu_tree(live, torch)
            candidate.update(physical)
            candidate['scut_v14_command_termination_state'] = cmd.state_dict(env)
            candidate['scut_v14_reward_state'] = scut_reward_state(env, torch)
            candidate['scut_v14_recipe_binding'] = cpu_tree(recipe, torch)
            candidate['scut_v14_live_algorithm'] = dict(
                iteration=int(runner.current_learning_iteration), mutable_learning_rate=float(runner.alg.learning_rate),
                actual_algorithm_attributes={key: getattr(runner.alg, key) for key in SCUT_ALGORITHM})
            need(candidate['scut_v14_live_algorithm']['actual_algorithm_attributes'] == SCUT_ALGORITHM and
                 float(runner.alg.learning_rate) == core['source_LR'], 'Actual saved PPO cfg/current LR differs')
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
            candidate['mod4v2_migration'].update(window_mode=SCUT_MODE, requested_effective_update_quota=1,
                ppo_started_epoch=window.ppo_started_epoch, completed_save_wall_seconds=window.completed_save_wall_seconds,
                hour_not_started=True, skill_graduation=False, registry_writes=0,
                source_once1=True, reference_default_learning_rate=SCUT_REFERENCE_INITIAL_LR,
                actual_source_mutable_learning_rate=source_core['source_LR'],
                initial_checkpoint_acceptance=task.get('_scut_initial_checkpoint_acceptance'),
                initial_checkpoint_is_before_any_PPO=window.updates == 0)
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
            need(exact(source, source_immutable, torch) and
                 exact(decoded['mod4v2_historical_source_checkpoint'], source_immutable, torch),
                 'Immutable full historical source changed during own save')
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
                latest_complete_save=dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()),
                window_mode=SCUT_MODE, requested_update_quota=1, hour_not_started=True,
                requested_original_runner_save_path=str(requested_path),
                own_roundtrip_full_tree_exact=True, initial_source_core_exact=window.updates == 0,
                command_done_and_reward_history_saved=True, actual_cfg_and_source_SHA_saved=True)
            name = ('V2_COMPLETE_SAVE.json' if not (out / 'V2_COMPLETE_SAVE.json').exists()
                    else 'V2_COMPLETE_SAVE_U%03d.json' % window.updates)
            put(out / name, window.fullsave)
            return None

        runner.save = save  # Install original full-save boundary BEFORE U000 or any PPO control.
        initial_counts = dict(physics=int(env._sim_step_counter), feedback=int(env._feedback_100hz_tick),
                              controls=int(env.common_step_counter))
        runner.save(str(out / 'model_mod4v2_migration_complete_U000.pt'))
        initial_live = dict(runner.alg.save(), iter=int(runner.current_learning_iteration))
        initial_core_exact = (all(exact(initial_live[key], source[key], torch) for key in CORE_KEYS) and
                              adam_core(initial_live, torch) == source_core and
                              runner.alg.learning_rate == source_core['source_LR'])
        need(initial_core_exact and window.updates == window.optimizer_steps == window.rollout_controls == 0 and
             initial_counts == dict(physics=int(env._sim_step_counter), feedback=int(env._feedback_100hz_tick),
                                    controls=int(env.common_step_counter)) and
             window.fullsave['initial_source_core_exact'] and window.fullsave['own_roundtrip_full_tree_exact'],
             'Initial checkpoint acceptance requires source-exact U000 before PPO/no physical advance')
        initial_acceptance = dict(schema='mod4v2.e0.scut_initial_checkpoint_acceptance.v1',
            epoch=time.time(), role='E0', run_id=task['run_id'], worker_pid=os.getpid(),
            task_sha256=task['_task_sha256'], mode=SCUT_MODE, accepted=True,
            passed=True, source_SHA=cache.SHA, actor_exact=True, critic_exact=True,
            normalization_exact=True, learned_STD_exact=True, Adam17_exact=True, LR_exact=True,
            iteration_exact=True, latest_complete_save=copy.deepcopy(window.fullsave['latest_complete_save']),
            actual_save=copy.deepcopy(window.fullsave['latest_complete_save']),
            checkpoint=window.fullsave['checkpoint'], bytes=window.fullsave['bytes'], SHA=window.fullsave['SHA'],
            actor_source_exact=True, critic_source_exact=True, normalizers_source_exact=True,
            learned_STD6_source_exact=True, all17_Adam_full_state_source_exact=True,
            optimizer_and_algorithm_mutableLR_source_exact=True, iteration_source_exact=True,
            source_core=source_core, saved_core=window.fullsave['live_core'],
            core_structure_and_normalization_source=model_evidence, statistics_invented=False,
            source_IO=source_io(cache), source_once1=True, source_immutable_CPU_tree_exact=True,
            own_full_save_roundtrip_exact=True, actual_PPO_updates=0, actual_Adam_steps=0,
            actual_PPO_rollout_controls=0, native_zero_controls_not_PPO=1,
            physical_counters_unchanged_during_initial_save=initial_counts,
            live_D0_fresh=True, command_done_and_reward_history_saved=True,
            source_environment_state_applied=False, hour_not_started=True,
            skill_graduation=False, registry_writes=0)
        put(out / 'SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json', initial_acceptance)
        task['_scut_initial_checkpoint_acceptance'] = initial_acceptance
        initial_save_seconds = window.completed_save_wall_seconds
        original_update = runner.alg.update
        original_step = runner.alg.optimizer.step
        original_log = runner.logger.log
        original_vec_step = vec.step

        def opt_step(*args, **kwargs):
            need(window.in_update and window.optimizer_steps < 20, 'Adam step outside sole original PPO update')
            result = original_step(*args, **kwargs)
            window.optimizer_steps += 1
            return result

        def update(*args, **kwargs):
            need(not window.in_update and window.updates == 0 and window.rollout_controls == 24 and
                 task['_scut_initial_checkpoint_acceptance']['accepted'] is True,
                 'Exactly one original update after accepted U000 / 24 rollout controls required')
            cmd.set_training_iteration(env, int(runner.current_learning_iteration))
            update_wall_started = time.time()
            window.in_update = True
            try:
                result = original_update(*args, **kwargs)
            finally:
                window.in_update = False
                window.ppo_update_call_wall_seconds += time.time() - update_wall_started
            need(window.optimizer_steps == 20 * (window.updates + 1), 'Original 5 x 4 Adam update changed')
            window.updates += 1
            cmd.set_training_iteration(env, int(runner.current_learning_iteration))
            return result

        def vec_step(*args, **kwargs):
            need(not window.in_update and window.updates == 0 and window.rollout_controls < 24 and
                 task['_scut_initial_checkpoint_acceptance']['accepted'] is True,
                 'Environment step outside sole accepted PPO rollout')
            cmd.set_training_iteration(env, int(runner.current_learning_iteration))
            rollout_wall_started = time.time()
            result = original_vec_step(*args, **kwargs)
            window.rollout_step_call_wall_seconds += time.time() - rollout_wall_started
            window.rollout_controls += 1
            return result

        def log(*args, **kwargs):
            need(window.updates == 1 and window.optimizer_steps == 20 and window.rollout_controls == 24,
                 'Original logger reached outside completed sole probe update')
            cmd.set_training_iteration(env, int(runner.current_learning_iteration))
            result = original_log(*args, **kwargs)
            reason = window.boundary_reason()
            # Metadata only: no additional update, observation or checkpoint read.
            put(out / ('V2_TRAINING_PROGRESS_U%06d.json' % window.updates), dict(
                epoch=time.time(), actual_new_updates=window.updates, actual_optimizer_steps=window.optimizer_steps,
                actual_rollout_controls=window.rollout_controls, optimized_transitions=20000*window.rollout_controls,
                ppo_started_epoch=window.ppo_started_epoch, rollout_step_call_wall_seconds=window.rollout_step_call_wall_seconds,
                PPO_update_call_wall_seconds=window.ppo_update_call_wall_seconds,
                own_complete_save_wall_seconds=window.completed_save_wall_seconds,
                observed_loop_wall_seconds_excluding_complete_save=time.time()-window.ppo_started_epoch-
                    (window.completed_save_wall_seconds-initial_save_seconds),
                window_mode=SCUT_MODE, requested_update_quota=1, hour_not_started=True,
                no_skill_claim=True, parent_save_deadline=task['save_deadline']))
            if reason:
                window.stop_reason = reason
                if window.last_saved_update != window.updates:
                    runner.save(str(out / 'model_mod4v2_migration_complete_U001.pt'))
                raise SavedStop(reason)
            return result

        runner.alg.optimizer.step = opt_step
        runner.alg.update = update
        runner.logger.log = log
        vec.step = vec_step
        ppo_before = dict(physics=int(env._sim_step_counter), feedback=int(env._feedback_100hz_tick),
                          controls=int(env.common_step_counter), actual_alg_updates=window.updates)
        task['_scut_ppo_before'] = ppo_before
        need(ppo_before == dict(initial_counts, actual_alg_updates=0), 'Physical advance between U000 and PPO')
        window.ppo_started_epoch = time.time()
        put(out / 'V2_PPO_LOOP_STARTED.json', dict(epoch=window.ppo_started_epoch, run_id=task['run_id'], role='E0',
            original_GO_epoch=task['_worker_started_epoch'],
            native_and_load_startup_seconds=window.ppo_started_epoch-task['_worker_started_epoch'],
            requested_update_quota=1, window_mode=SCUT_MODE, hour_not_started=True,
            initial_checkpoint_acceptance=initial_acceptance, physical_before=ppo_before,
            original_save_deadline=task['save_deadline']))
        # Use ONLY the original learn path.  Its iteration label is left as-is;
        # actual alg.update/Adam/control counters, not iter+1 arithmetic, admit it.
        reason = window.boundary_reason()
        if reason:
            window.stop_reason = reason  # U000 already durably exists; do not publish it twice.
        else:
            task['_scut_original_learn_calls'] = 1
            try:
                runner.learn(num_learning_iterations=1, init_at_random_ep_len=True)
            except SavedStop:
                pass
            cmd.set_training_iteration(env, int(runner.current_learning_iteration))
            if window.last_saved_update != window.updates:
                runner.save(str(out / ('model_mod4v2_migration_complete_U%03d.pt' % window.updates)))
        ppo_after = dict(physics=int(env._sim_step_counter), feedback=int(env._feedback_100hz_tick),
                         controls=int(env.common_step_counter), actual_alg_updates=window.updates)
        ppo_delta = {key: ppo_after[key]-ppo_before[key] for key in ppo_before}
        task['_scut_ppo_after'] = ppo_after
        task['_scut_ppo_delta'] = ppo_delta
        actual_source_io = source_io(cache)
        accepted = (window.updates == 1 and window.optimizer_steps == 20 and window.rollout_controls == 24 and
            task.get('_scut_original_learn_calls') == 1 and initial_acceptance['accepted'] is True and
            actual_source_io['physical_byte_opens'] == actual_source_io['CPU_decodes'] == 1 and
            ppo_delta == dict(physics=192, feedback=48, controls=24, actual_alg_updates=1) and
            window.fullsave is not None and window.fullsave['actual_new_updates'] == 1 and
            window.last_saved_update == 1 and exact(source, source_immutable, torch))
        need(accepted, 'Probe requires actual1/20Adam/24controls/192physics/48feedback/sourceIO1/acceptedU000/fullU001')
        if window.stop_reason is None:
            window.stop_reason = 'ONE_UPDATE_PROBE_COMPLETED_NOT_HOUR'
        ppo_ended = time.time()
        return dict(schema=SCHEMA, epoch=ppo_ended, role=task['role'], run_id=task['run_id'],
            execution=accepted, passed_execution=accepted, error=None, close_errors=[],
            completed_requested_update_window=accepted, window_mode=SCUT_MODE, requested_update_quota=1,
            requested_hour_wall_window_elapsed=False, hour_not_started=True,
            training_timing=dict(ppo_started_epoch=window.ppo_started_epoch, ppo_ended_epoch=ppo_ended,
                native_and_load_startup_seconds=window.ppo_started_epoch-task['_worker_started_epoch'],
                observed_loop_wall_seconds_excluding_complete_save=ppo_ended-window.ppo_started_epoch-
                    (window.completed_save_wall_seconds-initial_save_seconds),
                rollout_step_call_wall_seconds=window.rollout_step_call_wall_seconds,
                PPO_update_call_wall_seconds=window.ppo_update_call_wall_seconds,
                own_complete_save_wall_seconds=window.completed_save_wall_seconds,
                initial_complete_save_wall_seconds=initial_save_seconds),
            completed_actual_updates=window.updates, source_Adam_step=source_core['source_Adam_step'],
            final_Adam_step_set=sorted(set(window.fullsave['live_core']['Adam17_steps'])),
            target_asset_SHA=native['binding']['asset_sha256'],
            target_contract_SHA=native['binding']['contract_sha256'],
            source_env_state_applied=False, cross_D0_task_state_fresh_no_environment_exactresume=True,
            latest_complete_save=window.fullsave['latest_complete_save'],
            source_IO=actual_source_io, new_updates=window.updates, actual_optimizer_steps=window.optimizer_steps,
            actual_rollout_controls=window.rollout_controls, pretraining_validation_controls=1,
            learnedstate=dict(complete_original_actor_critic_STD6_Adam17_LR_normalizer=True,
                              source_core=source_core, live_core=window.fullsave['live_core']),
            fullsave=window.fullsave, asset_hash=native['binding'], stop_reason=window.stop_reason,
            initial_checkpoint_acceptance=initial_acceptance, source_once1=True,
            actual_original_runner_learn_calls=1, actual_update_delta=ppo_delta['actual_alg_updates'],
            PPO_physical_feedback_counters=dict(before=ppo_before, after=ppo_after, delta=ppo_delta),
            real_command_training_iteration=env.command_manager.get_term('twist').training_iteration,
            recipe_binding_file=str(out / 'SCUT_RECIPE_BINDING.json'),
            worker_pid=os.getpid(), parent_pid=os.getppid(), owner_pid=task['owner_pid'],
            task_sha256=task['_task_sha256'], close_intent_required=True,
            parent_actual_childwait_RC0_final_intent_ERROR_checks_required=True,
            skill_graduation=False, mother_replaced=False, registry_writes=0)


def close_resources(task, out, ns, env, execution_error):
    failures = []
    def failed_final():
        # Close may fast-exit the process: publish a real failed FINAL before it.
        # Only this task's already-owned FINAL is replaced, preserving its shape.
        if not failures:
            return
        path = out / 'V2_MIGRATION_FINAL.json'
        value = json.loads(path.read_bytes())
        value.update(execution=False, passed_execution=False, completed_requested_update_window=False,
                     error=value.get('error') or '\n'.join(failures), close_errors=list(failures))
        temporary = path.with_name(path.name + '.close_error.partial')
        raw = json.dumps(value, indent=2, allow_nan=False).encode('utf-8')
        with temporary.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        if os.name == 'posix':
            fd = os.open(str(out), os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    if env is not None:
        try:
            put(out / 'PRE_CLOSE.json', dict(epoch=time.time(), calling_original_env_close=True))
            env.close()
            put(out / 'ENV_CLOSE_RETURNED.json', dict(epoch=time.time(), original_env_close_returned=True))
        except BaseException:
            failures.append(error_record(out, 'ENV_CLOSE_ERROR'))
            failed_final()
    app = ns.get('app') if ns else None
    if app is not None:
        try:
            helper = importlib.import_module('app_close_semantics_v6')
            binding = helper._pin_original_app_close(app)
            need(binding['fast_shutdown'] is True, 'Original V6 fast_shutdown binding differs')
            if execution_error is None and not failures:
                raw = (out / 'V2_MIGRATION_FINAL.json').read_bytes()
                final = json.loads(raw)
                need(final['execution'] is True and final['passed_execution'] is True and
                     final['completed_requested_update_window'] is True and final['window_mode'] == SCUT_MODE and
                     final['completed_actual_updates'] == 1 and final['source_once1'] is True and
                     final['initial_checkpoint_acceptance']['accepted'] is True and
                     final['worker_pid'] == os.getpid() and final['task_sha256'] == task['_task_sha256'] and
                     (out / 'ENV_CLOSE_RETURNED.json').is_file() and not list(out.glob('*ERROR*.json')),
                     'Actual probe FINAL/task/PID/env-close/U000/sourceIO1/error evidence required before close intent')
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
            failed_final()
        try:
            app.close()  # Original zero-argument fast shutdown may not return.
        except BaseException:
            failures.append(error_record(out, 'APP_CLOSE_ERROR'))
            failed_final()
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
    task['_worker_started_epoch'] = time.time()
    task['_scut_original_learn_calls'] = 0
    try:
        need(task['role'] in ROLES and type(task['num_envs']) is int and task['num_envs'] == 20000 and
             type(task['steps_per_env']) is int and task['steps_per_env'] == 24,
             'E0 original-family N20000/24 task required')
        need(task['role'] == 'E0' and task.get('window_mode') == SCUT_MODE and
             type(task['max_additional_updates']) is int and task['max_additional_updates'] == 1,
             'E0 SCUT native + exactly one PPO probe mode/int cap1 required; hour not started')
        need(all(key in task and type(task[key]) is type(value) and task[key] == value
                 for key, value in E0_SOURCE.items()), 'Exact formal 6cd E0 source metadata required')
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
        if not (final['execution'] and final['completed_requested_update_window'] and
                final['window_mode'] == SCUT_MODE and final['completed_actual_updates'] == 1 and
                final['source_once1'] and final['initial_checkpoint_acceptance']['accepted']):
            raise RuntimeError('SCUT one-update probe sourceIO1 / U000 / actual1 acceptance incomplete')
        put(out / 'V2_MIGRATION_FINAL.json', final)
    except BaseException:
        execution_error = error_record(out, 'V2_MIGRATION_EXECUTION_ERROR')
        ns = task.get('_namespace', ns)
        env = task.get('_env', env)
        if not (out / 'V2_MIGRATION_FINAL.json').exists():
            failed_save = getattr(task.get('_window'), 'fullsave', None)
            put(out / 'V2_MIGRATION_FINAL.json', dict(schema=SCHEMA, epoch=time.time(),
                execution=False, passed_execution=False, error=execution_error, close_errors=[],
                completed_requested_update_window=False, role=task.get('role'),
                run_id=task.get('run_id'), worker_pid=os.getpid(), parent_pid=os.getppid(),
                owner_pid=task.get('owner_pid'), window_mode=SCUT_MODE, requested_update_quota=1,
                requested_hour_wall_window_elapsed=False, hour_not_started=True,
                task_sha256=task['_task_sha256'], fullsave=failed_save,
                latest_complete_save=failed_save['latest_complete_save'] if failed_save else None,
                source_IO=failed_save['source_IO'] if failed_save else None,
                new_updates=getattr(task.get('_window'), 'updates', 0),
                completed_actual_updates=getattr(task.get('_window'), 'updates', 0),
                actual_optimizer_steps=getattr(task.get('_window'), 'optimizer_steps', 0),
                actual_rollout_controls=getattr(task.get('_window'), 'rollout_controls', 0),
                initial_checkpoint_acceptance=task.get('_scut_initial_checkpoint_acceptance'),
                PPO_physical_feedback_counters=dict(before=task.get('_scut_ppo_before'),
                    after=task.get('_scut_ppo_after'), delta=task.get('_scut_ppo_delta')),
                source_env_state_applied=False, cross_D0_task_state_fresh_no_environment_exactresume=True,
                skill_graduation=False, mother_replaced=False, registry_writes=0,
                close_intent_required=True, parent_actual_childwait_still_required=True,
                parent_actual_childwait_RC0_final_intent_ERROR_checks_required=True))
    failures = close_resources(task, out, ns, env, execution_error)
    return 1 if execution_error is not None or failures else 0


if __name__ == '__main__':
    raise SystemExit(main())

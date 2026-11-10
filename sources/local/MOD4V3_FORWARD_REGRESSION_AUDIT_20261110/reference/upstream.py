"""Execute pinned, already archived SCUT functions without copying its tree.

AST extraction changes no function body or line number. Imports and Isaac scene
constructors are excluded; the explicit SDK bridge supplies their dependencies.
SOURCES.json records file SHA256, Git blob, commit and existing Git path.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import types
from collections.abc import Mapping, Sequence

import torch
from . import math_ops

HERE = Path(__file__).resolve().parent
BASE_METHODS = (
    '_get_rewards', '_get_root_quat_inv_and_wheel_pos_b', '_invalidate_step_caches',
    '_use_absolute_height', '_use_leg_length_height', '_get_leg_length_height',
    '_apply_height_obs_clip', '_get_observed_height', '_get_height_reward_target_height',
    '_get_height_reward_reference_height', '_get_wheel_contact_force_peaks',
    '_get_wheel_air_spin_reward', '_get_policy_action_slices', '_get_leg_policy_action_dim',
    '_get_vel_height_gate_full_error', '_get_vel_height_gate_zero_error',
    '_get_vel_height_gate_enabled', '_get_vel_orientation_x_gate_enabled',
    '_get_vel_orientation_x_gate_full_deg', '_get_vel_orientation_x_gate_zero_deg',
    '_get_vel_orientation_y_gate_enabled', '_get_vel_orientation_y_gate_full_deg',
    '_get_vel_orientation_y_gate_zero_deg', '_as_reward_gate_tensor',
    '_as_reward_gate_bool_tensor', '_get_wheel_forward_temporal_height_diffs_raw',
    '_get_wheel_forward_stair_temporal_height_diffs_raw', '_get_ctrl_mode_obs_raw',
    '_get_dones', '_apply_termination_duration', '_clear_termination_duration_buffers',
    '_sample_height_command', '_as_env_ids_tensor', '_apply_special_mode_height_ranges',
    '_apply_jump_takeoff_permission_height_range', '_get_jump_takeoff_permission_cfg',
    '_is_jump_takeoff_permission_enabled', '_per_env_max_abs_from_blocks',
)


def registry():
    result = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    supplement = HERE / 'SOURCES_EXTENSION.json'
    if supplement.exists():
        extra = json.loads(supplement.read_text(encoding='utf-8'))
        if extra['commit'] != result['commit'] or set(extra['files']) & set(result['files']):
            raise ValueError('Source supplement must add files at the same fixed commit')
        result['files'].update(extra['files'])
    return result


def source_path(key):
    row = registry()['files'][key]
    # A portable installation can reference an existing archive checkout. No tree copy.
    root = os.environ.get('MOD4_SCUT_SOURCE_ROOT')
    paths = os.environ.get('MOD4_SCUT_SOURCE_PATHS')
    if paths:
        path = Path(json.loads(Path(paths).read_text(encoding='utf-8'))[key])
    else:
        path = Path(root) / row['git_path'] if root else Path(row['path'])
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise ValueError('Pinned source changed: ' + key)
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if blob != row['git_blob']:
        raise ValueError('Pinned Git blob changed: ' + key)
    return path


def load_functions(key, names=None, class_name=None, extra=None):
    path = source_path(key)
    tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    ns = dict(torch=torch, Mapping=Mapping, Sequence=Sequence)
    ns.update({k: getattr(math_ops, k) for k in (
        'wrap_to_pi', 'quat_inv', 'quat_apply', 'quat_apply_inverse',
        'quat_from_euler_xyz', 'euler_xyz_from_quat')})
    ns.update(extra or {})
    if class_name:
        nodes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name]
    else:
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        nodes = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
        if {n.name for n in nodes} != set(names):
            raise ValueError('Missing pinned function: ' + key)
    unit = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *nodes], type_ignores=[])
    ast.fix_missing_locations(unit)
    exec(compile(unit, str(path), 'exec'), ns)
    return ns


def base_functions():
    return load_functions('base_env', BASE_METHODS)


def state_classes():
    base = load_functions('state_base', class_name='StateMachineBase')['StateMachineBase']
    extra = {'WheelbipeStateMachineBase': base}
    classes = {}
    for key, name in [('airborne', 'AirborneStateMachine'),
                      ('jump_takeoff', 'JumpTakeoffStateMachine'),
                      ('step_up', 'StepUpStateMachine'), ('stair', 'StairStateMachine')]:
        classes[key] = load_functions(key, class_name=name, extra=extra)[name]
    manager = load_functions('state_manager', class_name='StateMachineManager')
    classes['manager'] = manager['StateMachineManager']
    return classes


def initialize_buffers(env):
    """Reuse each original state-buffer allocation, excluding the SCUT constructor."""
    path = source_path('base_env')
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    prefixes = ('airborne_', 'jump_takeoff_', 'wheel_forward_', 'height_reward_')
    selected = []
    for node in init.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                and target.value.id == 'self' and target.attr.startswith(prefixes)):
            selected.append(node)
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'),
         dict(torch=torch, self=env))


def bind_base_functions(cls):
    namespace = base_functions()
    for name in BASE_METHODS:
        setattr(cls, name, namespace[name])
    # V14 inherits this synchronization through V13, even when the terrain
    # command manager is disabled on the explicitly authored single course.
    name = '_sync_command_generator_command'
    setattr(cls, name, load_functions('parent_env', [name])[name])
    return cls

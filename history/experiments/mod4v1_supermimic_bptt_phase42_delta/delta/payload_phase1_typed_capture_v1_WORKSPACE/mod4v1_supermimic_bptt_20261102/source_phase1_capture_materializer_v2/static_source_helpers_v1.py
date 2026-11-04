"""17 exact whole original stdlib materializer helpers; never native entrypoints.

Only helper-component derivation, NOT pruning any installed runtime/static tree.
"""
from __future__ import annotations

import argparse

import ast

import builtins

import contextlib

import copy

import hashlib

import io

import importlib.util

import json

import os

from pathlib import Path, PurePosixPath

import re

import runpy

import sys

import time

import traceback

MODEL_SUFFIXES = {'.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.pt2', '.pkl', '.pickle'}

DENIED_SUFFIXES = MODEL_SUFFIXES | {'.pyc', '.pyo', '.partial', '.jsonl', '.log', '.lock'}

DENIED_NAMES = {'model', 'models', 'adaptation', 'production', 'checkpoint', 'checkpoints',
    'kit', 'kit_storage', 'kit_isolation', 'private', 'private_train', 'home', 'tmp',
    'cache', 'caches', '.cache', 'logs', 'log', 'raw', 'reports', 'cases', 'results',
    '__pycache__', '.git', '.pytest_cache', 'deriveddatacache', 'tensorboard', 'wandb'}

POSE_SHA = '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f'

DEPENDENCY_PIN = (22337, 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7')

APP_CLOSE_PIN = (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39')

def need(value, message):
    if not value:
        raise ValueError(message)

def H(raw):
    return hashlib.sha256(raw).hexdigest()

def is_sha(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None

def lexical(path):
    """No resolve/lstat: checkpoint locations here are metadata, not file observations."""
    return Path(os.path.abspath(os.fspath(path)))

def model_path(path):
    return not isinstance(path, int) and Path(os.fspath(path)).suffix.lower() in MODEL_SUFFIXES

def metadata(path, maximum=8 * 1024 * 1024):
    path = Path(path)
    need(path.suffix == '.json' and 'budget' not in path.name.lower(), 'explicit non-budget JSON metadata only')
    with path.open('rb') as stream:
        raw = stream.read(maximum + 1)
    need(len(raw) <= maximum, 'bounded JSON metadata exceeded: ' + path.name)
    value = json.loads(raw)
    need(type(value) is dict, 'metadata object required: ' + path.name)
    return value, raw

def safe_relative(value):
    need(type(value) is str and value and '\\' not in value and ':' not in value,
         'plain relative POSIX installed alias required')
    parts = value.split('/')
    need(not value.startswith('/') and all(p not in ('', '.', '..') for p in parts), 'relative alias escaped root')
    return value

def denied(name):
    lower = name.lower()
    suffix = Path(name).suffix.lower()
    states = {'go_production.json', 'stop_after_save.json', 'final.json', 'task.json',
              'parent_waited_actual.json', 'owner_started.json', 'owner_current.json',
              'owner_exit_actual.json', 'cohort_final.json', 'group_start.json', 'group_abort.json'}
    return (lower in DENIED_NAMES or lower in states or suffix in DENIED_SUFFIXES
            or (suffix != '.py' and ('budget' in lower or lower.startswith(('private_', 'kit_', 'raw_'))
                or '_raw.' in lower or '_skill_raw' in lower)))

def no_links(root, relative):
    cursor = Path(root)
    need(not cursor.is_symlink(), 'symlink root is not static source')
    for part in PurePosixPath(safe_relative(relative)).parts:
        cursor /= part
        need(not cursor.is_symlink(), 'static source symlink is not followed: ' + relative)
    return cursor

def identity(path):
    path = Path(path)
    # Callers reject every RELATIVE tree component before classification. Absolute
    # input ancestors may legitimately be /home or /tmp on Linux.
    need(not denied(path.name), 'denied path must not be stat/read/hashed')
    digest = hashlib.sha256(); size = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk); size += len(chunk)
    return dict(bytes=size, SHA=digest.hexdigest())

def tree(root):
    """Reject names BEFORE DirEntry classification; preserve complete non-denied bytes."""
    root = Path(root)
    need(not root.is_symlink() and root.is_dir(), 'explicit static tree missing or symlinked')
    result = {}
    def visit(directory, prefix):
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda e: e.name):
                if denied(entry.name):
                    continue
                need(not entry.is_symlink(), 'static symlink is not followed: ' + entry.name)
                rel = (prefix / entry.name).as_posix()
                if entry.is_dir(follow_symlinks=False):
                    visit(Path(entry.path), prefix / entry.name)
                elif entry.is_file(follow_symlinks=False):
                    result[rel] = (Path(entry.path), identity(Path(entry.path)))
                else:
                    raise ValueError('special static file: ' + entry.name)
    visit(root, PurePosixPath())
    return result

def digest_tree(items):
    rows = [dict(relative=rel, **info) for rel, (_, info) in sorted(items.items())]
    return dict(files=len(rows), SHA=H(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()))

def semantic_success(row):
    semantic = row.get('semantic_result')
    need(row.get('phase') == 'terminal' and row.get('terminal_all_own_children_waited') is True
         and type(row.get('returncode')) is int and row['returncode'] == 0
         and row.get('original_error') is False, 'original actual-wait terminal row failed')
    need(type(semantic) is dict and semantic.get('kind') == 'ACTUAL_WAIT_APP_CLOSE_SEMANTIC_RESULT_V5'
         and semantic.get('passed_execution') is True
         and semantic.get('original_error') is False and semantic.get('actual_wait_returned') is True
         and type(semantic.get('returncode')) is int and semantic['returncode'] == 0
         and semantic.get('reasons') == [] and semantic.get('error_sidefiles') == [], 'original waited semantic failed')
    return semantic

def paired_plan():
    protocol = dict(pose_source_SHA=POSE_SHA, pose_source_bytes=18161,
        pose_source_version='POSE_CACHE_RUNTIME_ADAPTER_V4_NATIVE_NEGATIVE_INFINITY_STALE_V1',
        install_timing='after_env_construction_before_original_single_explicit_reset', seed=20260928, num_envs=80,
        explicit_original_reset_count=1, physics_dt=.0025, control_dt=.02, feedback_hz=100,
        actor_observation='original_noisy_delayed_policy35')
    return dict(kind='PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2', reference_planned_protocol=dict(protocol),
        candidate_planned_protocol=dict(protocol), historical_bug_baseline_reused=False, reference_actual_receipt=None)

def verify_close_dependency_imports(app_source, base_source):
    """Real full-module imports, no stubs or SDK instance/close calls."""
    app_source, base_source = Path(app_source), Path(base_source)
    receipts = {}
    for label, path, pin, extra in (
        ('contracts', base_source, DEPENDENCY_PIN, set()),
        ('AppV6', app_source, APP_CLOSE_PIN, {'resume_runtime_contracts_v3'})):
        raw = path.read_bytes()
        need((len(raw), H(raw)) == pin, 'close dependency source pin differs: ' + label)
        parsed = ast.parse(raw)
        roots = set()
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import): roots.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module: roots.add(node.module.split('.')[0])
        need(roots <= set(sys.stdlib_module_names) | {'__future__'} | extra,
             'unexpected non-stdlib close dependency import: ' + label)
        receipts[label] = dict(path=str(path), bytes=len(raw), SHA256=H(raw), import_roots=sorted(roots),
                               full_original_module=True, AST_cropped_or_stubbed=False)
    names = ('app_close_semantics_v5', 'resume_runtime_contracts_v3')
    before = {name: sys.modules.get(name) for name in names}
    try:
        for name in names: sys.modules.pop(name, None)
        base_spec = importlib.util.find_spec('resume_runtime_contracts_v3')
        need(base_spec is not None and Path(base_spec.origin).resolve() == base_source.resolve(),
             'real base dependency must resolve in the actual source/stage root')
        base = importlib.import_module('resume_runtime_contracts_v3')
        need(Path(base.__file__).resolve() == base_source.resolve(), 'actual contracts import origin differs')
        app_spec = importlib.util.spec_from_file_location('app_close_semantics_v5', app_source)
        app = importlib.util.module_from_spec(app_spec)
        sys.modules['app_close_semantics_v5'] = app
        app_spec.loader.exec_module(app)  # Entire unchanged helper, including its real import at line 23.
        need(app._base is base and base.FINAL_KIND == 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
             and callable(base.evaluate_waited_worker), 'helper must bind real complete contracts module')
        need(app.SOURCE_CODE_VERSION == 'V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES', 'actual AppV6 version differs')
        need(not any(name in sys.modules for name in ('torch', 'isaacsim', 'omni')), 'dependency check imported native package')
        return dict(kind='REAL_COMPLETE_APP_V6_CONTRACTS_IMPORT_CHECK_V2', passed=True,
                    modules=receipts, helper_base_is_actual_imported_contracts=True,
                    model_C_lock_SDK_GPU_operations=0, actual_SimulationApp_binding=None,
                    actual_close_or_wait_performed=False)
    finally:
        for name, old in before.items():
            if old is None: sys.modules.pop(name, None)
            else: sys.modules[name] = old

def put_once(path, raw):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())

def put_json(path, value):
    put_once(path, (json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


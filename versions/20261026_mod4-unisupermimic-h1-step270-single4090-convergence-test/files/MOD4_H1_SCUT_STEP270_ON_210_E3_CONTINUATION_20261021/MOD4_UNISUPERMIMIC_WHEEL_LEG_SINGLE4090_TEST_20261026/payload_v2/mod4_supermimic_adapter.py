"""Small explicit underactuated MOD4 adapter around pinned upstream tensor kernels.

No simulator, production policy or upstream G1 environment is substituted here.
"""
from pathlib import Path
import importlib
import sys
import types

def load_core(root):
    source = Path(root) / 'upstream/src'
    # Import only tensor kernels, not upstream's eager learner/UniLab package initializer.
    for suffix in ('', '.rl', '.rl.contracts', '.rl.algos', '.rl.algos.supermimic'):
        name = 'unisupermimic' + suffix
        if name not in sys.modules:
            m = types.ModuleType(name)
            m.__path__ = [str(source.joinpath(*name.split('.')))]
            sys.modules[name] = m
    geometry = importlib.import_module('unisupermimic.rl.algos.supermimic.geometry')
    networks = importlib.import_module('unisupermimic.rl.algos.supermimic.networks')
    return geometry, networks

def make_world_model(networks, hidden=(2048, 2048, 2048), joints=30, actions=6, context=49):
    import torch.nn as nn
    model = networks.WorldModel(hidden=hidden, num_joints=joints, context_dim=context)
    if actions != joints:
        # Upstream assumes one action per joint. Retain all30 joint states and72 targets.
        model.in_dim = 13 + 2 * joints + actions + context
        model.net[0] = nn.Linear(model.in_dim, hidden[0])
        model.in_norm = networks.RunningNorm(model.in_dim)
    model.action_dim = actions
    return model

ACTION_ORDER = ['left_crank', 'left_hip', 'right_crank', 'right_hip', 'left_wheel_spin', 'right_wheel_spin']

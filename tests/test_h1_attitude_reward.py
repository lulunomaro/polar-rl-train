import importlib.util
from pathlib import Path
import sys
import types

import torch

spec = importlib.util.spec_from_file_location('h1_attitude_reward', Path(__file__).parents[1]/'project/train/h1_attitude_reward.py')
reward = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward)


def test_known_reference_angles_and_frame_invariance():
    theta = torch.tensor([0., .2, .55, torch.pi], dtype=torch.float64)
    c, s, z, one = theta.cos(), theta.sin(), torch.zeros_like(theta), torch.ones_like(theta)
    rotations = torch.stack((c, -s, z, s, c, z, z, z, one), -1).reshape(-1, 3, 3)
    reference = torch.eye(3, dtype=torch.float64).expand_as(rotations)
    expected = (theta/.2).square()
    assert torch.allclose(reward.normalized_attitude_cost(rotations, reference), expected, atol=1e-10)
    frame = rotations[2]
    assert torch.allclose(reward.normalized_attitude_cost(frame@rotations, frame@reference), expected, atol=1e-10)


def test_wrapper_replaces_only_the_rotation_term(monkeypatch):
    original = types.ModuleType('tracking_reference389')
    original.tracking_cost389 = lambda *args: (torch.tensor([3.]), dict(rotation=torch.tensor([.1]), position=torch.tensor([2.])))
    monkeypatch.setitem(sys.modules, original.__name__, original)
    rotation = torch.eye(3)[None]
    label = {'state': torch.zeros(1, 78)}
    label['state'][:, 3:12] = rotation.flatten(1)
    cost, terms = reward.tracking_cost_attitude((None, rotation), label, [], [], None, None)
    assert torch.allclose(cost, torch.tensor([2.95]))
    assert terms['position'].item() == 2.
    assert terms['rotation'].item() == 0.

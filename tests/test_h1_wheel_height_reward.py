import importlib.util
from pathlib import Path
import types

import torch

spec = importlib.util.spec_from_file_location('h1_wheel_height_reward', Path(__file__).parents[1]/'project/train/h1_wheel_height_reward.py')
reward = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward)


def test_world_height_deficit_and_reference_shift():
    reference = torch.tensor([[.37, .38], [.0637, .0637]], dtype=torch.float64)
    assert torch.equal(reward.normalized_wheel_height_cost(reference, reference), torch.zeros(2))
    actual = reference-torch.tensor([[.05, .10], [0., .05]], dtype=torch.float64)
    expected = torch.tensor([2.5, .5], dtype=torch.float64)
    assert torch.allclose(reward.normalized_wheel_height_cost(actual, reference), expected)
    assert torch.allclose(reward.normalized_wheel_height_cost(actual+3., reference+3.), expected)


def test_addition_preserves_attitude_and_other_terms(monkeypatch):
    attitude = types.ModuleType('h1_attitude_reward')
    attitude.tracking_cost_attitude = lambda *args: (torch.tensor([3.]), dict(rotation=torch.tensor([7.]), position=torch.tensor([2.])))
    monkeypatch.setitem(__import__('sys').modules, attitude.__name__, attitude)
    label = dict(wheel_world=torch.tensor([[[0., 0., .37], [0., 0., .38]]]))
    cost, terms = reward.tracking_cost_wheel_height(None, label, [], [], None, None,
                                                  wheel_height=torch.tensor([[.32, .33]]))
    assert torch.allclose(cost, torch.tensor([4.]))
    assert terms['rotation'].item() == 7. and terms['position'].item() == 2.
    assert torch.allclose(terms['wheel_world_height'], torch.tensor([1.]))

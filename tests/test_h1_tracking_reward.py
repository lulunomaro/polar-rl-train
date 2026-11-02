import importlib.util
from pathlib import Path

import torch

spec = importlib.util.spec_from_file_location(
    'h1_tracking_reward', Path(__file__).parents[1]/'project/train/h1_tracking_reward.py')
reward = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward)


def test_reward_order_optimum_and_small_error_slope():
    cost = torch.tensor([0., 1e-5, 5., 25., 100.], dtype=torch.float64)
    value = reward.tracking_reward(cost)
    assert value[0] == 1.
    assert torch.all((value > 0.) & (value <= 1.))
    assert torch.all(value[:-1] > value[1:])
    assert torch.allclose(value[[2, 3]], torch.tensor([.5, 1./6], dtype=value.dtype))
    assert abs(float((value[1]-value[0])/1e-5)+.2) < 1e-6


def test_height_improvement_remains_visible_at_saved_large_error():
    # Actual467 env0,4s: unchanged base14.1814,height29.0417. Raising both
    # wheel centers10mm reduces height cost by about2.1159. This is a local
    # counterfactual reward check, not a physically achieved improvement.
    cost = torch.tensor([43.223098902057885, 41.1072012671761], dtype=torch.float64)
    actual_delta = reward.tracking_reward(cost)[1]-reward.tracking_reward(cost)[0]
    exponential_delta = torch.exp(-cost[1]/5.)-torch.exp(-cost[0]/5.)
    assert actual_delta > 40*exponential_delta
    assert actual_delta > .004

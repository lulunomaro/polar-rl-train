import importlib.util
from pathlib import Path
import sys
import types

import torch

spec=importlib.util.spec_from_file_location('h1_target_limit_reward',
    Path(__file__).parents[1]/'project/train/h1_target_limit_reward.py')
reward=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward)


def test_joint_limits_scale_and_feasible_targets():
    targets=torch.tensor([[-1.2,-.5,.9,.5],[-1.4,-.6,1.0,.8]],dtype=torch.float64)
    assert torch.allclose(reward.normalized_leg_target_limit_cost(targets),
                          torch.tensor([0.,3.75],dtype=torch.float64))
    assert reward.normalized_leg_target_limit_cost(torch.zeros(1,4)).item()==0.


def test_wrapper_retains_previous_costs_and_does_not_modify_targets(monkeypatch):
    prior=types.ModuleType('h1_tight_attitude_reward')
    wheel=torch.zeros(1,2,3)
    def previous(*args,wheel_position):
        assert wheel_position is wheel
        return torch.tensor([4.]),dict(rotation=torch.tensor([3.]),overflow=torch.zeros(1))
    prior.tracking_cost_tight_attitude=previous
    monkeypatch.setitem(sys.modules,prior.__name__,prior)
    target=torch.tensor([[0.,.5,0.,.7]])
    original=target.clone()
    cost,terms=reward.tracking_cost_target_limit(None,None,[],[],None,None,
                                               wheel_position=wheel,leg_target=target)
    assert torch.allclose(cost,torch.tensor([5.]))
    assert torch.allclose(terms['leg_target_limit'],torch.ones(1))
    assert terms['rotation']==3. and terms['overflow']==0.
    assert torch.equal(target,original)

import importlib.util
from pathlib import Path
import sys
import types

import torch

spec=importlib.util.spec_from_file_location('h1_tight_attitude_reward',
    Path(__file__).parents[1]/'project/train/h1_tight_attitude_reward.py')
reward=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward)


def test_tighter_scale_preserves_other_costs_and_wheel_measurement(monkeypatch):
    previous=types.ModuleType('h1_wheel_position_reward')
    wheel=torch.tensor([[[.3,.1,.07],[.3,-.1,.08]]])
    def cost(*args,wheel_position):
        assert wheel_position is wheel
        return torch.tensor([8.]),dict(rotation=torch.tensor([4.]),
                                      wheel_world_planar=torch.tensor([3.]),
                                      wheel_world_height=torch.tensor([1.]))
    previous.tracking_cost_wheel_position=cost
    monkeypatch.setitem(sys.modules,previous.__name__,previous)
    result,terms=reward.tracking_cost_tight_attitude(None,None,[],[],None,None,wheel_position=wheel)
    assert torch.equal(result,torch.tensor([14.]))
    assert terms['rotation']==16.
    assert terms['wheel_world_planar']==3. and terms['wheel_world_height']==1.


def test_reference_attitude_zero_cost_is_preserved(monkeypatch):
    previous=types.ModuleType('h1_wheel_position_reward')
    previous.tracking_cost_wheel_position=lambda *a,**k:(torch.tensor([2.]),dict(rotation=torch.zeros(1)))
    monkeypatch.setitem(sys.modules,previous.__name__,previous)
    result,terms=reward.tracking_cost_tight_attitude(None,None,[],[],None,None,wheel_position=None)
    assert result==2. and terms['rotation']==0.

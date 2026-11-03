import importlib.util
from pathlib import Path
import sys
import types

import torch

spec=importlib.util.spec_from_file_location('h1_wheel_position_reward',
    Path(__file__).parents[1]/'project/train/h1_wheel_position_reward.py')
reward=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward)


def test_planar_tracking_scale_and_common_frame_invariance():
    reference=torch.tensor([[[.8,.2,.37],[.8,-.2,.38]]],dtype=torch.float64)
    actual=reference-torch.tensor([[[.1,0.,0.],[.2,.1,0.]]],dtype=torch.float64)
    expected=torch.tensor([3.],dtype=torch.float64)
    assert torch.allclose(reward.normalized_wheel_planar_cost(actual,reference),expected)
    shift=torch.tensor([9.,-7.,4.],dtype=torch.float64)
    assert torch.allclose(reward.normalized_wheel_planar_cost(actual+shift,reference+shift),expected)
    angle=torch.tensor(.7,dtype=torch.float64)
    rot=torch.tensor([[angle.cos(),-angle.sin(),0.],[angle.sin(),angle.cos(),0.],[0.,0.,1.]],dtype=torch.float64)
    assert torch.allclose(reward.normalized_wheel_planar_cost(actual@rot.T,reference@rot.T),expected)
    assert torch.equal(reward.normalized_wheel_planar_cost(reference,reference),torch.zeros(1))


def test_height_and_existing_cost_terms_are_preserved(monkeypatch):
    module=types.ModuleType('h1_wheel_height_reward')
    def previous(*args,wheel_height):
        assert torch.allclose(wheel_height,torch.tensor([[.32,.33]]))
        return torch.tensor([4.]),dict(rotation=torch.tensor([7.]),wheel_world_height=torch.tensor([1.]))
    module.tracking_cost_wheel_height=previous
    monkeypatch.setitem(sys.modules,module.__name__,module)
    label=dict(wheel_world=torch.tensor([[[.8,.2,.37],[.8,-.2,.38]]]))
    actual=torch.tensor([[[.7,.2,.32],[.7,-.2,.33]]])
    cost,terms=reward.tracking_cost_wheel_position(None,label,[],[],None,None,wheel_position=actual)
    assert torch.allclose(cost,torch.tensor([5.]))
    assert terms['rotation']==7. and terms['wheel_world_height']==1.
    assert torch.allclose(terms['wheel_world_planar'],torch.tensor([1.]))

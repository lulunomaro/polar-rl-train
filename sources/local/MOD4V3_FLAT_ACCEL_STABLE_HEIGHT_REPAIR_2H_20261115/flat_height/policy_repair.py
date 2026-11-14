"""Bound exploration around the retained parent and recalibrate the new value head."""
import torch

INITIAL_STD = [.035, .035, .035, .035, .08, .08]
MIN_STD = [.015, .015, .015, .015, .03, .03]
MAX_STD = [.06, .06, .06, .06, .15, .15]


def clear_moments(optimizer, parameter, mask=None):
    for name, value in optimizer.state.get(parameter, {}).items():
        if not torch.is_tensor(value):
            continue
        if mask is None:
            value.zero_()
        elif value.shape == parameter.shape:
            value[mask] = 0.


def initialize(algorithm):
    actor_before = {k: v.clone() for k, v in algorithm.actor.state_dict().items() if k.startswith('mlp.')}
    std = algorithm.actor.distribution.std_param
    std_before = std.detach().clone()
    with torch.no_grad():
        std.copy_(std.new_tensor(INITIAL_STD))
        clear_moments(algorithm.optimizer, std)
        head = algorithm.critic.mlp[-1]
        for parameter in (head.weight, head.bias):
            parameter.zero_()
            clear_moments(algorithm.optimizer, parameter)
    assert all(torch.equal(v, algorithm.actor.state_dict()[k]) for k, v in actor_before.items())
    return dict(full_parent_loaded_before_repair=True, actor_MLP_retained_exactly=True,
                STD_before=std_before.tolist(), STD_initial=std.tolist(),
                STD_min=MIN_STD, STD_max=MAX_STD, critic_output_reset=True,
                matching_STD_and_value_head_Adam_state_reset=True)


def bound_exploration(algorithm):
    std = algorithm.actor.distribution.std_param
    assert bool(torch.isfinite(std).all()), 'Nonfinite exploration STD'
    with torch.no_grad():
        before = std.clone()
        std.copy_(torch.maximum(std.new_tensor(MIN_STD), torch.minimum(std, std.new_tensor(MAX_STD))))
        clear_moments(algorithm.optimizer, std, before != std)
    return std.detach().tolist()


def in_bounds(std):
    return bool(torch.isfinite(std).all() and (std >= std.new_tensor(MIN_STD)).all()
                and (std <= std.new_tensor(MAX_STD)).all())

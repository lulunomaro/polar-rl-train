"""Regression: the command visible to PPO must retain the post-physics run brake taper."""
import os
from types import SimpleNamespace
from unittest.mock import patch

import torch

from repair_step import RepairStepMixin


class _Scene(dict):
    pass


class _Env(RepairStepMixin):
    def _repair_apply(self, names):
        pass


def test_every_step_reference_preserves_braking_and_stand_zero():
    env = _Env()
    env.num_envs = 4
    env.device = "cpu"
    env.scene = _Scene()
    env.scene.env_origins = torch.zeros(4, 3)
    env.scene["robot"] = SimpleNamespace(data=SimpleNamespace(
        root_pos_w=torch.tensor([[1.5, 0., 0.], [2.7, 0., 0.],
                                 [3.15, 0., 0.], [1.5, 0., 0.]]),
        root_quat_w=torch.tensor([[0., 0., 0., 1.]]).repeat(4, 1)))
    env._mod4_routes = SimpleNamespace(
        ids=torch.zeros(4, dtype=torch.long), goals=torch.tensor([[3.5, 0., 0.]]),
        speed=torch.ones(4), spin_speed=torch.zeros(4),
        route_kinds=torch.tensor([0]), kind_ids={"run": 0, "slope_spin": 1,
                                                "jump_in_place": 2},
        finished=torch.zeros(4, dtype=torch.bool))
    env._mod4_route_ready = True
    env._mod4_run_stand = torch.tensor([False, False, False, True])
    term = SimpleNamespace(command=torch.zeros(4, 3), time_left=torch.zeros(4),
                           is_standing_env=torch.zeros(4, dtype=torch.bool))
    env.command_manager = SimpleNamespace(get_term=lambda name: term)
    with patch.dict(os.environ, {"RM_RUN_BRAKE_GATE": "1", "RM_RUN_BRAKE_DIST_M": "0.9",
                                 "RM_RUN_GOAL_RADIUS_M": "0.35"}):
        for _ in range(2):
            # Simulate command_manager's full-speed publication before the custom publisher.
            term.command[:, 0] = 1.0
            env._repair_publish_reference()
            torch.testing.assert_close(term.command[:, 0], torch.tensor([1., .5, 0., 0.]),
                                       atol=1e-6, rtol=0)
            torch.testing.assert_close(term.command[:, 1:], torch.zeros(4, 2))


def test_taper_is_zero_at_goal_and_bounded_outside_brake_zone():
    from route_isaac import _run_brake_scale
    torch.testing.assert_close(_run_brake_scale(torch.tensor([.35, .8, 2.0]), .35, .9),
                               torch.tensor([0., .5, 1.]), atol=1e-6, rtol=0)

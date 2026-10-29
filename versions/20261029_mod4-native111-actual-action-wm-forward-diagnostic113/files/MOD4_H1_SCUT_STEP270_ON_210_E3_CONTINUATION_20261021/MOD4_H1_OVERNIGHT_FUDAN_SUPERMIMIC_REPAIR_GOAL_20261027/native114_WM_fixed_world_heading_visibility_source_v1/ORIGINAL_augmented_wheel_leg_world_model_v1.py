"""Source-only wheel-leg state extension for the pinned SuperMimic BPTT loop.

The first six State components and their SE(3) integration match the frozen
vendor implementation. The seventh is dynamic auxiliary state, never static xi.
This module does not load checkpoints, start simulation or admit a Task.
"""
from __future__ import annotations
from dataclasses import dataclass
import torch
from torch import nn
from supermimic_wheel_leg_v3.geometry import (
    invariant_features, mat_to_quat, quat_to_mat, yaw_mat, so3_exp,
)
from supermimic_wheel_leg_v3.networks import (
    WorldModel as OriginalWorldModel, RunningNorm, mlp, run_mlp,
)

@dataclass(frozen=True)
class WheelLegStateLayout:
    num_joints: int = 30
    auxiliary_dim: int = 54

    @property
    def packed_dim(self):
        return 13 + 2*self.num_joints + self.auxiliary_dim

    def unpack(self, value):
        if value.shape[-1] != self.packed_dim:
            raise ValueError(f"Expected explicit packed state width {self.packed_dim}, got {value.shape}")
        j = self.num_joints
        return (
            value[..., :3], quat_to_mat(value[..., 3:7]),
            value[..., 7:10], value[..., 10:13],
            value[..., 13:13+j], value[..., 13+j:13+2*j],
            value[..., 13+2*j:],
        )

    def pack(self, state):
        self.validate(state)
        p, R, v, w, q, dq, aux = state
        return torch.cat((p, mat_to_quat(R), v, w, q, dq, aux), -1)

    def validate(self, state):
        if len(state) != 7:
            raise ValueError("Wheel-leg state requires six physical components plus explicit auxiliary")
        batch = state[0].shape[:-1]
        expected = ((3,), (3,3), (3,), (3,), (self.num_joints,),
                    (self.num_joints,), (self.auxiliary_dim,))
        for i, (value, tail) in enumerate(zip(state, expected)):
            if value.shape != (*batch, *tail):
                raise ValueError(f"state component {i} has wrong shape {value.shape}")
            if value.dtype != state[0].dtype or value.device != state[0].device:
                raise ValueError("State component dtype/device mismatch")

    @staticmethod
    def stack(states, dim=0):
        return tuple(torch.stack([s[i] for s in states], dim) for i in range(7))


class AugmentedWheelLegWorldModel(nn.Module):
    """Predict original rigid-body increments and dynamic-aux increments together.

    Episode-fixed xi is a separate input. Terrain-relative coordinates prevent
    the old world-XY alias for a task with a fixed obstacle. No auxiliary variable
    is presented as a joint angle or silently kept constant through imagination.
    """
    def __init__(self, *, context_dim, hidden=(2048,2048,2048),
                 num_joints=30, auxiliary_dim=54, action_dim=6,
                 edge_x_m=.35, platform_top_z_m=.27):
        super().__init__()
        self.layout = WheelLegStateLayout(num_joints, auxiliary_dim)
        self.num_joints, self.context_dim = num_joints, context_dim
        self.action_dim = action_dim
        self.edge_x_m = float(edge_x_m)
        self.platform_top_z_m = float(platform_top_z_m)
        self.in_dim = 13+2*num_joints+auxiliary_dim+action_dim+context_dim+3
        self.out_dim = 12+2*num_joints+auxiliary_dim
        self.net = mlp(self.in_dim, hidden, self.out_dim,
                       act=nn.SiLU, layer_norm=True)
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)
        self.in_norm = RunningNorm(self.in_dim)
        self.out_norm = RunningNorm(self.out_dim, eps=1e-4)

    def terrain_relative(self, state):
        p = state[0]
        return torch.stack((self.edge_x_m-p[...,0], -p[...,1],
                            self.platform_top_z_m-p[...,2]), -1)

    def inputs(self, state, action, normalized_context):
        self.layout.validate(state)
        shape = state[0].shape[:-1]
        if action.shape != (*shape, self.action_dim):
            raise ValueError("Action width/batch differs from explicit six-actuator contract")
        if normalized_context.shape != (*shape, self.context_dim):
            raise ValueError("Static context width/batch differs from declared schema")
        return torch.cat((invariant_features(state[:6]), state[6],
                          action, normalized_context, self.terrain_relative(state)), -1)

    @staticmethod
    def targets(state, next_state):
        return torch.cat((OriginalWorldModel.targets(state[:6], next_state[:6]),
                          next_state[6]-state[6]), -1)

    @staticmethod
    def state_error(predicted_state, true_state):
        return torch.cat((OriginalWorldModel.state_error(predicted_state[:6], true_state[:6]),
                          predicted_state[6]-true_state[6]), -1)

    def step(self, state, action, normalized_context):
        p, R, v, w, q, dq, aux = state
        prediction = run_mlp(self.net, self.in_norm(self.inputs(state, action, normalized_context)))
        inc = prediction*self.out_norm.std()+self.out_norm.mean
        dp, dR, dv, dw, d_q, d_dq, d_aux = inc.split(
            (3,3,3,3,self.num_joints,self.num_joints,self.layout.auxiliary_dim), -1)
        heading = yaw_mat(R)
        return (
            p+(heading@dp.unsqueeze(-1)).squeeze(-1),
            R@so3_exp(dR),
            v+(R@dv.unsqueeze(-1)).squeeze(-1),
            w+(R@dw.unsqueeze(-1)).squeeze(-1),
            q+d_q, dq+d_dq, aux+d_aux,
        )


def require_architecture_source_migration(checkpoint_contract, current_contract):
    """Reject a legacy128/xi49 checkpoint being called an exact same-source resume."""
    if checkpoint_contract != current_contract:
        raise ValueError("Explicit architecture/source migration required; legacy parameters are not shape-compatible continuation")


def learner_error_floor(layout):
    # Same units/floors for original body and joint components. Aux normalized
    # labels use their own unit scale; a concrete runtime schema must pin it.
    return torch.cat((torch.full((3,),3e-3), torch.full((3,),5e-3),
                      torch.full((3,),2e-2), torch.full((3,),5e-2),
                      torch.full((layout.num_joints,),3e-3),
                      torch.full((layout.num_joints,),5e-2),
                      torch.full((layout.auxiliary_dim,),1e-3)))


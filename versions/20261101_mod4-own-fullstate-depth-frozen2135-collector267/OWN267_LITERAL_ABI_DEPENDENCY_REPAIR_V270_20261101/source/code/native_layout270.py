"""Unchanged native layout class only; no unused network/goal imports."""
from dataclasses import dataclass
import torch
from supermimic_wheel_leg_v3.geometry import quat_to_mat,mat_to_quat
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

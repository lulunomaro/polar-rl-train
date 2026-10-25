"""New task action layers; retains fixed upstream adaln output interface."""
from __future__ import annotations
import torch
from torch import nn


class MoETemporalActionEncoder(nn.Module):
    def __init__(self, conditioning_dim, *, physics_ticks_per_frame, mode, mean, scale,
                 hidden=128, frame_width=64):
        super().__init__()
        self.dim = int(conditioning_dim)
        self.mode = mode
        self.ticks = int(physics_ticks_per_frame)
        self.channels = {"command_route": 9, "applied_diagnostic": 16}[mode]
        if self.ticks not in (20, 100) or self.dim <= 0:
            raise ValueError("explicit PhysX20/MuJoCo100 tick geometry and target encoder width required")
        center = torch.as_tensor(mean, dtype=torch.float32, device="cpu")
        divisor = torch.as_tensor(scale, dtype=torch.float32, device="cpu")
        if center.shape != (self.channels,) or divisor.shape != center.shape or not bool(torch.isfinite(center).all()) or not bool(torch.isfinite(divisor).all()) or not bool((divisor > 0).all()):
            raise ValueError("train-only stats must match declared feature semantics")
        self.register_buffer("center", center)
        self.register_buffer("divisor", divisor)
        phase = torch.arange(self.ticks, dtype=torch.float32) / self.ticks
        self.register_buffer("phase", torch.stack((phase, phase + 1 / self.ticks), -1))
        self.temporal = nn.Sequential(nn.Linear(self.ticks * (self.channels + 3), hidden), nn.GELU(), nn.Linear(hidden, frame_width))
        self.context = nn.Sequential(nn.Linear(frame_width, self.dim), nn.GELU(), nn.Linear(self.dim, self.dim))
        self.modulation = nn.Sequential(nn.Linear(4 * frame_width, hidden), nn.SiLU(), nn.Linear(hidden, self.dim))

    def _encode(self, action):
        if action.ndim != 4 or action.shape[-2:] != (self.ticks, self.channels + 1) or action.shape[1] < 5 or action.shape[1] % 4 != 1:
            raise ValueError("backend/mode tensor geometry mismatch; never truncate/resample across backends")
        if not bool(torch.isfinite(action).all()):
            raise ValueError("nonfinite action/plan")
        mask = action[..., -1:]
        if bool(mask[:, 0].any()) or not bool((mask[:, 1:] == 1).all()) or bool((action[:, 0] != 0).any()):
            raise ValueError("strict no-action anchor and complete future physics coverage required")
        x = ((action[..., :-1] - self.center) / self.divisor) * mask
        phase = self.phase.to(dtype=action.dtype).expand(*action.shape[:2], self.ticks, 2) * mask
        frame = self.temporal(torch.cat((x, phase, mask), -1).flatten(-2))
        return frame * mask.any(dim=-2).to(frame.dtype)

    def forward(self, action):
        return self.context(self._encode(action))

    def encode_ti2v2(self, action):
        frame = self._encode(action)
        grouped = torch.cat((frame[:, :1].expand(-1, 3, -1), frame), 1)
        grouped = grouped.reshape(frame.shape[0], (frame.shape[1] + 3) // 4, -1)
        return self.context(frame), self.modulation(grouped)

    def load_state_dict(self, state_dict, strict=True, assign=False):
        if any("action_mlp" in key or "action_embedding" in key for key in state_dict):
            raise ValueError("OLD_MANIPULATION_ACTION_WEIGHTS_FORBIDDEN")
        if not strict:
            raise ValueError("MoE adapter resume requires strict architecture/stat matching")
        return super().load_state_dict(state_dict, strict=True, assign=assign)


def install_moe_action_encoder(pipe, *, ticks, mode, mean, scale):
    if getattr(pipe, "action_injection_mode", "adaln") != "adaln":
        raise ValueError("only audited adaln path supported")
    old = pipe.action_encoder
    width = int(old.action_mlp1[0].out_features)
    reference = next(old.parameters())
    new = MoETemporalActionEncoder(width, physics_ticks_per_frame=ticks, mode=mode, mean=mean, scale=scale)
    pipe.action_encoder = new.to(device=reference.device, dtype=reference.dtype)
    return {"conditioning_dim_from_old_encoder": width, "physics_ticks_per_frame": ticks,
            "mode": mode, "old_action_weights_loaded": False, "new_layers_initialized": True}

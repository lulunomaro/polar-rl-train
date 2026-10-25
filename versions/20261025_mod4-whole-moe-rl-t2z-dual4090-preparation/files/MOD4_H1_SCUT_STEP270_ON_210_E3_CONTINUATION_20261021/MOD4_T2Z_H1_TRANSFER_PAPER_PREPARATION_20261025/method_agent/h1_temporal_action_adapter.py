"""Proposed new H1 action encoder, CPU-testable without Wan or pretrained files.

Replace the *whole* old WanVideoActionEncoder for action_mode='adaln'.
Bypass upstream LoadCobotAction and pass [B,T,20,7], never padded 14D arms.
This preserves the encode_ti2v2 output shapes, not the old action semantics.
"""
from __future__ import annotations

import torch
from torch import nn


class H1TemporalActionEncoder(nn.Module):
    def __init__(self, conditioning_dim: int, train_mean6, train_std6,
                 frame_width: int = 128, hidden_width: int = 256):
        super().__init__()
        if conditioning_dim <= 0:
            raise ValueError("conditioning_dim must be read from the target Wan action encoder")
        mean = torch.as_tensor(train_mean6, dtype=torch.float32, device="cpu")
        std = torch.as_tensor(train_std6, dtype=torch.float32, device="cpu")
        if mean.shape != (6,) or std.shape != (6,) or not bool(torch.isfinite(mean).all()) or not bool(torch.isfinite(std).all()) or not bool((std > 0).all()):
            raise ValueError("six finite train-only means and positive scales required")
        self.action_dim, self.dim, self.frame_width = 6, conditioning_dim, frame_width
        self.register_buffer("train_mean6", mean)
        self.register_buffer("train_std6", std)
        starts = torch.arange(20, dtype=torch.float32) / 20.0
        self.register_buffer("relative_time", torch.stack((starts, starts + 1.0 / 20), -1))
        # Ordered flattening retains all 20 physics targets and their validity.
        # 6 normalized targets + 2 relative time boundaries + 1 validity bit.
        self.temporal = nn.Sequential(nn.Linear(20 * 9, hidden_width), nn.GELU(),
                                      nn.Linear(hidden_width, frame_width))
        self.context = nn.Sequential(nn.Linear(frame_width, conditioning_dim), nn.GELU(),
                                     nn.Linear(conditioning_dim, conditioning_dim))
        self.modulation = nn.Sequential(nn.Linear(4 * frame_width, hidden_width), nn.SiLU(),
                                        nn.Linear(hidden_width, conditioning_dim))

    def _frame_features(self, action):
        if action.ndim != 4 or tuple(action.shape[-2:]) != (20, 7) or action.shape[1] < 5 or action.shape[1] % 4 != 1:
            raise ValueError("H1 action must be [B,4k+1,20,7], k>=1")
        if not bool(torch.isfinite(action).all()):
            raise ValueError("nonfinite action input")
        valid = action[..., 6:7]
        if not bool(((valid == 0) | (valid == 1)).all()):
            raise ValueError("mask must be binary")
        if bool(valid[:, 0].any()) or not bool(valid[:, 1:].all()):
            raise ValueError("first frame is no-action anchor; all future physics ticks must be present")
        if bool((action[:, 0, :, :6] != 0).any()):
            raise ValueError("no previous/future action may be copied into the initial observation anchor")
        target = (action[..., :6] - self.train_mean6) / self.train_std6
        target = target * valid
        timing = self.relative_time.to(dtype=action.dtype).expand(*action.shape[:2], 20, 2) * valid
        features = torch.cat((target, timing, valid), -1).flatten(-2)
        encoded = self.temporal(features)
        # Explicit zero anchor; learned bias must not create an initial action.
        return encoded * valid.any(dim=-2).to(dtype=encoded.dtype)

    def forward(self, action):
        return self.context(self._frame_features(action))

    def encode_ti2v2(self, action):
        frame = self._frame_features(action)
        context = self.context(frame)
        # Mirror upstream causal VAE alignment: one anchor latent, then four
        # intervals per latent. One future latent = 80 physics ticks = 200ms.
        padded = torch.cat((frame[:, :1].expand(-1, 3, -1), frame), dim=1)
        grouped = padded.reshape(frame.shape[0], (frame.shape[1] + 3) // 4,
                                 4 * self.frame_width)
        return context, self.modulation(grouped)


def replace_action_encoder(pipe, train_mean6, train_std6):
    """Explicit integration helper; caller must audit loader and checkpoint keys.

    Read width/device/dtype from the actual old module. Every new action layer
    is newly initialized. No old 14D action state_dict is loaded into it.
    """
    old = pipe.action_encoder
    width = old.action_mlp1[0].out_features
    reference = next(old.parameters())
    new = H1TemporalActionEncoder(width, train_mean6, train_std6)
    pipe.action_encoder = new.to(device=reference.device, dtype=reference.dtype)
    return pipe.action_encoder

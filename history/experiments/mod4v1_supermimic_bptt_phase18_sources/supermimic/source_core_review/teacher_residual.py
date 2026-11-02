"""Generic, model-I/O-free frozen teacher35 + vendor student policy wrapper.
Parent owns teacher loading/identity and exact observation/action contracts.
No SDK import and no model load. Do not normalize/detach the teacher input.
"""
from __future__ import annotations
import math
import torch
from torch import nn


class TeacherResidualPolicy(nn.Module):
    def __init__(self, residual, frozen_teacher, *, obs_ctx_offset,
                 teacher_obs_dim=35, action_dim=6, residual_scale=0.05,
                 zero_residual_output=True):
        super().__init__()
        if not math.isfinite(residual_scale) or residual_scale <= 0:
            raise ValueError('positive finite residual scale is required for student gradients')
        if obs_ctx_offset < 0:
            raise ValueError('explicit raw teacher-observation offset required')
        for key in ('enc', 'dec', 'obs_norm', 'goal_norm', 'hist'):
            if not hasattr(residual, key):
                raise TypeError('vendor residual interface missing: ' + key)
        self.residual = residual
        self.teacher = frozen_teacher
        self.teacher.requires_grad_(False)
        self.teacher.eval()
        self.obs_ctx_offset = int(obs_ctx_offset)
        self.teacher_obs_dim = int(teacher_obs_dim)
        self.action_dim = int(action_dim)
        self.register_buffer('_residual_scale', torch.tensor(float(residual_scale)))
        if zero_residual_output:
            output = self.residual.dec[-1]
            if not isinstance(output, nn.Linear) or output.out_features != self.action_dim:
                raise TypeError('reviewed vendor dec[-1] must be Linear(..., action_dim)')
            with torch.no_grad():
                output.weight.zero_()
                output.bias.zero_()

    @property
    def enc(self): return self.residual.enc

    @property
    def dec(self): return self.residual.dec

    @property
    def obs_norm(self): return self.residual.obs_norm

    @property
    def goal_norm(self): return self.residual.goal_norm

    @property
    def hist(self): return self.residual.hist

    def train(self, mode=True):
        super().train(mode)
        self.teacher.eval()
        return self

    def forward(self, obs_hist, goal):
        stop = self.obs_ctx_offset + self.teacher_obs_dim
        if obs_hist.ndim < 3 or obs_hist.shape[-1] < stop:
            raise ValueError('expected [..., history, obs_dim] with explicit original teacher35 slice')
        raw = obs_hist[..., -1, self.obs_ctx_offset:stop]
        base = self.teacher(raw)  # frozen weights; DO preserve d(action)/d(raw obs)
        delta = self.residual(obs_hist, goal)
        if base.shape != delta.shape or base.shape[-1] != self.action_dim:
            raise ValueError('teacher/student action shape mismatch')
        # Vendor imagination and real bridge own the final action-space clip.
        # Joint target scales/physical delays remain in the original environment.
        return base + self._residual_scale * delta

    def trainable_parameters(self):
        return (p for p in self.parameters() if p.requires_grad)

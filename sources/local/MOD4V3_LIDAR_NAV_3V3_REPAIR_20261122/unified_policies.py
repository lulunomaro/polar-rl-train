"""COMMANDER-AUTHORED & LOCKED NEURAL ARCHITECTURES (DO NOT MODIFY!).

Contains:
1. StairNav4DExpert: Bilaterally equivariant 459D (obs35 + hist420 + g_step4) stair policy.
   - Keeps obs35 & hist420 100% uncorrupted (gravity & mode bits untouched).
   - Injects 8D bounded nonlinear local-terrain features via a zero-initialized context branch
     into StairHead so 0-update output matches the donor to 0.0 floating-point error.
2. UnifiedJumpActor: Bilaterally symmetric R10-seeded all-regime jump actor (obs35 + hist420 -> 6D)
   with frozen E0/loco_base and correlated symmetric PPO exploration.
3. AsymmetricValue: Privileged critic MLP with LayerNorm for stable value estimation.
"""
from __future__ import annotations

import math
import torch
from torch import nn

from manual_fsm_model import make_stair, mirror_action, mirror_obs


def normalize_g_step(g_step: torch.Tensor) -> torch.Tensor:
    """Convert raw [d1, h1, d2, h2] (metres) into 8D bounded, even-symmetric phase features."""
    d1, h1, d2, h2 = g_step.unbind(-1)
    has1 = (h1 > 0.05).float()
    has2 = (h2 > 0.05).float()
    d1_clamped = d1.clamp(-0.35, 1.60)
    d2_clamped = d2.clamp(0.00, 1.60)
    d1_n = torch.where(has1 > 0.5, (d1_clamped - 0.35) / 0.50, torch.full_like(d1, 1.8))
    h1_n = (h1 / 0.20).clamp(0.0, 1.5) * has1
    d2_n = torch.where(has2 > 0.5, (d2_clamped - 0.80) / 0.50, torch.full_like(d2, 1.8))
    h2_n = (h2 / 0.20).clamp(0.0, 1.5) * has2
    # Smooth radial phase indicators for high-stance guide-wheel prep vs active riser tuck
    prep_phase = has1 * torch.exp(-((d1_clamped - 0.55) / 0.32).square())
    riser_phase = has1 * torch.exp(-((d1_clamped - 0.04) / 0.16).square())
    return torch.stack((d1_n, h1_n, d2_n, h2_n, has1, has2, prep_phase, riser_phase), dim=-1)


class StairNav4DExpert(nn.Module):
    """Bilaterally symmetric 459D stair expert with zero-drift donor initialization.

    Works universally with any donor architecture returned by make_stair() (StairExpert,
    ResidualStair, or A1StairExpert) while jointly training both the trunk and a dedicated
    bilaterally equivariant 4D-terrain + proprioception + temporal-history residual head.
    """

    def __init__(self, donor_payload: dict):
        super().__init__()
        self.trunk = make_stair(donor_payload)
        self.hist_conv = nn.Sequential(
            nn.Conv1d(35, 48, kernel_size=3, padding=1),
            nn.ELU(),
            nn.Conv1d(48, 32, kernel_size=3, stride=2, padding=1),
            nn.ELU(),
        )
        # 35 (obs) + 32*6 (192 temporal) + 8 (g8) = 235 -> 192 -> 128 -> 6
        self.terrain_delta = nn.Sequential(
            nn.Linear(235, 192),
            nn.LayerNorm(192),
            nn.ELU(),
            nn.Linear(192, 128),
            nn.ELU(),
            nn.Linear(128, 6),
        )
        nn.init.zeros_(self.terrain_delta[-1].weight)
        nn.init.zeros_(self.terrain_delta[-1].bias)

    def _delta_raw(self, obs: torch.Tensor, hist: torch.Tensor, g8: torch.Tensor) -> torch.Tensor:
        past = hist.reshape(-1, 12, 35).transpose(1, 2)
        h_feat = self.hist_conv(past).flatten(1)
        return self.terrain_delta(torch.cat((obs.clamp(-12.0, 12.0), h_feat, g8), dim=-1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x455 = x[..., :455]
        obs = x[..., :35]
        hist = x[..., 35:455]
        g8 = normalize_g_step(x[..., 455:459])

        base_act = self.trunk(x455)

        ref_obs = mirror_obs(obs)
        ref_hist = mirror_obs(hist.reshape(-1, 12, 35)).flatten(1)
        cat_obs = torch.cat((obs, ref_obs), dim=0)
        cat_hist = torch.cat((hist, ref_hist), dim=0)
        cat_g8 = torch.cat((g8, g8), dim=0)

        da, db = self._delta_raw(cat_obs, cat_hist, cat_g8).chunk(2, dim=0)
        sym_delta = 0.5 * (da + mirror_action(db))
        return (base_act + sym_delta).clamp(-6.0, 6.0)


SYMMETRIC_VARIANCE = 0.88
PAIR_VARIANCE = 1.0 + SYMMETRIC_VARIANCE
DIFFERENCE_VARIANCE = 1.0 - SYMMETRIC_VARIANCE


def sample_symmetric_action(mean: torch.Tensor, std: torch.Tensor) -> torch.Tensor:
    """Correlated bilateral Gaussian exploration: strongly favors symmetric leg actions while still exploring differential corrections."""
    white = torch.randn_like(mean)
    sym = 0.5 * (white + mirror_action(white))
    noise = math.sqrt(PAIR_VARIANCE) * sym + math.sqrt(DIFFERENCE_VARIANCE) * (white - sym)
    return mean + std * noise


def symmetric_action_log_prob(action: torch.Tensor, mean: torch.Tensor, std: torch.Tensor) -> torch.Tensor:
    residual = (action - mean) / std
    sym = 0.5 * (residual + mirror_action(residual))
    diff = residual - sym
    quad = sym.square() / PAIR_VARIANCE + diff.square() / DIFFERENCE_VARIANCE
    norm = 3.0 * math.log(2.0 * math.pi) + 1.5 * math.log(PAIR_VARIANCE * DIFFERENCE_VARIANCE)
    return -0.5 * quad.sum(dim=-1) - std.log().sum(dim=-1) - norm


class UnifiedJumpActor(nn.Module):
    """Bilaterally symmetric all-regime jump actor warm-started from R10ActorCritic (4c35c0e1).

    Preserves exact JumpPlant / Jump380Gpu motor law, obs_mean/obs_scale normalization buffers,
    learned mode_head + drive_head self-recovery, and strictly frozen E0 / loco_base.
    """

    def __init__(self, r10_checkpoint_path):
        super().__init__()
        from jump380_r10_policy import R10ActorCritic

        payload = torch.load(r10_checkpoint_path, map_location="cpu", weights_only=False)
        self.core = R10ActorCritic()
        self.core.load_state_dict(payload["state_dict"], strict=True)
        self.core.verify_zero_e0_drift()
        # Keep E0 and loco_base strictly frozen; train encoder, delta_head, mode_head, drive_head
        self.core.actor_body.e0.requires_grad_(False)
        self.core.actor_body.e_jump.loco_base.requires_grad_(False)
        for name, param in self.core.named_parameters():
            if name.startswith(("critic.", "e0_std")):
                param.requires_grad_(False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        obs = x[..., :35]
        hist = x[..., 35:455]
        action, _ = self.core.action_and_phase(obs, hist)
        return action.clamp(-6.0, 6.0)

    def verify_zero_e0_drift(self):
        self.core.verify_zero_e0_drift()


class AsymmetricValue(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.obs_norm = nn.LayerNorm(input_dim)
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ELU(),
            nn.Linear(512, 256),
            nn.ELU(),
            nn.Linear(256, 128),
            nn.ELU(),
            nn.Linear(128, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_clean = torch.nan_to_num(x, nan=0.0, posinf=10.0, neginf=-10.0).clamp(-25.0, 25.0)
        return self.net(self.obs_norm(x_clean)).squeeze(-1)

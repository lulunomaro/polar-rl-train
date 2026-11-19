# SPDX-License-Identifier: MIT
"""Pure-Neural Instant Serial-LQR-Style Jump & Step-Vault MoE Model for MOD4v3 (HW300N60_R3).

Zero-Cheating Architecture:
  - E0 (Frozen Locomotion Base): Exact c874 ActorMLP (35 -> 256 -> 128 -> 64 -> 6),
    strictly frozen (requires_grad=False, 0.0 parameter & action drift), active when obs[..., 30] <= 0.5.
  - E2 / InstantPureNeuralJumpExpert: Active when obs[..., 30] > 0.5 (GATE_STEPS = 45 = 0.90s at 50Hz).
    Inputs: ONLY standard 35-D proprioceptive actor obs + 40 x 35 = 1400-D pure-obs history.
    Zero runtime teacher, zero external phase state machine/timers, zero world-z / step-height / step-distance inputs.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
LOW_PITCH_DELIVERY = REPO / "deliveries/MOD4V3_LOW_PITCH_20261116"
C874_CKPT_PATH = LOW_PITCH_DELIVERY / "model_full_ppo.pt"
EXPECTED_C874_SHA256 = "c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617"

OBS_DIM = 35
HIST_LEN = 40
HIST_DIM = HIST_LEN * OBS_DIM  # 1400-D pure-obs history (0.80s at 50Hz)
ACT_DIM = 6
PRIV_CRITIC_DIM = 18  # Training-only privileged critic state (NEVER fed to actor!)
ACTION_CLIP = 6.0
JUMP_MODE_BIT_INDEX = 30
GATE_STEPS = 45  # 0.90s crisp jump window at 50Hz
JUMP_GATE_DURATION_S = GATE_STEPS * 0.02


def verify_c874_checkpoint(path: Path = C874_CKPT_PATH) -> dict:
    raw_bytes = path.read_bytes()
    sha = hashlib.sha256(raw_bytes).hexdigest()
    if sha != EXPECTED_C874_SHA256:
        raise RuntimeError(f"c874 SHA256 mismatch: expected {EXPECTED_C874_SHA256}, got {sha}")
    return torch.load(path, map_location="cpu", weights_only=False)


def build_c874_mlp() -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(OBS_DIM, 256),
        nn.ELU(),
        nn.Linear(256, 128),
        nn.ELU(),
        nn.Linear(128, 64),
        nn.ELU(),
        nn.Linear(64, ACT_DIM),
    )


class HistoryQueue:
    """Sliding 40-frame x 35-D pure proprioceptive observation history buffer (1400-D flattened)."""

    def __init__(self, hist_len: int = HIST_LEN):
        self.hist_len = hist_len
        self.buffer: torch.Tensor | None = None

    def clear(self) -> None:
        self.buffer = None

    def reset(self, obs: torch.Tensor) -> torch.Tensor:
        self.buffer = obs.unsqueeze(-2).repeat(*([1] * (obs.ndim - 1)), self.hist_len, 1).clone()
        return self.buffer.flatten(-2)

    def seed_from_short_history(self, short_seq: torch.Tensor) -> torch.Tensor:
        """Seed 40-frame buffer from a shorter K x 35 history (e.g. 12 x 35 from UnifiedThreeExpertMoE)."""
        k = short_seq.shape[-2]
        if k >= self.hist_len:
            self.buffer = short_seq[..., -self.hist_len :, :].clone()
        else:
            pad = short_seq[..., :1, :].repeat(*([1] * (short_seq.ndim - 2)), self.hist_len - k, 1)
            self.buffer = torch.cat((pad, short_seq), dim=-2).clone()
        return self.buffer.flatten(-2)

    def append(self, obs: torch.Tensor, done: torch.Tensor | None = None) -> torch.Tensor:
        if self.buffer is None or self.buffer.shape[:-2] != obs.shape[:-1] or self.buffer.device != obs.device:
            return self.reset(obs)
        self.buffer = torch.cat((self.buffer[..., 1:, :], obs.unsqueeze(-2)), dim=-2)
        if done is not None and bool(done.any()):
            self.buffer[done] = obs[done, None, :].expand(-1, self.hist_len, -1)
        return self.buffer.flatten(-2)


def mirror_obs_35(obs: torch.Tensor) -> torch.Tensor:
    """Exact bilateral left-right reflection of standard 35-D MOD4v3 observation."""
    m = obs.clone()
    m[..., 1] = -obs[..., 1]
    m[..., 2] = -obs[..., 2]
    m[..., 4] = -obs[..., 4]
    m[..., 6] = -obs[..., 6]
    m[..., 8] = -obs[..., 8]
    m[..., 10:12] = obs[..., 12:14]
    m[..., 12:14] = obs[..., 10:12]
    m[..., 14] = obs[..., 15]
    m[..., 15] = obs[..., 14]
    m[..., 16:18] = obs[..., 18:20]
    m[..., 18:20] = obs[..., 16:18]
    m[..., 20] = obs[..., 21]
    m[..., 21] = obs[..., 20]
    m[..., 22:24] = obs[..., 24:26]
    m[..., 24:26] = obs[..., 22:24]
    m[..., 26] = obs[..., 27]
    m[..., 27] = obs[..., 26]
    return m


def mirror_history_1400(hist: torch.Tensor) -> torch.Tensor:
    h_reshaped = hist.reshape(*hist.shape[:-1], HIST_LEN, OBS_DIM)
    return mirror_obs_35(h_reshaped).flatten(-2)


def mirror_action_6(act: torch.Tensor) -> torch.Tensor:
    out = act.clone()
    out[..., 0:2] = act[..., 2:4]
    out[..., 2:4] = act[..., 0:2]
    out[..., 4] = act[..., 5]
    out[..., 5] = act[..., 4]
    return out


class InstantTemporalEncoder(nn.Module):
    """Encodes 40 x 35 pure-obs history (1400-D) with 1D-Conv + crisp last-8-frame high-res shortcut."""

    def __init__(self, latent_dim: int = 96):
        super().__init__()
        self.register_buffer("obs_mean", torch.zeros(OBS_DIM))
        self.register_buffer("obs_scale", torch.ones(OBS_DIM))

        self.conv = nn.Sequential(
            nn.Conv1d(OBS_DIM, 64, kernel_size=3, padding=1),
            nn.ELU(),
            nn.Conv1d(64, 64, kernel_size=3, stride=2, padding=1),  # 40 -> 20
            nn.ELU(),
            nn.Conv1d(64, 64, kernel_size=3, stride=2, padding=1),  # 20 -> 10
            nn.ELU(),
            nn.Flatten(start_dim=-2),  # 640
        )
        # Recent 8 frames (8 x 35 = 280) + 1-step finite diff (35) + conv features (640) = 955
        self.mlp = nn.Sequential(
            nn.Linear(640 + 8 * OBS_DIM + OBS_DIM, 256),
            nn.LayerNorm(256),
            nn.ELU(),
            nn.Linear(256, 160),
            nn.ELU(),
            nn.Linear(160, latent_dim),
            nn.ELU(),
        )

    def normalize_obs(self, x: torch.Tensor) -> torch.Tensor:
        return ((x - self.obs_mean) / self.obs_scale.clamp_min(1e-4)).clamp(-10.0, 10.0)

    def forward(self, hist_flat: torch.Tensor) -> torch.Tensor:
        orig_shape = hist_flat.shape[:-1]
        h_seq = hist_flat.reshape(-1, HIST_LEN, OBS_DIM)
        h_norm = self.normalize_obs(h_seq)
        c_feat = self.conv(h_norm.transpose(1, 2))
        recent_8 = h_norm[:, -8:, :].flatten(1)
        diff_1 = h_norm[:, -1, :] - h_norm[:, -2, :]
        combined = torch.cat((c_feat, recent_8, diff_1), dim=-1)
        z = self.mlp(combined)
        return z.reshape(*orig_shape, -1)


class InstantPureNeuralJumpExpert(nn.Module):
    """Pure obs(35) + obs_history(1400) -> action(6) Instant Serial-LQR-Style Jump Expert.

    Plug-and-play compatible with:
      1) Stateless batched RL/DAgger: expert(obs_35, hist_1400)
      2) Stateful single-obs inference: expert(obs_35)
      3) UnifiedThreeExpertMoE (which passes 12x35=420-D hist): expert(obs_35, hist_420)
         automatically maintains internal 40-frame pure-obs history seeded cleanly on rising jump edge!
    """

    def __init__(self, latent_dim: int = 96):
        super().__init__()
        self.loco_base = build_c874_mlp()
        self.loco_base.requires_grad_(False)

        self.encoder = InstantTemporalEncoder(latent_dim=latent_dim)
        self.delta_head = nn.Sequential(
            nn.Linear(OBS_DIM + latent_dim, 256),
            nn.LayerNorm(256),
            nn.ELU(),
            nn.Linear(256, 256),
            nn.ELU(),
            nn.Linear(256, 128),
            nn.ELU(),
            nn.Linear(128, ACT_DIM),
        )
        nn.init.orthogonal_(self.delta_head[-1].weight, gain=0.05)
        nn.init.zeros_(self.delta_head[-1].bias)
        self._internal_queue = HistoryQueue(hist_len=HIST_LEN)

    def reset_history(self) -> None:
        self._internal_queue.clear()

    def set_normalization(self, mean: torch.Tensor, scale: torch.Tensor) -> None:
        self.encoder.obs_mean.copy_(mean.detach())
        self.encoder.obs_scale.copy_(scale.detach().clamp_min(1e-3))

    def _resolve_history(self, obs: torch.Tensor, hist: torch.Tensor | None) -> torch.Tensor:
        if hist is not None and hist.shape[-1] == HIST_DIM:
            return hist
        if hist is not None and hist.shape[-1] % OBS_DIM == 0 and hist.shape[-1] >= 2 * OBS_DIM:
            k = hist.shape[-1] // OBS_DIM
            short_seq = hist.reshape(*obs.shape[:-1], k, OBS_DIM)
            prev_jump = short_seq[..., -2, JUMP_MODE_BIT_INDEX] > 0.5
            cur_jump = obs[..., JUMP_MODE_BIT_INDEX] > 0.5
            if self._internal_queue.buffer is None or bool((cur_jump & ~prev_jump).any()):
                return self._internal_queue.seed_from_short_history(short_seq)
            return self._internal_queue.append(obs)
        return self._internal_queue.append(obs)

    def forward(self, obs: torch.Tensor, hist: torch.Tensor | None = None) -> torch.Tensor:
        hist_1400 = self._resolve_history(obs, hist)
        normal_obs = obs.clone()
        normal_obs[..., 28:35] = normal_obs.new_tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        with torch.no_grad():
            a_base = self.loco_base(normal_obs)
        z_hist = self.encoder(hist_1400)
        obs_norm = self.encoder.normalize_obs(obs)
        delta_a = self.delta_head(torch.cat((obs_norm, z_hist), dim=-1))
        return a_base + delta_a


class MoEInstantJumpBody(nn.Module):
    """Routes obs[..., 30] <= 0.5 to frozen E0 (c874) and obs[..., 30] > 0.5 to InstantPureNeuralJumpExpert."""

    def __init__(self):
        super().__init__()
        self.e0 = build_c874_mlp()
        self.e0.requires_grad_(False)
        self.e_jump = InstantPureNeuralJumpExpert(latent_dim=96)

    def forward(self, obs: torch.Tensor, hist: torch.Tensor | None = None) -> torch.Tensor:
        is_jump = obs[..., JUMP_MODE_BIT_INDEX : JUMP_MODE_BIT_INDEX + 1] > 0.5
        normal_obs = obs.clone()
        normal_obs[..., 28:35] = normal_obs.new_tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        with torch.no_grad():
            a0 = self.e0(normal_obs)
        if not bool(is_jump.any()):
            return a0
        aj = self.e_jump(obs, hist)
        return torch.where(is_jump, aj, a0)


class AsymmetricInstantJumpCritic(nn.Module):
    """Training-only Privileged Value Critic (NEVER used at evaluation/deployment)."""

    def __init__(self):
        super().__init__()
        self.register_buffer("priv_mean", torch.zeros(PRIV_CRITIC_DIM))
        self.register_buffer("priv_scale", torch.ones(PRIV_CRITIC_DIM))
        in_dim = OBS_DIM + 8 * OBS_DIM + PRIV_CRITIC_DIM
        self.net = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.LayerNorm(256),
            nn.ELU(),
            nn.Linear(256, 256),
            nn.ELU(),
            nn.Linear(256, 128),
            nn.ELU(),
            nn.Linear(128, 1),
        )

    def forward(self, obs_norm: torch.Tensor, recent_hist_norm: torch.Tensor, priv: torch.Tensor) -> torch.Tensor:
        p_norm = ((priv - self.priv_mean) / self.priv_scale.clamp_min(1e-3)).clamp(-10.0, 10.0)
        return self.net(torch.cat((obs_norm, recent_hist_norm, p_norm), dim=-1)).squeeze(-1)


class MoEInstantJumpActorCritic(nn.Module):
    """Complete MoE Actor-Critic container with strict zero-E0-drift verification."""

    def __init__(self):
        super().__init__()
        self.actor_body = MoEInstantJumpBody()
        self.e0_std = nn.Parameter(torch.ones(ACT_DIM), requires_grad=False)
        self.ejump_log_std = nn.Parameter(
            torch.tensor([0.022, 0.022, 0.022, 0.022, 0.032, 0.032], dtype=torch.float32).log()
        )
        self.critic = AsymmetricInstantJumpCritic()

    def load_frozen_c874(self, ckpt_path: Path = C874_CKPT_PATH) -> None:
        ck = verify_c874_checkpoint(ckpt_path)
        sd = ck["actor_state_dict"]
        mlp_sd = {k.replace("mlp.", "", 1): v.clone() for k, v in sd.items() if k.startswith("mlp.")}
        self.actor_body.e0.load_state_dict(mlp_sd, strict=True)
        self.actor_body.e_jump.loco_base.load_state_dict(mlp_sd, strict=True)
        if "distribution.std_param" in sd:
            self.e0_std.data.copy_(sd["distribution.std_param"].detach().clone())
        self.actor_body.e0.requires_grad_(False)
        self.actor_body.e_jump.loco_base.requires_grad_(False)
        self.e0_std.requires_grad_(False)

    def verify_zero_e0_drift(self, ckpt_path: Path = C874_CKPT_PATH) -> float:
        ck = verify_c874_checkpoint(ckpt_path)
        sd = ck["actor_state_dict"]
        max_diff = 0.0
        for k, v in sd.items():
            if k.startswith("mlp."):
                sub_k = k.replace("mlp.", "", 1)
                d0 = float((self.actor_body.e0.state_dict()[sub_k].cpu() - v.cpu()).abs().max().item())
                d1 = float((self.actor_body.e_jump.loco_base.state_dict()[sub_k].cpu() - v.cpu()).abs().max().item())
                max_diff = max(max_diff, d0, d1)
        if max_diff != 0.0:
            raise RuntimeError(f"E0 parameter drift detected: {max_diff}")
        return max_diff

    def act_deterministic(self, obs: torch.Tensor, hist: torch.Tensor) -> torch.Tensor:
        return self.actor_body(obs, hist).clamp(-ACTION_CLIP, ACTION_CLIP)

    def action_std(self, obs: torch.Tensor) -> torch.Tensor:
        is_jump = obs[..., JUMP_MODE_BIT_INDEX : JUMP_MODE_BIT_INDEX + 1] > 0.5
        j_std = self.ejump_log_std.clamp(min=-4.6, max=-1.2).exp().expand(*obs.shape[:-1], ACT_DIM)
        e0_s = self.e0_std.expand(*obs.shape[:-1], ACT_DIM)
        return torch.where(is_jump, j_std, e0_s)

    def evaluate_value(self, obs: torch.Tensor, hist: torch.Tensor, priv: torch.Tensor) -> torch.Tensor:
        enc = self.actor_body.e_jump.encoder
        obs_n = enc.normalize_obs(obs)
        h_seq = hist.reshape(*hist.shape[:-1], HIST_LEN, OBS_DIM)
        recent_n = enc.normalize_obs(h_seq[..., -8:, :]).flatten(-2)
        return self.critic(obs_n, recent_n, priv)

    def sample_action_and_value(
        self, obs: torch.Tensor, hist: torch.Tensor, priv: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        mean = self.actor_body(obs, hist).clamp(-ACTION_CLIP, ACTION_CLIP)
        std = self.action_std(obs)
        dist = torch.distributions.Normal(mean, std)
        sampled = dist.sample()
        log_prob = dist.log_prob(sampled).sum(dim=-1)
        val = self.evaluate_value(obs, hist, priv)
        return sampled.clamp(-ACTION_CLIP, ACTION_CLIP), sampled, log_prob, val

    def evaluate_actions(
        self, obs: torch.Tensor, hist: torch.Tensor, priv: torch.Tensor, raw_sampled_actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        mean = self.actor_body(obs, hist).clamp(-ACTION_CLIP, ACTION_CLIP)
        std = self.action_std(obs)
        dist = torch.distributions.Normal(mean, std)
        log_prob = dist.log_prob(raw_sampled_actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        val = self.evaluate_value(obs, hist, priv)
        return log_prob, entropy, val, mean

    def symmetry_loss(self, obs: torch.Tensor, hist: torch.Tensor) -> torch.Tensor:
        a_orig = self.actor_body.e_jump(obs, hist)
        a_mir = mirror_action_6(self.actor_body.e_jump(mirror_obs_35(obs), mirror_history_1400(hist)))
        return ((a_orig - a_mir) ** 2).mean()


class StatefulInstantJumpMoE(nn.Module):
    """Deployment/Evaluation Stateful Actor: standard obs_35 -> act_6 (zero privileged inputs!)."""

    def __init__(self, core: MoEInstantJumpActorCritic):
        super().__init__()
        self.core = core
        self.queue = HistoryQueue(hist_len=HIST_LEN)

    def reset_history(self) -> None:
        self.queue.clear()
        self.core.actor_body.e_jump.reset_history()

    @torch.inference_mode()
    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        hist = self.queue.append(obs)
        return self.core.act_deterministic(obs, hist)


def load_instant_jump_checkpoint(
    ckpt_path: Path | str | None = None,
    device: str | torch.device = "cpu",
) -> Tuple[MoEInstantJumpActorCritic, StatefulInstantJumpMoE, InstantPureNeuralJumpExpert]:
    """Load trained InstantPureNeuralJumpExpert & StatefulInstantJumpMoE from checkpoint."""
    if ckpt_path is None:
        ckpt_path = HERE / "weights/model_instant_jump_best.pt"
    ckpt_path = Path(ckpt_path)
    ck = torch.load(ckpt_path, map_location=device, weights_only=False)
    model = MoEInstantJumpActorCritic().to(device)
    model.load_frozen_c874()
    sd = ck["model_state_dict"] if "model_state_dict" in ck else ck
    model.load_state_dict(sd, strict=True)
    model.eval()
    model.verify_zero_e0_drift()
    stateful = StatefulInstantJumpMoE(model).to(device)
    stateful.eval()
    return model, stateful, model.actor_body.e_jump

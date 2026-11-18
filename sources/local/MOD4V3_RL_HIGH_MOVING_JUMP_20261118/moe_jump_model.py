# SPDX-License-Identifier: MIT
"""Pure-Neural MoE High-Jump & Moving-Jump Model for MOD4v3 (HW300N60_R3).

MoE Architecture (Zero Runtime Cheating):
  - E0 (Frozen Locomotion Base): Exact c874 ActorMLP (35 -> 256 -> 128 -> 64 -> 6),
    strictly frozen (requires_grad=False, 0.0 parameter drift), active when obs[..., 30] <= 0.5.
  - E_jump (Pure-Neural RL Jump Expert): Active when obs[..., 30] > 0.5.
    Inputs: ONLY standard 35-D proprioceptive actor obs + 12 x 35 = 420-D obs_history.
    Zero teacher calls, zero external phase timers, zero contact gates, zero world-z inputs.
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
HIST_LEN = 12
HIST_DIM = HIST_LEN * OBS_DIM  # 420
ACT_DIM = 6
PRIV_CRITIC_DIM = 14  # Training-only privileged critic inputs (never fed to actor!)
ACTION_CLIP = 6.0
JUMP_MODE_BIT_INDEX = 30


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
    """Sliding 12-frame x 35-D observation history buffer (420-D flattened)."""

    def __init__(self, hist_len: int = HIST_LEN):
        self.hist_len = hist_len
        self.buffer: torch.Tensor | None = None

    def reset(self, obs: torch.Tensor) -> torch.Tensor:
        # obs: (..., 35) -> buffer: (..., 12, 35)
        self.buffer = obs.unsqueeze(-2).repeat(*([1] * (obs.ndim - 1)), self.hist_len, 1).clone()
        return self.buffer.flatten(-2)

    def append(self, obs: torch.Tensor, done: torch.Tensor | None = None) -> torch.Tensor:
        if self.buffer is None:
            return self.reset(obs)
        self.buffer = torch.cat((self.buffer[..., 1:, :], obs.unsqueeze(-2)), dim=-2)
        if done is not None and bool(done.any()):
            self.buffer[done] = obs[done, None, :].expand(-1, self.hist_len, -1)
        return self.buffer.flatten(-2)


def mirror_obs_35(obs: torch.Tensor) -> torch.Tensor:
    """Bilateral left-right reflection of standard 35-D MOD4v3 observation for symmetry regularization.

    35-D layout:
      [0:3]   cmd: vx (+), vy (-), wz (-)
      [3:4]   height_cmd * 5 (+)
      [4:7]   root_ang_vel_b * 0.5: wx (-), wy (+), wz (-)
      [7:10]  gravity_b: gx (+), gy (-), gz (+)
      [10:16] joint_pos: [LF, LR, RF, RR, LW(0), RW(0)] -> swap (0,1)<->(2,3), 4<->5
      [16:20] qd_leg * 0.1: [LF, LR, RF, RR] -> swap (0,1)<->(2,3)
      [20:22] qd_wheel * 0.1: [LW, RW] -> swap 0<->1
      [22:28] a_prev: [LF, LR, RF, RR, LW, RW] -> swap (0,1)<->(2,3), 4<->5
      [28:35] ctrl_mode_obs (+)
    """
    m = obs.clone()
    m[..., 1] = -obs[..., 1]
    m[..., 2] = -obs[..., 2]
    m[..., 4] = -obs[..., 4]
    m[..., 6] = -obs[..., 6]
    m[..., 8] = -obs[..., 8]
    # Swap joint_pos LF,LR <-> RF,RR
    m[..., 10:12] = obs[..., 12:14]
    m[..., 12:14] = obs[..., 10:12]
    m[..., 14] = obs[..., 15]
    m[..., 15] = obs[..., 14]
    # Swap qd_leg LF,LR <-> RF,RR
    m[..., 16:18] = obs[..., 18:20]
    m[..., 18:20] = obs[..., 16:18]
    # Swap qd_wheel LW <-> RW
    m[..., 20] = obs[..., 21]
    m[..., 21] = obs[..., 20]
    # Swap a_prev
    m[..., 22:24] = obs[..., 24:26]
    m[..., 24:26] = obs[..., 22:24]
    m[..., 26] = obs[..., 27]
    m[..., 27] = obs[..., 26]
    return m


def mirror_history_420(hist: torch.Tensor) -> torch.Tensor:
    h_reshaped = hist.reshape(*hist.shape[:-1], HIST_LEN, OBS_DIM)
    return mirror_obs_35(h_reshaped).flatten(-2)


def mirror_action_6(act: torch.Tensor) -> torch.Tensor:
    out = act.clone()
    out[..., 0:2] = act[..., 2:4]
    out[..., 2:4] = act[..., 0:2]
    out[..., 4] = act[..., 5]
    out[..., 5] = act[..., 4]
    return out


class TemporalHistoryEncoder(nn.Module):
    """Encodes 12 x 35 proprioceptive history (420-D) into a 64-D latent temporal representation."""

    def __init__(self, latent_dim: int = 64):
        super().__init__()
        self.register_buffer("obs_mean", torch.zeros(OBS_DIM))
        self.register_buffer("obs_scale", torch.ones(OBS_DIM))

        # Multi-scale temporal Conv1d over (B, 35, 12) + global flattened MLP skip
        self.conv = nn.Sequential(
            nn.Conv1d(OBS_DIM, 64, kernel_size=3, padding=1),
            nn.ELU(),
            nn.Conv1d(64, 64, kernel_size=3, stride=2, padding=1),  # length 12 -> 6
            nn.ELU(),
            nn.Flatten(start_dim=-2),  # 64 * 6 = 384
        )
        self.mlp = nn.Sequential(
            nn.Linear(HIST_DIM + 384, 256),
            nn.LayerNorm(256),
            nn.ELU(),
            nn.Linear(256, 128),
            nn.ELU(),
            nn.Linear(128, latent_dim),
            nn.ELU(),
        )

    def normalize_obs(self, x: torch.Tensor) -> torch.Tensor:
        return ((x - self.obs_mean) / self.obs_scale.clamp_min(1e-4)).clamp(-10.0, 10.0)

    def forward(self, hist_flat: torch.Tensor) -> torch.Tensor:
        orig_shape = hist_flat.shape[:-1]
        h_seq = hist_flat.reshape(-1, HIST_LEN, OBS_DIM)
        h_norm = self.normalize_obs(h_seq)
        # Conv1d expects (N, C=35, L=12)
        c_feat = self.conv(h_norm.transpose(1, 2))
        combined = torch.cat((h_norm.flatten(1), c_feat), dim=-1)
        z = self.mlp(combined)
        return z.reshape(*orig_shape, -1)


class PureNeuralJumpExpert(nn.Module):
    """Pure obs(35) + obs_history(420) -> action(6) neural jump expert (zero state-machine / zero world-z)."""

    def __init__(self, latent_dim: int = 64):
        super().__init__()
        # Frozen c874 locomotion prior (purely neural 35->6 branch on normal mode bits)
        self.loco_base = build_c874_mlp()
        self.loco_base.requires_grad_(False)

        self.encoder = TemporalHistoryEncoder(latent_dim=latent_dim)
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
        # Initialize output layer near small values for stable training start
        nn.init.orthogonal_(self.delta_head[-1].weight, gain=0.05)
        nn.init.zeros_(self.delta_head[-1].bias)

    def set_normalization(self, mean: torch.Tensor, scale: torch.Tensor) -> None:
        self.encoder.obs_mean.copy_(mean.detach())
        self.encoder.obs_scale.copy_(scale.detach().clamp_min(1e-3))

    def forward(self, obs: torch.Tensor, hist: torch.Tensor) -> torch.Tensor:
        normal_obs = obs.clone()
        normal_obs[..., 28:35] = normal_obs.new_tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        with torch.no_grad():
            a_base = self.loco_base(normal_obs)
        z_hist = self.encoder(hist)
        obs_norm = self.encoder.normalize_obs(obs)
        delta_a = self.delta_head(torch.cat((obs_norm, z_hist), dim=-1))
        return a_base + delta_a


class MoEJumpBody(nn.Module):
    """Routes obs[..., 30] <= 0.5 to frozen E0 (c874) and obs[..., 30] > 0.5 to PureNeuralJumpExpert."""

    def __init__(self):
        super().__init__()
        self.e0 = build_c874_mlp()
        self.e0.requires_grad_(False)
        self.e_jump = PureNeuralJumpExpert(latent_dim=64)

    def forward(self, obs: torch.Tensor, hist: torch.Tensor) -> torch.Tensor:
        is_jump = obs[..., JUMP_MODE_BIT_INDEX : JUMP_MODE_BIT_INDEX + 1] > 0.5
        normal_obs = obs.clone()
        normal_obs[..., 28:35] = normal_obs.new_tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        with torch.no_grad():
            a0 = self.e0(normal_obs)
        if not bool(is_jump.any()):
            return a0
        aj = self.e_jump(obs, hist)
        return torch.where(is_jump, aj, a0)


class JumpValueCritic(nn.Module):
    """Asymmetric Value Critic for Stage-2 PPO (used ONLY during training, never at deployment)."""

    def __init__(self):
        super().__init__()
        self.register_buffer("priv_mean", torch.zeros(PRIV_CRITIC_DIM))
        self.register_buffer("priv_scale", torch.ones(PRIV_CRITIC_DIM))
        in_dim = OBS_DIM + HIST_DIM + PRIV_CRITIC_DIM
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

    def forward(self, obs_norm: torch.Tensor, hist_norm_flat: torch.Tensor, priv: torch.Tensor) -> torch.Tensor:
        p_norm = ((priv - self.priv_mean) / self.priv_scale.clamp_min(1e-3)).clamp(-10.0, 10.0)
        return self.net(torch.cat((obs_norm, hist_norm_flat, p_norm), dim=-1)).squeeze(-1)


class MoEJumpActorCritic(nn.Module):
    """Complete MoE Actor-Critic container with frozen E0 (c874) verification."""

    def __init__(self):
        super().__init__()
        self.actor_body = MoEJumpBody()
        # Frozen E0 std (kept from c874) vs trainable E_jump exploration log_std
        self.e0_std = nn.Parameter(torch.ones(ACT_DIM), requires_grad=False)
        self.ejump_log_std = nn.Parameter(
            torch.tensor([0.040, 0.040, 0.040, 0.040, 0.060, 0.060], dtype=torch.float32).log()
        )
        self.critic = JumpValueCritic()

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
        """Return exact max abs parameter difference between E0 (and loco_base) and original c874."""
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
        hist_n = enc.normalize_obs(hist.reshape(*hist.shape[:-1], HIST_LEN, OBS_DIM)).flatten(-2)
        return self.critic(obs_n, hist_n, priv)

    def sample_action_and_value(
        self, obs: torch.Tensor, hist: torch.Tensor, priv: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        mean_raw = self.actor_body(obs, hist)
        mean = mean_raw.clamp(-ACTION_CLIP, ACTION_CLIP)
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
        """Enforce pi(mirror(obs, hist)) == mirror(pi(obs, hist)) on E_jump."""
        pred = self.actor_body.e_jump(obs, hist)
        obs_m = mirror_obs_35(obs)
        hist_m = mirror_history_420(hist)
        pred_m = self.actor_body.e_jump(obs_m, hist_m)
        target_m = mirror_action_6(pred)
        return ((pred_m - target_m) ** 2).mean()

    def save_checkpoint(self, path: Path, metadata: dict | None = None) -> str:
        self.verify_zero_e0_drift()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model_type": "MOD4v3_MoE_RL_HighMovingJump",
            "obs_dim": OBS_DIM,
            "hist_len": HIST_LEN,
            "hist_dim": HIST_DIM,
            "action_dim": ACT_DIM,
            "jump_mode_bit_index": JUMP_MODE_BIT_INDEX,
            "c874_sha256": EXPECTED_C874_SHA256,
            "state_dict": self.state_dict(),
            "metadata": metadata or {},
        }
        torch.save(payload, path)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @classmethod
    def load_from_checkpoint(cls, path: Path, device: str = "cpu") -> "MoEJumpActorCritic":
        ck = torch.load(path, map_location=device, weights_only=False)
        model = cls().to(device)
        model.load_state_dict(ck["state_dict"], strict=True)
        model.actor_body.e0.requires_grad_(False)
        model.actor_body.e_jump.loco_base.requires_grad_(False)
        model.e0_std.requires_grad_(False)
        model.verify_zero_e0_drift()
        return model


class StatefulMoEJumpActor(nn.Module):
    """Deployment / evaluation wrapper maintaining internal 12-step HistoryQueue (obs_35 -> act_6)."""

    def __init__(self, core_model: MoEJumpActorCritic):
        super().__init__()
        self.core = core_model
        self.core.eval()
        self.queue = HistoryQueue(HIST_LEN)

    def reset_history(self) -> None:
        self.queue = HistoryQueue(HIST_LEN)

    @torch.inference_mode()
    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        hist = self.queue.append(obs)
        return self.core.act_deterministic(obs, hist)

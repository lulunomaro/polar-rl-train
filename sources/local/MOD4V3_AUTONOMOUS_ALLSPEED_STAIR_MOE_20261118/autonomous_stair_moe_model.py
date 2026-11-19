# SPDX-License-Identifier: MIT
"""Pure-Neural Proprioceptive Autonomous All-Speed Stair-Climb MoE for MOD4v3 (HW300N60_R3).

Architecture (`AutonomousStairMoE`, Zero Runtime Cheating):
  - Runtime Input: ONLY standard 35-D proprioceptive observation `obs`
    `[cmd_vx, cmd_vy, cmd_wz, h_cmd*5, ang_vel_b*0.5, grav_b, joint_pos_6, qd_6*0.1, prev_a_6, mode_7]`
    with normal driving `mode = [1, 0, 0, 0, 0, 0, 0]` (works 100% autonomously when `obs[29] == 0`,
    and also honors manual override `obs[29] > 0.5` if ever passed).
  - Internal Proprioceptive History Buffer: `H = 40` frames (`0.80s` at `50Hz`, `40 * 35 = 1400D`)
    managed inside `AutonomousStairMoE` via `.reset_history()`.
  - Frozen `E0` (`c874`): Exact `35 -> 256 -> 128 -> 64 -> 6` locomotion policy, strictly frozen
    (`requires_grad=False`, `0.0` drift verified against SHA256 `c874a1af...`).
  - `g_stair(obs, hist_40) -> [0, 1]`: Pure-neural temporal-conv router predicting stair-climb activation
    from proprioceptive impact + leg/pitch/wheel-velocity history, decaying smoothly back to `0` once
    relative standing height `h_cmd` is restored on top of the step.
  - `AllSpeedStairExpert(obs, hist_40) -> act_6`: Pure-neural multi-speed climb + auto-standup expert
    combining neural virtual-(v, h) modulation through frozen `E0` with a learned 6-D residual action head.
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
HIST_DIM = HIST_LEN * OBS_DIM  # 1400
ACT_DIM = 6
LATENT_DIM = 96
PRIV_CRITIC_DIM = 20  # Training-only privileged critic vector (NEVER passed to AutonomousStairMoE!)
ACTION_CLIP = 6.0
STAIR_MANUAL_BIT_INDEX = 29
GATE_DEADZONE = 0.05  # Pure differentiable tensor floor so g_prob <= 0.05 gives exact 0.0 interference on E0


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


class ProprioHistoryQueue40:
    """Sliding 40-frame x 35-D proprioceptive observation history buffer (1400-D flattened)."""

    def __init__(self, hist_len: int = HIST_LEN):
        self.hist_len = hist_len
        self.buffer: torch.Tensor | None = None

    def clear(self) -> None:
        self.buffer = None

    def reset(self, obs: torch.Tensor) -> torch.Tensor:
        self.buffer = obs.unsqueeze(-2).repeat(*([1] * (obs.ndim - 1)), self.hist_len, 1).clone()
        return self.buffer.flatten(-2)

    def append(self, obs: torch.Tensor, done: torch.Tensor | None = None) -> torch.Tensor:
        if self.buffer is None or self.buffer.shape[:-2] != obs.shape[:-1]:
            return self.reset(obs)
        self.buffer = torch.cat((self.buffer[..., 1:, :], obs.unsqueeze(-2)), dim=-2)
        if done is not None and bool(done.any()):
            self.buffer[done] = obs[done, None, :].expand(-1, self.hist_len, -1)
        return self.buffer.flatten(-2)


def canonicalize_normal_obs(obs: torch.Tensor) -> torch.Tensor:
    """Ensure mode bits [28:35] are canonical normal driving [1,0,0,0,0,0,0] for E0 & autonomous feature extraction."""
    out = obs.clone()
    out[..., 28:35] = out.new_tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    return out


def mirror_obs_35(obs: torch.Tensor) -> torch.Tensor:
    """Bilateral left-right reflection of standard 35-D MOD4v3 proprioceptive observation."""
    m = obs.clone()
    m[..., 1] = -obs[..., 1]  # cmd_vy
    m[..., 2] = -obs[..., 2]  # cmd_wz
    m[..., 4] = -obs[..., 4]  # wx
    m[..., 6] = -obs[..., 6]  # wz
    m[..., 8] = -obs[..., 8]  # grav_y
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


def mirror_hist_1400(hist: torch.Tensor) -> torch.Tensor:
    h_seq = hist.reshape(*hist.shape[:-1], HIST_LEN, OBS_DIM)
    return mirror_obs_35(h_seq).flatten(-2)


def mirror_action_6(act: torch.Tensor) -> torch.Tensor:
    out = act.clone()
    out[..., 0:2] = act[..., 2:4]
    out[..., 2:4] = act[..., 0:2]
    out[..., 4] = act[..., 5]
    out[..., 5] = act[..., 4]
    return out


class ProprioHistoryEncoder40(nn.Module):
    """Multi-scale 1D Temporal Conv + Recent-Window MLP encoder over H=40 (0.80s) proprioceptive frames."""

    def __init__(self, latent_dim: int = LATENT_DIM):
        super().__init__()
        self.register_buffer("obs_mean", torch.zeros(OBS_DIM))
        self.register_buffer("obs_scale", torch.ones(OBS_DIM))

        # Input to conv: (B, 35, 40) -> 20 -> 10 -> 5 => 5 * 64 = 320-D multi-scale temporal context
        self.temporal_conv = nn.Sequential(
            nn.Conv1d(OBS_DIM, 64, kernel_size=5, stride=2, padding=2),
            nn.ELU(),
            nn.Conv1d(64, 64, kernel_size=5, stride=2, padding=2),
            nn.ELU(),
            nn.Conv1d(64, 64, kernel_size=3, stride=2, padding=1),
            nn.ELU(),
            nn.Flatten(start_dim=-2),  # 320
        )
        # Concatenate 320-D 0.80s conv features + high-resolution last 6 frames (6 * 35 = 210D) = 530D
        self.proj = nn.Sequential(
            nn.Linear(320 + 6 * OBS_DIM, 256),
            nn.LayerNorm(256),
            nn.ELU(),
            nn.Linear(256, 128),
            nn.ELU(),
            nn.Linear(128, latent_dim),
            nn.ELU(),
        )

    def set_normalization(self, mean: torch.Tensor, scale: torch.Tensor) -> None:
        self.obs_mean.copy_(mean.detach())
        self.obs_scale.copy_(scale.detach().clamp_min(1e-3))

    def normalize_obs(self, x: torch.Tensor) -> torch.Tensor:
        xc = canonicalize_normal_obs(x)
        return ((xc - self.obs_mean) / self.obs_scale.clamp_min(1e-4)).clamp(-10.0, 10.0)

    def forward(self, obs: torch.Tensor, hist_flat: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        orig_shape = obs.shape[:-1]
        obs_norm = self.normalize_obs(obs)
        h_seq = hist_flat.reshape(-1, HIST_LEN, OBS_DIM)
        h_norm = self.normalize_obs(h_seq)
        c_feat = self.temporal_conv(h_norm.transpose(1, 2))
        recent_feat = h_norm[:, -6:, :].flatten(1)
        z = self.proj(torch.cat((c_feat, recent_feat), dim=-1)).reshape(*orig_shape, -1)
        return obs_norm, z


class ProprioStairRouter(nn.Module):
    """Pure-neural proprioceptive router `g_stair(obs, hist_40) -> [0, 1]`."""

    def __init__(self, in_dim: int = OBS_DIM + LATENT_DIM):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.LayerNorm(128),
            nn.ELU(),
            nn.Linear(128, 64),
            nn.ELU(),
            nn.Linear(64, 1),
        )
        # Initialize bias negative so initial gate probability is ~0.01 (safe E0 default)
        nn.init.orthogonal_(self.net[-1].weight, gain=0.1)
        nn.init.constant_(self.net[-1].bias, -3.5)

    def forward_logit(self, feat: torch.Tensor) -> torch.Tensor:
        return self.net(feat)


class AllSpeedStairExpert(nn.Module):
    """Pure-neural All-Speed Stair Climb + Auto-Standup Expert (`obs_35, hist_40 -> act_6`).

    Predicts virtual `(dv_virt, dh_virt)` command modulation routed through frozen `E0` (`c874`)
    for rock-solid closed-loop balance across `[0.40, 1.70] m/s` and `[0.25, 0.38] m`,
    plus a 6-D residual action head `delta_act` for rapid leg lift/tuck/standup responsiveness.
    """

    def __init__(self, e0_ref: nn.Module, in_dim: int = OBS_DIM + LATENT_DIM):
        super().__init__()
        # Share frozen E0 weights by reference or copy; keep strictly frozen
        self.loco_base = build_c874_mlp()
        self.loco_base.load_state_dict(e0_ref.state_dict(), strict=True)
        self.loco_base.requires_grad_(False)

        self.head = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.LayerNorm(256),
            nn.ELU(),
            nn.Linear(256, 256),
            nn.ELU(),
            nn.Linear(256, 128),
            nn.ELU(),
            nn.Linear(128, 2 + ACT_DIM),  # [dv_raw, dh_raw, delta_act_6]
        )
        nn.init.orthogonal_(self.head[-1].weight, gain=0.05)
        nn.init.zeros_(self.head[-1].bias)

    def forward_expert(self, normal_obs: torch.Tensor, feat: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        raw = self.head(feat)
        dv = 2.20 * torch.tanh(raw[..., 0:1])
        dh = 0.24 * torch.tanh(raw[..., 1:2])
        delta_a = 2.00 * torch.tanh(raw[..., 2:8])

        v_virt = (normal_obs[..., 0:1] + dv).clamp(-0.45, 1.85)
        h_cmd = normal_obs[..., 3:4] / 5.0
        h_virt = (h_cmd + dh).clamp(0.195, 0.415)

        obs_virt = torch.cat(
            (
                v_virt,
                normal_obs[..., 1:3],
                h_virt * 5.0,
                normal_obs[..., 4:],
            ),
            dim=-1,
        )
        a_virt = self.loco_base(obs_virt)
        a_stair = a_virt + delta_a
        return a_stair, v_virt.squeeze(-1), h_virt.squeeze(-1)


class AutonomousStairMoE(nn.Module):
    """Single pure-neural deployment & training module for Autonomous All-Speed Stair Climbing.

    Usage in unified WASD player or standalone evaluation:
        moe = AutonomousStairMoE.load_from_checkpoint("weights/model_autonomous_stair_moe_best.pt")
        moe.reset_history()
        act = moe(obs_35)                     # (B, 6) or (1, 6) in [-6, 6]
        act, g_stair = moe.forward_with_gate(obs_35)  # also returns live router gate in [0, 1]
    """

    def __init__(self):
        super().__init__()
        self.e0 = build_c874_mlp()
        self.e0.requires_grad_(False)
        self.encoder = ProprioHistoryEncoder40(latent_dim=LATENT_DIM)
        self.router = ProprioStairRouter(in_dim=OBS_DIM + LATENT_DIM)
        self.e1_stair = AllSpeedStairExpert(self.e0, in_dim=OBS_DIM + LATENT_DIM)
        self.history = ProprioHistoryQueue40(hist_len=HIST_LEN)

    def load_frozen_c874(self, ckpt_path: Path = C874_CKPT_PATH) -> None:
        ck = verify_c874_checkpoint(ckpt_path)
        sd = ck["actor_state_dict"]
        mlp_sd = {k.removeprefix("mlp."): v.clone() for k, v in sd.items() if k.startswith("mlp.")}
        self.e0.load_state_dict(mlp_sd, strict=True)
        self.e1_stair.loco_base.load_state_dict(mlp_sd, strict=True)
        self.e0.requires_grad_(False)
        self.e1_stair.loco_base.requires_grad_(False)

    def verify_zero_e0_drift(self, ckpt_path: Path = C874_CKPT_PATH) -> float:
        ck = verify_c874_checkpoint(ckpt_path)
        sd = ck["actor_state_dict"]
        max_diff = 0.0
        for name, param in self.e0.named_parameters():
            ref = sd[f"mlp.{name}"]
            max_diff = max(max_diff, float((param.detach().cpu() - ref).abs().max().item()))
            if param.requires_grad:
                raise RuntimeError(f"E0 parameter {name} has requires_grad=True!")
        for name, param in self.e1_stair.loco_base.named_parameters():
            ref = sd[f"mlp.{name}"]
            max_diff = max(max_diff, float((param.detach().cpu() - ref).abs().max().item()))
            if param.requires_grad:
                raise RuntimeError(f"E1 loco_base parameter {name} has requires_grad=True!")
        if max_diff != 0.0:
            raise RuntimeError(f"Non-zero E0 drift detected: {max_diff}")
        return max_diff

    def reset_history(self) -> None:
        self.history.clear()

    def compute_all_heads(
        self, obs: torch.Tensor, hist_flat: torch.Tensor
    ) -> dict[str, torch.Tensor]:
        normal_obs = canonicalize_normal_obs(obs)
        with torch.no_grad():
            a_e0 = self.e0(normal_obs)

        obs_norm, z_hist = self.encoder(obs, hist_flat)
        feat = torch.cat((obs_norm, z_hist), dim=-1)

        g_logit = self.router.forward_logit(feat)
        g_prob = torch.sigmoid(g_logit)
        g_auto = torch.clamp((g_prob - GATE_DEADZONE) / (1.0 - GATE_DEADZONE), 0.0, 1.0)
        manual_on = obs[..., STAIR_MANUAL_BIT_INDEX : STAIR_MANUAL_BIT_INDEX + 1] > 0.5
        g_eff = torch.where(manual_on, torch.ones_like(g_auto), g_auto)

        a_stair, v_virt, h_virt = self.e1_stair.forward_expert(normal_obs, feat)
        act_raw = (1.0 - g_eff) * a_e0 + g_eff * a_stair
        act = act_raw.clamp(-ACTION_CLIP, ACTION_CLIP)
        return {
            "act": act,
            "act_raw": act_raw,
            "a_e0": a_e0,
            "a_stair": a_stair,
            "g_logit": g_logit.squeeze(-1),
            "g_prob": g_prob.squeeze(-1),
            "g_eff": g_eff.squeeze(-1),
            "v_virt": v_virt,
            "h_virt": h_virt,
        }

    def forward_with_history(self, obs: torch.Tensor, hist_flat: torch.Tensor) -> torch.Tensor:
        return self.compute_all_heads(obs, hist_flat)["act"]

    def forward_with_history_and_gate(
        self, obs: torch.Tensor, hist_flat: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        out = self.compute_all_heads(obs, hist_flat)
        return out["act"], out["g_prob"]

    def forward_with_gate(self, obs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        squeeze_out = obs.ndim == 1
        x = obs.unsqueeze(0) if squeeze_out else obs
        hist = self.history.append(x)
        out = self.compute_all_heads(x, hist)
        if squeeze_out:
            return out["act"][0], out["g_prob"][0]
        return out["act"], out["g_prob"]

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        squeeze_out = obs.ndim == 1
        x = obs.unsqueeze(0) if squeeze_out else obs
        hist = self.history.append(x)
        act = self.compute_all_heads(x, hist)["act"]
        return act[0] if squeeze_out else act

    @classmethod
    def load_from_checkpoint(cls, ckpt_path: str | Path, device: str = "cpu") -> "AutonomousStairMoE":
        ck = torch.load(ckpt_path, map_location=device, weights_only=False)
        moe = cls().to(device)
        if "moe_state_dict" in ck:
            moe.load_state_dict(ck["moe_state_dict"], strict=True)
        elif "state_dict" in ck:
            sub = {k.removeprefix("moe."): v for k, v in ck["state_dict"].items() if k.startswith("moe.")}
            moe.load_state_dict(sub if sub else ck["state_dict"], strict=True)
        else:
            moe.load_state_dict(ck, strict=True)
        moe.e0.requires_grad_(False)
        moe.e1_stair.loco_base.requires_grad_(False)
        moe.verify_zero_e0_drift()
        moe.eval()
        return moe


class AsymmetricStairValueCritic(nn.Module):
    """Training-only Value Critic (NEVER instantiated or used at deployment/eval time)."""

    def __init__(self):
        super().__init__()
        self.register_buffer("priv_mean", torch.zeros(PRIV_CRITIC_DIM))
        self.register_buffer("priv_scale", torch.ones(PRIV_CRITIC_DIM))
        in_dim = OBS_DIM + LATENT_DIM + PRIV_CRITIC_DIM
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

    def forward(self, obs_norm: torch.Tensor, z_hist: torch.Tensor, priv: torch.Tensor) -> torch.Tensor:
        p_norm = ((priv - self.priv_mean) / self.priv_scale.clamp_min(1e-3)).clamp(-10.0, 10.0)
        return self.net(torch.cat((obs_norm, z_hist, p_norm), dim=-1)).squeeze(-1)


class AutonomousStairActorCritic(nn.Module):
    """Training container combining `AutonomousStairMoE` + `AsymmetricStairValueCritic` + Gaussian exploration."""

    def __init__(self):
        super().__init__()
        self.moe = AutonomousStairMoE()
        self.e0_std = nn.Parameter(torch.ones(ACT_DIM), requires_grad=False)
        self.stair_log_std = nn.Parameter(
            torch.tensor([0.022, 0.022, 0.022, 0.022, 0.035, 0.035], dtype=torch.float32).log()
        )
        self.critic = AsymmetricStairValueCritic()

    def load_frozen_c874(self, ckpt_path: Path = C874_CKPT_PATH) -> None:
        self.moe.load_frozen_c874(ckpt_path)
        ck = verify_c874_checkpoint(ckpt_path)
        sd = ck["actor_state_dict"]
        if "distribution.std_param" in sd:
            self.e0_std.data.copy_(sd["distribution.std_param"].clone())
        self.e0_std.requires_grad_(False)

    def verify_zero_e0_drift(self, ckpt_path: Path = C874_CKPT_PATH) -> float:
        return self.moe.verify_zero_e0_drift(ckpt_path)

    def evaluate_value(self, obs: torch.Tensor, hist_flat: torch.Tensor, priv: torch.Tensor) -> torch.Tensor:
        obs_norm, z_hist = self.moe.encoder(obs, hist_flat)
        return self.critic(obs_norm, z_hist, priv)

    def act_and_value(
        self, obs: torch.Tensor, hist_flat: torch.Tensor, priv: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        out = self.moe.compute_all_heads(obs, hist_flat)
        mean_raw = out["act_raw"]
        g_eff = out["g_eff"]
        std = self.stair_log_std.exp().clamp(0.006, 0.20).expand_as(mean_raw)
        dist = torch.distributions.Normal(mean_raw, std)
        # Only inject exploration noise when g_eff > 0.02 so pure E0 flat/slope/rough rollouts stay crisp!
        raw_sample = dist.rsample()
        active_mask = (g_eff.unsqueeze(-1) > 0.02).float()
        raw_exec = mean_raw + active_mask * (raw_sample - mean_raw)
        log_prob = dist.log_prob(raw_exec).sum(dim=-1)
        exec_act = raw_exec.clamp(-ACTION_CLIP, ACTION_CLIP)

        obs_norm, z_hist = self.moe.encoder(obs, hist_flat)
        val = self.critic(obs_norm, z_hist, priv)
        return exec_act, raw_exec, log_prob, val, out["g_prob"]

    def evaluate_ppo(
        self, obs: torch.Tensor, hist_flat: torch.Tensor, priv: torch.Tensor, raw_actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict[str, torch.Tensor]]:
        out = self.moe.compute_all_heads(obs, hist_flat)
        mean_raw = out["act_raw"]
        std = self.stair_log_std.exp().clamp(0.006, 0.20).expand_as(mean_raw)
        dist = torch.distributions.Normal(mean_raw, std)
        log_prob = dist.log_prob(raw_actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        obs_norm, z_hist = self.moe.encoder(obs, hist_flat)
        val = self.critic(obs_norm, z_hist, priv)
        return log_prob, entropy, val, out

    def save_checkpoint(self, path: str | Path, metadata: dict | None = None) -> str:
        self.verify_zero_e0_drift()
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format": "MOD4V3_AUTONOMOUS_ALLSPEED_STAIR_MOE_V1",
            "obs_dim": OBS_DIM,
            "hist_len": HIST_LEN,
            "hist_dim": HIST_DIM,
            "act_dim": ACT_DIM,
            "c874_sha256": EXPECTED_C874_SHA256,
            "moe_state_dict": self.moe.state_dict(),
            "state_dict": self.state_dict(),
            "metadata": metadata or {},
        }
        torch.save(payload, p)
        return hashlib.sha256(p.read_bytes()).hexdigest()

    @classmethod
    def load_from_checkpoint(cls, path: str | Path, device: str = "cpu") -> "AutonomousStairActorCritic":
        ck = torch.load(path, map_location=device, weights_only=False)
        ac = cls().to(device)
        ac.load_state_dict(ck["state_dict"], strict=True)
        ac.moe.e0.requires_grad_(False)
        ac.moe.e1_stair.loco_base.requires_grad_(False)
        ac.e0_std.requires_grad_(False)
        ac.verify_zero_e0_drift()
        return ac

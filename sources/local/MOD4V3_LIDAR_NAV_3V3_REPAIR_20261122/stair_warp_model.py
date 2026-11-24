"""COMMANDER-AUTHORED FiLM-Conditioned 459D Stair Neural Architecture (`StairWarpExpert`).

Pure end-to-end differentiable `nn.Module` mapping `[obs35, hist420, g_step4] -> action6`:
- Zero external command hijacking (`obs` and `history` enter completely untouched).
- Zero external state machines or tick counters inside or outside `forward()`.
- Exact bilateral equivariance (`f(mirror(x)) == mirror(f(x))` to ~1e-6).
- Solves the pretrained trunk OOD low-stance pull (`obs[3]=1.40` at `h=0.28m` vs trunk's `1.95`
  at `h=0.39m`) via a learnable symmetric Feature-wise Linear Modulation (`cond_mlp`) conditioned
  on `g8` + even proprioception, jointly trained end-to-end with `trunk` + `hist_conv` +
  `terrain_delta` on 4,096 `mujoco_warp` GPU worlds!
"""
from __future__ import annotations

import torch
from torch import nn

from manual_fsm_model import make_stair, mirror_action, mirror_obs


def normalize_g_step_ttc(g_step: torch.Tensor) -> torch.Tensor:
    """8D bounded even-symmetric terrain features supporting 2.30 m TTC lookahead.
    Matches normalize_g_step identically for all d1 <= 1.60 m while smoothly extending to 2.30 m!
    """
    d1, h1, d2, h2 = g_step.unbind(-1)
    has1 = (h1 > 0.05).float()
    has2 = (h2 > 0.05).float()
    d1_clamped = d1.clamp(-0.35, 2.25)
    d2_clamped = d2.clamp(0.00, 1.60)
    d1_n = torch.where(has1 > 0.5, (d1_clamped - 0.35) / 0.50, torch.full_like(d1, 1.8))
    h1_n = (h1 / 0.20).clamp(0.0, 1.5) * has1
    d2_n = torch.where(has2 > 0.5, (d2_clamped - 0.80) / 0.50, torch.full_like(d2, 1.8))
    h2_n = (h2 / 0.20).clamp(0.0, 1.5) * has2
    prep_phase = has1 * torch.exp(-((d1_clamped - 0.55) / 0.32).square())
    riser_phase = has1 * torch.exp(-((d1_clamped - 0.04) / 0.16).square())
    return torch.stack((d1_n, h1_n, d2_n, h2_n, has1, has2, prep_phase, riser_phase), dim=-1)


class StairWarpExpert(nn.Module):
    """Bilaterally symmetric FiLM + Residual 459D stair expert with optional High-Speed Kinetic Residual."""

    def __init__(self, donor_payload: dict, enable_hs_residual: bool = False):
        super().__init__()
        self.enable_hs_residual = enable_hs_residual
        self.trunk = make_stair(donor_payload)
        self.trunk.requires_grad_(False)

        # Even-symmetric terrain & proprioception conditioning head (14D -> 64 -> 32 -> 3)
        # Inputs (all strictly invariant under mirror_obs):
        #   g8 (8) + v_cmd (1) + h_cmd (1) + g_x (1) + q_sym_f (1) + q_sym_r (1) + qd_sym_w (1) = 14
        self.cond_mlp = nn.Sequential(
            nn.Linear(14, 64),
            nn.LayerNorm(64),
            nn.ELU(),
            nn.Linear(64, 32),
            nn.ELU(),
            nn.Linear(32, 3),
        )
        nn.init.normal_(self.cond_mlp[-1].weight, mean=0.0, std=0.01)
        with torch.no_grad():
            # Initial latent prior when step is present:
            # z[0]=2.2 -> alpha_h ~ 0.90 (smoothly elevates low stances toward ~0.39m when step ahead)
            # z[1]=0.0 -> h_climb_embed = 1.96 (~0.392m, exact trunk sweet spot)
            # z[2]=0.2 -> v_climb_cap ~ 1.18 m/s (prevents 2.0 m/s ballistic launch before riser)
            self.cond_mlp[-1].bias.copy_(torch.tensor([2.2, 0.0, 0.20]))

        self.hist_conv = nn.Sequential(
            nn.Conv1d(35, 48, kernel_size=3, padding=1),
            nn.ELU(),
            nn.Conv1d(48, 32, kernel_size=3, stride=2, padding=1),
            nn.ELU(),
        )
        # 35 (raw obs) + 192 (temporal conv) + 8 (g8) = 235 -> 192 -> 128 -> 6
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

        if self.enable_hs_residual:
            self.cond_mlp.requires_grad_(False)
            self.hist_conv.requires_grad_(False)
            self.terrain_delta.requires_grad_(False)
            self.hs_conv = nn.Sequential(
                nn.Conv1d(35, 48, kernel_size=3, padding=1),
                nn.ELU(),
                nn.Conv1d(48, 32, kernel_size=3, stride=2, padding=1),
                nn.ELU(),
            )
            self.hs_delta = nn.Sequential(
                nn.Linear(235, 192),
                nn.LayerNorm(192),
                nn.ELU(),
                nn.Linear(192, 128),
                nn.ELU(),
                nn.Linear(128, 6),
            )
            nn.init.zeros_(self.hs_delta[-1].weight)
            nn.init.zeros_(self.hs_delta[-1].bias)

    def _delta_raw(self, obs: torch.Tensor, hist: torch.Tensor, g8: torch.Tensor) -> torch.Tensor:
        past = hist.reshape(-1, 12, 35).transpose(1, 2)
        h_feat = self.hist_conv(past).flatten(1)
        return self.terrain_delta(torch.cat((obs.clamp(-12.0, 12.0), h_feat, g8), dim=-1))

    def _hs_raw(self, obs: torch.Tensor, hist: torch.Tensor, g8: torch.Tensor) -> torch.Tensor:
        past = hist.reshape(-1, 12, 35).transpose(1, 2)
        h_feat = self.hs_conv(past).flatten(1)
        return self.hs_delta(torch.cat((obs.clamp(-12.0, 12.0), h_feat, g8), dim=-1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        obs = x[..., :35]
        hist = x[..., 35:455]
        g_raw = x[..., 455:459]
        g8_ttc = normalize_g_step_ttc(g_raw)
        if self.enable_hs_residual:
            # Frozen r3 base was trained on <=1.59 m horizon; mask >1.59 m distant terrace steps for r3 base!
            in_r3_range = g_raw[..., 0] <= 1.595
            g_r3 = torch.stack(
                (
                    torch.where(in_r3_range, g_raw[..., 0].clamp(-0.35, 1.60), torch.full_like(g_raw[..., 0], 1.60)),
                    torch.where(in_r3_range, g_raw[..., 1], torch.zeros_like(g_raw[..., 1])),
                    g_raw[..., 2].clamp(0.00, 1.60),
                    g_raw[..., 3],
                ),
                dim=-1,
            )
            g8 = normalize_g_step_ttc(g_r3)
            step_h_max = torch.maximum(g_r3[..., 1], g_r3[..., 3])
        else:
            g8 = g8_ttc
            step_h_max = torch.maximum(g_raw[..., 1], g_raw[..., 3])

        # Smooth differentiable step-presence envelope: ~0 on flat/ramp/post-deck, ~1 when h1 or h2 >= 8cm
        has_step_smooth = torch.sigmoid((step_h_max - 0.058) / 0.008)

        # Strictly reflection-invariant (even) features for trunk conditioning
        even_prop = torch.stack(
            (
                obs[..., 0].clamp(-3.0, 3.0),
                obs[..., 3].clamp(1.0, 2.3),
                obs[..., 7].clamp(-1.0, 1.0),
                (0.5 * (obs[..., 10] + obs[..., 12])).clamp(-4.0, 4.0),
                (0.5 * (obs[..., 11] + obs[..., 13])).clamp(-4.0, 4.0),
                (0.5 * (obs[..., 20] + obs[..., 21])).clamp(-6.0, 6.0),
            ),
            dim=-1,
        )
        z_cond = self.cond_mlp(torch.cat((g8, even_prop), dim=-1))
        alpha_h = torch.sigmoid(z_cond[..., 0]) * has_step_smooth
        h_climb_embed = 1.96 + 0.28 * torch.tanh(z_cond[..., 1])
        v_climb_target = 0.65 + 0.90 * torch.sigmoid(z_cond[..., 2])
        v_raw = obs[..., 0]
        fwd_gate = torch.sigmoid((v_raw - 0.16) / 0.04)
        alpha_v = torch.sigmoid(z_cond[..., 0] - 0.2) * has_step_smooth * fwd_gate

        h_eff = torch.lerp(obs[..., 3], h_climb_embed, alpha_h)
        v_eff = torch.lerp(v_raw, v_climb_target, alpha_v)

        # Differentiable non-inplace reconstruction of internal trunk input
        obs_mod = torch.cat(
            (
                v_eff.unsqueeze(-1),
                obs[..., 1:3],
                h_eff.unsqueeze(-1),
                obs[..., 4:],
            ),
            dim=-1,
        )
        hist_3d = hist.reshape(-1, 12, 35)
        h_hist_eff = torch.lerp(hist_3d[..., 3], h_climb_embed.unsqueeze(-1), alpha_h.unsqueeze(-1))
        v_hist_raw = hist_3d[..., 0]
        fwd_hist_gate = torch.sigmoid((v_hist_raw - 0.16) / 0.04)
        alpha_v_hist = torch.sigmoid(z_cond[..., 0:1] - 0.2) * has_step_smooth.unsqueeze(-1) * fwd_hist_gate
        v_hist_eff = torch.lerp(v_hist_raw, v_climb_target.unsqueeze(-1), alpha_v_hist)
        hist_mod = torch.cat(
            (
                v_hist_eff.unsqueeze(-1),
                hist_3d[..., 1:3],
                h_hist_eff.unsqueeze(-1),
                hist_3d[..., 4:],
            ),
            dim=-1,
        ).flatten(1)

        base_act = self.trunk(torch.cat((obs_mod, hist_mod), dim=-1))

        ref_obs = mirror_obs(obs)
        ref_hist = mirror_obs(hist_3d).flatten(1)
        cat_obs = torch.cat((obs, ref_obs), dim=0)
        cat_hist = torch.cat((hist, ref_hist), dim=0)
        cat_g8 = torch.cat((g8, g8), dim=0)

        da, db = self._delta_raw(cat_obs, cat_hist, cat_g8).chunk(2, dim=0)
        sym_delta = 0.5 * (da + mirror_action(db))
        out = base_act + sym_delta
        if self.enable_hs_residual:
            has_step_ttc = torch.sigmoid((torch.maximum(g_raw[..., 1], g_raw[..., 3]) - 0.058) / 0.008)
            qdw_cur = 0.5 * (obs[..., 20] + obs[..., 21])
            qdw_hist = (0.5 * (hist_3d[..., 20] + hist_3d[..., 21])).amax(dim=-1)
            qdw_peak = torch.maximum(qdw_cur, 0.92 * qdw_hist)
            v_cmd_peak = torch.maximum(obs[..., 0], hist_3d[..., 0].amax(dim=-1))
            cmd_hs = ((torch.sigmoid((v_cmd_peak - 1.95) / 0.12) - 0.02) / 0.98).clamp(0.0, 1.0)
            vel_hs = ((torch.sigmoid((qdw_peak - 3.05) / 0.18) - 0.02) / 0.98).clamp(0.0, 1.0)
            hs_gate = has_step_ttc * cmd_hs * vel_hs
            cat_g8_ttc = torch.cat((g8_ttc, g8_ttc), dim=0)
            ha, hb = self._hs_raw(cat_obs, cat_hist, cat_g8_ttc).chunk(2, dim=0)
            sym_hs = 0.5 * (ha + mirror_action(hb))
            out = out + hs_gate.unsqueeze(-1) * sym_hs
        return out.clamp(-6.0, 6.0)

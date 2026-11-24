"""COMMANDER-AUTHORED Bilaterally Symmetric 459D Perception-Guided Jump Actor (`JumpWarpPerceptionActor`).

Maps `[obs35, hist420, g_jump4] -> action6` (and accepts `455D` `[obs35, hist420]` seamlessly):
- Triggered ONLY when the human manually presses `Space` / `J` (`jump_active == True`).
- Combines two strictly frozen (`0.0` drift!) pure-neural cores inside ONE unified module:
  1. `flat_core` (`E_jump_unified_candidate.pt`): Graduated `56/56` groups (`112/112` replays), `0` flips,
     `<=10 deg` level-chassis open-flat jump core (standing `0.0 m/s` to `2.8 m/s`, keep & abrupt release `W`).
  2. `vault_core` (`jump_r10_donor.pt`): Graduated `50..53 cm` all-geom clearance high-vault core across
     `0.24..0.42 m` stances for `380 mm` 3D solid platforms & `RMUL 270x352 mm` orange-tip bridge hurdles.
- Learns:
  1. `cond_mlp`: Reflection-invariant rising-edge takeoff-distance & approach-speed conditioning (`fire_ready`)
     around the exact ballistic `R10` sweet-spot curve so pressing `Space` anywhere `0.45..2.05 m` before an
     obstacle paces run-up steps with `obs[30]=0` and fires a clean `0 -> 1` rising edge at `d_sweet(v, h, span)`;
  2. `hist_conv + jump_delta`: Bilaterally equivariant 6-DOF residual boosting tall-stance (`0.35..0.42 m`)
     flat clearance (`>=38 cm`) and obstacle flight/landing stability.
"""
from __future__ import annotations

from pathlib import Path
import torch
from torch import nn

from manual_fsm_model import mirror_action, mirror_obs
from unified_policies import UnifiedJumpActor


def normalize_g_jump(g_jump: torch.Tensor) -> torch.Tensor:
    """Convert raw [d_front, d_back, z_top_rel, z_land_rel] into 10D bounded even-symmetric features."""
    df, db, zt, zl = g_jump.unbind(-1)
    span_raw = (db - df).clamp_min(0.0)
    has_obs = (((zt > 0.05) | (span_raw > 0.20)) & (df <= 2.25)).float()
    is_hurdle = has_obs * ((zt > 0.08) & (zl < 0.08)).float()
    is_plat = has_obs * (zl >= 0.08).float()
    is_trench = has_obs * ((zt <= 0.08) & (span_raw > 0.20)).float()

    df_c = df.clamp(-0.45, 2.25)
    db_c = db.clamp(-0.45, 2.50)
    df_n = torch.where(has_obs > 0.5, (df_c - 0.65) / 0.55, torch.full_like(df, 2.0))
    db_n = torch.where(has_obs > 0.5, (db_c - 0.90) / 0.55, torch.full_like(db, 2.0))
    span_n = (span_raw.clamp(0.0, 1.20) / 0.40) * has_obs
    zt_n = (zt.clamp(0.0, 0.45) / 0.38) * has_obs
    zl_n = (zl.clamp(-0.25, 0.45) / 0.38) * has_obs
    launch_win = has_obs * torch.exp(-((df_c - 0.68) / 0.36).square())
    return torch.stack((df_n, db_n, span_n, zt_n, zl_n, has_obs, is_hurdle, is_plat, is_trench, launch_win), dim=-1)


class JumpWarpPerceptionActor(nn.Module):
    """Bilaterally symmetric 459D perception-guided dual-core jump expert."""

    def __init__(self, r10_donor_path: Path, unified_init_path: Path | None = None):
        super().__init__()
        self.flat_core = UnifiedJumpActor(r10_donor_path)
        if unified_init_path is not None and Path(unified_init_path).is_file():
            ckpt = torch.load(unified_init_path, map_location="cpu", weights_only=False)
            sd = ckpt["actor"]
            if any(k.startswith("flat_core.") for k in sd):
                self.flat_core.load_state_dict(
                    {k.removeprefix("flat_core."): v for k, v in sd.items() if k.startswith("flat_core.")},
                    strict=True,
                )
            elif any(k.startswith("base.") for k in sd):
                self.flat_core.load_state_dict(
                    {k.removeprefix("base."): v for k, v in sd.items() if k.startswith("base.")},
                    strict=True,
                )
            else:
                self.flat_core.load_state_dict(sd, strict=True)
        self.vault_core = UnifiedJumpActor(r10_donor_path)

        # Keep both proven neural cores 100% frozen (zero E0 drift, zero flat regression!)
        self.flat_core.requires_grad_(False)
        self.vault_core.requires_grad_(False)

        self.cond_mlp = nn.Sequential(
            nn.Linear(16, 64),
            nn.LayerNorm(64),
            nn.ELU(),
            nn.Linear(64, 32),
            nn.ELU(),
            nn.Linear(32, 2),
        )
        nn.init.zeros_(self.cond_mlp[-1].weight)
        nn.init.zeros_(self.cond_mlp[-1].bias)

        self.hist_conv = nn.Sequential(
            nn.Conv1d(35, 48, kernel_size=3, padding=1),
            nn.ELU(),
            nn.Conv1d(48, 32, kernel_size=3, stride=2, padding=1),
            nn.ELU(),
        )
        self.jump_delta = nn.Sequential(
            nn.Linear(237, 192),
            nn.LayerNorm(192),
            nn.ELU(),
            nn.Linear(192, 128),
            nn.ELU(),
            nn.Linear(128, 6),
        )
        nn.init.zeros_(self.jump_delta[-1].weight)
        nn.init.zeros_(self.jump_delta[-1].bias)

    def _even_prop(self, obs: torch.Tensor) -> torch.Tensor:
        return torch.stack(
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

    def fire_ready(self, obs: torch.Tensor, g_jump: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Compute rising-edge takeoff readiness & minimum run-up velocity before an obstacle."""
        g10 = normalize_g_jump(g_jump)
        has_obs = g10[..., 5] > 0.5
        is_hurdle = g10[..., 6] > 0.5
        z_cond = self.cond_mlp(torch.cat((g10, self._even_prop(obs)), dim=-1))

        h_m = (obs[..., 3] * 0.2).clamp(0.20, 0.42)
        v_wheel = (0.5 * (obs[..., 20] + obs[..., 21]) * 0.625).clamp(0.0, 3.2)
        min_v_base = torch.where(
            is_hurdle,
            torch.full_like(h_m, 1.75),
            torch.where(g_jump[..., 2] >= 0.34, torch.full_like(h_m, 1.55), torch.full_like(h_m, 1.25)),
        )
        min_v = (min_v_base + 0.25 * torch.tanh(z_cond[..., 1])).clamp(1.05, 2.60)
        v_runup = torch.where(has_obs, torch.maximum(obs[..., 0], min_v), obs[..., 0])

        # Use actual wheel velocity once moving so early Space press accelerates cleanly before firing!
        v_eff = torch.maximum(v_wheel, 0.75 * v_runup).clamp(1.0, 3.0)
        span_c = (g_jump[..., 1] - g_jump[..., 0]).clamp(0.0, 0.90)

        # Calibrated from R10 400Hz ballistic trajectory table (TRAIN_TIMING.json):
        d_plat = 0.34 * v_eff + 0.55 * (h_m - 0.28) + 0.06
        d_hurd = 0.40 * v_eff + 0.50 * (h_m - 0.28) - 0.36 * span_c + 0.08
        d_sweet = (torch.where(is_hurdle, d_hurd, d_plat) + 0.18 * torch.tanh(z_cond[..., 0])).clamp(0.38, 1.28)

        speed_ready = v_wheel >= (min_v - 0.30).clamp_max(2.10)
        ready = (~has_obs) | ((g_jump[..., 0] <= d_sweet) & (speed_ready | (g_jump[..., 0] <= 0.52)))
        return ready, v_runup

    def _delta_raw(self, obs: torch.Tensor, hist: torch.Tensor, g10: torch.Tensor) -> torch.Tensor:
        past = hist.reshape(-1, 12, 35).transpose(1, 2)
        h_feat = self.hist_conv(past).flatten(1)
        return self.jump_delta(torch.cat((obs.clamp(-12.0, 12.0), h_feat, g10), dim=-1))

    def action_and_phase(
        self,
        obs: torch.Tensor,
        hist: torch.Tensor,
        g_jump: torch.Tensor | None = None,
        fire_dist: torch.Tensor | None = None,
    ):
        if g_jump is None:
            g_jump = torch.tensor([2.50, 2.50, 0.0, 0.0], dtype=obs.dtype, device=obs.device).expand(obs.shape[0], 4)
        g10 = normalize_g_jump(g_jump)
        has_obs = g10[..., 5]  # 0.0 on open flat ground, 1.0 on obstacle vault!
        is_hurdle = g10[..., 6]
        z_cond = self.cond_mlp(torch.cat((g10, self._even_prop(obs)), dim=-1))

        # On obstacle vaults:
        # 1) Ensure forward velocity >= min_v for span crossing, AND <= max_v_safe when Space was pressed very close (<0.75m at high speed);
        # 2) Coil target stance height command into the 0.25m high-impulse pocket so tall stances (0.35..0.42m) achieve full 46..52cm clearance!
        min_v = (
            torch.where(
                is_hurdle > 0.5,
                torch.full_like(has_obs, 1.75),
                torch.where(g_jump[..., 2] >= 0.34, torch.full_like(has_obs, 1.55), torch.full_like(has_obs, 1.25)),
            )
            + 0.25 * torch.tanh(z_cond[..., 1])
        ).clamp(1.05, 2.65)
        if fire_dist is not None:
            max_v_safe = (fire_dist.to(obs.dtype) / 0.36).clamp(1.45, 3.0)
            v_vault = torch.minimum(torch.maximum(obs[..., 0], min_v), torch.maximum(min_v, max_v_safe)).clamp(-1.0, 3.0)
        else:
            v_vault = torch.maximum(obs[..., 0], min_v).clamp(-1.0, 3.0)

        h_coil = torch.minimum(obs[..., 3], torch.full_like(obs[..., 3], 5.0 * 0.255))
        obs_vault = torch.cat(
            (v_vault.unsqueeze(-1), obs[..., 1:3], h_coil.unsqueeze(-1), obs[..., 4:]),
            dim=-1,
        )
        hist_3d = hist.reshape(-1, 12, 35)
        hist_v = (
            torch.minimum(torch.maximum(hist_3d[..., 0], min_v.unsqueeze(-1)), v_vault.unsqueeze(-1) + 0.15).clamp(-1.0, 3.0)
            if fire_dist is not None
            else torch.maximum(hist_3d[..., 0], min_v.unsqueeze(-1)).clamp(-1.0, 3.0)
        )
        hist_h = torch.minimum(hist_3d[..., 3], torch.full_like(hist_3d[..., 3], 5.0 * 0.255))
        hist_vault = torch.cat(
            (hist_v.unsqueeze(-1), hist_3d[..., 1:3], hist_h.unsqueeze(-1), hist_3d[..., 4:]),
            dim=-1,
        ).flatten(1)

        with torch.no_grad():
            flat_act, flat_mode = self.flat_core.core.action_and_phase(obs, hist)
            vault_act, vault_mode = self.vault_core.core.action_and_phase(obs_vault, hist_vault)

        base_act = torch.where(has_obs.unsqueeze(-1) > 0.5, vault_act, flat_act)
        mode = torch.where(has_obs > 0.5, vault_mode, flat_mode)

        # Keep open-flat jump 100.0% anchored to flat_core (56/56 groups, 112/112 replays, 0 flips, <=8.5 deg air pitch!),
        # and engage learned perception residual strictly on obstacle vaults (has_obs == 1.0)!
        res_gate = has_obs

        ref_obs = mirror_obs(obs)
        ref_hist = mirror_obs(hist_3d).flatten(1)
        cat_obs = torch.cat((obs, ref_obs), dim=0)
        cat_hist = torch.cat((hist, ref_hist), dim=0)
        cat_g10 = torch.cat((g10, g10), dim=0)

        da, db = self._delta_raw(cat_obs, cat_hist, cat_g10).chunk(2, dim=0)
        sym_delta = 0.5 * (da + mirror_action(db))
        act = (base_act + res_gate.unsqueeze(-1) * sym_delta).clamp(-6.0, 6.0)
        return act, mode

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        obs = x[..., :35]
        hist = x[..., 35:455]
        g_jump = x[..., 455:459] if x.shape[-1] >= 459 else None
        act, _ = self.action_and_phase(obs, hist, g_jump)
        return act

    def verify_zero_e0_drift(self):
        self.flat_core.verify_zero_e0_drift()
        self.vault_core.verify_zero_e0_drift()

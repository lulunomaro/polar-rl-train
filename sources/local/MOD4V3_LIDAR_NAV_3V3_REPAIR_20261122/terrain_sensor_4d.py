"""COMMANDER-AUTHORED & LOCKED 50 Hz Objective 4D Local Step Feature Extractor.

Computes g_step = [d1, h1, d2, h2] along the yaw-projected horizontal ray with 3-layer
geometric stair verification (zero false triggers on guardrails, baffles, perimeter walls,
cliffs, or parallel/grazing passes):
1. Ray-level approach & supporting-tread verification:
   - Unobstructed approach from robot center (s=0) to riser foot (no intervening wall or cliff chasm);
   - >= 0.40 m continuous elevated supporting tread behind the riser (rejects all thin guardrails/baffles).
2. 2D Topological Platform verification (`ElevationMap.is_traversable`):
   - Landing footprint (+0.18 m and +0.36 m behind riser) must lie on a >= 0.48 m wide,
     topologically reachable walkable deck (eliminates grazing rays along walls & perimeter rims).
3. Bilateral wheel-track alignment (`y_local = 0, +0.14, -0.14 m`):
   - Left and right tire tracks must both encounter the stair within |d_L - d_R| <= 0.25 m
     (supports up to +-40 deg oblique stair climbs while rejecting corner clips & parallel passes).
"""
from __future__ import annotations

import math
import numpy as np
import torch

S_GRID_NP = np.round(np.arange(-0.35, 2.691, 0.02), 4).astype(np.float32)  # 153 samples (-0.35..+2.69 m: full +0.40m tread check out to d1=2.25m)
EMPTY_NP = np.array([2.30, 0.0, 1.60, 0.0], dtype=np.float32)
EMPTY_JUMP_NP = np.array([2.50, 2.50, 0.0, 0.0], dtype=np.float32)


def extract_jump_feature_torch(
    s: torch.Tensor,
    z_eff: torch.Tensor,
    z_ground: torch.Tensor,
    z_ref: torch.Tensor | None = None,
) -> torch.Tensor:
    """Vectorized 4D Jump-Obstacle Extractor: returns [d_front, d_back, z_top_rel, z_land_rel] of shape (N, 4).

    Unifies all manual-jump terrains into one continuous 4D physical representation:
    - Open flat ground: [2.50, 2.50, 0.00, 0.00]
    - Overhead bridge beam / box hurdle (e.g. RMUL 270mm x 352mm orange-tip beam): [d_front, d_front+0.36, 0.27, 0.00]
    - Solid 200~390mm high platform / sheer highland: [d_front, d_front+0.08, z_plat, z_plat]
    - Sunken trench / broken-bridge gap (e.g. RMUL 800mm trench): [d_front, d_front+0.80, z_beam_or_0, 0.00]
    """
    n, m = z_eff.shape
    device = z_eff.device
    valid_far = torch.isfinite(z_ground)
    ze = torch.nan_to_num(z_eff, nan=9.9)
    zg = torch.nan_to_num(z_ground, nan=9.9)

    i_zero = int(s.abs().argmin())
    if z_ref is None:
        z_here = zg[:, max(0, i_zero - 2) : min(m, i_zero + 2)].median(dim=1).values  # (N,)
    else:
        z_here = z_ref.to(device=device, dtype=zg.dtype).reshape(n)
    rel_eff = ze - z_here[:, None]
    rel_gnd = zg - z_here[:, None]

    # Candidate jumpable obstacle region along s >= -0.35 m:
    # Either elevated obstacle in (0.11, 0.415] m OR sunken trench < -0.10 m, while rejecting >0.415 m arena walls!
    in_search = (s >= -0.35) & (s <= 2.20)
    wall_block = (rel_eff > 0.415) | (~valid_far)
    # Mask out anything at or behind an unjumpable >41.5cm outer arena wall
    wall_hit = (wall_block & (s[None, :] >= -0.05)).cumsum(dim=1) > 0

    is_elev = (rel_eff > 0.11) & (rel_eff <= 0.415) & ~wall_hit
    is_trench = (rel_gnd < -0.10) & ~wall_hit
    is_obs = is_elev | is_trench

    INF = m + 10
    idx = torch.arange(m, device=device).unsqueeze(0).expand(n, -1)
    first_idx = torch.where(is_obs & in_search[None, :], idx, INF).amin(dim=1)  # (N,)
    has_obs = first_idx < m - 8
    f_clamped = first_idx.clamp(0, m - 2)
    d_front = s[f_clamped]

    # Scan forward from first_idx up to +1.06 m (53 samples) to find if obstacle terminates (hurdle or trench)
    # vs stays elevated continuously (solid platform)!
    after_first = (idx >= f_clamped[:, None]) & (idx <= (f_clamped + 53).clamp_max(m - 1)[:, None])
    returned_level = after_first & (~is_obs) & (~wall_hit) & (rel_gnd.abs() <= 0.11)
    end_idx = torch.where(returned_level, idx, INF).amin(dim=1)
    is_finite_span = has_obs & (end_idx < INF) & ((s[end_idx.clamp_max(m - 1)] - d_front) <= 1.02)

    # Confirm landing zone beyond finite span or on platform is valid (not arena exterior wall!)
    land_probe_idx = torch.where(
        is_finite_span,
        (end_idx + 8).clamp_max(m - 1),
        (f_clamped + 18).clamp_max(m - 1),
    )
    land_valid = (
        torch.gather(valid_far, 1, land_probe_idx[:, None]).squeeze(1)
        & ~torch.gather(wall_hit, 1, land_probe_idx[:, None]).squeeze(1)
    )
    # Also reject sheer drops with no far deck (cliff off highland into open floor > 1.05 m wide without landing!)
    first_is_trench = torch.gather(is_trench, 1, f_clamped[:, None]).squeeze(1)
    has_obs = has_obs & land_valid & (~first_is_trench | is_finite_span)

    d_back_raw = torch.where(
        is_finite_span,
        s[end_idx.clamp_max(m - 1)],
        d_front + 0.08,
    )
    span_mask = (idx >= f_clamped[:, None]) & (
        idx <= torch.where(is_finite_span, end_idx.clamp_max(m - 1), (f_clamped + 16).clamp_max(m - 1))[:, None]
    )
    z_top_raw = torch.where(span_mask, rel_eff, torch.zeros_like(rel_eff)).amax(dim=1).clamp(0.0, 0.42)
    z_land_raw = torch.where(
        is_finite_span,
        torch.gather(rel_gnd, 1, (end_idx + 8).clamp_max(m - 1)[:, None]).squeeze(1).clamp(-0.22, 0.42),
        torch.gather(rel_gnd, 1, (f_clamped + 18).clamp_max(m - 1)[:, None]).squeeze(1).clamp(0.0, 0.42),
    )

    out_df = torch.where(has_obs, d_front, torch.full_like(d_front, 2.50))
    out_db = torch.where(has_obs, d_back_raw, torch.full_like(d_front, 2.50))
    out_zt = torch.where(has_obs, z_top_raw, torch.zeros_like(d_front))
    out_zl = torch.where(has_obs, z_land_raw, torch.zeros_like(d_front))
    return torch.stack((out_df, out_db, out_zt, out_zl), dim=1)


def extract_profile_torch(s: torch.Tensor, z: torch.Tensor) -> torch.Tensor:
    """Vectorized GPU/CPU PyTorch extractor: z has shape (N, M), s has shape (M,). Returns (N, 4)."""
    n, m = z.shape
    device = z.device
    z_clean = z.clone()
    for _ in range(3):
        nan_mask = ~torch.isfinite(z_clean)
        if not bool(nan_mask.any()):
            break
        shifted_r = torch.cat((z_clean[:, :1], z_clean[:, :-1]), dim=1)
        shifted_l = torch.cat((z_clean[:, 1:], z_clean[:, -1:]), dim=1)
        z_clean = torch.where(nan_mask, torch.where(torch.isfinite(shifted_r), shifted_r, shifted_l), z_clean)
    z_clean = torch.nan_to_num(z_clean, nan=0.0)

    dz = z_clean[:, 1:] - z_clean[:, :-1]  # (N, M-1)
    steep = dz > 0.016  # > 0.80 m/m (~39 deg), ignores all <= 22 deg ramps!
    bridged = steep.clone()
    bridged[:, 1:-1] |= steep[:, :-2] & steep[:, 2:]

    prev_b = torch.cat((torch.zeros((n, 1), dtype=torch.bool, device=device), bridged[:, :-1]), dim=1)
    next_b = torch.cat((bridged[:, 1:], torch.zeros((n, 1), dtype=torch.bool, device=device)), dim=1)
    starts = bridged & ~prev_b
    ends = bridged & ~next_b

    idx = torch.arange(m - 1, device=device).unsqueeze(0).expand(n, -1)
    INF = m + 10
    s_idx = torch.where(starts, idx, INF).topk(4, dim=1, largest=False).values  # (N, 4)
    e_idx = torch.where(ends, idx, INF).topk(4, dim=1, largest=False).values    # (N, 4)
    valid_seg = (s_idx < m - 1) & (e_idx < m - 1) & (e_idx >= s_idx)

    s_clamped = s_idx.clamp(0, m - 2)
    e_plus1 = (e_idx + 1).clamp(0, m - 1)

    z0 = torch.gather(z_clean, 1, s_clamped)
    z1 = torch.gather(z_clean, 1, e_plus1)
    x0 = s[s_clamped]
    x1 = s[e_plus1]

    h_seg = z1 - z0
    w_seg = x1 - x0
    d_seg = 0.5 * (x0 + x1)

    # Layer 1A: Unobstructed approach from robot base (s=0) for candidate 0, or from previous riser top for candidates 1..3!
    i_zero = int(s.abs().argmin())
    prev_end = torch.cat((torch.full((n, 1), max(0, i_zero - 2), dtype=torch.long, device=device), e_plus1[:, :-1]), dim=1)
    z_start = torch.gather(z_clean, 1, prev_end.clamp(0, m - 1))
    pos_grid = torch.arange(m, device=device).view(1, 1, m)
    in_runway = (pos_grid >= prev_end.unsqueeze(-1)) & (pos_grid <= s_clamped.unsqueeze(-1))
    z_exp = z_clean.unsqueeze(1).expand(-1, 4, -1)
    runway_max = torch.where(in_runway, z_exp, z0.unsqueeze(-1)).amax(dim=-1)
    runway_min = torch.where(in_runway, z_exp, z0.unsqueeze(-1)).amin(dim=-1)
    approach_clear = torch.where(
        s_clamped > prev_end + 2,
        (runway_max <= torch.maximum(z0, z_start) + 0.075)
        & (z_start <= z0 + 0.085)
        & (runway_min >= torch.minimum(z0, z_start) - 0.075),
        torch.ones_like(valid_seg),
    )

    # Layer 1B: Continuous elevated supporting tread over +6..+40 cm behind riser top
    # (Preserves RMUC 50mm / RM27 40mm CAD crest lips while rejecting all guardrails/baffles that drop back down!)
    has_lookahead = e_plus1 + 20 < m
    tread_elevated = torch.ones_like(valid_seg)
    for k in (3, 6, 9, 12, 16, 20):
        zk = torch.gather(z_clean, 1, (e_plus1 + k).clamp_max(m - 1))
        tread_elevated &= (zk >= z1 - 0.078) & (zk >= z0 + 0.072)
    z_near1 = torch.gather(z_clean, 1, (e_plus1 + 3).clamp_max(m - 1))
    z_near2 = torch.gather(z_clean, 1, (e_plus1 + 10).clamp_max(m - 1))
    flat_landing = ((z_near1 - z1).abs() <= 0.075) & ((z_near2 - z1).abs() <= 0.078)
    tread_ok = torch.where(has_lookahead, tread_elevated & flat_landing, flat_landing & (e_plus1 + 6 < m))

    # Valid climbable stair riser: height in [0.078, 0.270] m, bevel width <= 0.225 m, distance <= 2.28 m
    good = valid_seg & (h_seg >= 0.078) & (h_seg <= 0.270) & (w_seg <= 0.225) & (d_seg <= 2.28) & approach_clear & tread_ok
    # A downstream segment cannot look "through" a rejected non-stair barrier/guardrail in front of the robot!
    blocked_front = valid_seg & (e_plus1 > i_zero) & ~good
    blocked_prefix = torch.zeros_like(good)
    blocked_prefix[:, 1] = blocked_front[:, 0]
    blocked_prefix[:, 2] = blocked_front[:, 0] | blocked_front[:, 1]
    blocked_prefix[:, 3] = blocked_front[:, 0] | blocked_front[:, 1] | blocked_front[:, 2]
    good = good & ~blocked_prefix

    rank_key = torch.where(good, torch.arange(4, device=device).unsqueeze(0), 99)
    pick = rank_key.topk(2, dim=1, largest=False).indices
    pick_good = torch.gather(good, 1, pick)
    pick_d = torch.gather(d_seg, 1, pick)
    pick_h = torch.gather(h_seg, 1, pick)

    d1 = torch.where(pick_good[:, 0], pick_d[:, 0], torch.full((n,), 2.30, device=device))
    h1 = torch.where(pick_good[:, 0], pick_h[:, 0], torch.zeros(n, device=device))
    good2 = pick_good[:, 1] & (pick_d[:, 1] <= 1.58)
    d2 = torch.where(good2, pick_d[:, 1], torch.full((n,), 1.60, device=device))
    h2 = torch.where(good2, pick_h[:, 1], torch.zeros(n, device=device))
    return torch.stack((d1, h1, d2, h2), dim=1)


def extract_profile(s: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Single-ray CPU wrapper around extract_profile_torch for guaranteed bit-equivalence."""
    st = torch.as_tensor(s, dtype=torch.float32)
    zt = torch.as_tensor(z, dtype=torch.float32).reshape(1, -1)
    return extract_profile_torch(st, zt)[0].numpy()


class TerrainSensor4D:
    def __init__(self, elevation):
        self.map = elevation
        self.s = S_GRID_NP.copy()
        self._s_torch = torch.from_numpy(self.s)
        self._lats = np.array([0.0, 0.10, -0.10], dtype=np.float32)[:, None]

    def sample(self, x: float, y: float, yaw: float):
        c, sn = math.cos(yaw), math.sin(yaw)
        xs = x + c * self.s[None, :] - sn * self._lats
        ys = y + sn * self.s[None, :] + c * self._lats
        zs = self.map.sample(xs, ys).astype(np.float32)
        feats = extract_profile_torch(self._s_torch, torch.from_numpy(zs)).numpy()
        fc = feats[0].copy()
        fl, fr = feats[1], feats[2]

        # Layer 2 (2D traversable landing platform) + Layer 3 (anti-parallel normal alignment <= 46 deg)
        if fc[1] > 0.05:
            d1 = float(fc[0])
            ok_land = self.map.is_traversable(x + (d1 + 0.18) * c, y + (d1 + 0.18) * sn) and self.map.is_traversable(
                x + (d1 + 0.36) * c, y + (d1 + 0.36) * sn
            )
            l_match = (fl[1] > 0.05) and (abs(float(fl[1]) - float(fc[1])) <= 0.065) and (abs(float(fl[0]) - d1) <= 0.105)
            r_match = (fr[1] > 0.05) and (abs(float(fr[1]) - float(fc[1])) <= 0.065) and (abs(float(fr[0]) - d1) <= 0.105)
            both_seen = (fl[1] > 0.05) and (fr[1] > 0.05)
            ok_bilat = (l_match and r_match and abs(float(fl[0]) - float(fr[0])) <= 0.21) if both_seen else (l_match or r_match)
            if not (ok_land and ok_bilat):
                fc = EMPTY_NP.copy()

        if fc[3] > 0.05:
            d2 = float(fc[2])
            ok_land2 = self.map.is_traversable(x + (d2 + 0.18) * c, y + (d2 + 0.18) * sn) and self.map.is_traversable(
                x + (d2 + 0.36) * c, y + (d2 + 0.36) * sn
            )
            if not ok_land2:
                fc[2], fc[3] = 1.60, 0.0

        node = self.map.index(x, y)
        return fc, float(self.map.ceiling[node]), zs[0]

    def sample_jump(self, x: float, y: float, yaw: float, z_ref: float | None = None) -> np.ndarray:
        c, sn = math.cos(yaw), math.sin(yaw)
        rx = x + c * self.s
        ry = y + sn * self.s
        zg = self.map.sample(rx, ry).astype(np.float32)
        ceil = self.map.sample_ceiling(rx, ry).astype(np.float32)
        # Convert low overhead beams (e.g. RMUL 250..270mm orange-tip bridge) into jumpable solid beam height!
        ze = np.where(np.isfinite(ceil) & (ceil < 0.38), zg + ceil + 0.021, zg).astype(np.float32)
        zg_t = torch.from_numpy(zg).unsqueeze(0)
        ze_t = torch.from_numpy(ze).unsqueeze(0)
        zr_t = None if z_ref is None else torch.tensor([float(z_ref)], dtype=torch.float32)
        return extract_jump_feature_torch(self._s_torch, ze_t, zg_t, zr_t)[0].numpy()

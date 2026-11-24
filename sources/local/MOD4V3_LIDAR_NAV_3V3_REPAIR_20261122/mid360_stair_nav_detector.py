"""Real-Time Livox Mid-360 3D Point-Cloud Stair, Jump-Hurdle & Dynamic-Obstacle Detector.

Supports two operating modes seamlessly for both MuJoCo simulation and real-robot ROS2 deployment:
1. `mode="fusion"` (Competition Default: Pre-built Prior Map + Live Mid-360 3D Point Cloud):
   - Uses pre-built 2.5D prior map (`ElevationMap` from CAD or FAST-LIO2 `.pcd`) for occlusion-free near-field terrain;
   - Registers live 50 Hz / 10 Hz Mid-360 3D point clouds into `map` frame to:
     a) Count real-time 3D point-cloud support on upcoming stair risers & treads (`stair_pc_pts`);
     b) Detect unmapped dynamic obstacles (enemy/ally robots, armor blocks, debris) via 3D height discrepancy
        (`z_live > z_prior + 0.14 m` reaching `> +0.28 m`), immediately VETOING false stair triggers (`g_step -> EMPTY`)
        and maintaining an inflated 2D `dynamic_blocked` mask for real-time A* path replanning;
     c) Fuse genuine unmapped low platforms/steps (`0.08..0.40 m` tall, `>= 0.48 m` wide, flat top) into local `g_step` / `g_jump`.
2. `mode="online_pc"` (Mapless / Unknown-Venue Mode: Pure Live Mid-360 3D Point Cloud, `prior_map=None`):
   - Accumulates motion-compensated 3D Mid-360 scans in a robot-centered scrolling `2 cm` 2.5D + overhang submap (`12 m x 12 m`),
     applies free-space cone interpolation inside the near-wheel blind cone, and extracts `g_step`, `g_jump`, and `ceiling`
     purely from live 3D Mid-360 point clouds!
"""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt, label, median_filter
import torch

from mid360_sensor import Mid360Config, quat_wxyz_to_rotmat
from terrain_sensor_4d import (
    EMPTY_JUMP_NP,
    EMPTY_NP,
    S_GRID_NP,
    extract_jump_feature_torch,
    extract_profile_torch,
)


class Mid360ScrollingSubmap:
    """Fast `2 cm` world-aligned scrolling 2.5D surface + overhang + tall-wall submap (`12.8 m x 12.8 m`)."""

    def __init__(self, res: float = 0.02, half_extent_m: float = 6.40):
        self.res = float(res)
        self.half = float(half_extent_m)
        self.n = int(round(2.0 * self.half / self.res))  # 640 x 640 (~1.6 MB per float32 layer)
        self.origin_x = -self.half
        self.origin_y = -self.half
        self.z_gnd = np.full((self.n, self.n), np.nan, dtype=np.float32)
        self.z_ceil = np.full((self.n, self.n), np.inf, dtype=np.float32)
        self.wall_hits = np.zeros((self.n, self.n), dtype=np.float32)
        self.hit_count = np.zeros((self.n, self.n), dtype=np.int32)
        self.initialized = False

    def reset(self, center_x: float = 0.0, center_y: float = 0.0) -> None:
        self.origin_x = round(float(center_x) / self.res) * self.res - self.half
        self.origin_y = round(float(center_y) / self.res) * self.res - self.half
        self.z_gnd.fill(np.nan)
        self.z_ceil.fill(np.inf)
        self.wall_hits.fill(0.0)
        self.hit_count.fill(0)
        self.initialized = True

    def _recenter_if_needed(self, cx: float, cy: float) -> None:
        if not self.initialized:
            self.reset(cx, cy)
            return
        cur_cx = self.origin_x + self.half
        cur_cy = self.origin_y + self.half
        if abs(cx - cur_cx) <= 2.40 and abs(cy - cur_cy) <= 2.40:
            return
        dx_cells = int(round((cx - cur_cx) / self.res))
        dy_cells = int(round((cy - cur_cy) / self.res))
        if abs(dx_cells) >= self.n or abs(dy_cells) >= self.n:
            self.reset(cx, cy)
            return

        def _shift(arr: np.ndarray, fill_val) -> np.ndarray:
            out = np.full_like(arr, fill_val)
            sy0 = max(0, dy_cells)
            sy1 = min(self.n, self.n + dy_cells)
            dy0 = max(0, -dy_cells)
            dy1 = dy0 + (sy1 - sy0)
            sx0 = max(0, dx_cells)
            sx1 = min(self.n, self.n + dx_cells)
            dx0 = max(0, -dx_cells)
            dx1 = dx0 + (sx1 - sx0)
            out[dy0:dy1, dx0:dx1] = arr[sy0:sy1, sx0:sx1]
            return out

        self.z_gnd = _shift(self.z_gnd, np.nan)
        self.z_ceil = _shift(self.z_ceil, np.inf)
        self.wall_hits = _shift(self.wall_hits, 0.0)
        self.hit_count = _shift(self.hit_count, 0)
        self.origin_x += dx_cells * self.res
        self.origin_y += dy_cells * self.res

    def update(self, pts_world: np.ndarray, rx: float, ry: float, z_foot: float) -> None:
        self._recenter_if_needed(rx, ry)
        # Gentle temporal decay on wall_hits so moving dynamic obstacles clear when gone
        self.wall_hits *= 0.96
        if len(pts_world) == 0:
            return

        ix = np.rint((pts_world[:, 0] - self.origin_x) / self.res).astype(np.int32)
        iy = np.rint((pts_world[:, 1] - self.origin_y) / self.res).astype(np.int32)
        inb = (ix >= 0) & (ix < self.n) & (iy >= 0) & (iy < self.n)
        if not np.any(inb):
            return
        ix = ix[inb]
        iy = iy[inb]
        pz = pts_world[inb, 2]

        # Seed robot footprint (`r <= 0.16 m`) with known tire contact height `z_foot`
        r_foot = int(round(0.14 / self.res))
        icx = int(np.clip(round((rx - self.origin_x) / self.res), r_foot, self.n - r_foot - 1))
        icy = int(np.clip(round((ry - self.origin_y) / self.res), r_foot, self.n - r_foot - 1))
        sub = self.z_gnd[icy - r_foot : icy + r_foot + 1, icx - r_foot : icx + r_foot + 1]
        nan_sub = ~np.isfinite(sub)
        if np.any(nan_sub):
            sub[nan_sub] = float(z_foot)

        # Classify 3D points relative to current foot plane `z_foot`:
        # 1) Walkable / climbable / jumpable surface band: [z_foot - 0.35, z_foot + 0.415] m
        # 2) Low-overhang / tunnel / wall band: (z_foot + 0.16, z_foot + 0.92] m
        #    Distinguished from solid walls by checking whether lower wall-stem hits exist in [z_foot + 0.05, z_foot + 0.15] m!
        rel_z = pz - float(z_foot)

        tall_mask = (rel_z > 0.54) & (rel_z <= 1.05)
        if np.any(tall_mask):
            np.add.at(self.wall_hits, (iy[tall_mask], ix[tall_mask]), 1.0)

        # Surface band: up to +0.52 m so 400 mm double-stair upper decks (+Mid360 noise) are never clipped as walls!
        surf_mask = (rel_z >= -0.35) & (rel_z <= 0.52)
        if np.any(surf_mask):
            six = ix[surf_mask]
            siy = iy[surf_mask]
            spz = pz[surf_mask]
            # Per-cell max inside surface band within this single scan (captures top of stair tread over riser face!),
            # blended smoothly (alpha=0.45) with prior `z_gnd` to suppress 1.5 cm Gaussian range noise!
            flat_idx = siy * self.n + six
            order = np.argsort(flat_idx)
            f_s = flat_idx[order]
            z_s = spz[order]
            # Max z per cell in this scan:
            uniq_c, first_c, cnt_c = np.unique(f_s, return_index=True, return_counts=True)
            # Use max.reduceat to get top surface of stair tread rather than vertical riser midpoint!
            cell_top = np.maximum.reduceat(z_s, first_c)
            # Wait: if a cell ALSO has floor points right under a low 250mm bridge (`z_max - z_min > 0.16 m`),
            # then `z_min` is the floor and `z_max` is the overhead bridge beam!
            cell_bot = np.minimum.reduceat(z_s, first_c)
            uy = uniq_c // self.n
            ux = uniq_c % self.n

            is_bimodal_beam = (cnt_c >= 2) & ((cell_top - cell_bot) >= 0.16) & (cell_bot <= float(z_foot) + 0.08)
            # Normal solid surface cells:
            solid_sel = ~is_bimodal_beam
            if np.any(solid_sel):
                suy, sux = uy[solid_sel], ux[solid_sel]
                stop = cell_top[solid_sel]
                prev = self.z_gnd[suy, sux]
                # If already seen overhead beam above floor here, keep floor unless new point is near floor!
                has_ceil = self.z_ceil[suy, sux] < 0.39
                # Update EMA: fast rise on newly seen step tread, noise-filtered on flat
                blended = np.where(
                    ~np.isfinite(prev),
                    stop,
                    np.where(
                        has_ceil & (stop > prev + 0.14),
                        prev,
                        np.where(np.abs(stop - prev) <= 0.045, 0.70 * prev + 0.30 * stop, 0.20 * prev + 0.80 * stop),
                    ),
                )
                self.z_gnd[suy, sux] = blended.astype(np.float32)
                self.hit_count[suy, sux] += cnt_c[solid_sel]

            if np.any(is_bimodal_beam):
                buy, bux = uy[is_bimodal_beam], ux[is_bimodal_beam]
                bbot = cell_bot[is_bimodal_beam]
                btop = cell_top[is_bimodal_beam]
                self.z_gnd[buy, bux] = bbot.astype(np.float32)
                self.z_ceil[buy, bux] = np.minimum(self.z_ceil[buy, bux], (btop - bbot).astype(np.float32))

        # Check overhead points (`rel_z in [0.18, 0.39]`) over already-known low floor cells (`z_gnd <= z_foot + 0.08`):
        oh_mask = (rel_z >= 0.18) & (rel_z <= 0.39)
        if np.any(oh_mask):
            oix, oiy, opz = ix[oh_mask], iy[oh_mask], pz[oh_mask]
            known_gnd = self.z_gnd[oiy, oix]
            # Only treat as overhang if cell has known floor >= 0.15 m below `opz` AND adjacent neighbors also have low floor!
            is_oh = np.isfinite(known_gnd) & ((opz - known_gnd) >= 0.15) & (self.wall_hits[oiy, oix] < 2.0)
            if np.any(is_oh):
                oy, ox, oz = oiy[is_oh], oix[is_oh], opz[is_oh]
                clr = (oz - self.z_gnd[oy, ox]).astype(np.float32)
                self.z_ceil[oy, ox] = np.minimum(self.z_ceil[oy, ox], clr)


class Mid360PointCloudNavDetector:
    """Unified 50 Hz Mid-360 Point-Cloud -> `g_step`, `g_jump`, `ceiling`, & `dynamic_blocked` Engine."""

    def __init__(
        self,
        prior_map=None,
        config: Mid360Config | None = None,
        mode: str = "fusion",
    ):
        assert mode in ("fusion", "online_pc"), f"Unknown detector mode: {mode}"
        self.prior_map = prior_map
        self.cfg = config or Mid360Config.from_json()
        self.mode = mode if prior_map is not None else "online_pc"
        self.r_bl = self.cfg.r_base_lidar
        self.t_bl = self.cfg.t_base_lidar
        self.s = S_GRID_NP.copy()
        self._s_torch = torch.from_numpy(self.s)
        self._lats = np.array([0.0, 0.10, -0.10], dtype=np.float32)[:, None]
        self.submap = Mid360ScrollingSubmap(res=0.02, half_extent_m=6.40)

        # Dynamic obstacle occupancy score on `prior_map` grid (when prior_map is available)
        if self.prior_map is not None:
            shape = self.prior_map.h.shape
            self.dyn_score = np.zeros(shape, dtype=np.float32)
            self.dyn_top_z = np.full(shape, -np.inf, dtype=np.float32)
            self.dyn_blocked = np.zeros(shape, dtype=bool)
        else:
            self.dyn_score = None
            self.dyn_top_z = None
            self.dyn_blocked = None

        self.last_points_world = np.zeros((0, 3), dtype=np.float32)
        self.last_stair_pts_count = 0
        self.last_dyn_cells_count = 0
        self._tick = 0

    def reset(self, x: float = 0.0, y: float = 0.0) -> None:
        self.submap.reset(x, y)
        if self.dyn_score is not None:
            self.dyn_score.fill(0.0)
            self.dyn_top_z.fill(-np.inf)
            self.dyn_blocked.fill(False)
        self.last_points_world = np.zeros((0, 3), dtype=np.float32)
        self.last_stair_pts_count = 0
        self.last_dyn_cells_count = 0
        self._tick = 0

    def ingest_lidar_scan(
        self,
        points_lidar: np.ndarray,
        base_pos_w: np.ndarray,
        base_rot_or_quat: np.ndarray,
        z_foot: float | None = None,
    ) -> np.ndarray:
        """Register raw `/livox/lidar` 3D points (`livox_frame`) into `map` frame and update submap + dynamic obstacles."""
        self._tick += 1
        p_wb = np.asarray(base_pos_w, dtype=np.float64).reshape(3)
        rot_arr = np.asarray(base_rot_or_quat, dtype=np.float64)
        R_wb = quat_wxyz_to_rotmat(rot_arr) if rot_arr.size == 4 else rot_arr.reshape(3, 3)

        pts_l = np.asarray(points_lidar, dtype=np.float64).reshape(-1, 3)
        if len(pts_l) > 0:
            rng = np.linalg.norm(pts_l, axis=1)
            good_r = (rng >= self.cfg.min_range_m) & (rng <= self.cfg.max_range_m) & np.isfinite(rng)
            pts_l = pts_l[good_r]
            pts_b = pts_l @ self.r_bl.T + self.t_bl[None, :]
            x0, x1, y0, y1, z0, z1 = self.cfg.self_box
            not_self = ~(
                (pts_b[:, 0] >= x0)
                & (pts_b[:, 0] <= x1)
                & (pts_b[:, 1] >= y0)
                & (pts_b[:, 1] <= y1)
                & (pts_b[:, 2] >= z0)
                & (pts_b[:, 2] <= z1)
            )
            pts_b = pts_b[not_self]
            pts_w = (pts_b @ R_wb.T + p_wb[None, :]).astype(np.float32)
        else:
            pts_w = np.zeros((0, 3), dtype=np.float32)

        self.last_points_world = pts_w
        zf = float(z_foot) if z_foot is not None else float(p_wb[2] - 0.28)
        if self.prior_map is not None and z_foot is None:
            zp = float(self.prior_map.sample(p_wb[0], p_wb[1]))
            if np.isfinite(zp):
                zf = zp

        self.submap.update(pts_w, float(p_wb[0]), float(p_wb[1]), zf)
        if self.prior_map is not None:
            self._update_dynamic_obstacles(pts_w)
        return pts_w

    def _update_dynamic_obstacles(self, pts_w: np.ndarray) -> None:
        """Compare live 3D Mid-360 points against `prior_map` to detect unmapped dynamic obstacles (e.g. robots)."""
        pm = self.prior_map
        # Temporal decay so dynamic obstacles clear smoothly when they move away
        self.dyn_score *= 0.90
        if self._tick % 25 == 0:
            self.dyn_top_z = np.where(self.dyn_score > 0.4, self.dyn_top_z, -np.inf)

        if len(pts_w) > 0:
            ix = np.rint((pts_w[:, 0] - pm.x[0]) / pm.res).astype(np.int32)
            iy = np.rint((pts_w[:, 1] - pm.y[0]) / pm.res).astype(np.int32)
            inb = (ix >= 0) & (ix < len(pm.x)) & (iy >= 0) & (iy < len(pm.y))
            ix, iy, pz = ix[inb], iy[inb], pts_w[inb, 2]
            if len(pz) > 0:
                z_prior = pm.h[iy, ix]
                c_prior = pm.ceiling[iy, ix]
                sem_prior = pm.semantic[iy, ix]
                # Ignore points near known static stair risers / walls (`semantic in {2, 3}` or `blocked`)
                # and ignore known low-ceiling beams (`pz >= z_prior + c_prior - 0.05`)!
                on_open_deck = np.isfinite(z_prior) & (~pm.blocked[iy, ix]) & (sem_prior != 2) & (sem_prior != 3)
                not_known_roof = ~(np.isfinite(c_prior) & (pz >= z_prior + c_prior - 0.06))
                dz = pz - z_prior

                # Ground hits near `z_prior` actively clear stale dynamic obstacle scores!
                clear_hit = on_open_deck & (np.abs(dz) <= 0.06)
                if np.any(clear_hit):
                    self.dyn_score[iy[clear_hit], ix[clear_hit]] *= 0.35

                # Unmapped elevated obstacle hits (`0.14 m < dz <= 1.25 m` above open traversable floor/deck)
                anom = on_open_deck & not_known_roof & (dz >= 0.14) & (dz <= 1.25)
                if np.any(anom):
                    aiy, aix, adz = iy[anom], ix[anom], dz[anom]
                    np.add.at(self.dyn_score, (aiy, aix), 1.0)
                    np.maximum.at(self.dyn_top_z, (aiy, aix), adz)

        # Recompute inflated `dyn_blocked` every 3 ticks (60 ms -> negligible CPU cost!)
        if self._tick % 3 == 0:
            # Non-climbable dynamic obstacle = cell cluster with >= 3 hits reaching > 0.27 m above prior floor
            # (or narrower than a walkable 0.48 m platform!)
            core_dyn = (self.dyn_score >= 2.5) & (self.dyn_top_z >= 0.275)
            if np.any(core_dyn):
                # Require >= 3 contiguous cells (`>= 6 cm`) to reject single-ray LiDAR noise
                lbl_d, nd = label(binary_dilation(core_dyn, iterations=1))
                cnts = np.bincount(lbl_d.ravel())
                cnts[0] = 0
                valid_comp = np.isin(lbl_d, np.nonzero(cnts >= 4)[0]) & core_dyn
                self.last_dyn_cells_count = int(valid_comp.sum())
                if self.last_dyn_cells_count > 0:
                    # Inflate by 0.24 m (12 cells at 2 cm) for safe robot chassis clearance during A* avoidance!
                    self.dyn_blocked = binary_dilation(valid_comp, iterations=12)
                else:
                    self.dyn_blocked.fill(False)
            else:
                self.last_dyn_cells_count = 0
                self.dyn_blocked.fill(False)

    def _sample_online_submap(self, x: float, y: float, yaw: float, z_foot: float):
        """Extract `g_step`, `ceiling`, `profile` purely from live accumulated Mid-360 3D point cloud (`prior_map=None`)."""
        sm = self.submap
        c, sn = math.cos(yaw), math.sin(yaw)

        # Extract local 3.4 m x 3.4 m window around robot from `sm` for fast gap-filling & traversability check
        r_win = int(round(2.85 / sm.res))
        icx = int(np.clip(round((x - sm.origin_x) / sm.res), r_win, sm.n - r_win - 1))
        icy = int(np.clip(round((y - sm.origin_y) / sm.res), r_win, sm.n - r_win - 1))
        x0 = sm.origin_x + (icx - r_win) * sm.res
        y0 = sm.origin_y + (icy - r_win) * sm.res
        patch_z = sm.z_gnd[icy - r_win : icy + r_win + 1, icx - r_win : icx + r_win + 1].copy()
        patch_w = sm.wall_hits[icy - r_win : icy + r_win + 1, icx - r_win : icx + r_win + 1]
        patch_c = sm.z_ceil[icy - r_win : icy + r_win + 1, icx - r_win : icx + r_win + 1]
        ph, pw = patch_z.shape

        # Mark verified tall walls (`wall_hits >= 2.5` without low overhang) as high barrier (+2.0 m)
        is_wall = (patch_w >= 2.5) & ~(patch_c < 0.39)
        patch_z[is_wall] = float(z_foot) + 1.20

        # Fill small 1..2 pixel LiDAR scan gaps using 3x3 local median where >= 4 neighbors are finite
        for _ in range(2):
            nan_m = ~np.isfinite(patch_z)
            if not np.any(nan_m):
                break
            fin = np.isfinite(patch_z).astype(np.int32)
            nb = (
                np.pad(fin, 1)[0:ph, 0:pw]
                + np.pad(fin, 1)[0:ph, 1 : pw + 1]
                + np.pad(fin, 1)[0:ph, 2 : pw + 2]
                + np.pad(fin, 1)[1 : ph + 1, 0:pw]
                + np.pad(fin, 1)[1 : ph + 1, 2 : pw + 2]
                + np.pad(fin, 1)[2 : ph + 2, 0:pw]
                + np.pad(fin, 1)[2 : ph + 2, 1 : pw + 1]
                + np.pad(fin, 1)[2 : ph + 2, 2 : pw + 2]
            )
            med = median_filter(np.nan_to_num(patch_z, nan=float(z_foot)), size=3)
            patch_z = np.where(nan_m & (nb >= 4), med.astype(np.float32), patch_z)

        # Sample 3 forward rays (`y_local = 0, +0.10, -0.10 m`)
        xs = x + c * self.s[None, :] - sn * self._lats
        ys = y + sn * self.s[None, :] + c * self._lats
        qix = np.clip(np.rint((xs - x0) / sm.res).astype(np.int32), 0, pw - 1)
        qiy = np.clip(np.rint((ys - y0) / sm.res).astype(np.int32), 0, ph - 1)
        zs = patch_z[qiy, qix].astype(np.float32)

        # Free-space blind-cone interpolation on `s in [-0.35, +0.98] m`:
        # Unobserved NaNs inside the close-range downward blind cone (when first observed floor ahead is near `z_foot`)
        # cannot contain a >= 8 cm step (otherwise it would have intercepted the -25 deg cone!).
        i_zero = int(np.argmin(np.abs(self.s)))
        i_cone = int(np.searchsorted(self.s, 1.32))
        for r_i in range(3):
            row = zs[r_i]
            row[max(0, i_zero - 3) : min(len(row), i_zero + 3)] = np.where(
                np.isfinite(row[max(0, i_zero - 3) : min(len(row), i_zero + 3)]),
                row[max(0, i_zero - 3) : min(len(row), i_zero + 3)],
                float(z_foot),
            )
            fin_after = np.nonzero(np.isfinite(row[i_zero:]))[0]
            if len(fin_after) > 0:
                first_f = min(i_cone, i_zero + int(fin_after[0]))
                row[i_zero:first_f] = np.where(np.isfinite(row[i_zero:first_f]), row[i_zero:first_f], float(z_foot))

        feats = extract_profile_torch(self._s_torch, torch.from_numpy(zs)).numpy()
        fc = feats[0].copy()
        fl, fr = feats[1], feats[2]

        if fc[1] > 0.05:
            d1 = float(fc[0])
            # Verify 2D walkable tread width >= 0.44 m behind riser in `patch_z`
            ok_land = True
            for off in (0.18, 0.36):
                lx = x + (d1 + off) * c
                ly = y + (d1 + off) * sn
                # Check lateral width y_lat in [-0.18, +0.18] m is finite, non-wall, and consistent within +-6.5 cm
                lat_offs = np.linspace(-0.18, 0.18, 7)
                pxs = np.clip(np.rint((lx - sn * lat_offs - x0) / sm.res).astype(np.int32), 0, pw - 1)
                pys = np.clip(np.rint((ly + c * lat_offs - y0) / sm.res).astype(np.int32), 0, ph - 1)
                z_lat = patch_z[pys, pxs]
                w_lat = patch_w[pys, pxs]
                if np.sum(np.isfinite(z_lat) & (w_lat < 2.5)) < 5 or float(np.nanmax(z_lat) - np.nanmin(z_lat)) > 0.09:
                    ok_land = False
                    break
            l_match = (fl[1] > 0.05) and (abs(float(fl[1]) - float(fc[1])) <= 0.075) and (abs(float(fl[0]) - d1) <= 0.12)
            r_match = (fr[1] > 0.05) and (abs(float(fr[1]) - float(fc[1])) <= 0.075) and (abs(float(fr[0]) - d1) <= 0.12)
            both_seen = (fl[1] > 0.05) and (fr[1] > 0.05)
            ok_bilat = (l_match and r_match and abs(float(fl[0]) - float(fr[0])) <= 0.22) if both_seen else (l_match or r_match)
            if not (ok_land and ok_bilat):
                fc = EMPTY_NP.copy()

        ceil_here = float(patch_c[r_win, r_win])
        return fc, ceil_here, zs[0]

    def sample(self, x: float, y: float, yaw: float, z_foot: float = 0.0):
        """Compute `g_step = [d1, h1, d2, h2]`, `ceiling`, and 1D profile at 50 Hz."""
        c, sn = math.cos(yaw), math.sin(yaw)

        # Count live 3D Mid-360 points in forward stair box (`s in [0.05, 2.20] m, |y_l| <= 0.24 m`) for HUD/telemetry
        if len(self.last_points_world) > 0:
            dx = self.last_points_world[:, 0] - float(x)
            dy = self.last_points_world[:, 1] - float(y)
            sx = c * dx + sn * dy
            sy = -sn * dx + c * dy
            sz = self.last_points_world[:, 2] - float(z_foot)
            self.last_stair_pts_count = int(
                np.sum((sx >= 0.05) & (sx <= 2.20) & (np.abs(sy) <= 0.24) & (sz >= 0.04) & (sz <= 0.42))
            )
        else:
            self.last_stair_pts_count = 0

        if self.mode == "online_pc" or self.prior_map is None:
            return self._sample_online_submap(x, y, yaw, z_foot)

        # Fusion mode: Prior Map + Live Mid-360 Point Cloud (dynamic obstacle veto + unmapped step fusion)
        pm = self.prior_map
        xs = x + c * self.s[None, :] - sn * self._lats
        ys = y + sn * self.s[None, :] + c * self._lats
        zs = pm.sample(xs, ys).astype(np.float32)

        # Overlay any verified unmapped obstacles / dynamic walls from live Mid-360 onto the 3 forward rays!
        if self.last_dyn_cells_count > 0:
            qix = np.clip(np.rint((xs - pm.x[0]) / pm.res).astype(np.int32), 0, len(pm.x) - 1)
            qiy = np.clip(np.rint((ys - pm.y[0]) / pm.res).astype(np.int32), 0, len(pm.y) - 1)
            dyn_hit = (self.dyn_score[qiy, qix] >= 2.5) & (self.dyn_top_z[qiy, qix] >= 0.275)
            # Raising blocked dynamic cells to +1.5 m causes `extract_profile_torch`'s `blocked_front` logic
            # to reject BOTH the dynamic robot itself (`h_seg > 0.27 m`) AND any staircase hidden behind it!
            zs = np.where(dyn_hit, zs + 1.50, zs).astype(np.float32)

        # Also fuse unmapped climbable temporary platforms (`0.08 <= dz <= 0.26 m`, non-wall) from `submap`
        sm = self.submap
        if sm.initialized:
            six = np.clip(np.rint((xs - sm.origin_x) / sm.res).astype(np.int32), 0, sm.n - 1)
            siy = np.clip(np.rint((ys - sm.origin_y) / sm.res).astype(np.int32), 0, sm.n - 1)
            z_live = sm.z_gnd[siy, six]
            cnt_live = sm.hit_count[siy, six]
            wall_live = sm.wall_hits[siy, six]
            unmapped_step = (
                np.isfinite(z_live)
                & np.isfinite(zs)
                & (cnt_live >= 2)
                & (wall_live < 2.0)
                & ((z_live - zs) >= 0.075)
                & ((z_live - zs) <= 0.265)
            )
            if np.any(unmapped_step):
                zs = np.where(unmapped_step, z_live, zs).astype(np.float32)

        feats = extract_profile_torch(self._s_torch, torch.from_numpy(zs)).numpy()
        fc = feats[0].copy()
        fl, fr = feats[1], feats[2]

        if fc[1] > 0.05:
            d1 = float(fc[0])
            lx1, ly1 = x + (d1 + 0.18) * c, y + (d1 + 0.18) * sn
            lx2, ly2 = x + (d1 + 0.36) * c, y + (d1 + 0.36) * sn
            ok_land = pm.is_traversable(lx1, ly1) and pm.is_traversable(lx2, ly2)
            # Dynamic obstacle veto on landing zone!
            if ok_land and self.last_dyn_cells_count > 0:
                if self.dyn_blocked[pm.index(lx1, ly1)] or self.dyn_blocked[pm.index(lx2, ly2)]:
                    ok_land = False
            l_match = (fl[1] > 0.05) and (abs(float(fl[1]) - float(fc[1])) <= 0.065) and (abs(float(fl[0]) - d1) <= 0.105)
            r_match = (fr[1] > 0.05) and (abs(float(fr[1]) - float(fc[1])) <= 0.065) and (abs(float(fr[0]) - d1) <= 0.105)
            both_seen = (fl[1] > 0.05) and (fr[1] > 0.05)
            ok_bilat = (l_match and r_match and abs(float(fl[0]) - float(fr[0])) <= 0.21) if both_seen else (l_match or r_match)
            if not (ok_land and ok_bilat):
                fc = EMPTY_NP.copy()

        if fc[3] > 0.05:
            d2 = float(fc[2])
            lx1, ly1 = x + (d2 + 0.18) * c, y + (d2 + 0.18) * sn
            lx2, ly2 = x + (d2 + 0.36) * c, y + (d2 + 0.36) * sn
            ok_land2 = pm.is_traversable(lx1, ly1) and pm.is_traversable(lx2, ly2)
            if ok_land2 and self.last_dyn_cells_count > 0:
                if self.dyn_blocked[pm.index(lx1, ly1)] or self.dyn_blocked[pm.index(lx2, ly2)]:
                    ok_land2 = False
            if not ok_land2:
                fc[2], fc[3] = 1.60, 0.0

        node = pm.index(x, y)
        return fc, float(pm.ceiling[node]), zs[0]

    def sample_jump(self, x: float, y: float, yaw: float, z_ref: float | None = None, z_foot: float = 0.0) -> np.ndarray:
        """Compute `g_jump = [d_front, d_back, z_top_rel, z_land_rel]` from fused or online Mid-360 point cloud."""
        c, sn = math.cos(yaw), math.sin(yaw)
        rx = x + c * self.s
        ry = y + sn * self.s

        if self.mode == "online_pc" or self.prior_map is None:
            sm = self.submap
            six = np.clip(np.rint((rx - sm.origin_x) / sm.res).astype(np.int32), 0, sm.n - 1)
            siy = np.clip(np.rint((ry - sm.origin_y) / sm.res).astype(np.int32), 0, sm.n - 1)
            zg = sm.z_gnd[siy, six].copy()
            ceil = sm.z_ceil[siy, six].copy()
            wall = sm.wall_hits[siy, six]
            zg = np.where((wall >= 2.5) & ~(ceil < 0.39), float(z_foot) + 1.20, zg)
            i_zero = int(np.argmin(np.abs(self.s)))
            fin_after = np.nonzero(np.isfinite(zg[i_zero:]))[0]
            first_f = (i_zero + int(fin_after[0])) if len(fin_after) > 0 else min(len(zg), i_zero + 45)
            zg[:first_f] = np.where(np.isfinite(zg[:first_f]), zg[:first_f], float(z_foot if z_ref is None else z_ref))
            ze = np.where(np.isfinite(ceil) & (ceil < 0.39), zg + ceil + 0.021, zg).astype(np.float32)
        else:
            pm = self.prior_map
            zg = pm.sample(rx, ry).astype(np.float32)
            ceil = pm.sample_ceiling(rx, ry).astype(np.float32)
            if self.last_dyn_cells_count > 0:
                qix = np.clip(np.rint((rx - pm.x[0]) / pm.res).astype(np.int32), 0, len(pm.x) - 1)
                qiy = np.clip(np.rint((ry - pm.y[0]) / pm.res).astype(np.int32), 0, len(pm.y) - 1)
                dyn_hit = (self.dyn_score[qiy, qix] >= 2.5) & (self.dyn_top_z[qiy, qix] >= 0.275)
                zg = np.where(dyn_hit, zg + 1.50, zg).astype(np.float32)
            ze = np.where(np.isfinite(ceil) & (ceil < 0.38), zg + ceil + 0.021, zg).astype(np.float32)

        zg_t = torch.from_numpy(zg).unsqueeze(0)
        ze_t = torch.from_numpy(ze).unsqueeze(0)
        zr_t = None if z_ref is None else torch.tensor([float(z_ref)], dtype=torch.float32)
        return extract_jump_feature_torch(self._s_torch, ze_t, zg_t, zr_t)[0].numpy()

    def is_path_blocked(self, path: list[tuple[float, float]], x: float, y: float, lookahead_m: float = 2.8) -> bool:
        """Return True if any upcoming waypoint segment within `lookahead_m` enters `dyn_blocked`."""
        if self.prior_map is None or self.last_dyn_cells_count == 0 or len(path) < 2:
            return False
        pm = self.prior_map
        for i in range(len(path) - 1):
            p0, p1 = path[i], path[i + 1]
            if math.hypot(p0[0] - x, p0[1] - y) > lookahead_m and math.hypot(p1[0] - x, p1[1] - y) > lookahead_m:
                continue
            a = pm.index(*p0)
            b = pm.index(*p1)
            n = max(2, int(math.dist(a, b) * 2) + 1)
            pts = np.rint(np.linspace(a, b, n)).astype(np.int32)
            if np.any(self.dyn_blocked[pts[:, 0], pts[:, 1]]):
                return True
        return False

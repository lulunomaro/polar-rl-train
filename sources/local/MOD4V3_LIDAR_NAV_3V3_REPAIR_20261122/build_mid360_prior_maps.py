"""Offline & Pre-Match Livox Mid-360 3D Point-Cloud (.pcd) -> 2.5D Multi-Layer Nav & Stair Map Builder.

Supports two workflows with identical reconstruction math:
1. Real-Robot / FAST-LIO2 `.pcd` import:
   `python build_mid360_prior_maps.py --from-pcd my_fastlio_map.pcd --name custom_arena`
   Converts any gravity-aligned FAST-LIO2 / Point-LIO `.pcd` point cloud into:
   - `maps/elevation/<name>.npz` & `maps/mid360_prior/<name>_pcd_nav25d.npz` (2 cm 2.5D height, ceiling, semantic, valid)
   - `maps/mid360_prior/<name>_stairs.json` (all detected climbable stair risers, step heights, and approach normals)
2. Pre-building all official competition arenas (`RMUL 2027 3v3`, `RMUC 2027 5v5`, `suite_proving`, etc.) via
   multi-pose simulated Livox Mid-360 3D survey scans -> `.pcd` prior point clouds + `.npz` reconstructed maps.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
import numpy as np
from scipy.ndimage import binary_closing, binary_dilation, distance_transform_edt, label, maximum_filter, median_filter

from nav_common import HERE, put
from mid360_sensor import LivoxMid360Sensor, Mid360Config, load_pcd, rpy_deg_to_rotmat, save_pcd_binary

ALL_COURSES = (
    "suite_rmul2027",
    "suite_rmuc2027",
    "suite_proving",
    "step_20",
    "oblique_20",
    "oblique_20_negative",
    "curb_11",
    "rm27_west_400",
    "rm27_east_400",
    "flat",
    "rough_L9",
    "serial_17",
)


def voxel_downsample_xyz(
    xyz: np.ndarray,
    intensity: np.ndarray | None = None,
    voxel_size: float = 0.025,
) -> tuple[np.ndarray, np.ndarray]:
    """Fast deterministic 3D voxel centroid downsampling in pure NumPy."""
    pts = np.asarray(xyz, dtype=np.float32).reshape(-1, 3)
    if len(pts) == 0:
        return pts, np.zeros((0,), dtype=np.float32)
    inten = pts[:, 2].copy() if intensity is None else np.asarray(intensity, dtype=np.float32).reshape(len(pts))
    mins = pts.min(axis=0)
    q = np.floor((pts - mins[None, :]) / float(voxel_size)).astype(np.int64)
    # Pack 3D integer coordinates into 64-bit keys (supports spans up to +-20,000 voxels = +-500 m)
    span_y = int(q[:, 1].max()) + 2
    span_z = int(q[:, 2].max()) + 2
    keys = (q[:, 0] * span_y + q[:, 1]) * span_z + q[:, 2]
    order = np.argsort(keys, kind="mergesort")
    keys_s = keys[order]
    pts_s = pts[order]
    int_s = inten[order]
    uniq, first, counts = np.unique(keys_s, return_index=True, return_counts=True)
    # Filter single-ray isolated flyer noise when total cloud is dense
    sum_x = np.add.reduceat(pts_s[:, 0].astype(np.float64), first)
    sum_y = np.add.reduceat(pts_s[:, 1].astype(np.float64), first)
    sum_z = np.add.reduceat(pts_s[:, 2].astype(np.float64), first)
    sum_i = np.add.reduceat(int_s.astype(np.float64), first)
    inv = 1.0 / np.maximum(counts, 1)
    out_xyz = np.stack((sum_x * inv, sum_y * inv, sum_z * inv), axis=1).astype(np.float32)
    out_int = (sum_i * inv).astype(np.float32)
    return out_xyz, out_int


def reconstruct_nav25d_from_pointcloud(
    points_xyz: np.ndarray,
    res: float = 0.02,
    bounds: tuple[float, float, float, float] | None = None,
    z_clip: tuple[float, float] = (-0.50, 2.40),
    min_pts_per_voxel: int = 1,
) -> dict[str, np.ndarray]:
    """Reconstruct multi-layer 2 cm 2.5D `height`, `ceiling`, `semantic`, `valid` purely from 3D point cloud.

    Automatically separates:
    - Walkable ground & stair treads (`height`),
    - Low overhead bridge beams / tunnel roofs with open space underneath (`ceiling = z_underside - height`),
    - Climbable stairs (`semantic == 2`, `0.08 <= dh <= 0.255 m`),
    - Ramps / rough terrain (`semantic == 1`),
    - Tall walls / cliffs (`semantic == 3`).
    """
    pts = np.asarray(points_xyz, dtype=np.float32).reshape(-1, 3)
    pts = pts[np.isfinite(pts).all(axis=1)]
    pts = pts[(pts[:, 2] >= z_clip[0]) & (pts[:, 2] <= z_clip[1])]
    if len(pts) == 0:
        raise ValueError("Input point cloud is empty after finite/z clipping")

    if bounds is None:
        xmin, ymin = pts[:, 0].min() - 0.10, pts[:, 1].min() - 0.10
        xmax, ymax = pts[:, 0].max() + 0.10, pts[:, 1].max() + 0.10
        bounds = (float(xmin), float(xmax), float(ymin), float(ymax))

    x = np.arange(bounds[0], bounds[1] + res * 0.1, res, dtype=np.float32)
    y = np.arange(bounds[2], bounds[3] + res * 0.1, res, dtype=np.float32)
    nx, ny = len(x), len(y)

    ix = np.rint((pts[:, 0] - x[0]) / res).astype(np.int32)
    iy = np.rint((pts[:, 1] - y[0]) / res).astype(np.int32)
    inb = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    pts = pts[inb]
    ix = ix[inb]
    iy = iy[inb]

    # 3D occupancy grid (ny, nx, nz) at 2 cm vertical resolution for exact floor vs overhang gap separation!
    z0 = float(np.percentile(pts[:, 2], 0.2)) - 0.06
    z1 = min(float(z_clip[1]), z0 + 2.20)
    vz = 0.02
    nz = max(16, int(math.ceil((z1 - z0) / vz)) + 1)
    iz = np.clip(np.floor((pts[:, 2] - z0) / vz).astype(np.int32), 0, nz - 1)

    flat_xy = iy * nx + ix
    n_cells = ny * nx

    # Accumulate 3D voxel counts and exact mean z per occupied 3D voxel via sparse sorting
    vox_key = flat_xy.astype(np.int64) * nz + iz.astype(np.int64)
    order = np.argsort(vox_key, kind="mergesort")
    vk_s = vox_key[order]
    pz_s = pts[order, 2].astype(np.float64)
    uniq_vk, first_vk, cnt_vk = np.unique(vk_s, return_index=True, return_counts=True)
    if min_pts_per_voxel > 1:
        keep = cnt_vk >= min_pts_per_voxel
        uniq_vk = uniq_vk[keep]
        first_vk = first_vk[keep]
        cnt_vk = cnt_vk[keep]
        # Recompute sum cleanly via segments
    # Sum z per unique voxel
    # Note: if filtered, use bincount on original or compute before filtering
    all_uniq, all_first, all_cnt = np.unique(vk_s, return_index=True, return_counts=True)
    all_mean_z = (np.add.reduceat(pz_s, all_first) / np.maximum(all_cnt, 1)).astype(np.float32)
    if min_pts_per_voxel > 1:
        mask_v = all_cnt >= min_pts_per_voxel
        all_uniq = all_uniq[mask_v]
        all_mean_z = all_mean_z[mask_v]

    occ = np.zeros((n_cells, nz), dtype=bool)
    vox_z = np.full((n_cells, nz), np.nan, dtype=np.float32)
    u_xy = (all_uniq // nz).astype(np.int64)
    u_iz = (all_uniq % nz).astype(np.int32)
    occ[u_xy, u_iz] = True
    vox_z[u_xy, u_iz] = all_mean_z

    # Exact single-column vertical air-gap check (>= 8 empty 2 cm bins = >= 16 cm clear vertical air gap)
    # so solid walls (which have NO floor points underneath them!) NEVER get misclassified as overhangs!
    occ_b = occ.copy()
    occ_b[:, 1:-1] |= occ[:, :-2] & occ[:, 2:]

    iz_idx = np.arange(nz, dtype=np.int32)[None, :]
    INF_Z = nz + 10
    has_any = occ_b.any(axis=1)
    iz_low = np.where(occ_b, iz_idx, INF_Z).min(axis=1)

    empty_c = ~occ_b
    empty_8 = np.ones((n_cells, nz - 7), dtype=bool)
    for k in range(8):
        empty_8 &= empty_c[:, k : nz - 7 + k]
    e_idx = np.arange(nz - 7, dtype=np.int32)[None, :]
    valid_air_gap = empty_8 & (e_idx > iz_low[:, None])
    gap_start = np.where(valid_air_gap, e_idx, INF_Z).min(axis=1)

    below_gap = occ & (iz_idx < gap_start[:, None])
    iz_gnd_top = np.where(below_gap, iz_idx, -1).max(axis=1)
    above_gap = occ & (iz_idx >= (gap_start + 8)[:, None])
    iz_ceil_bot = np.where(above_gap, iz_idx, INF_Z).min(axis=1)

    height_flat = np.full(n_cells, np.nan, dtype=np.float32)
    ceiling_flat = np.full(n_cells, np.inf, dtype=np.float32)

    valid_gnd = has_any & (iz_gnd_top >= 0)
    vg_cells = np.nonzero(valid_gnd)[0]
    height_flat[vg_cells] = vox_z[vg_cells, iz_gnd_top[vg_cells]]

    has_overhang = valid_gnd & (iz_ceil_bot < nz)
    oh_cells = np.nonzero(has_overhang)[0]
    if len(oh_cells) > 0:
        ceil_z = vox_z[oh_cells, iz_ceil_bot[oh_cells]]
        clearance_h = ceil_z - height_flat[oh_cells]
        good_oh = clearance_h >= 0.18
        ceiling_flat[oh_cells[good_oh]] = clearance_h[good_oh]

    height = height_flat.reshape(ny, nx)
    ceiling = ceiling_flat.reshape(ny, nx)

    # Despike roof-only pixels INSIDE verified overhang regions (where >= 3 neighbors in 5x5 saw BOTH floor & ceiling,
    # whereas this sparse 2 cm pixel happened to catch only the roof/beam and missed the floor ray!):
    oh_mask = np.isfinite(ceiling) & (ceiling < 1.90)
    if np.any(oh_mask):
        from scipy.ndimage import uniform_filter, minimum_filter
        oh_nb_count = np.rint(uniform_filter(oh_mask.astype(np.float32), size=5, mode="constant") * 25.0).astype(np.int32)
        oh_floor_min = minimum_filter(np.where(oh_mask, height, 99.0), size=5)
        oh_ceil_min = minimum_filter(np.where(oh_mask, ceiling, 99.0), size=5)
        roof_spike_in_tunnel = (~oh_mask) & (oh_nb_count >= 3) & np.isfinite(height) & (oh_floor_min < 50.0) & ((height - oh_floor_min) >= 0.16)
        height = np.where(roof_spike_in_tunnel, oh_floor_min, height).astype(np.float32)
        ceiling = np.where(roof_spike_in_tunnel, oh_ceil_min, ceiling).astype(np.float32)
        # Also fill empty NaN pixels inside verified overhang zones before Voronoi so roof edges don't bleed in
        nan_in_tunnel = (~np.isfinite(height)) & (oh_nb_count >= 4) & (oh_floor_min < 50.0)
        height = np.where(nan_in_tunnel, oh_floor_min, height).astype(np.float32)
        ceiling = np.where(nan_in_tunnel, oh_ceil_min, ceiling).astype(np.float32)

    # Watertight Nearest-Voronoi interpolation within 0.32 m (16 cells) so 2~4 cm downsampled FAST-LIO2 .pcd maps
    # have ZERO interior NaN holes while keeping 90-deg stair risers 1-pixel (2 cm) razor-sharp!
    nan_mask = ~np.isfinite(height)
    if np.any(nan_mask) and np.any(~nan_mask):
        edt_cells, (near_iy, near_ix) = distance_transform_edt(nan_mask, return_indices=True)
        fill_ok = nan_mask & ((edt_cells * res) <= 0.32)
        height = np.where(fill_ok, height[near_iy, near_ix], height).astype(np.float32)

    # Light 3x3 outlier despike ONLY where local 3x3 height variation is flat (< 3.5 cm) so stair edges stay sharp!
    h_pad = np.nan_to_num(height, nan=0.0)
    h_med3 = median_filter(h_pad, size=3).astype(np.float32)
    flat_patch = np.isfinite(height) & (np.abs(height - h_med3) <= 0.035)
    height = np.where(flat_patch, 0.5 * height + 0.5 * h_med3, height).astype(np.float32)

    # Propagate low-ceiling beam clearance across 1..2 cell ray gaps inside overhead beams
    has_low_ceil = np.isfinite(ceiling) & (ceiling < 0.40)
    if has_low_ceil.any():
        closed_ceil = binary_closing(has_low_ceil, structure=np.ones((3, 3), dtype=bool))
        c_med = median_filter(np.where(np.isfinite(ceiling), ceiling, 9.9), size=3).astype(np.float32)
        ceiling = np.where(closed_ceil & ~has_low_ceil & (c_med < 0.40), c_med, ceiling)

    valid = np.isfinite(height)
    dy, dx = np.gradient(np.nan_to_num(height, nan=0.0), res)
    diffx = np.abs(np.diff(height, axis=1, prepend=height[:, :1]))
    diffy = np.abs(np.diff(height, axis=0, prepend=height[:1, :]))
    dh = np.maximum(diffx, diffy)
    semantic = np.zeros_like(height, dtype=np.uint8)
    semantic[(np.hypot(dx, dy) > 0.04) & (dh < 0.075)] = 1  # ramp / rough
    semantic[(dh >= 0.08) & (dh <= 0.255)] = 2               # climbable stair riser
    semantic[(dh >= 0.26) | ~valid] = 3                      # unwalkable wall / cliff
    semantic[ceiling < 0.36] = 4                             # low-ceiling tunnel / jumpable bridge beam

    return dict(
        x=x,
        y=y,
        height=height,
        ceiling=ceiling,
        semantic=semantic,
        valid=valid,
        resolution=np.float32(res),
    )


def extract_stair_corridors_from_map(map_dict: dict[str, np.ndarray]) -> list[dict]:
    """Identify all genuine climbable stair risers, heights, widths, and horizontal climb normals from 2.5D map."""
    x = map_dict["x"]
    y = map_dict["y"]
    h = map_dict["height"]
    valid = map_dict["valid"]
    ceil = map_dict["ceiling"]
    res = float(map_dict["resolution"])

    step_edge = np.zeros_like(valid)
    for axis in (0, 1):
        ch = np.abs(np.diff(h, axis=axis)) >= 0.065
        if axis == 0:
            step_edge[:-1] |= ch
            step_edge[1:] |= ch
        else:
            step_edge[:, :-1] |= ch
            step_edge[:, 1:] |= ch
    smooth = valid & (~step_edge) & (ceil >= 0.35)
    rad = distance_transform_edt(smooth) * res
    deck = binary_dilation(rad >= 0.18, iterations=4) & valid

    # Compute 8 cm baseline gradient so directional sectors split L/U-shaped corners cleanly into straight stair lines!
    h_clean = np.nan_to_num(h, nan=float(np.nanmedian(h)))
    gx = np.zeros_like(h_clean)
    gy = np.zeros_like(h_clean)
    gx[:, 2:-2] = (h_clean[:, 4:] - h_clean[:, :-4]) / (4.0 * res)
    gy[2:-2, :] = (h_clean[4:, :] - h_clean[:-4, :]) / (4.0 * res)
    gmag = np.hypot(gx, gy)
    ang = np.arctan2(gy, gx)  # [-pi, pi]
    # Shift by +pi/8 (+22.5 deg) so sector centers sit cleanly on 0, 45, 90, 135, 180, -135, -90, -45 deg!
    sector = np.floor(((ang + math.pi + math.pi / 8.0) / (2.0 * math.pi)) * 8.0).astype(np.int32) % 8

    riser_base = (map_dict["semantic"] == 2) & binary_dilation(deck, iterations=8) & (gmag > 0.5)
    stairs = []
    for sec in range(8):
        sec_mask = binary_closing(riser_base & (sector == sec), structure=np.ones((3, 3), dtype=bool))
        lbl, n_comp = label(sec_mask)
        for cid in range(1, n_comp + 1):
            ys, xs = np.nonzero(lbl == cid)
            if len(xs) < 10:
                continue
            span_m = float(math.hypot(x[xs.max()] - x[xs.min()], y[ys.max()] - y[ys.min()]))
            if span_m < 0.42:
                continue
            # Pick median pixel along the riser segment (lies directly on the riser even if slightly curved)
            med_order = np.argsort(xs * 1.0 + ys * 1.0)
            mid_k = med_order[len(med_order) // 2]
            cx = float(x[xs[mid_k]])
            cy = float(y[ys[mid_k]])
            vx = float(np.mean(gx[ys, xs]))
            vy = float(np.mean(gy[ys, xs]))
            norm = math.hypot(vx, vy)
            if norm < 1e-4:
                continue
            nx_u, ny_u = vx / norm, vy / norm
            ix_lo = int(np.clip(round((cx - 0.24 * nx_u - x[0]) / res), 0, len(x) - 1))
            iy_lo = int(np.clip(round((cy - 0.24 * ny_u - y[0]) / res), 0, len(y) - 1))
            ix_hi = int(np.clip(round((cx + 0.24 * nx_u - x[0]) / res), 0, len(x) - 1))
            iy_hi = int(np.clip(round((cy + 0.24 * ny_u - y[0]) / res), 0, len(y) - 1))
            if not (deck[iy_lo, ix_lo] and deck[iy_hi, ix_hi]):
                continue
            z_lo = float(h[iy_lo, ix_lo])
            z_hi = float(h[iy_hi, ix_hi])
            step_h = z_hi - z_lo
            if not (0.075 <= step_h <= 0.270):
                continue
            stairs.append(
                dict(
                    id=len(stairs),
                    center_xy=[round(cx, 3), round(cy, 3)],
                    width_m=round(span_m, 3),
                    z_low_m=round(z_lo, 4),
                    z_high_m=round(z_hi, 4),
                    step_height_m=round(step_h, 4),
                    climb_normal_xy=[round(nx_u, 4), round(ny_u, 4)],
                    climb_yaw_deg=round(math.degrees(math.atan2(ny_u, nx_u)), 1),
                )
            )
    return stairs


def scan_arena_with_mid360(course: str) -> tuple[np.ndarray, np.ndarray, dict]:
    """Simulate a pre-match multi-pose Livox Mid-360 survey across `course` and return downsampled 3D cloud."""
    import mujoco as mj
    from nav_maps import extent, stage_scene

    t0 = time.perf_counter()
    meta = stage_scene(course)
    m = mj.MjModel.from_binary_path(meta["mjb_path"])
    for g in range(m.ngeom):
        m.geom_group[g] = 3 if m.body_weldid[m.geom_bodyid[g]] == 0 and (m.geom_contype[g] or m.geom_conaffinity[g]) else 2
        if m.geom_group[g] == 3 and m.geom_rgba[g, 3] == 0:
            m.geom_rgba[g, 3] = 0.0001
    d = mj.MjData(m)
    mj.mj_forward(m, d)

    bounds = extent(course)
    # Pre-match handheld/robot Mid-360 survey grid: spacing ~1.35 m across arena at two handheld heights
    # (0.42 m robot height + 1.05 m handheld sweep so every stair tread, riser & overhang underside is hit cleanly!)
    span_x = bounds[1] - bounds[0]
    span_y = bounds[3] - bounds[2]
    step_xy = 1.15 if (span_x * span_y) > 150.0 else 1.05
    xs = np.arange(bounds[0] + 0.55, bounds[1] - 0.45, step_xy)
    ys = np.arange(bounds[2] + 0.55, bounds[3] - 0.45, step_xy)

    cfg = Mid360Config.from_json()
    # Clean mapping mode (low 4 mm mapping noise after FAST-LIO2 multi-scan averaging)
    cfg_map = Mid360Config(
        pos_base_m=cfg.pos_base_m,
        rpy_deg=cfg.rpy_deg,
        el_min_deg=cfg.el_min_deg,
        el_max_deg=cfg.el_max_deg,
        min_range_m=0.10,
        max_range_m=30.0,
        points_per_subframe=10_000,
        range_noise_std_m=0.004,
        dropout_prob=0.0,
    )
    sensor = LivoxMid360Sensor(cfg_map, seed=100)
    grp = np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8)
    gid1 = np.zeros(1, dtype=np.int32)
    down = np.array([0.0, 0.0, -1.0], dtype=np.float64)

    from lidar_nav_planner import ElevationMap
    em_ref = ElevationMap(course)

    clouds = []
    intens = []
    n_poses = 0
    for yy in ys:
        for xx in xs:
            iy_r, ix_r = em_ref.index(float(xx), float(yy))
            if em_ref.blocked[iy_r, ix_r] or not em_ref.valid[iy_r, ix_r]:
                continue
            z_floor = float(em_ref.h[iy_r, ix_r])
            c_clear = float(em_ref.ceiling[iy_r, ix_r])
            if c_clear < 0.30:
                continue
            max_z_off = min(0.92, c_clear - 0.14) if np.isfinite(c_clear) else 0.92
            low_z_off = min(0.32, max(0.18, max_z_off - 0.04))
            for yaw_deg, z_off in ((0.0, low_z_off), (180.0, low_z_off), (90.0, max_z_off), (-90.0, max_z_off)):
                R_wb = rpy_deg_to_rotmat(0.0, 0.0, yaw_deg)
                p_wb = np.array([float(xx), float(yy), z_floor + z_off], dtype=np.float64)
                scan = sensor.scan(m, d, p_wb, R_wb, n_rays=8_000, add_noise=True, return_normals_w=True)
                pw = scan["points_world"]
                nw = scan["normals_world"]
                # Keep points inside course bounds
                inb = (
                    (pw[:, 0] >= bounds[0] - 0.05)
                    & (pw[:, 0] <= bounds[1] + 0.05)
                    & (pw[:, 1] >= bounds[2] - 0.05)
                    & (pw[:, 1] <= bounds[3] + 0.05)
                )
                if np.any(inb):
                    clouds.append(pw[inb])
                    # Intensity = |nz| in [0, 1] (1.0 = horizontal floor/tread, 0.0 = vertical riser/wall)
                    intens.append(np.abs(nw[inb, 2]).astype(np.float32))
                n_poses += 1

    raw_xyz = np.concatenate(clouds, axis=0)
    raw_int = np.concatenate(intens, axis=0)
    vox_size = 0.020
    ds_xyz, ds_int = voxel_downsample_xyz(raw_xyz, raw_int, voxel_size=vox_size)
    info = dict(
        course=course,
        bounds=list(bounds),
        survey_poses=n_poses,
        raw_points=int(len(raw_xyz)),
        voxel_size_m=vox_size,
        downsampled_points=int(len(ds_xyz)),
        scan_elapsed_s=round(time.perf_counter() - t0, 3),
    )
    return ds_xyz, ds_int, info


def build_prior_for_course(course: str, prior_dir: Path | None = None) -> dict:
    from nav_maps import build_elevation, extent

    out_dir = prior_dir or (HERE / "maps" / "mid360_prior")
    out_dir.mkdir(parents=True, exist_ok=True)
    elev_path = HERE / "maps" / "elevation" / f"{course}.npz"
    if not elev_path.exists():
        build_elevation(course)

    pcd_path = out_dir / f"{course}_prior.pcd"
    if pcd_path.is_file() and pcd_path.stat().st_size > 1024:
        loaded_xyz, _ = load_pcd(pcd_path)
        scan_info = dict(
            course=course,
            bounds=list(extent(course)),
            survey_poses=-1,
            raw_points=int(len(loaded_xyz)),
            voxel_size_m=0.030 if course == "suite_rmuc2027" else 0.020,
            downsampled_points=int(len(loaded_xyz)),
            scan_elapsed_s=0.0,
        )
    else:
        ds_xyz, ds_int, scan_info = scan_arena_with_mid360(course)
        save_pcd_binary(pcd_path, ds_xyz, ds_int)
        loaded_xyz, _ = load_pcd(pcd_path)
    t_rec = time.perf_counter()
    rec = reconstruct_nav25d_from_pointcloud(loaded_xyz, res=0.02, bounds=extent(course))
    rec_elapsed = time.perf_counter() - t_rec

    nav_npz_path = out_dir / f"{course}_pcd_nav25d.npz"
    np.savez_compressed(
        nav_npz_path,
        x=rec["x"],
        y=rec["y"],
        height=rec["height"],
        ceiling=rec["ceiling"],
        semantic=rec["semantic"],
        valid=rec["valid"],
        resolution=rec["resolution"],
        course=course,
        source_pcd=pcd_path.name,
        coordinate_reference="robot_base_center_horizontal",
    )

    stairs = extract_stair_corridors_from_map(rec)
    stairs_path = out_dir / f"{course}_stairs.json"
    put(stairs_path, dict(course=course, source_pcd=pcd_path.name, stair_count=len(stairs), stairs=stairs))

    # Accuracy audit against CAD collision ground-truth `maps/elevation/<course>.npz` on walkable interior (`em_gt.traversable`)
    from lidar_nav_planner import ElevationMap
    em_gt_chk = ElevationMap(course)
    gt = np.load(elev_path)
    gt_h = gt["height"]
    mask_walk = em_gt_chk.traversable & np.isfinite(gt_h) & np.isfinite(rec["height"])
    diff_mm = 1000.0 * np.abs(rec["height"][mask_walk] - gt_h[mask_walk]) if np.any(mask_walk) else np.zeros(1)
    gt_low_ceil = int((gt["ceiling"] < 0.36).sum())
    rec_low_ceil = int((rec["ceiling"] < 0.36).sum())

    summary = dict(
        **scan_info,
        pcd_file=f"maps/mid360_prior/{pcd_path.name}",
        pcd_bytes=int(pcd_path.stat().st_size),
        nav25d_file=f"maps/mid360_prior/{nav_npz_path.name}",
        stairs_file=f"maps/mid360_prior/{stairs_path.name}",
        reconstruct_elapsed_s=round(rec_elapsed, 3),
        grid_shape=list(rec["height"].shape),
        walkable_mae_mm=round(float(diff_mm.mean()), 2),
        walkable_p95_mm=round(float(np.percentile(diff_mm, 95.0)), 2),
        gt_low_ceiling_cells=gt_low_ceil,
        pcd_low_ceiling_cells=rec_low_ceil,
        detected_stair_corridors=len(stairs),
        stairs_preview=stairs[:8],
    )
    print(
        f"[Mid360 Prior] {course}: {scan_info['downsampled_points']} pts -> {pcd_path.name} "
        f"(MAE={summary['walkable_mae_mm']:.2f}mm, stairs={len(stairs)}, low_ceil={rec_low_ceil})",
        flush=True,
    )
    return summary


def import_external_pcd(pcd_file: Path, name: str, install_as_course: bool = True) -> dict:
    """Import a real-robot FAST-LIO2 `.pcd` map and generate ready-to-run Nav4D `.npz` + `_stairs.json`."""
    out_dir = HERE / "maps" / "mid360_prior"
    out_dir.mkdir(parents=True, exist_ok=True)
    xyz, _ = load_pcd(pcd_file)
    rec = reconstruct_nav25d_from_pointcloud(xyz, res=0.02, bounds=None)
    nav_npz = out_dir / f"{name}_pcd_nav25d.npz"
    payload = dict(
        x=rec["x"],
        y=rec["y"],
        height=rec["height"],
        ceiling=rec["ceiling"],
        semantic=rec["semantic"],
        valid=rec["valid"],
        resolution=rec["resolution"],
        course=name,
        source_pcd=str(pcd_file),
        coordinate_reference="robot_base_center_horizontal",
    )
    np.savez_compressed(nav_npz, **payload)
    if install_as_course:
        elev_out = HERE / "maps" / "elevation" / f"{name}.npz"
        elev_out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(elev_out, **payload)
    stairs = extract_stair_corridors_from_map(rec)
    stairs_path = out_dir / f"{name}_stairs.json"
    info = dict(
        course=name,
        source_pcd=str(pcd_file),
        input_points=int(len(xyz)),
        grid_shape=list(rec["height"].shape),
        nav25d_file=str(nav_npz),
        installed_elevation_file=str(HERE / "maps" / "elevation" / f"{name}.npz") if install_as_course else None,
        stair_count=len(stairs),
        stairs=stairs,
    )
    put(stairs_path, info)
    return info


def main() -> None:
    p = argparse.ArgumentParser(description="Build or import Livox Mid-360 3D .pcd prior maps & 2.5D Nav maps.")
    p.add_argument("--from-pcd", type=Path, default=None, help="Import an external real-robot FAST-LIO2 .pcd map")
    p.add_argument("--name", type=str, default="real_mid360_map", help="Map name when using --from-pcd")
    p.add_argument("--courses", nargs="*", default=list(ALL_COURSES), help="Simulation courses to pre-build")
    args = p.parse_args()

    if args.from_pcd is not None:
        info = import_external_pcd(args.from_pcd, args.name, install_as_course=True)
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return

    reports = []
    for c in args.courses:
        reports.append(build_prior_for_course(c))
    audit = dict(
        sensor="Livox Mid-360 (360x59 deg, -7..+52 deg dome FOV, +18 deg forward mount)",
        courses_built=len(reports),
        reports=reports,
    )
    put(HERE / "evidence" / "MID360_PRIOR_MAP_AUDIT.json", audit)


if __name__ == "__main__":
    main()

"""SCUT Rough-v0 rotation terrain.

This is the local MOD4v3 adaptation of SCUT's
``RM_ROTATION_TERRAINS_CFG_99``.  The standard Isaac Lab sub-terrains are used
directly; SCUT's custom grid-bar tile is reproduced here because the target
does not install the ``agent_world`` package.
"""
from __future__ import annotations

import numpy as np
import trimesh
import isaaclab.terrains as t
from isaaclab.terrains import SubTerrainBaseCfg, TerrainGeneratorCfg
from isaaclab.utils.configclass import configclass


def _resolve_fixed_or_difficulty_value(fixed_value, value_range, difficulty, name):
    if fixed_value is not None:
        return float(fixed_value)
    if value_range is None:
        raise ValueError(f"Either '{name}' or '{name}_range' must be specified")
    lower, upper = value_range
    if lower > upper:
        raise ValueError(f"Invalid range for {name}: {value_range}")
    return float(lower + difficulty * (upper - lower))


def _resolve_fixed_or_difficulty_int(fixed_value, value_range, difficulty, name):
    if fixed_value is not None:
        return int(fixed_value)
    if value_range is None:
        raise ValueError(f"Either '{name}' or '{name}_range' must be specified")
    lower, upper = value_range
    if lower > upper:
        raise ValueError(f"Invalid range for {name}: {value_range}")
    return int(np.rint(lower + difficulty * (upper - lower)))


def _resolve_int_bounds(fixed_value, value_range, name):
    if fixed_value is not None:
        value = int(fixed_value)
        return value, value
    if value_range is None:
        raise ValueError(f"Either '{name}' or '{name}_range' must be specified")
    return int(value_range[0]), int(value_range[1])


def _force_even_count(value, fixed_value, value_range, name):
    if value % 2 == 0:
        return value
    lower, upper = _resolve_int_bounds(fixed_value, value_range, name)
    candidates = [candidate for candidate in (value + 1, value - 1) if lower <= candidate <= upper]
    if candidates:
        return int(candidates[0])
    raise ValueError(f"Cannot make {name} even within {value_range}")


def _symmetric_bar_centers(count, lower, upper, bar_width, name):
    if count <= 0:
        return np.zeros((0,), dtype=np.float32)
    usable = upper - lower
    if usable <= 0 or count * bar_width > usable:
        raise ValueError(f"Invalid {name} bar layout")
    if count == 1:
        return np.array([(lower + upper) * 0.5], dtype=np.float32)
    gap = (usable - count * bar_width) / (count + 1)
    first = lower + gap + 0.5 * bar_width
    step = bar_width + gap
    return (first + np.arange(count, dtype=np.float32) * step).astype(np.float32)


def _centered_fraction_span(lower, upper, fraction, name):
    if not 0.0 < fraction <= 1.0:
        raise ValueError(f"{name} must be in (0, 1]")
    margin = 0.5 * (upper - lower) * (1.0 - fraction)
    return lower + margin, upper - margin


def _resolve_grid_bars_params(difficulty, cfg):
    hd = float(np.random.uniform(0.0, 1.0)) if cfg.randomize_bar_count_difficulty else difficulty
    vd = float(np.random.uniform(0.0, 1.0)) if cfg.randomize_bar_count_difficulty else difficulty
    wd = float(np.random.uniform(0.0, 1.0)) if cfg.randomize_bar_width_difficulty else difficulty
    nh = _resolve_fixed_or_difficulty_int(cfg.num_horizontal, cfg.num_horizontal_range, hd, "num_horizontal")
    nv = _resolve_fixed_or_difficulty_int(cfg.num_vertical, cfg.num_vertical_range, vd, "num_vertical")
    if cfg.force_even_counts:
        nh = _force_even_count(nh, cfg.num_horizontal, cfg.num_horizontal_range, "num_horizontal")
        nv = _force_even_count(nv, cfg.num_vertical, cfg.num_vertical_range, "num_vertical")
    if cfg.force_unequal_counts and nh == nv:
        vmin, vmax = _resolve_int_bounds(cfg.num_vertical, cfg.num_vertical_range, "num_vertical")
        hmin, hmax = _resolve_int_bounds(cfg.num_horizontal, cfg.num_horizontal_range, "num_horizontal")
        step = 2 if cfg.force_even_counts else 1
        if nv + step <= vmax:
            nv += step
        elif nv - step >= vmin:
            nv -= step
        elif nh + step <= hmax:
            nh += step
        elif nh - step >= hmin:
            nh -= step
        else:
            raise ValueError("Could not make grid bar counts unequal")
    bw = _resolve_fixed_or_difficulty_value(cfg.bar_width, cfg.bar_width_range, wd, "bar_width")
    bh = _resolve_fixed_or_difficulty_value(cfg.bar_height, cfg.bar_height_range, difficulty, "bar_height")
    if nh < 0 or nv < 0 or (nh == 0 and nv == 0) or bw <= 0.0 or bh < 0.0:
        raise ValueError("Invalid grid bar parameters")
    return nh, nv, bw, bh


def mesh_grid_bars_terrain(difficulty: float, cfg: "MeshCustomGridBarsTerrainCfg"):
    """Generate SCUT's centered grid-bar mesh tile."""
    nh, nv, bw, bh = _resolve_grid_bars_params(difficulty, cfg)
    if cfg.ground_thickness < 0.0:
        raise ValueError("ground_thickness must be non-negative")
    x0, x1 = 0.0, float(cfg.size[0])
    y0, y1 = 0.0, float(cfg.size[1])
    xb0, xb1 = _centered_fraction_span(x0, x1, cfg.bar_length_ratio, "bar_length_ratio")
    yb0, yb1 = _centered_fraction_span(y0, y1, cfg.bar_length_ratio, "bar_length_ratio")
    hc = _symmetric_bar_centers(nh, y0, y1, bw, "horizontal")
    vc = _symmetric_bar_centers(nv, x0, x1, bw, "vertical")
    meshes = []

    def add_box(dims, pos):
        meshes.append(trimesh.creation.box(dims, trimesh.transformations.translation_matrix(pos)))

    if cfg.ground_thickness > 0.0:
        add_box((cfg.size[0], cfg.size[1], cfg.ground_thickness),
                (0.5 * cfg.size[0], 0.5 * cfg.size[1], -0.5 * cfg.ground_thickness))

    vertical_spans = []
    for cx in vc:
        a = max(xb0, float(cx) - 0.5 * bw)
        b = min(xb1, float(cx) + 0.5 * bw)
        if b > a:
            vertical_spans.append((a, b))
    vertical_spans.sort()

    for cy in hc:
        start = xb0
        for a, b in vertical_spans:
            end = min(max(a, start), xb1)
            length = end - start
            if length > 1.0e-6:
                add_box((length, bw, bh), (start + 0.5 * length, float(cy), 0.5 * bh))
            start = max(start, min(max(b, xb0), xb1))
        length = xb1 - start
        if length > 1.0e-6:
            add_box((length, bw, bh), (start + 0.5 * length, float(cy), 0.5 * bh))

    for cx in vc:
        length = yb1 - yb0
        add_box((bw, length, bh), (float(cx), yb0 + 0.5 * length, 0.5 * bh))

    return meshes, np.asarray([0.5 * cfg.size[0], 0.5 * cfg.size[1], bh])


@configclass
class MeshCustomGridBarsTerrainCfg(SubTerrainBaseCfg):
    """Centered grid of rectangular bars, matching SCUT's tiny-step tile."""
    function = mesh_grid_bars_terrain
    num_horizontal: int | None = None
    num_horizontal_range: tuple[int, int] | None = None
    num_vertical: int | None = None
    num_vertical_range: tuple[int, int] | None = None
    randomize_bar_count_difficulty: bool = False
    force_unequal_counts: bool = False
    force_even_counts: bool = False
    bar_width: float | None = None
    bar_width_range: tuple[float, float] | None = None
    randomize_bar_width_difficulty: bool = False
    bar_height: float | None = None
    bar_height_range: tuple[float, float] | None = None
    bar_length_ratio: float = 0.95
    ground_thickness: float = 0.05


def generator():
    """Return the SCUT rough-rotation terrain saved by the trained run."""
    return TerrainGeneratorCfg(
        seed=None,
        curriculum=True,
        size=(9.0, 9.0),
        border_width=5.0,
        border_height=1.0,
        num_rows=10,
        num_cols=14,
        color_scheme="none",
        horizontal_scale=0.1,
        vertical_scale=0.005,
        slope_threshold=0.5,
        difficulty_range=(0.0, 1.0),
        use_cache=False,
        cache_dir="/tmp/isaaclab/terrains",
        sub_terrains={
            "tiny_step_rot": MeshCustomGridBarsTerrainCfg(
                proportion=0.2,
                num_horizontal_range=(2, 4),
                num_vertical_range=(2, 4),
                randomize_bar_count_difficulty=True,
                force_unequal_counts=False,
                force_even_counts=True,
                bar_width_range=(0.05, 0.2),
                randomize_bar_width_difficulty=True,
                bar_height_range=(0.01, 0.03),
                bar_length_ratio=0.95,
                ground_thickness=0.05,
            ),
            "slope_for_rm_low": t.HfPyramidSlopedTerrainCfg(
                proportion=0.1, slope_range=(0.05, 0.15), platform_width=0.0,
                inverted=False, border_width=1.0
            ),
            "inv_slope_for_rm_low": t.HfInvertedPyramidSlopedTerrainCfg(
                proportion=0.1, slope_range=(0.05, 0.15), platform_width=0.0,
                inverted=True, border_width=1.0
            ),
            "stair_slope_for_rm_low": t.HfPyramidStairsTerrainCfg(
                proportion=0.1, step_height_range=(0.005, 0.015), step_width=0.1,
                platform_width=1.0, inverted=False, border_width=1.0
            ),
            "stair_slope_for_rm_mid": t.HfPyramidStairsTerrainCfg(
                proportion=0.2, step_height_range=(0.025, 0.04), step_width=0.1,
                platform_width=1.0, inverted=False, border_width=1.0
            ),
            "inv_stair_slope_for_rm_low": t.HfInvertedPyramidStairsTerrainCfg(
                proportion=0.1, step_height_range=(0.005, 0.015), step_width=0.1,
                platform_width=2.0, inverted=True, border_width=1.0
            ),
            "inv_stair_slope_for_rm_mid": t.HfInvertedPyramidStairsTerrainCfg(
                proportion=0.2, step_height_range=(0.025, 0.04), step_width=0.1,
                platform_width=1.0, inverted=True, border_width=1.0
            ),
            "plane_for_rm_rot": t.MeshPlaneTerrainCfg(proportion=0.3),
            "random_uniform_for_rm": t.HfRandomUniformTerrainCfg(
                proportion=0.1, noise_range=(0.0, 0.03), noise_step=0.005,
                downsampled_scale=0.2, border_width=1.0
            ),
        },
    )

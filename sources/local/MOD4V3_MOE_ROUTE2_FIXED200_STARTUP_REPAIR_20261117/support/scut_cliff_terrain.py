"""SCUT reference cliff generator; original functions and config copied verbatim."""

from dataclasses import MISSING

import numpy as np

from isaaclab.terrains import HfTerrainBaseCfg

from isaaclab.terrains.height_field.utils import height_field_to_mesh

from isaaclab.utils import configclass

def discretize_size_to_pixels(size: float, scale: float) -> int:
    """Convert a metric size to a discrete height-field resolution robustly."""

    return int(np.round(size / scale))

def _resolve_fixed_or_difficulty_value(
    fixed_value: float | None,
    value_range: tuple[float, float] | None,
    difficulty: float,
    name: str,
) -> float:
    """Resolve a terrain parameter from a fixed value or a difficulty-interpolated range."""

    if fixed_value is not None:
        return float(fixed_value)
    if value_range is None:
        raise ValueError(f"Either '{name}' or '{name}_range' must be specified.")
    lower, upper = value_range
    if lower > upper:
        raise ValueError(f"The range for '{name}' must satisfy lower <= upper. Got: {value_range}.")
    return float(lower + difficulty * (upper - lower))

def _resolve_height_offset_curriculum(
    difficulty: float, cfg: "HfCliffInvertedPyramidStairsTerrainCfg"
) -> tuple[float, float]:
    """Resolve row-bucket scale and local interpolation difficulty for height offsets."""

    if not cfg.height_offset_curriculum_scale_by_difficulty:
        return 1.0, difficulty

    num_levels = max(int(cfg.height_offset_curriculum_num_levels), 1)
    if num_levels <= 1:
        return 1.0, difficulty

    clipped_difficulty = float(np.clip(difficulty, 0.0, 1.0))
    scaled_difficulty = clipped_difficulty * num_levels
    level = int(np.floor(scaled_difficulty))
    level = int(np.clip(level, 0, num_levels - 1))
    local_difficulty = float(np.clip(scaled_difficulty - level, 0.0, 1.0))
    return float(level) / float(num_levels - 1), local_difficulty

@height_field_to_mesh
def cliff_inverted_pyramid_stairs_terrain(
    difficulty: float, cfg: "HfCliffInvertedPyramidStairsTerrainCfg"
) -> np.ndarray:
    """Generate an inverted pyramid stairs terrain elevated above the surrounding border."""

    step_height = cfg.step_height_range[0] + difficulty * (cfg.step_height_range[1] - cfg.step_height_range[0])
    step_height *= -1
    height_offset_scale, height_offset_difficulty = _resolve_height_offset_curriculum(difficulty, cfg)
    height_offset = _resolve_fixed_or_difficulty_value(
        cfg.height_offset,
        (
            tuple(value * height_offset_scale for value in cfg.height_offset_range)
            if cfg.height_offset_range is not None
            else None
        ),
        height_offset_difficulty,
        "height_offset",
    )

    width_pixels = discretize_size_to_pixels(cfg.size[0], cfg.horizontal_scale)
    length_pixels = discretize_size_to_pixels(cfg.size[1], cfg.horizontal_scale)
    step_width = max(1, discretize_size_to_pixels(cfg.step_width, cfg.horizontal_scale))
    step_height_pixels = int(np.rint(step_height / cfg.vertical_scale))
    platform_width = discretize_size_to_pixels(cfg.platform_width, cfg.horizontal_scale)
    height_offset_pixels = int(np.rint(height_offset / cfg.vertical_scale))

    hf_raw = np.full((width_pixels, length_pixels), height_offset_pixels, dtype=np.float32)

    current_step_height = 0
    start_x, start_y = 0, 0
    stop_x, stop_y = width_pixels, length_pixels
    while (stop_x - start_x) > platform_width and (stop_y - start_y) > platform_width:
        start_x += step_width
        stop_x -= step_width
        start_y += step_width
        stop_y -= step_width
        current_step_height += step_height_pixels
        hf_raw[start_x:stop_x, start_y:stop_y] = height_offset_pixels + current_step_height

    return np.rint(hf_raw).astype(np.int16)

@configclass
class HfCliffInvertedPyramidStairsTerrainCfg(HfTerrainBaseCfg):
    """Configuration for a raised inverted pyramid stairs terrain with a cliff at the border."""

    function = cliff_inverted_pyramid_stairs_terrain

    step_height_range: tuple[float, float] = MISSING
    """The minimum and maximum height of the steps (in m)."""

    step_width: float = MISSING
    """The width of the steps (in m)."""

    platform_width: float = 1.0
    """The width of the square platform at the center of the terrain (in m)."""

    height_offset: float | None = None
    """The fixed z-offset applied to the whole internal terrain (in m)."""

    height_offset_range: tuple[float, float] | None = None
    """The range of z-offset values, interpolated from terrain difficulty (in m)."""

    height_offset_curriculum_scale_by_difficulty: bool = False
    """Whether to scale ``height_offset_range`` by a difficulty bucket before interpolation."""

    height_offset_curriculum_num_levels: int = 11
    """Number of difficulty buckets used by the height-offset curriculum scale."""

"""SCUT rough_rotation_stair terrain, built from the pinned saved env.yaml.

The reward/state-machine contract is *not* constructed here. This module only
rebuilds the terrain that the published SCUT run used; all values are read from
the pinned `trained_env` YAML through `config.read_yaml`.
"""
from __future__ import annotations

from typing import Any

import isaaclab.sim as sim_utils
import isaaclab.terrains as terrain_gen
from isaaclab.utils.configclass import configclass

from .config import read_yaml
from .scut_height_field import (
    HfCliffInvertedPyramidStairsTerrainCfg,
    MeshCustomGridBarsTerrainCfg,
)


def _tuple(value):
    return tuple(value) if isinstance(value, (list, tuple)) else value


def _common(raw: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "proportion", "size", "flat_patch_sampling", "border_width",
        "horizontal_scale", "vertical_scale", "slope_threshold",
    }
    out = {key: _tuple(raw[key]) for key in allowed if key in raw}
    return out


def _subterrain(name: str, raw: dict[str, Any]):
    function = str(raw.get("function", ""))
    if name == "tiny_step_rot" or function.endswith("mesh_grid_bars_terrain"):
        return MeshCustomGridBarsTerrainCfg(
            **{key: _tuple(value) for key, value in raw.items() if key != "function"}
        )
    if function.endswith("cliff_inverted_pyramid_stairs_terrain"):
        return HfCliffInvertedPyramidStairsTerrainCfg(
            **{key: _tuple(value) for key, value in raw.items() if key != "function"}
        )
    if function.endswith("pyramid_sloped_terrain"):
        values = _common(raw)
        for key in ("slope_range", "platform_width", "inverted"):
            if key in raw:
                values[key] = _tuple(raw[key])
        return terrain_gen.HfPyramidSlopedTerrainCfg(**values)
    if function.endswith("pyramid_stairs_terrain"):
        values = _common(raw)
        for key in ("step_height_range", "step_width", "platform_width", "inverted"):
            if key in raw:
                values[key] = _tuple(raw[key])
        return terrain_gen.HfPyramidStairsTerrainCfg(**values)
    if function.endswith("random_uniform_terrain"):
        values = _common(raw)
        for key in ("noise_range", "noise_step", "downsampled_scale"):
            if key in raw:
                values[key] = _tuple(raw[key])
        return terrain_gen.HfRandomUniformTerrainCfg(**values)
    if function.endswith("flat_terrain"):
        return terrain_gen.MeshPlaneTerrainCfg(**_common(raw))
    raise ValueError(f"Unsupported pinned SCUT sub-terrain {name}: {function}")


def scut_rough_terrain_cfg(num_envs: int):
    """Return the exact saved Rough/rotation/stair terrain config."""
    env_raw = read_yaml("trained_env")
    raw = env_raw.get("rough_terrain_generator_cfg") or env_raw["terrain"]["terrain_generator"]
    sub_terrains = {
        name: _subterrain(name, dict(cfg))
        for name, cfg in raw["sub_terrains"].items()
    }
    generator = terrain_gen.TerrainGeneratorCfg(
        seed=raw.get("seed"),
        curriculum=bool(raw["curriculum"]),
        size=_tuple(raw["size"]),
        border_width=float(raw["border_width"]),
        border_height=float(raw["border_height"]),
        num_rows=int(raw["num_rows"]),
        num_cols=int(raw["num_cols"]),
        color_scheme=raw.get("color_scheme", "none"),
        horizontal_scale=float(raw["horizontal_scale"]),
        vertical_scale=float(raw["vertical_scale"]),
        slope_threshold=raw.get("slope_threshold"),
        sub_terrains=sub_terrains,
        difficulty_range=_tuple(raw.get("difficulty_range", (0.0, 1.0))),
        use_cache=bool(raw.get("use_cache", False)),
        cache_dir=raw.get("cache_dir", "/tmp/isaaclab/terrains"),
    )
    return terrain_gen.TerrainImporterCfg(
        prim_path="/World/ground",
        num_envs=int(num_envs),
        terrain_type="generator",
        terrain_generator=generator,
        env_spacing=4.0,
        use_terrain_origins=True,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
        ),
        debug_vis=False,
    )


def _source_metadata():
    """Describe the exact terrain source recorded in the run receipt."""
    import hashlib
    from .upstream import source_path

    path = source_path("trained_env")
    env_raw = read_yaml("trained_env")
    raw = env_raw.get("rough_terrain_generator_cfg") or env_raw["terrain"]["terrain_generator"]
    return {
        "source": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sub_terrains": list(raw["sub_terrains"].keys()),
        "curriculum": bool(raw["curriculum"]),
        "num_rows": int(raw["num_rows"]),
        "num_cols": int(raw["num_cols"]),
        "size_m": list(raw["size"]),
        "difficulty_range": list(raw["difficulty_range"]),
    }

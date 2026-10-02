"""RMUC2026 7v7 field: the RL terrain is generated from the *measured* map geometry.

`scripts/map_field_dims.py` extracts the feature inventory from
C:/Users/lulunomaro/Downloads/RMUC2026_V2.0.0.stp and writes cad/out_map/field_dims.json;
this module turns that JSON into a mjlab terrain curriculum, so the policy trains on the
slopes / stairs / barricades that actually exist in the 7v7 field instead of on invented
rough ground.  With ``curriculum=True`` every terrain type gets one column and difficulty
increases along rows, so the robot is walked up to the hardest ramp/stair in the map.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mujoco
import numpy as np
from mjlab.terrains import (BoxFlatTerrainCfg, BoxNarrowBeamsTerrainCfg,
                            BoxOpenStairsTerrainCfg, BoxSteppingStonesTerrainCfg,
                            FlatPatchSamplingCfg, HfDiscreteObstaclesTerrainCfg,
                            HfPyramidSlopedTerrainCfg, HfRandomUniformTerrainCfg,
                            HfWaveTerrainCfg, TerrainEntityCfg, TerrainGeneratorCfg)
from mjlab.terrains.terrain_generator import (SubTerrainCfg, TerrainGeometry,
                                              TerrainOutput)
from mjlab.terrains.utils import make_plane

#: every patch gets level spawn pads, so episodes do not start mid-slope
#: (the field is a dict so several named pads per terrain are possible)
SPAWN_PATCHES = FlatPatchSamplingCfg(
  num_patches=12, patch_radius=0.45, max_height_diff=0.02, grid_resolution=0.1)

DIMS_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "cad", "out_map", "field_dims.json"))

#: Fallback = the published RMUC 步兵 field numbers; only used if the CAD-derived JSON is
#: missing, so the task always builds.
DEFAULTS = dict(
    field_size_m=(17.0, 15.0),
    slope_deg=(12.0, 30.0),
    step_height_m=(0.05, 0.15),
    step_run_m=(0.25, 0.45),
    obstacle_height_m=(0.05, 0.20),
    obstacle_width_m=(0.30, 0.90),
    roughness_m=0.02,
    platform_height_m=0.40,
)


def load_dims(path: str = DIMS_PATH) -> dict:
    d = dict(DEFAULTS)
    d["source"] = "defaults"
    if os.path.isfile(path):
        try:
            got = json.load(open(path, encoding="utf-8"))
            d.update(got)
            d["source"] = "cad:" + os.path.basename(path)
            print("[field_cfg] map dims from CAD:",
                  {k: d[k] for k in ("slope_deg", "step_height_m", "step_run_m",
                                     "obstacle_height_m", "obstacle_width_m")})
        except Exception as exc:
            print("[field_cfg] could not read %s (%s); using defaults" % (path, exc))
    return d


# v11: the run skill collapsed on the map curriculum (v10 top speed 0.47 m/s vs 2.60 m/s
# on flat), so the flat-arena share is now tunable; the six terrain columns keep their
# relative weights and simply absorb whatever the flat column gives back.
FLAT_PROP = float(os.environ.get("RM_FLAT_PROP", 0.25))
# Relative weights of the non-flat columns.  They are normalised to (1-FLAT_PROP) so the
# skill mix can be re-balanced from the environment without editing this file.
_BASE_NONFLAT = (0.14 + 0.13 + 0.14 + 0.11 + 0.10 + 0.08
                 + 0.06 + 0.05 + 0.07 + 0.12)


@dataclass(kw_only=True)
class TunnelWallTerrainCfg(SubTerrainCfg):
  """A wall with a rectangular hole the robot must crouch through.

  The user measured the real opening at 250 mm high x 800 mm wide x 300 mm deep.
  The delivered CAD robot's top is 273 mm above the ground even at its deepest
  commanded crouch, so a fixed 250 mm hole would be an impossible feature and would
  starve the terrain curriculum.  The hole therefore starts at ``hole_height_range[0]``
  and shrinks to the real ``hole_height_range[1]`` as difficulty rises; the curriculum
  metrics then show exactly how close the policy gets to the real tunnel.
  """

  hole_height_range: tuple[float, float] = (0.35, 0.25)
  """Opening height from difficulty 0 to 1 [m]."""

  hole_width_range: tuple[float, float] = (1.2, 0.8)
  """Opening width from difficulty 0 to 1 [m]."""

  wall_thickness: float = 0.30
  """Tunnel depth along the driving direction [m] (user: 300 mm)."""

  wall_height: float = 1.2
  """Total wall height; tall enough that going over is not an option [m]."""

  spawn_x: float = 1.5
  """Spawn distance in front of the wall [m]."""

  def function(self, difficulty: float, spec: mujoco.MjSpec,
               rng: np.random.Generator) -> TerrainOutput:
    del rng
    body = spec.body("terrain")
    geoms = []
    ground = make_plane(body, self.size, 0.0, center_zero=False)
    for g in ground:
      geoms.append(TerrainGeometry(geom=g, color=(0.5, 0.5, 0.5, 1.0)))

    h0, h1 = self.hole_height_range
    w0, w1 = self.hole_width_range
    hole_h = h0 + difficulty * (h1 - h0)
    hole_w = w0 + difficulty * (w1 - w0)

    cx, cy = self.size[0] / 2.0, self.size[1] / 2.0
    tx = self.wall_thickness / 2.0
    wall_rgba = (0.85, 0.35, 0.25, 1.0)
    side_w = (self.size[1] - hole_w) / 2.0
    top_h = self.wall_height - hole_h

    # Left / right side walls, full height, full depth.
    for sign in (-1.0, 1.0):
      geoms.append(TerrainGeometry(geom=body.add_geom(
        type=mujoco.mjtGeom.mjGEOM_BOX,
        size=(tx, side_w / 2.0, self.wall_height / 2.0),
        pos=(cx, cy + sign * (hole_w / 2.0 + side_w / 2.0),
             self.wall_height / 2.0)), color=wall_rgba))
    # Top beam above the opening.
    geoms.append(TerrainGeometry(geom=body.add_geom(
      type=mujoco.mjtGeom.mjGEOM_BOX,
      size=(tx, hole_w / 2.0, top_h / 2.0),
      pos=(cx, cy, hole_h + top_h / 2.0)), color=wall_rgba))
    return TerrainOutput(origin=np.array([self.spawn_x, cy, 0.0]), geometries=geoms)


def _p(base):
  """Rescale a non-flat column proportion so all seven still sum to 1."""
  return base / _BASE_NONFLAT * (1.0 - FLAT_PROP)


def capability_cap_m() -> float:
    """The tallest map feature this chassis can physically deal with.

    Measured, not guessed: scripts/climb_capability.py holds the frame rigid, sweeps the two
    hip-axis motors over the range the policy can actually command (LEG_ACTION_SCALE 0.5 rad
    per unit action, so +-0.5 rad) through the VALIDATED closed-chain equality constraints, and
    reads the wheel's height relative to the chassis.  The stroke is 0.274 m
    (wheel bottom swings between -0.044 m and +0.230 m below the chassis origin).  Climbing a
    step of height h needs one wheel lifted by h while the OTHER wheel still carries the robot,
    and the chassis box must not dig in, so the usable cap is well below the raw stroke.

    Why the curriculum must be capped at all: the 2026 map really does contain barricades up to
    0.416 m (measured out of RMUC2026_V2.0.0.stp).  Spawning 20% of the environments in front of
    geometry the mechanism can never surmount is not "training on the map" - it just pins every
    env on that row at difficulty 0, which is exactly what v14's
    Curriculum/terrain_levels/mean = 0.067 shows.  The cap keeps the honest map geometry for
    everything the robot CAN climb and states the rest out loud.
    """
    return float(os.environ.get("RM_TERRAIN_CAP_H", "0.20"))


def rmuc2026_terrain(num_rows: int = 4, size_m: float = 8.0, curriculum: bool = True,
                     dims: dict | None = None) -> TerrainGeneratorCfg:
    """7 columns: flat arena, ramp up, ramp down, stairs up, stairs down, barricades, bumps."""
    d = dims or load_dims()
    s_lo, s_hi = [float(v) for v in d["slope_deg"]]
    h_lo, h_hi = [float(v) for v in d["step_height_m"]]
    r_lo, r_hi = [float(v) for v in d["step_run_m"]]
    o_lo, o_hi = [float(v) for v in d["obstacle_height_m"]]
    w_lo, w_hi = [float(v) for v in d["obstacle_width_m"]]
    rough = float(d["roughness_m"])
    cap = capability_cap_m()
    if h_hi > cap or o_hi > cap:
        print("[field_cfg] map asks for steps %.2f m / barricades %.2f m; the measured leg "
              "stroke caps the curriculum at %.2f m (scripts/climb_capability.py)"
              % (h_hi, o_hi, cap))
    h_hi, o_hi = min(h_hi, cap), min(o_hi, cap)
    h_lo, o_lo = min(h_lo, h_hi), min(o_lo, o_hi)
    subs = {
      # 平地竞技场: 跑 / 小陀螺 / 跳 live here
      "flat": BoxFlatTerrainCfg(proportion=FLAT_PROP, size=(size_m, size_m),
                        flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 坡道 (up)
      "ramp_up": HfPyramidSlopedTerrainCfg(
        proportion=_p(0.14), slope_range=(s_lo, s_hi), platform_width=1.6,
        size=(size_m, size_m), inverted=False,
        flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 坡道 (down)
      "ramp_down": HfPyramidSlopedTerrainCfg(
        proportion=_p(0.13), slope_range=(s_lo, s_hi), platform_width=1.6,
        size=(size_m, size_m), inverted=True,
        flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 台阶 (up)
      "stairs_up": BoxOpenStairsTerrainCfg(
        proportion=_p(0.14), step_height_range=(h_lo, h_hi), step_width_range=(r_lo, r_hi),
        platform_width=1.6, size=(size_m, size_m), inverted=False, step_thickness=0.04,
        flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 台阶 (down)
      "stairs_down": BoxOpenStairsTerrainCfg(
        proportion=_p(0.11), step_height_range=(h_lo, h_hi), step_width_range=(r_lo, r_hi),
        platform_width=1.6, size=(size_m, size_m), inverted=True, step_thickness=0.04,
        flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 掩体 (barricades to climb over / jump onto)
      "obstacles": HfDiscreteObstaclesTerrainCfg(
        proportion=_p(0.10), obstacle_height_mode="fixed",
        obstacle_width_range=(w_lo, w_hi), obstacle_height_range=(o_lo, o_hi),
        num_obstacles=18, platform_width=1.6, size=(size_m, size_m),
        square_obstacles=True, flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 起伏地面
      "rough": HfRandomUniformTerrainCfg(
        proportion=_p(0.08), noise_range=(-rough, rough), noise_step=0.03,
        size=(size_m, size_m), flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 过洞/过坑 proxy: stepping stones with difficulty-scaled gaps.  The RMUC2026 CAD
      # JSON has no tunnel/gate dimensions, so this trains the underlying skill (precise
      # wheel placement across a gap) until the real tunnel opening is measured.
      "gap": BoxSteppingStonesTerrainCfg(
        proportion=_p(0.06), stone_size_range=(0.45, 0.80),
        stone_distance_range=(0.15, 0.35), stone_height=0.15,
        stone_height_variation=0.05, floor_depth=1.2, platform_width=1.6,
        border_width=0.25, size=(size_m, size_m),
        flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 窄道 proxy: beams wide enough for the 0.472 m track, narrowing with difficulty.
      "narrow": BoxNarrowBeamsTerrainCfg(
        proportion=_p(0.05), num_beams=8, beam_width_range=(0.55, 0.90),
        beam_height=0.15, spacing=1.6, platform_width=1.6, border_width=0.25,
        size=(size_m, size_m), flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 连续起伏: low-amplitude waves between the discrete obstacles and the random noise.
      "wave": HfWaveTerrainCfg(
        proportion=_p(0.07), amplitude_range=(0.02, 0.08), num_waves=2,
        horizontal_scale=0.10, vertical_scale=0.005, border_width=0.25,
        size=(size_m, size_m), flat_patch_sampling={"spawn": SPAWN_PATCHES}),
      # 真实洞口: 用户实测 高 250 mm × 宽 800 mm × 长 300 mm.  开口从 350 mm 收到
      # 250 mm；CAD 机器人最低蹲姿顶部约 273 mm，课程会如实显示它能到哪一档。
      "tunnel": TunnelWallTerrainCfg(
        proportion=_p(0.12), hole_height_range=(0.25, 0.25),
        hole_width_range=(0.80, 0.80), wall_thickness=0.30, wall_height=1.2,
        spawn_x=1.5, size=(size_m, size_m),
        flat_patch_sampling={"spawn": SPAWN_PATCHES}),
    }
    return TerrainGeneratorCfg(
      size=(size_m, size_m),
      border_width=20.0,
      num_rows=num_rows,
      num_cols=len(subs),
      curriculum=curriculum,
      color_scheme="height",
      difficulty_range=(0.0, 1.0),
      sub_terrains=subs,
    )


def field_terrain_entity(num_rows=8, size_m=8.0, env_spacing=10.0,
                         dims: dict | None = None) -> TerrainEntityCfg:
    return TerrainEntityCfg(
      terrain_type="generator",
      terrain_generator=rmuc2026_terrain(num_rows=num_rows, size_m=size_m, dims=dims),
      env_spacing=env_spacing,
      max_init_terrain_level=1,
    )

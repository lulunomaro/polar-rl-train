"""Measured torque-speed curve actuator, modelled on SCUT's M3508Actuator.

SCUT's wheeled-legged_RL clips the wheel effort with a *measured* torque-speed CSV
(``agent_world/actuators/m3508_actuator.py``) instead of a two-point datasheet fit.
This module gives our mjlab pipeline the same capability as a drop-in replacement for
``DcMotorActuatorCfg``:

* same CSV column names as SCUT by default
  (``Motor_shaft_torque_Nm_ideal``, ``Motor_shaft_speed_rpm``);
* torque and speed are converted from motor shaft to the actuator output shaft with the
  configured gear ratio and efficiency;
* below/above the measured points the curve is extended with a smooth stall hold and a
  hard zero past the last point, matching SCUT's behaviour.

Until a bench curve exists the analytic two-piece :class:`DcMotorActuatorCfg` remains the
default; set ``RM_WHEEL_CURVE=/path/to/curve.csv`` to switch without touching any task
code.  ``scripts/make_synthetic_wheel_curve.py`` generates a CSV that reproduces the
analytic envelope, so the whole path can be tested before the hardware data arrives.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import mujoco
import mujoco_warp as mjwarp
import torch

from mjlab.actuator import DcMotorActuator, DcMotorActuatorCfg


@dataclass(kw_only=True)
class CurveMotorActuatorCfg(DcMotorActuatorCfg):
  """Wheel actuator whose effort limit is a measured torque-speed curve."""

  curve_path: str = ""
  """CSV with the measured motor-shaft torque/speed points."""

  gear_ratio: float = 1.0
  """Motor shaft -> actuator output shaft reduction (e.g. 15.8)."""

  gearbox_efficiency: float = 1.0
  """Multiplier applied to the geared torque."""

  output_stall_torque: float = 0.0
  """Hard cap at zero speed; 0 means use ``saturation_effort``."""

  torque_column: str = "Motor_shaft_torque_Nm_ideal"
  speed_column: str = "Motor_shaft_speed_rpm"

  def build(self, entity, target_ids, target_names):
    return CurveMotorActuator(self, entity, target_ids, target_names)


class CurveMotorActuator(DcMotorActuator):
  """Piecewise-linear lookup of the measured torque limit at the current joint speed."""

  def initialize(
    self,
    mj_model: mujoco.MjModel,
    model: mjwarp.Model,
    data: mjwarp.Data,
    device: str,
  ) -> None:
    super().initialize(mj_model, model, data, device)
    speed, torque = load_curve(self.cfg, device=device)
    self._curve_speed = speed
    self._curve_torque = torque
    self._curve_zeros = torch.zeros_like(torque[:1])

  def _clip_effort(self, effort: torch.Tensor) -> torch.Tensor:
    assert self._joint_vel_clipped is not None
    limit = self._lookup(self._joint_vel_clipped.abs())
    if self.force_limit is not None:
      limit = torch.minimum(limit, self.force_limit)
    return torch.clamp(effort, min=-limit, max=limit)

  def _lookup(self, abs_speed: torch.Tensor) -> torch.Tensor:
    flat = abs_speed.reshape(-1)
    idx_hi = torch.searchsorted(self._curve_speed, flat, right=False)
    idx_hi = torch.clamp(idx_hi, min=1, max=self._curve_speed.numel() - 1)
    idx_lo = idx_hi - 1
    s_lo, s_hi = self._curve_speed[idx_lo], self._curve_speed[idx_hi]
    t_lo, t_hi = self._curve_torque[idx_lo], self._curve_torque[idx_hi]
    alpha = (flat - s_lo) / torch.clamp(s_hi - s_lo, min=1e-6)
    limit = t_lo + alpha * (t_hi - t_lo)
    limit = torch.where(flat <= self._curve_speed[0], self._curve_torque[0], limit)
    limit = torch.where(flat > self._curve_speed[-1],
                        self._curve_zeros.reshape(-1)[:1].expand_as(flat), limit)
    return limit.clamp(min=0.0).reshape_as(abs_speed)


def load_curve(cfg: CurveMotorActuatorCfg, device: str = "cpu"):
  """Read a SCUT-format CSV and return (output_speed_rad_s, output_torque_Nm)."""
  path = _resolve(cfg.curve_path)
  points: list[tuple[float, float]] = []
  with path.open(newline="") as fh:
    reader = csv.DictReader(fh)
    missing = {cfg.torque_column, cfg.speed_column}.difference(reader.fieldnames or [])
    if missing:
      raise ValueError("%s is missing columns %s" % (path, sorted(missing)))
    for row in reader:
      motor_torque = float(row[cfg.torque_column])
      motor_rpm = float(row[cfg.speed_column])
      out_torque = motor_torque * cfg.gear_ratio * cfg.gearbox_efficiency
      out_speed = motor_rpm / cfg.gear_ratio * 2.0 * math.pi / 60.0
      if out_speed >= 0.0 and out_torque >= 0.0 and math.isfinite(out_speed + out_torque):
        points.append((out_speed, out_torque))
  if len(points) < 2:
    raise ValueError("curve %s has fewer than two valid points" % path)
  points.sort(key=lambda p: p[0])
  speed = torch.tensor([p[0] for p in points], dtype=torch.float32, device=device)
  torque = torch.tensor([p[1] for p in points], dtype=torch.float32, device=device)
  cap = float(cfg.output_stall_torque) or float(cfg.saturation_effort)
  torque = torch.minimum(torque, torch.tensor(cap, device=device))
  return speed.contiguous(), torque.contiguous()


def _resolve(curve_path: str) -> Path:
  path = Path(curve_path).expanduser()
  if path.is_absolute() and path.exists():
    return path
  here = Path(__file__).resolve()
  for base in (Path.cwd(), here.parents[4], here.parents[3]):
    candidate = base / path
    if candidate.exists():
      return candidate
  raise FileNotFoundError("torque-speed curve not found: %s" % curve_path)

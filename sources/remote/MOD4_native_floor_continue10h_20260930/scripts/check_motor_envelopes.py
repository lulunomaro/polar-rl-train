#!/usr/bin/env python3
"""Audit the output-shaft torque/speed envelopes used by training."""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))
from rmvehicle import robot_cfg as rc  # noqa: E402


def available_positive_torque(current_limit: float, voltage_intercept: float,
                              no_load: float, speed: float) -> float:
  return max(0.0, min(current_limit,
                      voltage_intercept * (1.0 - speed / no_load)))


def close(got: float, expected: float, label: str, atol: float = 1.0e-3) -> None:
  if not math.isclose(got, expected, abs_tol=atol, rel_tol=0.0):
    raise SystemExit(f"MOTOR ENVELOPE FAIL: {label}: {got:.8f} != {expected:.8f}")


def main() -> int:
  c = rc.contract()
  leg_knee = c["leg_no_load"] * (
      1.0 - c["leg_effort"] / c["leg_voltage_line_intercept"])
  wheel_knee = c["wheel_no_load"] * (
      1.0 - c["wheel_effort"] / c["wheel_voltage_line_intercept"])
  close(wheel_knee, c["wheel_knee_speed"], "wheel plateau knee")
  close(available_positive_torque(c["leg_effort"], c["leg_voltage_line_intercept"],
                                  c["leg_no_load"], 0.0), c["leg_effort"],
        "leg zero-speed current cap")
  close(available_positive_torque(c["wheel_effort"], c["wheel_voltage_line_intercept"],
                                  c["wheel_no_load"], wheel_knee), c["wheel_effort"],
        "wheel knee torque")
  close(available_positive_torque(c["wheel_effort"], c["wheel_voltage_line_intercept"],
                                  c["wheel_no_load"], c["wheel_no_load"]), 0.0,
        "wheel no-load torque")

  two_rev_yaw = 4.0 * math.pi
  wheel_speed = two_rev_yaw * c["half_track"] / c["wheel_radius"]
  remaining = available_positive_torque(
      c["wheel_effort"], c["wheel_voltage_line_intercept"],
      c["wheel_no_load"], wheel_speed)
  if remaining <= 0.0:
    raise SystemExit("MOTOR ENVELOPE FAIL: 2 rev/s gyro is outside the wheel envelope")
  print(f"leg plateau:  {c['leg_effort']:.4f} N.m through {leg_knee:.4f} rad/s")
  print(f"wheel plateau:{c['wheel_effort']:.4f} N.m through {wheel_knee:.4f} rad/s")
  print(f"wheel no-load:{c['wheel_no_load']:.4f} rad/s")
  print(f"2 rev/s gyro: {wheel_speed:.4f} rad/s per wheel, {remaining:.4f} N.m remains")
  print("MOTOR ENVELOPES PASS")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

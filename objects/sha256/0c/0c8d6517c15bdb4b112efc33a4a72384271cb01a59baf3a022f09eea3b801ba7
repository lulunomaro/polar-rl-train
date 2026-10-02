"""Generate a SCUT-format torque-speed CSV from our analytic two-piece envelope.

Purpose: prove the measured-curve actuator path end to end *before* the real bench data
exists.  When the DM3519+15.8 bench CSV arrives, drop it in with the same columns and set
RM_WHEEL_CURVE to it; no code changes are needed.

  python scripts/make_synthetic_wheel_curve.py --out train/deploy/wheel_curve_synthetic.csv
"""
import argparse
import csv
import json
import math
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="train/deploy/wheel_curve_synthetic.csv")
ap.add_argument("--effort", type=float, default=6.0, help="current plateau N*m")
ap.add_argument("--saturation", type=float, default=31.322311300346446,
                help="voltage-line zero-speed intercept N*m")
ap.add_argument("--no-load", type=float, default=55.3557, help="no-load rad/s")
ap.add_argument("--gear-ratio", type=float, default=15.8)
ap.add_argument("--vmax", type=float, default=60.0)
ap.add_argument("--points", type=int, default=121)
a = ap.parse_args()

out = Path(a.out)
out.parent.mkdir(parents=True, exist_ok=True)
knee = a.no_load * (1.0 - a.effort / a.saturation)
speeds = {a.vmax * i / (a.points - 1) for i in range(a.points)}
speeds.add(0.0)
speeds.add(round(knee, 9))          # the envelope is piecewise linear; without the exact
speeds.add(round(a.no_load, 9))     # kink the CSV interpolation overshoots by ~0.06 N*m
rows = []
for v in sorted(speeds):
  tau = min(a.effort, a.saturation * (1.0 - v / a.no_load))
  tau = max(tau, 0.0)
  motor_rpm = v * a.gear_ratio * 60.0 / (2.0 * math.pi)
  motor_tau = tau / a.gear_ratio
  rows.append((motor_tau, motor_rpm))

with out.open("w", newline="") as fh:
  w = csv.writer(fh)
  w.writerow(["Motor_shaft_torque_Nm_ideal", "Motor_shaft_speed_rpm"])
  for tau, rpm in rows:
    w.writerow(["%.9f" % tau, "%.6f" % rpm])

manifest = dict(source="analytic_two_piece", effort=a.effort, saturation=a.saturation,
                no_load_rad_s=a.no_load, gear_ratio=a.gear_ratio,
                knee_rad_s=knee, points=len(rows), csv=str(out))
Path(str(out) + ".json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
print("wrote", out, "and", str(out) + ".json")

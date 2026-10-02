"""Verify the SCUT-style measured-curve actuator loader against an analytic envelope.

  python scripts/check_curve_actuator.py --csv train/deploy/wheel_curve_synthetic.csv

Exits non-zero on any mismatch.  This is the gate that lets us swap in a real bench CSV
with confidence: the same loader is exercised here, only the file changes.
"""
import argparse
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))

from rmvehicle.actuators import CurveMotorActuatorCfg, load_curve  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default=str(ROOT / "train" / "deploy" /
                                     "wheel_curve_synthetic.csv"))
ap.add_argument("--effort", type=float, default=6.0)
ap.add_argument("--saturation", type=float, default=31.322311300346446)
ap.add_argument("--no-load", type=float, default=55.3557)
ap.add_argument("--gear-ratio", type=float, default=15.8)
ap.add_argument("--tol", type=float, default=2e-3)
a = ap.parse_args()

cfg = CurveMotorActuatorCfg(
    target_names_expr=(".*",), stiffness=0.0, damping=0.0,
    effort_limit=a.effort, saturation_effort=a.saturation, velocity_limit=a.no_load,
    curve_path=a.csv, gear_ratio=a.gear_ratio, output_stall_torque=a.saturation)
speed, torque = load_curve(cfg)
print("curve points:", speed.numel(), "speed[0..-1]",
      float(speed[0]), float(speed[-1]))

fails = []
probe = torch.linspace(0.0, a.no_load, 41)
idx = torch.searchsorted(speed, probe, right=False).clamp(1, speed.numel() - 1)
lo, hi = idx - 1, idx
alpha = (probe - speed[lo]) / (speed[hi] - speed[lo]).clamp(min=1e-9)
got = torque[lo] + alpha * (torque[hi] - torque[lo])
want = torch.clamp(a.saturation * (1.0 - probe / a.no_load), min=0.0, max=a.effort)
err = (got - want).abs()
print("max torque error on 0..no-load:", float(err.max()))
if float(err.max()) > a.tol:
    fails.append("curve deviates from the analytic envelope by %.5f > %.5f"
                 % (float(err.max()), a.tol))

# Above no-load the measured curve must clamp to zero, not go negative.
above = torch.tensor([a.no_load * 1.05, a.no_load * 1.2])
idx2 = torch.searchsorted(speed, above, right=False).clamp(1, speed.numel() - 1)
lo2, hi2 = idx2 - 1, idx2
alpha2 = (above - speed[lo2]) / (speed[hi2] - speed[lo2]).clamp(min=1e-9)
got2 = torque[lo2] + alpha2 * (torque[hi2] - torque[lo2])
if bool((got2 < -1e-6).any()):
    fails.append("curve went negative above no-load: %s" % got2.tolist())
print("torque above no-load:", got2.tolist())

print("RESULT:", "CURVE ACTUATOR PASS" if not fails else "CURVE ACTUATOR FAIL")
for f in fails:
    print("  -", f)
raise SystemExit(1 if fails else 0)

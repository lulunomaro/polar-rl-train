"""Aggregate independent episode reports; fail if any route kind is missing."""
from __future__ import annotations
import argparse, json
from pathlib import Path

KINDS = ("run", "ramp_up", "ramp_down", "step_up", "step_down",
         "rough_cross", "slope_spin", "fly_jump", "jump_in_place", "tunnel_cross")

ap = argparse.ArgumentParser()
ap.add_argument("reports", nargs="+")
ap.add_argument("--out", required=True)
args = ap.parse_args()

rows = []
for name in args.reports:
    data = json.loads(Path(name).read_text(encoding="utf8"))
    if data.get("status") != "ROLLOUT_COMPLETE":
        raise ValueError("incomplete report: " + name)
    rows.extend(data.get("episodes") or [])

summary = {}
for kind in KINDS:
    part = [r for r in rows if r.get("kind") == kind]
    if not part:
        raise ValueError("no completed episodes for " + kind)
    n = len(part)
    summary[kind] = {
        "episodes": n,
        "successes": sum(bool(r.get("success")) for r in part),
        "complete_rate": sum(bool(r.get("success")) for r in part) / n,
        "termination_rate": sum(bool(r.get("terminated")) for r in part) / n,
        "underpass_rate": sum(bool(r.get("underpass_seen")) for r in part) / n,
        "launch_rate": sum(bool(r.get("launched")) for r in part) / n,
        "air_after_launch_rate": sum(bool(r.get("air_after_launch")) for r in part) / n,
    }
payload = {"schema": "mod4_multiseed_acceptance_v1", "reports": args.reports,
           "episodes": len(rows), "route_kinds": summary}
# Preserve action smoothness as a separately auditable gate.  Weight by scalar sample counts;
# averaging per-seed RMS values would bias a shortened rollout.
smooth = [json.loads(Path(name).read_text(encoding="utf8")).get("action_smoothness", {})
          for name in args.reports]
dn = sum(int(s.get("delta_scalar_samples", 0)) for s in smooth)
an = sum(int(s.get("second_difference_scalar_samples", 0)) for s in smooth)
if dn and an:
    import math
    payload["action_smoothness"] = {
        "delta_scalar_samples": dn,
        "delta_rms_per_step": math.sqrt(sum(float(s.get("delta_sum_sq", 0.0)) for s in smooth) / dn),
        "delta_max_abs": max(float(s.get("delta_max_abs", 0.0)) for s in smooth),
        "second_difference_scalar_samples": an,
        "second_difference_rms_per_step": math.sqrt(
            sum(float(s.get("second_difference_sum_sq", 0.0)) for s in smooth) / an),
        "second_difference_max_abs": max(
            float(s.get("second_difference_max_abs", 0.0)) for s in smooth),
    }
Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(json.dumps(payload, ensure_ascii=False, indent=2))

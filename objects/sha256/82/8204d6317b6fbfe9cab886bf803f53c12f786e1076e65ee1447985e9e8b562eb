"""Aggregate independent episode reports and enforce route-by-route acceptance."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

KINDS = ("run", "ramp_up", "ramp_down", "step_up", "step_down",
         "rough_cross", "slope_spin", "fly_jump", "jump_in_place", "tunnel_cross")

ap = argparse.ArgumentParser()
ap.add_argument("reports", nargs="+")
ap.add_argument("--out", required=True)
ap.add_argument("--profile", choices=("auto", "nominal", "dr"), default="auto")
ap.add_argument("--report-only", action="store_true",
                help="write verdict but return zero even when gates fail")
args = ap.parse_args()

datasets = [json.loads(Path(name).read_text(encoding="utf8")) for name in args.reports]
for name, data in zip(args.reports, datasets):
    if data.get("status") != "ROLLOUT_COMPLETE":
        raise ValueError("incomplete report: " + name)
domains = {bool(data.get("domain_randomization")) for data in datasets}
if len(domains) != 1:
    raise ValueError("nominal and DR reports cannot be pooled")
profile = args.profile
if profile == "auto":
    profile = "dr" if next(iter(domains)) else "nominal"
if (profile == "dr") != next(iter(domains)):
    raise ValueError("profile disagrees with report domain_randomization")

# Minimum release bars. Every route is checked separately.
gates = ({
    "min_complete_rate": 0.70,
    "max_termination_rate": 0.20,
    "min_special_event_rate": 0.65,
    "max_action_delta_rms": 0.18,
    "max_action_second_difference_rms": 0.25,
} if profile == "nominal" else {
    "min_complete_rate": 0.50,
    "max_termination_rate": 0.35,
    "min_special_event_rate": 0.45,
    "max_action_delta_rms": 0.20,
    "max_action_second_difference_rms": 0.28,
})
gates.update(max_closure_post_grace_m=0.002, max_mimic_post_grace_rad=0.01)

rows = []
for data in datasets:
    target = float((data.get("protocol", {}).get("rm_env", {}) or {}).get(
        "RM_JUMP_LO", 0.18))
    for row in data.get("episodes") or []:
        item = dict(row)
        item["_jump_target_m"] = target
        rows.append(item)

summary = {}
failures = []
for kind in KINDS:
    part = [row for row in rows if row.get("kind") == kind]
    if not part:
        raise ValueError("no completed episodes for " + kind)
    n = len(part)
    complete = sum(bool(row.get("success")) for row in part) / n
    terminated = sum(bool(row.get("terminated")) for row in part) / n
    rec = summary[kind] = {
        "episodes": n,
        "successes": sum(bool(row.get("success")) for row in part),
        "complete_rate": complete,
        "termination_rate": terminated,
        "underpass_rate": sum(bool(row.get("underpass_seen")) for row in part) / n,
        "launch_rate": sum(bool(row.get("launched")) for row in part) / n,
        "air_after_launch_rate": sum(bool(row.get("air_after_launch")) for row in part) / n,
        "landed_rate": sum(bool(row.get("landed")) for row in part) / n,
    }
    if kind == "jump_in_place":
        rec["jump_clear_rate"] = sum(
            float(row.get("peak_rise_m", 0.0)) >= float(row["_jump_target_m"])
            for row in part) / n
    if complete < gates["min_complete_rate"]:
        failures.append(
            f"{kind}: complete_rate {complete:.3f} < {gates['min_complete_rate']:.3f}")
    if terminated > gates["max_termination_rate"]:
        failures.append(
            f"{kind}: termination_rate {terminated:.3f} > {gates['max_termination_rate']:.3f}")

special = gates["min_special_event_rate"]
if summary["tunnel_cross"]["underpass_rate"] < special:
    failures.append("tunnel_cross: underpass_rate below %.3f" % special)
for metric in ("launch_rate", "air_after_launch_rate", "landed_rate"):
    if summary["fly_jump"][metric] < special:
        failures.append("fly_jump: %s below %.3f" % (metric, special))
if summary["jump_in_place"]["jump_clear_rate"] < special:
    failures.append("jump_in_place: jump_clear_rate below %.3f" % special)

smooth_parts = [data.get("action_smoothness", {}) for data in datasets]
dn = sum(int(item.get("delta_scalar_samples", 0)) for item in smooth_parts)
an = sum(int(item.get("second_difference_scalar_samples", 0)) for item in smooth_parts)
if not dn or not an:
    failures.append("action_smoothness: missing samples")
    smooth = {}
else:
    smooth = {
        "delta_scalar_samples": dn,
        "delta_rms_per_step": math.sqrt(
            sum(float(item.get("delta_sum_sq", 0.0)) for item in smooth_parts) / dn),
        "delta_max_abs": max(float(item.get("delta_max_abs", 0.0)) for item in smooth_parts),
        "second_difference_scalar_samples": an,
        "second_difference_rms_per_step": math.sqrt(
            sum(float(item.get("second_difference_sum_sq", 0.0)) for item in smooth_parts) / an),
        "second_difference_max_abs": max(
            float(item.get("second_difference_max_abs", 0.0)) for item in smooth_parts),
    }
    if smooth["delta_rms_per_step"] > gates["max_action_delta_rms"]:
        failures.append("action_smoothness: delta RMS exceeds gate")
    if smooth["second_difference_rms_per_step"] > gates["max_action_second_difference_rms"]:
        failures.append("action_smoothness: second-difference RMS exceeds gate")

closure = max(float(data.get("closure_post_grace_max_m", math.inf)) for data in datasets)
mimic = max(float(data.get("mimic_post_grace_max_rad", math.inf)) for data in datasets)
if not math.isfinite(closure) or closure > gates["max_closure_post_grace_m"]:
    failures.append("plant: post-grace closure error exceeds gate")
if not math.isfinite(mimic) or mimic > gates["max_mimic_post_grace_rad"]:
    failures.append("plant: post-grace mimic error exceeds gate")

payload = {
    "schema": "mod4_multiseed_acceptance_v2",
    "profile": profile,
    "passed": not failures,
    "failures": failures,
    "gates": gates,
    "reports": args.reports,
    "episodes": len(rows),
    "route_kinds": summary,
    "action_smoothness": smooth,
    "closure_post_grace_max_m": closure,
    "mimic_post_grace_max_rad": mimic,
}
Path(args.out).write_text(
    json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
    encoding="utf8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
if failures and not args.report_only:
    raise SystemExit(2)

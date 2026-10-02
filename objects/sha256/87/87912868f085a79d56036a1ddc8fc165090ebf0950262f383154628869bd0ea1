"""Locate the real MOD4 folding stop from exact cached STEP B-Rep solids."""
from __future__ import annotations

import json
from pathlib import Path

from scipy.optimize import brentq

from audit_source import configuration, distance, moved, si


OUT = Path(__file__).resolve().parent / "folded_pose_sim" / "hard_stop_brep.json"
PARTS = (124, 134)  # rocker and shin against fixed stop part 145


def gap(source_difference: float, part: int) -> float:
    return distance(si[145], moved(part, float(source_difference)))


report = {
    "source": "exact STEP B-Rep cache; source files read-only",
    "fixed_stop_part": 145,
    "moving_parts": list(PARTS),
    "neutral_source_difference_rad": 0.45,
    "threshold_solutions": {},
}

# BRepExtrema returns exactly zero once solids touch/interpenetrate. Solve several
# positive clearances and use the 0.1 micrometre result as a stable contact onset.
for part in PARTS:
    rows = []
    for threshold in (1e-4, 1e-5, 1e-6, 1e-7):
        source_difference = brentq(
            lambda value: gap(value, part) - threshold,
            -0.70,
            -0.55,
            xtol=1e-12,
            rtol=1e-12,
            maxiter=100,
        )
        values, _ = configuration(0.0, source_difference)
        rows.append(
            {
                "clearance_threshold_m": threshold,
                "source_difference_rad": source_difference,
                "packaged_difference_rad": source_difference - 0.45,
                "knee_rad": float(values["knee"]),
                "actual_gap_m": gap(source_difference, part),
            }
        )
    report["threshold_solutions"][str(part)] = rows

onsets = [report["threshold_solutions"][str(part)][-1]["source_difference_rad"] for part in PARTS]
# While folding from high to low difference, the first (largest) onset is the
# physical lower stop. The other pair may touch only after illegal penetration.
source_stop = max(onsets)
values, points = configuration(0.0, source_stop)
report["selected_contact"] = {
    "source_difference_rad": source_stop,
    "packaged_difference_rad": source_stop - 0.45,
    "contact_part": PARTS[onsets.index(source_stop)],
    "gaps_m": {str(part): gap(source_stop, part) for part in PARTS},
    "joint_values_source_zero_rad": {key: float(value) for key, value in values.items()},
    "spring_eye_length_m": float(((points["T"] - points["S"]) ** 2).sum() ** 0.5),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")
print(json.dumps(report, ensure_ascii=False, indent=2))

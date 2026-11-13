"""MOD4v2 HW300N60 source-branch geometry, in SI units; no simulator is imported on load.

Inputs are ABSOLUTE continuous hip/crank coordinates, unlike legacy kinematics.py
whose second argument was a difference. A common 2*pi turn is retained in the two
active coordinates and their drive followers. Passive coordinates are evaluated
in the hip-local frame on the neutral assembly's signed-intersection branch.
This is linkage geometry and equivalent joint-stop checking, not a mesh-contact
or measured hardware-stroke certificate.
"""
from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Mapping

import numpy as np

ROOT = Path(__file__).resolve().parent
PARAMS = json.loads((ROOT / "model_parameters.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "reports/model_manifest.json").read_text(encoding="utf-8"))
PINS = {side: {name: np.asarray(xz, dtype=float) for name, xz in pins.items()}
        for side, pins in MANIFEST["neutral_skeleton_xz_m"].items()}
JOINT_BOUNDS = PARAMS["per_side_joint_bounds_SI"]
CAD_DELTA_MIN = float(PARAMS["source_mechanical_delta_min_rad"])
GEOMETRY_MARGIN_M = 1.0e-7  # original source's strict circle-tangency conditioning guard
TAU = 2.0 * math.pi


def rotate(vector: np.ndarray, q: float) -> np.ndarray:
    c, s = math.cos(q), math.sin(q)
    return np.array([[c, s], [-s, c]]) @ vector


def angle(v: np.ndarray, w: np.ndarray) -> float:
    value = -(math.atan2(w[1], w[0]) - math.atan2(v[1], v[0]))
    return (value + math.pi) % TAU - math.pi


def intersect(a: np.ndarray, ra: float, b: np.ndarray, rb: float,
              sign: float) -> np.ndarray:
    length = float(np.linalg.norm(b - a))
    if not abs(ra - rb) + GEOMETRY_MARGIN_M < length < ra + rb - GEOMETRY_MARGIN_M:
        raise ValueError("Linkage singularity or unreachable pose on source assembly branch")
    t = (ra * ra - rb * rb + length * length) / (2.0 * length)
    h = math.sqrt(max(0.0, ra * ra - t * t))
    x = (b - a) / length
    return a + t * x + sign * h * np.array([-x[1], x[0]])


def _local_configuration(delta: float, side: str) -> tuple[dict, dict]:
    """Same neutral pins/link lengths/chirality as v1; hip is zero in this solve."""
    p = PINS[side]
    length = lambda a, b: float(np.linalg.norm(p[a] - p[b]))
    cross = lambda a, b: float(a[0] * b[1] - a[1] * b[0])
    q = {name: xz.copy() for name, xz in p.items()}
    q["A"] = rotate(p["A"], delta)
    q["B"] = intersect(q["A"], length("A", "B"), p["P"], length("B", "P"),
                       math.copysign(1.0, cross(p["P"] - p["A"], p["B"] - p["A"])))
    rocker = angle(p["B"] - p["P"], q["B"] - p["P"])
    q["C"] = p["P"] + rotate(p["C"] - p["P"], rocker)
    q["D"] = intersect(p["K"], length("K", "D"), q["C"], length("C", "D"),
                       math.copysign(1.0, cross(p["C"] - p["K"], p["D"] - p["K"])))
    shin = angle(p["D"] - p["K"], q["D"] - p["K"])
    for name in ("W", "T"):
        q[name] = p["K"] + rotate(p[name] - p["K"], shin)
    values = {
        "hip": 0.0, "crank": delta, "rocker_pin": rocker,
        "coupler_pin": angle(p["B"] - p["A"], q["B"] - q["A"]) - delta,
        "knee": shin,
        "distal_pin": angle(p["D"] - p["C"], q["D"] - q["C"]) - rocker,
        "gas_pin": angle(p["T"] - p["S"], q["T"] - p["S"]),
        "gas_slide": float(np.linalg.norm(q["T"] - p["S"])) - length("T", "S"),
        "drive_hip_spin": 0.0, "drive_input_spin": delta, "wheel_spin": 0.0,
    }
    # These are the neutral-connected relative hinge lifts, NOT active-axis wraps.
    # On the selected feasible branch none of these passive coordinates crosses pi.
    for name in ("rocker_pin", "coupler_pin", "knee", "distal_pin", "gas_pin"):
        values[name] = (values[name] + math.pi) % TAU - math.pi
    return values, q


def check_joint_limits(values: Mapping[str, float], side: str = "left",
                       tolerance: float = 1.0e-9) -> None:
    """Check equivalent v2 physical bounds only; null sides mean infinite extent."""
    if side not in PINS or not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("Unknown side or invalid bound tolerance")
    for name, bounds in JOINT_BOUNDS.items():
        value = float(values[name])
        if not math.isfinite(value):
            raise ValueError(f"{side}_{name} must be finite")
        low, high = bounds
        if ((low is not None and value < low - tolerance) or
                (high is not None and value > high + tolerance)):
            raise ValueError(f"{side}_{name}={value:.15g} outside mechanical bounds {bounds}")


def _first_positive_loop_guard(side: str) -> float:
    """Analytic first A--B--P triangle tangency; do not search other revolutions."""
    p = PINS[side]
    a, b = p["A"], p["P"]
    ra = float(np.linalg.norm(p["A"] - p["B"]))
    rb = float(np.linalg.norm(p["B"] - p["P"]))
    u = float(np.dot(a, b))
    v = float(a[1] * b[0] - a[0] * b[1])
    amplitude = math.hypot(u, v)
    phase = math.atan2(v, u)
    candidates = []
    for distance in (abs(ra - rb) + GEOMETRY_MARGIN_M, ra + rb - GEOMETRY_MARGIN_M):
        cosine = (float(np.dot(a, a) + np.dot(b, b)) - distance * distance) / (2 * amplitude)
        if -1.0 <= cosine <= 1.0:
            arc = math.acos(cosine)
            for root in (phase - arc, phase + arc):
                root %= TAU
                if root > 1.0e-10:
                    candidates.append(root)
    # Equal AB/PB links can stay nonsingular for a full active revolution.
    # In that case cap only the bracket search at one relative revolution;
    # this is not an authored motor bound and the gas stop must occur first.
    return min(candidates) if candidates else TAU


def _feasible(delta: float, side: str) -> bool:
    try:
        values, _ = _local_configuration(delta, side)
        check_joint_limits(values, side, tolerance=1.0e-12)
    except ValueError:
        return False
    return True


@lru_cache(maxsize=2)
def boundary_report(side: str = "left") -> dict:
    """Few doubling brackets plus bisection, only on the neutral-connected branch.

    The current upper endpoint follows this candidate's hardware slider bound,
    not a legacy operating interval. The proximal-loop guard prevents jumping over a
    linkage tangency into a different assembly. No pose grid or simulator is run.
    """
    if side not in PINS:
        raise ValueError(f"Unknown side {side!r}")
    if not _feasible(0.0, side):
        raise ValueError("Neutral disagrees with source pins and v2 stop group")
    # Start at the source CAD stop. This HW spec fixes the legacy rocker
    # metadata's 2e-7 rad disagreement using the unchanged neutral-pin backsolve.
    # A different future spec must explicitly report any local reconciliation;
    # never hide a disagreement behind a broad geometric tolerance.
    lower = CAD_DELTA_MIN
    lower_initial_bracket = None
    if not _feasible(lower, side):
        step = 1.0e-6
        lower_inside = lower + step
        for _ in range(8):
            if _feasible(lower_inside, side):
                break
            step *= 2.0
            lower_inside = lower + step
        else:
            raise ValueError("CAD stop group needs more than local numerical reconciliation")
        lower_initial_bracket = [lower, lower_inside]
        lower_outside = lower
        for _ in range(64):
            middle = 0.5 * (lower_outside + lower_inside)
            if _feasible(middle, side):
                lower_inside = middle
            else:
                lower_outside = middle
            if lower_inside - lower_outside <= 2.0e-13:
                break
        lower = lower_inside
    lower_values, _ = _local_configuration(lower, side)
    cap = _first_positive_loop_guard(side)
    inside = 0.0
    trial = min(0.125, cap)
    brackets = 0
    while trial < cap and _feasible(trial, side):
        inside = trial
        trial = min(2.0 * trial, cap)
        brackets += 1
        if brackets > 8:
            raise ValueError("Unexpected source branch: bounded bracket budget exhausted")
    outside = trial
    # cap is itself the strict tangency guard and thus the limiting open endpoint
    # if no earlier mechanical bound or distal closure has cut this branch.
    initial_bracket = [inside, outside]
    for _ in range(64):
        middle = 0.5 * (inside + outside)
        if _feasible(middle, side):
            inside = middle
        else:
            outside = middle
        if outside - inside <= 2.0e-13:
            break
    values, _ = _local_configuration(inside, side)
    active = []
    for name, (low, high) in JOINT_BOUNDS.items():
        if low is not None and abs(values[name] - low) < 1.0e-8:
            active.append(name + ":lower")
        if high is not None and abs(values[name] - high) < 1.0e-8:
            active.append(name + ":upper")
    # No unsupported global-reachability claim if a future geometry revision
    # changes this expected first upper event. Such an asset needs fresh review.
    if active != ["gas_slide:upper"]:
        raise ValueError(f"Unexpected first upper event {active}; review source branch")
    return {
        "side": side, "delta_min_rad": lower, "delta_max_rad": inside,
        "source_CAD_delta_min_rad": CAD_DELTA_MIN,
        "lower_shift_from_source_CAD_rad": lower - CAD_DELTA_MIN,
        "lower_initial_bracket_rad": lower_initial_bracket, "lower_values": lower_values,
        "upper_outside_rad": outside, "upper_active_constraints": active,
        "upper_values": values, "proximal_loop_guard_rad": cap,
        "initial_upper_bracket_rad": initial_bracket, "doubling_brackets": brackets,
        "method": "source signed branch + mechanical bounds + bounded bisection",
        "legacy_operating_window_used": False,
        "hardware_stroke_spec_confirmed": bool(PARAMS["gas_spring"]["hardware_stroke_spec_confirmed"]),
        "force_curve_calibrated": bool(PARAMS["gas_spring"]["force_curve_calibrated"]),
        "mesh_collision_checked": False,
    }


def mechanical_delta_bounds(side: str = "left") -> tuple[float, float]:
    report = boundary_report(side)
    return report["delta_min_rad"], report["delta_max_rad"]


def leg_configuration(hip: float, crank: float, side: str = "left",
                      check_limits: bool = True) -> tuple[dict, dict]:
    """Return joint values and chassis-relative xz pins for ABSOLUTE rotor inputs."""
    hip, crank = float(hip), float(crank)
    if side not in PINS or not math.isfinite(hip) or not math.isfinite(crank):
        raise ValueError("Unknown side or nonfinite absolute active coordinate")
    delta = crank - hip
    if check_limits:
        low, high = mechanical_delta_bounds(side)
        if not low - 1.0e-9 <= delta <= high + 1.0e-9:
            raise ValueError(f"{side} delta={delta:.15g} outside source mechanical branch [{low}, {high}]")
    values, local_pins = _local_configuration(delta, side)
    values.update(hip=hip, crank=crank, drive_hip_spin=hip, drive_input_spin=crank)
    if check_limits:
        check_joint_limits(values, side)
    return values, {name: rotate(xz, hip) for name, xz in local_pins.items()}


def set_configuration(model, data, left=(0.0, 0.0), right=(0.0, 0.0),
                      check_limits: bool = True) -> None:
    """Set a matching v2 MJCF pose and mj_forward only; never calls mj_step.

    Both legs are checked before qpos mutation. Matching MJCF ranges are checked
    too: passing an old v1 model never silently bypasses its asset discrepancy.
    Root/ground position is not changed and no wheel-ground collision is solved.
    """
    assignments = []
    for side, active in (("left", left), ("right", right)):
        values, _ = leg_configuration(*active, side=side, check_limits=check_limits)
        for name, value in values.items():
            joint = model.joint(side + "_" + name)
            if check_limits and model.jnt_limited[joint.id]:
                low, high = model.jnt_range[joint.id]
                if not low - 1.0e-9 <= value <= high + 1.0e-9:
                    raise ValueError(f"MJCF/v2 discrepancy: {joint.name}={value} outside [{low}, {high}]")
            assignments.append((int(model.jnt_qposadr[joint.id]), value))
    import mujoco  # optional backend, only when explicitly setting a compiled model
    for address, value in assignments:
        data.qpos[address] = value
    mujoco.mj_forward(model, data)

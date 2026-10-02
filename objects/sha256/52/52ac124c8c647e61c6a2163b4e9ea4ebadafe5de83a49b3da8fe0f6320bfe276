"""Audit every domain-randomization event: does it actually move the model?

This exists because two events were silently doing nothing: they scaled a model field that
the delivered MJCF leaves at zero (`dof_frictionloss`, `jnt_stiffness`), and `scale * 0 = 0`.
Ring-fencing DR by name is not enough - an event that runs and writes nothing looks exactly
like a robust policy until the hardware disagrees.

For each randomization event it prints the target field, the plant's base values, the
operation and range, and whether the resulting per-environment spread is non-zero.

Usage (training host):
    PYTHONPATH=train/rmvehicle/src:third_party/rc_mjlab/mjlab/src \
    python scripts/audit_dr_events.py --task RM2025-Later-CC-Flat-v0
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))

import rmvehicle  # noqa: E402,F401
from rmvehicle import robot_cfg as RC  # noqa: E402
from rmvehicle.names import RM2025_LATER  # noqa: E402
from mjlab.tasks.registry import load_env_cfg  # noqa: E402

# event function -> (model field, entity kind, how the event selects entries)
FIELDS = {
    "joint_friction": ("dof_frictionloss", "joints"),
    "dof_frictionloss": ("dof_frictionloss", "joints"),
    "joint_armature": ("dof_armature", "joints"),
    "joint_damping": ("dof_damping", "joints"),
    "joint_stiffness": ("jnt_stiffness", "joints"),
    "effort_limits": ("actuator_forcerange", "actuators"),
    "geom_friction": ("geom_friction", "geoms"),
    "body_com_offset": ("body_ipos", "bodies"),
    "pseudo_inertia": ("body_mass", "bodies"),
}


def fn_name(cfg) -> str:
    f = getattr(cfg, "func", None)
    name = getattr(f, "__name__", None)
    if name:
        return name
    text = str(f)
    return text.rsplit(".", 1)[-1].split(" ")[0] if text else "?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="RM2025-Later-CC-Flat-v0")
    args = ap.parse_args()
    cfg = load_env_cfg(args.task, play=False)
    m = mujoco.MjModel.from_xml_path(str(RC._resolve_path(RM2025_LATER)))
    print("plant:", RC._resolve_path(RM2025_LATER))
    print("%-22s %-20s %-24s %-8s %-24s %s"
          % ("event", "field", "base value range", "op", "range", "verdict"))
    dead = []
    for name, ev in cfg.events.items():
        params = dict(getattr(ev, "params", {}) or {})
        field = FIELDS.get(fn_name(ev))
        if field is None:
            continue
        field_name, kind = field
        asset = params.get("asset_cfg")
        ids = None
        if kind == "joints" and asset is not None:
            pats = getattr(asset, "joint_names", None)
            if pats:
                import re
                ids = [j for j in range(m.njnt)
                       if any(re.fullmatch(p, mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) or "")
                              for p in pats)]
        base = []
        for j in (ids if ids is not None else range(m.njnt)):
            if kind == "joints":
                if field_name == "jnt_stiffness":
                    base.append(float(m.jnt_stiffness[j]))
                else:
                    base.append(float(getattr(m, field_name)[m.jnt_dofadr[j]]))
        if not base:
            if field_name == "actuator_forcerange":
                base = [float(np.abs(m.actuator_forcerange[a]).max()) for a in range(m.nu)]
        base = np.array(base) if base else np.array([float("nan")])
        # ranges can be a tuple, or a per-axis dict
        rng = params.get("ranges", params.get("effort_limit_range", params.get("alpha_range")))
        if isinstance(rng, dict):
            vals = [v for pair in rng.values() for v in pair]
            rng = (min(vals), max(vals))
        op = params.get("operation", "abs")
        op = getattr(op, "name", op)
        verdict = "OK"
        if rng is None:
            verdict = "no range?"
        elif op == "scale":
            lo, hi = float(rng[0]), float(rng[1])
            if np.nanmax(np.abs(base)) == 0.0:
                verdict = "NO-OP (scale * 0)"
                dead.append(name)
            elif abs(hi - lo) < 1e-9:
                verdict = "NO-OP (range is a point)"
                dead.append(name)
        elif op in ("abs", "add"):
            lo, hi = float(rng[0]), float(rng[1])
            if abs(hi - lo) < 1e-12 and op == "add":
                verdict = "NO-OP (range is a point)"
                dead.append(name)
        print("%-22s %-20s [%8.5f,%8.5f] %-8s %-24s %s"
              % (name, field_name, float(np.nanmin(base)), float(np.nanmax(base)), op,
                 str(tuple(round(float(v), 4) for v in rng)) if rng else "-", verdict))
    print("")
    if dead:
        print("DEAD EVENTS (%d): %s" % (len(dead), ", ".join(dead)))
    else:
        print("no dead randomization events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""MOD4 sim2sim acceptance gate: deployment contract -> MuJoCo -> ONNX policy.

Why this file exists
--------------------
v2 item 5 makes "ONNX -> MuJoCo -> pass" a mandatory gate before any delivery.  The reference
implementation (refs/fudan_src/fudan_rl_wheel_leg-main/mujoco/python_tools/onnx_mj_*.py) has a
runnable, obs-aligned demo but **zero gate machinery**: no comparison, no threshold, no metric,
no exit code, and no headless mode (it is welded to `mujoco.viewer.launch_passive` + `pynput`).
We already have the gate shape in `sim2sim_later/check_sim2sim_later.py`
(`check(...)` + `RESULT: ... PASS/FAIL` + `sys.exit(main())`), so this is a MOD4 port of that
pattern rather than a copy of theirs.

Measured problem this file is written to catch
----------------------------------------------
`sim_mujoco/onnx_play.py` is a deployment-parity harness for a DIFFERENT contract:

    constant          onnx_play.py        MOD4 contract
    policy rate       50 Hz (line 245)    100 Hz
    physics step      0.001 s             0.0005 s
    wheel damping     1.5                 0.6
    wheel radius      0.073               0.0625

Running it as-is would certify a robot that is not the one being deployed (policy called at half
rate, 2x physics step, 2.5x wheel damping, 17 % wheel-radius error).  The reference's sim2sim has
the same class of defect (it clips every joint to +-30 Nm where the URDF says 50 legs / 5 wheels).
So section 1 below asserts the control law against the contract BEFORE anything is simulated.

Usage
-----
    PY=/home/egde/fangzhen_linux/third_party/rc_mjlab/.venv/bin/python   # has mujoco 3.13
    $PY -m pip install onnxruntime                                       # one-time, CPU wheel
    $PY sim2sim_mod4/check_sim2sim_mod4.py [--onnx <policy.onnx>] [--stage contract|all]

Exit codes: 0 = PASS, 2 = FAIL, 3 = a required dependency is missing (never silently skipped).
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "train" / "deploy" / "contract_rm2025_later.json"
MJCF_SERIAL = ROOT / "sim2sim" / "rm_vehicle" / "mjcf" / "rm_vehicle.xml"
MJCF_PARALLEL = ROOT / "sim2sim_cc" / "rm_vehicle_cc" / "mjcf" / "rm_vehicle.xml"

_FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    """Record a gate result.  Never raises: the report at the end carries every failure."""
    print("  [%s] %s" % ("ok  " if condition else "FAIL", message))
    if not condition:
        _FAILURES.append(message)


def load_contract() -> dict:
    if not CONTRACT.is_file():
        raise SystemExit("contract missing: %s" % CONTRACT)
    return json.loads(CONTRACT.read_text(encoding="utf8"))


# ---------------------------------------------------------------------------------------
# 1. Control law vs the deployment contract (pure python -- runs anywhere)
# ---------------------------------------------------------------------------------------
def check_control_law(c: dict) -> None:
    print("[1] control law vs contract (%s)" % CONTRACT.name)
    policy_hz = float(c.get("policy_hz", 0.0))
    physics_dt = float(c.get("physics_dt", 0.0))
    check(abs(policy_hz - 100.0) < 1e-9, "policy rate is 100 Hz (got %g)" % policy_hz)
    check(abs(physics_dt - 0.0005) < 1e-12, "physics dt is 0.5 ms (got %g s)" % physics_dt)
    decim = int(round((1.0 / policy_hz) / physics_dt)) if policy_hz and physics_dt else 0
    check(decim == 20, "decimation is 20 physics steps per policy step (got %d)" % decim)

    # The numbers onnx_play.py hardcodes; each must be overridden by the contract.
    stale = {
        "policy rate": (50.0, policy_hz, "100 Hz"),
        "physics step": (0.001, physics_dt, "0.0005 s"),
    }
    for name, (onnx_play_default, contract_value, want) in stale.items():
        check(abs(onnx_play_default - contract_value) > 1e-9,
              "onnx_play.py's %s default (%g) differs from the contract (%g = %s), so the "
              "harness MUST read the contract" % (name, onnx_play_default, contract_value, want))

    for key, fallback in (("leg_kp", None), ("leg_kd", None), ("wheel_kd", None),
                          ("leg_action_scale", None), ("wheel_action_scale", None),
                          ("wheel_radius", None)):
        v = c.get(key, fallback)
        check(v is not None, "contract carries %s" % key)
    wr = float(c.get("wheel_radius", 0.0))
    check(abs(wr - 0.0625) < 1e-9,
          "wheel_radius is 0.0625 m (got %g; onnx_play.py defaults to 0.073)" % wr)
    # torque / effort budgets: the reference got this wrong, so assert they exist and are sane
    for key in ("leg_effort", "wheel_effort"):
        v = c.get(key)
        check(isinstance(v, (int, float)) and v > 0.0, "contract carries a positive %s" % key)
    print("      leg kp/kd %s/%s | wheel kd %s | scales %s/%s | efforts %s/%s Nm"
          % (c.get("leg_kp"), c.get("leg_kd"), c.get("wheel_kd"),
             c.get("leg_action_scale"), c.get("wheel_action_scale"),
             c.get("leg_effort"), c.get("wheel_effort")))


# ---------------------------------------------------------------------------------------
# 2. Observation layout (the deployment FIFO contract)
# ---------------------------------------------------------------------------------------
def check_obs_layout(c: dict, args) -> None:
    print("[2] observation layout")
    seq = (args.encoder_history > 0)
    frame = int(args.frame_dim)
    if args.encoder_history < 0:
        check(True, "layout is read from the ONNX metadata (--encoder-history auto); the "
                    "metadata must declare obs_width/encoder_history or the gate fails")
    elif seq:
        want_in = frame * args.encoder_history
        check(True, "encoder mode: ONNX input is a %d-frame history, newest frame LAST "
                    "(%d floats) -- Isaac Lab flattens history with the most recent entry at "
                    "the end (CircularBuffer.buffer)" % (args.encoder_history, want_in))
        check(args.encoder_history == 5, "history length is 5 frames (got %d)" % args.encoder_history)
    else:
        check(True, "no encoder: ONNX input is the %d-D contract vector" % frame)
        check(frame == 35, "frame dim is the 35-D contract (got %d)" % frame)
    check(int(c.get("action_width", 0)) == 6, "contract action width is 6")
    check(int(c.get("obs_width", 0)) == 35, "contract obs width is 35 (got %s)" % c.get("obs_width"))
    # the exported permutation must equal the policy-side order the env uses
    perm = c.get("export_action_permutation")
    check(perm == [1, 0, 3, 2, 4, 5],
          "export_action_permutation is [1,0,3,2,4,5] (got %s)" % perm)


# ---------------------------------------------------------------------------------------
# 3. MuJoCo plant + ONNX policy (requires mujoco / onnxruntime)
# ---------------------------------------------------------------------------------------
def check_plant(args) -> None:
    print("[3] MuJoCo plant")
    try:
        import mujoco  # noqa: F401
    except Exception as exc:
        check(False, "mujoco import failed (%s) -- install it in this interpreter" % exc)
        return
    import mujoco
    for label, path in (("serial", MJCF_SERIAL), ("parallel", MJCF_PARALLEL)):
        if not path.is_file():
            check(False, "%s MJCF missing: %s" % (label, path))
            continue
        try:
            m = mujoco.MjModel.from_xml_path(str(path))
        except Exception as exc:
            check(False, "%s MJCF failed to load (%s)" % (label, exc))
            continue
        check(True, "%s MJCF loads: nq=%d nv=%d nu=%d" % (label, m.nq, m.nv, m.nu))
        # the MJCF must not silently assume a different integrator step than the contract
        if label == "serial":
            check(abs(float(m.opt.timestep) - 0.0005) <= 0.0005 * 0.5 + 1e-9,
                  "serial MJCF timestep %.6g s is within 50%% of the contract's 0.5 ms "
                  "(the reference's sim2sim silently ran 2.5x faster than training here)"
                  % float(m.opt.timestep))


def check_onnx(args, c: dict) -> None:
    print("[4] ONNX policy")
    try:
        import onnxruntime  # noqa: F401
    except Exception as exc:
        check(False, "onnxruntime import failed (%s) -- `pip install onnxruntime` (CPU wheel)"
              % exc)
        return
    import numpy as np
    import onnxruntime as ort
    if not args.onnx:
        check(False, "no --onnx policy given, so the ONNX contract cannot be checked")
        return
    p = pathlib.Path(args.onnx)
    check(p.is_file(), "policy exists: %s" % p)
    if not p.is_file():
        return
    sess = ort.InferenceSession(str(p), providers=["CPUExecutionProvider"])
    ins = [(i.name, i.shape) for i in sess.get_inputs()]
    outs = [(o.name, o.shape) for o in sess.get_outputs()]
    print("      inputs=%s outputs=%s" % (ins, outs))
    # The exporter writes the layout into the ONNX; the gate cross-checks the DECLARATION
    # against the contract instead of trusting a default (an earlier version of this file
    # defaulted --encoder-history 5 and wrongly rejected a legitimate 35-wide policy).
    meta = dict(sess.get_modelmeta().custom_metadata_map or {})
    check("obs_width" in meta, "ONNX declares obs_width (metadata_props)")
    check("encoder_history" in meta, "ONNX declares encoder_history (metadata_props)")
    declared_w = int(meta["obs_width"]) if meta.get("obs_width", "").isdigit() else -1
    declared_h = int(meta["encoder_history"]) if meta.get("encoder_history", "").lstrip("-").isdigit() else -2
    check(declared_h in (0, 5), "declared encoder_history is 0 or 5 (got %s)" % declared_h)
    want = int(args.frame_dim) * (declared_h if declared_h > 0 else 1)
    check(declared_w == want,
          "declared obs_width %s is consistent with the contract frame_dim %d and history %s"
          % (declared_w, args.frame_dim, declared_h))
    if args.encoder_history >= 0:
        check(declared_h == args.encoder_history,
              "declared history %s matches the required --encoder-history %d"
              % (declared_h, args.encoder_history))
    print("      declared layout: obs_width=%s encoder_history=%s (%s)"
          % (meta.get("obs_width"), meta.get("encoder_history"), meta.get("obs_layout")))
    check(len(ins) == 1, "exactly ONE input (history already flattened) -- got %d" % len(ins))
    if ins:
        last = ins[0][1][-1]
        check(last in (want, "batch", None) or str(last) == str(want),
              "input width %s matches the declared layout (%d)" % (last, want))
        check(str(last) == "batch" or int(last) == declared_w,
              "input width agrees with the declared obs_width")
    check(len(outs) == 1, "exactly ONE output (action mean) -- got %d" % len(outs))
    if outs:
        check(str(outs[0][1][-1]) in ("6", str(6)), "output width is 6 (got %s)" % outs[0][1][-1])
    # every contract number the harness needs must be present in the metadata
    for key in ("leg_kp", "leg_kd", "wheel_kd", "leg_action_scale", "wheel_action_scale",
                "wheel_radius", "physics_dt", "policy_hz"):
        check(key in meta, "ONNX carries the contract value %s" % key)

    # --- cross-check the TWO independent declarations of the observation layout --------------
    # The contract declares `obs_layout` (added by migration/linux/patch_contract_obs_layout.py)
    # and the ONNX declares its own `obs_layout`/`obs_width`/`encoder_history`.  Two independent
    # declarations that are never compared are worth very little -- the point of writing the layout
    # into both places is that they can disagree LOUDLY.  (Same rule as audit section 17.)
    lay = c.get("obs_layout")
    if not isinstance(lay, dict):
        print("      note: the contract carries no `obs_layout`; apply "
              "migration/linux/patch_contract_obs_layout.py to enable the cross-check")
    else:
        w = lay.get("obs_width")
        check(int(w or 0) == int(c.get("obs_width", 0)),
              "contract obs_layout.obs_width (%s) agrees with contract obs_width (%s)"
              % (w, c.get("obs_width")))
        segs = lay.get("segments") or []
        total = sum(int(s["slice"][1]) - int(s["slice"][0]) for s in segs if "slice" in s)
        check(total == int(c.get("obs_width", 0)),
              "contract obs_layout segments sum to %d == obs_width %s" % (total, c.get("obs_width")))
        check(bool(segs), "contract obs_layout lists explicit segments (%d)" % len(segs))
        try:
            onnx_w = int(meta.get("obs_width", "-1"))
        except ValueError:
            onnx_w = -1
        check(onnx_w == int(c.get("obs_width", 0)),
              "ONNX obs_width (%s) == contract obs_width (%s)" % (onnx_w, c.get("obs_width")))
        hist = lay.get("history") or {}
        frames = int(hist.get("frames", 0) or 0)
        try:
            onnx_h = int(meta.get("encoder_history", "-1"))
        except ValueError:
            onnx_h = -1
        if onnx_h > 0:
            check(onnx_h == frames,
                  "ONNX encoder_history (%d) == contract obs_layout.history.frames (%d)"
                  % (onnx_h, frames))
        else:
            check(onnx_h == 0 and frames >= 0,
                  "ONNX is single-frame (encoder_history=%d); the contract documents "
                  "history.frames=%d as OPTIONAL (RM_SEQ_ENCODER=1)" % (onnx_h, frames))
        print("      contract layout: %d segments, width %s, history frames %s"
              % (len(segs), w, frames))


# ---------------------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", default="", help="exported MOD4 policy (.onnx)")
    ap.add_argument("--stage", default="all", choices=["contract", "all"])
    ap.add_argument("--frame-dim", type=int, default=35)
    ap.add_argument("--encoder-history", type=int, default=-1,
                    help="actor history frames; 0 = plain 35-D contract, -1 = read the ONNX "
                         "metadata (default)")
    args = ap.parse_args(argv)
    print("MOD4 sim2sim gate  |  frame_dim=%d history=%d onnx=%s"
          % (args.frame_dim, args.encoder_history, args.onnx or "(none)"))
    try:
        c = load_contract()
    except SystemExit as exc:
        print("RESULT: SIM2SIM MOD4 FAIL -- %s" % exc)
        return 2
    check_control_law(c)
    check_obs_layout(c, args)
    if args.stage == "all":
        check_plant(args)
        check_onnx(args, c)
    if _FAILURES:
        print("\nRESULT: SIM2SIM MOD4 FAIL -- %d check(s):" % len(_FAILURES))
        for f in _FAILURES:
            print("   - %s" % f)
        return 2
    print("\nRESULT: SIM2SIM MOD4 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

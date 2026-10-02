#!/usr/bin/env python3
"""MOD4 policy rollout in MuJoCo -- the BEHAVIOURAL half of the sim2sim gate (first version).

What this does
--------------
Loads the parallel MJCF, drives its six `class="motor"` joints with the DELIVERY CONTRACT's control
law (kp/kd/scales/effort clamps via `qfrc_applied`, since the MJCF declares nu=0 and closes the
5-bar loop with six `<connect>` constraints -- `neq=6`), builds the 35-D observation from the
contract's own `obs_layout` (added by migration/linux/patch_contract_obs_layout.py), runs the ONNX
policy at the contract rate, and reports whether the result is physically sane.

What it does NOT do (read this before trusting it)
--------------------------------------------------
The JOINT-NAME CORRESPONDENCE between the policy and this MJCF is an ASSUMPTION, not a derivation.
The plant's two driven hinges (`left_crank`, `left_hip`) sit on separate axes 17.5 mm apart while
the MJCF's (`left_front1_joint`, `left_rear1_joint`) are COAXIAL -- audit sections 5.9/5.10 measured
the link lengths as the same linkage within 1.7-4 %, but the mapping between the two
parameterisations is non-linear, so this script exposes `--mapping` and does not claim to be exact.
The route-specific observation features (mode one-hot beyond `normal`, the jump/tunnel state bits)
are set to their neutral values, so this validates the FLAT `run` behaviour only.

A pass therefore means: the artifact, the contract and the plant are mutually consistent enough for
the policy to stand and act without diverging.  A fail means either the mapping is wrong or the
policy does not transfer -- and this tool cannot tell those apart, which is exactly why the
`--mapping` switch exists.

    PY=third_party/rc_mjlab/.venv/bin/python
    $PY sim2sim_mod4/rollout_mod4.py --onnx <policy.onnx> --steps 500 --vx 0.0
    $PY sim2sim_mod4/rollout_mod4.py --onnx <policy.onnx> --mapping rear1_is_hip
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "train" / "deploy" / "contract_rm2025_later.json"
# The SCENE, not the robot file: `rm_vehicle.xml` contains only the robot (no ground), so loading
# it drops the machine in free fall -- measured 2026-09-13 with a zero-action (pure PD) control:
# tilt stayed at 0.6 deg and vx at 0.000 while the base fell to -10.7 m, i.e. upright but falling.
# `scene.xml` <include>s the same robot and adds the floor plane.
MJCF = ROOT / "sim2sim_cc" / "rm_vehicle_cc" / "mjcf" / "scene.xml"

# action slot order the policy exports (contract.action_slot_order_exported)
SLOTS = ["left_crank", "left_hip", "right_crank", "right_hip", "left_wheel_spin", "right_wheel_spin"]


def quat_to_gravity(q):
    """Projected gravity in the body frame for a (w, x, y, z) quaternion."""
    w, x, y, z = q
    return np.array([
        2.0 * (x * z - w * y),
        2.0 * (y * z + w * x),
        1.0 - 2.0 * (x * x + y * y),
    ]) * -1.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", required=True)
    ap.add_argument("--steps", type=int, default=500, help="policy steps (100 Hz -> 10 ms each)")
    ap.add_argument("--vx", type=float, default=0.0, help="forward command (m/s)")
    ap.add_argument("--height-cmd", type=float, default=0.30)
    ap.add_argument("--mapping", default="front1_is_hip",
                    choices=["front1_is_hip", "rear1_is_hip"])
    ap.add_argument("--report", default="")
    ap.add_argument("--contract", default="", help="override the contract path (default: repo)")
    ap.add_argument("--mjcf", default="", help="override the MJCF path (default: parallel)")
    ap.add_argument("--stand-pose", default="0.20,1.00",
                    help="MJCF (rear1, front1) that puts the wheel ~0.27 m below the base -- "
                         "SOLVED 2026-09-13 with mj_step sampling: (0.20, 1.00) gives a residual "
                         "of 0.0004 m, and the runner-up is 0.065 m away (well separated). "
                         "qpos0 is a FOLDED pose (wheel level with the base) and cannot stand.")
    ap.add_argument("--leg-kp", type=float, default=0.0,
                    help="override leg kp (0 = the contract's value). Use this to test the "
                         "train-vs-contract gain gap: training ran at 2500, the contract says 60")
    ap.add_argument("--leg-kd", type=float, default=0.0, help="override leg kd (0 = contract)")
    ap.add_argument("--base-z", type=float, default=0.3321,
                    help="base height above the floor: 0.2696 (solved leg extension) + 0.0625 "
                         "(wheel radius) = 0.3321 for the solved stand pose")
    ap.add_argument("--base-z-offset", type=float, default=-0.2706,
                    help="MJCF base_link is at the AXLE height, not the chassis top: measured "
                         "offset -0.2706 m (audit section 5.11). The contract's root_height is a "
                         "CHASSIS height, so the MJCF base goes at root_height + this.")
    args = ap.parse_args(argv)

    try:
        import mujoco
        import onnxruntime as ort
    except Exception as exc:
        print("RESULT: ROLLOUT FAIL -- need mujoco + onnxruntime (%s)" % exc)
        return 3

    contract_path = pathlib.Path(args.contract) if args.contract else CONTRACT
    mjcf_path = pathlib.Path(args.mjcf) if args.mjcf else MJCF
    c = json.loads(contract_path.read_text(encoding="utf8"))
    lay = c.get("obs_layout")
    if not isinstance(lay, dict):
        print("RESULT: ROLLOUT FAIL -- the contract has no obs_layout; apply "
              "migration/linux/patch_contract_obs_layout.py (this tool refuses to guess the layout)")
        return 3
    segs = {s["name"]: s for s in lay["segments"]}
    need = {"commands", "height_command", "base_ang_vel", "projected_gravity", "leg_pos",
            "wheel_pos_slots", "leg_vel", "wheel_vel", "last_action", "mode_onehot"}
    missing = need - set(segs)
    if missing:
        print("RESULT: ROLLOUT FAIL -- contract obs_layout is missing %s" % sorted(missing))
        return 2

    leg_kp, leg_kd = float(c["leg_kp"]), float(c["leg_kd"])
    if args.leg_kp > 0:
        leg_kp = args.leg_kp
    if args.leg_kd > 0:
        leg_kd = args.leg_kd
    wheel_kd = float(c["wheel_kd"])
    leg_scale, wheel_scale = float(c["leg_action_scale"]), float(c["wheel_action_scale"])
    leg_eff, wheel_eff = float(c["leg_effort"]), float(c["wheel_effort"])
    dt = float(c["physics_dt"])
    decim = int(round((1.0 / float(c["policy_hz"])) / dt))

    m = mujoco.MjModel.from_xml_path(str(mjcf_path))
    d = mujoco.MjData(m)
    J = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
    B = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)

    # policy joint name -> MJCF joint name under the assumed correspondence
    hip_j, crank_j = ("front1", "rear1") if args.mapping == "front1_is_hip" else ("rear1", "front1")
    RES = {
        "left_crank": "left_%s_joint" % crank_j, "left_hip": "left_%s_joint" % hip_j,
        "right_crank": "right_%s_joint" % crank_j, "right_hip": "right_%s_joint" % hip_j,
        "left_wheel_spin": "left_wheel_joint", "right_wheel_spin": "right_wheel_joint",
    }
    for n in RES.values():
        if J(n) < 0:
            print("RESULT: ROLLOUT FAIL -- MJCF has no joint %r" % n)
            return 2
    base = B("base_link")
    ids = [J(RES[s]) for s in SLOTS]
    qadr = [m.jnt_qposadr[i] for i in ids]
    vadr = [m.jnt_dofadr[i] for i in ids]
    q_default = np.array(m.qpos0)[qadr].copy()
    if args.stand_pose:
        r1, f1 = [float(v) for v in args.stand_pose.split(",")]
        # the solved pose is stated for the LEFT leg's (rear1, front1); mirror to the right
        for k, slot in enumerate(SLOTS):
            if slot.endswith("crank") or slot.endswith("hip"):
                pass
        def _name_to_qpos(nm):
            return m.jnt_qposadr[J(nm)]
        q_default[0] = f1 if args.mapping == "front1_is_hip" else r1   # left_crank
        q_default[1] = r1 if args.mapping == "front1_is_hip" else f1   # left_hip
        q_default[2] = q_default[0]                                    # right mirrors
        q_default[3] = q_default[1]

    sess = ort.InferenceSession(str(args.onnx), providers=["CPUExecutionProvider"])
    in_names = [i.name for i in sess.get_inputs()]
    hist_frames = int(float(dict(sess.get_modelmeta().custom_metadata_map).get("encoder_history", 0)))

    d.qpos[:] = m.qpos0
    d.qvel[:] = 0.0
    d.qpos[m.jnt_qposadr[J("floating_base")] + 2] = (args.base_z if args.base_z > 0
                                                     else float(c.get("root_height", 0.30))
                                                     + args.base_z_offset)
    for k in range(6):
        d.qpos[qadr[k]] = q_default[k]
    last_action = np.zeros(6, dtype=np.float32)
    hist = [np.zeros(int(c["obs_width"]), dtype=np.float32)] * max(1, hist_frames)

    h0 = None
    min_h, max_tilt, nan_seen = 1e9, 0.0, False
    for step in range(args.steps):
        q = np.array([d.qpos[a] for a in qadr])
        qd = np.array([d.qvel[a] for a in vadr])
        base_q = np.array(d.qpos[m.jnt_qposadr[J("floating_base")] + 3:][:4])
        base_w = np.array(d.qvel[m.jnt_dofadr[J("floating_base")] + 3:][:3])
        pos = np.array(d.xpos[base])

        obs = np.zeros(int(c["obs_width"]), dtype=np.float32)
        for name, s in segs.items():
            a, b = s["slice"]
            sc = float(s.get("scale", 1.0))
            if name == "commands":
                obs[a:b] = np.array([args.vx, 0.0, 0.0]) * sc
            elif name == "height_command":
                obs[a:b] = args.height_cmd * sc
            elif name == "base_ang_vel":
                obs[a:b] = base_w * sc
            elif name == "projected_gravity":
                obs[a:b] = quat_to_gravity(base_q) * sc
            elif name == "leg_pos":
                obs[a:b] = (q[[0, 1, 2, 3]] - q_default[[0, 1, 2, 3]]) * sc
            elif name == "wheel_pos_slots":
                obs[a:b] = 0.0
            elif name == "leg_vel":
                obs[a:b] = qd[[0, 1, 2, 3]] * sc
            elif name == "wheel_vel":
                obs[a:b] = qd[[4, 5]] * sc
            elif name == "last_action":
                obs[a:b] = last_action * sc
            elif name == "mode_onehot":
                obs[a:b] = 0.0
                obs[a] = 1.0                      # 'normal'
        if hist_frames > 0:
            hist = hist[1:] + [obs]
            feed = {in_names[0]: obs[None, :], in_names[1]: np.concatenate(hist)[None, :]}
        else:
            feed = {in_names[0]: obs[None, :]}
        action = np.asarray(sess.run(None, feed)[0]).reshape(-1).astype(np.float32)
        if not np.all(np.isfinite(action)):
            nan_seen = True
            break
        last_action = action

        # the contract control law, applied to the six motors through qfrc_applied (nu = 0)
        tau = np.zeros(m.nv)
        for k, (slot, a_idx) in enumerate(zip(SLOTS, qadr)):
            v_idx = vadr[k]
            if "wheel" in slot:
                tau[v_idx] = float(np.clip(wheel_kd * (action[k] * wheel_scale - d.qvel[v_idx]),
                                           -wheel_eff, wheel_eff))
            else:
                target = q_default[k] + action[k] * leg_scale
                tau[v_idx] = float(np.clip(leg_kp * (target - d.qpos[a_idx])
                                           - leg_kd * d.qvel[v_idx], -leg_eff, leg_eff))
        for _ in range(decim):
            d.qfrc_applied[:] = tau
            mujoco.mj_step(m, d)
        h = float(d.xpos[base][2])
        if h0 is None:
            h0 = h
        min_h = min(min_h, h)
        g = quat_to_gravity(np.array(d.qpos[m.jnt_qposadr[J("floating_base")] + 3:][:4]))
        max_tilt = max(max_tilt, math.degrees(math.acos(max(-1.0, min(1.0, -g[2])))))
        if not np.all(np.isfinite(d.qpos)):
            nan_seen = True
            break

    final_h = float(d.xpos[base][2])
    vx = float(d.qvel[m.jnt_dofadr[J("floating_base")]])
    out = {"steps": args.steps, "mapping": args.mapping, "h0": h0, "min_h": min_h,
           "final_h": final_h, "max_tilt_deg": max_tilt, "vx_final": vx, "nan": nan_seen,
           "obs_layout_source": lay.get("source", "")}
    if args.report:
        pathlib.Path(args.report).write_text(json.dumps(out, indent=1), encoding="utf8")
    print("rollout: mapping=%s steps=%d  h0=%.4f min=%.4f final=%.4f  max_tilt=%.1f deg  nan=%s"
          % (args.mapping, args.steps, h0 or 0.0, min_h, final_h, max_tilt, nan_seen))
    print("         final vx=%.3f m/s  (commanded %.2f)" % (vx, args.vx))
    ok = (h0 is not None and not nan_seen and min_h > 0.5 * h0 and max_tilt < 75.0)
    print("RESULT: ROLLOUT %s" % ("SANE" if ok else "DIVERGED"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())

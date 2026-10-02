"""CPU-only gate for a RM2025-later deployment ONNX.

Checks the artifact contract that the ROS2 / sim2sim / real bridge all rely on:

  * input  "obs"     float32[1,35]
  * output "actions" float32[1,6]
  * action_order / action_order_permutation == the later contract
  * base_contract_sha256 == the contract digest recomputed from contract_rm2025_later.json
  * actuator / geometry / yaw-limit metadata agrees with the contract
  * optional *.obs_probe.npz: ONNX output on the saved observation == saved action

It never imports mjlab, torch-cuda or touches the training GPU.  Run it anywhere with
onnx + onnxruntime installed::

  python scripts/check_onnx_later.py --onnx train/deploy/rm2025_later_smoke.onnx
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort

ROOT = Path(__file__).resolve().parents[1]

# Fields write_deploy_contract.py appends AFTER computing base_contract_sha256.
ADDED_BY_CONTRACT_WRITER = {
    "base_contract_sha256", "plant", "plant_leg_torque", "plant_wheel_torque",
    "command_limits", "yaw_rate_at_unit_action", "wheel_rad_s_per_yaw_rad_s",
    "checkpoint",
}


def contract_digest(contract: dict) -> str:
    base = {k: v for k, v in contract.items() if k not in ADDED_BY_CONTRACT_WRITER}
    blob = json.dumps(base, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", required=True)
    ap.add_argument("--contract", default=str(ROOT / "train" / "deploy" /
                                             "contract_rm2025_later.json"))
    ap.add_argument("--probe", default="", help="optional *.obs_probe.npz")
    ap.add_argument("--tol", type=float, default=1e-4)
    a = ap.parse_args()

    contract = json.loads(Path(a.contract).read_text(encoding="utf-8"))
    model = onnx.load(a.onnx)
    md = {e.key: e.value for e in model.metadata_props}
    fails: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        print(("   OK   " if cond else "   FAIL ") + msg)
        if not cond:
            fails.append(msg)

    print("onnx      :", a.onnx)
    print("contract  :", a.contract)
    print("[1] io signature")
    ins = {i.name: [d.dim_value for d in i.type.tensor_type.shape.dim]
           for i in model.graph.input if i.name != "yaw_trim_vec"}
    outs = {o.name: [d.dim_value for d in o.type.tensor_type.shape.dim]
            for o in model.graph.output}
    ok(ins.get("obs") == [1, 35], "input obs float32[1,35] (got %s)" % ins.get("obs"))
    ok(outs.get("actions") == [1, 6],
       "output actions float32[1,6] (got %s)" % outs.get("actions"))

    print("[2] action order")
    want_order = list(contract["action_slot_order_exported"])
    got_order = [x for x in (md.get("action_order") or "").split(",") if x]
    ok(got_order == want_order, "action_order == %s (got %s)" % (want_order, got_order))
    want_perm = list(contract["export_action_permutation"])
    got_perm = [int(x) for x in (md.get("action_order_permutation") or "").split(",") if x]
    ok(got_perm == want_perm, "permutation == %s (got %s)" % (want_perm, got_perm))
    ok("knee" not in ",".join(want_order), "no passive knee in the exported slots")

    print("[3] contract stamp")
    want_digest = contract_digest(contract)
    ok(md.get("base_contract_sha256") == want_digest,
       "base_contract_sha256 == %s (got %s)" % (want_digest, md.get("base_contract_sha256")))
    ok(md.get("plant_kind") == contract["plant_kind"], "plant_kind agrees")
    ok(md.get("policy_coordinate_space") == contract["policy_coordinate_space"],
       "policy_coordinate_space agrees")
    ok(md.get("policy_controls_passive_knee") == "0", "passive knee not controlled")

    print("[4] actuator / geometry metadata")
    scale = [float(x) for x in (md.get("joint_action_scale") or "").split(",") if x]
    want_scale = ([contract["leg_action_scale"]] * 4
                  + [contract["wheel_action_scale"]] * 2 + [0.0, 0.0])
    ok(len(scale) >= 6 and np.allclose(scale[:6], want_scale[:6], atol=1e-9),
       "joint_action_scale %s (got %s)" % (want_scale[:6], scale[:6]))
    out_max = [float(x) for x in (md.get("joint_output_max") or "").split(",") if x]
    want_out = [contract["leg_effort"]] * 4 + [contract["wheel_effort"]] * 2
    ok(len(out_max) >= 6 and np.allclose(out_max[:6], want_out, atol=1e-9),
       "joint_output_max %s (got %s)" % (want_out, out_max[:6]))
    for key, want in (("wheel_no_load_rad_s", contract["wheel_no_load"]),
                      ("wheel_knee_speed_rad_s", contract["wheel_knee_speed"]),
                      ("wheel_voltage_line_intercept_nm",
                       contract["wheel_voltage_line_intercept"]),
                      ("leg_voltage_line_intercept_nm",
                       contract["leg_voltage_line_intercept"])):
        got = md.get(key)
        ok(got is not None and abs(float(got) - float(want)) < 1e-6,
           "%s == %.6g (got %s)" % (key, want, got))
    yaw_lim = md.get("yaw_command_limit_rad_s")
    ok(yaw_lim is not None
       and abs(float(yaw_lim) - abs(contract["command_limits"]["angular_z"][1])) < 1e-6,
       "yaw_command_limit_rad_s matches contract (got %s)" % yaw_lim)
    hw = md.get("hardware_deployable")
    ok(hw in ("0", "1"), "hardware_deployable is stamped (got %s)" % hw)
    it = int(md.get("checkpoint_iteration") or 0)
    ok("checkpoint_iteration" in md, "checkpoint_iteration is stamped (got %s)" % it)
    if hw == "1":
        ok(it >= 1000, "hardware_deployable=1 requires iteration >= 1000 (got %d)" % it)
        ok(not md.get("deploy_block_reason"),
           "no deploy_block_reason on a deployable artifact")
    else:
        print("   NOTE hardware_deployable=0: %s"
              % (md.get("deploy_block_reason") or "blocked (no reason recorded)"))

    print("[5] probe parity" if (a.probe or Path(a.onnx).with_suffix(".obs_probe.npz").exists())
          else "[5] probe parity (skipped: no npz)")
    probe = a.probe or str(Path(a.onnx).with_suffix(".obs_probe.npz"))
    if Path(probe).exists():
        z = np.load(probe)
        obs = z["obs"].astype(np.float32)
        # action_torch is the PyTorch policy output after the same trim+permutation the
        # ONNX graph applies; action is the ONNX output captured on the export host.
        ref_key = "action_torch" if "action_torch" in z.files else "action"
        ref = z[ref_key]
        sess = ort.InferenceSession(a.onnx, providers=["CPUExecutionProvider"])
        got = sess.run(None, {"obs": obs})[0]
        err = float(np.max(np.abs(got - ref)))
        ok(got.shape == (1, 6) and err <= a.tol,
           "ONNX(probe obs) == %s, max_abs_err %.3e <= %.3g" % (ref_key, err, a.tol))

    print()
    print("RESULT:", "ONNX LATER CONTRACT PASS" if not fails
          else "%d CHECK(S) FAILED" % len(fails))
    for f in fails:
        print("   -", f)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

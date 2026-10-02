"""Emit train/deploy/contract.json: the one authoritative copy of every number the
sim2sim / sim2real deployment has to agree with.

Run this IMMEDIATELY AFTER exporting a policy, with the same environment variables that
training used, because two of these values are checkpoint-specific:
  * wheel_action_scale  (v11/v12 trained at 10, v13 at 20, v14+ at 55)
  * the yaw command window (RM_WZ_MAX)
A policy trained at one scale and deployed at the other runs at the wrong speed and looks
like a failed skill rather than a config bug -- which is exactly how this project lost a day.
"""
import argparse, hashlib, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))
import rmvehicle                      # noqa: F401  registers tasks, resolves the profile
from rmvehicle import robot_cfg as RC  # noqa
from rmvehicle.names import CC, RM2025_LATER  # noqa

MODELS = {"cc": CC, "later": RM2025_LATER}
# Single source of truth: the contract must describe the plant that names.py actually
# selects.  This used to hard-code incoming/rm2025_fixed/robot_hifi.xml, which silently
# kept pointing at the 0910 model after the MOD4 switch (and skipped the deprecation guard
# in robot_cfg._resolve_path).
PLANTS = {
    "cc": str(ROOT / "robot" / "out_cc" / "rm_vehicle_cc.xml"),
    "later": str(RC._resolve_path(RM2025_LATER)),
}

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(ROOT / "train" / "deploy" / "contract.json"))
ap.add_argument("--checkpoint", default="", help="which policy this contract belongs to")
ap.add_argument("--model", choices=sorted(MODELS), default="cc",
                help="which plant this contract describes (default keeps the historic CC path)")
ap.add_argument("--plant", default="", help="override the plant MJCF path")
ap.add_argument("--wz-max", type=float, default=float(os.environ.get("RM_WZ_MAX", "14.0")))
a = ap.parse_args()
if not a.plant:
  a.plant = PLANTS[a.model]

c = RC.contract(MODELS[a.model])
xml = open(a.plant, encoding="utf-8").read()

# Fingerprint the training/deployment semantics before checkpoint-specific fields
# are appended.  The same digest is embedded in ONNX metadata by export_onnx.py.
c["base_contract_sha256"] = hashlib.sha256(
    json.dumps(c, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
).hexdigest()


def fr(needle):
    """Largest |forcerange| among motors whose joint name contains ``needle``."""
    vals = []
    for joint, rng in re.findall(r'joint="([^"]+)"[^>]*forcerange="([^"]+)"', xml):
        if needle in joint:
            vals += [abs(float(v)) for v in rng.split()]
    return max(vals) if vals else None


c["plant"] = os.path.basename(a.plant)
c["plant_leg_torque"] = fr("hip") or fr("front1")
c["plant_wheel_torque"] = fr("wheel")
c["command_limits"] = dict(linear_x=[-1.5, 2.8], angular_z=[-a.wz_max, a.wz_max],
                           height=[0.18, 0.34])
c["yaw_rate_at_unit_action"] = round(
    c["wheel_action_scale"] * c["wheel_radius"] / c["half_track"], 3)
c["wheel_rad_s_per_yaw_rad_s"] = round(c["half_track"] / c["wheel_radius"], 3)
c["checkpoint"] = a.checkpoint
# guard: the contract must describe the plant it was generated from
if c.get("plant_kind") != "similar_linkage_closed_chain":
    raise SystemExit("DEPLOYMENT CONTRACT MUST USE THE CLOSED-CHAIN PLANT")
if c.get("policy_coordinate_space") != "actuator_output_joint":
    raise SystemExit("POLICY MUST SPEAK ACTUATOR OUTPUT-JOINT COORDINATES")
if c.get("policy_controls_passive_knee") is not False:
    raise SystemExit("PASSIVE KNEE MUST NOT BE A POLICY ACTION")
if c.get("model_key") != MODELS[a.model].key:
    raise SystemExit("MODEL IDENTITY DRIFT: contract model_key %r != %r"
                     % (c.get("model_key"), MODELS[a.model].key))
if any("knee" in name for name in c.get("action_slot_order_exported", [])):
    raise SystemExit("PASSIVE KNEE LEAKED INTO THE EXPORTED ACTION ORDER")
expected_knee = c["wheel_no_load"] * (
    1.0 - c["wheel_effort"] / c["wheel_voltage_line_intercept"])
if abs(expected_knee - c["wheel_knee_speed"]) > 1.0e-3:
    raise SystemExit("WHEEL ENVELOPE IS INTERNALLY INCONSISTENT: knee %.6f vs %.6f"
                     % (c["wheel_knee_speed"], expected_knee))
if c["plant_wheel_torque"] and abs(c["plant_wheel_torque"] - c["wheel_effort"]) > 1e-6:
    raise SystemExit("PLANT/CONFIG DISAGREE: MJCF wheel forcerange %s N*m but the training "
                     "profile says %s" % (c["plant_wheel_torque"], c["wheel_effort"]))
if c["plant_leg_torque"] and abs(c["plant_leg_torque"] - c["leg_effort"]) > 1e-6:
    raise SystemExit("PLANT/CONFIG DISAGREE: MJCF leg forcerange %s but profile %s"
                     % (c["plant_leg_torque"], c["leg_effort"]))
os.makedirs(os.path.dirname(a.out), exist_ok=True)
json.dump(c, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(c, indent=1, ensure_ascii=False))
print("wrote", a.out)

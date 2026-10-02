#!/usr/bin/env python3
"""Fail closed unless the H7-to-policy joint-coordinate calibration is complete.

The policy and ROS wire protocol use *actuator output-joint* radians/Nm.  Raw
motor/encoder units, gearbox reduction, polarity and zero belong in the embedded
adapter.  In particular, front1 is the crank motor at the hip axis; the passive
knee angle must never appear in the six policy slots.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def die(message: str) -> None:
  raise SystemExit("CALIBRATION BLOCKED: " + message)


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--contract", default=str(ROOT / "train/deploy/contract.json"))
  ap.add_argument("--calibration", default=str(ROOT / "train/deploy/hardware_calibration.json"))
  ap.add_argument("--allow-unverified", action="store_true",
                  help="schema-test a template; never use this for a real enable")
  args = ap.parse_args()

  contract_path = Path(args.contract)
  calibration_path = Path(args.calibration)
  if not contract_path.is_file():
    die(f"missing deployment contract: {contract_path}")
  if not calibration_path.is_file():
    die(f"missing physical calibration: {calibration_path}; copy and measure "
        "train/deploy/hardware_calibration.template.json")
  contract = json.loads(contract_path.read_text(encoding="utf-8"))
  calibration = json.loads(calibration_path.read_text(encoding="utf-8"))

  if contract.get("plant_kind") != "similar_linkage_closed_chain":
    die("contract plant is not the validated closed chain")
  if contract.get("policy_coordinate_space") != "actuator_output_joint":
    die("policy coordinate is not actuator_output_joint")
  if contract.get("policy_controls_passive_knee") is not False:
    die("passive knee is present in the policy contract")
  if calibration.get("schema_version") != 1:
    die("unsupported calibration schema_version")
  if not calibration.get("firmware_applies_conversion"):
    die("firmware_applies_conversion must be true")
  if calibration.get("wire_coordinate") != "model_output_radians_and_output_newton_meters":
    die("wire coordinate must already be normalized to model output units")
  if not calibration.get("verified") and not args.allow_unverified:
    die("verified=false; physical signs/zeros/reductions have not been accepted")

  expected = list(contract.get("action_slot_order_exported", []))
  rows = list(calibration.get("joints", []))
  got = [row.get("name") for row in rows]
  if got != expected:
    die(f"joint order {got!r} does not equal policy/H7 order {expected!r}")
  roles = contract.get("leg_drive_roles", {})
  wheel_roles = {"left_wheel_joint": "left_wheel_drive",
                 "right_wheel_joint": "right_wheel_drive"}
  for row in rows:
    name = row["name"]
    if "knee" in name:
      die(f"passive knee leaked into active calibration: {name}")
    expected_role = roles.get(name, wheel_roles.get(name))
    if row.get("role") != expected_role:
      die(f"{name} role {row.get('role')!r} != {expected_role!r}")
    if args.allow_unverified and not calibration.get("verified"):
      continue
    sign = row.get("sign")
    if sign not in (-1, 1):
      die(f"{name}.sign must be +1 or -1")
    for key in ("raw_zero", "raw_position_units_per_model_rad",
                "raw_effort_units_per_model_nm"):
      value = row.get(key)
      if not isinstance(value, (int, float)) or not math.isfinite(value):
        die(f"{name}.{key} must be finite")
    if row["raw_position_units_per_model_rad"] <= 0.0:
      die(f"{name}.raw_position_units_per_model_rad must be positive")
    if row["raw_effort_units_per_model_nm"] <= 0.0:
      die(f"{name}.raw_effort_units_per_model_nm must be positive")

  label = "SCHEMA ONLY" if args.allow_unverified and not calibration.get("verified") else "READY"
  print(f"CALIBRATION {label}: {calibration_path}")
  print("wire order:", ", ".join(expected))
  print("front1=crank drive, rear1=thigh drive; passive knee is not commanded")
  return 0


if __name__ == "__main__":
  sys.exit(main())

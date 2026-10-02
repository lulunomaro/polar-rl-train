"""Bake the steady-state yaw trim into an exported ONNX policy (post-processing).

Kept separate from train/export_onnx.py because the training venv deliberately does not
ship onnxruntime, while the deployment/sim2sim hosts do.  Uses THIS plant's geometry from
the contract - the old in-export path hardcoded the CC wheel radius/half-track and baked a
~2 % wrong trim into later-model policies.

  python scripts/bake_yaw_trim.py --onnx train/deploy/policy.onnx \
      --contract train/deploy/contract_rm2025_later.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import onnx

ROOT = Path(__file__).resolve().parents[1]
# Load yaw_trim.py directly: importing the rmvehicle package would pull in mjlab, which
# the deployment/CPU hosts do not need (or have).
_YT_PATH = ROOT / "train" / "rmvehicle" / "src" / "rmvehicle" / "yaw_trim.py"
_spec = importlib.util.spec_from_file_location("rmvehicle_yaw_trim", _YT_PATH)
assert _spec and _spec.loader
YT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(YT)


def set_meta(model: onnx.ModelProto, key: str, value: str) -> None:
    for e in model.metadata_props:
        if e.key == key:
            e.value = value
            return
    e = onnx.StringStringEntryProto()
    e.key, e.value = key, value
    model.metadata_props.append(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", required=True)
    ap.add_argument("--out", default="", help="default: overwrite --onnx")
    ap.add_argument("--contract", default=str(ROOT / "train" / "deploy" /
                                             "contract_rm2025_later.json"))
    ap.add_argument("--force", action="store_true",
                    help="re-bake even if a trim is already present")
    a = ap.parse_args()

    out = a.out or a.onnx
    contract = json.loads(Path(a.contract).read_text(encoding="utf-8"))
    model = onnx.load(a.onnx)
    md = {e.key: e.value for e in model.metadata_props}
    if "yaw_command_trim_rad_s" in md and not a.force:
        print("already baked: yaw_command_trim_rad_s=%s (use --force to re-bake)"
              % md["yaw_command_trim_rad_s"])
        return 0

    geom = YT.geometry_from_contract(contract)
    print("geometry: wheel_scale=%.3f wheel_radius=%.6f half_track=%.6f "
          "rad_s_per_yaw=%.4f"
          % (geom.wheel_scale, geom.wheel_radius, geom.half_track,
             geom.rad_s_per_yaw_rad_s))
    trim, y0 = YT.solve_trim(YT.session_from_model(model), geom=geom)
    if abs(trim) > 1e-4:
        YT.bake(model, trim)
    set_meta(model, "yaw_equilibrium_rad_s", "%.4f" % y0)
    set_meta(model, "yaw_command_trim_rad_s", "%.4f" % trim)
    onnx.save(model, out)
    print("YAW TRIM: untrimmed equilibrium %+0.4f rad/s -> baked %+0.4f rad/s" % (y0, trim))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

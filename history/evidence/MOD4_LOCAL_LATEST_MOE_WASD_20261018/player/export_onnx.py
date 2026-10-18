"""Export rsl_rl actor checkpoints to deterministic, deployment-shaped ONNX.

The checkpoint stores an ELU MLP under ``actor_state_dict``.  The exported graph
accepts one or more 35-D policy observations and returns the action actually
handed to the simulator, including the training wrapper's +/-6 clamp.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn


ROOT = Path(__file__).resolve().parent


class Actor(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(35, 256), nn.ELU(),
            nn.Linear(256, 128), nn.ELU(),
            nn.Linear(128, 64), nn.ELU(),
            nn.Linear(64, 6),
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return torch.clamp(self.mlp(obs), -6.0, 6.0)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def export_one(checkpoint: Path, output: Path, role: str) -> dict:
    raw = torch.load(checkpoint, map_location="cpu", weights_only=False)
    state = raw["actor_state_dict"]
    model = Actor().eval()
    missing, unexpected = model.load_state_dict(
        {k: v for k, v in state.items() if not k.startswith("distribution.")}, strict=False)
    if missing or unexpected:
        raise RuntimeError(f"state mismatch: missing={missing}, unexpected={unexpected}")

    output.parent.mkdir(parents=True, exist_ok=True)
    dummy = torch.zeros(3, 35, dtype=torch.float32)
    torch.onnx.export(
        model, dummy, output, input_names=["observation"], output_names=["action"],
        dynamic_axes={"observation": {0: "batch"}, "action": {0: "batch"}},
        opset_version=18, do_constant_folding=True, dynamo=False,
    )
    onnx.checker.check_model(onnx.load(output))

    rng = np.random.default_rng(20260913)
    cases = np.concatenate([
        np.zeros((1, 35), np.float32),
        rng.normal(0.0, 0.5, (64, 35)).astype(np.float32),
        rng.uniform(-3.0, 3.0, (64, 35)).astype(np.float32),
    ])
    with torch.no_grad():
        expected = model(torch.from_numpy(cases)).numpy()
    session = ort.InferenceSession(str(output), providers=["CPUExecutionProvider"])
    actual = session.run(["action"], {"observation": cases})[0]
    max_abs_error = float(np.max(np.abs(expected - actual)))
    if max_abs_error > 2.0e-5:
        raise RuntimeError(f"ONNX parity failed: max_abs_error={max_abs_error:g}")

    meta = {
        "schema_version": 1,
        "role": role,
        "source_checkpoint": checkpoint.name,
        "source_checkpoint_sha256": sha256(checkpoint),
        "source_iteration": int(raw.get("iter", -1)),
        "onnx_sha256": sha256(output),
        "onnx_opset": 18,
        "onnxruntime_max_abs_error": max_abs_error,
        "input": {"name": "observation", "shape": ["batch", 35], "dtype": "float32"},
        "output": {"name": "action", "shape": ["batch", 6], "dtype": "float32", "clamp": [-6.0, 6.0]},
        "observation_layout": [
            {"slice": [0, 3], "name": "command_vx_vy_wz", "scale": 1.0},
            {"slice": [3, 4], "name": "height_command_m", "scale": 5.0},
            {"slice": [4, 7], "name": "base_angular_velocity_body_rad_s", "scale": 0.5},
            {"slice": [7, 10], "name": "projected_gravity_body", "scale": 1.0},
            {"slice": [10, 14], "name": "leg_position_relative_rad", "scale": 1.0},
            {"slice": [14, 16], "name": "reserved_wheel_position", "constant": 0.0},
            {"slice": [16, 20], "name": "leg_velocity_rad_s", "scale": 0.1},
            {"slice": [20, 22], "name": "wheel_velocity_rad_s", "scale": 0.1},
            {"slice": [22, 28], "name": "last_applied_action", "scale": 1.0},
            {"slice": [28, 35], "name": "mode", "labels": ["normal", "stair", "slope", "recover", "jump", "height", "state_time"]},
        ],
        "leg_state_order": ["left_crank", "left_hip", "right_crank", "right_hip"],
        "action_order": ["left_crank", "left_hip", "right_crank", "right_hip", "left_wheel_spin", "right_wheel_spin"],
        "deterministic": True,
    }
    output.with_suffix(".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--role", default="manual")
    args = parser.parse_args()
    if args.checkpoint:
        jobs = [(args.checkpoint, args.output or ROOT / "policies" / (args.checkpoint.stem + ".onnx"), args.role)]
    else:
        jobs = [
            (ROOT / "incoming" / "model_16295.pt", ROOT / "policies" / "mod4_general_16295.onnx", "recommended_general"),
            (ROOT / "incoming" / "model_399.pt", ROOT / "policies" / "mod4_tunnel_399_ab_only.onnx", "ab_comparison_not_mature"),
        ]
    for checkpoint, output, role in jobs:
        print(json.dumps(export_one(checkpoint.resolve(), output.resolve(), role), ensure_ascii=False))


if __name__ == "__main__":
    main()

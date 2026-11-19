# SPDX-License-Identifier: MIT
"""Deployment of the frozen Gemini stair and jump experts with a shared observation stream."""
from __future__ import annotations

import hashlib
import io
from pathlib import Path
import sys

import numpy as np
import torch
from torch import nn

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
STAIR_SOURCE = LOCAL / "MOD4V3_AUTONOMOUS_ALLSPEED_STAIR_MOE_20261118"
JUMP_SOURCE = LOCAL / "MOD4V3_INSTANT_LQR_STYLE_RL_JUMP_20261118"
for path in (STAIR_SOURCE, JUMP_SOURCE):
    sys.path.insert(0, str(path))

import autonomous_stair_moe_model as stair  # noqa: E402
import moe_instant_jump_model as jump  # noqa: E402

C874_SHA = stair.EXPECTED_C874_SHA256
STAIR_SHA = "f4185e24d4261870ed3bbab1789a0e32434b9cef305c558f83a2c4ab3e8bf4eb"
JUMP_SHA = "e2d836573e6f89002a5769b1dcacc212f18cc9c24329ad9a13108607578b2c8c"
SOURCE_SHA = {"E0": C874_SHA, "E1": STAIR_SHA, "E2": JUMP_SHA}
WEIGHTS = HERE / "weights"
PACKAGE = WEIGHTS / "model_autonomous_three_expert.pt"
FORMAT = "MOD4V3_AUTONOMOUS_THREE_EXPERT_V1"


class AutonomousThreeExpert(nn.Module):
    """E0/E1 learned soft gate, and the trained E2 jump-request input."""

    def __init__(self) -> None:
        super().__init__()
        self.stair = stair.AutonomousStairMoE()
        self.jump = jump.InstantPureNeuralJumpExpert()
        self.history = stair.ProprioHistoryQueue40()

    def reset_history(self) -> None:
        self.history.clear()

    @torch.inference_mode()
    def act(self, obs: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
        x = torch.from_numpy(obs).reshape(1, stair.OBS_DIM)
        history = self.history.append(x)
        if obs[jump.JUMP_MODE_BIT_INDEX] > 0.5:
            action = self.jump(x, history).clamp(-jump.ACTION_CLIP, jump.ACTION_CLIP)
            return action[0].numpy(), {"e0": 0.0, "e1": 0.0, "e2": 1.0}

        # E1 was trained with normal-mode bits. Use the same joint/IMU/action
        # history during and after jumps, with that expert's native mode bits.
        x_stair = stair.canonicalize_normal_obs(x)
        history_stair = stair.canonicalize_normal_obs(
            history.view(1, stair.HIST_LEN, stair.OBS_DIM)
        ).flatten(-2)
        out = self.stair.compute_all_heads(x_stair, history_stair)
        g = float(out["g_eff"].item())
        return out["act"][0].numpy(), {
            "e0": 1.0 - g, "e1": g, "e2": 0.0,
            "virtual_height": float(out["h_virt"].item()),
        }


def checked_source(path: Path, expected: str, *, weights_only: bool = True) -> dict:
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != expected:
        raise RuntimeError(f"Unexpected SHA-256 for {path.name}: {sha}")
    return torch.load(io.BytesIO(raw), map_location="cpu", weights_only=weights_only)


def same_locomotion(expected: dict, source: dict, prefix: str) -> None:
    for name, value in expected.items():
        if not torch.equal(value, source[prefix + name]):
            raise RuntimeError(f"c874 weight mismatch in {prefix}{name}")


def pack() -> None:
    if stair.HIST_LEN != jump.HIST_LEN or stair.OBS_DIM != jump.OBS_DIM:
        raise RuntimeError("Gemini observation history contracts differ")
    # The legacy c874 checkpoint contains non-tensor metadata and is pinned by SHA.
    c874 = checked_source(stair.C874_CKPT_PATH, C874_SHA, weights_only=False)
    e0 = {k.removeprefix("mlp."): v for k, v in c874["actor_state_dict"].items() if k.startswith("mlp.")}
    e1 = checked_source(WEIGHTS / "model_autonomous_stair_moe_best.pt", STAIR_SHA)
    e2 = checked_source(WEIGHTS / "model_instant_jump_best.pt", JUMP_SHA)
    e1_weights = e1["moe_state_dict"]
    e2_weights = e2["model_state_dict"]
    for weights, prefix in (
        (e1_weights, "e0."),
        (e1_weights, "e1_stair.loco_base."),
        (e2_weights, "actor_body.e0."),
        (e2_weights, "actor_body.e_jump.loco_base."),
    ):
        same_locomotion(e0, weights, prefix)

    model = AutonomousThreeExpert()
    model.stair.load_state_dict(e1_weights, strict=True)
    jump_prefix = "actor_body.e_jump."
    model.jump.load_state_dict(
        {name.removeprefix(jump_prefix): value for name, value in e2_weights.items() if name.startswith(jump_prefix)},
        strict=True,
    )
    tmp = PACKAGE.with_suffix(".tmp")
    torch.save({
        "format": FORMAT,
        "source_sha256": SOURCE_SHA,
        "observation_dim": stair.OBS_DIM,
        "history_len": stair.HIST_LEN,
        "action_dim": stair.ACT_DIM,
        "state_dict": model.state_dict(),
    }, tmp)
    tmp.replace(PACKAGE)
    print(f"{PACKAGE.name} {hashlib.sha256(PACKAGE.read_bytes()).hexdigest()}")


def load() -> tuple[AutonomousThreeExpert, str]:
    torch.set_num_threads(1)
    raw = PACKAGE.read_bytes()
    payload = torch.load(io.BytesIO(raw), map_location="cpu", weights_only=True)
    if payload["format"] != FORMAT or payload["source_sha256"] != SOURCE_SHA:
        raise RuntimeError("Unexpected autonomous MoE checkpoint provenance")
    model = AutonomousThreeExpert()
    model.load_state_dict(payload["state_dict"], strict=True)
    return model.eval().requires_grad_(False), hashlib.sha256(raw).hexdigest()


if __name__ == "__main__":
    torch.set_num_threads(1)
    pack()

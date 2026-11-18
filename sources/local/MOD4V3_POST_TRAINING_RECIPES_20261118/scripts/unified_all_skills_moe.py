"""Unified 3-Expert MoE Merger, Zero-Interference Verifier, and Combined Hurdle + Stair Showcase
for MOD4v3-Family Wheel-Leg Robots (`MOD4V3_POST_TRAINING_RECIPES_20261118`).

Combines into a single pure-neural `(obs 35D, obs_history 420D) -> action 6D` model:
  - E0 (mode=[1,0,0,0,0,0,0]): Frozen c874 full-DR flat/rough/slope/descent locomotion
  - E1 (obs[29] > 0.5):        Best RL Anti-Cheat Stair-Climbing Expert
  - E2 (obs[30] > 0.5):        Best RL Deep-Crouch High-Jump & Moving-Jump Expert
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import mujoco as mj
import numpy as np
import torch
from torch import nn

RECIPES_DIR = Path(__file__).resolve().parents[1]
REPO = RECIPES_DIR.parents[2]
C874_PATH = REPO / "deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt"
JUMP_DIR = REPO / "sources/local/MOD4V3_RL_HIGH_MOVING_JUMP_20261118"
STAIR_SINGLE_DIR = REPO / "sources/local/MOD4V3_MOE_ROUTE2_SINGLE200_STABLE_5OF5_20261118"
E_TEACH = REPO / "sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class UnifiedThreeExpertMoE(nn.Module):
    """Single pure-neural deployment module routing E0 (locomotion), E1 (stairs), and E2 (high/moving jump)."""

    def __init__(self, stair_common_mod, jump_mod):
        super().__init__()
        self.e0 = stair_common_mod.action_mlp(35)
        self.e0.requires_grad_(False)
        self.e1_stair = stair_common_mod.StairExpert()
        self.e2_jump = jump_mod.PureNeuralJumpExpert(latent_dim=64)
        self.history = stair_common_mod.HistoryQueue()

    def reset_history(self):
        self.history.buffer = None

    @torch.inference_mode()
    def forward_with_history(self, obs: torch.Tensor, hist: torch.Tensor) -> torch.Tensor:
        is_stair = obs[..., 29:30] > 0.5
        is_jump = (obs[..., 30:31] > 0.5) & (~is_stair)

        normal_obs = obs.clone()
        normal_obs[..., 28:35] = normal_obs.new_tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        out = self.e0(normal_obs)
        if bool(is_stair.any()):
            out = torch.where(is_stair, self.e1_stair(obs, hist), out)
        if bool(is_jump.any()):
            out = torch.where(is_jump, self.e2_jump(obs, hist), out)
        return out.clamp(-6.0, 6.0)

    @torch.inference_mode()
    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        hist = self.history.append(obs)
        return self.forward_with_history(obs, hist)


def build_and_verify_unified_moe(stair_ckpt_path: Path, jump_ckpt_path: Path, out_ckpt_path: Path) -> dict:
    stair_rc = _load_module("stair_rc", STAIR_SINGLE_DIR / "support/mod4v3_ppo_v1/route2_common.py")
    jump_mod = _load_module("jump_mod", JUMP_DIR / "moe_jump_model.py")

    c874 = torch.load(C874_PATH, map_location="cpu", weights_only=False)
    stair_ck = torch.load(stair_ckpt_path, map_location="cpu", weights_only=False)
    jump_ck = torch.load(jump_ckpt_path, map_location="cpu", weights_only=False)

    unified = UnifiedThreeExpertMoE(stair_rc, jump_mod)
    # 1. Load E0
    e0_sd = {k.removeprefix("mlp."): v.clone() for k, v in c874["actor_state_dict"].items() if k.startswith("mlp.")}
    unified.e0.load_state_dict(e0_sd, strict=True)
    # 2. Load E1
    e1_sd = {k.removeprefix("mlp.e1."): v.clone() for k, v in stair_ck["actor_state_dict"].items() if k.startswith("mlp.e1.")}
    unified.e1_stair.load_state_dict(e1_sd, strict=True)
    # 3. Load E2
    j_state = jump_ck["state_dict"]
    e2_sd = {k.removeprefix("actor_body.e_jump."): v.clone() for k, v in j_state.items() if k.startswith("actor_body.e_jump.")}
    unified.e2_jump.load_state_dict(e2_sd, strict=True)
    unified.eval()

    # Verify bit-exact 0.0 cross-expert interference on random test batch
    torch.manual_seed(20261118)
    obs_test = torch.randn(64, 35)
    hist_test = torch.randn(64, 420)

    obs_e0 = obs_test.clone()
    obs_e0[:, 28:35] = torch.tensor([1., 0., 0., 0., 0., 0., 0.])
    obs_e1 = obs_test.clone()
    obs_e1[:, 28:35] = torch.tensor([0., 1., 0., 0., 0., 1., 0.])
    obs_e2 = obs_test.clone()
    obs_e2[:, 28:35] = torch.tensor([1., 0., 1., 0., 0., 0., 0.])

    ref_stair = stair_rc.LocalRoute2Actor().load_checkpoint(stair_ck).eval()
    ref_jump = jump_mod.MoEJumpActorCritic.load_from_checkpoint(jump_ckpt_path).eval()

    err_e0 = float((unified.forward_with_history(obs_e0, hist_test) - ref_stair(obs_e0, hist_test).clamp(-6, 6)).abs().max())
    err_e1 = float((unified.forward_with_history(obs_e1, hist_test) - ref_stair(obs_e1, hist_test).clamp(-6, 6)).abs().max())
    err_e2 = float((unified.forward_with_history(obs_e2, hist_test) - ref_jump.act_deterministic(obs_e2, hist_test)).abs().max())
    assert err_e0 == 0.0 and err_e1 == 0.0 and err_e2 == 0.0, (err_e0, err_e1, err_e2)

    out_ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": "MOD4V3_UNIFIED_3EXPERT_MOE_V1",
        "c874_sha256": hashlib.sha256(C874_PATH.read_bytes()).hexdigest(),
        "stair_source": str(stair_ckpt_path),
        "stair_sha256": hashlib.sha256(stair_ckpt_path.read_bytes()).hexdigest(),
        "jump_source": str(jump_ckpt_path),
        "jump_sha256": hashlib.sha256(jump_ckpt_path.read_bytes()).hexdigest(),
        "zero_interference_max_abs_error": {"E0": err_e0, "E1_stair": err_e1, "E2_jump": err_e2},
        "state_dict": unified.state_dict(),
    }
    torch.save(payload, out_ckpt_path)
    u_sha = hashlib.sha256(out_ckpt_path.read_bytes()).hexdigest()
    return {
        "unified_checkpoint": str(out_ckpt_path),
        "unified_sha256": u_sha,
        "c874_sha256": payload["c874_sha256"],
        "stair_sha256": payload["stair_sha256"],
        "jump_sha256": payload["jump_sha256"],
        "zero_interference_verified": True,
        "max_abs_errors": payload["zero_interference_max_abs_error"],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stair-ckpt", type=Path, required=True)
    p.add_argument("--jump-ckpt", type=Path, required=True)
    p.add_argument("--out", type=Path, default=RECIPES_DIR / "weights/model_unified_3expert_moe.pt")
    args = p.parse_args()
    info = build_and_verify_unified_moe(args.stair_ckpt, args.jump_ckpt, args.out)
    (RECIPES_DIR / "UNIFIED_MOE_VERIFICATION.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

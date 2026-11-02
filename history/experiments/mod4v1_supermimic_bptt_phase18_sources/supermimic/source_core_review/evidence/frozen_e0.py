"""Frozen 400 N / 50 Hz E0 codec and a native SuperMimic residual policy.

E0 consumes the original, unnormalized 35-value policy observation. Its raw
output order is Lcrank, Lhip, Rcrank, Rhip, Lwheel, Rwheel. The caller owns the
single final action clip and the original position/velocity target pipeline.

Freezing parameters deliberately does not disable autograd: imagination needs
the derivative of E0's action with respect to its observation.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path
from typing import Iterator

import torch
from torch import nn


E0_CHECKPOINT_SHA256 = "a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a"
E0_CHECKPOINT_BYTES = 14_031_973
E0_OBS_DIM = 35
E0_ACTION_DIM = 6
E0_ACTION_ORDER = (
    "left_crank", "left_hip", "right_crank", "right_hip",
    "left_wheel_spin", "right_wheel_spin",
)


def module_state_hash(module: nn.Module) -> str:
    """Hash named tensor values deterministically, without NumPy or filesystem IO."""
    digest = hashlib.sha256()
    for name, value in sorted(module.state_dict().items()):
        if not isinstance(value, torch.Tensor):
            raise TypeError(f"Non-tensor state entry: {name}")
        tensor = value.detach().cpu().contiguous()
        header = json.dumps(
            [name, str(tensor.dtype), list(tensor.shape)], separators=(",", ":")
        ).encode("utf8")
        digest.update(len(header).to_bytes(8, "little"))
        digest.update(header)
        digest.update(bytes(tensor.reshape(-1).view(torch.uint8).tolist()))
    return digest.hexdigest()


class FrozenE0(nn.Module):
    """Load the exact v89d final_valid_update82 checkpoint as a frozen mean actor.

    The checkpoint's learned STD is retained as provenance, but inference uses
    the deterministic mean. No optimizer, critic, observation normalizer, action
    scaling or activation is added to that mean.
    """

    def __init__(
        self,
        checkpoint_path: str | Path,
        expected_sha: str = E0_CHECKPOINT_SHA256,
        device: str | torch.device = "cpu",
    ):
        super().__init__()
        expected_sha = str(expected_sha).lower()
        if expected_sha != E0_CHECKPOINT_SHA256:
            raise ValueError("Expected SHA must identify the frozen v89d E0 checkpoint")
        path = Path(checkpoint_path)
        if path.stat().st_size != E0_CHECKPOINT_BYTES:
            raise ValueError(f"E0 checkpoint size must be {E0_CHECKPOINT_BYTES} bytes")
        raw = path.read_bytes()
        actual_sha = hashlib.sha256(raw).hexdigest()
        if len(raw) != E0_CHECKPOINT_BYTES or actual_sha != expected_sha:
            raise ValueError("E0 checkpoint SHA/size mismatch")
        # Decode only after binding the bytes to the authoritative source hash.
        checkpoint = torch.load(io.BytesIO(raw), map_location="cpu", weights_only=False)
        if not isinstance(checkpoint, dict) or not isinstance(checkpoint.get("actor_state_dict"), dict):
            raise ValueError("E0 checkpoint is missing actor_state_dict")
        actor_state = checkpoint["actor_state_dict"]
        layers = (0, 2, 4, 6)
        names = {f"mlp.{i}.{kind}" for i in layers for kind in ("weight", "bias")}
        if set(actor_state) != names | {"distribution.std_param"}:
            raise ValueError("E0 actor must contain exactly eight MLP tensors and its STD")
        for name, value in actor_state.items():
            if not isinstance(value, torch.Tensor) or not value.is_floating_point():
                raise ValueError(f"Invalid E0 actor tensor: {name}")
            if not bool(torch.isfinite(value).all()):
                raise ValueError(f"Non-finite E0 actor tensor: {name}")
        dtype = actor_state["mlp.0.weight"].dtype
        if any(value.dtype != dtype for value in actor_state.values()):
            raise ValueError("E0 actor tensor dtypes differ")
        self.mlp = nn.Sequential(
            nn.Linear(35, 256, dtype=dtype), nn.ELU(),
            nn.Linear(256, 128, dtype=dtype), nn.ELU(),
            nn.Linear(128, 64, dtype=dtype), nn.ELU(),
            nn.Linear(64, 6, dtype=dtype),
        )
        weights = {name.removeprefix("mlp."): actor_state[name] for name in names}
        self.mlp.load_state_dict(weights, strict=True)
        std = actor_state["distribution.std_param"]
        if tuple(std.shape) != (E0_ACTION_DIM,):
            raise ValueError("E0 learned STD must have six entries")
        self.register_buffer("source_std", std.detach().clone())
        iteration = checkpoint.get("iter")
        self.source_iteration = None if iteration is None else int(iteration)
        self.checkpoint_path = str(path.resolve())
        self.checkpoint_sha = actual_sha
        self.checkpoint_bytes = len(raw)
        self.requires_grad_(False)
        self.to(device)
        self.eval()
        self._loaded_state_hash = self.state_hash()

    def train(self, mode: bool = True) -> FrozenE0:
        # A parent residual policy may enter train mode; the expert remains frozen.
        super().train(False)
        return self

    def forward(self, obs35: torch.Tensor) -> torch.Tensor:
        if obs35.ndim < 1 or obs35.shape[-1] != E0_OBS_DIM:
            raise ValueError("FrozenE0 expects (..., 35) original policy observations")
        if not obs35.is_floating_point():
            raise TypeError("FrozenE0 observations must be floating-point tensors")
        # Casting preserves the input gradient; no detach/no_grad belongs here.
        return self.mlp(obs35.to(dtype=self.mlp[0].weight.dtype))

    def state_hash(self) -> str:
        return module_state_hash(self)

    def receipt(self) -> dict:
        current_hash = self.state_hash()
        return {
            "checkpoint_path": self.checkpoint_path,
            "checkpoint_sha256": self.checkpoint_sha,
            "checkpoint_bytes": self.checkpoint_bytes,
            "source_iteration": self.source_iteration,
            "architecture": [35, 256, 128, 64, 6],
            "hidden_activation": "ELU",
            "action_order": list(E0_ACTION_ORDER),
            "learned_std_provenance_only": self.source_std.detach().cpu().tolist(),
            "weights_frozen": all(not p.requires_grad for p in self.parameters()),
            "input_gradients_preserved": True,
            "loaded_state_sha256": self._loaded_state_hash,
            "current_state_sha256": current_hash,
            "state_unchanged": current_hash == self._loaded_state_hash,
            "output": "raw deterministic mean; final clip is external",
        }


class E0ResidualPolicy(nn.Module):
    """Wrap vendor.Policy so collection and imagination use the same total action.

    Every observation-history frame ends with the original raw obs35. Only the
    newest such slice reaches the frozen expert; the residual uses the vendor's
    normalizers and goal encoder. The expert is intentionally outside those
    normalizers and receives no extra absolute state or goal channels.
    """

    def __init__(self, residual: nn.Module, expert: FrozenE0, residual_scale: float = 1.0):
        super().__init__()
        if not math.isfinite(float(residual_scale)):
            raise ValueError("Residual scale must be finite")
        for name in ("enc", "dec", "obs_norm", "goal_norm"):
            if not hasattr(residual, name):
                raise TypeError(f"Residual policy is missing vendor interface: {name}")
        self.residual = residual
        self.expert = expert
        self.expert.requires_grad_(False)
        self.expert.eval()
        self.register_buffer("_residual_scale", torch.tensor(float(residual_scale)))

    @property
    def enc(self):
        return self.residual.enc

    @property
    def dec(self):
        return self.residual.dec

    @property
    def obs_norm(self):
        return self.residual.obs_norm

    @property
    def goal_norm(self):
        return self.residual.goal_norm

    @property
    def hist(self):
        return self.residual.hist

    @property
    def residual_scale(self) -> float:
        return float(self._residual_scale.detach().cpu())

    def forward(self, obs_hist: torch.Tensor, goal: torch.Tensor) -> torch.Tensor:
        if obs_hist.ndim < 3 or obs_hist.shape[-2] < 1 or obs_hist.shape[-1] < E0_OBS_DIM:
            raise ValueError("Expected (..., history, obs_dim>=35), newest frame last")
        base = self.expert(obs_hist[..., -1, -E0_OBS_DIM:])
        delta = self.residual(obs_hist, goal)
        if delta.shape != base.shape:
            raise ValueError("Residual policy must produce the same (..., 6) shape as E0")
        return base + self._residual_scale * delta

    def trainable_parameters(self) -> Iterator[nn.Parameter]:
        """Use for opt_pi; the shared expert never enters the optimizer."""
        return (p for p in self.parameters() if p.requires_grad)

    def expert_state_hash(self) -> str:
        return self.expert.state_hash()

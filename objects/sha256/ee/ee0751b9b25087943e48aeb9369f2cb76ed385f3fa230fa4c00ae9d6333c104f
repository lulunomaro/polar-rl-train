#!/usr/bin/env python3
"""Create an auditable constant-action specialist seed from an RSL-RL checkpoint.

The actor architecture and critic are preserved, but the actor's final affine layer is replaced
by a constant expert action.  This is behavior cloning for tasks whose validated controller is a
constant action (the tunnel low pose and wheel speed).  The output is a specialist seed, never a
drop-in replacement for the mixed all-terrain policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--actions", required=True,
                    help="comma-separated six-dimensional normalized expert action")
    ap.add_argument("--std", type=float, default=0.02)
    args = ap.parse_args()

    src, dst = Path(args.input), Path(args.output)
    action = [float(x) for x in args.actions.split(",")]
    if len(action) != 6 or not all(float("-inf") < x < float("inf") for x in action):
        raise ValueError("--actions must contain six finite values")
    if not 0.0 < args.std <= 1.0:
        raise ValueError("--std must be in (0, 1]")

    ck = torch.load(src, map_location="cpu", weights_only=False)
    actor = ck.get("actor_state_dict")
    if not isinstance(actor, dict):
        raise ValueError("checkpoint has no actor_state_dict")
    wkey, bkey = "mlp.6.weight", "mlp.6.bias"
    if wkey not in actor or bkey not in actor:
        raise ValueError("unexpected actor head keys")
    if tuple(actor[wkey].shape[:1]) != (6,) or tuple(actor[bkey].shape) != (6,):
        raise ValueError("actor output is not six-dimensional")

    actor[wkey] = torch.zeros_like(actor[wkey])
    actor[bkey] = torch.tensor(action, dtype=actor[bkey].dtype)
    for key in tuple(actor):
        if key.endswith("log_std_param"):
            actor[key] = torch.full_like(actor[key], torch.log(torch.tensor(args.std)))
        elif key.endswith("std_param"):
            actor[key] = torch.full_like(actor[key], args.std)
    # Keep the optimizer dictionary for strict evaluation loaders.  MOD4 warm-start training
    # explicitly loads actor/critic with optimizer=False, so these moments are never reused.
    infos = ck.setdefault("infos", {})
    if not isinstance(infos, dict):
        infos = ck["infos"] = {"previous_infos_repr": repr(infos)}
    infos["constant_specialist"] = {
        "source": str(src), "source_sha256": sha256(src),
        "normalized_action": action, "std": args.std,
    }

    dst.parent.mkdir(parents=True, exist_ok=True)
    torch.save(ck, dst)
    report = {
        "schema": "mod4.constant_specialist.v1",
        "source": str(src), "source_sha256": sha256(src),
        "output": str(dst), "output_sha256": sha256(dst),
        "normalized_action": action, "std": args.std,
        "actor_head_weight_nonzero": int(torch.count_nonzero(actor[wkey])),
        "actor_head_bias": actor[bkey].tolist(),
    }
    dst.with_suffix(dst.suffix + ".json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

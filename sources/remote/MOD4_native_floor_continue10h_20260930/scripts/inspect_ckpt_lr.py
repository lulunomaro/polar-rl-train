"""Print the iteration and optimizer learning rate stored inside an rsl_rl checkpoint.

Why: rsll_rl's PPO defaults to schedule="adaptive" and silently multiplies the learning
rate by 1.5 whenever kl_mean < desired_kl / 2 (capped at 1e-2, i.e. 100x the 1e-4 start).
The training log never prints it, so the only ground truth is the optimizer state that
gets serialised into each checkpoint.

Usage:
    python scripts/inspect_ckpt_lr.py <checkpoint.pt> [more.pt ...]
"""
from __future__ import annotations

import sys

import torch


def describe(path: str) -> None:
    ck = torch.load(path, map_location="cpu", weights_only=False)
    print("=" * 78)
    print("file:", path)
    print("keys:", sorted(ck.keys()))
    print("iteration:", ck.get("iter"))
    opt = ck.get("optimizer_state_dict")
    if not opt:
        print("optimizer_state_dict: MISSING")
    else:
        for i, group in enumerate(opt.get("param_groups", [])):
            keep = {k: group.get(k) for k in ("lr", "eps", "weight_decay", "betas", "amsgrad")}
            print("param_group[%d]: %s" % (i, keep))
    for key in ("infos", "config"):
        if key in ck:
            value = ck[key]
            if hasattr(value, "items"):
                skip = ("model_state_dict", "optimizer_state_dict")
                value = {k: v for k, v in value.items() if k not in skip}
            print("%s: %s" % (key, value))
    sd = ck.get("model_state_dict") or ck.get("actor_critic_state_dict")
    if isinstance(sd, dict):
        for name in [k for k in sd if "std" in k.lower()]:
            tensor = sd[name]
            try:
                flat = tensor.reshape(-1)[:6].tolist()
                print("state[%s]: shape=%s first=%s" % (name, tuple(tensor.shape), flat))
            except Exception as exc:  # pragma: no cover
                print("state[%s]: %s" % (name, exc))


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    for path in argv[1:]:
        try:
            describe(path)
        except Exception as exc:
            print("FAILED %s: %s" % (path, exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

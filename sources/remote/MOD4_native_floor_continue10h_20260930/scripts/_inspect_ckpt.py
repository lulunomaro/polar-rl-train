"""Print what a MOD4 checkpoint actually contains (no Isaac needed).

    python scripts/_inspect_ckpt.py <checkpoint.pt>
"""
import sys

import torch

ck = torch.load(sys.argv[1], map_location="cpu", weights_only=False)
print("top keys:", list(ck.keys()))
sd = (ck.get("model_state_dict") or ck.get("state_dict")
      or ck.get("actor_state_dict") or {})
if not sd:
    print("no model_state_dict; nothing else to inspect")
else:
    keys = [k for k in sd if "std" in k.lower()]
    print("std-ish keys:", keys)
    for k in keys:
        print("   %-40s shape=%s mean=%.6f" % (k, tuple(sd[k].shape), float(sd[k].mean())))
    print("first 6 param names:", list(sd)[:6])
print("infos:", ck.get("infos"))
print("iteration:", ck.get("iter"), "learning_iteration:", ck.get("learning_iteration"))

"""Print the lr / std / provenance of a warm-start seed checkpoint (read only)."""
import sys

import torch

path = sys.argv[1]
d = torch.load(path, map_location="cpu", weights_only=False)
groups = d["optimizer_state_dict"]["param_groups"]
print("path         :", path)
print("lr per group :", [g["lr"] for g in groups])
print("adam moments :", len(d["optimizer_state_dict"]["state"]))
print("iter         :", d.get("iter"))
sd = d["actor_state_dict"]
std = sd.get("distribution.std_param", sd.get("distribution.log_std_param"))
print("std          :", [round(float(x), 4) for x in std])
infos = d.get("infos") or {}
print("note         :", infos.get("warm_start_note"))
print("lr_source    :", infos.get("warm_start_lr_source"))
print("warm_from    :", infos.get("warm_start_from"))

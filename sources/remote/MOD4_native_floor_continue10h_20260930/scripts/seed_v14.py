"""Build v14's starting checkpoint out of v12's, adapted to the corrected plant.

Three measured problems have to be fixed in the checkpoint before fine-tuning is meaningful:

1. ACTION-UNIT CONTINUITY (this is the one that silently breaks a seed).
   v12 was trained with WHEEL_ACTION_SCALE = 10 (read straight out of its own
   params/env.yaml).  v14 uses 55, because at 10 the *policy output* ran out before the
   hardware did: v12's wheel actions saturated at about +-2.2 raw -> 22 rad/s of wheel ->
   5.9 rad/s of yaw, which is exactly the 5.35/5.75 rad/s plateau v11 and v12 reported.  The
   gyro ceiling was an action unit, not a learning failure.  Loading v12 unchanged at scale 55
   multiplies every wheel command by 5.5: the smoke test showed the chassis flinging itself to
   13 rad/s while falling over, and a naive curriculum reading that as "can hold the rate".
   So the wheel rows of the actor's output layer are divided by 55/10, which keeps the
   *physical* wheel velocity command identical.

2. EXPLORATION.  v12's log_std had collapsed to std 0.097-0.165.  A plant whose chassis COM
   just moved 0.239 m upward and whose yaw inertia grew 14x needs the policy to leave its old
   basin, so the noise is re-opened (in physical units, after the rescale above).

3. OBSERVATION NORMALIZER.  EmpiricalNormalization updates with rate = batch/count and v12's
   count is 5.19e8 -> the statistics are frozen at the old action unit, the old inertia and
   +-6 rad/s commands.  Capping the count re-opens the window and keeps the old values as the
   prior, so it re-adapts inside one iteration instead of never.

Nothing network-shaped is touched apart from the wheel output rows: any regression we then
measure is attributable to the plant, not to this surgery.
"""
import os
import numpy as np
import torch

R = r"D:/claude2/fangzhen"
SRC = os.path.join(R, "train/logs/rsl_rl/rm_cc_v12/2026-09-05_10-10-37/model_8696.pt")
DST = os.path.join(R, "train/logs/rsl_rl/rm_cc_v14/seed_from_v12/model_8696.pt")

OLD_SCALE = float(os.environ.get("RM_SEED_OLD_WHEEL_SCALE", "10.0"))
NEW_SCALE = float(os.environ.get("RM_WHEEL_SCALE", "55.0"))
LEG_STD = float(os.environ.get("RM_SEED_LEG_STD", "0.22"))
WHL_STD = float(os.environ.get("RM_SEED_WHL_STD", "0.12"))
COUNT = int(os.environ.get("RM_SEED_NORM_COUNT", "20000"))
K = OLD_SCALE / NEW_SCALE

ck = torch.load(SRC, map_location="cpu", weights_only=False)
md = ck["actor_state_dict"]
print("checkpoint keys:", [k for k in md if k.startswith("mlp.6") or "std" in k])

w, b = md["mlp.6.weight"], md["mlp.6.bias"]
print("wheel rows before: |w| mean %.4f  bias %s"
      % (float(w[4:6].abs().mean()), np.round(b[4:6].numpy(), 3)))
w = w.clone(); b = b.clone()
w[4:6] *= K
b[4:6] *= K
md["mlp.6.weight"], md["mlp.6.bias"] = w, b
print("scaled the wheel output rows by %.4f (%.0f -> %.0f rad/s of action unit)"
      % (K, OLD_SCALE, NEW_SCALE))
print("wheel rows after : |w| mean %.4f  bias %s"
      % (float(w[4:6].abs().mean()), np.round(b[4:6].numpy(), 3)))

ls = md["distribution.log_std_param"]
print("std in :", np.round(np.exp(ls.float().numpy()), 3))
phys = np.exp(ls.float().numpy())
new = torch.tensor(np.log([LEG_STD] * 4 + [WHL_STD] * 2), dtype=ls.dtype)  # LOG-std!
md["distribution.log_std_param"] = new
print("std out:", np.round(np.exp(new.numpy()), 3),
      " -> physical  legs +-%.3f rad  wheels +-%.1f rad/s"
      % (LEG_STD * 0.5, WHL_STD * NEW_SCALE))

c0 = int(md["obs_normalizer.count"].item())
md["obs_normalizer.count"] = torch.tensor(min(c0, COUNT),
                                          dtype=md["obs_normalizer.count"].dtype)
print("obs normalizer count %d -> %d (per-update rate %.5f -> %.3f)"
      % (c0, int(md["obs_normalizer.count"]), 10240 / max(c0, 1),
         10240 / (float(md["obs_normalizer.count"]) + 10240)))

# a note inside the checkpoint so nobody later wonders what this file is
ck["rm_seed_note"] = dict(from_="rm_cc_v12 model_8696", wheel_scale_ratio=K,
                          leg_std=LEG_STD, wheel_std=WHL_STD, norm_count=COUNT)
os.makedirs(os.path.dirname(DST), exist_ok=True)
torch.save(ck, DST)
print("wrote", DST)


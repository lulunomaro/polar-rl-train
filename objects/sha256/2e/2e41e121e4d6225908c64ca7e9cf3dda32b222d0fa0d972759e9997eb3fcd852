"""Seed v15 out of v14, with the ONE thing v14's measurement says is missing: reach.

Measured on v14 (model_9200, docs/audit/skills_v14_9200_gyro.json): the policy holds
5.53 rad/s = 0.88 rev/s when asked for 14, and 5.53 rad/s of yaw needs only 20.5 rad/s of wheel
- i.e. a raw wheel action of 0.37 at the current action unit of 55.  It is not hitting a motor
limit (the M3508 curve still has ~1.5 N*m at the 46 rad/s the user's 2 rev/s needs), it is not
slipping, and it is not a plant bug: the seeded policy simply never learned to push the wheel
action past the amplitude it had at scale 10.  v14's own seed surgery multiplied the wheel rows
by 10/55 to keep the physical command identical, which by construction also kept the reachable
WHEEL-SPEED range identical - 22 rad/s, exactly the plateau we measure.

So v15 changes the exploration, not the weights: the wheel action noise is opened from
std 0.12 to 0.30 raw (= 16.5 rad/s of wheel-speed exploration, ~35% of full rate), which is what
lets PPO discover larger wheel commands at all; the new upright-gated LINEAR gyro-rate reward
then pays for every rad/s it finds.  Actor weights are otherwise copied untouched, and the
observation normalizer is re-opened (its count is what froze v12's statistics last time).
"""
import argparse, os
import numpy as np
import torch

R = r"D:/claude2/fangzhen"
ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True, help="v14 checkpoint to continue from")
ap.add_argument("--dst-dir", default=os.path.join(R, "train/logs/rsl_rl/rm_cc_v15/seed_from_v14"))
ap.add_argument("--leg-std", type=float, default=float(os.environ.get("RM_SEED_LEG_STD", "0.22")))
ap.add_argument("--wheel-std", type=float, default=float(os.environ.get("RM_SEED_WHL_STD", "0.30")))
ap.add_argument("--norm-count", type=int, default=int(os.environ.get("RM_SEED_NORM_COUNT", "20000")))
a = ap.parse_args()

ck = torch.load(a.src, map_location="cpu", weights_only=False)
md = ck["actor_state_dict"]
ls = md["distribution.log_std_param"]
print("std in :", np.round(np.exp(ls.float().numpy()), 3))
new = torch.tensor(np.log([a.leg_std] * 4 + [a.wheel_std] * 2), dtype=ls.dtype)
md["distribution.log_std_param"] = new
print("std out:", np.round(np.exp(new.numpy()), 3),
      " -> wheels explore +-%.1f rad/s of wheel speed = +-%.2f rad/s of yaw"
      % (a.wheel_std * float(os.environ.get("RM_WHEEL_SCALE", "55.0")),
         a.wheel_std * float(os.environ.get("RM_WHEEL_SCALE", "55.0")) * 0.073 / 0.270))
c0 = int(md["obs_normalizer.count"].item())
md["obs_normalizer.count"] = torch.tensor(min(c0, a.norm_count),
                                          dtype=md["obs_normalizer.count"].dtype)
print("obs normalizer count %d -> %d" % (c0, int(md["obs_normalizer.count"])))
ck["rm_seed_note"] = dict(from_=os.path.abspath(a.src), leg_std=a.leg_std,
                          wheel_std=a.wheel_std, norm_count=a.norm_count,
                          why="v14 plateaued at 0.88 rev/s; wheel exploration opened so the "
                              "linear gyro-rate reward can find larger wheel commands")
os.makedirs(a.dst_dir, exist_ok=True)
name = os.path.basename(a.src)
dst = os.path.join(a.dst_dir, name)
torch.save(ck, dst)
print("wrote", dst)

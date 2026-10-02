"""Warm-start the later no-gimbal policy from the mature CC closed-chain checkpoint.

CC v17a actor/critic shapes match the later model exactly:
    actor 35 -> 512-256-128 -> 6      critic 39 -> 512-256-128 -> 1
The only incompatibility is the action-noise parameterization: CC trained with rsl_rl's
"log" std (``distribution.log_std_param``), while the later SCUT-style config uses the
"scalar" std (``distribution.std_param``).  This converts std = exp(log_std), keeps the
actor/critic weights and the Adam state, and resets the iteration counter so the new run
starts its own budget.

Usage:
    python scripts/warm_start_from_cc.py --src <cc_model.pt> --dst <run_seed>/model_0.pt \
        --lr 1e-4

2026-09-10: the optimizer state is no longer carried over verbatim.  The CC run trained at
lr 3.8443e-4, so the seed shipped that value into a run configured for 1e-4; combined with
the rsl_rl adaptive-schedule bug it floored the new run at 1e-5 for 300 iterations
(docs/DIAG_FLAT_V1_20260910.md).  ``--lr`` now rewrites every optimizer param group on the
way out, and the value written is recorded in infos for later inspection.
"""
import argparse

import torch

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--dst", required=True)
ap.add_argument("--wheel-output-scale", type=float, default=1.0,
                help="multiply the final-layer rows for the two wheel actions; pass "
                     "old_wheel_unit/new_wheel_unit when the wheel action scale "
                     "changes so the resumed policy commands the same wheel speed")
# The target lr of the NEW run, not of the source run.  Rewriting it here is what keeps the
# "seed" from silently overriding the launcher's RM_LR.
ap.add_argument("--lr", type=float, default=1e-4,
                help="learning rate written into every optimizer param group (0 = keep)")
ap.add_argument("--drop-optimizer-state", action="store_true",
                help="throw the Adam moment estimates away (cold optimizer, warm weights); "
                     "more conservative than keeping them at a corrected lr")

a = ap.parse_args()

d = torch.load(a.src, map_location="cpu", weights_only=False)
actor = dict(d["actor_state_dict"])
critic = dict(d["critic_state_dict"])

if a.wheel_output_scale != 1.0:
    f = float(a.wheel_output_scale)
    for key in ("mlp.6.weight", "mlp.6.bias"):
        t = actor[key].clone()
        t[4:6] = t[4:6] * f
        actor[key] = t
    print("rescaled wheel output rows by %.4f" % f)

log_std = actor.pop("distribution.log_std_param", None)
if log_std is not None:
    std = torch.exp(log_std)
    actor["distribution.std_param"] = std
    print("converted log_std -> scalar std:",
          [round(float(x), 4) for x in std])
else:
    print("WARNING: source has no distribution.log_std_param (already scalar?)")

infos = dict(d.get("infos") or {})
env_state = dict(infos.get("env_state") or {})
env_state["common_step_counter"] = 0
infos["env_state"] = env_state
infos["warm_start_from"] = a.src
infos["warm_start_note"] = ("CC closed-chain actor/critic; std parameterization converted "
                            "log->scalar; iteration reset to 0")

opt = d["optimizer_state_dict"]
if a.drop_optimizer_state:
    opt = {k: v for k, v in opt.items() if k in ("param_groups", "state")}
    opt["state"] = {}
    infos["warm_start_note"] += "; Adam moments DROPPED"
    print("dropped Adam moment estimates")
old_lr = [pg.get("lr") for pg in opt.get("param_groups", [])]
if a.lr:
    for pg in opt.get("param_groups", []):
        pg["lr"] = float(a.lr)
    print("optimizer lr %s -> %s" % ([round(x, 8) if x is not None else None for x in old_lr],
                                     a.lr))
    infos["warm_start_note"] += "; optimizer lr forced to %g" % a.lr
    infos["warm_start_lr"] = float(a.lr)
    infos["warm_start_lr_source"] = old_lr
else:
    print("optimizer lr kept:", old_lr)

out = {
    "actor_state_dict": actor,
    "critic_state_dict": critic,
    "optimizer_state_dict": opt,
    "iter": 0,
    "infos": infos,
}
torch.save(out, a.dst)
print("wrote", a.dst)
print("actor keys:", len(actor), "critic keys:", len(critic))

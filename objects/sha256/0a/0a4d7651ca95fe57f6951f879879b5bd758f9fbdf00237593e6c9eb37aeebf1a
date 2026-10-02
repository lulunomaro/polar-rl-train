"""PPO hyper-parameters for the rm_vehicle tasks.

2026-09-10: re-aligned with SCUT's wheeled-legged_RL PPO config after our fresh runs
collapsed (action std 0.30 -> 12.88 with rsl_rl's default log parameterization).

SCUT facts this file now mirrors:
  * rsl_rl GaussianDistribution noise_std_type = "scalar"  (linear, not exponential)
  * learning_rate = 1e-4, desired_kl=0.01
  * value_loss_coef = 2.0, entropy_coef = 0.005, clip_param = 0.2
  * num_steps_per_env = 24, 5 learning epochs, 4 mini-batches

2026-09-10 - why the schedule is now "fixed":
  rsl_rl 5.4 runs its adaptive branch INSIDE the mini-batch loop, so a single iteration
  (5 epochs x 4 mini-batches) can divide the learning rate by 1.5 up to twenty times.
  The warm start handed this config an Adam state whose lr was 3.8443e-4; the first
  iteration alone floored it at 1e-5 and rm2025_later_flat_verify_v1 then trained 300
  iterations at 1/10th of the configured rate (see docs/DIAG_FLAT_V1_20260910.md).
  The vendored rsl_rl is patched to adapt once per iteration instead
  (scripts/patch_rsl_rl_adaptive_lr.py), but the default schedule stays "fixed" until a
  run shows the patched adaptor is well behaved.  RM_LR_SCHEDULE=adaptive opts back in.

Deliberate deviations, because our wheel action unit is 5.5x SCUT's (55 vs 10 rad/s):
  * init std 0.3 instead of SCUT's 1.0
  * std_range clamps the scalar std to [0.05, 0.5] so it cannot run away
  * clip_actions = 3.0
"""
import os

from mjlab.rl import RslRlModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoAlgorithmCfg

_INIT_STD = float(os.environ.get("RM_INIT_STD", "0.3"))
_STD_TYPE = os.environ.get("RM_STD_TYPE", "scalar")
_STD_RANGE = (float(os.environ.get("RM_STD_MIN", "0.05")),
              float(os.environ.get("RM_STD_MAX", "0.5")))
_ENTROPY_COEF = float(os.environ.get("RM_ENTROPY_COEF", "0.005"))
_LR = float(os.environ.get("RM_LR", "1e-4"))
# "fixed" | "adaptive" - see the header note.
_LR_SCHEDULE = os.environ.get("RM_LR_SCHEDULE", "fixed")
_VALUE_LOSS_COEF = float(os.environ.get("RM_VALUE_LOSS_COEF", "2.0"))
_CLIP_ACTIONS = float(os.environ.get("RM_CLIP_ACTIONS", "3.0"))


def flat_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
  return RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
      hidden_dims=(512, 256, 128), activation="elu", obs_normalization=True,
      distribution_cfg={"class_name": "GaussianDistribution",
                        "init_std": _INIT_STD, "std_type": _STD_TYPE,
                        "std_range": _STD_RANGE}),
    critic=RslRlModelCfg(
      hidden_dims=(512, 256, 128), activation="elu", obs_normalization=True),
    algorithm=RslRlPpoAlgorithmCfg(
      value_loss_coef=_VALUE_LOSS_COEF, use_clipped_value_loss=True, clip_param=0.2,
      entropy_coef=_ENTROPY_COEF, num_learning_epochs=5, num_mini_batches=4,
      learning_rate=_LR, schedule=_LR_SCHEDULE, gamma=0.99, lam=0.95,
      desired_kl=0.01, max_grad_norm=1.0),
    clip_actions=_CLIP_ACTIONS,
    experiment_name="rm_vehicle_flat",
    logger="tensorboard",
    save_interval=200,
    num_steps_per_env=24,
    max_iterations=4000,
  )

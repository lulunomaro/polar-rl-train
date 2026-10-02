"""PPO hyper-parameters: the mjlab flat-task values, re-expressed for rsl_rl 5 (Isaac Lab 3)."""
from __future__ import annotations

from isaaclab.utils.configclass import configclass
from isaaclab_rl.rsl_rl import RslRlMLPModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoAlgorithmCfg


@configclass
class Mod4FlatPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    seed = 42
    num_steps_per_env = 24
    max_iterations = 8000
    save_interval = 200
    experiment_name = "mod4_isaac_flat"
    logger = "tensorboard"
    empirical_normalization = False
    clip_actions = 3.0
    obs_groups = {"actor": ["policy"], "critic": ["critic"]}
    # Actor/critic classes are rsl_rl 5 MLPModels; the old RslRlPpoActorCriticCfg mapped to a
    # class name ("ActorCritic") that no longer exists in rsl_rl 5 and fails to resolve.
    actor = RslRlMLPModelCfg(
        hidden_dims=[512, 256, 128],
        activation="elu",
        obs_normalization=True,
        distribution_cfg=RslRlMLPModelCfg.GaussianDistributionCfg(init_std=0.3, std_type="scalar"),
    )
    critic = RslRlMLPModelCfg(
        hidden_dims=[512, 256, 128],
        activation="elu",
        obs_normalization=True,
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=2.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.005,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-4,
        schedule="fixed",  # see train/rmvehicle rl_cfg.py on the adaptive-lr trap in rsl_rl 5.4
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )

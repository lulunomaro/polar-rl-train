"""Independent E3 sequence-PPO adaptation; no simulator import or native execution.

Reference: yly-true/fudan_rl_wheel_leg, commit
8204e853dfd2ed06d85a322e1a998c3d20a3be2c, jump/wheel_legged_gym/rsl_rl/.
Local differences (capacity, log-std, grouped clipping, full checkpoint) are
intentional. See README.md for the worker contract and rollout schema.
"""
from __future__ import annotations

import copy
import math
from dataclasses import asdict, dataclass
from typing import Any, Mapping

import torch
from torch import Tensor, nn
from torch.distributions import Normal


@dataclass(frozen=True)
class PPOConfig:
    obs_dim: int = 35
    history_length: int = 5
    privileged_dim: int = 38
    latent_dim: int = 3
    action_dim: int = 6
    actor_hidden: tuple[int, ...] = (256, 128, 64)
    critic_hidden: tuple[int, ...] = (256, 128, 64)
    encoder_hidden: tuple[int, ...] = (128, 64)
    initial_std: float = 0.5
    body_velocity_scale: float = 3.0
    rollout_steps: int = 48  # Worker-owned horizon; short functional tests may differ.
    gamma: float = 0.99
    gae_lambda: float = 0.95
    epochs: int = 5
    mini_batches: int = 4
    clip_param: float = 0.2
    value_loss_coef: float = 1.0
    entropy_coef: float = 0.01
    learning_rate: float = 1e-3
    encoder_learning_rate: float = 1e-3
    desired_kl: float = 0.005
    min_learning_rate: float = 1e-5
    max_learning_rate: float = 1e-2
    main_grad_norm: float = 1.0
    encoder_grad_norm: float = 0.1
    seed: int = 1

    @property
    def history_dim(self) -> int:
        return self.obs_dim * self.history_length


class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden: tuple[int, ...], output_dim: int):
        super().__init__()
        layers: list[nn.Module] = []
        previous = input_dim
        for width in hidden:
            layers.extend((nn.Linear(previous, width), nn.ELU()))
            previous = width
        layers.append(nn.Linear(previous, output_dim))
        self.mlp = nn.Sequential(*layers)

    def forward(self, inputs: Tensor) -> Tensor:
        return self.mlp(inputs)


class SequenceActorCritic(nn.Module):
    def __init__(self, config: PPOConfig):
        super().__init__()
        self.encoder = MLP(config.history_dim, config.encoder_hidden, config.latent_dim)
        self.actor = MLP(config.obs_dim + config.latent_dim, config.actor_hidden, config.action_dim)
        self.critic = MLP(config.privileged_dim + config.latent_dim, config.critic_hidden, 1)
        # Local parameterization adaptation: positive std = exp(log_std).
        self.log_std = nn.Parameter(torch.full((config.action_dim,), math.log(config.initial_std)))

    def distribution(self, obs: Tensor, history: Tensor) -> tuple[Normal, Tensor]:
        # The reference policy does NOT send PPO gradients into its history encoder.
        with torch.no_grad():
            latent = self.encoder(history)
        mean = self.actor(torch.cat((obs, latent.detach()), dim=-1))
        sigma = self.log_std.exp().expand_as(mean)
        return Normal(mean, sigma), latent

    def value(self, privileged_obs: Tensor, stored_latent: Tensor) -> Tensor:
        return self.critic(torch.cat((privileged_obs, stored_latent.detach()), dim=-1)).squeeze(-1)


def clone_tree(value: Any) -> Any:
    """Copy tensor leaves too: returned checkpoints must never alias live state."""
    if isinstance(value, Tensor):
        return value.detach().clone()
    if isinstance(value, dict):
        return {key: clone_tree(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clone_tree(item) for item in value]
    if isinstance(value, tuple):
        return tuple(clone_tree(item) for item in value)
    return copy.deepcopy(value)


def timeout_bootstrap_rewards(rewards: Tensor, values: Tensor, time_outs: Tensor,
                              gamma: float = 0.99) -> Tensor:
    """Literal upstream compatibility: r_t += gamma * V_t * timeout_t.

    V_t is the collection-time PRE-step value, NOT a terminal-observation value.
    Dones (including timeouts) still cut GAE. Input rewards must be unadjusted.
    """
    if rewards.shape != values.shape or rewards.shape != time_outs.shape:
        raise ValueError("rewards, values and time_outs must have identical shapes")
    return rewards.detach().clone() + gamma * values.detach() * time_outs.to(values.dtype)


def compute_gae(rewards: Tensor, values: Tensor, dones: Tensor, last_values: Tensor,
                gamma: float = 0.99, gae_lambda: float = 0.95) -> tuple[Tensor, Tensor]:
    """Return UNNORMALIZED advantages and returns; rewards already include timeout fix."""
    if rewards.ndim != 2 or rewards.shape != values.shape or rewards.shape != dones.shape:
        raise ValueError("GAE expects rewards/values/dones with equal [T, N] shapes")
    if last_values.shape != (rewards.shape[1],):
        raise ValueError("last_values must have shape [N]")
    advantages = torch.zeros_like(rewards)
    tail = torch.zeros_like(last_values)
    for step in reversed(range(rewards.shape[0])):
        next_value = last_values if step == rewards.shape[0] - 1 else values[step + 1]
        alive = (~dones[step].bool()).to(values.dtype)
        delta = rewards[step] + gamma * alive * next_value - values[step]
        tail = delta + gamma * gae_lambda * alive * tail
        advantages[step] = tail
    return advantages, advantages + values


class SequencePPO:
    """Torch-only learner. The worker owns simulation, histories, DR and accounting."""
    FORMAT_VERSION = 1

    def __init__(self, config: PPOConfig | None = None, device: str | torch.device = "cpu"):
        self.config = config or PPOConfig()
        cfg = self.config
        if (cfg.obs_dim, cfg.history_length, cfg.privileged_dim, cfg.latent_dim) != (35, 5, 38, 3):
            raise ValueError("This E3 branch requires obs35/history5/priv38/latent3")
        if cfg.actor_hidden != (256, 128, 64) or cfg.critic_hidden != (256, 128, 64):
            raise ValueError("E3 warm-start capacity must remain 256/128/64")
        if cfg.encoder_hidden != (128, 64) or cfg.initial_std <= 0:
            raise ValueError("Expected encoder128/64 and positive initial_std")
        if cfg.action_dim < 1 or cfg.epochs < 1 or cfg.mini_batches < 1:
            raise ValueError("action_dim, epochs and mini_batches must be positive")
        self.device = torch.device(device)
        self.model = SequenceActorCritic(cfg).to(self.device)
        self.main_parameters = list(self.model.actor.parameters()) + list(self.model.critic.parameters()) + [self.model.log_std]
        self.encoder_parameters = list(self.model.encoder.parameters())
        self.main_optimizer = torch.optim.Adam(self.main_parameters, lr=cfg.learning_rate)
        self.encoder_optimizer = torch.optim.Adam(self.encoder_parameters, lr=cfg.encoder_learning_rate)
        self.learning_rate = cfg.learning_rate
        self.generator = torch.Generator(device=self.device).manual_seed(cfg.seed)
        self.counters = {"updates": 0, "policy_optimizer_steps": 0,
                         "encoder_optimizer_steps": 0, "transitions_seen": 0}
        self.branch_metadata: dict[str, Any] = {
            "kind": "NEW_BRANCH_RANDOM_INIT", "inherited_optimizer": False,
            "inherited_iteration": False, "native_training_evidence": False,
        }

    def _tensor(self, item: Tensor, shape: tuple[int, ...], name: str,
                *, boolean: bool = False, clone: bool = False) -> Tensor:
        if not isinstance(item, Tensor) or tuple(item.shape) != shape:
            raise ValueError(f"{name} must be a Tensor of shape {shape}")
        if boolean and item.dtype != torch.bool:
            raise ValueError(f"{name} must be bool; no implicit nonzero-to-done conversion")
        result = item.detach().to(device=self.device, dtype=torch.bool if boolean else torch.float32)
        if not boolean and not bool(torch.isfinite(result).all()):
            raise FloatingPointError(f"Non-finite input: {name}")
        return result.clone() if clone else result

    def _inputs(self, obs: Tensor, history: Tensor, privileged_obs: Tensor | None = None):
        if not isinstance(obs, Tensor) or obs.ndim != 2:
            raise ValueError("obs must have shape [N, 35]")
        rows = obs.shape[0]
        obs = self._tensor(obs, (rows, self.config.obs_dim), "obs")
        history = self._tensor(history, (rows, self.config.history_dim), "history")
        if privileged_obs is None:
            return obs, history
        privileged_obs = self._tensor(privileged_obs, (rows, self.config.privileged_dim), "privileged_obs")
        return obs, history, privileged_obs

    @torch.no_grad()
    def act(self, obs: Tensor, history: Tensor, privileged_obs: Tensor,
            deterministic: bool = False) -> dict[str, Tensor]:
        """Collect-time outputs [N,...]; store latent, values, log_prob, mu and sigma."""
        obs, history, privileged_obs = self._inputs(obs, history, privileged_obs)
        distribution, latent = self.model.distribution(obs, history)
        actions = distribution.mean if deterministic else distribution.mean + distribution.stddev * torch.randn(
            distribution.mean.shape, device=self.device, generator=self.generator)
        values = self.model.value(privileged_obs, latent)
        return {"actions": actions.clone(), "values": values.clone(),
                "log_prob": distribution.log_prob(actions).sum(-1).clone(),
                "mu": distribution.mean.clone(), "sigma": distribution.stddev.clone(),
                "latent": latent.clone()}

    @torch.no_grad()
    def value(self, privileged_obs: Tensor, *, stored_latent: Tensor | None = None,
              history: Tensor | None = None) -> Tensor:
        """Provide exactly one of stored_latent or history (history for rollout tail)."""
        if (stored_latent is None) == (history is None):
            raise ValueError("Provide exactly one of stored_latent or history")
        rows = privileged_obs.shape[0]
        privileged_obs = self._tensor(privileged_obs, (rows, self.config.privileged_dim), "privileged_obs")
        if history is not None:
            history = self._tensor(history, (rows, self.config.history_dim), "history")
            stored_latent = self.model.encoder(history)
        else:
            stored_latent = self._tensor(stored_latent, (rows, self.config.latent_dim), "stored_latent")
        return self.model.value(privileged_obs, stored_latent).clone()

    def evaluate(self, obs: Tensor, history: Tensor, privileged_obs: Tensor,
                 stored_latent: Tensor, actions: Tensor) -> dict[str, Tensor]:
        """Gradient-enabled actor/critic evaluation; no encoder gradients in this path."""
        obs, history, privileged_obs = self._inputs(obs, history, privileged_obs)
        rows = obs.shape[0]
        stored_latent = self._tensor(stored_latent, (rows, self.config.latent_dim), "stored_latent")
        actions = self._tensor(actions, (rows, self.config.action_dim), "actions")
        distribution, _ = self.model.distribution(obs, history)
        return {"log_prob": distribution.log_prob(actions).sum(-1),
                "entropy": distribution.entropy().sum(-1),
                "values": self.model.value(privileged_obs, stored_latent),
                "mu": distribution.mean, "sigma": distribution.stddev}

    def encoder_loss(self, history: Tensor, body_velocity: Tensor) -> Tensor:
        """Only encoder gradients; physical body-frame m/s target is scaled ONCE by 3."""
        rows = history.shape[0]
        history = self._tensor(history, (rows, self.config.history_dim), "history")
        body_velocity = self._tensor(body_velocity, (rows, 3), "body_velocity")
        target = body_velocity * self.config.body_velocity_scale
        return (self.model.encoder(history) - target).square().mean()

    def warm_start(self, actor_state: Mapping[str, Tensor],
                   critic_state: Mapping[str, Tensor]) -> dict[str, Any]:
        """Copy complete legacy mlp.0/2/4/6.* weights; never import old Adam/counters.

        Source dimensions are 35 for actor and 38 for critic. New latent columns
        are zero. Validate BOTH whole networks before changing either network.
        """
        if any(self.counters.values()) or self.main_optimizer.state or self.encoder_optimizer.state:
            raise RuntimeError("warm_start is only valid before this branch has optimizer steps")
        expected = {f"mlp.{index}.{suffix}" for index in (0, 2, 4, 6) for suffix in ("weight", "bias")}
        validated: list[tuple[nn.Module, dict[str, Tensor], int]] = []
        for label, source, target, old_width in (
            ("actor", actor_state, self.model.actor, self.config.obs_dim),
            ("critic", critic_state, self.model.critic, self.config.privileged_dim),
        ):
            if set(source) != expected:
                raise ValueError(f"{label}: require exactly the complete legacy mlp.0/2/4/6.* state")
            copied: dict[str, Tensor] = {}
            for key, destination in target.state_dict().items():
                desired_shape = list(destination.shape)
                if key == "mlp.0.weight":
                    desired_shape[1] = old_width
                item = source[key]
                if not isinstance(item, Tensor) or list(item.shape) != desired_shape:
                    raise ValueError(f"{label}.{key}: expected legacy shape {desired_shape}")
                if not item.is_floating_point() or not bool(torch.isfinite(item).all()):
                    raise FloatingPointError(f"{label}.{key}: require finite floating-point weights")
                copied[key] = item.detach().to(device=self.device, dtype=destination.dtype).clone()
            validated.append((target, copied, old_width))
        with torch.no_grad():
            for target, source, old_width in validated:
                for key, destination in target.state_dict().items():
                    if key == "mlp.0.weight":
                        destination.zero_()
                        destination[:, :old_width].copy_(source[key])
                    else:
                        destination.copy_(source[key])
            self.model.log_std.fill_(math.log(self.config.initial_std))
        self.branch_metadata = {
            "kind": "NEW_BRANCH_WARM_START", "inherited_optimizer": False,
            "inherited_iteration": False, "native_training_evidence": False,
            "legacy_actor_input": 35, "legacy_critic_input": 38,
            "latent_columns_zero_initialized": True,
            "std_parameterization": "new learnable log_std; not copied from legacy",
        }
        return {"branch_metadata": clone_tree(self.branch_metadata), "counters": dict(self.counters)}

    def prepare_rollout(self, rollout: Mapping[str, Tensor], last_values: Tensor) -> dict[str, Tensor]:
        """Validate/copy [T,N,...] rollout; flatten only AFTER full-rollout GAE.

        Required keys: obs, history, privileged_obs, body_velocity, latent,
        actions, rewards, dones(bool), time_outs(bool), values, log_prob, mu,
        sigma. Scalar fields are [T,N], vector fields [T,N,D]. rewards are
        UNADJUSTED; body_velocity is physical m/s, not an already-scaled target.
        """
        cfg = self.config
        required = {"obs", "history", "privileged_obs", "body_velocity", "latent", "actions",
                    "rewards", "dones", "time_outs", "values", "log_prob", "mu", "sigma"}
        missing = required - set(rollout)
        if missing:
            raise ValueError(f"Missing rollout keys: {sorted(missing)}")
        if not isinstance(rollout["rewards"], Tensor) or rollout["rewards"].ndim != 2:
            raise ValueError("rollout rewards must have shape [T,N]")
        steps, rows = rollout["rewards"].shape
        if steps < 1 or rows < 1 or (steps * rows) % cfg.mini_batches:
            raise ValueError("T*N must be positive and divisible by mini_batches; no samples are dropped")
        widths = {"obs": cfg.obs_dim, "history": cfg.history_dim,
                  "privileged_obs": cfg.privileged_dim, "body_velocity": 3,
                  "latent": cfg.latent_dim, "actions": cfg.action_dim,
                  "mu": cfg.action_dim, "sigma": cfg.action_dim}
        data: dict[str, Tensor] = {}
        for key in required:
            shape = (steps, rows, widths[key]) if key in widths else (steps, rows)
            data[key] = self._tensor(rollout[key], shape, key,
                                     boolean=key in ("dones", "time_outs"), clone=True)
        if bool((data["time_outs"] & ~data["dones"]).any()):
            raise ValueError("time_outs must be a subset of dones")
        if not bool((data["sigma"] > 0).all()):
            raise ValueError("Collection-time sigma must be positive")
        last_values = self._tensor(last_values, (rows,), "last_values", clone=True)
        adjusted = timeout_bootstrap_rewards(data["rewards"], data["values"], data["time_outs"], cfg.gamma)
        raw_advantages, returns = compute_gae(adjusted, data["values"], data["dones"],
                                             last_values, cfg.gamma, cfg.gae_lambda)
        # Match reference torch.std() (sample std), including its 1e-8 denominator.
        std = raw_advantages.std(unbiased=True) if raw_advantages.numel() > 1 else raw_advantages.new_zeros(())
        data["advantages"] = (raw_advantages - raw_advantages.mean()) / (std + 1e-8)
        data["returns"] = returns
        data["adjusted_rewards"] = adjusted
        return {key: item.flatten(0, 1).clone() for key, item in data.items()}

    def _clear_gradients(self) -> None:
        # Local correction: clear both groups; no stale cross-phase gradients.
        self.main_optimizer.zero_grad(set_to_none=True)
        self.encoder_optimizer.zero_grad(set_to_none=True)

    def _checked_step(self, loss: Tensor, optimizer: torch.optim.Optimizer,
                      parameters: list[nn.Parameter], forbidden: list[nn.Parameter],
                      max_norm: float, counter_name: str) -> float:
        if not bool(torch.isfinite(loss)):
            raise FloatingPointError("Non-finite loss before optimizer step")
        loss.backward()
        if any(parameter.grad is not None for parameter in forbidden):
            raise RuntimeError("Gradient leaked into the other optimizer group")
        gradients = [parameter.grad for parameter in parameters if parameter.grad is not None]
        if not gradients or not all(bool(torch.isfinite(gradient).all()) for gradient in gradients):
            raise FloatingPointError("Missing or non-finite gradients")
        # Local correction: clip ONLY this optimizer's parameter group.
        norm = nn.utils.clip_grad_norm_(parameters, max_norm, error_if_nonfinite=True)
        optimizer.step()
        # Count the real step even if the subsequent finite-parameter guard fails.
        self.counters[counter_name] += 1
        if not all(bool(torch.isfinite(parameter).all()) for parameter in parameters):
            raise FloatingPointError("Non-finite parameter after optimizer step")
        return float(norm)

    def update(self, rollout: Mapping[str, Tensor], last_values: Tensor) -> dict[str, Any]:
        """One learner update: all PPO batches, then all supervised encoder batches.

        Counters track REAL successful optimizer.step calls, not simulated/native
        iterations. An exception preserves already-completed step counts.
        """
        data = self.prepare_rollout(rollout, last_values)
        cfg = self.config
        batch_size = data["obs"].shape[0]
        mini_size = batch_size // cfg.mini_batches
        before = {name: parameter.detach().clone() for name, parameter in self.model.named_parameters()}
        main_start = self.counters["policy_optimizer_steps"]
        encoder_start = self.counters["encoder_optimizer_steps"]
        sums = {"value_loss": 0.0, "surrogate_loss": 0.0, "kl": 0.0, "encoder_loss": 0.0}
        main_norm, encoder_norm = 0.0, 0.0
        # Upstream uses one permutation per phase, reused across its epochs.
        indices = torch.randperm(batch_size, generator=self.generator, device=self.device)
        for _ in range(cfg.epochs):
            for mini in range(cfg.mini_batches):
                chosen = indices[mini * mini_size:(mini + 1) * mini_size]
                self._clear_gradients()
                result = self.evaluate(data["obs"][chosen], data["history"][chosen],
                                       data["privileged_obs"][chosen], data["latent"][chosen],
                                       data["actions"][chosen])
                with torch.no_grad():
                    old_mu, old_sigma = data["mu"][chosen], data["sigma"][chosen]
                    mu, sigma = result["mu"], result["sigma"]
                    kl = (torch.log(sigma / old_sigma + 1e-5)
                          + (old_sigma.square() + (old_mu - mu).square()) / (2 * sigma.square()) - 0.5).sum(-1).mean()
                    if not bool(torch.isfinite(kl)):
                        raise FloatingPointError("Non-finite KL")
                    if float(kl) > cfg.desired_kl * 2:
                        self.learning_rate = max(cfg.min_learning_rate, self.learning_rate / 1.5)
                    elif 0 < float(kl) < cfg.desired_kl / 2:
                        self.learning_rate = min(cfg.max_learning_rate, self.learning_rate * 1.5)
                    for group in self.main_optimizer.param_groups:
                        group["lr"] = self.learning_rate
                ratio = (result["log_prob"] - data["log_prob"][chosen]).exp()
                advantages = data["advantages"][chosen]
                surrogate = torch.maximum(-advantages * ratio,
                                          -advantages * ratio.clamp(1 - cfg.clip_param, 1 + cfg.clip_param)).mean()
                old_values = data["values"][chosen]
                value_clipped = old_values + (result["values"] - old_values).clamp(-cfg.clip_param, cfg.clip_param)
                returns = data["returns"][chosen]
                value_loss = torch.maximum((result["values"] - returns).square(),
                                           (value_clipped - returns).square()).mean()
                loss = surrogate + cfg.value_loss_coef * value_loss - cfg.entropy_coef * result["entropy"].mean()
                norm = self._checked_step(loss, self.main_optimizer, self.main_parameters,
                                          self.encoder_parameters, cfg.main_grad_norm,
                                          "policy_optimizer_steps")
                main_norm = max(main_norm, norm)
                sums["value_loss"] += float(value_loss.detach())
                sums["surrogate_loss"] += float(surrogate.detach())
                sums["kl"] += float(kl)
        indices = torch.randperm(batch_size, generator=self.generator, device=self.device)
        for _ in range(cfg.epochs):
            for mini in range(cfg.mini_batches):
                chosen = indices[mini * mini_size:(mini + 1) * mini_size]
                self._clear_gradients()
                loss = self.encoder_loss(data["history"][chosen], data["body_velocity"][chosen])
                norm = self._checked_step(loss, self.encoder_optimizer, self.encoder_parameters,
                                          self.main_parameters, cfg.encoder_grad_norm,
                                          "encoder_optimizer_steps")
                encoder_norm = max(encoder_norm, norm)
                sums["encoder_loss"] += float(loss.detach())
        self._clear_gradients()
        main_steps = self.counters["policy_optimizer_steps"] - main_start
        encoder_steps = self.counters["encoder_optimizer_steps"] - encoder_start
        self.counters["updates"] += 1
        self.counters["transitions_seen"] += batch_size
        delta_sq = {"actor": 0.0, "critic": 0.0, "encoder": 0.0, "log_std": 0.0}
        for name, parameter in self.model.named_parameters():
            group = name.split(".", 1)[0]
            delta_sq[group] += float((parameter.detach() - before[name]).double().square().sum())
        return {
            "value_loss": sums["value_loss"] / main_steps,
            "surrogate_loss": sums["surrogate_loss"] / main_steps,
            "kl": sums["kl"] / main_steps,
            "encoder_loss": sums["encoder_loss"] / encoder_steps,
            "learning_rate": self.learning_rate,
            "main_grad_norm_max_before_clip": main_norm,
            "encoder_grad_norm_max_before_clip": encoder_norm,
            "parameter_delta_l2": {key: math.sqrt(value) for key, value in delta_sq.items()},
            "finite_gradients": True, "gradient_groups_separated": True,
            "policy_optimizer_steps_this_update": main_steps,
            "encoder_optimizer_steps_this_update": encoder_steps,
            "counters": dict(self.counters), "native_training_evidence": False,
        }

    def state_dict(self) -> dict[str, Any]:
        """Complete independent branch state; every tensor leaf is a detached copy."""
        return clone_tree({
            "format_version": self.FORMAT_VERSION, "config": asdict(self.config),
            "model": self.model.state_dict(), "main_optimizer": self.main_optimizer.state_dict(),
            "encoder_optimizer": self.encoder_optimizer.state_dict(),
            "counters": self.counters, "branch_metadata": self.branch_metadata,
            "current_learning_rate": self.learning_rate, "generator_state": self.generator.get_state(),
        })

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        """Resume THIS branch, including both Adam moments/steps and local RNG.

        Loading requires the same config. Caller-owned input state is never mutated
        or retained by alias. This is separate from legacy NEW_BRANCH_WARM_START.
        """
        checkpoint = clone_tree(dict(state))
        if checkpoint["format_version"] != self.FORMAT_VERSION:
            raise ValueError("Unsupported sequence-PPO state format")
        if checkpoint["config"] != asdict(self.config):
            raise ValueError("Checkpoint config does not match this branch")
        expected = {"updates", "policy_optimizer_steps", "encoder_optimizer_steps", "transitions_seen"}
        if set(checkpoint["counters"]) != expected or any(
                not isinstance(item, int) or item < 0 for item in checkpoint["counters"].values()):
            raise ValueError("Invalid optimizer/update counters")
        self.model.load_state_dict(checkpoint["model"], strict=True)
        self.main_optimizer.load_state_dict(checkpoint["main_optimizer"])
        self.encoder_optimizer.load_state_dict(checkpoint["encoder_optimizer"])
        self.learning_rate = float(checkpoint["current_learning_rate"])
        for group in self.main_optimizer.param_groups:
            group["lr"] = self.learning_rate
        self.generator.set_state(checkpoint["generator_state"].cpu())
        self.counters = dict(checkpoint["counters"])
        self.branch_metadata = clone_tree(checkpoint["branch_metadata"])
        self._clear_gradients()

"""One small synthetic CPU functional check, not a native training/evaluation run."""
from __future__ import annotations

import io
import json
import math
from pathlib import Path
import sys
import traceback
from typing import Any

import torch
from torch import Tensor

from fudan_seq_ppo import MLP, PPOConfig, SequencePPO, clone_tree, timeout_bootstrap_rewards


def assert_same_tree(left: Any, right: Any) -> None:
    if isinstance(left, Tensor):
        assert isinstance(right, Tensor) and torch.equal(left, right)
    elif isinstance(left, dict):
        assert isinstance(right, dict) and set(left) == set(right)
        for key in left:
            assert_same_tree(left[key], right[key])
    elif isinstance(left, (list, tuple)):
        assert type(left) is type(right) and len(left) == len(right)
        for first, second in zip(left, right):
            assert_same_tree(first, second)
    else:
        assert left == right


def finite_nonzero_gradient(parameters) -> bool:
    gradients = [parameter.grad for parameter in parameters if parameter.grad is not None]
    return bool(gradients) and all(bool(torch.isfinite(item).all()) for item in gradients) and any(
        bool(item.abs().sum() > 0) for item in gradients)


def run_once() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.manual_seed(20261104)
    cfg = PPOConfig(epochs=2, mini_batches=4, seed=104)
    learner = SequencePPO(cfg, device="cpu")
    # Entirely synthetic legacy models: no real checkpoint is opened.
    old_actor = MLP(35, (256, 128, 64), cfg.action_dim)
    old_critic = MLP(38, (256, 128, 64), 1)
    actor_state, critic_state = old_actor.state_dict(), old_critic.state_dict()
    old_inputs_snapshot = clone_tree({"actor": actor_state, "critic": critic_state})
    receipt = learner.warm_start(actor_state, critic_state)
    assert receipt["branch_metadata"]["kind"] == "NEW_BRANCH_WARM_START"
    assert all(item == 0 for item in receipt["counters"].values())
    assert not learner.main_optimizer.state and not learner.encoder_optimizer.state
    assert torch.count_nonzero(learner.model.actor.mlp[0].weight[:, 35:]) == 0
    assert torch.count_nonzero(learner.model.critic.mlp[0].weight[:, 38:]) == 0
    torch.testing.assert_close(learner.model.log_std.detach(), torch.full((cfg.action_dim,), math.log(0.5)))

    n, t = 8, 8
    obs = torch.randn(t, n, 35) * 0.2
    history = torch.randn(t, n, 175) * 0.2
    history[..., -35:] = obs
    body_velocity = history[..., -35:-32].clone() * 0.15  # synthetic physical m/s
    privileged = torch.cat((3 * body_velocity, obs), dim=-1)
    flat_obs, flat_history, flat_priv = obs.flatten(0, 1), history.flatten(0, 1), privileged.flatten(0, 1)
    deterministic = learner.act(flat_obs, flat_history, flat_priv, deterministic=True)
    with torch.no_grad():
        old_mean = old_actor(flat_obs)
        old_value = old_critic(flat_priv).squeeze(-1)
    torch.testing.assert_close(deterministic["mu"], old_mean, rtol=1e-5, atol=1e-7)
    torch.testing.assert_close(deterministic["values"], old_value, rtol=1e-5, atol=1e-7)
    random_latent = torch.randn(t * n, 3)
    torch.testing.assert_close(learner.value(flat_priv, stored_latent=random_latent), old_value,
                               rtol=1e-5, atol=1e-7)
    mean_error = float((deterministic["mu"] - old_mean).abs().max())
    value_error = float((deterministic["values"] - old_value).abs().max())

    collected = learner.act(flat_obs, flat_history, flat_priv)
    # Explicitly check BOTH gradient directions before doing any optimizer steps.
    learner.main_optimizer.zero_grad(set_to_none=True)
    learner.encoder_optimizer.zero_grad(set_to_none=True)
    evaluated = learner.evaluate(flat_obs, flat_history, flat_priv,
                                 collected["latent"], collected["actions"])
    (evaluated["values"].square().mean() - evaluated["log_prob"].mean()).backward()
    assert finite_nonzero_gradient(learner.main_parameters)
    assert all(parameter.grad is None for parameter in learner.encoder_parameters)
    learner.main_optimizer.zero_grad(set_to_none=True)
    learner.encoder_optimizer.zero_grad(set_to_none=True)
    enc_loss_before = learner.encoder_loss(flat_history, body_velocity.flatten(0, 1))
    enc_loss_before.backward()
    assert finite_nonzero_gradient(learner.encoder_parameters)
    assert all(parameter.grad is None for parameter in learner.main_parameters)
    learner.main_optimizer.zero_grad(set_to_none=True)
    learner.encoder_optimizer.zero_grad(set_to_none=True)

    rollout = {"obs": obs, "history": history, "privileged_obs": privileged,
               "body_velocity": body_velocity,
               "rewards": torch.randn(t, n) * 0.05,
               "dones": torch.zeros(t, n, dtype=torch.bool),
               "time_outs": torch.zeros(t, n, dtype=torch.bool)}
    for name in ("actions", "values", "log_prob", "mu", "sigma", "latent"):
        item = collected[name]
        rollout[name] = item.reshape(t, n, *item.shape[1:])
    rollout["dones"][3, 1] = True
    rollout["dones"][-1, 0] = True
    rollout["time_outs"][-1, 0] = True
    last_values = learner.value(torch.randn(n, 38) * 0.1, history=torch.randn(n, 175) * 0.1)
    rollout_snapshot = clone_tree(rollout)
    last_values_snapshot = last_values.clone()
    prepared = learner.prepare_rollout(rollout, last_values)
    expected_adjusted = timeout_bootstrap_rewards(rollout["rewards"], rollout["values"],
                                                   rollout["time_outs"], cfg.gamma)
    torch.testing.assert_close(prepared["adjusted_rewards"], expected_adjusted.flatten())
    # At timeout, terminal GAE cuts; the only bootstrap is the explicit gamma*V_t addition.
    expected_terminal_return = rollout["rewards"][-1, 0] + cfg.gamma * rollout["values"][-1, 0]
    torch.testing.assert_close(prepared["returns"].reshape(t, n)[-1, 0], expected_terminal_return)
    assert abs(float(prepared["advantages"].mean())) < 1e-6
    assert abs(float(prepared["advantages"].std()) - 1.0) < 1e-5
    assert prepared["obs"].data_ptr() != rollout["obs"].data_ptr()
    first_metrics = learner.update(rollout, last_values)
    assert first_metrics["policy_optimizer_steps_this_update"] == 8
    assert first_metrics["encoder_optimizer_steps_this_update"] == 8
    assert first_metrics["finite_gradients"] and first_metrics["gradient_groups_separated"]
    assert first_metrics["parameter_delta_l2"]["actor"] > 0
    assert first_metrics["parameter_delta_l2"]["critic"] > 0
    assert first_metrics["parameter_delta_l2"]["encoder"] > 0
    assert first_metrics["counters"] == {"updates": 1, "policy_optimizer_steps": 8,
                                         "encoder_optimizer_steps": 8, "transitions_seen": 64}
    with torch.no_grad():
        enc_loss_after = float(learner.encoder_loss(flat_history, body_velocity.flatten(0, 1)))

    checkpoint = learner.state_dict()
    checkpoint_snapshot = clone_tree(checkpoint)
    assert checkpoint["main_optimizer"]["state"] and checkpoint["encoder_optimizer"]["state"]
    assert checkpoint["model"]["actor.mlp.0.weight"].data_ptr() != learner.model.actor.mlp[0].weight.data_ptr()
    # Test serialization in memory ONLY; no .pt file is read or written.
    stream = io.BytesIO()
    torch.save(checkpoint, stream)
    stream.seek(0)
    memory_checkpoint = torch.load(stream, map_location="cpu", weights_only=False)
    restored = SequencePPO(cfg, device="cpu")
    restored.load_state_dict(memory_checkpoint)
    assert_same_tree(checkpoint, restored.state_dict())

    # A synthetic repeated rollout is used ONLY to test continuation equivalence;
    # it is not presented as fresh on-policy/native robot data.
    second_metrics = learner.update(rollout, last_values)
    restored_metrics = restored.update(rollout, last_values)
    assert_same_tree(learner.state_dict(), restored.state_dict())
    assert_same_tree(second_metrics, restored_metrics)
    assert learner.counters == {"updates": 2, "policy_optimizer_steps": 16,
                                "encoder_optimizer_steps": 16, "transitions_seen": 128}
    # Caller inputs, warm-start states and returned checkpoints remain untouched.
    assert_same_tree(old_inputs_snapshot, {"actor": actor_state, "critic": critic_state})
    assert_same_tree(rollout_snapshot, rollout)
    assert_same_tree(last_values_snapshot, last_values)
    assert_same_tree(checkpoint_snapshot, checkpoint)
    assert_same_tree(checkpoint_snapshot, memory_checkpoint)
    return {
        "status": "PASS", "scope": "ONE_SYNTHETIC_CPU_FUNCTIONAL_CHECK",
        "native_training_evidence": False, "actual_checkpoint_read": False,
        "torch_version": str(torch.__version__), "device": "cpu", "N": n, "T": t,
        "epochs": cfg.epochs, "mini_batches": cfg.mini_batches,
        "warm_start_mean_max_abs_error": mean_error,
        "warm_start_value_max_abs_error": value_error,
        "warm_start_zero_latent_columns": True,
        "separate_gradient_paths": True, "timeout_current_Vt_and_done_cut": True,
        "encoder_loss_before": float(enc_loss_before.detach()), "encoder_loss_after": enc_loss_after,
        "first_update": first_metrics,
        "continuation_state_exact_equal": True, "both_adam_states_restored": True,
        "local_generator_restored": True, "inputs_and_checkpoints_unmodified": True,
        "primary_instance_counters": dict(learner.counters),
        "restored_instance_counters": dict(restored.counters),
        "optimizer_steps_across_all_test_instances": {"policy": 24, "encoder": 24},
        "note": "Two updates on primary and one on restored learner; synthetic CPU counts only.",
    }


if __name__ == "__main__":
    output = Path(__file__).with_name("cpu_functional_result.json")
    try:
        result = run_once()
        exit_code = 0
    except Exception as error:
        result = {"status": "FAIL", "scope": "ONE_SYNTHETIC_CPU_FUNCTIONAL_CHECK",
                  "native_training_evidence": False, "error": repr(error),
                  "traceback": traceback.format_exc()}
        exit_code = 1
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    sys.exit(exit_code)

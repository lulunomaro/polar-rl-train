"""One N80 synthetic adapter test; no simulator, real checkpoint, GPU or PPO update."""
from __future__ import annotations

import json
import sys
import traceback
from collections import OrderedDict
from dataclasses import asdict
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "source_fudan_seq_ppo_v1"))
import fudan_seq_ppo as core
import frozen_sequence_mean as adapter


class NeverRestore:
    """Opaque N4096-training-state sentinel: any use as evaluator state is a bug."""
    def __getitem__(self, key):
        raise AssertionError("Training environment/DR/history must not be read, sliced or restored")

    def __getattr__(self, name):
        raise AssertionError("Training environment/DR/history must not be materialized")


def expect_error(function, error_type):
    try:
        function()
    except error_type:
        return True
    raise AssertionError(f"Expected {error_type.__name__}")


def synthetic_checkpoint():
    config = core.PPOConfig(seed=7307)
    # This CPU-only full core NETWORK is the independent reference, not a learner.
    # It is constructed before strict load below; no Adam or SequencePPO is built.
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(7307)
        weights_source = core.SequenceActorCritic(config).cpu()
        with torch.no_grad():
            weights_source.actor.mlp[6].bias.copy_(torch.linspace(-7.5, 7.5, 6))
        model_state = OrderedDict((name, value.detach().clone())
                                  for name, value in weights_source.state_dict().items())
    learner = OrderedDict(
        format_version=1, config=asdict(config), model=model_state,
        main_optimizer=dict(state={}, param_groups=[dict(params=[])]),
        encoder_optimizer=dict(state={}, param_groups=[dict(params=[])]),
        counters=dict(updates=0, policy_optimizer_steps=0, encoder_optimizer_steps=0, transitions_seen=0),
        branch_metadata=dict(kind="NEW_BRANCH_WARM_START", inherited_optimizer=False, inherited_iteration=False),
        current_learning_rate=1e-3, generator_state=torch.Generator().manual_seed(440).get_state(),
    )
    never = NeverRestore()
    environment = {key: never for key in (
        "root_state_w", "joint_pos", "joint_vel", "body_names", "joint_names", "actual_observations",
        "history_old_to_new", "recovery", "command_tensors", "command_named_rng_states",
        "environment_tensor_caches", "episode_length_buf", "common_step_counter", "sim_step_counter",
        "feedback_100hz_tick", "action_manager_action", "action_manager_prev_action", "task_stage_summary")}
    environment["D0_D7"] = {key: never for key in (
        "_sensor_mild", "_feedback_delay_mild", "_physics_action_delay", "_spring_pressure", "_gas_damping",
        "_chassis_com", "_explicit_pd", "_mild_dr", "integrated_contact",
        "adapter_baselines_and_dynamic_caches", "actuator_coefficients")}
    environment["native_PhysX_bitwise_exact_resume"] = False
    environment["opaque_SDK_scene_and_warp_alias_references_serialized"] = False
    source = OrderedDict(source_path=adapter.MOTHER_PATH, source_sha256=adapter.MOTHER_SHA,
                         source_bytes=adapter.MOTHER_BYTES, source_iter=adapter.MOTHER_ITER,
                         physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1,
                         whole_source_root_and_bytes_retained=True, source_tensor_versions_unchanged=True,
                         actor_critic_MLP_only=True, ignored_old_exploration_keys=[],
                         source_optimizer_and_DR_state_not_restored=True, old_iteration_not_inherited=True)
    checkpoint = OrderedDict(
        kind=adapter.KIND, version=1, epoch=0.0, reason="synthetic_cpu_only",
        resource_binding=OrderedDict(run="SYNTHETIC_CPU_ONLY_NOT_NATIVE"),
        branch_kind="NEW_SEQUENCE_PPO_ACTOR_CRITIC_WARM_START", inherited_old_iterations=0,
        source_checkpoint=source, learner=learner,
        global_rng={key: never for key in ("python", "numpy", "torch_cpu", "torch_cuda_all")},
        environment=environment, pending_rollout={},
        native_counters=dict(actual_native_policy_steps=0, actual_native_transitions=0,
                             physical_callbacks=0, feedback_callbacks=0, termination_computations=0),
        save_is_typed_fullstate_not_native_PhysX_bitwise_resume=True,
        fullstate_required_components_complete=True, skill_improvement_claim=False,
    )
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(991)
        reference = core.SequenceActorCritic(config).cpu()  # construct FIRST
        reference.load_state_dict(model_state, strict=True)  # THEN load same weights
        reference.requires_grad_(False).eval()
    return checkpoint, reference


def run():
    torch.set_num_threads(1)
    root, reference = synthetic_checkpoint()
    source_model = root["learner"]["model"]
    before = {key: value.clone() for key, value in source_model.items()}
    versions = {key: value._version for key, value in source_model.items()}
    result = dict(
        purpose="single_new_frozen_adapter_functionality_test", synthetic_only=True,
        real_checkpoint_read=False, real_checkpoint_file_written=False, SDK_imported=False,
        GPU_used=False, native_evaluation=False, MuJoCo_evaluation=False,
        old_core_test_rerun=False, PPO_updates_executed=0, Adam_objects_constructed=0,
        num_envs=80, steps=9, torch_version=torch.__version__, device="cpu",
    )
    # Ordinary evaluation must reject this explicitly zero-native synthetic fixture.
    result["zero_native_default_rejected"] = expect_error(
        lambda: adapter.validate_checkpoint_provenance(root), ValueError)
    rng_before = torch.get_rng_state().clone()
    policy = adapter.FrozenSequenceMean(root, device="cpu", require_native_updates=False,
                                        expected_run="SYNTHETIC_CPU_ONLY_NOT_NATIVE")
    result["constructor_preserved_CPU_global_RNG"] = torch.equal(rng_before, torch.get_rng_state())
    assert result["constructor_preserved_CPU_global_RNG"]
    assert set(policy._network.state_dict()) == set(adapter.PI_SHAPES)
    assert not hasattr(policy._network, "critic") and not hasattr(policy._network, "log_std")
    assert not hasattr(policy, "main_optimizer") and not hasattr(policy, "encoder_optimizer")
    assert all(not p.requires_grad and p.grad is None for p in policy._network.parameters())
    assert all(not module.training for module in policy._network.modules())
    for key, value in policy._network.state_dict().items():
        assert torch.equal(value, source_model[key])
        assert value.data_ptr() != source_model[key].data_ptr()
    result["strict_loaded_all_14_selected_tensors"] = True
    result["runtime_parameter_tensor_count"] = len(list(policy._network.parameters()))
    result["runtime_parameter_numel"] = sum(p.numel() for p in policy._network.parameters())
    result["no_critic_logstd_Adam_or_training_learner_in_adapter"] = True

    missing_root = OrderedDict(root)
    missing_root["learner"] = OrderedDict(root["learner"])
    missing_root["learner"]["model"] = OrderedDict(source_model)
    del missing_root["learner"]["model"]["encoder.mlp.4.bias"]
    result["missing_encoder_key_rejected_not_random_fallback"] = expect_error(
        lambda: adapter.FrozenSequenceMean(missing_root, require_native_updates=False), ValueError)

    generator = torch.Generator().manual_seed(4381)
    first = torch.randn(80, 35, generator=generator)
    history = first[:, None, :].repeat(1, 5, 1)
    with torch.inference_mode():
        policy.initialize(first)
    first.fill_(999.0)  # caller owns this tensor; internal history must be a copy
    assert torch.equal(policy.history_snapshot(), history)
    result["first_sample_repeated_and_input_unaliased"] = True
    mean_errors, reset_counts, clipped_counts = [], [], []
    duplicate_act_guard = duplicate_observe_guard = False
    for step in range(9):
        assert torch.equal(policy.history_snapshot(), history)
        with torch.no_grad():
            distribution, _ = reference.distribution(history[:, -1, :], history.reshape(80, 175))
            expected = distribution.mean.clamp(-6.0, 6.0)
        with torch.inference_mode():
            action = policy.act()
        assert torch.equal(action, expected), "Adapter/core deterministic clipped means diverged"
        mean_errors.append(float((action - expected).abs().max()))
        clipped_counts.append(int((action.abs() == 6).sum()))
        assert action.shape == (80, 6) and not action.requires_grad and bool((action.abs() <= 6).all())
        if step == 0:
            duplicate_act_guard = expect_error(policy.act, RuntimeError)
        action.fill_(0.0)  # output is not an alias to the history or model
        returned = torch.randn(80, 35, generator=generator) + step * .03
        done = torch.arange(80).remainder(step + 3).eq(1)
        if step == 4:
            done.fill_(True)
        reset_counts.append(int(done.sum()))
        previous = history.clone()
        history = torch.cat((history[:, 1:, :], returned[:, None, :]), dim=1)
        history[done] = returned[done, None, :].expand(-1, 5, -1)
        with torch.inference_mode():
            policy.observe(returned, done)
        assert torch.equal(policy.history_snapshot(), history)
        assert torch.equal(history[done], returned[done, None, :].expand(-1, 5, -1))
        assert torch.equal(history[~done, :-1], previous[~done, 1:])
        if step == 0:
            duplicate_observe_guard = expect_error(lambda: policy.observe(returned, done), RuntimeError)
        returned.add_(777.0)  # no alias to new actual sample either
        done.logical_not_()
        assert torch.equal(policy.history_snapshot(), history)
        public_copy = policy.history_snapshot()
        public_copy.zero_()
        assert torch.equal(policy.history_snapshot(), history)
    result["core_deterministic_clipped_mean_max_abs_error_by_step"] = mean_errors
    result["all_steps_exact_match"] = all(error == 0.0 for error in mean_errors)
    result["done_counts_by_step"] = reset_counts
    result["saturated_action_elements_by_step"] = clipped_counts
    result["mixed_reset_history_exact_each_step"] = True
    result["public_snapshots_and_returned_obs_unaliased"] = True
    result["duplicate_act_guard"] = duplicate_act_guard
    result["duplicate_observe_guard"] = duplicate_observe_guard
    assert sum(clipped_counts) > 0 and duplicate_act_guard and duplicate_observe_guard
    snapshot = policy.weights_snapshot()
    next(iter(snapshot.values())).add_(100.0)
    policy.assert_immutable(deep=True)
    result["weights_unchanged_after_inference_and_public_snapshot_mutation"] = True
    result["policy_receipt_before_deliberate_guard_probes"] = policy.receipt()
    assert policy.receipt()["actions_issued"] == 9
    assert policy.receipt()["returned_observations_accepted"] == 9

    # Two focused destructive guard probes, never used for an action afterwards.
    guard_policy = adapter.FrozenSequenceMean(root, require_native_updates=False)
    parameter = next(guard_policy._network.parameters())
    parameter.data.add_(.125)  # deliberately bypass Torch's normal version counter
    guard_policy.assert_immutable()  # cheap version guard does not claim to hash all values
    result["deep_weight_SHA_catches_data_bypass"] = expect_error(
        lambda: guard_policy.assert_immutable(deep=True), RuntimeError)
    with torch.no_grad():
        parameter.add_(.125)
    result["normal_weight_version_guard"] = expect_error(guard_policy.assert_immutable, RuntimeError)
    policy._history.data[0, 0, 0] += 1.0
    result["exact_history_guard_catches_data_bypass"] = expect_error(policy.assert_immutable, RuntimeError)
    assert all(torch.equal(value, before[key]) and value._version == versions[key]
               for key, value in source_model.items())
    result["caller_CPU_model_unchanged_no_weight_alias"] = True
    result["training_DR_history_RNG_sentinels_never_read_or_restored"] = True
    result["independent_native_N80_and_31body_MuJoCo_acceptance_still_required"] = True
    result["status"] = "PASS"
    return result


def main():
    output = HERE / "CPU_RESULT.json"
    if output.exists():
        raise RuntimeError("This one-run synthetic test already has a result; preserve it")
    try:
        result = run()
    except BaseException as exc:
        result = dict(status="FAIL", synthetic_only=True, error=repr(exc), traceback=traceback.format_exc(),
                      real_checkpoint_read=False, GPU_used=False, native_evaluation=False)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))
        raise
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

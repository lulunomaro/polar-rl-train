"""Original E3 N80/160/20260928, fresh full DR, frozen FDN actor+encoder only.

Derived from worker_five_original_n80.py's E3 path; no lowrise26/8s task patch,
PoseV4, teacher reopening, learning, parent launch or resource acquisition.
"""
from pathlib import Path
import json
import os
import runpy
import sys
import time
import traceback

from fudan_frozen_eval_safe import (KIND, INTERFACE, WholeFDNCheckpointCache,
    task_args, put, wait_start, close_original_resources)
from launch_storage_contract import parent_five_storage
from n80_gpu_capacity import capacity_ctor


def main():
    task, out, group = task_args()
    role = task["role"]
    B = Path(task["runtime_root"])
    mod = B / "runtime/isaac/mod4"
    namespace = env = cache = policy = oldterm = None
    execution_error = None
    started_wall = time.time()
    completed = 0
    max_returned = max_applied = 0.0
    try:
        # Original E3 factory/storage/environment route, not the training worker.
        original = json.loads((B / "original_run_manifest.json").read_bytes())["env"]
        for key in list(os.environ):
            if key.startswith("RM_") or key in ("RANK", "WORLD_SIZE", "LOCAL_RANK", "MASTER_ADDR", "MASTER_PORT"):
                del os.environ[key]
        os.environ.update({key: str(value) for key, value in original.items()
            if key not in ("RM_RESCUE_STOP_FILE", "RM_RESCUE_DEADLINE", "RM_SLOPE_INITIAL_ADMISSION")})
        os.environ.update(RM_MOD4_USD=str(B / "runtime/assets/robot.usd"), RM_KEEP_STD="1",
            RM_PHYSICS_DT_S="0.0025", RM_SOLVER_POS="32", RM_SOLVER_VEL="4",
            MOD4_RESUME_QUEUE_CONTROL_US="20000")
        storage = parent_five_storage(B, out)
        storage.mkdir()
        (storage / "data").mkdir()
        (storage / "DerivedDataCache").mkdir()
        (storage / "data/user.config.json").write_text("{}")
        os.environ["WP_CACHE_DIR"] = str(out / "warp_cache")
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        os.environ.update(MOD4V1_E3_ASSET_DIR=str(B / "runtime/assets"), MOD4V1_E3_JOB_ROOT=str(B),
            MOD4V1_E3_KIT_STORAGE_ROOT=str(storage), OWN_E2_H1_KIND="E3_PUBLIC_RECOVERY",
            RM_SPAWN_GRACE_STEPS="5", RM_JUMP_SCRIPT_PROB="0", RM_MOD4_MAP="", RM_MOD4_TERRAIN="flat")
        entry = mod / "train_mod4v1_e3.py"
        sys.path[:0] = [str(Path(__file__).resolve().parent), str(B / "lib"), str(mod),
                        str(B / "runtime"), str(B), str(out)]
        assert os.environ.get("CUDA_VISIBLE_DEVICES") == task["GPU_UUID"]
        from mod4v1_fresh_dr_guard import FreshDRNominalGuard
        sys.argv = [str(entry), "--headless", "--device", "cuda:0", "--num_envs", "80",
                    "--seed", "20260928", "--dry_run", "160"]
        import torch
        cache = WholeFDNCheckpointCache(torch, task)

        def no_other_checkpoint(*args, **kwargs):
            raise RuntimeError("Only the already cached selected new FDN save is permitted; no mother/other PT")
        torch.load = no_other_checkpoint
        namespace = runpy.run_path(str(entry), run_name="fudan_frozen_original_E3_build_no_main")
        factory = namespace["build_env"]
        factory.__globals__["Mod4Env"] = capacity_ctor(factory.__globals__["Mod4Env"])
        env = factory()
        identity = namespace["E3_IDENTITY"]
        from mild_dr import tensor
        from actual_DR_memory_getter272 import RuntimeOrderBinding, ActualDRMemoryGetter
        robot = env.scene["robot"]
        guard = FreshDRNominalGuard(env, identity, torch_module=torch, tensor_converter=tensor)
        guard.assert_new_nominals_unchanged()
        env.reset()  # same sole explicit fresh reset as original E3 N80
        env.e3_reset_enabled = True
        env.place_declared_fall(torch.arange(80, device=env.device))
        env.publish()
        assert set(env.recovery.recipe.tolist()) == set(range(13))
        assert type(env.recovery).__module__ == "e3_public_recovery_phase_v1"
        assert torch.equal(env.recovery.recipe, torch.arange(80, device=env.device) % 13)
        guard.assert_new_nominals_unchanged()
        audit = env._mild_dr.audit()
        assert audit["actual_parameters_pass"]
        assert env.num_envs == 80 and env.step_dt == .02 and env.physics_dt == .0025 and env.cfg.decimation == 8
        assert env.cfg.terminations.closure.params["threshold"] == .01
        assert env.cfg.terminations.mimic.params["threshold"] == .01
        assert identity.usd_sha256 == task["asset_SHA"] and identity.contract_sha256 == task["contract_SHA"]

        def names(key):
            ids = robot.actuators[key].joint_indices
            if isinstance(ids, slice):
                ids = list(range(len(robot.joint_names)))[ids]
            elif hasattr(ids, "tolist"):
                ids = ids.tolist()
            return tuple(robot.joint_names[index] for index in ids)
        binding = RuntimeOrderBinding(tuple(robot.body_names), tuple(robot.joint_names), names("legs"),
            names("wheels"), names("gas_springs"), int(env._mild_dr.materials.shape[1]))
        getter = ActualDRMemoryGetter(env, binding)
        getter.capture_initial()

        def small(value):
            value = value.detach()
            return dict(shape=list(value.shape), dtype=str(value.dtype), finite=bool(torch.isfinite(value).all()),
                        min=float(value.min()), max=float(value.max()), first8=value.reshape(-1)[:8].cpu().tolist())
        memory = {key: small(value) for key, value in getter.cache.items()}
        obs = env.observation_manager.compute()  # ORIGINAL one first sample, no extra/noise resampling
        guard.check_observations(obs)
        policy = cache.policy(env.device)
        policy.initialize(obs["policy"])
        ready = dict(kind=KIND, resource_only_GPU_capacity=env._n80_allocation_only_capacity,
            source_cache=cache.receipt(), policy_receipt=policy.receipt(), D0_D7_fresh_audit=audit,
            actual_component_memory_not_independentbackend=memory, num_envs=80,
            observations={key: list(value.shape) for key, value in obs.items()},
            new_nominal_guard_passed=True, one_explicit_fresh_reset=True,
            scope="Original13 E3 bank; first74 recovery+6normal; new N4096 training state CPU-cache-only",
            controls=160, seed=20260928, interface=dict(raw_policy=35, fresh_noisy_history_frames=5,
                encoder_input=175, latent=3, actor_input=38, critic_observation_logged_only=38, actions=6),
            policy_interface=INTERFACE, physics_dt=.0025, policy_dt=.02, feedback_Hz=100,
            original_recovery_requests=74, normal_envs_excluded_from_recovery_denominator=6,
            new_lowrise_8second_task_enabled=False)
        put(out / "FRESH80_FULLDR_BEFORE_CONTROL.json", ready)
        reasons = {key: 0 for key in env.termination_manager.active_terms}
        terminated_env = torch.zeros(80, dtype=torch.bool, device=env.device)
        truncated_env = terminated_env.clone()
        first_episode_live = ~terminated_env
        episode_events = torch.zeros(80, dtype=torch.long, device=env.device)
        integrated_body_error = torch.zeros(80, 3, device=env.device)
        root_initial = tensor(robot.data.root_pos_w).clone()
        root_last = root_initial.clone()
        reward_sum = torch.zeros(80, device=env.device)
        original_old_closure_boundary = terminated_env.clone()
        current_closure_max = current_mimic_max = 0.0
        command_before = None
        first_recipe = env.recovery.recipe.clone()
        first_credit = terminated_env.clone()
        first_term = terminated_env.clone()
        oldterm = env.termination_manager.compute

        def terminal(*args, **kwargs):
            nonlocal root_last, current_closure_max, current_mimic_max
            value = oldterm(*args, **kwargs)
            tm = env.termination_manager
            ter, tru = tm.terminated.clone(), tm.time_outs.clone()
            terminated_env.logical_or_(ter)
            truncated_env.logical_or_(tru)
            episode_events.add_((ter | tru).long())
            root_last = tensor(robot.data.root_pos_w).clone()
            for name in reasons:
                reasons[name] += int(tm.get_term(name).sum())
            if command_before is not None:
                velocity = tensor(robot.data.root_lin_vel_b)
                yaw = tensor(robot.data.root_ang_vel_b)[:, 2]
                integrated_body_error.add_(torch.stack((velocity[:, 0] - command_before[:, 0],
                    velocity[:, 1] - command_before[:, 1], yaw - command_before[:, 2]), 1).abs() * .02)
            closure, mimic = getattr(env, "_mod4_closure_now", None), getattr(env, "_mod4_mimic_now", None)
            if closure is not None:
                current_closure_max = max(current_closure_max, float(closure.max()))
                original_old_closure_boundary.logical_or_(closure > .002)
            if mimic is not None:
                current_mimic_max = max(current_mimic_max, float(mimic.max()))
            # EXACT original pre-reset first-episode observer; normal excluded below.
            first_credit.logical_or_(env.recovery.credited & first_episode_live)
            first_term.logical_or_(ter & first_episode_live)
            first_episode_live.logical_and_(~(ter | tru))
            return value
        env.termination_manager.compute = terminal
        ready["torch_reserved_bytes_before_empty_cache"] = torch.cuda.memory_reserved()
        torch.cuda.empty_cache()
        ready["torch_reserved_bytes_after_empty_cache"] = torch.cuda.memory_reserved()
        ready["allocation_only_empty_cache_no_live_tensor_or_RNG_change"] = True
        wait_start(task, out, group, ready)
        tick = int(env._integrated_contact.tick)
        feedback_tick = int(env._feedback_100hz_tick)
        delay = dict(env._physics_action_delay.calls)
        eval_started = time.time()
        with torch.inference_mode():
            for index in range(160):
                if time.time() >= task["absolute_worker_deadline_epoch"]:
                    raise TimeoutError("Original bounded worker deadline")
                if (group / "GROUP_ABORT.json").exists():
                    raise RuntimeError("Own single-E3 evaluation group aborted")
                command_before = tensor(env.command_manager.get_term("twist").command).clone()
                action = policy.act()
                assert action.shape == (80, 6) and torch.isfinite(action).all()
                max_returned = max(max_returned, float(action.abs().max()))
                applied = action.clamp(-6.0, 6.0)  # original physical control clip is retained
                max_applied = max(max_applied, float(applied.abs().max()))
                obs, reward, ter, tru, extra = env.step(applied)
                completed += 1
                reward_sum.add_(reward)
                assert obs["policy"].shape == (80, 35) and obs["critic"].shape == (80, 38)
                assert all(bool(torch.isfinite(value).all()) for value in (obs["policy"], obs["critic"], reward))
                policy.observe(obs["policy"], ter | tru)  # SAME returned noisy frames; no new observation call
        physics = int(env._integrated_contact.tick) - tick
        feedback = int(env._feedback_100hz_tick) - feedback_tick
        actual_delay = {key: env._physics_action_delay.calls[key] - delay[key] for key in ("legs", "wheels")}
        assert completed == 160 and physics == 8 * completed and feedback == 2 * completed
        assert actual_delay == {"legs": 8 * completed, "wheels": 8 * completed}
        cache.check_policy(policy)
        policy_receipt = policy.receipt()
        assert policy_receipt["actions_issued"] == policy_receipt["returned_observations_accepted"] == 160
        assert not policy_receipt["awaiting_env_step_result"]
        guard.assert_new_nominals_unchanged()
        after = env._mild_dr.audit()
        assert after["actual_parameters_pass"]
        rows = []
        for recipe in range(13):
            mask = first_recipe == recipe
            rows.append(dict(recipe=recipe, initial_envs=int(mask.sum()), original_request=recipe != 12,
                first_episode_original_stable_credit=int((mask & first_credit).sum()),
                first_episode_physical_terminated=int((mask & first_term).sum())))
        requested = first_recipe != 12
        assert int(requested.sum()) == 74 and int((~requested).sum()) == 6
        skill = dict(original_aggregate_graduation_rule="NONE_IN_JOINED_SOURCE_NO_NEW_PASS_RATE",
            full_expert_graduated=False, new_N80_fresh_cohort_not_original_N20k_cohort=True,
            source_training_cohort_N4096_not_restored=True,
            body_velocity_absolute_error_time_integral_per_env=integrated_body_error.cpu().tolist(),
            root_before_and_last_terminal_world_xyz_per_env=dict(before=root_initial.cpu().tolist(), last=root_last.cpu().tolist()),
            no_cross_reset_endpoint_displacement_success_claim=True, original_recovery_recipe_rows=rows,
            stable50_public100Hz_age_equals_seconds=.5, stable50_equals_policy_controls=25,
            request300_age_seconds=3.0, no_reset_stitched_credit=True,
            original_recovery_request_denominator=74, normal_envs_excluded=6,
            original_first_episode_recovery_credits=int((requested & first_credit).sum()),
            new_lowrise_8second_task_evaluated=False)
        result = dict(kind=KIND, group_id=task["group_id"], role="E3", GPU_UUID=task["GPU_UUID"],
            worker_pid=os.getpid(), parent_pid=os.getppid(), task_sha256=task["_task_sha256"],
            passed_execution=True, num_envs=80, controls=completed, seconds=.02 * completed,
            seed=20260928, physics_callbacks=physics, feedback_samples=feedback, delay_calls=actual_delay,
            source_cache=cache.receipt(), policy_receipt=policy_receipt, policy_interface=INTERFACE,
            actor_encoder_weights_before_after_exact=True, cached_full_checkpoint_before_after_exact=True,
            live_critic_optimizer_created=False, live_log_std_created=False, live_SequencePPO_created=False,
            optimizer_updates=0, policy_clip_actions=6.0, original_control_clip_actions=6.0,
            max_raw_action_abs=None, unclipped_actor_linear_max_not_observed=True,
            max_policy_return_action_abs=max_returned, max_applied_action_abs=max_applied,
            source_saved_training_DR_history_applied=False, source_N4096_DR_history_sliced=False,
            D0_D7_fresh_audit_before=audit, D0_D7_fresh_audit_after=after,
            termination_events_by_reason=reasons, unique_envs_terminated=int(terminated_env.sum()),
            unique_envs_truncated=int(truncated_env.sum()), episode_end_events=int(episode_events.sum()),
            reward_sum_per_env=reward_sum.cpu().tolist(), max_current_closure_m=current_closure_max,
            max_current_mimic_rad=current_mimic_max, old002_closure_prefix_hit_envs=int(original_old_closure_boundary.sum()),
            skill=skill, first_eval_epoch=eval_started, last_eval_epoch=time.time(),
            wall_seconds=time.time() - started_wall, canonical_access=False, new_PPO_or_BPTT=False,
            asset_SHA=task["asset_SHA"], contract_SHA=task["contract_SHA"],
            parent_actual_wait_and_close_evidence_still_required=True,
            independent_31body_MuJoCo_acceptance_proven=False)
        put(out / "FINAL.json", result)
        env.termination_manager.compute = oldterm
    except BaseException:
        execution_error = traceback.format_exc()
        put(out / "WORKER_ERROR.json", dict(role="E3", epoch=time.time(), controls_completed=completed,
            error=execution_error, source_cache=cache.receipt() if cache is not None else None,
            no_retry_samepurpose=True))
        raise
    finally:
        if env is not None and oldterm is not None:
            env.termination_manager.compute = oldterm
        close_original_resources(task, out, env, namespace, cache, execution_error, controls_completed=completed)


if __name__ == "__main__":
    main()

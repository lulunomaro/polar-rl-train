"""E3 full-learner continuation from qualified Root7/55afa, fresh N20000 env.

Derived from the executed v4 continuation worker: only finite25 admission,
Root7/config/lineage/load/save metadata and the fixed a848 training overlay pins
change. Original rollout, physics, optimizer calls, resource/close lifecycle and
audits stay intact. Mother/bad candidates are metadata, never model inputs.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import runpy
import sys
import time
import traceback
from typing import Any, Mapping
from retained_learner_source_v1 import (
    BRANCH_KIND, SOURCE_KIND, INPUT_SCHEMA_VERSION, INPUT_BRANCH_KIND, INPUT_SOURCE_KIND,
    RetainedLearnerSource, validate_source_binding,
)

KIND = "MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1"
TASK_RUNTIME_SHA = "a84823a59731f9cd805aa0bf6a91af10e0e26e729652df39b8cbd17dc6def3f9"
TASK_RUNTIME_BYTES = 12745
ASSET_SHA = "2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3"
CONTRACT_SHA = "bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755"
MOTHER_SHA = "1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8"
MOTHER_BYTES = 14715029
MOTHER_ITER = 43090
MOTHER_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def field(value: Mapping[str, Any], *names: str) -> Any:
    hits = [(name, value[name]) for name in names if name in value]
    need(bool(hits), "Missing field: " + "/".join(names))
    need(all(v == hits[0][1] for _, v in hits), "Conflicting field aliases: " + "/".join(names))
    return hits[0][1]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fsync_directory(path: Path) -> None:
    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def put(path: Path, value: Any) -> str:
    """Atomic, durable JSON.  It never opens a canonical accounting file."""
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + ".partial")
    with temporary.open("wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    fsync_directory(path.parent)
    return sha(raw)


def read_json(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    value = json.loads(raw)
    need(type(value) is dict, "JSON object required: " + str(path))
    return value, sha(raw)


def child_path(root: Path, relative: str) -> Path:
    need(isinstance(relative, str) and bool(relative), "Relative installed path required")
    path = (root / relative).resolve(strict=True)
    need(path.is_relative_to(root) and path.is_file(), "Installed path escaped job root: " + relative)
    return path


def admit(job: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Bind real inherited resources BEFORE SDK construction or checkpoint I/O."""
    task, task_sha = read_json(job / "TASK.json")
    go, go_sha = read_json(job / "GO_PRODUCTION.json")
    ad, ad_sha = read_json(job / "ROOT_ADMISSION_ACTUAL.json")
    manifest, manifest_sha = read_json(job / "INSTALL_MANIFEST.json")
    need(task["kind"] == go["kind"] == KIND, "Wrong worker kind")
    need(task["role"] == go["role"] == ad["role"] == "E3", "E3-only worker")
    run = field(task, "run", "run_id")
    gpu = field(task, "gpu_uuid", "GPU_UUID")
    need(run == field(go, "run", "run_id") == field(ad, "run", "run_id"), "Run binding differs")
    need(gpu == field(go, "gpu_uuid", "GPU_UUID") == field(ad, "gpu_uuid", "GPU_UUID"), "GPU binding differs")
    need(os.environ.get("CUDA_VISIBLE_DEVICES") == gpu, "Actual CUDA UUID differs")
    need(int(task["owner_parent_pid"]) == os.getppid(), "Actual owner parent PID differs")
    for name in ("parent_pid", "owner_parent_pid"):
        if name in ad:
            need(int(ad[name]) == os.getppid(), "Admission parent PID differs")
    need(field(task, "root_admission_sha256", "root_admission_SHA") == ad_sha, "Admission SHA differs")
    need(field(task, "install_manifest_sha256", "manifest_SHA") == manifest_sha, "Manifest SHA differs")
    need(field(go, "task_sha256", "task_SHA") == task_sha, "GO TASK SHA differs")
    for value, names, expected in (
        (go, ("root_admission_sha256", "root_admission_SHA"), ad_sha),
        (go, ("install_manifest_sha256", "manifest_SHA"), manifest_sha),
    ):
        need(field(value, *names) == expected, "GO source binding differs")
    need(ad["actual_original_authority_EX_private_GPU_EX_finite_SH"] is True,
         "Original owner resource admission missing")
    need(ad["original_canonical_owner_admitted"] is True, "Original canonical owner admission missing")
    need(go["canonical_binding"] == ad["canonical_binding"], "Parent canonical binding differs")
    fds = field(task, "inherited_lock_fds") if "inherited_lock_fds" in task else field(ad, "inherited_lock_fds")
    if "inherited_lock_fds" in ad:
        need(fds == ad["inherited_lock_fds"], "Admission FD list differs")
    need(len(fds) == 4 and len(set(fds)) == 4 and all(type(fd) is int for fd in fds), "Four distinct inherited FDs required")
    lock_receipts = []
    names = ("native_floor_supervisor.lock", "autonomy_controller.lock",
             "three_expert_v2_" + gpu + ".lock", "finite_environment_validation.lock")
    for index, fd in enumerate(fds):
        actual = os.fstat(fd)
        parent = os.stat(f"/proc/{os.getppid()}/fd/{fd}")
        need((actual.st_dev, actual.st_ino) == (parent.st_dev, parent.st_ino), "FD is not the actual parent's inherited object")
        target = os.readlink(f"/proc/self/fd/{fd}")
        need(Path(target).name == names[index], "Inherited lock identity/order differs")
        info = Path(f"/proc/self/fdinfo/{fd}").read_text(encoding="utf-8")
        mode = "READ" if index == 3 else "WRITE"
        need(any(line.startswith("lock:") and "FLOCK" in line and re.search(r"\b" + mode + r"\b", line)
                 for line in info.splitlines()), "Inherited lock mode differs")
        lock_receipts.append(dict(fd=fd, path=target, mode="SH" if index == 3 else "EX",
                                  inode=actual.st_ino, actual_parent_same_inode=True))
    need(task["num_envs"] == 20000 and task.get("steps_per_env", 48) == 48, "Continuation batch must be N20000/T48")
    need(type(task.get("max_iterations")) is int and 1 <= task["max_iterations"] <= 25,
         "Finite55afa window cap must be an explicit integer in 1..25 NEW updates")
    validate_source_binding(task)  # metadata only, before SDK/model I/O
    need(field(task, "teacher", "teacher_path") == MOTHER_PATH, "Mother path differs")
    need(field(task, "teacher_sha256", "teacher_SHA") == MOTHER_SHA and task["teacher_bytes"] == MOTHER_BYTES,
         "Mother source binding differs")
    need(task.get("teacher_iter", MOTHER_ITER) == MOTHER_ITER, "Mother iteration binding differs")
    need(field(task, "asset_sha256", "asset_SHA") == ASSET_SHA and
         field(task, "contract_sha256", "contract_SHA") == CONTRACT_SHA, "New physical asset binding differs")
    start = float(go["learning_started_epoch"])
    save_deadline = float(field(go, "save_deadline_epoch", "save_deadline"))
    end = float(field(go, "nominal_end_epoch", "nominal_end"))
    need(save_deadline == start + 3600 and end == start + 3900, "One-hour save/headroom contract differs")
    need(go["max_parent_seconds"] == 3900 and go["shutdown_headroom_seconds"] == 300, "Original owner deadline contract differs")
    need(start <= time.time() < save_deadline, "GO learning window is not current")
    entries = manifest["files"]
    need(type(entries) is list and bool(entries), "Empty install manifest")
    installed = set()
    task_overlays = []
    for item in entries:
        relative = field(item, "path", "relative")
        path = child_path(job, relative)
        need(path.suffix.lower() not in (".pt", ".pth", ".ckpt", ".onnx", ".data"), "Model files must not be manifest-read")
        need(relative not in installed, "Duplicate install path")
        installed.add(relative)
        raw = path.read_bytes()
        need(len(raw) == item["bytes"] and sha(raw) == field(item, "sha256", "SHA"), "Installed source hash differs: " + relative)
        if path.name == "e3_fudan_task_runtime_v1.py":
            need(len(raw) == TASK_RUNTIME_BYTES and sha(raw) == TASK_RUNTIME_SHA, "Fixed timeout8 task overlay differs")
            task_overlays.append(path)
    required = {"worker_fudan_sequence_ppo_native_v1.py", "fudan_seq_ppo.py", "e3_fudan_task_runtime_v1.py",
                "app_close_semantics_v6.py", "resume_runtime_contracts_v3.py", "pose_cache_runtime_adapter_v4.py",
                "train_mod4v1_e3.py", "fudan_task_pose.json", "retained_learner_source_v1.py"}
    need(required <= {Path(p).name for p in installed}, "Required native dependency missing from manifest")
    need(len(task_overlays) == 1, "One fixed new timeout8 task overlay required")
    receipt = dict(kind=KIND, version=8, branch_kind=BRANCH_KIND, source_kind=SOURCE_KIND,
                   source_schema_version=INPUT_SCHEMA_VERSION, source_branch_kind=INPUT_BRANCH_KIND,
                   source_input_source_kind=INPUT_SOURCE_KIND,
                   full_learner_resume=True, inherited_old_iterations=0, bad_candidate_reads=0, current_mother_reads=0,
                   source_training_execution_qualified=True, max_iterations=task["max_iterations"],
                   task_runtime_overlay=dict(path=str(task_overlays[0]), bytes=TASK_RUNTIME_BYTES, sha256=TASK_RUNTIME_SHA),
                   epoch=time.time(), task_sha256=task_sha, GO_sha256=go_sha,
                   root_admission_sha256=ad_sha, install_manifest_sha256=manifest_sha,
                   run=run, gpu_uuid=gpu, actual_parent_pid=os.getppid(), inherited_locks=lock_receipts,
                   canonical_binding=ad["canonical_binding"], child_canonical_reads_writes=0,
                   SDK_constructed=False, source_checkpoint_reads=0, original_mother_reads=0,
                   learner_source_reads=0, num_envs=20000, source_envs=20000,
                   native_counters_scope="CURRENT_N20000_WINDOW_ONLY",
                   learner_source_binding=validate_source_binding(task),
                   base_counters=dict(task["learner_source"]["counters"]),
                   counters=dict(task["learner_source"]["counters"]),
                   window_counters={key: 0 for key in task["learner_source"]["counters"]})
    return task, go, receipt


def configure_environment(job: Path, task: dict[str, Any], go: dict[str, Any]) -> Path:
    manifest, _ = read_json(child_path(job, task.get("original_run_manifest", "original_run_manifest.json")))
    for name in list(os.environ):
        if name.startswith(("RM_", "MOD4V1_", "MOD4_RESUME_")) or name in (
            "PYTHONPATH", "OWN_E2_H1_KIND", "RANK", "LOCAL_RANK", "WORLD_SIZE", "MASTER_ADDR", "MASTER_PORT"
        ):
            del os.environ[name]
    original = manifest["env"]
    excluded = {"RM_RESCUE_DEADLINE", "RM_RESCUE_STOP_FILE", "RM_SLOPE_INITIAL_ADMISSION", "CUDA_VISIBLE_DEVICES"}
    os.environ.update({k: str(v) for k, v in original.items() if k not in excluded})
    assets = child_path(job, task.get("asset_usd", "runtime/assets/robot.usd")).parent
    storage = job / "kit_isolation"
    storage.mkdir(exist_ok=False)
    (storage / "data").mkdir()
    (storage / "DerivedDataCache").mkdir()
    (storage / "data/user.config.json").write_text("{}", encoding="utf-8")
    os.environ.update(RM_MOD4_USD=str(assets / "robot.usd"), RM_KEEP_STD="1", RM_PHYSICS_DT_S=".0025",
                      RM_SOLVER_POS="32", RM_SOLVER_VEL="4", MOD4_RESUME_QUEUE_CONTROL_US="20000",
                      RM_RESCUE_DEADLINE=str(field(go, "save_deadline_epoch", "save_deadline")),
                      RM_RESCUE_STOP_FILE=str(job / "STOP_AFTER_SAVE.json"), PYTHONDONTWRITEBYTECODE="1",
                      MOD4V1_E3_ASSET_DIR=str(assets), MOD4V1_E3_JOB_ROOT=str(job),
                      MOD4V1_E3_KIT_STORAGE_ROOT=str(storage), OWN_E2_H1_KIND="E3_PUBLIC_RECOVERY",
                      RM_SPAWN_GRACE_STEPS="5", RM_JUMP_SCRIPT_PROB="0", RM_MOD4_MAP="", RM_MOD4_TERRAIN="flat")
    mod = job / "runtime/isaac/mod4"
    sys.path[:0] = [str(job / "worker_sources"), str(job / "lib"), str(mod),
                   str(job / "runtime"), str(job / "producer/lib"), str(job)]
    entry = child_path(job, task.get("runtime_entry", "runtime/isaac/mod4/train_mod4v1_e3.py"))
    sys.argv = [str(entry), "--headless", "--device", "cuda:0", "--num_envs", "20000", "--seed", str(task["seed"]),
                "--steps_per_env", "48", "--additional_iterations", "1"]
    return entry


def cpu_tree(value: Any, torch: Any, np: Any) -> Any:
    if torch.is_tensor(value):
        result = value.detach().cpu().clone()
        if result.is_floating_point() or result.is_complex():
            need(bool(torch.isfinite(result).all()), "Nonfinite tensor in complete state")
        return result
    if isinstance(value, np.ndarray):
        if np.issubdtype(value.dtype, np.number):
            need(bool(np.isfinite(value).all()), "Nonfinite array in complete state")
        return value.copy()
    if isinstance(value, Mapping):
        return {key: cpu_tree(item, torch, np) for key, item in value.items()}
    if type(value) in (list, tuple):
        return type(value)(cpu_tree(item, torch, np) for item in value)
    if value is None or isinstance(value, (str, bool, int, float, bytes, np.generic, torch.dtype, torch.device)):
        if isinstance(value, (float, np.floating)):
            need(bool(np.isfinite(value)), "Nonfinite scalar in complete state")
        return copy.deepcopy(value)
    raise TypeError("Unsupported fullstate field: " + type(value).__name__)


def named_rngs(obj: Any, torch: Any) -> dict[str, Any]:
    return {name: generator.get_state().clone() for name, generator in vars(obj).items()
            if isinstance(generator, torch.Generator)}


def snapshot_env(env: Any, observations: Any, history: Any, torch: Any, np: Any, tensor: Any,
                 task_runtime: Any) -> dict[str, Any]:
    """Typed Python/plant fullstate, explicitly NOT an opaque PhysX exact resume."""
    robot = env.scene["robot"]
    twist = env.command_manager.get_term("twist")
    components = {}
    for name in ("_sensor_mild", "_feedback_delay_mild", "_physics_action_delay", "_spring_pressure",
                 "_gas_damping", "_chassis_com", "_explicit_pd"):
        component = getattr(env, name)
        need(callable(getattr(component, "state_dict", None)), "Required DR state_dict missing: " + name)
        components[name] = component.state_dict()
    dr = env._mild_dr
    dr_fields = ("mass", "inertia", "materials", "com", "gains", "other_joint_values", "wheel_shapes",
                 "nonwheel_shapes", "friction_buckets", "factor", "nominal", "mu", "reset_count", "output")
    components["_mild_dr"] = {name: getattr(dr, name) for name in dr_fields}
    components["_mild_dr"]["named_rng_states"] = named_rngs(dr, torch)
    need({"generator", "cpu_generator"} <= set(components["_mild_dr"]["named_rng_states"]), "D0 named RNG missing")
    components["_mild_dr"]["actuators"] = {
        key: {name: getattr(robot.actuators[key], name) for name in ("episode_scale", "step_scale")}
        for key in ("legs", "wheels")
    }
    contact = env._integrated_contact
    contact_fields = ("dt", "crossbin", "dt_us", "stride", "tick", "sums", "peaks", "history",
                      "peak_history", "impulse", "loaded", "off_run", "off_max")
    components["integrated_contact"] = {name: getattr(contact, name) for name in contact_fields}
    # These adapter baselines/caches are NOT included in component.state_dict().
    # Historical audit event lists and opaque SDK references are not restart state.
    adapter_fields = {
        "_spring_pressure": ("nominal", "ids", "initial_other", "setter_calls", "stiffness_error"),
        "_gas_damping": ("original_damping", "ids", "other_ids", "fixed", "reset_calls", "selected_reset_samples", "setter_calls"),
        "_chassis_com": ("original_pose", "orientation_after_parent_reset", "body_id", "setter_calls", "reset_calls",
                         "cache_invalidations", "orientation_roundtrip_max", "raw_quaternion_bytes_always_exact"),
        "_explicit_pd": ("nominal", "leg_ids", "wheel_ids", "motor_ids", "model_write_calls", "reset_calls"),
    }
    components["adapter_baselines_and_dynamic_caches"] = {
        key: {name: getattr(getattr(env, key), name) for name in names}
        for key, names in adapter_fields.items()
    }
    components["actuator_coefficients"] = {
        key: {name: tensor(getattr(robot.actuators[key], name)) for name in ("stiffness", "damping")}
        for key in ("legs", "wheels", "gas_springs")
    }
    need(hasattr(twist, "_mode_rng"), "Original E3 command RNG missing")
    command_tensors = {name: value for name, value in vars(twist).items() if torch.is_tensor(value)}
    env_tensors = {name: value for name, value in vars(env).items() if torch.is_tensor(value)}
    payload = dict(
        root_state_w=tensor(robot.data.root_state_w), joint_pos=tensor(robot.data.joint_pos),
        joint_vel=tensor(robot.data.joint_vel), body_names=list(robot.body_names), joint_names=list(robot.joint_names),
        actual_observations=observations, history_old_to_new=history,
        recovery=env.recovery.state_dict(), command_tensors=command_tensors, command_named_rng_states=named_rngs(twist, torch),
        D0_D7=components, environment_tensor_caches=env_tensors,
        episode_length_buf=env.episode_length_buf, common_step_counter=int(env.common_step_counter),
        sim_step_counter=int(env._sim_step_counter), feedback_100hz_tick=int(env._feedback_100hz_tick),
        action_manager_action=env.action_manager.action, action_manager_prev_action=env.action_manager.prev_action,
        task_stage_summary=task_runtime.state_summary(env),
        native_PhysX_bitwise_exact_resume=False,
        opaque_SDK_scene_and_warp_alias_references_serialized=False,
    )
    return cpu_tree(payload, torch, np)


class NativeStats:
    """Observe existing termination computation; no additional observation/noise call."""
    def __init__(self, env: Any, torch: Any, tensor: Any):
        self.env, self.torch, self.tensor = env, torch, tensor
        self.controls = 0
        self.physics_start = int(env._integrated_contact.tick)
        self.feedback_start = int(env._feedback_100hz_tick)
        self.compute_calls = 0
        self.terms = {name: 0 for name in env.termination_manager.active_terms}
        self.credit_events = 0
        self.height_sum = 0.0
        self.height_count = 0
        self.height_min = None
        self.height_max = None
        self.gravity_sum = 0.0
        self.last_term = self.last_timeout = None
        self.original_compute = env.termination_manager.compute
        env.termination_manager.compute = self.compute

    def compute(self, *args: Any, **kwargs: Any) -> Any:
        before = self.env.recovery.credited.clone()
        result = self.original_compute(*args, **kwargs)
        tm = self.env.termination_manager
        self.last_term = tm.terminated.clone()
        self.last_timeout = tm.time_outs.clone()
        self.compute_calls += 1
        for name in self.terms:
            self.terms[name] += int(tm.get_term(name).sum().item())
        self.credit_events += int((self.env.recovery.credited & ~before).sum().item())
        robot = self.env.scene["robot"]
        heights = self.tensor(robot.data.root_state_w)[:, 2] - self.env.scene.env_origins[:, 2]
        low, high = float(heights.min().item()), float(heights.max().item())
        self.height_min = low if self.height_min is None else min(self.height_min, low)
        self.height_max = high if self.height_max is None else max(self.height_max, high)
        self.height_sum += float(heights.sum().item())
        self.height_count += heights.numel()
        self.gravity_sum += float(self.tensor(robot.data.projected_gravity_b)[:, 2].sum().item())
        return result

    def after_step(self) -> None:
        self.controls += 1
        need(int(self.env._integrated_contact.tick) - self.physics_start == self.controls * 8, "Actual physics/control clock differs")
        need(int(self.env._feedback_100hz_tick) - self.feedback_start == self.controls * 2, "Actual feedback/control clock differs")
        need(self.compute_calls == self.controls, "Termination computation count differs")

    def receipt(self) -> dict[str, Any]:
        return dict(actual_native_policy_steps=self.controls, actual_native_transitions=self.controls * self.env.num_envs,
                    physical_callbacks=int(self.env._integrated_contact.tick) - self.physics_start,
                    feedback_callbacks=int(self.env._feedback_100hz_tick) - self.feedback_start,
                    termination_computations=self.compute_calls, termination_counts=dict(self.terms),
                    pre_reset_credit_events=self.credit_events, pre_reset_height_min_m=self.height_min,
                    pre_reset_height_max_m=self.height_max,
                    pre_reset_height_mean_m=self.height_sum / self.height_count if self.height_count else None,
                    pre_reset_gravity_z_mean=self.gravity_sum / self.height_count if self.height_count else None,
                    counters_are_training_description_not_independent_skill_rate=True)


def check_plant(env: Any, identity: Any, task: dict[str, Any]) -> None:
    need(env.num_envs == 20000 and env.physics_dt == .0025 and env.step_dt == .02 and env.cfg.decimation == 8,
         "Fresh N20000/2.5ms/20ms clock differs")
    need(env.cfg.terminations.closure.params["threshold"] == .01 and
         env.cfg.terminations.mimic.params["threshold"] == .01, "Original reset thresholds differ")
    need(identity.usd_sha256 == ASSET_SHA and identity.contract_sha256 == CONTRACT_SHA, "Constructed asset differs")
    need(env.cfg.sim.physics.solver_type == 1, "Original TGS solver differs")
    props = env.cfg.scene.robot.spawn.articulation_props
    need(props.solver_position_iteration_count == 32 and props.solver_velocity_iteration_count == 4,
         "Original TGS32/4 differs")
    need(env._mild_dr.profile == "white_v3" and env._sensor_mild.profile == "noise_bias_mild_v1", "Original DR profile differs")
    need(env._feedback_delay_mild.enabled and env._physics_action_delay.queue.enabled, "Original delay queues disabled")
    for name in ("_spring_pressure", "_gas_damping", "_chassis_com", "_explicit_pd"):
        need(getattr(env, name).component.enabled, "Original DR component disabled: " + name)
    need(env._physics_action_delay.queue.control_us == 20000, "Action delay queue clock differs")
    need(env.spring_pressure_recipe()["nominal_stiffness_N_m"] == 2000, "Original spring stiffness differs")


def outputs(obs: Any, n: int, torch: Any) -> tuple[Any, Any]:
    need(isinstance(obs, Mapping), "Actual environment observation dict required")
    actor, critic = obs["policy"], obs["critic"]
    need(tuple(actor.shape) == (n, 35) and tuple(critic.shape) == (n, 38), "Actual raw35/priv38 interface differs")
    need(bool(torch.isfinite(actor).all()) and bool(torch.isfinite(critic).all()), "Nonfinite actual observations")
    return actor.detach(), critic.detach()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-root", required=True, type=Path)
    args = parser.parse_args()
    job = args.job_root.resolve(strict=True)
    task, go, admission = admit(job)
    out = job / "production"
    need(not out.exists(), "Production output already exists; old worker replay is not permitted")
    out.mkdir()
    put(out / "FDN_TASK_RESOURCE_BOUND_BEFORE_SDK_MODEL.json", admission)
    env = app = learner = source = stats = task_runtime = torch = np = tensor = None
    close_helper = pose_handle = pose_events = guard = None
    observations = history = None
    pending: dict[str, Any] = {}
    latest = None
    save_count = 0
    error = None
    close_errors: list[dict[str, str]] = []
    reason = "not_started"
    save_deadline = float(field(go, "save_deadline_epoch", "save_deadline"))
    end_deadline = float(field(go, "nominal_end_epoch", "nominal_end"))
    last_update_seconds = 0.0

    def save(reason_for_save: str) -> dict[str, Any]:
        nonlocal latest, save_count
        need(all(item is not None for item in (env, learner, source, stats, observations, history)),
             "Complete new state is not initialized")
        need(source.loaded, "Complete inherited learner has not been loaded")
        import random
        source.assert_frozen()
        window = source.window_counters(learner)
        root_receipt = source.receipt()
        state = source.unknown_root_for_save()
        state.update(dict(
            kind=KIND, version=8, epoch=time.time(), reason=reason_for_save, resource_binding=admission,
            branch_kind=BRANCH_KIND, source_kind=SOURCE_KIND, task_runtime_overlay=admission["task_runtime_overlay"],
            source_schema_version=INPUT_SCHEMA_VERSION, source_branch_kind=INPUT_BRANCH_KIND,
            source_input_source_kind=INPUT_SOURCE_KIND,
            full_learner_resume=True, inherited_old_iterations=0, bad_candidate_reads=0, current_mother_reads=0,
            source_training_execution_qualified=True, max_iterations=task["max_iterations"], num_envs=20000, source_envs=20000,
            inherited_source_learner_updates=source.base_counters["updates"], ancestral_mother_iterations_inherited=0,
            learner_continuation=source.continuation(), base_counters=dict(source.base_counters),
            counters=dict(learner.counters), window_counters=window, native_counters_scope="CURRENT_N20000_WINDOW_ONLY",
            source_checkpoint=root_receipt, source_receipt=root_receipt, ancestral_mother_checkpoint=source.ancestral_receipt(),
            original_mother_reads=0, learner_source_reads=1, learner=source.learner_state_for_save(learner),
            global_rng=dict(python=random.getstate(), numpy=np.random.get_state(),
                            torch_cpu=torch.get_rng_state(), torch_cuda_all=torch.cuda.get_rng_state_all()),
            environment=snapshot_env(env, observations, history, torch, np, tensor, task_runtime),
            pending_rollout=cpu_tree(pending, torch, np), native_counters=stats.receipt(),
            save_is_typed_fullstate_not_native_PhysX_bitwise_resume=True,
            fullstate_required_components_complete=True, skill_improvement_claim=False,
        ))
        state = cpu_tree(state, torch, np)
        index = save_count + 1
        path = out / f"fudan_seq20k_full_u{learner.counters['updates']:06d}_wu{window['updates']:06d}_c{stats.controls:08d}_s{index:04d}.pt"
        temporary = path.with_name(path.name + ".partial")
        need(not path.exists() and not temporary.exists(), "New save path collision")
        with temporary.open("xb") as stream:
            torch.save(state, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        fsync_directory(out)
        digest = hashlib.sha256()
        with path.open("rb") as stream:  # this OWN new save is hashed exactly once
            while True:
                block = stream.read(4 * 1024 * 1024)
                if not block:
                    break
                digest.update(block)
        save_receipt = source.receipt()
        receipt = dict(kind=KIND, version=8, branch_kind=BRANCH_KIND, source_kind=SOURCE_KIND,
                       source_schema_version=INPUT_SCHEMA_VERSION, source_branch_kind=INPUT_BRANCH_KIND,
                       source_input_source_kind=INPUT_SOURCE_KIND,
                       full_learner_resume=True, inherited_old_iterations=0, bad_candidate_reads=0, current_mother_reads=0,
                       source_training_execution_qualified=True, max_iterations=task["max_iterations"], num_envs=20000, source_envs=20000,
                       task_runtime_overlay=admission["task_runtime_overlay"],
                       path=str(path), bytes=path.stat().st_size, sha256=digest.hexdigest(),
                       save_index=index, epoch=time.time(), fullstate_required_components_complete=True,
                       both_Adam_states_present=True, model_and_all_required_RNG_present=True,
                       new_asset_and_fresh_D0_D7_state_present=True, original_mother_reads=0, learner_source_reads=1,
                       source_checkpoint=save_receipt, source_receipt=save_receipt, ancestral_mother_checkpoint=source.ancestral_receipt(),
                       learner_continuation=source.continuation(), base_counters=dict(source.base_counters),
                       window_counters=window, native_counters_scope="CURRENT_N20000_WINDOW_ONLY",
                       own_new_save_hash_opens=1, counters=dict(learner.counters), native_counters=stats.receipt(),
                       native_PhysX_bitwise_exact_resume=False, save_reason=reason_for_save)
        put(out / "FDN_LATEST_COMPLETE_SAVE.json", receipt)
        latest, save_count = receipt, index
        return receipt

    try:
        entry = configure_environment(job, task, go)
        # App exists only after this non-main import.  Never call ns['main'].
        ns = runpy.run_path(str(entry), run_name="new_fudan_native_constructor_not_old_PPO_main")
        app = ns["app"]
        import torch as torch_module
        import numpy as numpy_module
        torch, np = torch_module, numpy_module
        from mild_dr import tensor as tensor_converter
        tensor = tensor_converter
        from mod4v1_fresh_dr_guard import FreshDRNominalGuard
        import fudan_seq_ppo as core
        close_helper = importlib.import_module("app_close_semantics_v6")
        close_binding = close_helper._pin_original_app_close(app)
        need(close_binding["fast_shutdown"] is True, "Actual original App fast_shutdown differs")
        put(out / "FDN_ORIGINAL_APP_CLOSE_BINDING.json", close_binding)
        task_runtime = importlib.import_module("e3_fudan_task_runtime_v1")
        need(Path(task_runtime.__file__).resolve(strict=True) == Path(admission["task_runtime_overlay"]["path"]),
             "Imported task runtime is not the fixed installed timeout8 overlay")
        task_runtime.install_before_build()  # AFTER App/runtime import, BEFORE build_env
        env = ns["build_env"]()
        identity = ns["E3_IDENTITY"]
        check_plant(env, identity, task)
        timeout_term = getattr(env.cfg.terminations, "e3_fudan_lowrise_timeout8")
        need(timeout_term.func is task_runtime.lowrise_timeout8 and timeout_term.time_out is True,
             "Constructed lowrise timeout is not the fixed independent timeout8 term")
        task_runtime.bind_after_build(env, job)
        env.e3_reset_enabled = True
        pose_module = importlib.import_module("pose_cache_runtime_adapter_v4")
        def pose_emit(event: Any) -> None:
            put(out / "FDN_POSE_CACHE_EVENTS.json", event)
        pose_events = close_helper.BoundedPoseCacheEventsV5(pose_emit)
        pose_handle = pose_module.install_pose_cache_runtime_adapter_v4(env.scene["robot"], receipt_callback=pose_events)
        guard = FreshDRNominalGuard(env, identity, torch_module=torch, tensor_converter=tensor)
        with guard.around_original_fullstate_restore():
            reset = env.reset()  # the one explicit fresh reset; NOT an old checkpoint restore
        observations = reset[0] if isinstance(reset, tuple) else reset
        guard.check_observations(observations)
        put(out / "FDN_FRESH_NEW_NOMINAL_RESET.json", guard.receipt())
        actor_obs, critic_obs = outputs(observations, env.num_envs, torch)
        history = actor_obs[:, None, :].repeat(1, 5, 1).clone()
        stats = NativeStats(env, torch, tensor)
        source = RetainedLearnerSource(task, torch, np)
        # TASK.seed belongs to the fresh ENV, source config to the learner.
        # Forking preserves new-window global CPU/CUDA DR/reset RNG streams.
        # The unchanged loader clones models/STD/LR/both Adam/counters/private RNG.
        # NEVER apply source environment/global_rng/history/queues/pending to N20000.
        with torch.random.fork_rng(devices=[torch.cuda.current_device()]):
            learner = core.SequencePPO(core.PPOConfig(**dict(source.root["learner"]["config"])), device=env.device)
            loaded = source.load_into(learner)
        initial_window = source.window_counters(learner)
        need(all(value == 0 for value in initial_window.values()), "Initial NEW-window delta is not zero")
        put(out / "FDN_FULL_LEARNER_CONTINUATION_INITIALIZED.json", dict(kind=KIND, version=8,
            branch_kind=BRANCH_KIND, source_kind=SOURCE_KIND, task_runtime_overlay=admission["task_runtime_overlay"],
            source_schema_version=INPUT_SCHEMA_VERSION, source_branch_kind=INPUT_BRANCH_KIND,
            source_input_source_kind=INPUT_SOURCE_KIND,
            full_learner_resume=True, inherited_old_iterations=0, bad_candidate_reads=0, current_mother_reads=0,
            source_training_execution_qualified=True, max_iterations=task["max_iterations"], num_envs=20000,
            source_checkpoint=loaded, source_receipt=loaded, ancestral_mother_checkpoint=source.ancestral_receipt(),
            learner_continuation=source.continuation(),
            base_counters=dict(source.base_counters), counters=dict(learner.counters), window_counters=initial_window,
            native_counters_scope="CURRENT_N20000_WINDOW_ONLY",
            inherited_source_learner_updates=source.base_counters["updates"], ancestral_mother_iterations_inherited=0,
            learner_config=copy.deepcopy(dict(source.root["learner"]["config"])), current_learning_rate=learner.learning_rate,
            fresh_envs=20000, source_envs=20000, history_initialized_from_new_returned_raw35_repeated_five=True,
            environment_seed=int(task["seed"]), learner_config_seed=learner.config.seed,
            original_mother_reads=0, learner_source_reads=1,
            source_global_RNG_environment_DR_history_queues_or_pending_applied=False,
            task_summary=task_runtime.state_summary(env), stage1_only=True,
            whole_leg_rear_video_target_covered=False, implementation_is_institution_official_recovery_code=False))
        while source.window_counters(learner)["updates"] < task["max_iterations"]:
            if time.time() >= save_deadline or (job / "STOP_AFTER_SAVE.json").exists() or (job / "STOP_AFTER_SAVE").exists():
                reason = "save_deadline_or_parent_stop"
                break
            rows: dict[str, list[Any]] = {key: [] for key in (
                "obs", "history", "privileged_obs", "body_velocity", "latent", "actions", "rewards", "dones",
                "time_outs", "values", "log_prob", "mu", "sigma")}
            pending = dict(kind="partial_T48_rollout", rows=rows, completed_control_steps=0)
            for step in range(48):
                if time.time() >= save_deadline or (job / "STOP_AFTER_SAVE.json").exists() or (job / "STOP_AFTER_SAVE").exists():
                    reason = "save_deadline_or_parent_stop_during_rollout"
                    break
                actor_obs, critic_obs = outputs(observations, env.num_envs, torch)
                flat_history = history.reshape(env.num_envs, 175)
                velocity = tensor(env.scene["robot"].data.root_lin_vel_b).detach().clone()
                need(tuple(velocity.shape) == (env.num_envs, 3) and bool(torch.isfinite(velocity).all()), "Body-velocity target differs")
                sample = learner.act(actor_obs, flat_history, critic_obs)
                need(bool(torch.isfinite(sample["actions"]).all()), "Nonfinite policy sample")
                before = dict(obs=actor_obs.clone(), history=flat_history.clone(), privileged_obs=critic_obs.clone(),
                              body_velocity=velocity, **{key: sample[key].detach().clone()
                                  for key in ("latent", "actions", "values", "log_prob", "mu", "sigma")})
                result = env.step(sample["actions"].clamp(-6.0, 6.0))
                need(isinstance(result, tuple) and len(result) == 5, "Original native Gym step interface differs")
                observations, reward, terminated, truncated, infos = result
                stats.after_step()
                done = (terminated | truncated).bool()
                need(torch.equal(stats.last_term, terminated.bool()) and torch.equal(stats.last_timeout, truncated.bool()),
                     "Returned terminal masks differ from pre-reset computation")
                need(bool(torch.isfinite(reward).all()), "Nonfinite original task reward")
                before.update(rewards=reward.detach().clone(), dones=done.clone(), time_outs=truncated.bool().clone())
                for key, value in before.items():
                    rows[key].append(value)
                next_actor, _ = outputs(observations, env.num_envs, torch)
                history = torch.cat((history[:, 1:], next_actor[:, None, :]), dim=1)
                history[done] = next_actor[done, None, :].expand(-1, 5, -1)
                pending["completed_control_steps"] = step + 1
            if pending["completed_control_steps"] != 48:
                break
            if time.time() + max(60.0, last_update_seconds * 1.5) >= save_deadline:
                reason = "headroom_before_next_main_encoder_update"
                break
            rollout = {key: torch.stack(value) for key, value in rows.items()}
            _, current_critic = outputs(observations, env.num_envs, torch)
            last_values = learner.value(current_critic, history=history.reshape(env.num_envs, 175))
            update_start = time.time()
            metrics = learner.update(rollout, last_values)
            last_update_seconds = time.time() - update_start
            pending = {}
            source.assert_frozen()
            guard.assert_new_nominals_unchanged()
            window = source.window_counters(learner)
            need(window["policy_optimizer_steps"] == 20 * window["updates"] and
                 window["encoder_optimizer_steps"] == 20 * window["updates"] and
                 window["transitions_seen"] == 48 * 20000 * window["updates"],
                 "Completed NEW-window learner accounting differs")
            need(stats.controls >= 48 * window["updates"], "Window native controls do not cover optimized rollouts")
            update_source_receipt = source.receipt()
            update_receipt = dict(kind=KIND, version=8, epoch=time.time(), branch_kind=BRANCH_KIND, source_kind=SOURCE_KIND,
                source_schema_version=INPUT_SCHEMA_VERSION, source_branch_kind=INPUT_BRANCH_KIND,
                source_input_source_kind=INPUT_SOURCE_KIND,
                full_learner_resume=True, inherited_old_iterations=0, bad_candidate_reads=0, current_mother_reads=0,
                source_training_execution_qualified=True, max_iterations=task["max_iterations"], num_envs=20000, source_envs=20000,
                task_runtime_overlay=admission["task_runtime_overlay"],
                learner_continuation=source.continuation(), base_counters=dict(source.base_counters),
                window_counters=window, native_counters_scope="CURRENT_N20000_WINDOW_ONLY",
                source_checkpoint=update_source_receipt, source_receipt=update_source_receipt,
                ancestral_mother_checkpoint=source.ancestral_receipt(), original_mother_reads=0, learner_source_reads=1,
                counters=dict(learner.counters), native_counters=stats.receipt(), learner_functional_metrics=metrics,
                task_summary=task_runtime.state_summary(env), last_update_wall_seconds=last_update_seconds,
                actual_native_training_update=True, inherited_source_learner_updates=source.base_counters["updates"],
                inherited_old_iteration_count=0,
                ancestral_mother_iterations_inherited=0, rollout_T=48, rollout_N=20000,
                physical_action_clip=6.0, stored_unclipped_Gaussian_actions=True,
                recovery_summary_is_training_description_not_independent_pass_rate=True,
                original_74_task_improvement_claim=False, whole_leg_rear_video_target_covered=False)
            put(out / "FDN_NATIVE_UPDATE.json", update_receipt)
            if window["updates"] % 25 == 0:
                save("interval_25_new_updates")
            if pose_events is not None:
                pose_events.flush()
        else:
            reason = f"max_{task['max_iterations']}_new_iterations"
        save(reason)
    except BaseException as exc:
        error = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc(), epoch=time.time())
        put(out / "FDN_NATIVE_ERROR.json", error)
        if all(item is not None for item in (env, learner, source, stats, observations, history)):
            try:
                save("error_complete_state_attempt")
            except BaseException as save_exc:
                put(out / "FDN_SAVE_ERROR.json", dict(type=type(save_exc).__name__, message=str(save_exc), traceback=traceback.format_exc()))
    # Metadata errors must not bypass env/App close or upgrade a failed run.
    counters = dict(learner.counters) if learner is not None else {}
    native, source_receipt, task_summary = {}, None, None
    base_counters, window_counters, continuation, ancestral = {}, {}, None, None
    try:
        native = stats.receipt() if stats is not None else {}
        source_receipt = source.receipt() if source is not None else None
        if source is not None:
            base_counters = dict(source.base_counters)
            continuation, ancestral = source.continuation(), source.ancestral_receipt()
            if learner is not None:
                window_counters = source.window_counters(learner)
        task_summary = task_runtime.state_summary(env) if task_runtime is not None and env is not None else None
        if pose_events is not None:
            pose_events.flush(force=True)
    except BaseException as exc:
        metadata_error = dict(stage="final_metadata", type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
        if error is None:
            error = metadata_error
        else:
            close_errors.append(metadata_error)
        put(out / "FDN_FINAL_METADATA_ERROR.json", metadata_error)
    # Inherited 25/500/500 alone NEVER qualifies a zero-new-learning window.
    complete = latest is not None and latest.get("fullstate_required_components_complete") is True
    qualified = bool(error is None and not close_errors and complete and native.get("actual_native_policy_steps", 0) > 0 and
                     window_counters.get("updates", 0) > 0 and window_counters.get("policy_optimizer_steps", 0) > 0 and
                     window_counters.get("encoder_optimizer_steps", 0) > 0 and
                     latest.get("counters") == counters and latest.get("window_counters") == window_counters)
    final = dict(kind=KIND, version=8, branch_kind=BRANCH_KIND, source_kind=SOURCE_KIND,
                 source_schema_version=INPUT_SCHEMA_VERSION, source_branch_kind=INPUT_BRANCH_KIND,
                 source_input_source_kind=INPUT_SOURCE_KIND,
                 full_learner_resume=True, inherited_old_iterations=0, bad_candidate_reads=0, current_mother_reads=0,
                 source_training_execution_qualified=True, max_iterations=task["max_iterations"], num_envs=20000, source_envs=20000,
                 task_runtime_overlay=admission["task_runtime_overlay"],
                 epoch=time.time(), run=field(task, "run", "run_id"), role="E3",
                 worker_pid=os.getpid(), parent_pid=os.getppid(), resource_binding=admission,
                 final=qualified, complete_save=complete, latest_complete_save=latest,
                 counters=counters, native_counters=native, save_count=save_count, stop_reason=reason,
                 learner_continuation=continuation, base_counters=base_counters, window_counters=window_counters,
                 native_counters_scope="CURRENT_N20000_WINDOW_ONLY",
                 original_mother_reads=0,
                 learner_source_reads=(source.counts["learner_source_reads"] if source is not None else None),
                 error=error, close_errors=close_errors, source_checkpoint=source_receipt, source_receipt=source_receipt,
                 ancestral_mother_checkpoint=ancestral, task_summary=task_summary,
                 old_SM_learner_or_old_PPO_main_called=False, child_canonical_reads_writes=0,
                 native_PhysX_bitwise_exact_resume=False, skill_improvement_claim=False,
                 whole_leg_rear_video_target_covered=False, parent_actual_wait_still_required=True,
                 nominal_end_epoch=end_deadline, save_deadline_epoch=save_deadline)
    final_path = out / "FDN_FINAL.json"
    final_sha = put(final_path, final)
    if env is not None:
        try:
            env.close()
        except BaseException as exc:
            close_errors.append(dict(stage="env.close", type=type(exc).__name__, message=str(exc)))
            final["final"] = False
            final_sha = put(final_path, final)
    if app is not None:
        try:
            # Pin again after env.close, then only durable Python I/O before close.
            need(close_helper is not None, "Original App close binding helper unavailable")
            binding = close_helper._pin_original_app_close(app)
            need(binding["fast_shutdown"] is True, "Original App close is not fast_shutdown")
            intent = dict(kind=KIND, version=8, branch_kind=BRANCH_KIND, source_kind=SOURCE_KIND,
                           source_schema_version=INPUT_SCHEMA_VERSION, source_branch_kind=INPUT_BRANCH_KIND,
                           source_input_source_kind=INPUT_SOURCE_KIND,
                           full_learner_resume=True, inherited_old_iterations=0, bad_candidate_reads=0, current_mother_reads=0,
                           source_training_execution_qualified=True, max_iterations=task["max_iterations"], num_envs=20000, source_envs=20000,
                           task_runtime_overlay=admission["task_runtime_overlay"], epoch=time.time(),
                           worker_pid=os.getpid(), parent_pid=os.getppid(), original_bound_close=binding,
                           learner_continuation=continuation, base_counters=base_counters, window_counters=window_counters,
                           counters=counters, native_counters_scope="CURRENT_N20000_WINDOW_ONLY",
                           original_mother_reads=0,
                           learner_source_reads=(source.counts["learner_source_reads"] if source is not None else None),
                           source_checkpoint=source_receipt, source_receipt=source_receipt, ancestral_mother_checkpoint=ancestral,
                           final_path=str(final_path), final_sha256=final_sha,
                           latest_complete_save=latest, actual_native_policy_steps=native.get("actual_native_policy_steps", 0),
                           learner_counters=counters, env_close_returned=not close_errors,
                           worker_final_qualified=final["final"], error_before_close=error, close_errors=close_errors,
                           parent_must_wait_rc0_and_validate_FDN_final=True,
                           no_SDK_calls_between_fsynced_intent_and_original_zero_argument_close=True)
            put(out / "FDN_APP_FAST_CLOSE_INTENT.json", intent)
            app.close()  # ORIGINAL bound method, zero arguments, immediately after fsynced intent
        except BaseException as exc:  # SystemExit is an error, never a synthetic close success
            close_errors.append(dict(stage="application.close", type=type(exc).__name__, message=str(exc)))
            final["final"] = False
            put(out / "FDN_APP_CLOSE_ERROR.json", close_errors[-1])
            put(final_path, final)
        else:
            put(out / "FDN_APP_CLOSE_RETURNED.json", dict(kind=KIND, epoch=time.time(), normal_python_return=True))
    return 0 if final["final"] and not close_errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Frozen E3 sequence mean: encoder + actor only; never opens checkpoint files.

The caller reads/hashes/CPU-decodes one whole new native-worker checkpoint.
Pass that Mapping here. Training DR/queues/history and optimizer state remain
caller-owned CPU data and are never restored or sliced into evaluation envs.
"""
from __future__ import annotations

import copy
import hashlib
import math
from collections.abc import Mapping
from typing import Any

import torch
from torch import Tensor, nn

KIND = "MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1"
MOTHER_SHA = "1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8"
MOTHER_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt"
MOTHER_BYTES = 14715029
MOTHER_ITER = 43090
BRANCH_KIND = "FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_HEIGHTGATE"
SOURCE_KIND = "fdn_fresh_mlp_warm_1cd_n20000_timeout8_heightgate"
# These old inputs are exclusions, NOT ancestors of this fresh-learner branch.
EXCLUDED_TIMEOUT8_RUN = "MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_CONTINUE133_W6_20261104_231058_1793805058620541900"
EXCLUDED_TIMEOUT8_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/" + EXCLUDED_TIMEOUT8_RUN + "/roles/E3/production/fudan_seq20k_full_u000205_wu000072_c00003504_s0003.pt"
EXCLUDED_TIMEOUT8_SHA = "3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e"
EXCLUDED_FRESH25_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W8_ADMISSION2_20261105_013118_1793813478778262400/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt"
EXCLUDED_FRESH25_SHA = "246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2"
EXCLUDED_PREVIOUS_N20000_RUN = "MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W5_ADMISSION2_20261104_204218_1793796138143516800"
EXCLUDED_PREVIOUS_N20000_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/" + EXCLUDED_PREVIOUS_N20000_RUN + "/roles/E3/production/fudan_seq20k_full_u000133_wu000069_c00003360_s0003.pt"
EXCLUDED_PREVIOUS_N20000_SHA = "8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78"
EXCLUDED_N4096_RUN = "MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W3_MAPPING_ADMISSION_20261104_185407_1793789647408789000"
EXCLUDED_N4096_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/" + EXCLUDED_N4096_RUN + "/roles/E3/production/fudan_seq_full_u000064_c00003110_s0003.pt"
EXCLUDED_N4096_SHA = "47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d"
BASE_COUNTERS = dict(updates=0, policy_optimizer_steps=0, encoder_optimizer_steps=0, transitions_seen=0)
TASK_RUNTIME_OVERLAY_SHA = "a89ff5487e76a5d7256b4cf9e60d5c7292047e3d70ca681f02d8c9900f0c4c35"
TASK_RUNTIME_OVERLAY_BYTES = 12723


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{name}: expected Mapping")
    return value


def _integer(value: Any, name: str) -> int:
    _require(type(value) is int and value >= 0, f"{name}: expected nonnegative int")
    return value


def _shapes(prefix: str, widths: tuple[int, ...]) -> dict[str, tuple[int, ...]]:
    out: dict[str, tuple[int, ...]] = {}
    for layer, (inputs, outputs) in enumerate(zip(widths, widths[1:])):
        out[f"{prefix}.mlp.{2 * layer}.weight"] = (outputs, inputs)
        out[f"{prefix}.mlp.{2 * layer}.bias"] = (outputs,)
    return out


ACTOR_SHAPES = _shapes("actor", (38, 256, 128, 64, 6))
ENCODER_SHAPES = _shapes("encoder", (175, 128, 64, 3))
PI_SHAPES = {**ACTOR_SHAPES, **ENCODER_SHAPES}
TRAINING_MODEL_KEYS = set(PI_SHAPES) | set(_shapes("critic", (41, 256, 128, 64, 1))) | {"log_std"}
COUNTER_KEYS = {"updates", "policy_optimizer_steps", "encoder_optimizer_steps", "transitions_seen"}


def _validate_learner(learner: Mapping[str, Any]) -> tuple[Mapping[str, Any], dict[str, int]]:
    required = {"format_version", "config", "model", "main_optimizer", "encoder_optimizer",
                "counters", "branch_metadata", "current_learning_rate", "generator_state"}
    _require(required <= set(learner), "learner: missing core.state_dict fields")
    _require(learner["format_version"] == 1, "learner: unsupported format_version")
    config = _mapping(learner["config"], "learner.config")
    fixed = dict(obs_dim=35, history_length=5, privileged_dim=38, latent_dim=3,
                 action_dim=6, rollout_steps=48, epochs=5, mini_batches=4,
                 body_velocity_scale=3.0)
    for name, expected in fixed.items():
        _require(config.get(name) == expected, f"learner.config.{name}: expected {expected}")
    for name, expected in (("actor_hidden", (256, 128, 64)),
                           ("critic_hidden", (256, 128, 64)), ("encoder_hidden", (128, 64))):
        _require(isinstance(config.get(name), (tuple, list)) and tuple(config[name]) == expected,
                 f"learner.config.{name}: wrong capacity")
    model = _mapping(learner["model"], "learner.model")
    _require(set(model) == TRAINING_MODEL_KEYS,
             "learner.model: require exact core actor/encoder/critic/log_std keys; no prefix guessing")
    for name in ("main_optimizer", "encoder_optimizer"):
        optimizer = _mapping(learner[name], f"learner.{name}")
        _require({"state", "param_groups"} <= set(optimizer), f"learner.{name}: missing Adam structure")
    counts = _mapping(learner["counters"], "learner.counters")
    _require(set(counts) == COUNTER_KEYS, "learner.counters: wrong keys")
    counters = {name: _integer(counts[name], f"learner.counters.{name}") for name in sorted(COUNTER_KEYS)}
    _require(counters["policy_optimizer_steps"] == counters["updates"] * 20 and
             counters["encoder_optimizer_steps"] == counters["updates"] * 20,
             "learner.counters: not completed 5x4 two-phase updates")
    # Population/stream-cut transition arithmetic is checked against the root below.
    branch = _mapping(learner["branch_metadata"], "learner.branch_metadata")
    _require(branch.get("kind") == "NEW_BRANCH_WARM_START" and
             branch.get("inherited_optimizer") is False and branch.get("inherited_iteration") is False,
             "learner.branch_metadata: wrong new-branch provenance")
    rate = learner["current_learning_rate"]
    _require(isinstance(rate, (int, float)) and math.isfinite(rate) and rate > 0,
             "learner.current_learning_rate: expected finite positive scalar")
    return model, counters


def validate_checkpoint_provenance(cpu_checkpoint: Mapping[str, Any], *,
                                   require_native_updates: bool = True,
                                   expected_run: str | None = None) -> dict[str, Any]:
    """Check fresh1cd N20000 save metadata, NOT file SHA, wait or skill success.

    The complete CPU root stays untouched. The training overlay is metadata only;
    it is never installed into the original N80 evaluator. The real 1cd receipt
    describes the training MLP warm start, not a full-learner/environment resume.
    """
    root = _mapping(cpu_checkpoint, "checkpoint")
    required = {"kind", "version", "epoch", "reason", "resource_binding", "branch_kind",
                "source_kind", "task_runtime_overlay", "inherited_old_iterations", "num_envs",
                "full_learner_resume", "bad_candidate_reads", "counters", "source_checkpoint",
                "learner", "global_rng", "environment", "pending_rollout", "native_counters",
                "native_counters_scope", "base_counters", "window_counters",
                "save_is_typed_fullstate_not_native_PhysX_bitwise_resume",
                "fullstate_required_components_complete", "skill_improvement_claim"}
    _require(required <= set(root), "checkpoint: missing native worker.save fields")
    _require(root["kind"] == KIND and type(root["version"]) is int and root["version"] == 5,
             "checkpoint: wrong kind/version5")
    _require(root["branch_kind"] == BRANCH_KIND and root["source_kind"] == SOURCE_KIND and
             _integer(root["inherited_old_iterations"], "inherited_old_iterations") == 0 and
             root["num_envs"] == 20000 and root["full_learner_resume"] is False and
             _integer(root["bad_candidate_reads"], "bad_candidate_reads") == 0,
             "checkpoint: wrong fresh1cd branch/zero-base initialization metadata")
    _require(not {"learner_continuation", "ancestral_N4096_checkpoint", "ancestral_mother_checkpoint"}.intersection(root),
             "checkpoint: fresh MLP warm start must not carry full-learner continuation ancestry")
    _require(root["fullstate_required_components_complete"] is True and
             root["save_is_typed_fullstate_not_native_PhysX_bitwise_resume"] is True and
             root["skill_improvement_claim"] is False, "checkpoint: wrong full-save declarations")
    _require(isinstance(root["reason"], str) and bool(root["reason"]) and
             "error" not in root["reason"].lower(), "checkpoint: error-path or missing save reason")
    binding = _mapping(root["resource_binding"], "resource_binding")
    run = binding.get("run", binding.get("run_id"))
    _require(isinstance(run, str) and bool(run), "resource_binding: missing run")
    if "run" in binding and "run_id" in binding:
        _require(binding["run"] == binding["run_id"], "resource_binding: conflicting run aliases")
    if expected_run is not None:
        _require(run == expected_run, "resource_binding: unexpected run")
    overlay = _mapping(root["task_runtime_overlay"], "task_runtime_overlay")
    _require(overlay.get("sha256") == TASK_RUNTIME_OVERLAY_SHA and
             overlay.get("bytes") == TASK_RUNTIME_OVERLAY_BYTES and
             isinstance(overlay.get("path"), str) and overlay["path"].startswith("/") and
             overlay["path"].endswith("/e3_fudan_task_runtime_v1.py") and
             _mapping(binding.get("task_runtime_overlay"), "resource_binding.task_runtime_overlay") == overlay,
             "task_runtime_overlay: wrong metadata-only training overlay binding")
    _, counters = _validate_learner(_mapping(root["learner"], "learner"))
    base = _mapping(root["base_counters"], "base_counters")
    window = _mapping(root["window_counters"], "window_counters")
    base_counts = {k: _integer(base.get(k), f"base_counters.{k}") for k in BASE_COUNTERS}
    window_counts = {k: _integer(window.get(k), f"window_counters.{k}") for k in BASE_COUNTERS}
    _require(base_counts == BASE_COUNTERS, "base_counters: fresh1cd requires all four counters zero")
    _require(counters == window_counts and _mapping(root["counters"], "counters") == counters,
             "learner.counters: fresh1cd root/window/learner counts differ")
    updates = window_counts["updates"]
    _require(window_counts["policy_optimizer_steps"] == 20 * updates and
             window_counts["encoder_optimizer_steps"] == 20 * updates and
             window_counts["transitions_seen"] == 48 * 20000 * updates,
             "window_counters: not completed N20000/T48/5x4 two-phase updates")
    source = _mapping(root["source_checkpoint"], "source_checkpoint")
    source_pin = dict(source_path=MOTHER_PATH, source_sha256=MOTHER_SHA,
                      source_bytes=MOTHER_BYTES, source_iter=MOTHER_ITER,
                      physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1)
    for key, value in source_pin.items():
        _require(source.get(key) == value, f"source_checkpoint.{key}: wrong actual 1cd warm-source pin")
    for key in ("whole_source_root_and_bytes_retained", "source_tensor_versions_unchanged",
                "actor_critic_MLP_only", "source_optimizer_and_DR_state_not_restored", "old_iteration_not_inherited"):
        _require(source.get(key) is True, f"source_checkpoint.{key}: expected true")
    ignored = source.get("ignored_old_exploration_keys")
    _require(isinstance(ignored, list) and all(type(key) is str for key in ignored) and
             len(ignored) == len(set(ignored)) and
             set(ignored) <= {"distribution.std_param", "distribution.log_std_param", "std", "log_std"},
             "source_checkpoint: unexpected ignored legacy exploration keys")
    learner = _mapping(root["learner"], "learner")
    initial_config = _mapping(learner["config"], "learner.config")
    for key, expected in dict(initial_std=.5, learning_rate=.001, encoder_learning_rate=.001).items():
        _require(initial_config.get(key) == expected, f"learner.config.{key}: wrong fresh initialization setting")
    warm = _mapping(learner["branch_metadata"], "learner.branch_metadata")
    for key, expected in dict(legacy_actor_input=35, legacy_critic_input=38,
                              latent_columns_zero_initialized=True,
                              std_parameterization="new learnable log_std; not copied from legacy").items():
        _require(warm.get(key) == expected, f"learner.branch_metadata.{key}: wrong MLP warm initialization metadata")
    native = _mapping(root["native_counters"], "native_counters")
    native_fields = ("actual_native_policy_steps", "actual_native_transitions", "physical_callbacks",
                     "feedback_callbacks", "termination_computations")
    native_counts = {name: _integer(native.get(name), f"native_counters.{name}") for name in native_fields}
    controls = native_counts["actual_native_policy_steps"]
    _require(root["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
             native_counts["actual_native_transitions"] == controls * 20000 and
             native_counts["physical_callbacks"] == controls * 8 and
             native_counts["feedback_callbacks"] == controls * 2 and
             native_counts["termination_computations"] == controls,
             "native_counters: wrong current-window 20000/8/2/control relationship")
    _require(0 <= controls - 48 * updates <= 48,
             "native_counters: invalid current-window optimized/partial control count")
    if require_native_updates:
        _require(controls > 0 and updates > 0 and window_counts["policy_optimizer_steps"] > 0 and
                 window_counts["encoder_optimizer_steps"] > 0,
                 "checkpoint: require positive new-window native controls and both Adam deltas")
    rng = _mapping(root["global_rng"], "global_rng")
    _require({"python", "numpy", "torch_cpu", "torch_cuda_all"} <= set(rng), "global_rng: missing keys")
    environment = _mapping(root["environment"], "environment")
    env_fields = {"root_state_w", "joint_pos", "joint_vel", "body_names", "joint_names",
                  "actual_observations", "history_old_to_new", "recovery", "command_tensors",
                  "command_named_rng_states", "D0_D7", "environment_tensor_caches", "episode_length_buf",
                  "common_step_counter", "sim_step_counter", "feedback_100hz_tick",
                  "action_manager_action", "action_manager_prev_action", "task_stage_summary",
                  "native_PhysX_bitwise_exact_resume", "opaque_SDK_scene_and_warp_alias_references_serialized"}
    _require(env_fields <= set(environment), "environment: missing typed snapshot structure")
    root_state = environment["root_state_w"]
    _require(isinstance(root_state, Tensor) and root_state.device.type == "cpu" and
             root_state.ndim >= 1 and root_state.shape[0] == 20000,
             "environment.root_state_w: expected whole N20000 CPU state")
    _require(environment["native_PhysX_bitwise_exact_resume"] is False and
             environment["opaque_SDK_scene_and_warp_alias_references_serialized"] is False,
             "environment: wrong non-PhysX-exact declarations")
    components = _mapping(environment["D0_D7"], "environment.D0_D7")
    _require({"_sensor_mild", "_feedback_delay_mild", "_physics_action_delay", "_spring_pressure",
              "_gas_damping", "_chassis_com", "_explicit_pd", "_mild_dr", "integrated_contact",
              "adapter_baselines_and_dynamic_caches", "actuator_coefficients"} <= set(components),
             "environment.D0_D7: missing component structure")
    _mapping(root["pending_rollout"], "pending_rollout")
    return dict(kind=KIND, run=run, schema_version=5, training_num_envs=20000,
                branch_kind=BRANCH_KIND, source_kind=SOURCE_KIND, task_runtime_overlay=dict(overlay),
                source_checkpoint_sha256=MOTHER_SHA, training_warm_source_receipt=dict(source),
                initialization_branch_metadata=dict(warm), initialization_config=dict(initial_config),
                full_learner_resume=False, inherited_old_iterations=0, bad_candidate_reads=0,
                original_mother_reads=source["physical_byte_opens"],
                base_counters=base_counts, window_counters=window_counts,
                learner_counters=counters, native_counters=native_counts,
                source_N20000_DR_history_sliced=False,
                full_save_structure_checked=True, native_updates_required=bool(require_native_updates),
                external_file_SHA_FINAL_and_parent_wait_verified=False,
                DR_contents_or_PhysX_resume_validated=False, skill_improvement_claim=False)


def extract_pi_state_dict(cpu_learner_state: Mapping[str, Any]) -> dict[str, Tensor]:
    """Return only 14 independently owned FP32 CPU actor/encoder tensors."""
    learner = _mapping(cpu_learner_state, "learner")
    model, _ = _validate_learner(learner)
    out: dict[str, Tensor] = {}
    with torch.inference_mode(False), torch.no_grad():
        for name, shape in PI_SHAPES.items():
            item = model[name]
            _require(isinstance(item, Tensor) and item.device.type == "cpu" and
                     item.dtype == torch.float32 and item.layout == torch.strided and tuple(item.shape) == shape,
                     f"{name}: require exact FP32 CPU shape {shape}")
            _require(bool(torch.isfinite(item).all()), f"{name}: nonfinite weights")
            out[name] = item.detach().contiguous().clone()
    return out


class _MLP(nn.Module):
    def __init__(self, widths: tuple[int, ...]):
        super().__init__()
        layers: list[nn.Module] = []
        for index, (inputs, outputs) in enumerate(zip(widths, widths[1:])):
            layers.append(nn.Linear(inputs, outputs, device="cpu", dtype=torch.float32))
            if index != len(widths) - 2:
                layers.append(nn.ELU())
        self.mlp = nn.Sequential(*layers)

    def forward(self, value: Tensor) -> Tensor:
        return self.mlp(value)


class _PiOnly(nn.Module):
    def __init__(self):
        super().__init__()
        self.actor = _MLP((38, 256, 128, 64, 6))
        self.encoder = _MLP((175, 128, 64, 3))

    def forward(self, history: Tensor) -> Tensor:
        latent = self.encoder(history.reshape(history.shape[0], 175))
        return self.actor(torch.cat((history[:, -1, :], latent), dim=-1))


def _weight_sha(state: Mapping[str, Tensor]) -> str:
    digest = hashlib.sha256()
    for name in sorted(state):
        item = state[name].detach().to(device="cpu", dtype=torch.float32).contiguous()
        digest.update(f"{name}:{tuple(item.shape)}:float32\n".encode("ascii"))
        digest.update(item.numpy().tobytes(order="C"))
    return digest.hexdigest()


class FrozenSequenceMean:
    """initialize(raw35); then repeat act() -> env.step -> observe(raw35, done).

    No critic, log_std, optimizer, training learner, privilege/body-V input or
    training environment/history restoration. Only fresh evaluator observations
    establish history. All public snapshots are detached copies.
    """
    def __init__(self, cpu_checkpoint: Mapping[str, Any], *, device: str | torch.device = "cpu",
                 require_native_updates: bool = True, expected_run: str | None = None):
        self._provenance = validate_checkpoint_provenance(
            cpu_checkpoint, require_native_updates=require_native_updates, expected_run=expected_run)
        selected = extract_pi_state_dict(cpu_checkpoint["learner"])
        self.device = torch.device(device)
        with torch.inference_mode(False), torch.random.fork_rng(devices=[]):
            # Construct FIRST, then strict-load; no random-policy fallback/reconstruction.
            self._network = _PiOnly()
            self._network.load_state_dict(selected, strict=True)
            self._network.requires_grad_(False)
            self._network.eval()
            self._loaded_weight_sha256 = _weight_sha(self._network.state_dict())
            _require(self._loaded_weight_sha256 == _weight_sha(selected), "Strict-loaded weight digest differs")
            self._network.to(self.device)
        self._weight_guards = self._weight_signatures()
        self._history: Tensor | None = None
        self._history_anchor: Tensor | None = None
        self._history_guard: tuple[Any, ...] | None = None
        self._pending_action = False
        self._actions_issued = 0
        self._returned_observations_accepted = 0
        self._num_envs = 0
        self.assert_immutable()

    @staticmethod
    def _signature(tensor: Tensor) -> tuple[Any, ...]:
        return (id(tensor), tensor.data_ptr(), tensor._version, tuple(tensor.shape), tensor.dtype, tensor.device)

    def _weight_signatures(self) -> dict[str, tuple[Any, ...]]:
        return {name: self._signature(parameter) for name, parameter in self._network.named_parameters()}

    @torch.inference_mode(False)
    @torch.no_grad()
    def assert_immutable(self, *, deep: bool = False) -> None:
        """Cheap parameter identity/version guards; history exact guard; optional weight SHA."""
        if self._weight_signatures() != self._weight_guards:
            raise RuntimeError("Frozen actor/encoder identity, device or tensor version changed")
        if any(module.training for module in self._network.modules()) or any(
                p.requires_grad or p.grad is not None for p in self._network.parameters()):
            raise RuntimeError("Frozen actor/encoder mode, requires_grad or gradients changed")
        if self._history is not None:
            if (self._signature(self._history) != self._history_guard or
                    self._history_anchor is None or not torch.equal(self._history, self._history_anchor)):
                raise RuntimeError("Private evaluator history changed outside initialize/observe")
        if deep and _weight_sha(self._network.state_dict()) != self._loaded_weight_sha256:
            raise RuntimeError("Frozen actor/encoder value digest changed")

    def _observations(self, raw35: Tensor, *, first: bool = False) -> Tensor:
        _require(isinstance(raw35, Tensor) and raw35.ndim == 2 and raw35.shape[1] == 35 and
                 raw35.shape[0] > 0 and raw35.is_floating_point(), "raw35: expected floating [N,35] Tensor")
        if not first:
            _require(raw35.shape[0] == self._num_envs, "raw35: evaluation N changed")
        sample = raw35.detach().to(device=self.device, dtype=torch.float32).clone()
        _require(bool(torch.isfinite(sample).all()), "raw35: nonfinite evaluator sample")
        return sample

    def _seal_history(self, history: Tensor) -> None:
        self._history = history
        self._history_anchor = history.detach().clone()
        self._history_guard = self._signature(history)

    @torch.inference_mode(False)
    @torch.no_grad()
    def initialize(self, raw35: Tensor) -> None:
        """Repeat the first actual noisy sample; call once for this evaluator instance."""
        self.assert_immutable()
        if self._history is not None:
            raise RuntimeError("History already initialized; use observe(returned_raw35, done)")
        sample = self._observations(raw35, first=True)
        self._num_envs = sample.shape[0]
        self._seal_history(sample[:, None, :].repeat(1, 5, 1))

    @torch.inference_mode(False)
    @torch.no_grad()
    def act(self) -> Tensor:
        """One deterministic encoder->actor mean, clip[-6,6]; never append history."""
        self.assert_immutable()
        if self._history is None:
            raise RuntimeError("Call initialize(actual_reset_raw35) before act")
        if self._pending_action:
            raise RuntimeError("Action already issued; observe one env.step result before next act")
        output = self._network(self._history).clamp(-6.0, 6.0)
        if not bool(torch.isfinite(output).all()):
            raise FloatingPointError("Frozen actor mean became nonfinite")
        self._pending_action = True
        self._actions_issued += 1
        return output.detach().clone()

    @torch.inference_mode(False)
    @torch.no_grad()
    def observe(self, returned_raw35: Tensor, done: Tensor) -> None:
        """Append exactly once; only done rows repeat their already-returned sample."""
        self.assert_immutable()
        if self._history is None or not self._pending_action:
            raise RuntimeError("observe requires exactly one preceding act and env.step result")
        _require(isinstance(done, Tensor) and done.dtype == torch.bool and
                 tuple(done.shape) == (self._num_envs,), "done: expected boolean [N] termination|timeout")
        sample = self._observations(returned_raw35)
        mask = done.detach().to(self.device)
        history = torch.cat((self._history[:, 1:, :], sample[:, None, :]), dim=1)
        history[mask] = sample[mask, None, :].expand(-1, 5, -1)
        self._seal_history(history)
        self._returned_observations_accepted += 1
        self._pending_action = False

    @torch.inference_mode(False)
    @torch.no_grad()
    def history_snapshot(self) -> Tensor:
        self.assert_immutable()
        if self._history is None:
            raise RuntimeError("History is not initialized")
        return self._history.detach().clone()

    @torch.inference_mode(False)
    @torch.no_grad()
    def weights_snapshot(self) -> dict[str, Tensor]:
        self.assert_immutable()
        return {name: value.detach().to("cpu").clone() for name, value in self._network.state_dict().items()}

    def receipt(self) -> dict[str, Any]:
        self.assert_immutable()
        return dict(adapter="FrozenSequenceMeanV1", device=str(self.device), eval_num_envs=self._num_envs,
                    selected_weight_sha256=self._loaded_weight_sha256,
                    selected_keys=sorted(PI_SHAPES), loaded_before_inference=True,
                    critic_or_optimizer_constructed=False, training_state_restored_or_sliced=False,
                    actions_issued=self._actions_issued,
                    returned_observations_accepted=self._returned_observations_accepted,
                    awaiting_env_step_result=self._pending_action, provenance=copy.deepcopy(self._provenance),
                    independent_native_or_MuJoCo_acceptance_proven=False)

"""One qualified Root7/55afa full learner -> at most 25 NEW N20000 updates.

Import is stdlib-only. Torch/NumPy are supplied by the admitted native worker.
The whole once-decoded CPU root/raw bytes, including unknown fields, remain
strongly immutable. Only learner state enters the unchanged core cloning loader.
The source's empty pending stream and all environment/global RNG stay unapplied.
"""
from __future__ import annotations

from collections.abc import Mapping
import copy
import hashlib
import io
import math
from pathlib import Path
import struct

KIND = "MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1"
BRANCH_KIND = "FDN_FULL_LEARNER_CONTINUATION_55AFA_FRESH_N20000_ENV"
SOURCE_KIND = "fdn_full_learner_resume55afa_n20000_finite25"
INPUT_SCHEMA_VERSION = 7
INPUT_BRANCH_KIND = "FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_LOWSTD005_LRSCALE001"
INPUT_SOURCE_KIND = "fdn_fresh_mlp_warm_1cd_n20000_timeout8_lowstd005_lrscale001"
COUNTER_KEYS = ("updates", "policy_optimizer_steps", "encoder_optimizer_steps", "transitions_seen")
SOURCE_RUN = "MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LRSCHEDULE001_W12_20261105_065201_1793832721176405000"
SOURCE_PIN = dict(
    path="/home/lc01/Zonglin Li/zonglin2/tasks/" + SOURCE_RUN + "/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt",
    sha256="55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7",
    bytes=146247985, run=SOURCE_RUN, source_envs=20000,
    counters=dict(updates=25, policy_optimizer_steps=500, encoder_optimizer_steps=500, transitions_seen=24000000),
    actual_native_policy_steps=1200, unoptimized_pending_controls=0,
    source_training_execution_qualified=True,
)
SOURCE_PRECEDING_BASE = dict(updates=0, policy_optimizer_steps=0, encoder_optimizer_steps=0, transitions_seen=0)
TASK_RUNTIME_SHA = "a84823a59731f9cd805aa0bf6a91af10e0e26e729652df39b8cbd17dc6def3f9"
TASK_RUNTIME_BYTES = 12745
MOTHER_SHA = "1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8"
MOTHER_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt"
MOTHER_BYTES = 14715029
MOTHER_ITER = 43090
# Exactly the known Root7 fields emitted by the actual v8 producer, not Root2.
SOURCE_ROOT_FIELDS = frozenset({
    "kind", "version", "branch_kind", "source_kind", "task_runtime_overlay", "epoch", "reason",
    "resource_binding", "inherited_old_iterations", "full_learner_resume", "bad_candidate_reads",
    "num_envs", "base_counters", "counters", "window_counters", "native_counters_scope",
    "source_checkpoint", "learner", "global_rng", "environment", "pending_rollout", "native_counters",
    "save_is_typed_fullstate_not_native_PhysX_bitwise_resume", "fullstate_required_components_complete",
    "skill_improvement_claim",
})


def need(value, message):
    if not value:
        raise RuntimeError(message)


def validate_source_binding(task):
    """Metadata only, also called BEFORE SDK construction; no path resolution/I/O."""
    source = task["learner_source"]
    need(task.get("source_kind") == SOURCE_KIND, "Finite25 full-learner source_kind required")
    need(isinstance(source, Mapping) and task.get("source_training_execution_qualified") is True and
         source.get("source_training_execution_qualified") is True, "Parent-qualified learner_source metadata required")
    for key, value in SOURCE_PIN.items():
        need(source.get(key) == value, "Selected qualified learner source pin differs: " + key)
    for key in ("bytes", "source_envs", "actual_native_policy_steps", "unoptimized_pending_controls"):
        need(type(source[key]) is int, "Learner source pin requires integer: " + key)
    need(set(source["counters"]) == set(COUNTER_KEYS) and
         all(type(value) is int for value in source["counters"].values()), "Typed source counter pin required")
    return {key: source[key] for key in ("path", "sha256", "bytes", "run")}


class RetainedLearnerSource:
    def __init__(self, task, torch_module, numpy_module):
        self.t, self.np = torch_module, numpy_module
        self.binding = validate_source_binding(task)
        # This is the ONLY physical input-model open/hash/decode in this worker.
        self.raw = Path(self.binding["path"]).read_bytes()
        self.counts = dict(physical_byte_opens=1, SHA_calculations=0, CPU_decodes=0,
                           original_mother_reads=0, current_mother_reads=0, bad_candidate_reads=0, learner_source_reads=1)
        need(len(self.raw) == self.binding["bytes"], "Actual learner source byte size differs")
        digest = hashlib.sha256(self.raw).hexdigest()
        self.counts["SHA_calculations"] += 1
        need(digest == self.binding["sha256"], "Actual learner source FILE SHA differs")
        with self.t.inference_mode(False):
            self.root = self.t.load(io.BytesIO(self.raw), map_location="cpu", weights_only=False)
        self.counts["CPU_decodes"] += 1
        self._validate_root()
        self.base_counters = dict(self.root["learner"]["counters"])
        self._raw_anchor = self.raw
        self._frozen = self._freeze(self.root)
        self.guard_checks = 0
        self.loaded = False
        self.assert_frozen()

    def _validate_root(self):
        root = self.root
        need(isinstance(root, Mapping) and SOURCE_ROOT_FIELDS <= set(root), "Complete actual Root7 save fields required")
        need(root["kind"] == KIND and type(root["version"]) is int and root["version"] == INPUT_SCHEMA_VERSION and
             root["branch_kind"] == INPUT_BRANCH_KIND and root["source_kind"] == INPUT_SOURCE_KIND,
             "Wrong actual Root7 fresh lowstd005/lrschedule001 source schema")
        need(not {"learner_continuation", "ancestral_N4096_checkpoint", "ancestral_mother_checkpoint"}.intersection(root),
             "Actual Root7 fresh source has no full-learner continuation ancestry")
        need(type(root["num_envs"]) is int and root["num_envs"] == 20000 and root["full_learner_resume"] is False and
             type(root["inherited_old_iterations"]) is int and root["inherited_old_iterations"] == 0 and
             type(root["bad_candidate_reads"]) is int and root["bad_candidate_reads"] == 0,
             "Source fresh zero-base initialization metadata differs")
        need(root["fullstate_required_components_complete"] is True and
             root["save_is_typed_fullstate_not_native_PhysX_bitwise_resume"] is True and
             root["skill_improvement_claim"] is False and isinstance(root["reason"], str) and
             bool(root["reason"]) and "error" not in root["reason"].lower(),
             "Source is incomplete or error-path save")
        resource = root["resource_binding"]
        need(isinstance(resource, Mapping) and resource.get("run", resource.get("run_id")) == self.binding["run"],
             "Decoded source run differs")
        if "run" in resource and "run_id" in resource:
            need(resource["run"] == resource["run_id"], "Source run aliases conflict")
        need(resource.get("kind") == KIND and resource.get("version") == INPUT_SCHEMA_VERSION and
             resource.get("branch_kind") == INPUT_BRANCH_KIND and resource.get("source_kind") == INPUT_SOURCE_KIND,
             "Source resource receipt schema differs")
        overlay = root["task_runtime_overlay"]
        need(isinstance(overlay, Mapping) and overlay.get("sha256") == TASK_RUNTIME_SHA and
             overlay.get("bytes") == TASK_RUNTIME_BYTES and isinstance(overlay.get("path"), str) and
             overlay["path"].startswith("/") and overlay["path"].endswith("/e3_fudan_task_runtime_v1.py") and
             resource.get("task_runtime_overlay") == overlay, "Source unchanged training overlay receipt differs")
        learner = root["learner"]
        required_learner = {"config", "model", "main_optimizer", "encoder_optimizer", "counters",
                            "current_learning_rate", "generator_state", "branch_metadata", "format_version"}
        need(isinstance(learner, Mapping) and required_learner <= set(learner) and
             type(learner["format_version"]) is int and learner["format_version"] == 1, "Complete source learner state required")
        need(learner["counters"] == SOURCE_PIN["counters"] and set(learner["counters"]) == set(COUNTER_KEYS) and
             all(type(v) is int for v in learner["counters"].values()), "Decoded source learner counters differ")
        for label, expected in (("base_counters", SOURCE_PRECEDING_BASE), ("window_counters", SOURCE_PIN["counters"]),
                                ("counters", SOURCE_PIN["counters"])):
            counts = root[label]
            need(isinstance(counts, Mapping) and set(counts) == set(COUNTER_KEYS) and counts == expected and
                 all(type(v) is int for v in counts.values()), "Source zero-base/window25 counters differ: " + label)
        need(all(learner["counters"][k] == root["base_counters"][k] + root["window_counters"][k] for k in COUNTER_KEYS),
             "Source cumulative learner counters differ from preceding base plus window")
        cfg = learner["config"]
        fixed = dict(obs_dim=35, history_length=5, privileged_dim=38, latent_dim=3, action_dim=6,
                     initial_std=.05, body_velocity_scale=3.0, rollout_steps=48, gamma=.99, gae_lambda=.95,
                     epochs=5, mini_batches=4, clip_param=.2, value_loss_coef=1.0, entropy_coef=.01,
                     learning_rate=1e-5, encoder_learning_rate=.001, desired_kl=.005,
                     min_learning_rate=1e-7, max_learning_rate=1e-4, main_grad_norm=1.0, encoder_grad_norm=.1)
        hidden = dict(actor_hidden=(256, 128, 64), critic_hidden=(256, 128, 64), encoder_hidden=(128, 64))
        need(isinstance(cfg, Mapping) and set(cfg) == set(fixed) | set(hidden) | {"seed"},
             "Full source PPOConfig dictionary required; no omitted/defaulted STD or LR fields")
        for key, value in fixed.items():
            need(cfg.get(key) == value, "Source algorithm/config differs: " + key)
        for key, value in hidden.items():
            need(type(cfg[key]) is tuple and cfg[key] == value, "Source network capacity differs: " + key)
        need(type(cfg["seed"]) is int, "Source learner-private config seed must be an integer")
        rate = learner["current_learning_rate"]
        need(type(rate) in (int, float) and math.isfinite(rate) and cfg["min_learning_rate"] <= rate <= cfg["max_learning_rate"] and
             math.isclose(rate, 2.562890625e-6, rel_tol=1e-12, abs_tol=0.0), "Source mutable main LR differs from qualified55afa")
        # Only validate the actual learned STD; never replace it by config.initial_std.
        shapes = {"log_std": (6,)}
        names = {}
        for prefix, widths in (("actor", (38, 256, 128, 64, 6)), ("critic", (41, 256, 128, 64, 1)),
                               ("encoder", (175, 128, 64, 3))):
            names[prefix] = []
            for index, (inputs, outputs) in enumerate(zip(widths, widths[1:])):
                for suffix, shape in (("weight", (outputs, inputs)), ("bias", (outputs,))):
                    key = f"{prefix}.mlp.{index * 2}.{suffix}"
                    shapes[key] = shape
                    names[prefix].append(key)
        model = learner["model"]
        need(isinstance(model, Mapping) and set(model) == set(shapes), "Exact full actor/critic/encoder/log_std keys required")
        for key, shape in shapes.items():
            value = model[key]
            need(self.t.is_tensor(value) and value.device.type == "cpu" and value.dtype == self.t.float32 and
                 value.layout == self.t.strided and tuple(value.shape) == shape and bool(self.t.isfinite(value).all()),
                 "Source complete learned tensor differs: " + key)
        for name, parameters, expected_lr in (
            ("main_optimizer", names["actor"] + names["critic"] + ["log_std"], rate),
            ("encoder_optimizer", names["encoder"], cfg["encoder_learning_rate"]),
        ):
            optimizer = learner[name]
            need(isinstance(optimizer, Mapping) and {"state", "param_groups"} <= set(optimizer) and
                 isinstance(optimizer["state"], Mapping) and isinstance(optimizer["param_groups"], (list, tuple)) and
                 len(optimizer["param_groups"]) == 1, "Missing complete source Adam: " + name)
            group = optimizer["param_groups"][0]
            need(isinstance(group, Mapping) and isinstance(group.get("params"), (list, tuple)) and
                 len(group["params"]) == len(parameters) and len(set(group["params"])) == len(parameters) and
                 set(optimizer["state"]) == set(group["params"]) and group.get("lr") == expected_lr,
                 "Source Adam parameter/state/LR binding differs: " + name)
            for parameter, key in zip(group["params"], parameters):
                slot = optimizer["state"][parameter]
                need(isinstance(slot, Mapping) and {"step", "exp_avg", "exp_avg_sq"} <= set(slot),
                     "Incomplete source Adam slot: " + name)
                step = slot["step"]
                if self.t.is_tensor(step):
                    need(step.device.type == "cpu" and step.numel() == 1, "Source Adam step must be a CPU scalar")
                    step = step.item()
                need(type(step) in (int, float) and step == 500, "Source both-Adam500 step differs: " + name)
                for moment in ("exp_avg", "exp_avg_sq"):
                    value = slot[moment]
                    need(self.t.is_tensor(value) and value.device.type == "cpu" and tuple(value.shape) == shapes[key] and
                         bool(self.t.isfinite(value).all()), "Source full Adam moment differs: " + name + "." + moment)
        generator = learner["generator_state"]
        need(self.t.is_tensor(generator) and generator.device.type == "cpu" and generator.dtype == self.t.uint8 and
             generator.ndim == 1 and generator.numel() > 0, "Source complete learner-private generator required")
        branch = learner["branch_metadata"]
        need(isinstance(branch, Mapping) and branch.get("kind") == "NEW_BRANCH_WARM_START" and
             branch.get("inherited_optimizer") is False and branch.get("inherited_iteration") is False,
             "Source learner original MLP-warm metadata differs")
        for key, value in dict(legacy_actor_input=35, legacy_critic_input=38, latent_columns_zero_initialized=True,
                               std_parameterization="new learnable log_std; not copied from legacy").items():
            need(branch.get(key) == value, "Source learner initialization receipt differs: " + key)
        native = root["native_counters"]
        need(isinstance(native, Mapping), "Source current-window native counters required")
        for key, value in dict(actual_native_policy_steps=1200, actual_native_transitions=24000000,
                               physical_callbacks=9600, feedback_callbacks=2400, termination_computations=1200).items():
            need(type(native.get(key)) is int and native[key] == value, "Source N20000 native clock differs: " + key)
        need(root["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
             native["actual_native_policy_steps"] == 48 * root["window_counters"]["updates"],
             "Source optimized controls must use actual source window25/N20000")
        need(isinstance(root["pending_rollout"], Mapping) and not root["pending_rollout"],
             "Qualified55afa has zero pending controls and an empty saved pending mapping")
        # Root7.source_checkpoint IS the full metadata-only 1cd MLP-warm receipt.
        mother = root["source_checkpoint"]
        need(isinstance(mother, Mapping), "Actual source original mother metadata receipt required")
        for key, value in dict(source_path=MOTHER_PATH, source_sha256=MOTHER_SHA, source_bytes=MOTHER_BYTES,
                               source_iter=MOTHER_ITER, physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1).items():
            need(mother.get(key) == value, "Source original mother ancestry differs: " + key)
        for key in ("whole_source_root_and_bytes_retained", "source_tensor_versions_unchanged", "actor_critic_MLP_only",
                    "source_optimizer_and_DR_state_not_restored", "old_iteration_not_inherited"):
            need(mother.get(key) is True, "Source mother warm receipt expected true: " + key)
        ignored = mother.get("ignored_old_exploration_keys")
        need(isinstance(ignored, list) and all(type(key) is str for key in ignored) and len(ignored) == len(set(ignored)) and
             set(ignored) <= {"distribution.std_param", "distribution.log_std_param", "std", "log_std"},
             "Source mother ignored legacy exploration receipt differs")
        rng = root["global_rng"]
        need(isinstance(rng, Mapping) and {"python", "numpy", "torch_cpu", "torch_cuda_all"} <= set(rng),
             "Source full global RNG structure required, retained but never applied")
        environment = root["environment"]
        env_fields = {"root_state_w", "joint_pos", "joint_vel", "body_names", "joint_names", "actual_observations",
                      "history_old_to_new", "recovery", "command_tensors", "command_named_rng_states", "D0_D7",
                      "environment_tensor_caches", "episode_length_buf", "common_step_counter", "sim_step_counter",
                      "feedback_100hz_tick", "action_manager_action", "action_manager_prev_action", "task_stage_summary",
                      "native_PhysX_bitwise_exact_resume", "opaque_SDK_scene_and_warp_alias_references_serialized"}
        need(isinstance(environment, Mapping) and env_fields <= set(environment), "Source full typed environment required")
        root_state = environment["root_state_w"]
        need(self.t.is_tensor(root_state) and root_state.device.type == "cpu" and root_state.ndim >= 1 and
             root_state.shape[0] == 20000, "Source whole N20000 CPU environment population differs")
        need(environment["native_PhysX_bitwise_exact_resume"] is False and
             environment["opaque_SDK_scene_and_warp_alias_references_serialized"] is False,
             "Source environment declarations differ")
        components = environment["D0_D7"]
        need(isinstance(components, Mapping) and {"_sensor_mild", "_feedback_delay_mild", "_physics_action_delay",
             "_spring_pressure", "_gas_damping", "_chassis_com", "_explicit_pd", "_mild_dr", "integrated_contact",
             "adapter_baselines_and_dynamic_caches", "actuator_coefficients"} <= set(components),
             "Source complete D0_D7 structure required, retained but never applied")

    def _tensor_signature(self, value):
        need(value.device.type == "cpu" and value.layout == self.t.strided,
             "Retained source tensors must be CPU strided tensors")
        raw = value.detach().contiguous().reshape(-1).view(self.t.uint8).numpy().tobytes()
        return (value._version, tuple(value.shape), value.dtype, tuple(value.stride()),
                value.storage_offset(), value.data_ptr(), hashlib.sha256(raw).digest())

    def _freeze(self, value):
        if self.t.is_tensor(value):
            return ("tensor", value, self._tensor_signature(value))
        if isinstance(value, Mapping):
            need(all(type(key) in (str, int) for key in value), "Unsupported typed Mapping key")
            return ("mapping", value, type(value), tuple(value), tuple(self._freeze(v) for v in value.values()))
        if type(value) in (list, tuple):
            return ("sequence", value, type(value), tuple(self._freeze(v) for v in value))
        if isinstance(value, self.np.ndarray):
            need(not value.dtype.hasobject, "Object array is outside native typed-save schema")
            return ("array", value, (value.dtype.str, value.shape, value.strides,
                                     hashlib.sha256(value.tobytes(order="C")).digest()))
        if isinstance(value, self.np.generic):
            return ("numpy_scalar", value, type(value), value.tobytes())
        if type(value) is float:
            return ("float", value, struct.pack("!d", value))
        if value is None or type(value) in (bool, int, str, bytes):
            return ("atom", value, type(value))
        if isinstance(value, (self.t.dtype, self.t.device)):
            return ("torch_metadata", value, type(value), str(value))
        raise TypeError("Unsupported retained CPU leaf: " + type(value).__qualname__)

    def _same(self, value, saved):
        tag = saved[0]
        if tag == "tensor":
            need(value is saved[1] and self._tensor_signature(value) == saved[2], "Source CPU tensor changed")
        elif tag == "mapping":
            need(value is saved[1] and type(value) is saved[2] and tuple(value) == saved[3],
                 "Source Mapping/OrderedDict identity/order changed")
            for item, frozen in zip(value.values(), saved[4]):
                self._same(item, frozen)
        elif tag == "sequence":
            need(value is saved[1] and type(value) is saved[2] and len(value) == len(saved[3]), "Source sequence changed")
            for item, frozen in zip(value, saved[3]):
                self._same(item, frozen)
        elif tag == "array":
            now = (value.dtype.str, value.shape, value.strides, hashlib.sha256(value.tobytes(order="C")).digest())
            need(value is saved[1] and now == saved[2], "Source NumPy identity/content changed")
        elif tag == "numpy_scalar":
            need(type(value) is saved[2] and value.tobytes() == saved[3], "Source NumPy scalar changed")
        elif tag == "float":
            need(type(value) is float and struct.pack("!d", value) == saved[2], "Source float bits changed")
        elif tag == "atom":
            need(type(value) is saved[2] and value == saved[1], "Source metadata changed")
        elif tag == "torch_metadata":
            need(type(value) is saved[2] and str(value) == saved[3], "Source Torch metadata changed")
        else:
            raise TypeError("Unknown source guard tag")

    def assert_frozen(self):
        need(self.raw is self._raw_anchor and len(self.raw) == self.binding["bytes"], "Retained source bytes changed")
        self._same(self.root, self._frozen)
        self.guard_checks += 1

    def load_into(self, learner):
        need(not self.loaded, "Learner source may be loaded only once")
        self.assert_frozen()
        learner.load_state_dict(self.root["learner"])  # unchanged core clones its complete input
        self.assert_frozen()
        need(learner.counters == self.base_counters, "Destination counters did not inherit complete learner")
        need(learner.learning_rate == self.root["learner"]["current_learning_rate"], "Destination adaptive LR differs")
        need(self.t.equal(learner.generator.get_state().cpu(), self.root["learner"]["generator_state"]),
             "Destination learner-private generator differs")
        self.loaded = True
        return self.receipt()

    def window_counters(self, learner):
        need(set(learner.counters) == set(COUNTER_KEYS), "Destination learner counter schema differs")
        result = {key: learner.counters[key] - self.base_counters[key] for key in COUNTER_KEYS}
        need(all(type(value) is int and value >= 0 for value in result.values()), "Learner counters regressed below source base")
        return result

    def unknown_root_for_save(self):
        """Copy only unknown root fields; known old env/RNG/pending never enter a new save."""
        return copy.deepcopy({key: value for key, value in self.root.items() if key not in SOURCE_ROOT_FIELDS})

    def learner_state_for_save(self, learner):
        """Keep unknown learner metadata without aliasing; all live known state wins."""
        current = learner.state_dict()
        unknown = copy.deepcopy({key: value for key, value in self.root["learner"].items() if key not in current})
        unknown.update(current)
        return unknown

    def continuation(self):
        controls = self.root["native_counters"]["actual_native_policy_steps"]
        preceding_window = self.root["window_counters"]
        optimized = 48 * preceding_window["updates"]
        return dict(mode="FULL_LEARNER_ONLY_NOT_FULL_ENVIRONMENT_RESUME", source_binding=dict(self.binding),
            source_kind=SOURCE_KIND, source_schema_version=self.root["version"], source_branch_kind=self.root["branch_kind"],
            source_input_source_kind=self.root["source_kind"],
            source_path=self.binding["path"], source_sha256=self.binding["sha256"],
            source_bytes=self.binding["bytes"], source_run=self.binding["run"],
            base_counters=dict(self.base_counters), source_envs=20000, new_envs=20000,
            source_preceding_base_counters=dict(self.root["base_counters"]),
            source_preceding_window_counters=dict(preceding_window),
            fresh_env_history_DR=True, source_env_history_DR_queues_applied=False,
            pending_rollout_discarded_at_stream_cut=True,
            source_native_counters_scope=self.root["native_counters_scope"],
            source_native_policy_steps=controls, source_optimized_control_steps=optimized,
            source_unoptimized_control_steps=controls-optimized,
            source_pending_rollout_completed_control_steps=self.root["pending_rollout"].get("completed_control_steps", 0),
            source_pending_rollout_retained_CPU_but_never_applied=True,
            model_critic_log_std_LR_both_Adam_and_private_generator_continued=True,
            source_global_environment_RNG_restored=False,
            environment_RNG_uses_new_window_fresh_reset_stream=True)

    def ancestral_receipt(self):
        return copy.deepcopy(self.root["source_checkpoint"])

    def receipt(self):
        self.assert_frozen()
        return dict(kind=KIND, version=8, branch_kind=BRANCH_KIND,
            source_path=self.binding["path"], source_sha256=self.binding["sha256"],
            source_bytes=self.binding["bytes"], source_run=self.binding["run"],
            source_kind=SOURCE_KIND, source_schema_version=self.root["version"], source_branch_kind=self.root["branch_kind"],
            source_input_source_kind=self.root["source_kind"],
            source_iter=self.base_counters["updates"], base_counters=dict(self.base_counters),
            **self.counts, whole_source_root_and_bytes_retained=True, unknown_source_fields_retained=True,
            whole_CPU_identity_content_and_versions_unchanged=True, full_CPU_guard_checks=self.guard_checks,
            unknown_root_fields=sorted(set(self.root) - SOURCE_ROOT_FIELDS, key=str),
            unknown_root_and_learner_fields_deep_copied_into_new_saves=True,
            source_envs=20000, new_envs=20000, complete_learner_loaded=self.loaded,
            source_training_execution_qualified=True, full_learner_resume=True, inherited_old_iterations=0,
            source_current_learning_rate=self.root["learner"]["current_learning_rate"],
            source_config_initial_learning_rate=self.root["learner"]["config"]["learning_rate"],
            source_native_policy_steps=1200, source_optimized_control_steps=1200, source_unoptimized_control_steps=0,
            source_environment_DR_history_queues_pending_or_global_RNG_applied=False,
            learner_load_uses_unchanged_core_clone=True, source_optimizer_object_constructed=False)

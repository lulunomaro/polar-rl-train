"""Single qualified N20000 source -> full learner only, fresh timeout8 environment.

Import is stdlib-only. Torch/NumPy are supplied by the admitted native worker.
The entire once-decoded CPU root, including unknown fields and 48 pending steps,
remains retained and strongly immutable. Only root['learner'] is loaded through
the unchanged core's cloning load_state_dict. Ancestors are metadata, never inputs.
"""
from __future__ import annotations

from collections.abc import Mapping
import copy
import hashlib
import io
from pathlib import Path
import struct

KIND = "MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1"
BRANCH_KIND = "FDN_FULL_LEARNER_CONTINUATION_FRESH_N20000_TIMEOUT8_ENV"
SOURCE_KIND = "fdn_n20000_full_learner_timeout8_source"
INPUT_BRANCH_KIND = "FDN_FULL_LEARNER_CONTINUATION_FRESH_N20000_ENV"
COUNTER_KEYS = ("updates", "policy_optimizer_steps", "encoder_optimizer_steps", "transitions_seen")
SOURCE_RUN = "MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W5_ADMISSION2_20261104_204218_1793796138143516800"
SOURCE_PIN = dict(
    path="/home/lc01/Zonglin Li/zonglin2/tasks/" + SOURCE_RUN + "/roles/E3/production/fudan_seq20k_full_u000133_wu000069_c00003360_s0003.pt",
    sha256="8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78",
    bytes=1204250903, run=SOURCE_RUN, source_envs=20000,
    counters=dict(updates=133, policy_optimizer_steps=2660, encoder_optimizer_steps=2660, transitions_seen=78822912),
    actual_native_policy_steps=3360, unoptimized_pending_controls=48,
    source_training_execution_qualified=True,
)
ANCESTOR_4096_RUN = "MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W3_MAPPING_ADMISSION_20261104_185407_1793789647408789000"
ANCESTOR_4096_BINDING = dict(
    path="/home/lc01/Zonglin Li/zonglin2/tasks/" + ANCESTOR_4096_RUN + "/roles/E3/production/fudan_seq_full_u000064_c00003110_s0003.pt",
    sha256="47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d",
    bytes=202962459, run=ANCESTOR_4096_RUN,
)
SOURCE_PRECEDING_BASE = dict(updates=64, policy_optimizer_steps=1280, encoder_optimizer_steps=1280, transitions_seen=12582912)
SOURCE_PRECEDING_WINDOW = dict(updates=69, policy_optimizer_steps=1380, encoder_optimizer_steps=1380, transitions_seen=66240000)
MOTHER_SHA = "1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8"
MOTHER_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt"
MOTHER_BYTES = 14715029
MOTHER_ITER = 43090


def need(value, message):
    if not value:
        raise RuntimeError(message)


def validate_source_binding(task):
    """Metadata only, also called BEFORE SDK construction; no path resolution/I/O."""
    source = task["learner_source"]
    need(task.get("source_kind") == SOURCE_KIND, "New timeout8 full-learner source_kind required")
    need(isinstance(source, Mapping) and task.get("source_training_execution_qualified") is True,
         "Parent-qualified learner_source metadata required")
    for key, value in SOURCE_PIN.items():
        need(source.get(key) == value, "Selected qualified learner source pin differs: " + key)
    return {key: source[key] for key in ("path", "sha256", "bytes", "run")}


class RetainedLearnerSource:
    def __init__(self, task, torch_module, numpy_module):
        self.t, self.np = torch_module, numpy_module
        self.binding = validate_source_binding(task)
        # This is the ONLY physical input-model open/hash/decode in this worker.
        self.raw = Path(self.binding["path"]).read_bytes()
        self.counts = dict(physical_byte_opens=1, SHA_calculations=0, CPU_decodes=0,
                           original_mother_reads=0, ancestor_N4096_reads=0, learner_source_reads=1)
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
        need(isinstance(root, Mapping), "Complete learner source root Mapping required")
        required = {"kind", "version", "branch_kind", "resource_binding", "source_checkpoint", "learner",
                    "global_rng", "environment", "pending_rollout", "native_counters", "reason",
                    "base_counters", "window_counters", "native_counters_scope", "learner_continuation",
                    "inherited_old_iterations", "ancestral_mother_iterations_inherited", "ancestral_mother_checkpoint",
                    "original_mother_reads", "learner_source_reads", "skill_improvement_claim",
                    "fullstate_required_components_complete", "save_is_typed_fullstate_not_native_PhysX_bitwise_resume"}
        need(required <= set(root), "Qualified source is missing complete-save fields")
        need(root["kind"] == KIND and type(root["version"]) is int and root["version"] == 2 and
             root["branch_kind"] == INPUT_BRANCH_KIND, "Wrong source version2 continuation schema")
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
        learner = root["learner"]
        need(isinstance(learner, Mapping) and {"config", "model", "main_optimizer", "encoder_optimizer",
             "counters", "current_learning_rate", "generator_state", "branch_metadata", "format_version"} <= set(learner),
             "Complete source learner state required")
        need(learner["counters"] == SOURCE_PIN["counters"] and set(learner["counters"]) == set(COUNTER_KEYS) and
             all(type(v) is int for v in learner["counters"].values()), "Decoded source learner counters differ")
        cfg = learner["config"]
        for key, value in dict(obs_dim=35, history_length=5, privileged_dim=38, latent_dim=3, action_dim=6,
                               rollout_steps=48, epochs=5, mini_batches=4).items():
            need(cfg.get(key) == value, "Source algorithm/interface differs: " + key)
        need("num_envs" not in cfg, "Learner config unexpectedly binds environment population")
        for name in ("main_optimizer", "encoder_optimizer"):
            optimizer = learner[name]
            need(isinstance(optimizer, Mapping) and {"state", "param_groups"} <= set(optimizer) and
                 bool(optimizer["state"]) and bool(optimizer["param_groups"]), "Missing complete source Adam: " + name)
        need(root["base_counters"] == SOURCE_PRECEDING_BASE and root["window_counters"] == SOURCE_PRECEDING_WINDOW and
             root["inherited_old_iterations"] == SOURCE_PRECEDING_BASE["updates"] and
             root["ancestral_mother_iterations_inherited"] == 0, "Source preceding base/window lineage differs")
        need(all(learner["counters"][k] == root["base_counters"][k] + root["window_counters"][k] for k in COUNTER_KEYS),
             "Source cumulative learner counters differ from preceding base plus window")
        native = root["native_counters"]
        need(isinstance(native, Mapping), "Source current-window native counters required")
        expected_native = dict(actual_native_policy_steps=3360, actual_native_transitions=67200000,
                               physical_callbacks=26880, feedback_callbacks=6720, termination_computations=3360)
        for key, value in expected_native.items():
            need(type(native.get(key)) is int and native[key] == value, "Source N20000 native clock differs: " + key)
        need(root["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
             native["actual_native_policy_steps"] - 48 * root["window_counters"]["updates"] == 48,
             "Source pending controls must use window69, not cumulative133")
        pending = root["pending_rollout"]
        need(isinstance(pending, Mapping) and pending.get("kind") == "partial_T48_rollout" and
             type(pending.get("completed_control_steps")) is int and pending["completed_control_steps"] == 48 and
             isinstance(pending.get("rows"), Mapping), "Source 48 unoptimized pending steps required")
        rows = pending["rows"]
        row_keys = {"obs", "history", "privileged_obs", "body_velocity", "latent", "actions", "rewards", "dones",
                    "time_outs", "values", "log_prob", "mu", "sigma"}
        need(row_keys <= set(rows), "Source retained pending rollout fields missing")
        for key in row_keys:
            need(isinstance(rows[key], (list, tuple)) and len(rows[key]) == 48 and
                 all(self.t.is_tensor(v) and v.device.type == "cpu" and v.ndim >= 1 and v.shape[0] == 20000
                     for v in rows[key]), "Source whole pending rollout structure differs: " + key)
        ancestor = root["source_checkpoint"]
        need(isinstance(ancestor, Mapping), "Source metadata-only N4096 ancestor receipt required")
        ancestor_pin = dict(source_path=ANCESTOR_4096_BINDING["path"], source_sha256=ANCESTOR_4096_BINDING["sha256"],
                            source_bytes=ANCESTOR_4096_BINDING["bytes"], source_run=ANCESTOR_4096_RUN, source_iter=64,
                            source_envs=4096, new_envs=20000, physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1,
                            original_mother_reads=0, learner_source_reads=1)
        for key, value in ancestor_pin.items():
            need(ancestor.get(key) == value, "Source N4096 ancestor pin differs: " + key)
        need(ancestor.get("base_counters") == SOURCE_PRECEDING_BASE and
             type(ancestor.get("full_CPU_guard_checks")) is int and ancestor["full_CPU_guard_checks"] > 0,
             "Source N4096 ancestor base/immutable guard receipt differs")
        for key in ("whole_source_root_and_bytes_retained", "unknown_source_fields_retained",
                    "whole_CPU_identity_content_and_versions_unchanged", "complete_learner_loaded",
                    "learner_load_uses_unchanged_core_clone"):
            need(ancestor.get(key) is True, "Source N4096 ancestor receipt expected true: " + key)
        for key in ("source_environment_DR_history_queues_pending_or_global_RNG_applied", "source_optimizer_object_constructed"):
            need(ancestor.get(key) is False, "Source N4096 ancestor receipt expected false: " + key)
        continuation = root["learner_continuation"]
        need(isinstance(continuation, Mapping), "Source preceding continuation receipt required")
        continuation_pin = dict(mode="FULL_LEARNER_ONLY_NOT_FULL_ENVIRONMENT_RESUME", source_envs=4096, new_envs=20000,
                                source_path=ANCESTOR_4096_BINDING["path"], source_sha256=ANCESTOR_4096_BINDING["sha256"],
                                source_bytes=ANCESTOR_4096_BINDING["bytes"], source_run=ANCESTOR_4096_RUN,
                                source_native_policy_steps=3110, source_optimized_control_steps=3072,
                                source_unoptimized_control_steps=38, source_pending_rollout_completed_control_steps=38)
        for key, value in continuation_pin.items():
            need(continuation.get(key) == value, "Source preceding continuation differs: " + key)
        need(continuation.get("source_binding") == ANCESTOR_4096_BINDING and
             continuation.get("base_counters") == SOURCE_PRECEDING_BASE, "Source preceding continuation binding/base differs")
        for key in ("fresh_env_history_DR", "pending_rollout_discarded_at_stream_cut",
                    "source_pending_rollout_retained_CPU_but_never_applied",
                    "model_critic_log_std_LR_both_Adam_and_private_generator_continued",
                    "environment_RNG_uses_new_window_fresh_reset_stream"):
            need(continuation.get(key) is True, "Source preceding continuation expected true: " + key)
        for key in ("source_env_history_DR_queues_applied", "source_global_environment_RNG_restored"):
            need(continuation.get(key) is False, "Source preceding continuation expected false: " + key)
        mother = root["ancestral_mother_checkpoint"]
        need(isinstance(mother, Mapping), "Source original mother metadata receipt required")
        for key, value in dict(source_path=MOTHER_PATH, source_sha256=MOTHER_SHA, source_bytes=MOTHER_BYTES,
                               source_iter=MOTHER_ITER, actor_critic_MLP_only=True).items():
            need(mother.get(key) == value, "Source original mother ancestry differs: " + key)
        need(root["original_mother_reads"] == 0 and root["learner_source_reads"] == 1,
             "Source version2 window input-read counters differ")
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

    def continuation(self):
        controls = self.root["native_counters"]["actual_native_policy_steps"]
        pending = self.root["pending_rollout"]
        preceding_window = self.root["window_counters"]
        return dict(mode="FULL_LEARNER_ONLY_NOT_FULL_ENVIRONMENT_RESUME", source_binding=dict(self.binding),
            source_kind=SOURCE_KIND, source_schema_version=2, source_branch_kind=INPUT_BRANCH_KIND,
            source_path=self.binding["path"], source_sha256=self.binding["sha256"],
            source_bytes=self.binding["bytes"], source_run=self.binding["run"],
            base_counters=dict(self.base_counters), source_envs=20000, new_envs=20000,
            source_preceding_base_counters=dict(self.root["base_counters"]),
            source_preceding_window_counters=dict(preceding_window),
            fresh_env_history_DR=True, source_env_history_DR_queues_applied=False,
            pending_rollout_discarded_at_stream_cut=True,
            source_native_counters_scope="SOURCE_PRECEDING_N20000_WINDOW_ONLY",
            source_native_policy_steps=controls, source_optimized_control_steps=48*preceding_window["updates"],
            source_unoptimized_control_steps=controls-48*preceding_window["updates"],
            source_pending_rollout_completed_control_steps=pending["completed_control_steps"],
            source_pending_rollout_retained_CPU_but_never_applied=True,
            model_critic_log_std_LR_both_Adam_and_private_generator_continued=True,
            source_global_environment_RNG_restored=False,
            environment_RNG_uses_new_window_fresh_reset_stream=True)

    def ancestral_receipt(self):
        return copy.deepcopy(dict(self.root["ancestral_mother_checkpoint"]))

    def ancestral_4096_receipt(self):
        return copy.deepcopy(dict(self.root["source_checkpoint"]))

    def receipt(self):
        self.assert_frozen()
        return dict(source_path=self.binding["path"], source_sha256=self.binding["sha256"],
            source_bytes=self.binding["bytes"], source_run=self.binding["run"],
            source_kind=SOURCE_KIND, source_schema_version=2, source_branch_kind=INPUT_BRANCH_KIND,
            source_iter=self.base_counters["updates"], base_counters=dict(self.base_counters),
            **self.counts, whole_source_root_and_bytes_retained=True, unknown_source_fields_retained=True,
            whole_CPU_identity_content_and_versions_unchanged=True, full_CPU_guard_checks=self.guard_checks,
            source_envs=20000, new_envs=20000, complete_learner_loaded=self.loaded,
            source_training_execution_qualified=True,
            source_environment_DR_history_queues_pending_or_global_RNG_applied=False,
            learner_load_uses_unchanged_core_clone=True, source_optimizer_object_constructed=False)

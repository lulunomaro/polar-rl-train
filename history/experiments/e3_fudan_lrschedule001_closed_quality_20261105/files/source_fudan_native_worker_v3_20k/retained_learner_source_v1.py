"""Single qualified N4096 source -> full learner only; no source environment resume.

Import is stdlib-only. Torch/NumPy are supplied by the admitted native worker.
The entire once-decoded CPU root, including unknown fields and pending rollout,
remains retained and strongly immutable. Only root['learner'] is loaded through
the unchanged core's cloning load_state_dict. No source optimizer is constructed.
"""
from __future__ import annotations

from collections.abc import Mapping
import copy
import hashlib
import io
from pathlib import Path
import struct

KIND = "MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1"
BRANCH_KIND = "FDN_FULL_LEARNER_CONTINUATION_FRESH_N20000_ENV"
COUNTER_KEYS = ("updates", "policy_optimizer_steps", "encoder_optimizer_steps", "transitions_seen")
SOURCE_RUN = "MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W3_MAPPING_ADMISSION_20261104_185407_1793789647408789000"
SOURCE_PIN = dict(
    path="/home/lc01/Zonglin Li/zonglin2/tasks/" + SOURCE_RUN + "/roles/E3/production/fudan_seq_full_u000064_c00003110_s0003.pt",
    sha256="47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d",
    bytes=202962459, run=SOURCE_RUN, source_envs=4096,
    counters=dict(updates=64, policy_optimizer_steps=1280, encoder_optimizer_steps=1280, transitions_seen=12582912),
)
MOTHER_SHA = "1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8"


def need(value, message):
    if not value:
        raise RuntimeError(message)


def validate_source_binding(task):
    """Metadata only, also called BEFORE SDK construction; no path resolution/I/O."""
    source = task["learner_source"]
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
                           original_mother_reads=0, learner_source_reads=1)
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
                    "fullstate_required_components_complete", "save_is_typed_fullstate_not_native_PhysX_bitwise_resume"}
        need(required <= set(root), "Qualified source is missing complete-save fields")
        need(root["kind"] == KIND and root["version"] == 1 and
             root["branch_kind"] == "NEW_SEQUENCE_PPO_ACTOR_CRITIC_WARM_START", "Wrong source branch schema")
        need(root["fullstate_required_components_complete"] is True and
             root["save_is_typed_fullstate_not_native_PhysX_bitwise_resume"] is True and
             isinstance(root["reason"], str) and "error" not in root["reason"].lower(),
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
        need(learner["counters"] == SOURCE_PIN["counters"] and set(learner["counters"]) == set(COUNTER_KEYS),
             "Decoded source learner counters differ")
        cfg = learner["config"]
        for key, value in dict(obs_dim=35, history_length=5, privileged_dim=38, latent_dim=3, action_dim=6,
                               rollout_steps=48, epochs=5, mini_batches=4).items():
            need(cfg.get(key) == value, "Source algorithm/interface differs: " + key)
        need("num_envs" not in cfg, "Learner config unexpectedly binds environment population")
        native = root["native_counters"]
        controls = native["actual_native_policy_steps"]
        need(type(controls) is int and controls >= 48 * learner["counters"]["updates"],
             "Source native controls do not cover optimized transitions")
        need(native["actual_native_transitions"] == controls * 4096 and
             native["physical_callbacks"] == controls * 8 and native["feedback_callbacks"] == controls * 2 and
             native["termination_computations"] == controls, "Source N4096/8/2 clocks differ")
        # In particular 3110 is NOT required to equal 64*48=3072: 38 steps were pending.
        need(isinstance(root["pending_rollout"], Mapping), "Retained source pending-rollout Mapping required")
        environment = root["environment"]
        need(isinstance(environment, Mapping) and self.t.is_tensor(environment["root_state_w"]) and
             environment["root_state_w"].shape[0] == 4096, "Source environment population differs")
        ancestor = root["source_checkpoint"]
        need(isinstance(ancestor, Mapping) and ancestor.get("source_sha256") == MOTHER_SHA and
             ancestor.get("actor_critic_MLP_only") is True, "Ancestral mother receipt differs")

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
        return dict(mode="FULL_LEARNER_ONLY_NOT_FULL_ENVIRONMENT_RESUME", source_binding=dict(self.binding),
            source_path=self.binding["path"], source_sha256=self.binding["sha256"],
            source_bytes=self.binding["bytes"], source_run=self.binding["run"],
            base_counters=dict(self.base_counters), source_envs=4096, new_envs=20000,
            fresh_env_history_DR=True, source_env_history_DR_queues_applied=False,
            pending_rollout_discarded_at_stream_cut=True,
            source_native_policy_steps=controls, source_optimized_control_steps=48*self.base_counters["updates"],
            source_unoptimized_control_steps=controls-48*self.base_counters["updates"],
            source_pending_rollout_completed_control_steps=pending.get("completed_control_steps", 0),
            source_pending_rollout_retained_CPU_but_never_applied=True,
            model_critic_log_std_LR_both_Adam_and_private_generator_continued=True,
            source_global_environment_RNG_restored=False,
            environment_RNG_uses_new_window_fresh_reset_stream=True)

    def ancestral_receipt(self):
        return copy.deepcopy(dict(self.root["source_checkpoint"]))

    def receipt(self):
        self.assert_frozen()
        return dict(source_path=self.binding["path"], source_sha256=self.binding["sha256"],
            source_bytes=self.binding["bytes"], source_run=self.binding["run"],
            source_iter=self.base_counters["updates"], base_counters=dict(self.base_counters),
            **self.counts, whole_source_root_and_bytes_retained=True, unknown_source_fields_retained=True,
            whole_CPU_identity_content_and_versions_unchanged=True, full_CPU_guard_checks=self.guard_checks,
            source_envs=4096, new_envs=20000, complete_learner_loaded=self.loaded,
            source_environment_DR_history_queues_pending_or_global_RNG_applied=False,
            learner_load_uses_unchanged_core_clone=True, source_optimizer_object_constructed=False)

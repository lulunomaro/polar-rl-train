"""Read-only parent qualification AFTER the original parent's actual child.wait().

API:
    qualify_waited_eval(case_root, task, *, actual_child_pid, actual_parent_pid,
                        returncode, actual_waited) -> JSON-compatible dict

Use the original Popen.pid / os.getpid() / actual wait return value, not values
copied from a worker receipt. This function never waits/reaps/starts a process,
acquires a lock, reads canonical accounting, writes evidence, or opens/stats/
resolves a model. Only six fixed case JSON files and five error sidefiles are
read. task.json ACTUAL BYTES define its SHA; _task_sha256 is never authority.

Runtime dependencies: Python stdlib only. No sibling-module, Torch, SDK, NumPy,
model, parent implementation, stager, fixture or test dependency. Preserve the
already-frozen eight-file native worker closure and original runtime unchanged.
The caller remains responsible for its own error/timeout state, source admission
and original locks; AND this result with those existing parent conditions.

V6's real binding dict has NO close_args/zero_arg field. Both original zero-arg
app.close() callsites are in the already-frozen fudan_frozen_eval_safe.py source
SHA 9d3f5dfe1cbaf955670d87a4315d2c67f19d3c2bd638d175ec29e4cb54fb4e89.
The caller's unchanged stager must bind that source. No invented invocation
witness is accepted here; this qualification is conditional on that source
contract, not independent observation of call arguments or Python fsync calls.
fast_shutdown is checked as its original bool, including False, never forced.
Execution qualification is not a skill/pass-rate or MuJoCo graduation decision.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

KIND = "E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1"
INTERFACE = "fudan_sequence_raw35_history5_latent3_clipped_mean_v1"
INTENT_NAME = "FDN_N80_APP_CLOSE_INTENT.json"
ERROR_NAMES = ("WORKER_ERROR.json", "ENV_CLOSE_ERROR.json", "APP_CLOSE_BINDING_ERROR.json",
               "CLOSE_EVIDENCE_ERROR.json", "APP_CLOSE_ERROR.json")
_JSON_NAMES = ("task.json", "FINAL.json", INTENT_NAME, "WORKER_SCENE_READY.json",
               "WORKER_EVAL_STARTED.json", "PRE_CLOSE.json") + ERROR_NAMES
_MOTHER_SHA = "1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8"
_APP_SHA = "6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903"
_V6_SHA = "3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39"
_ZERO_ARG_ROUTE_SHA = "9d3f5dfe1cbaf955670d87a4315d2c67f19d3c2bd638d175ec29e4cb54fb4e89"
_MOTHER_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt"
_EXCLUDED_TIMEOUT8_SHA = "3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e"
_EXCLUDED_TIMEOUT8_RUN = "MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_CONTINUE133_W6_20261104_231058_1793805058620541900"
_EXCLUDED_TIMEOUT8_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/" + _EXCLUDED_TIMEOUT8_RUN + "/roles/E3/production/fudan_seq20k_full_u000205_wu000072_c00003504_s0003.pt"
_EXCLUDED_PREVIOUS_N20000_SHA = "8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78"
_EXCLUDED_PREVIOUS_N20000_RUN = "MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W5_ADMISSION2_20261104_204218_1793796138143516800"
_EXCLUDED_PREVIOUS_N20000_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/" + _EXCLUDED_PREVIOUS_N20000_RUN + "/roles/E3/production/fudan_seq20k_full_u000133_wu000069_c00003360_s0003.pt"
_EXCLUDED_N4096_SHA = "47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d"
_EXCLUDED_N4096_RUN = "MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W3_MAPPING_ADMISSION_20261104_185407_1793789647408789000"
_EXCLUDED_N4096_PATH = "/home/lc01/Zonglin Li/zonglin2/tasks/" + _EXCLUDED_N4096_RUN + "/roles/E3/production/fudan_seq_full_u000064_c00003110_s0003.pt"
_TRAINING_KIND = "MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1"
_BRANCH_KIND = "FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8"
_SOURCE_KIND = "fdn_fresh_mlp_warm_1cd_n20000_timeout8"
_TRAINING_OVERLAY_SHA = "386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2"
_ALLOWED_APP_MODULES = ("isaacsim.simulation_app.simulation_app", "simulation_app.simulation_app")
_PI_KEYS = sorted([f"actor.mlp.{i}.{k}" for i in (0, 2, 4, 6) for k in ("weight", "bias")] +
                  [f"encoder.mlp.{i}.{k}" for i in (0, 2, 4) for k in ("weight", "bias")])


def _same(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(_same(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(_same(a, b) for a, b in zip(actual, expected))
    return actual == expected


def _sha(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _integer(value, minimum=0):
    return type(value) is int and value >= minimum


def _absolute_path(value, suffix=None):
    # PURE lexical inspection only, including all model-path strings.
    return type(value) is str and bool(value) and any(
        p(value).is_absolute() and (suffix is None or p(value).suffix == suffix)
        for p in (PurePosixPath, PureWindowsPath))


def _public_task(value):
    if not isinstance(value, Mapping):
        raise TypeError("task must be a JSON-compatible Mapping")
    return {key: item for key, item in value.items() if key != "_task_sha256"}


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError("Non-finite JSON constant: " + value)


class _Audit:
    def __init__(self):
        self.checks, self.errors, self.files = {}, [], {}

    def check(self, name, passed, *, actual=None, expected=None, detail=None):
        def plain(value):
            try:
                _canonical(value)
                return value
            except (TypeError, ValueError, OverflowError, RecursionError):
                return {"non_JSON_value_type": type(value).__name__}
        row = dict(passed=bool(passed), actual=plain(actual), expected=plain(expected))
        if detail is not None:
            row["detail"] = str(detail)
        self.checks[name] = row
        if not row["passed"]:
            self.errors.append(dict(check=name, **row))
        return row["passed"]

    def eq(self, name, actual, expected):
        return self.check(name, _same(actual, expected), actual=actual, expected=expected)

    def mapping(self, name, value):
        valid = type(value) is dict
        self.check(name, valid, actual=type(value).__name__, expected="dict")
        return value if valid else {}

    def fields(self, prefix, value, expected):
        for key, item in expected.items():
            self.eq(prefix + "." + key, value.get(key), item)

    def read(self, root, name, *, required=True):
        if name not in _JSON_NAMES:
            raise ValueError("Not a fixed metadata filename")
        path = root / name
        record = self.files[name] = dict(path=str(path), present=None, bytes=None, sha256=None)
        try:
            # Linux parent: do not follow a metadata symlink to another artifact.
            fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "rb") as stream:
                raw = stream.read()
        except FileNotFoundError:
            record["present"] = False
            self.check("file." + name, not required, actual="absent",
                       expected="present" if required else "absent")
            return {}
        except (OSError, ValueError, TypeError) as exc:
            record["read_error"] = type(exc).__name__ + ": " + str(exc)
            self.check("file." + name, False, detail=record["read_error"])
            return {}
        record.update(present=True, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        self.check("file." + name, required, actual="present",
                   expected="present" if required else "absent")
        try:
            value = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_nonfinite)
            return self.mapping("json." + name, value)
        except (ValueError, UnicodeError, TypeError, RecursionError) as exc:
            record["parse_error"] = type(exc).__name__ + ": " + str(exc)
            self.check("json." + name, False, detail=record["parse_error"])
            return {}


def qualify_waited_eval(case_root, task, *, actual_child_pid, actual_parent_pid,
                        returncode, actual_waited) -> dict[str, Any]:
    """Return all checked JSON evidence/failures; do not raise to retry a purpose.

    case_root must be the original parent's absolute, canonical own case path.
    task is its original task Mapping; only child-private _task_sha256 is ignored
    in semantic comparison with disk. No supplied hash replaces actual task bytes.
    Call only after the same original parent's real p.wait() has returned.
    """
    audit = _Audit()
    notes = []
    result = dict(kind="FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V4_FRESH1CD", qualified=False,
        checks=audit.checks, errors=audit.errors, evidence_files=audit.files, notes=notes,
        original_fast_shutdown=None, source_binding=None, task_sha256=None, final_sha256=None,
        no_evidence_files_written_or_deleted=True, model_file_operations=False,
        model_path_resolved_or_statted=False, canonical_accounting_access=False, lock_operations=False,
        Torch_or_SDK_imported_by_this_module=False, actual_wait_performed_by_this_function=False,
        caller_private_task_SHA_used=False, training_owner_close_independently_verified=False,
        parent_own_error_timeout_state_independently_inspected=False,
        skill_improvement_or_graduation_claim=False, independent_MuJoCo_acceptance_proven=False,
        zero_argument_close_route=dict(source="fudan_frozen_eval_safe.py",
            expected_source_sha256=_ZERO_ARG_ROUTE_SHA, positional_arguments=0, keyword_arguments={},
            caller_stager_source_pin_required=True, invocation_arguments_independently_observed=False))

    def finish():
        result["qualified"] = bool(audit.checks) and not audit.errors
        return result

    audit.eq("wait.actual_waited", actual_waited, True)
    audit.check("wait.actual_child_pid", _integer(actual_child_pid, 1), actual=actual_child_pid)
    audit.check("wait.actual_parent_pid", _integer(actual_parent_pid, 1), actual=actual_parent_pid)
    audit.eq("wait.qualifier_runs_in_original_parent", actual_parent_pid, os.getpid())
    audit.eq("wait.returncode", returncode, 0)
    if actual_waited is not True:
        notes.append("No metadata read before actual wait; do not retry/reopen the purpose here.")
        return finish()
    try:
        root = Path(case_root)
        if not audit.check("case.absolute_own_path", root.is_absolute(), actual=str(root)):
            return finish()
        t = audit.read(root, "task.json")
        final = audit.read(root, "FINAL.json")
        intent = audit.read(root, INTENT_NAME)
        ready = audit.read(root, "WORKER_SCENE_READY.json")
        started = audit.read(root, "WORKER_EVAL_STARTED.json")
        preclose = audit.read(root, "PRE_CLOSE.json")
        for name in ERROR_NAMES:
            audit.read(root, name, required=False)
        task_sha = audit.files["task.json"]["sha256"]
        final_sha = audit.files["FINAL.json"]["sha256"]
        result.update(case_root=str(root), task_sha256=task_sha, final_sha256=final_sha)
        try:
            audit.eq("task.caller_public_metadata_matches_actual_file",
                     _canonical(_public_task(task)), _canonical(_public_task(t)))
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            audit.check("task.caller_public_metadata_matches_actual_file", False,
                        detail=type(exc).__name__ + ": " + str(exc))
        audit.fields("task", t, dict(kind=KIND, purpose=KIND, role="E3", num_envs=80,
            controls=160, seed=20260928, optimizer_updates=0, policy_hz=50, feedback_hz=100,
            physics_callbacks=1280, feedback_samples=320,
            physics_dt=.0025, TGS=[32, 4], closure_m=.01, mimic_rad=.01,
            fresh_fullDR_cohort=True, state_projection_or_slicing=False,
            policy_interface=INTERFACE, evaluation_scope="ORIGINAL_E3_74_PLUS_6_NORMAL",
            owner_parent_pid=actual_parent_pid, source_training_execution_qualified=True))
        audit.check("task.group_id", type(t.get("group_id")) is str and bool(t.get("group_id")))
        audit.check("task.GPU_UUID", type(t.get("GPU_UUID")) is str and bool(t.get("GPU_UUID")))
        audit.check("task.no_legacy_RSL_source_keys",
                    not {"source_iteration", "source_Adam17", "source_LR"}.intersection(t))
        ad = audit.mapping("task.actual_group_admission", t.get("actual_group_admission"))
        audit.fields("task.admission", ad, dict(group_id=t.get("group_id"), GPU_UUID=t.get("GPU_UUID"),
            source_SDK_admitted=True, private_GPU_EX_held=True, global_finite_EX_held=True))
        fds = ad.get("inherited_lock_fds")
        audit.check("task.admission.two_recorded_EX_fds", type(fds) is list and len(fds) == 2 and
                    all(_integer(fd, 0) for fd in fds) and fds[0] != fds[1], actual=fds,
                    detail="Descriptor metadata only; original parent retains actual lock authority.")
        binding = dict(path=t.get("source_path"), bytes=t.get("source_bytes"),
                       sha256=t.get("source_SHA"), run=t.get("source_run"))
        result["source_binding"] = binding
        audit.check("source.absolute_path_STRING_only", _absolute_path(binding["path"]))
        audit.check("source.positive_file_bytes_METADATA_only", _integer(binding["bytes"], 1))
        audit.check("source.FILE_SHA_metadata", _sha(binding["sha256"]) and
                    binding["sha256"] not in (_MOTHER_SHA, _EXCLUDED_N4096_SHA,
                                               _EXCLUDED_PREVIOUS_N20000_SHA, _EXCLUDED_TIMEOUT8_SHA))
        audit.check("source.not_old_input_path_STRING_only", type(binding["path"]) is str and
                    os.path.normpath(binding["path"]) not in tuple(os.path.normpath(path) for path in
                        (_MOTHER_PATH, _EXCLUDED_N4096_PATH, _EXCLUDED_PREVIOUS_N20000_PATH, _EXCLUDED_TIMEOUT8_PATH)))
        audit.check("source.run", type(binding["run"]) is str and bool(binding["run"]))
        ids = dict(group_id=t.get("group_id"), GPU_UUID=t.get("GPU_UUID"), role="E3")
        audit.fields("final.identity", final, dict(**ids, kind=KIND, worker_pid=actual_child_pid,
            parent_pid=actual_parent_pid, task_sha256=task_sha))
        audit.fields("intent.identity", intent, dict(**ids,
            kind="FDN_ORIGINAL_N80_PINNED_APP_CLOSE_INTENT_V1", worker_pid=actual_child_pid,
            parent_pid=actual_parent_pid, task_sha256=task_sha, final_path=str(root / "FINAL.json"),
            final_sha256=final_sha, source_binding=binding, controls=160, env_close_returned=True,
            error_before_close=False, close_errors=[],
            parent_actual_wait_RC0_and_final_intent_error_checks_still_required=True))
        audit.fields("ready.identity", ready, dict(**ids, kind=KIND, pid=actual_child_pid,
            parent_pid=actual_parent_pid, zero_controls_before_group_barrier=True))
        audit.fields("started.identity", started, ids)
        audit.fields("preclose", preclose, dict(role="E3", controls=160, controls_expected=160,
            calling_original_env_App_close=True))
        audit.fields("final", final, dict(passed_execution=True, num_envs=80, controls=160,
            seed=20260928, seconds=3.2, physics_callbacks=1280, feedback_samples=320,
            delay_calls={"legs": 1280, "wheels": 1280}, policy_interface=INTERFACE,
            actor_encoder_weights_before_after_exact=True, cached_full_checkpoint_before_after_exact=True,
            live_critic_optimizer_created=False, live_log_std_created=False, live_SequencePPO_created=False,
            optimizer_updates=0, policy_clip_actions=6.0, original_control_clip_actions=6.0,
            source_saved_training_DR_history_applied=False, source_N4096_DR_history_sliced=False,
            canonical_access=False, new_PPO_or_BPTT=False,
            parent_actual_wait_and_close_evidence_still_required=True,
            independent_31body_MuJoCo_acceptance_proven=False))
        for key in ("asset_SHA", "contract_SHA"):
            audit.check("task." + key + ".valid", _sha(t.get(key)))
            audit.eq("final." + key, final.get(key), t.get(key))
        audit.fields("ready", ready, dict(num_envs=80, controls=160, seed=20260928,
            new_nominal_guard_passed=True, one_explicit_fresh_reset=True, physics_dt=.0025,
            policy_dt=.02, feedback_Hz=100, policy_interface=INTERFACE,
            original_recovery_requests=74, normal_envs_excluded_from_recovery_denominator=6,
            new_lowrise_8second_task_enabled=False,
            interface=dict(raw_policy=35, fresh_noisy_history_frames=5, encoder_input=175, latent=3,
                           actor_input=38, critic_observation_logged_only=38, actions=6)))
        audit.fields("ready.observations", audit.mapping("ready.observations", ready.get("observations")),
                     {"policy": [80, 35], "critic": [80, 38]})
        for label, value in (("ready", ready.get("D0_D7_fresh_audit")),
                             ("final.before", final.get("D0_D7_fresh_audit_before")),
                             ("final.after", final.get("D0_D7_fresh_audit_after"))):
            audit.eq(label + ".actual_parameters_pass",
                     audit.mapping(label + ".audit", value).get("actual_parameters_pass"), True)

        caches, policies = [], []
        for label, packet, actions in (("ready", ready, 0), ("final", final, 160)):
            cache = audit.mapping(label + ".source_cache", packet.get("source_cache"))
            policy = audit.mapping(label + ".policy_receipt", packet.get("policy_receipt"))
            caches.append(cache)
            policies.append(policy)
            audit.fields(label + ".cache", cache, dict(source_binding=binding, source_path=binding["path"],
                source_SHA=binding["sha256"], source_bytes=binding["bytes"], source_run=binding["run"],
                physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1,
                selected_new_save_file_bytes_and_SHA_verified=True, source_run_provenance_verified=True,
                whole_root_and_raw_bytes_retained_CPU_only=True, whole_CPU_root_identity_and_content_checked=True,
                live_critic_optimizer_created=False, live_SequencePPO_created=False,
                training_history_DR_optimizer_RNG_applied=False, training_N4096_state_sliced=False,
                training_num_envs=20000, training_N20000_state_sliced=False,
                source_N20000_DR_history_sliced=False, ancestor_N4096_checkpoint_physically_opened=False,
                preceding_N20000_checkpoint_physically_opened=False,
                rejected_timeout8_candidate_checkpoint_physically_opened=False,
                mother_checkpoint_physically_opened=False, external_training_FINAL_actual_wait_verified_by_worker=False))
            audit.check(label + ".cache.full_CPU_guard_checks", _integer(cache.get("full_CPU_guard_checks"), 1))
            digest = cache.get("selected_pi_weight_digest_NOT_file_SHA")
            audit.check(label + ".cache.selected_pi_digest_is_distinct_identity", _sha(digest) and digest != binding["sha256"])
            audit.fields(label + ".policy", policy, dict(adapter="FrozenSequenceMeanV1", eval_num_envs=80,
                selected_weight_sha256=digest, selected_keys=_PI_KEYS, loaded_before_inference=True,
                critic_or_optimizer_constructed=False, training_state_restored_or_sliced=False,
                actions_issued=actions, returned_observations_accepted=actions,
                awaiting_env_step_result=False, independent_native_or_MuJoCo_acceptance_proven=False))
            audit.check(label + ".policy.device", policy.get("device") in ("cuda", "cuda:0"))
            audit.eq(label + ".policy.same_provenance", policy.get("provenance"), cache.get("provenance"))
        audit.eq("weights.before_after_digest", caches[0].get("selected_pi_weight_digest_NOT_file_SHA"),
                 caches[1].get("selected_pi_weight_digest_NOT_file_SHA"))
        audit.eq("source.before_after_provenance", caches[0].get("provenance"), caches[1].get("provenance"))
        audit.eq("source.before_after_saved_Adam_metadata", caches[0].get("saved_new_branch_Adam_metadata"),
                 caches[1].get("saved_new_branch_Adam_metadata"))
        prov = audit.mapping("source.provenance", caches[1].get("provenance"))
        audit.fields("source.provenance", prov, dict(kind=_TRAINING_KIND, run=binding["run"],
            source_checkpoint_sha256=_MOTHER_SHA, schema_version=4,
            branch_kind=_BRANCH_KIND, source_kind=_SOURCE_KIND,
            full_learner_resume=False, inherited_old_iterations=0, bad_candidate_reads=0, original_mother_reads=1,
            training_num_envs=20000, source_N20000_DR_history_sliced=False,
            full_save_structure_checked=True, native_updates_required=True,
            external_file_SHA_FINAL_and_parent_wait_verified=False, DR_contents_or_PhysX_resume_validated=False,
            skill_improvement_claim=False))
        audit.check("source.no_continuation_or_invented_ancestral_receipts",
                    not {"learner_continuation", "ancestral_N4096_checkpoint", "ancestral_mother_checkpoint"}.intersection(prov))
        overlay = audit.mapping("source.training_overlay_METADATA_only", prov.get("task_runtime_overlay"))
        audit.fields("source.training_overlay", overlay, dict(bytes=8571, sha256=_TRAINING_OVERLAY_SHA))
        audit.check("source.training_overlay.absolute_path_STRING_only",
                    _absolute_path(overlay.get("path")) and overlay["path"].endswith("/e3_fudan_task_runtime_v1.py"))
        base = audit.mapping("source.base_counters", prov.get("base_counters"))
        audit.eq("source.exact_base", base, dict(updates=0, policy_optimizer_steps=0,
                 encoder_optimizer_steps=0, transitions_seen=0))
        window = audit.mapping("source.window_counters", prov.get("window_counters"))
        wu0 = window.get("updates")
        audit.check("source.positive_current_window_updates", _integer(wu0, 1), actual=wu0)
        wu = wu0 if _integer(wu0, 1) else 0
        audit.fields("source.current_window", window, dict(updates=wu, policy_optimizer_steps=20*wu,
                     encoder_optimizer_steps=20*wu, transitions_seen=48*20000*wu))
        source = audit.mapping("source.actual_training_warm_source_receipt", prov.get("training_warm_source_receipt"))
        audit.fields("source.current_training_input", source, dict(
                     source_path=_MOTHER_PATH, source_sha256=_MOTHER_SHA, source_bytes=14715029, source_iter=43090,
                     physical_byte_opens=1, SHA_calculations=1, CPU_decodes=1,
                     whole_source_root_and_bytes_retained=True, source_tensor_versions_unchanged=True,
                     actor_critic_MLP_only=True, source_optimizer_and_DR_state_not_restored=True,
                     old_iteration_not_inherited=True))
        ignored = source.get("ignored_old_exploration_keys")
        audit.check("source.ignored_old_exploration_keys_METADATA_only", type(ignored) is list and
                    all(type(key) is str for key in ignored) and len(ignored) == len(set(ignored)) and
                    set(ignored) <= {"distribution.std_param", "distribution.log_std_param", "std", "log_std"})
        warm = audit.mapping("source.initialization_branch_metadata", prov.get("initialization_branch_metadata"))
        audit.fields("source.initialization_branch", warm, dict(kind="NEW_BRANCH_WARM_START",
                     inherited_optimizer=False, inherited_iteration=False, legacy_actor_input=35, legacy_critic_input=38,
                     latent_columns_zero_initialized=True,
                     std_parameterization="new learnable log_std; not copied from legacy"))
        initial_config = audit.mapping("source.initialization_config", prov.get("initialization_config"))
        audit.fields("source.initialization_settings", initial_config,
                     dict(initial_std=.5, learning_rate=.001, encoder_learning_rate=.001))
        learner = audit.mapping("source.learner_counters", prov.get("learner_counters"))
        native = audit.mapping("source.native_counters", prov.get("native_counters"))
        u = wu
        audit.eq("source.current_counts_equal_window", learner, window)
        audit.fields("source.learner", learner, dict(updates=u, policy_optimizer_steps=20*u,
                     encoder_optimizer_steps=20*u, transitions_seen=48*20000*u))
        controls = native.get("actual_native_policy_steps")
        audit.check("source.positive_native_controls", _integer(controls, 1), actual=controls)
        c = controls if _integer(controls, 1) else 0
        audit.fields("source.native", native, dict(actual_native_policy_steps=c,
                     actual_native_transitions=20000*c, physical_callbacks=8*c,
                     feedback_callbacks=2*c, termination_computations=c))
        audit.check("source.native_covers_current_window_and_bounded_partial", wu > 0 and 0 <= c-48*wu <= 48)
        if "expected_learner_counters" in t:
            audit.eq("source.parent_expected_learner_counters", learner, t["expected_learner_counters"])
        if "expected_native_counters" in t:
            expected_native = audit.mapping("task.expected_native_counters", t["expected_native_counters"])
            for key, value in expected_native.items():
                if key in native:
                    audit.eq("source.parent_expected_native." + key, native[key], value)
                else:
                    notes.append("Native key checked by frozen child against whole root, not exposed in five-counter receipt: " + key)
        saved = audit.mapping("source.saved_Adam_metadata", caches[1].get("saved_new_branch_Adam_metadata"))
        for name, count in (("main_optimizer", 20*u), ("encoder_optimizer", 20*u)):
            item = audit.mapping("source.saved_Adam." + name, saved.get(name))
            audit.check("source.saved_Adam." + name + ".nonempty", _integer(item.get("saved_state_entries"), 1))
            audit.fields("source.saved_Adam." + name, item, dict(completed_steps=count,
                optimizer_object_constructed=False, state_restored=False))

        close = audit.mapping("intent.original_bound_close", intent.get("original_bound_close"))
        module = close.get("actual_module")
        audit.check("close.allowed_published_module", module in _ALLOWED_APP_MODULES, actual=module)
        class_id = (module if type(module) is str else "INVALID") + ".SimulationApp"
        expected_close = dict(kind="PINNED_SIMULATIONAPP_CLOSE_BINDING_V5", actual_class=class_id,
            actual_MRO=[class_id, "builtins.object"], close_owner=class_id, actual_module=module,
            actual_type_name="SimulationApp", close_module=module, close_qualname="SimulationApp.close",
            source_bytes=48933, source_SHA256=_APP_SHA, close_firstlineno=848,
            exact_class_verified=True, method_self_is_application=True, method_function_is_MRO_definition=True,
            no_extra_SDK_getters=True, source_code_version="V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES",
            helper_source_bytes=27769, helper_source_SHA256=_V6_SHA)
        audit.fields("close", close, expected_close)
        audit.eq("close.real_V6_keys", sorted(close), sorted(set(expected_close) |
            {"source_file", "module_file", "code_filename", "helper_source_file", "fast_shutdown"}))
        paths = [close.get(key) for key in ("source_file", "module_file", "code_filename")]
        audit.check("close.same_absolute_python_source_paths", all(_absolute_path(p, ".py") for p in paths) and
                    paths[0] == paths[1] == paths[2], actual=paths)
        audit.check("close.absolute_python_helper_path", _absolute_path(close.get("helper_source_file"), ".py"))
        mode = close.get("fast_shutdown")
        audit.check("close.original_fast_shutdown_is_actual_bool", type(mode) is bool, actual=mode,
                    detail="Both original True and original False accepted; no configuration mutation.")
        result["original_fast_shutdown"] = mode if type(mode) is bool else None
        skill = audit.mapping("final.skill", final.get("skill"))
        audit.fields("final.skill", skill, dict(full_expert_graduated=False,
            original_recovery_request_denominator=74, normal_envs_excluded=6,
            no_reset_stitched_credit=True, new_lowrise_8second_task_evaluated=False))
        notes.append("No PT/source file SHA recomputation here: FILE identity is task-to-child-cache binding; 14-weight digest is separate.")
        notes.append("Source training FINAL/wait, parent own error/timeout state and unchanged source pins remain original parent's responsibility.")
    except Exception as exc:
        # Report unexpected schema/IO failures instead of erasing earlier checks
        # or turning an exception into a retry/relaunch of the original purpose.
        audit.check("qualification.unexpected_metadata_error", False,
                    detail=type(exc).__name__ + ": " + str(exc))
    return finish()

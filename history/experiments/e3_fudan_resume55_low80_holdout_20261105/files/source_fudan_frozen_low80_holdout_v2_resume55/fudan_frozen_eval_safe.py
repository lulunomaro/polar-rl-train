"""FDN frozen original-E3 N80 cache/barrier/close evidence; no SDK at import.

No parent, launcher, lock acquisition, training state restore or model selection.
The caller supplies an already qualified complete new FDN save, never mother PT.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import struct
import time
import traceback

KIND = "E3_FDN_FROZEN_LOW80_HOLDOUT_RESUME55_V2"
INTERFACE = "fudan_sequence_raw35_history5_latent3_clipped_mean_v1"
USD = "2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3"
CONTRACT = "bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755"
INTENT_NAME = "FDN_N80_APP_CLOSE_INTENT.json"
ERROR_NAMES = ("WORKER_ERROR.json", "ENV_CLOSE_ERROR.json", "APP_CLOSE_BINDING_ERROR.json",
               "CLOSE_EVIDENCE_ERROR.json", "APP_CLOSE_ERROR.json")


def need(value, message):
    if not value:
        raise ValueError(message)


def put(path, value):
    """Exclusive artifact, durable atomic publication; never replace old evidence."""
    path = Path(path)
    temporary = path.with_name(path.name + ".partial")
    need(not path.exists(), "Own output already exists: " + path.name)
    raw = json.dumps(value, indent=2, allow_nan=False).encode("utf-8")
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(str(path.parent), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def source_binding(task):
    return dict(path=task["source_path"], bytes=task["source_bytes"],
                sha256=task["source_SHA"], run=task["source_run"])


def task_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--group-root", type=Path, required=True)
    args = parser.parse_args()
    raw = args.task.read_bytes()  # JSON only; not a checkpoint
    task = json.loads(raw)
    ad = task["actual_group_admission"]
    fixed = dict(kind=KIND, purpose=KIND, role=task["role"], num_envs=80, controls=400, seed=task["seed"],
                 optimizer_updates=0, policy_hz=50, feedback_hz=100,
                 physics_dt=.0025, TGS=[32, 4], closure_m=.01, mimic_rad=.01,
                 fresh_fullDR_cohort=True, state_projection_or_slicing=False,
                 policy_interface=INTERFACE,
                 evaluation_scope="LOW80_FIVE_POSE16_8S_FULLDR_HOLDOUT_FIRSTEPISODE_CONFIRM")
    need(task["seed"] in (20261002,20261003,20261004) and task["role"] == "E3_LOW80_"+str(task["seed"]), "Explicit independent case/seed binding differs")
    for key, expected in fixed.items():
        need(task.get(key) == expected, "Original N80/task binding differs: " + key)
    need(task["asset_SHA"] == USD and task["contract_SHA"] == CONTRACT, "Asset binding differs")
    need(task["group_id"] == ad["group_id"] and
         os.environ.get("CUDA_VISIBLE_DEVICES") == task["GPU_UUID"] == ad["GPU_UUID"],
         "Actual group/GPU binding differs")
    need(type(task.get("owner_parent_pid")) is int and task["owner_parent_pid"] == os.getppid(),
         "Actual parent PID differs")
    need(ad["source_SDK_admitted"] is True and ad["private_GPU_EX_held"] is True and
         ad["global_finite_EX_held"] is True, "Original finite evaluation admission missing")
    fds = ad["inherited_lock_fds"]
    need(type(fds) is list and len(fds) == len(set(fds)) == 2 and
         all(type(fd) is int for fd in fds), "Two original inherited EX FDs required")
    # Observe the already inherited locks. Do not flock/unlock/open canonical state.
    for fd, name in zip(fds, ("three_expert_v2_" + task["GPU_UUID"] + ".lock",
                              "finite_environment_validation.lock")):
        actual = os.fstat(fd)
        parent = os.stat(f"/proc/{os.getppid()}/fd/{fd}")
        need((actual.st_dev, actual.st_ino) == (parent.st_dev, parent.st_ino),
             "FD differs from actual parent's inherited object")
        need(Path(os.readlink(f"/proc/self/fd/{fd}")).name == name, "Inherited FD identity differs")
        info = Path(f"/proc/self/fdinfo/{fd}").read_text(encoding="utf-8")
        need(any(line.startswith("lock:") and "FLOCK" in line and re.search(r"\bWRITE\b", line)
                 for line in info.splitlines()), "Inherited original EX mode differs")
    group = args.group_root.resolve(strict=True)
    out = args.task.parent.resolve(strict=True)
    need(out.is_relative_to(group) and Path(task["runtime_root"]).resolve(strict=True).is_relative_to(group),
         "Case/runtime is outside own isolated evaluation group")
    need(Path(task["source_path"]).is_absolute() and
         type(task["source_bytes"]) is int and task["source_bytes"] > 0 and
         re.fullmatch(r"[0-9a-f]{64}", task["source_SHA"]) is not None and
         type(task["source_run"]) is str and bool(task["source_run"]),
         "Parent must bind complete selected new save path/bytes/SHA/run")
    need(task.get("source_training_execution_qualified") is True,
         "Parent has not qualified selected new save's original training close/wait")
    need(not {"source_Adam17", "source_LR", "source_iteration"}.intersection(task),
         "Legacy RSL iteration/17Adam source fields do not describe this new branch")
    deadline = task["absolute_worker_deadline_epoch"]
    need(type(deadline) in (int, float) and math.isfinite(deadline) and time.time() < deadline,
         "Evaluation deadline is not current")
    task["_task_sha256"] = hashlib.sha256(raw).hexdigest()
    return task, out, group


class WholeFDNCheckpointCache:
    """One physical read/hash/CPU decode, retained whole CPU root plus raw bytes.

    Full CPU leaves are inspected ONLY for provenance and content immutability.
    No training environment/RNG/history/optimizer is sliced, applied or restored.
    """
    def __init__(self, torch_module, task):
        import numpy as np
        from frozen_sequence_mean import (validate_checkpoint_provenance, MOTHER_PATH, MOTHER_SHA,
                                          EXCLUDED_TIMEOUT8_PATH, EXCLUDED_TIMEOUT8_SHA,
                                          EXCLUDED_PREVIOUS_N20000_PATH, EXCLUDED_PREVIOUS_N20000_SHA,
                                          EXCLUDED_N4096_PATH, EXCLUDED_N4096_SHA, EXCLUDED_FRESH25_PATH, EXCLUDED_FRESH25_SHA, EXCLUDED_HEIGHTGATE_PATH, EXCLUDED_HEIGHTGATE_SHA, EXCLUDED_LOWSTD005_PATH, EXCLUDED_LOWSTD005_SHA, EXCLUDED_SOURCE55_PATH, EXCLUDED_SOURCE55_SHA)
        self.t, self.np = torch_module, np
        self.binding = source_binding(task)
        # Lexical exclusion BEFORE the only selected-model read; no old-input stat/resolve/open.
        need(os.path.normpath(self.binding["path"]) not in
             tuple(os.path.normpath(path) for path in (MOTHER_PATH, EXCLUDED_N4096_PATH,
                                                     EXCLUDED_PREVIOUS_N20000_PATH, EXCLUDED_TIMEOUT8_PATH, EXCLUDED_FRESH25_PATH, EXCLUDED_HEIGHTGATE_PATH, EXCLUDED_LOWSTD005_PATH, EXCLUDED_SOURCE55_PATH)) and
             self.binding["sha256"] not in (MOTHER_SHA, EXCLUDED_N4096_SHA,
                                           EXCLUDED_PREVIOUS_N20000_SHA, EXCLUDED_TIMEOUT8_SHA, EXCLUDED_FRESH25_SHA, EXCLUDED_HEIGHTGATE_SHA, EXCLUDED_LOWSTD005_SHA, EXCLUDED_SOURCE55_SHA),
             "Selected Root8 continuation save must not be 1cd, 47937, 8af4, 3e64, 246ac6, bf824, cc41 or source55 old input")
        self.raw = Path(self.binding["path"]).read_bytes()
        self.counts = dict(physical_byte_opens=1, SHA_calculations=0, CPU_decodes=0)
        need(len(self.raw) == self.binding["bytes"], "Selected new save byte size differs")
        digest = hashlib.sha256(self.raw).hexdigest()
        self.counts["SHA_calculations"] += 1
        need(digest == self.binding["sha256"], "Selected new save FILE SHA differs")
        with self.t.inference_mode(False):
            self.root = self.t.load(io.BytesIO(self.raw), map_location="cpu", weights_only=False)
        self.counts["CPU_decodes"] += 1
        self.provenance = validate_checkpoint_provenance(
            self.root, require_native_updates=True, expected_run=self.binding["run"])
        if "expected_learner_counters" in task:
            need(task["expected_learner_counters"] == self.provenance["learner_counters"],
                 "Selected save learner counters differ from parent binding")
        if "expected_native_counters" in task:
            for key, expected in task["expected_native_counters"].items():
                need(self.root["native_counters"].get(key) == expected,
                     "Selected save native counters differ from parent binding: " + key)
        self.saved_adam_metadata = self._adam_metadata()
        self._raw_anchor = self.raw
        self._frozen = self._freeze(self.root)
        self.deep_checks = 0
        self.policy_created = False
        self.policy_weight_digest = None
        self.check()

    def _adam_metadata(self):
        """Read saved scalar metadata, not Adam objects or a legacy RSL17 rule."""
        result = {}
        for name, count_name in (("main_optimizer", "policy_optimizer_steps"),
                                 ("encoder_optimizer", "encoder_optimizer_steps")):
            optimizer = self.root["learner"][name]
            state, groups = optimizer["state"], optimizer["param_groups"]
            need(isinstance(state, Mapping) and isinstance(groups, (list, tuple)) and bool(groups),
                 "Missing saved new-branch Adam metadata: " + name)
            ids = [index for group in groups for index in group["params"]]
            need(bool(ids) and all(type(index) is int for index in ids) and
                 len(ids) == len(set(ids)) and set(state) == set(ids),
                 "Saved Adam parameter IDs/state entries differ: " + name)
            expected = self.provenance["learner_counters"][count_name]
            for entry in state.values():
                need(isinstance(entry, Mapping) and {"step", "exp_avg", "exp_avg_sq"} <= set(entry),
                     "Incomplete saved Adam slots: " + name)
                step = entry["step"]
                if self.t.is_tensor(step):
                    need(step.device.type == "cpu" and step.numel() == 1,
                         "Saved Adam step is not a CPU scalar")
                    step = step.item()
                need(type(step) in (int, float) and math.isfinite(step) and step == expected,
                     "Saved Adam steps disagree with completed new-branch counters: " + name)
            result[name] = dict(saved_state_entries=len(state), completed_steps=expected,
                                optimizer_object_constructed=False, state_restored=False)
        return result

    def _tensor_signature(self, value):
        need(value.device.type == "cpu" and value.layout == self.t.strided,
             "Whole saved root must contain CPU strided tensors only")
        raw = value.detach().contiguous().reshape(-1).view(self.t.uint8).numpy().tobytes()
        return (value._version, tuple(value.shape), value.dtype, tuple(value.stride()),
                value.storage_offset(), value.data_ptr(), hashlib.sha256(raw).digest())

    def _freeze(self, value):
        if self.t.is_tensor(value):
            return ("tensor", value, self._tensor_signature(value))
        if isinstance(value, Mapping):
            need(all(type(key) in (str, int) for key in value), "Unknown saved mapping key type")
            return ("mapping", value, type(value), tuple(value),
                    tuple(self._freeze(item) for item in value.values()))
        if type(value) in (list, tuple):
            return ("sequence", value, type(value), tuple(self._freeze(item) for item in value))
        if isinstance(value, self.np.ndarray):
            need(not value.dtype.hasobject, "Object-array checkpoint leaf is outside typed save")
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
        raise TypeError("Unknown typed CPU checkpoint leaf: " + type(value).__qualname__)

    def _same(self, value, frozen):
        tag = frozen[0]
        if tag == "tensor":
            need(value is frozen[1] and self._tensor_signature(value) == frozen[2],
                 "Cached whole CPU tensor identity/content/version changed")
        elif tag == "mapping":
            need(value is frozen[1] and type(value) is frozen[2] and tuple(value) == frozen[3],
                 "Cached Mapping/OrderedDict identity/order changed")
            for item, saved in zip(value.values(), frozen[4]):
                self._same(item, saved)
        elif tag == "sequence":
            need(value is frozen[1] and type(value) is frozen[2] and len(value) == len(frozen[3]),
                 "Cached CPU sequence changed")
            for item, saved in zip(value, frozen[3]):
                self._same(item, saved)
        elif tag == "array":
            now = (value.dtype.str, value.shape, value.strides,
                   hashlib.sha256(value.tobytes(order="C")).digest())
            need(value is frozen[1] and now == frozen[2], "Cached CPU numpy array changed")
        elif tag == "numpy_scalar":
            need(type(value) is frozen[2] and value.tobytes() == frozen[3], "Cached numpy scalar changed")
        elif tag == "float":
            need(type(value) is float and struct.pack("!d", value) == frozen[2], "Cached float changed")
        elif tag == "atom":
            need(type(value) is frozen[2] and value == frozen[1], "Cached metadata changed")
        elif tag == "torch_metadata":
            need(type(value) is frozen[2] and str(value) == frozen[3], "Cached Torch metadata changed")
        else:
            raise TypeError("Unknown CPU guard tag")

    def check(self):
        need(self.raw is self._raw_anchor and len(self.raw) == self.binding["bytes"],
             "Retained selected new save bytes changed")
        self._same(self.root, self._frozen)
        self.deep_checks += 1
        return True

    def policy(self, device):
        from frozen_sequence_mean import FrozenSequenceMean
        need(not self.policy_created, "Only one frozen pi runtime per evaluator")
        policy = FrozenSequenceMean(self.root, device=device, require_native_updates=True,
                                    expected_run=self.binding["run"])
        self.policy_created = True
        self.policy_weight_digest = policy.receipt()["selected_weight_sha256"]
        self.check_policy(policy)
        return policy

    def check_policy(self, policy):
        policy.assert_immutable(deep=True)
        need(policy.receipt()["selected_weight_sha256"] == self.policy_weight_digest,
             "Frozen selected policy weight digest changed")
        return self.check()

    def receipt(self):
        return dict(source_binding=dict(self.binding), source_path=self.binding["path"],
                    source_SHA=self.binding["sha256"], source_bytes=self.binding["bytes"],
                    source_run=self.binding["run"], **self.counts,
                    selected_new_save_file_bytes_and_SHA_verified=True, source_run_provenance_verified=True,
                    whole_root_and_raw_bytes_retained_CPU_only=True,
                    whole_CPU_root_identity_and_content_checked=self.deep_checks > 0,
                    full_CPU_guard_checks=self.deep_checks, provenance=self.provenance,
                    saved_new_branch_Adam_metadata=self.saved_adam_metadata,
                    live_critic_optimizer_created=False, live_SequencePPO_created=False,
                    selected_pi_weight_digest_NOT_file_SHA=self.policy_weight_digest,
                    training_history_DR_optimizer_RNG_applied=False,
                    training_N4096_state_sliced=False, mother_checkpoint_physically_opened=False,
                    training_num_envs=20000, training_N20000_state_sliced=False,
                    source_N20000_DR_history_sliced=False,
                    ancestor_N4096_checkpoint_physically_opened=False,
                    preceding_N20000_checkpoint_physically_opened=False,
                    rejected_timeout8_candidate_checkpoint_physically_opened=False,
                     source55_checkpoint_physically_opened=False,
                    external_training_FINAL_actual_wait_verified_by_worker=False)


def wait_start(task, out, group, ready):
    """Original 900s ready barrier, only the one E3 member; no early controls."""
    put(out / "WORKER_SCENE_READY.json", dict(group_id=task["group_id"], GPU_UUID=task["GPU_UUID"],
        role=task["role"], pid=os.getpid(), parent_pid=os.getppid(), epoch=time.time(),
        zero_controls_before_group_barrier=True, **ready))
    until = min(task["absolute_worker_deadline_epoch"], time.time() + 900)
    while time.time() < until:
        if (group / "GROUP_ABORT.json").exists():
            raise RuntimeError("Own single-E3 evaluation group startup aborted")
        path = group / "GROUP_EVAL_START.json"
        if path.exists():
            value = json.loads(path.read_bytes())
            need(value["group_id"] == task["group_id"] and value["GPU_UUID"] == task["GPU_UUID"] and
                 value["all_members_ready"] is True and value["members"] == task["eval_members"] and len(value["members"]) == 3 and task["role"] in value["members"],
                 "Single original-E3 ready barrier binding differs")
            put(out / "WORKER_EVAL_STARTED.json", dict(epoch=time.time(), GPU_UUID=task["GPU_UUID"],
                role=task["role"], group_id=task["group_id"]))
            return value
        time.sleep(.1)
    raise TimeoutError("Original single-E3 ready barrier expired without stepping")


def close_original_resources(task, out, env, namespace, cache, execution_error, *, controls_completed):
    """No SM FINAL validator; use only V6's exact application Python pinner.

    Outer owner still actually child.wait()s and binds FINAL/intent/error absence.
    Failed evidence never qualifies, but original close cleanup is still attempted.
    """
    failures = []

    def record(name, label):
        failures.append(label + ": " + traceback.format_exc())
        try:
            put(out / name, dict(epoch=time.time(), error=failures[-1], SystemExit_is_not_completion=True))
        except BaseException:
            failures.append("error receipt publication failed: " + traceback.format_exc())

    env_closed = False
    if env is not None:
        try:
            put(out / "PRE_CLOSE.json", dict(epoch=time.time(), role=task["role"], controls=controls_completed,
                controls_expected=400, calling_original_env_App_close=True))
        except BaseException:
            record("CLOSE_EVIDENCE_ERROR.json", "PRE_CLOSE evidence")
        try:
            env.close()
            env_closed = True
        except BaseException:
            record("ENV_CLOSE_ERROR.json", "env.close")
    if namespace is None:
        if failures and not execution_error:
            raise RuntimeError(failures[-1])
        return
    app = namespace["app"]
    try:
        from app_close_semantics_v6 import _pin_original_app_close
        binding = _pin_original_app_close(app)
    except BaseException:
        binding = None
        record("APP_CLOSE_BINDING_ERROR.json", "original close binding")
    intent = None
    if not execution_error and not failures:
        try:
            need(env_closed and cache is not None and binding is not None,
                 "Successful original resources/cache/binding missing")
            cache.check()  # CPU only; no observation/SDK/GPU work after env.close
            raw = (out / "FINAL.json").read_bytes()
            final = json.loads(raw)
            need(final["kind"] == KIND and final["passed_execution"] is True and
                 final["group_id"] == task["group_id"] and final["GPU_UUID"] == task["GPU_UUID"] and
                 final["role"] == task["role"] and final["controls"] == controls_completed == 400 and final["num_envs"] == 80 and
                 final["worker_pid"] == os.getpid() and final["parent_pid"] == os.getppid() and
                 final["task_sha256"] == task["_task_sha256"] and
                 final["source_cache"]["source_binding"] == source_binding(task),
                 "Actual FINAL/task/selected complete save binding differs")
            need(not any((out / name).exists() for name in ERROR_NAMES), "Own error evidence exists")
            intent = dict(kind="FDN_ORIGINAL_N80_PINNED_APP_CLOSE_INTENT_V1", epoch=time.time(),
                group_id=task["group_id"], GPU_UUID=task["GPU_UUID"], role=task["role"],
                worker_pid=os.getpid(), parent_pid=os.getppid(), task_sha256=task["_task_sha256"],
                final_path=str(out / "FINAL.json"), final_sha256=hashlib.sha256(raw).hexdigest(),
                source_binding=source_binding(task), original_bound_close=binding,
                env_close_returned=True, error_before_close=False, close_errors=[], controls=400,
                parent_actual_wait_RC0_and_final_intent_error_checks_still_required=True)
        except BaseException:
            record("CLOSE_EVIDENCE_ERROR.json", "FINAL/close evidence")
    if intent is not None:
        try:
            put(out / INTENT_NAME, intent)
        except BaseException:
            record("CLOSE_EVIDENCE_ERROR.json", "durable close intent publication")
        else:
            try:
                app.close()  # immediate original zero-argument call; configuration unchanged
            except BaseException:
                record("APP_CLOSE_ERROR.json", "original app.close")
                raise
            return
    # Failure cleanup is never a qualifying intent or success substitution.
    try:
        app.close()
    except BaseException:
        record("APP_CLOSE_ERROR.json", "failure cleanup app.close")
        if not execution_error:
            raise
    if failures and not execution_error:
        raise RuntimeError("Original resource close did not qualify: " + failures[-1])

"""One bounded metadata-only observer of the own frozen original E3 group.
Adapted from collect_e3_frozen_once.py; consume the parent's actual wait qualification.
No model/old raw/JSONL/canonical reads, skill grade, reset stitching, signals or replay.
"""
from pathlib import Path, PurePosixPath
import json
import sys
import time

PREFIX = "FDNN20000_FROZEN_"
TASKS = "/home/lc01/Zonglin Li/zonglin2/tasks"
CAP_SECONDS = 4500
INTERVAL_SECONDS = 15
OUTER_DISPATCH = PREFIX + "OUTER_DISPATCH.json"
OUTER_WAIT = PREFIX + "PARENT_WAITED_ACTUAL.json"
NAMES = (
    "PARENT_STARTED.json", "CHILDREN.json", "ACTUAL_GROUP_ADMISSION.json",
    "BOUNDED_ORIGINAL_RESOURCE_WAIT.json", "GROUP_BARRIER_STATUS.json", "GROUP_EVAL_START.json",
    "FINAL.json", "TERMINAL_ROWS.json", "PARENT_EXIT_SCOPE.json", "PARENT_ORIGINAL_ERROR.json",
    "GROUP_ABORT.json", "GROUP_STARTUP_ABORT.json", OUTER_DISPATCH, OUTER_WAIT,
    "cases/E3/task.json", "cases/E3/FRESH80_FULLDR_BEFORE_CONTROL.json",
    "cases/E3/WORKER_SCENE_READY.json", "cases/E3/WORKER_EVAL_STARTED.json", "cases/E3/PRE_CLOSE.json",
    "cases/E3/FINAL.json", "cases/E3/FDN_N80_APP_CLOSE_INTENT.json", "cases/E3/WORKER_ERROR.json",
    "cases/E3/ENV_CLOSE_ERROR.json", "cases/E3/APP_CLOSE_BINDING_ERROR.json",
    "cases/E3/CLOSE_EVIDENCE_ERROR.json", "cases/E3/APP_CLOSE_ERROR.json",
)
ERROR_NAMES = (
    "PARENT_ORIGINAL_ERROR.json", "GROUP_ABORT.json", "GROUP_STARTUP_ABORT.json",
    "cases/E3/WORKER_ERROR.json", "cases/E3/ENV_CLOSE_ERROR.json", "cases/E3/APP_CLOSE_BINDING_ERROR.json",
    "cases/E3/CLOSE_EVIDENCE_ERROR.json", "cases/E3/APP_CLOSE_ERROR.json",
)
LOG_NAMES = ("OUTER_STDOUT_STDERR.log", "GROUP_SUPERVISOR_STDOUT_STDERR.log", "cases/E3/SDK_FULL_STDOUT_STDERR.log")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    D = Path(__file__).resolve().parent
    stage = json.loads((D / (PREFIX + "STAGE_RESULT.json")).read_bytes())
    dispatch = json.loads((D / (PREFIX + "DISPATCH_RESULT.json")).read_bytes())
    plan = json.loads((D / (PREFIX + "GROUP_PLAN_SOURCE.json")).read_bytes())
    root = stage["root"]
    p = PurePosixPath(root)
    need(type(stage["returncode"]) is type(dispatch["returncode"]) is int and
         stage["returncode"] == dispatch["returncode"] == 0 and stage["roles"] == dispatch["roles"] == ["E3"] and
         stage["num_envs"] == 80 and stage["controls"] == 160 and stage["seed"] == 20260928 and
         stage["source_training_num_envs"] == 20000 and stage["assessment_dispatched"] is False and
         p.parent == PurePosixPath(TASKS) and ".." not in p.parts and
         p.name == plan["group_id"] and p.name.startswith(PREFIX + "ORIGINAL_N80_") and
         dispatch["root"] == dispatch["dispatch"]["root"] == root and
         dispatch["dispatch"]["roles"] == ["E3"] and dispatch["dispatch"]["original_parent_Popen_calls"] == 1 and
         plan["GPU_UUID"] == stage["GPU_UUID"] == dispatch["GPU_UUID"] and
         len(plan["roles"]) == 1 and plan["roles"][0]["role"] == "E3" and plan["roles"][0]["controls"] == 160,
         "Actual dispatched own one-E3 original N80/160 group required")
    role = plan["roles"][0]
    expected_source = dict(path=role["source_path"], bytes=role["source_bytes"], sha256=role["source_SHA"], run=role["source_run"])
    need(expected_source == stage["source"] == dispatch["source"] and
         role["evaluation_scope"] == "ORIGINAL_E3_74_PLUS_6_NORMAL" and
         role["runtime_root"] == root + "/runtimes/E3", "Own selected-source/scope metadata differs")
    marker = D / (PREFIX + "OBSERVER_STARTED_ONCE.json")
    closed_path = D / (PREFIX + "CLOSED_RESULT.json")
    timeout_path = D / (PREFIX + "OBSERVER_TIMEOUT.json")
    scope_path = D / (PREFIX + "ORIGINAL_SCOPE_RESULT.json")
    need(not any(path.exists() for path in (marker, closed_path, timeout_path, scope_path)), "One unused bounded observer required")
    with marker.open("x", encoding="utf8") as stream:
        json.dump(dict(epoch=time.time(), root=root, roles=["E3"], cap_seconds=CAP_SECONDS,
            interval_seconds=INTERVAL_SECONDS, JSON_metadata_and_terminal_stdout_tails_only=True,
            models_raw_JSONL_or_canonical_access=False), stream, indent=2)
    sys.path.insert(0, str(D.parent / "mod4v1_experts_fulldr_rm70_20261101"))
    from project_connector import connect72
    c = s = None
    start = time.monotonic()
    last = None
    try:
        c = connect72()
        s = c.open_sftp()
        s.get_channel().settimeout(30)  # Bound each own metadata/tail I/O; no parent deadline change.

        def read(name):
            need(name in NAMES and name.endswith(".json"), "Own metadata whitelist only")
            try:
                size = s.stat(root + "/" + name).st_size
                need(size < 8 * 1024 * 1024, "Own JSON metadata exceeds original 8MiB bound: " + name)
                with s.open(root + "/" + name, "rb") as stream:
                    raw = stream.read(8 * 1024 * 1024 + 1)
                need(len(raw) < 8 * 1024 * 1024, "Growing JSON metadata exceeds original bound: " + name)
                return json.loads(raw)
            except FileNotFoundError:
                return None

        def terminal_tails():
            tails = {}
            for name in LOG_NAMES:
                try:
                    size = s.stat(root + "/" + name).st_size
                    with s.open(root + "/" + name, "rb") as stream:
                        stream.seek(max(0, size - 8192))
                        raw = stream.read(8192)
                    tails[name] = dict(observed_file_bytes=size, tail_bytes_read=len(raw),
                        tail_utf8=raw.decode("utf8", "replace"))
                except FileNotFoundError:
                    tails[name] = None
            return tails

        def waited(metadata):
            outer = metadata[OUTER_WAIT]
            return isinstance(metadata["PARENT_EXIT_SCOPE.json"], dict) and isinstance(outer, dict) and \
                outer.get("actual_parent_p_wait_returned") is True and outer.get("original_parent_reaped") is True

        while True:
            m = {name: read(name) for name in NAMES}
            closed = waited(m)
            if closed:
                # Parent and controller actually exited: refresh immutable own results once before reporting.
                m = {name: read(name) for name in NAMES}
                closed = waited(m)
            key = (m["ACTUAL_GROUP_ADMISSION.json"] is not None, m["GROUP_EVAL_START.json"] is not None, closed)
            current = dict(epoch=time.time(), root=root, roles=["E3"], closed=closed, metadata=m,
                model_or_raw_or_JSONL_or_canonical_access=False, observer_did_not_signal_or_extend_parent=True)
            temp = D / (PREFIX + "CURRENT.tmp")
            temp.write_text(json.dumps(current, indent=2, allow_nan=False), encoding="utf8")
            temp.replace(D / (PREFIX + "CURRENT.json"))
            if key != last:
                print("FDNN20000_FROZEN_PROGRESS " + json.dumps(dict(roles=["E3"], admitted=key[0], common_start=key[1], closed=closed)), flush=True)
                last = key
            if closed:
                group, terminal = m["FINAL.json"], m["TERMINAL_ROWS.json"]
                f, task = m["cases/E3/FINAL.json"], m["cases/E3/task.json"]
                end, outer = m["PARENT_EXIT_SCOPE.json"], m[OUTER_WAIT]
                # Consume only already-produced FDN qualification; it is nested, not a fictitious case JSON.
                row = terminal[0] if isinstance(terminal, list) and len(terminal) == 1 and isinstance(terminal[0], dict) else None
                qualification = row.get("fdn_wait_qualification") if isinstance(row, dict) else None
                child_waits = end.get("child_waits")
                child_wait = child_waits[0] if isinstance(child_waits, list) and len(child_waits) == 1 else None
                parent_started = m["PARENT_STARTED.json"]
                checks = dict(
                    original_parent_terminal_passed=isinstance(row, dict) and row.get("role") == "E3" and
                        row.get("passed_execution") is True and row.get("actual_waited") is True and row.get("returncode") == 0,
                    FDN_actual_wait_qualified=isinstance(qualification, dict) and qualification.get("qualified") is True and
                        qualification.get("errors") == [] and qualification.get("kind") == "FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V2_N20000",
                    group_one_E3_matches_actual_terminal=isinstance(group, dict) and group.get("group_id") == plan["group_id"] and
                        group.get("GPU_UUID") == stage["GPU_UUID"] and group.get("rows") == terminal and
                        isinstance(terminal, list) and len(terminal) == 1,
                    actual_case_final_matches_terminal=isinstance(f, dict) and isinstance(row, dict) and row.get("data") == f and
                        f.get("passed_execution") is True and f.get("role") == "E3" and f.get("num_envs") == 80 and
                        f.get("controls") == 160 and f.get("seed") == 20260928 and f.get("optimizer_updates") == 0,
                    actual_parent_cleanup_waited_and_released=end.get("all_own_children_waited") is True and
                        end.get("original_single_GPU_private_EX_released") is True and end.get("original_global_finite_EX_released") is True and
                        end.get("errors") == [],
                    actual_child_wait_matches_terminal=isinstance(child_wait, dict) and isinstance(row, dict) and
                        type(child_wait.get("pid")) is int and child_wait["pid"] > 0 and
                        child_wait.get("role") == "E3" and child_wait["pid"] == row.get("pid") and
                        child_wait.get("actual_waited") is True and child_wait.get("returncode") == 0,
                    outer_actual_reaped_RC0_no_errors=outer.get("actual_parent_p_wait_returned") is True and
                        outer.get("original_parent_reaped") is True and outer.get("returncode") == 0 and outer.get("errors") == [] and
                        outer.get("root") == root and outer.get("roles") == ["E3"] and outer.get("original_parent_Popen_calls") == 1,
                    outer_identity_matches_dispatch=outer.get("controller") == dispatch["dispatch"]["controller"] and
                        outer.get("parent") == dispatch["dispatch"]["parent"] and isinstance(outer.get("parent"), dict),
                    own_worker_error_evidence_absent=all(m[name] is None for name in ERROR_NAMES),
                    actual_ready_started_preclose_present=all(isinstance(m[name], dict) for name in
                        ("cases/E3/WORKER_SCENE_READY.json", "cases/E3/WORKER_EVAL_STARTED.json", "cases/E3/PRE_CLOSE.json")),
                )
                checks["actual_parent_child_task_PID_binding"] = bool(isinstance(task, dict) and isinstance(f, dict) and
                    isinstance(row, dict) and isinstance(parent_started, dict) and isinstance(outer.get("parent"), dict) and
                    type(f.get("parent_pid")) is type(f.get("worker_pid")) is int and
                    f["parent_pid"] > 0 and f["worker_pid"] > 0 and
                    task.get("owner_parent_pid") == f["parent_pid"] == parent_started.get("pid") == outer["parent"].get("pid") and
                    row.get("pid") == f["worker_pid"])
                checks["actual_selected_source_metadata_binding"] = bool(isinstance(qualification, dict) and isinstance(f, dict) and
                    isinstance(f.get("source_cache"), dict) and qualification.get("source_binding") ==
                    f["source_cache"].get("source_binding") == expected_source)
                checks = {name: bool(value) for name, value in checks.items()}
                execution_qualified = all(checks.values())
                current.update(execution_qualified=execution_qualified, execution_checks=checks,
                    failed_execution_checks=[name for name, ok in checks.items() if not ok],
                    terminal_stdout_tails=terminal_tails(), skill_acceptance_or_graduation_claim=False,
                    source_IO_or_training_counter_as_skill_evidence=False)
                compat = {name: group[name] for name in ("nine_ready_before_start", "all_nine_actual_execution_complete")
                          if isinstance(group, dict) and name in group}
                # Copy outcome verbatim, even if close failed; no new success threshold or reset stitching.
                outcome = f["skill"] if isinstance(f, dict) and "skill" in f else None
                result = dict(kind="FDN_N20000_ORIGINAL_E3_N80_FIRST_EPISODE_METADATA_NOT_SKILL_ADMISSION",
                    root=root, roles=["E3"], source_binding=expected_source, execution_qualified=execution_qualified,
                    execution_checks=checks, original_worker_outcome_verbatim=outcome,
                    actual_parent_wait_qualification=qualification, legacy_all_nine_keys_compatibility_only=compat,
                    parent_legacy_nine_keys_used_for_execution=False, new_success_threshold_or_reset_stitching=False,
                    skill_acceptance_or_graduation_claim=False, source_IO_or_training_counter_as_skill_evidence=False,
                    independent_MuJoCo_acceptance_claim=False)
                with scope_path.open("x", encoding="utf8") as stream:
                    json.dump(result, stream, indent=2, allow_nan=False)
                with closed_path.open("x", encoding="utf8") as stream:
                    json.dump(current, stream, indent=2, allow_nan=False)
                print("FDNN20000_FROZEN_CLOSED " + json.dumps(dict(root=root, roles=["E3"], execution_qualified=execution_qualified,
                    failed_execution_checks=current["failed_execution_checks"], skill_acceptance_claim=False)), flush=True)
                break
            if time.monotonic() - start >= CAP_SECONDS:
                timeout = dict(epoch=time.time(), root=root, roles=["E3"], observer_timed_out=True,
                    actual_close_not_claimed=True, original_parent_not_extended_or_signalled=True,
                    last_own_metadata=m, terminal_stdout_tails=terminal_tails(), skill_acceptance_claim=False)
                with timeout_path.open("x", encoding="utf8") as stream:
                    json.dump(timeout, stream, indent=2, allow_nan=False)
                print("FDNN20000_FROZEN_OBSERVER_TIMEOUT " + root, flush=True)
                break
            time.sleep(min(INTERVAL_SECONDS, max(0, CAP_SECONDS - (time.monotonic() - start))))
    finally:
        if s is not None:
            s.close()
        if c is not None:
            c.close()


if __name__ == "__main__":
    main()

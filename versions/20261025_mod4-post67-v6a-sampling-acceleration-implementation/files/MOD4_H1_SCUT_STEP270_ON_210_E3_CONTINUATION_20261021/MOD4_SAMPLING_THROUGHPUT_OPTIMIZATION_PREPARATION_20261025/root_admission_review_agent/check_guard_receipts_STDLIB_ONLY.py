"""Synthetic text-only admission tests; no bank/PT/NumPy/torch/SDK imports."""
from __future__ import annotations
import ast
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import traceback
import build_69_ready_guard_copies as config

HERE = Path(__file__).resolve().parent
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
out = HERE / ("SYNTHETIC_TEXT_GUARD_TEST_" + stamp)
out.mkdir(exist_ok=False)
report = {"trial_id": out.name, "status": "RUNNING", "cases": [],
          "synthetic_receipts_only_not_actual_admission": True,
          "PT_bank_numpy_torch_SDK_native_policy_GPU_remote_or_training": False,
          "bank_files_physically_present": False, "git_status": "PENDING_ROOT_UNIFIED_ARCHIVE"}


def row(path, relative):
    return {"relative": relative, "bytes": path.stat().st_size, "SHA": config.H(path)}


def must_reject(name, call):
    try:
        call()
    except (AssertionError, KeyError):
        report["cases"].append({"name": name, "expected_rejection": True})
    else:
        raise AssertionError("guard accepted invalid fixture: " + name)


try:
    names = {"h1": ("closed_production_continuation_CPU_v2.py", "target_H1_step270_closed_source_sdk_cpu_review_v1.py"),
             "recovery": ("original_account_policy50_source_CPU.py", "target_two50_source_sdk_cpu_review.py")}
    for key, (guard, target) in names.items():
        old = out / key / "old"
        new = out / key / "new"
        old.mkdir(parents=True); new.mkdir()
        for name in (guard, target):
            shutil.copyfile(config.BASE / key / name, old / name)
            shutil.copyfile(HERE / "copies_69_ready" / key / name, new / name)
        shutil.copyfile(config.CHECKER, new / "sampling_acceleration_installed_CPU_v2.py")
        for rel in config.BASE_CHANGE[key]:
            p = old / rel;p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(config.BASE / key / rel, p)
        speed_root = config.OPT / "your_agent/implementation_v1/revision_v2/payloads" / key
        for rel in config.CANDIDATES[key]:
            p = new / rel;p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(speed_root / rel, p)
        if key == "h1":
            for rel in config.FROZEN_H1:
                shutil.copyfile(config.BASE / key / rel, old / rel)
                shutil.copyfile(config.BASE / key / rel, new / rel)
        unchanged = "job0/runtime/isaac/mod4/SYNTHETIC_UNCHANGED.py"
        for root in (old, new):
            p = root / unchanged;p.parent.mkdir(parents=True, exist_ok=True);p.write_text("SYNTHETIC_CONSTANT = 1\n")
        before = {rel: row(old / rel, rel) for rel in config.BASE_CHANGE[key]}
        before[unchanged] = row(old / unchanged, unchanged)
        current = {rel: row(new / rel, rel) for rel in config.CANDIDATES[key]}
        current[unchanged] = row(new / unchanged, unchanged)
        # A missing physical bank is intentional: receipt verification must not
        # open it. The original target checker owns actual data validation.
        bank_rel = "job0/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz"
        if key == "recovery":
            item = {"relative": bank_rel, "bytes": 32022178, "SHA": "78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83"}
            before[bank_rel] = item; current[bank_rel] = dict(item)
        m = {"files": list(current.values())}
        auth = json.loads((HERE / "SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_SCHEMA_TEMPLATE.json").read_text())
        auth.update(approved=True, synthetic_fixture_only=True, human_authorization_source="SYNTHETIC_UNIT_TEST_NOT_REAL_AUTHORIZATION")
        auth_path = new / "SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json"
        auth_path.write_text(json.dumps(auth))
        speed = {"passed": True, "key": key, "base": str(new), "expected_base_SHA": config.BASE_CHANGE[key],
                 "candidate_SHA": config.CANDIDATES[key], "exact_source_allowlist": list(config.CANDIDATES[key]),
                 "no_GPU_API_SDK_scene_policy_physics_or_canonical": True,
                 "synthetic_fixture_only_not_actual_CPU_admission": True}
        if key == "h1":
            speed.update(status="CPU_exact_installed_sources_and_lossless_fixture_passed", NPZ_array_bytes_dtype_shape_exact=True, full_SHA_preserved=True)
        else:
            speed.update(status="CPU_exact_installed_sources_and_fresh_bank_geometry_context_passed", bank_SHA=before[bank_rel]["SHA"], bank_bytes=32022178, fresh_bank_physical_read_count=1)
        cpu = {"sampling_acceleration_CPU": speed}
        tree = ast.parse((new / guard).read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_sampling_receipt")
        namespace = {"Path": Path, "json": json, "H": config.H}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), "SYNTHETIC_RECEIPT_FUNCTION_ONLY", "exec"), namespace)
        check = namespace["_sampling_receipt"]
        check(new, old, key, m, before, cpu)
        report["cases"].append({"name": key + "_valid_synthetic_receipt_structure", "accepted_structure_only": True})
        denied = dict(auth, approved=False);auth_path.write_text(json.dumps(denied))
        must_reject(key + "_approval_false", lambda: check(new, old, key, m, before, cpu));auth_path.write_text(json.dumps(auth))
        extra = copy.deepcopy(m);extra["files"].append({"relative": "job0/runtime/extra.py", "bytes": 1, "SHA": "0" * 64})
        must_reject(key + "_extra_runtime", lambda: check(new, old, key, extra, before, cpu))
        missing = copy.deepcopy(m);missing["files"] = [r for r in missing["files"] if r["relative"] != unchanged]
        must_reject(key + "_deleted_runtime", lambda: check(new, old, key, missing, before, cpu))
        changed = copy.deepcopy(m)
        next(r for r in changed["files"] if r["relative"] == unchanged)["SHA"] = "f" * 64
        must_reject(key + "_unrelated_runtime_SHA", lambda: check(new, old, key, changed, before, cpu))
        bad_cpu = copy.deepcopy(cpu);bad_cpu["sampling_acceleration_CPU"]["base"] = str(old)
        must_reject(key + "_receipt_wrong_payload_root", lambda: check(new, old, key, m, before, bad_cpu))
        bad_candidate = copy.deepcopy(cpu);bad_candidate["sampling_acceleration_CPU"]["candidate_SHA"] = {}
        must_reject(key + "_receipt_wrong_candidate_map", lambda: check(new, old, key, m, before, bad_candidate))
        if key == "recovery":
            duplicate = copy.deepcopy(cpu);duplicate["sampling_acceleration_CPU"]["fresh_bank_physical_read_count"] = 2
            must_reject("recovery_duplicate_fresh_bank_checker_receipt", lambda: check(new, old, key, m, before, duplicate))
            must_reject("recovery_guard_rejects_e2_key", lambda: check(new, old, "e2", m, before, cpu))
            assert not (new / bank_rel).exists()
        else:
            rel = "H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json"
            original_bytes = (new / rel).read_bytes();(new / rel).write_bytes(original_bytes + b" ")
            must_reject("h1_old_retention_approval_bytes_changed", lambda: check(new, old, key, m, before, cpu))
            (new / rel).write_bytes(original_bytes)
    report.update(status="PASS_SYNTHETIC_SOURCE_RECEIPT_GUARDS_ONLY", cases_count=len(report["cases"]))
except BaseException:
    report.update(status="FAIL_PRESERVED", original_error=traceback.format_exc())
    raise
finally:
    (out / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report.get(k) for k in ("trial_id", "status", "cases_count")}))

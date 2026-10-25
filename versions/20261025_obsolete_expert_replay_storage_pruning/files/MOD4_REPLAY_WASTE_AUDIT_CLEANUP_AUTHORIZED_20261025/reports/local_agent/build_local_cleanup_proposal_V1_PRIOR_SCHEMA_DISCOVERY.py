"""Read metadata/text only; never load or hash PT/NPZ/USD/ZIP payloads."""
from __future__ import annotations

import collections
import datetime
import hashlib
import json
import os
import pathlib
import re
import time

W = pathlib.Path(r"C:\Users\lulu\Desktop\claude\mjcf")
S = W / "MOD4_REPLAY_WASTE_AUDIT_CLEANUP_AUTHORIZED_20261025"
R = S / "reports"
OUT = R / "local_agent"
OUT.mkdir(parents=True, exist_ok=True)
META = R / "LOCAL_PROJECT_FILE_METADATA_FULL.jsonl"
rows = [json.loads(line) for line in META.open(encoding="utf-8")]
by_rel = {r["relative"]: r for r in rows}
by_path = {os.path.normcase(os.path.normpath(r["path"])): r for r in rows}
errors = [{
    "attempt": "local_metadata_reader_python_windowsapps_alias",
    "command": "python - (metadata and text JSON only)",
    "observed": "exit_code=1; empty stdout; Get-Command resolved WindowsApps alias",
    "mutation_or_payload_read": False,
    "correction": "Used explicit Python314/python.exe -B -X utf8; no experiment reexecution",
}]
read_evidence = {}
candidates = []
protected = []
uncertain = []


def read_json(p):
    p = pathlib.Path(p)
    try:
        data = p.read_bytes()
        obj = json.loads(data.decode("utf-8-sig"))
        read_evidence[str(p)] = {"path": str(p), "bytes": len(data),
                                "text_SHA256": hashlib.sha256(data).hexdigest()}
        return obj
    except Exception as exc:
        errors.append({"attempt": "read_text_json", "path": str(p),
                       "error": f"{type(exc).__name__}: {exc}"})
        return None


baseline = read_json(R / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json")
manifest = read_json(W / "MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/policy/manifest.json")
inventory = read_json(R / "LOCAL_PROJECT_REPLAY_RESOURCE_METADATA_INVENTORY_ACTUAL.json")
auth = read_json(R / "HUMAN_NEW_REPLAY_WASTE_AUDIT_CLEANUP_AUTH_ACTUAL.json")
current_model_paths = {os.path.normcase(os.path.normpath(v["path"]))
                       for v in manifest["sources"].values()}
current_proof = read_json(baseline["latest_training_source_proof"])


def emit(row, bucket, category, reason, evidence, sha=None, **extra):
    p = row["path"]
    assert os.path.commonpath([str(W), p]) == str(W)
    assert os.path.normcase(os.path.normpath(p)) not in current_model_paths
    item = {"path": p, "relative": row["relative"], "bytes": row["bytes"],
            "mtime_ns": row["mtime_ns"], "producer_SHA": sha,
            "producer_SHA_status": "existing_text_evidence_only" if sha else "unknown_no_payload_hash",
            "category": category, "reason": reason, "evidence_paths": evidence,
            "protection_decision": "recommend_delete_after_root_fresh_identity_check" if bucket is candidates
                                   else "retain" if bucket is protected else "not_selected_pending_evidence",
            "metadata_identity": {"device": row.get("device"), "inode": row.get("inode"),
                                  "nlink": row.get("nlink"),
                                  "zero_values_mean_unknown": True},
            "physical_release_bytes": None,
            "physical_release_status": "unknown_until_fresh_file_identity_nlink_allocation_check",
            **extra}
    bucket.append(item)
    return item


# Frozen/retired E1 rollout products: preserve all producer/result/probe/manifest text.
# Current W35 weights remain protected even when an old evaluation of the same SHA is retired.
route_rows = [r for r in rows if r["relative"].endswith("/route_raw.npz")]
for row in route_rows:
    rel = row["relative"]
    old_e1 = rel.startswith(("MOD4_E1_", "MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_",
                             "MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_"))
    p = pathlib.Path(row["path"])
    result_path, probe_path = p.parent / "result.json", p.parent / "probe.json"
    if not old_e1:
        emit(row, protected, "native_action_geometry_ABI_reference_route",
             "The remaining route files are native/action/geometry or SCUT ABI comparisons; preserve exact reference fixtures.",
             [str(R / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json")])
        continue
    result, probe = read_json(result_path), read_json(probe_path)
    if result is None or probe is None:
        emit(row, uncertain, "retired_E1_route_missing_summary", "Summary read failed.", [str(result_path), str(probe_path)])
        continue
    raw = probe.get("full_route_raw", {})
    declared_bytes = raw.get("bytes")
    sha = raw.get("sha256") or raw.get("SHA")
    if result.get("phase") != "complete" or result.get("exit_code") != 0 or declared_bytes != row["bytes"]:
        emit(row, uncertain, "retired_E1_route_summary_binding_mismatch",
             "Producer completion or exact raw byte binding does not match metadata.",
             [str(result_path), str(probe_path)], sha,
             result_phase=result.get("phase"), exit_code=result.get("exit_code"), declared_bytes=declared_bytes)
        continue
    evidence = [str(result_path), str(probe_path), str(R / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json"),
                str(W / "MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/policy/manifest.json")]
    if (p.parent / "manifest.json").is_file():
        old_manifest = read_json(p.parent / "manifest.json")
        evidence.append(str(p.parent / "manifest.json"))
    emit(row, candidates, "retired_E1_full_route_replay",
         "Completed historical E1/early MoE evaluation, superseded by fixed E0/W35/gate plus current H1/E2/E3 player. "
         "The existing probe preserves exact raw SHA/bytes/shapes, protocol, checkpoint, per-group metrics and failure counts. "
         "New human authorization permits retiring the bulky unused replay while preserving every outcome and text diagnostic.",
         evidence, sha,
         producer_checkpoint_SHA=result.get("checkpoint", {}).get("sha256"),
         producer_plan_SHA=result.get("plan_sha256"), protocol=probe.get("protocol"),
         producer_job_id=result.get("job_id"), num_envs=result.get("num_envs"), steps=result.get("steps"),
         original_summary_values={k: probe.get(k) for k in ["nonfinite", "actual_union_ordinary", "actual_union_truncation",
                                                         "reason_coverage_exact", "max_closure_m"]},
         outcome_relabelled=False,
         retained_small_evidence=["probe.json", "result.json", "manifest.json if present", "all historical reports/logs", "small query/terrain arrays"])


# Full controls from finished frozen S4/S5 comparisons are redundant replay products.
# The short 120-step native samples and every query array remain as exact numerical witnesses.
for row in rows:
    if not row["relative"].endswith(("/S4_ROUTING_FULL_CONTROL_ACTUAL.npz", "/S5_SINGLE_FULL_CONTROL_ACTUAL.npz")):
        continue
    p = pathlib.Path(row["path"])
    cp = p.parent / "COMPLETE_ACTUAL.json"
    complete = read_json(cp)
    if complete is None:
        emit(row, uncertain, "frozen_full_control_missing_complete", "Producer summary unavailable.", [str(cp)])
        continue
    raw = complete.get("raw", {})
    if complete.get("steps", 0) < 1500:
        emit(row, protected, "short_native_control_fixture", "Keep short native numerical/action/query reference control fixture.",
             [str(cp)], raw.get("sha256"), steps=complete.get("steps"))
        continue
    if complete.get("passed_data_contract") is not True or raw.get("bytes") != row["bytes"]:
        emit(row, uncertain, "frozen_control_summary_binding_mismatch", "No exact completed raw metadata binding.",
             [str(cp)], raw.get("sha256"), declared_bytes=raw.get("bytes"), steps=complete.get("steps"))
        continue
    emit(row, candidates, "retired_frozen_S4_S5_long_control_replay",
         "Finished long evaluation of historical frozen single/rule/gate policies. COMPLETE binds the original replay SHA and size "
         "and preserves protocol/checkpoint/callback/reset metrics; retain all text, probe and short native/query arrays. "
         "Neither the current fixed player manifest nor current H1/E3 source consumes this historical replay.",
         [str(cp), str(p.parent / "probe.json"), str(R / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json")],
         raw.get("sha256"), steps=complete.get("steps"), checkpoint_SHA=complete.get("checkpoint_sha256"),
         protocol=complete.get("protocol"), ordinary=complete.get("ordinary"), truncation=complete.get("truncation"),
         outcome_relabelled=False)


# Closed old H1 training prefix, keeping beginning, last full predecessor and exact final failure.
H = W / "MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021"
pair_receipt_path = H / "reports/PAIR_V1_H1_CLOSED_CONTROL318_FORENSICS_RELOCATED_SPACE_RELEASED_ACTUAL.json"
pair_receipt = read_json(pair_receipt_path)
failure_path = H / "reports/H1_FAILED_CONTROL318_RECORDED_WORLD_FLOOR_BOUNDS_CPU_ACTUAL.json"
failure = read_json(failure_path)
pair_sha = {pathlib.PureWindowsPath(f["local_path"]).name: f.get("SHA") for f in pair_receipt["files"]}
for row in rows:
    if "/relocated_forensic_originals/H1step270_pairV1_closed_control318/" not in row["relative"] or not row["relative"].endswith(".npz"):
        continue
    name = pathlib.PurePosixPath(row["relative"]).name
    n = int(re.search(r"prefix_(\d+)", name).group(1))
    keep = n in [0, 12, 13]
    emit(row, protected if keep else candidates,
         "closed_H1_pairV1_representative" if keep else "closed_H1_pairV1_intermediate_replay",
         "Keep first raw, final complete 24-step predecessor and final six recorded controls containing the documented arena-exit anomaly."
         if keep else "Old failed stage is closed and superseded; retain first prefix0 plus prefix12/13 immediately surrounding the documented control317 anomaly. "
         "The intermediate replay is no longer needed; all exact file receipts and original failure reports remain.",
         [str(pair_receipt_path), str(failure_path), str(R / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json")],
         pair_sha.get(name), retained_representative_prefixes=[0, 12, 13], stage_source_controls=318)


# Historical T3 control replay: first/last retained, original receipts retained.
t3_receipt_path = H / "reports/H1_CLOSED_PREFIX12_FORENSICS_VERIFIED_RELOCATION_ACTUAL.json"
t3 = read_json(t3_receipt_path)
t3_sha = {}
for f in t3.get("removed", []) + t3.get("files", []):
    lp = f.get("local_path") or f.get("full_forensic_original_retained_at_verified_C_path")
    if lp:
        t3_sha[pathlib.PureWindowsPath(lp).name] = f.get("verified_C_SHA") or f.get("SHA") or f.get("sha256")
for row in rows:
    if "/relocated_forensic_originals/T3_1710v1_control_prefix_batch12/" not in row["relative"] or not row["relative"].endswith(".npz"):
        continue
    name = pathlib.PurePosixPath(row["relative"]).name
    n = int(re.search(r"prefix_(\d+)", name).group(1))
    keep = n in [24, 50]
    receipt = pathlib.Path(row["path"] + ".verified_receipt.json")
    if receipt.is_file():
        small = read_json(receipt)
    emit(row, protected if keep else candidates, "retired_T3_representative" if keep else "retired_T3_intermediate_replay",
         "Keep first and last locally retained T3 prefix representatives."
         if keep else "Old T3 closed-stage middle control replay, superseded by later complete H1 sources. "
         "Preserve prefix24 and50 as first/last local representatives plus every exact SHA receipt/report. "
         "No query/native evidence was identified as bound to these middle prefixes.",
         [str(t3_receipt_path), str(receipt), str(R / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json")],
         t3_sha.get(name), retained_representative_prefixes=[24, 50])


# Retired E1 phase2470: keep first/last and the sole recorded base_contact@884 block.
E1 = W / "MOD4_LINUX_BODYFRAME_RESAMPLE_PHASE_REPAIR_20261014"
e1_summary_path = E1 / "reports/PHASE_REPAIR_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json"
e1 = read_json(e1_summary_path)
e1_events = [v["control_step"] for v in e1.get("health", {}).get("last_actual_termination_events", [])]
for f in e1["all_trace"]:
    row = by_path.get(os.path.normcase(os.path.normpath(f["path"])))
    if row is None:
        continue
    name = pathlib.PureWindowsPath(f["path"]).name
    a, b = map(int, re.search(r"retention_prefix_(\d+)_(\d+)\.npz", name).groups())
    keep = a == 0 or b == e1["controls"] or any(a <= v < b for v in e1_events)
    emit(row, protected if keep else candidates, "retired_E1_phase2470_representative" if keep else "retired_E1_phase2470_intermediate_replay",
         "Keep startup, final block or the original block containing the documented sole base_contact@884 event."
         if keep else "Completed retired E1 phase; exact all-trace SHA/count/health/termination summary exists. "
         "Remove unused middle blocks while retaining startup, final block and the sole base_contact@884 block.",
         [str(e1_summary_path)], f.get("sha256"), controls=[a, b], retained_anomaly_controls=e1_events)


# A stale producer summary is explicitly NOT used as proof for another failed stage.
bad_summary_path = W / "MOD4_LINUX_WAVE50_BODYFRAME_SECOND_PREPARE_20261014/failed_window_actual_1791991561073533600/evidence_own_final.json"
bad = read_json(bad_summary_path)
if bad and "MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014" in bad.get("own_checkpoint", {}).get("path", ""):
    errors.append({"attempt": "failed_window_evidence_source_binding_review", "path": str(bad_summary_path),
                   "error": "The saved evidence_own_final JSON binds the earlier formal300/reset-integration stage, not its containing failed formal3600 stage.",
                   "action": "Original report retained; do not reuse its pass/SHA/all_trace for formal3600 cleanup proof."})
    for row in rows:
        if row["relative"].startswith("MOD4_LINUX_WAVE50_BODYFRAME_SECOND_PREPARE_20261014/failed_window_actual_") and row["relative"].endswith(".npz"):
            emit(row, uncertain, "failed_E1_formal3600_summary_binding_gap",
                 "Adjacent evidence_own_final is bound to earlier formal300, not this failed stage. Keep pending exact event-block summary; this is a reader evidence gap, not a new experiment failure.",
                 [str(bad_summary_path)])


# The accepted native/query fixture group is an explicit protection exception.
for row in rows:
    if row["relative"].startswith("MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/full20k_native180_V3_actual/out/") and row["relative"].endswith(".npz"):
        emit(row, protected, "accepted_exact_H1_native_query_numerical_fixture",
             "Preserve accepted same-source native/query evidence and original failure diagnostics; no re-audit or re-run is requested.",
             [str(R / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json"),
              str(H / "reports/STEP270_FULL20K_NATIVE180_V3_COMPLETE_RAW_AND_EXIT_RECOVERED_V2_ACTUAL.json")])


# These two ZIPs are produced exactly from retained unpacked trees; source scripts and
# manifests bind file rows. Do not inspect the ZIP and do not remove its source tree.
zip_specs = [
    ("MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015", "S4_FIRST_TRAINED_GATE_FROZEN35_V1.zip",
     "prepare_first_trained_gate_frozen35_CPU_package.py", "payload", "REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json"),
    ("MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015", "S5_NOMINAL_COMPLETE_ISOLATED_ABC_V1.zip",
     "prepare_complete_isolated_nominal_ABC_package_CPU_once.py", "isolated", "RETENTION_CPU_MANIFEST_V8.json"),
]
for root, zip_name, producer, tree, mf in zip_specs:
    rel = f"{root}/{zip_name}"
    row = by_rel.get(rel)
    if row is None:
        continue
    source = W / root / producer
    source_text = source.read_text(encoding="utf-8-sig")
    read_evidence[str(source)] = {"path": str(source), "bytes": source.stat().st_size,
                                 "text_SHA256": hashlib.sha256(source.read_bytes()).hexdigest()}
    # Source variables are checked manually as text, not executed.
    tree_path = W / root / tree
    manifest_path = tree_path / mf
    if not manifest_path.is_file():
        # Isolated nominal's complete source tree is named payload; reject guess.
        emit(row, uncertain, "rebuildable_package_manifest_unresolved",
             "ZIP producer is preserved, but the exact retained tree/manifest binding needs resolution; no archive content read.",
             [str(source), str(manifest_path)])
        continue
    package_manifest = read_json(manifest_path)
    file_rows = package_manifest.get("file_rows", [])
    missing_or_size = []
    for f in file_rows:
        rp = f.get("relative") or f.get("path")
        if not rp or pathlib.PureWindowsPath(rp).is_absolute():
            continue
        fp = tree_path / pathlib.PurePosixPath(rp)
        if not fp.is_file() or ("bytes" in f and fp.stat().st_size != f["bytes"]):
            missing_or_size.append(str(fp))
    if not file_rows or missing_or_size:
        emit(row, uncertain, "rebuildable_package_tree_incomplete_or_manifest_schema",
             "Exact retained-tree size checks did not establish the complete package source.",
             [str(source), str(manifest_path)], mismatches=missing_or_size[:10], manifest_file_rows=len(file_rows))
        continue
    emit(row, candidates, "redundant_rebuildable_retired_ZIP",
         "Saved producer source creates this transport ZIP from the retained unpacked source tree; every manifest file row still exists at its declared size. "
         "Delete only ZIP; preserve unpacked source, all models, assets, producer scripts and original manifests/reports. No ZIP content/hash was read.",
         [str(source), str(manifest_path)], retained_tree=str(tree_path), manifest_file_rows=len(file_rows))


# Standard Python bytecode is reconstructable if the matching .py source still exists.
# Inventory excludes cache directories, so collect only their file metadata now.
cache_started = time.time()
cache_rows = []
cache_uncertain = []
skip_dirs = {".git", "node_modules", ".venv", "venv", "site-packages", ".mypy_cache", ".ruff_cache"}
for root in inventory["selected_project_roots"]:
    root_path = pathlib.Path(root)
    if root_path == S or not root_path.exists():
        continue
    for dp, dns, fns in os.walk(root_path, followlinks=False):
        dns[:] = [d for d in dns if d.lower() not in skip_dirs]
        d = pathlib.Path(dp)
        if d.name != "__pycache__":
            continue
        for name in fns:
            if not name.endswith(".pyc"):
                continue
            p = d / name
            st = p.stat()
            rr = {"path": str(p), "relative": p.relative_to(W).as_posix(), "bytes": st.st_size,
                  "mtime_ns": st.st_mtime_ns, "device": st.st_dev, "inode": st.st_ino, "nlink": st.st_nlink}
            stem = re.sub(r"\.(?:cpython|pypy)-[^.]+(?:\.opt-\d+)?\.pyc$", "", name)
            py = d.parent / (stem + ".py")
            if py.is_file():
                emit(rr, candidates, "rebuildable_Python_bytecode_cache", "Standard __pycache__ bytecode with the matching retained .py source. Rebuilt on demand; no training/GUI execution required.",
                     [str(py)], source_file=str(py), metadata_fresh_os_stat=True)
                cache_rows.append(rr)
            else:
                emit(rr, uncertain, "bytecode_without_matching_retained_source", "No matching .py was established; do not assume this is redundant source.", [], source_file_attempt=str(py))
                cache_uncertain.append(rr)
        dns[:] = []


# Repeated large payload assets are real space candidates but same size is not proof.
# Do not classify hundreds of bank/robot path aliases as physical copies.
asset_groups = collections.defaultdict(list)
for row in rows:
    if row["relative"].endswith(("/MOD4_RESET_COLLISION_BANK.npz", "/robot.usd")):
        asset_groups[pathlib.PurePosixPath(row["relative"]).name].append(row)
asset_caution = []
for name, group in asset_groups.items():
    asset_caution.append({"name": name, "files": len(group), "logical_bytes": sum(x["bytes"] for x in group),
                          "classification": "not_selected_by_this_agent",
                          "reason": "Many historical payload/source-snapshot copies; metadata size equality and zero DirEntry identity do not prove byte duplicates or physical release. Exact current model/runtime dependencies and a surviving same-SHA source must be bound before deleting assets.",
                          "physical_release_bytes": None, "paths": [r["path"] for r in group]})

assert len({c["path"] for c in candidates}) == len(candidates)
assert not ({c["path"] for c in candidates} & {p["path"] for p in protected})
assert all(pathlib.Path(c["path"]).suffix.lower() in [".npz", ".pyc", ".zip"] for c in candidates)
assert all(not any(v in c["relative"] for v in baseline["current_step_diagnostic_stages"]) for c in candidates)
groups = collections.defaultdict(lambda: {"files": 0, "logical_bytes": 0})
for c in candidates:
    groups[c["category"]]["files"] += 1
    groups[c["category"]]["logical_bytes"] += c["bytes"]

report = {
    "schema": "MOD4_EXACT_LOCAL_REPLAY_CLEANUP_PROPOSAL_V1",
    "epoch": time.time(), "created_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "read_only_proposal_no_delete_move_or_hardlink": True,
    "authorization_scope": "Human newly authorized obsolete frozen/retired expert replay cleanup; parent relayed lowered threshold with first/last/key-anomaly representatives for old closed stages.",
    "current_protection_basis": str(R / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json"),
    "current_player_manifest": str(W / "MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/policy/manifest.json"),
    "metadata_basis": {"path": str(META), "rows": len(rows), "existing_SHA256": inventory["full_metadata"]["SHA"]},
    "selection_not_based_on_date_or_name_alone": True,
    "payload_PT_NPZ_USD_ZIP_not_opened_loaded_or_hashed": True,
    "current_GUI_models_rollout_GPU_training_SSH_budget_and_Git_untouched": True,
    "candidate_file_count": len(candidates), "candidate_logical_bytes": sum(c["bytes"] for c in candidates),
    "physical_release_bytes": None,
    "physical_release_explanation": "Logical size is not released allocation; root must freshly stat or use Win32 FileID/nlink and measure volume free space. DirEntry device/inode/nlink=0 are unknown. No all-path hardlink claim is made.",
    "candidate_groups": dict(groups), "candidates": candidates,
    "protected_file_count": len(protected), "protected_logical_bytes": sum(c["bytes"] for c in protected),
    "protected": protected, "uncertain": uncertain,
    "uncertain_count": len(uncertain), "uncertain_logical_bytes": sum(c["bytes"] for c in uncertain),
    "large_repeated_asset_groups_not_selected": asset_caution,
    "all_reports_logs_manifests_source_models_Git_history_retained": True,
    "source_errors_and_reader_binding_gaps": errors,
    "text_evidence_read_and_SHA_index": list(read_evidence.values()),
    "cache_metadata_collection_seconds": time.time() - cache_started,
    "execution_requirements_for_root": [
        "No recursive directory deletion; only exact candidate paths after fresh metadata/protection/identity checks.",
        "Abort changed path size or mtime; do not infer duplicates from device/inode/nlink zero.",
        "Preserve all protected current65/67 last-two jump replays, MoE collision, native/query fixtures, current source/FINAL, model/optimizer, original text failures and logs.",
        "Keep all producer SHA/size receipts and this exact deletion/protection index in the new stage Git archive; report fresh actual deletion and free-space results separately.",
    ],
    "Git_state": "new report/source pending parent unified archive; not claimed recorded remotely",
}
target = OUT / "EXACT_LOCAL_REPLAY_CLEANUP_PROPOSAL_ACTUAL.json"
target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"report": str(target), "candidates": len(candidates),
                  "logical_bytes": report["candidate_logical_bytes"], "groups": dict(groups),
                  "protected": len(protected), "uncertain": len(uncertain), "errors": len(errors),
                  "cache_scan_seconds": report["cache_metadata_collection_seconds"]}, ensure_ascii=False))

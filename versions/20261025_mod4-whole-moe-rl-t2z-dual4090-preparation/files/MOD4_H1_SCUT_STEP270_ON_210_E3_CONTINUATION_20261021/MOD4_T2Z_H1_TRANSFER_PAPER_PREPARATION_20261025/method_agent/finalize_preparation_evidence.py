"""Append local CLI evidence and a reproducibility inventory; never archive Git."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REPORTS = BASE / "reports"
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
identity = f"METHOD_CLI_SYNTHETIC_AND_MISSING_DATA_{stamp}"
env = dict(os.environ, CUDA_VISIBLE_DEVICES="")
missing = BASE / "missing_native_dataset_manifest.json"
if not missing.exists():
    missing.write_text(json.dumps({"schema": "mod4.h1.t2z.raw.v1", "synthetic": False,
                                  "dataset_id": "MISSING_REAL_H1_RGB_NOT_A_DATASET",
                                  "episodes": []}, indent=2) + "\n", encoding="utf-8")
cases = [("SYNTHETIC_CONVERSION", BASE / "synthetic_example_manifest.json", False, 0, "CONVERTED_NOT_TRAINING_READY"),
         ("SYNTHETIC_REFUSED_REAL", BASE / "synthetic_example_manifest.json", True, 1, "SYNTHETIC_NOT_TRAINING"),
         ("MISSING_REAL_DATA_REFUSED", missing, True, 1, "DATASET_MISSING")]
receipts = []
for label, manifest, real, expected_exit, expected_marker in cases:
    path = REPORTS / f"{identity}_{label}_output.json"
    command = [sys.executable, str(BASE / "contract_v1.py"), str(manifest),
               str(BASE / "synthetic_example_split.json"), str(path)]
    if real:
        command.append("--require-real")
    result = subprocess.run(command, cwd=BASE, env=env, capture_output=True, text=True, timeout=30)
    receipt = {"attempt_id": f"{identity}_{label}", "source_sha256": hashlib.sha256((BASE / "contract_v1.py").read_bytes()).hexdigest(),
               "manifest": str(manifest), "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
               "expected_exit": expected_exit, "actual_exit": result.returncode,
               "stdout": result.stdout, "stderr": result.stderr,
               "passed_expected_behavior": result.returncode == expected_exit and expected_marker in result.stdout + result.stderr,
               "output_exists": path.exists(), "synthetic_only_or_missing_data": True}
    receipts.append(receipt)
report = {"trial_id": identity, "observed_utc": stamp,
          "status": "PASS_EXPECTED_ACCEPT_AND_REJECTIONS" if all(r["passed_expected_behavior"] for r in receipts) else "FAIL_PRESERVED",
          "type": "CPU_SYNTHETIC_CLI_AND_MISSING_DATA_REJECTION_NOT_TRAINING",
          "receipts": receipts, "git_status": "PENDING_ROOT_UNIFIED_ARCHIVE"}
(REPORTS / f"{identity}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
inventory = []
for path in sorted(BASE.rglob("*")):
    if not path.is_file() or "__pycache__" in path.parts or path.name == "REPRODUCIBILITY_INDEX.json":
        continue
    inventory.append({"relative_path": path.relative_to(BASE).as_posix(), "path": str(path),
                      "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "git_status": "PENDING_ROOT_UNIFIED_ARCHIVE"})
workspace = BASE.parents[2]
stage = BASE.parents[1]
local_inputs = [workspace / "AGENTS.md", workspace / "polar-rl-train/AGENTS.md",
                workspace / "polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md",
                workspace / "polar-rl-train/docs/NEXT_AI_GIT_WORKFLOW.md",
                workspace / "polar-rl-train/docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md",
                stage / "MOD4_T2Z_FUTURE_TRAINING_FEASIBILITY_20261025/reports/SOURCES_AND_COMPATIBILITY_ACTUAL.json",
                stage / "MOD4_T2Z_FUTURE_TRAINING_FEASIBILITY_20261025/reports/FEASIBILITY_REVIEW_ACTUAL.md",
                stage / "MOD4_T2Z_FUTURE_TRAINING_FEASIBILITY_20261025/reports/ROOT_OFFLINE_TRAINING_AND_ONLINE_REAL_INTERACTION_CLARIFICATION_ACTUAL.md",
                stage / "H1_STEP270_CLOSED67_SAVED_REPLAY_AFTER_V5_20261025/reports/LATEST67_SELECTED_LEG_LENGTH_ACTION_CLIP_AND_REWARD_DESCRIPTIVE_ACTUAL.json",
                stage / "H1_STEP270_CLOSED67_SAVED_REPLAY_AFTER_V5_20261025/reports/LATEST67_STEP_TIMING_AND_REWARD_ALIGNMENT_DESCRIPTIVE_ACTUAL.json",
                stage / "H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/payloads/h1/job0/runtime/isaac/mod4/mod4_task.py",
                stage / "H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/payloads/h1/job0/runtime/isaac/mod4/action_delay_sdk_adapter.py",
                stage / "H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/payloads/h1/job0/runtime/isaac/mod4/action_delay_physics_queue.py"]
source_receipts = [{"path": str(p), "bytes": p.stat().st_size,
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                    "scope": "existing local small report or source; not executed"} for p in local_inputs]
upstream = "https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/"
web_sources = [{"url": "https://arxiv.org/html/2610.22364v1", "content_sha256": None,
                "inspection": "primary HTML method/setup/protocol sections, no figure-memory claim"}]
web_sources.extend({"url": upstream + name, "content_sha256": None,
                    "inspection": "fixed raw primary source read with web tool; no API; no full snapshot saved"}
                   for name in ("t2z/data.py", "t2z/metadata.py", "docs/simulation_observation_capture.md",
                                "wan_video_action/models/wan_video_action_encoder.py",
                                "configs/ours/sim_pushbox_friction.yaml"))
index = {"schema": "mod4.method.preparation.inventory.v1", "observed_utc": stamp,
         "scope": "method_agent only; no remote/policy/raw/model results",
         "archive_status": "LOCAL_ONLY_PENDING_ROOT_RECORD_EXPERIMENT_AND_REMOTE_MAIN_TAG_PEELED_VERIFICATION",
         "source_index_includes_failed_attempts": True,
         "self_hash_note": "index excludes itself; root archive manifest will hash this file",
         "excluded_runtime_cache": "__pycache__/*.pyc are interpreter cache, not reports or source evidence",
         "files": inventory, "local_input_source_receipts": source_receipts,
         "primary_web_sources": web_sources}
(REPORTS / "REPRODUCIBILITY_INDEX.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"trial_id": identity, "status": report["status"], "inventory_files": len(inventory)}))
print(str(REPORTS / "REPRODUCIBILITY_INDEX.json"))
sys.exit(0 if all(r["passed_expected_behavior"] for r in receipts) else 1)

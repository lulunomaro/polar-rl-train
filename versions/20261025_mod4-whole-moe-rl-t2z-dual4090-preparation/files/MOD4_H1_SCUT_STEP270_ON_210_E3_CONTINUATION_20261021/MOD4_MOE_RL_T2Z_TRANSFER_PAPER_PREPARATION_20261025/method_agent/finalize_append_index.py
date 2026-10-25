"""Create a new final inventory after appended protocol corrections; no overwrite."""
from __future__ import annotations
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
target = BASE / "reports/REPRODUCIBILITY_INDEX_V2.json"
if target.exists():
    raise RuntimeError("Final index already frozen; append another version instead")
for path in BASE.glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
files = []
json_count = 0
for path in sorted(BASE.rglob("*")):
    if not path.is_file() or "__pycache__" in path.parts or path == target:
        continue
    if path.suffix == ".json":
        json.loads(path.read_text(encoding="utf-8"))
        json_count += 1
    files.append({"relative_path": path.relative_to(BASE).as_posix(), "path": str(path),
                  "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
report = {"schema": "mod4.whole_moe.t2z.preparation.inventory.v2",
          "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
          "status": "LOCAL_PREPARATION_COMPLETE_PENDING_ROOT_GIT_NOT_TRAINING_READY",
          "supersedes_for_current_file_inventory": "reports/REPRODUCIBILITY_INDEX.json (retained historical snapshot)",
          "latest_cpu_trial": "MOE_T2Z_CPU_INTERFACE_20261025T060703500077Z",
          "latest_tests": 12, "latest_cli_checks": 4, "cuda_initialized": False,
          "current_top_level_python_ast_parse": "PASS", "json_files_parsed_before_index": json_count,
          "files": files, "training_started": False,
          "self_hash_note": "root archive manifest must hash this file; inventory excludes itself",
          "external_source_inventory": "source_facts.json small_local_input_receipts includes retained fixed upstream snapshots",
          "archive_status": "PENDING_ROOT_RECORD_EXPERIMENT_UNIQUE_ANNOTATED_TRIAL_MAIN_TAG_PEELED"}
target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
mismatches = [r["relative_path"] for r in files if hashlib.sha256((BASE / r["relative_path"]).read_bytes()).hexdigest() != r["sha256"]]
print(json.dumps({"index": str(target), "files": len(files), "parsed_json": json_count,
                  "sha_mismatches": mismatches, "training_ready": False}))
assert not mismatches

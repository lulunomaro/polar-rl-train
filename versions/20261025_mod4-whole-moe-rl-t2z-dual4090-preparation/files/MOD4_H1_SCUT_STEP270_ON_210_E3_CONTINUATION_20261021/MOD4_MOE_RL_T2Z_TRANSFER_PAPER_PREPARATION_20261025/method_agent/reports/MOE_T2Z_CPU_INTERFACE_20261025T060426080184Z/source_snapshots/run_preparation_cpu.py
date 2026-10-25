"""Run only new whole-MoE synthetic CPU tests and preserve each attempt."""
from __future__ import annotations
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
os.environ["CUDA_VISIBLE_DEVICES"] = ""
BASE = Path(__file__).resolve().parent
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
trial = "MOE_T2Z_CPU_INTERFACE_" + stamp
out = BASE / "reports" / trial
out.mkdir(parents=True, exist_ok=False)
snapshots = out / "source_snapshots"
snapshots.mkdir()
for source in BASE.glob("*.py"):
    shutil.copyfile(source, snapshots / source.name)
output = io.StringIO()
result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName("test_moe_cpu"))
(out / "TEST_LOG.txt").write_text(output.getvalue(), encoding="utf-8")
from test_moe_cpu import fixture
raw, plan = fixture()
(out / "SYNTHETIC_MANIFEST_NOT_DATA.json").write_text(json.dumps(raw) + "\n", encoding="utf-8")
(out / "SYNTHETIC_SPLITS.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
missing = dict(raw, synthetic=False, episodes=[])
(out / "MISSING_NATIVE_DATA_NOT_DATASET.json").write_text(json.dumps(missing) + "\n", encoding="utf-8")
cli = []
for name, manifest, flags, code, marker in (
    ("synthetic_check", "SYNTHETIC_MANIFEST_NOT_DATA.json", ["--synthetic-contract-test"], 0, "CHECKED_NOT_TRAINING_READY"),
    ("synthetic_rejected_real", "SYNTHETIC_MANIFEST_NOT_DATA.json", [], 1, "SYNTHETIC_NOT_TRAINING"),
    ("missing_real_rejected", "MISSING_NATIVE_DATA_NOT_DATASET.json", [], 1, "DATASET_MISSING"),
    ("train_disabled", "SYNTHETIC_MANIFEST_NOT_DATA.json", ["--train"], 1, "TRAINING_DISABLED_IN_PREPARATION")):
    proc = subprocess.run([sys.executable, str(BASE / "moe_train_entry.py"), "--manifest", str(out / manifest),
                           "--splits", str(out / "SYNTHETIC_SPLITS.json"), *flags],
                          capture_output=True, text=True, cwd=BASE, timeout=30)
    cli.append({"attempt_id": trial + "_" + name, "exit_code": proc.returncode,
                "stdout": proc.stdout, "stderr": proc.stderr,
                "expected_behavior": proc.returncode == code and marker in proc.stdout + proc.stderr})
import torch
report = {"trial_id": trial, "status": "PASS" if result.wasSuccessful() and all(c["expected_behavior"] for c in cli) else "FAIL_PRESERVED",
          "tests_run": result.testsRun, "failures": [(str(t), e) for t, e in result.failures],
          "errors": [(str(t), e) for t, e in result.errors], "cli": cli,
          "torch_version": torch.__version__, "cuda_initialized": torch.cuda.is_initialized(),
          "actual_upstream_full_package_imported": False,
          "fixed_source_ast_method_bodies_executed_with_cpu_stubs": True,
          "native_data_policy_physics_weights_training_or_remote_used": False,
          "scope": "WHOLE_MOE_E0_W35_H1_E2_E3_GATE; synthetic interface only",
          "git_status": "PENDING_ROOT_SUPPLEMENTAL_GIT"}
(out / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"trial_id": trial, "status": report["status"], "tests_run": result.testsRun,
                  "cli_expected": all(c["expected_behavior"] for c in cli), "cuda_initialized": torch.cuda.is_initialized()}))
print(str(out / "RESULT.json"))
sys.exit(0 if report["status"] == "PASS" else 1)

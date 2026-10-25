"""Run synthetic CPU interface tests and append unique evidence reports."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import sys
import unittest

# Set before any optional torch import; this is a CPU-only test process.
os.environ["CUDA_VISIBLE_DEVICES"] = ""
BASE = Path(__file__).resolve().parent
REPORTS = BASE / "reports"
REPORTS.mkdir(exist_ok=True)
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
identity = f"METHOD_CPU_SYNTHETIC_INTERFACE_{stamp}"
output = io.StringIO()
loader = unittest.TestLoader()
suite = loader.loadTestsFromName("test_contract_cpu")
torch_present = importlib.util.find_spec("torch") is not None
if torch_present:
    suite.addTests(loader.loadTestsFromName("test_adapter_cpu"))
result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
log = REPORTS / f"{identity}.log.txt"
log.write_text(output.getvalue(), encoding="utf-8")
from test_contract_cpu import fixture
raw, split = fixture()
fixture_path = BASE / "synthetic_example_manifest.json"
split_path = BASE / "synthetic_example_split.json"
# Identical fixtures can be referenced by SHA; never overwrite earlier failures.
for path, content in ((fixture_path, raw), (split_path, split)):
    body = json.dumps(content, indent=2, allow_nan=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != body:
        raise RuntimeError(f"Preserve prior fixture before changing it: {path}")
    if not path.exists():
        path.write_text(body, encoding="utf-8")
report = {"trial_id": identity, "observed_utc": stamp,
          "type": "PURE_CPU_SYNTHETIC_INTERFACE_TEST_NOT_H1_RESULT",
          "status": "PASS" if result.wasSuccessful() else "FAIL_PRESERVED",
          "tests_run": result.testsRun,
          "failures": [{"test": str(test), "traceback": trace} for test, trace in result.failures],
          "errors": [{"test": str(test), "traceback": trace} for test, trace in result.errors],
          "skipped": [(str(test), why) for test, why in result.skipped],
          "python": sys.version, "python_executable": sys.executable,
          "platform": platform.platform(), "torch_present": torch_present,
          "torch_version": sys.modules["torch"].__version__ if "torch" in sys.modules else None,
          "torch_cuda_initialized": sys.modules["torch"].cuda.is_initialized() if "torch" in sys.modules else None,
          "synthetic_only": True, "training_ready": False,
          "gpu_rollout_policy_inference_model_download_install_remote_or_training": False,
          "log": str(log), "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
          "git_status": "PENDING_ROOT_UNIFIED_ARCHIVE",
          "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in BASE.glob("*.py")}}
path = REPORTS / f"{identity}.json"
path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("trial_id", "status", "tests_run", "torch_present", "torch_cuda_initialized")}))
print(str(path))
sys.exit(0 if result.wasSuccessful() else 1)

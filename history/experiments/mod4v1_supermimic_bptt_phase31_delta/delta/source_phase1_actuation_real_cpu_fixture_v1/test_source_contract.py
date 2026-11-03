"""SOURCE/AST/stdlib tests only. Never imports Torch or calls run_fixture."""
from pathlib import Path
import ast
import hashlib
import io
import json
import sys
import unittest
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
before_torch = "torch" in sys.modules
import real_cpu_fixture as fixture
import source_pins


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (HERE / "real_cpu_fixture.py").read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.text)
        cls.functions = {n.name: n for n in cls.tree.body if isinstance(n, ast.FunctionDef)}

    def test_import_does_not_load_torch(self):
        self.assertEqual("torch" in sys.modules, before_torch)
        imports = []
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Import): imports.extend(a.name for a in n.names)
            elif isinstance(n, ast.ImportFrom): imports.append(n.module)
        self.assertEqual(set(imports), {"pathlib", "types", "hashlib", "inspect"})

    def test_compile_without_execution(self):
        compile(self.text, "real_cpu_fixture.py", "exec")

    def test_no_top_level_call_to_cpu_fixture(self):
        calls = [n for n in self.tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)]
        self.assertEqual(calls, [])
        self.assertNotIn("__main__", self.text)

    def test_injection_signature_is_explicit(self):
        fn = self.functions["run_fixture"]
        self.assertEqual([a.arg for a in fn.args.args], ["torch_module", "PhysicsActionQueue", "tap_module"])
        self.assertEqual([a.arg for a in fn.args.kwonlyargs], ["n", "seed"])

    def test_missing_real_torch_is_unknown_not_fake_fallback(self):
        with self.assertRaises(fixture.FixtureUnknown): fixture.validate_injections(None, None, None)
        self.assertNotIn("FakeQueue", self.text)
        classes = {n.name for n in self.tree.body if isinstance(n, ast.ClassDef)}
        self.assertEqual(classes, {"FixtureUnknown", "_OriginalReturnProbe", "FakeAsset", "FakeActionTerm", "FakeEnv"})

    def test_n2_n3_nine_lag_pairs(self):
        for n in (2, 3):
            plan = fixture.build_plan(n)
            self.assertEqual(len(plan), 9)
            self.assertEqual({(x["lags"]["legs"], x["lags"]["wheels"]) for x in plan}, {(a, b) for a in range(3) for b in range(3)})
            self.assertTrue(all(x["n"] == n for x in plan))

    def test_two_control_eight_ticks_and_partial_reset_plan(self):
        for x in fixture.build_plan():
            self.assertEqual(x["controls"], [0, 8])
            self.assertEqual(x["physics_ticks"], list(range(16)))
            self.assertEqual(x["partial_reset_ids"], [1])
        self.assertEqual(9 * 2 * 8 * len(fixture.WIDTHS), 288)

    def test_invalid_n_is_rejected(self):
        for n in (0, 1, 4, True, 2.0):
            with self.assertRaises(ValueError): fixture.build_plan(n)

    def test_original_source_signatures_and_old_seals(self):
        result = source_pins.verify()
        self.assertEqual(result["old_members_unchanged"], 17)
        self.assertEqual(result["original_submit_return"], "None")
        self.assertEqual(result["original_apply_return"], "g['applied'].clone()")
        self.assertFalse(result["real_torch_cpu_executed"])

    def test_original_pins_match_injection_constants(self):
        pins = list(source_pins.SOURCES.values())
        self.assertEqual(pins[0], fixture.QUEUE_SHA256)
        self.assertEqual(pins[2], fixture.TAP_SHA256)
        body = json.loads((HERE / "SOURCE_PINS.json").read_text(encoding="utf-8"))
        self.assertEqual(body, source_pins.verify())

    def test_full_queue_fields_and_bytewise_tensor_comparator(self):
        self.assertEqual(len(fixture.FIELDS), 12)
        self.assertEqual(fixture.WIDTHS, {"legs": 4, "wheels": 2})
        body = ast.unparse(self.functions["_equal"])
        self.assertIn("view(torch.uint8)", body)
        self.assertIn("torch.equal(a, b)", body)
        whole = ast.unparse(self.functions["_full_state"])
        self.assertIn("queue.state_dict()", whole)
        self.assertIn("original_attributes", whole)

    def test_cpu_only_no_global_seed_or_state_rewrite(self):
        self.assertNotIn("import torch", self.text)
        self.assertNotIn("cuda", self.text.lower())
        self.assertNotIn("manual_seed(", self.text)
        self.assertNotIn("set_rng_state(", self.text)
        self.assertNotIn("load_state_dict(", self.text)
        self.assertIn("torch.get_rng_state().clone()", self.text)
        self.assertIn("queue.state_dict()", self.text)

    def test_no_fixture_file_network_or_driver_execution_calls(self):
        forbidden = {"write_text", "write_bytes", "open", "save", "load", "step", "backward", "optimizer", "connect", "system", "popen", "exec", "eval"}
        calls = {n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id if isinstance(n.func, ast.Name) else "" for n in ast.walk(self.tree) if isinstance(n, ast.Call)}
        self.assertFalse(calls & forbidden)
        self.assertIn("reset", calls)  # original CPU component reset, not env reset
        self.assertNotIn("_reset_idx", calls)

    def test_assertions_cover_identity_owned_overflow_restore(self):
        for marker in ("Queue apply return identity changed", "Writer argument identity changed", "Writer return identity changed", "Original exception identity changed", "captured-Tensor-not-return-alias", "sameTick/rejected-call-state-unchanged", "global-physics-clock-preserved", "first-latency-not-held-age", "Overflow was promoted to complete coverage", "Tap did not restore probe identity"):
            self.assertIn(marker, self.text)
        self.assertIn("probe.remove()", self.text)
        self.assertIn('if start == 8 and tick == 8', self.text)

    def test_fixture_never_calls_static_or_physical_readback(self):
        self.assertNotIn("get_joint", self.text)
        self.assertNotIn("get_masses", self.text)
        self.assertNotIn("snapshot_static(", self.text)
        self.assertIn('"physical_readback": "UNKNOWN"', self.text)
        self.assertIn('"actor35": "NOT_TESTED"', self.text)
        self.assertIn('"actual_sdk_pass": False', self.text)


def main():
    requested = sys.argv[1:]
    if requested not in ([], ["--receipt"]): raise SystemExit("Use no args, or --receipt once")
    if requested and any((HERE / n).exists() for n in ("SOURCE_TEST_LOG.txt", "SOURCE_RECEIPT.json")):
        raise SystemExit("SOURCE receipt already frozen; run without --receipt")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
    text = stream.getvalue()
    print(text, end="")
    if requested:
        if not result.wasSuccessful(): raise SystemExit("SOURCE tests failed; receipt not written")
        pins = source_pins.verify()
        receipt = {"version": 1, "status": "SOURCE_AST_STDLIB_FIXTURE_CONTRACT_PASS_REAL_CPU_PENDING",
                   "created_utc": datetime.now(timezone.utc).isoformat(), "tests_run": result.testsRun,
                   "errors": len(result.errors), "failures": len(result.failures), "source_count": len(pins["sources"]),
                   "old_members_unchanged": 17, "old_seals_unchanged": True, "real_torch_cpu_executed": False,
                   "original_queue_execution": "PENDING_PARENT_INJECTED_TORCH_CPU_RUN",
                   "actual_sdk_pass": False, "gate1_admitted": False, "exact": False,
                   "runtime_source_binding": "UNKNOWN", "physical_readback": "UNKNOWN", "actor35": "NOT_TESTED",
                   "no_torch_import": ("torch" in sys.modules) == before_torch,
                   "test_log_sha256": hashlib.sha256(text.encode()).hexdigest(), "stage2": False}
        for name, data in (("SOURCE_TEST_LOG.txt", text), ("SOURCE_RECEIPT.json", json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")):
            with (HERE / name).open("x", encoding="utf-8", newline="\n") as f: f.write(data)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__": raise SystemExit(main())

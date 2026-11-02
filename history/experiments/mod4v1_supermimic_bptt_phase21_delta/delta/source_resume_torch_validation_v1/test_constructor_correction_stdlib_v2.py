"""Local stdlib-only V2 source delta checks. This is not a Torch execution."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V1 = HERE / 'test_resume_legacy_torch_cpu_v1.py'
V2 = HERE / 'test_resume_legacy_torch_cpu_v2.py'
T1 = V1.read_text(encoding='utf-8')
T2 = V2.read_text(encoding='utf-8')
A1, A2 = ast.parse(T1), ast.parse(T2)
D = lambda node: ast.dump(node, include_attributes=False)
F1 = {node.name: node for node in ast.walk(A1) if isinstance(node, ast.FunctionDef)}
F2 = {node.name: node for node in ast.walk(A2) if isinstance(node, ast.FunctionDef)}


class ConstructorCorrectionSourceChecks(unittest.TestCase):
    def test_frozen_v1_and_new_v2_SHA(self):
        self.assertEqual(hashlib.sha256(V1.read_bytes()).hexdigest(), '08c89b3603eb7b32b4eb430a9cde112035ca187695272ee992742ceb147079d7')
        self.assertEqual(hashlib.sha256(V2.read_bytes()).hexdigest(), '4a4141259410702d2103952a828be31a7ddaf28057272b69bbf8a8bde3109e55')

    def test_import_V2_does_not_load_Torch_or_SDK(self):
        self.assertNotIn('torch', sys.modules)
        spec = importlib.util.spec_from_file_location('_constructor_delta_stdlib_v2', V2)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertNotIn('torch', sys.modules)
        self.assertFalse(any(name == 'isaaclab' or name.startswith('isaaclab.') for name in sys.modules))
        self.assertTrue(callable(module.run))

    def test_snapshot_is_before_single_real_loader(self):
        start = T2.index("restored, fresh_env, restored_teacher, restored_snapshot = make_learner")
        before = T2.index('initializations_before_load = fresh_env.fresh_initializations', start)
        load = T2.index('pinned_read_and_load(restored, read_task)', before)
        after = T2.index('initializations_after_load = fresh_env.fresh_initializations', load)
        collect = T2.index('restored.collect(1)', after)
        continued = T2.index('initializations_after_continue = fresh_env.fresh_initializations', collect)
        self.assertTrue(start < before < load < after < collect < continued)
        self.assertIn('initializations_before_load == 1 and fresh_env.calls == 0', T2)
        self.assertIn('fresh_env.calls == 0 and initializations_after_load == initializations_before_load == 1', T2)
        self.assertIn('fresh_env.calls == 1 and initializations_after_continue == initializations_before_load == 1', T2)

    def test_all_non_delta_functions_identical(self):
        self.assertEqual(set(F1), set(F2))
        for name in F1:
            if name not in ('run', 'one_variant', 'main'):
                self.assertEqual(D(F1[name]), D(F2[name]), name)

    def test_real_vendor_constructor_cause_and_loader_no_reset(self):
        vendor = ast.parse((ROOT / 'source_core_review/evidence/learner.py').read_text(encoding='utf-8'))
        methods = {node.name: node for node in ast.walk(vendor) if isinstance(node, ast.FunctionDef)}
        critic = ast.unparse(methods['_critic_input_dim'])
        info = ast.unparse(methods['_state_info'])
        self.assertIn('self._state_info()', critic)
        self.assertIn('self.env.init_state()', info)
        core = ast.parse((ROOT / 'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py').read_text(encoding='utf-8'))
        load = next(node for node in ast.walk(core) if isinstance(node, ast.FunctionDef) and node.name == 'load_full_checkpoint')
        for node in ast.walk(load):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, ('init_state', 'reset'))

    def test_source_plan_restore_guards_unchanged(self):
        for name in ('make_learner', 'pinned_read_and_load', 'assert_all_restored', 'rng_sequence_probe', 'assert_teacher', 'write_own_synthetic'):
            self.assertEqual(D(F1[name]), D(F2[name]))
        self.assertIn('synthetic_initialization_counts=dict(before_full_load=initializations_before_load', T2)
        self.assertIn('SYNTHETIC_TORCH_RESUME_RECEIPT_V2.json', T2)
        self.assertNotIn('SYNTHETIC_TORCH_RESUME_RECEIPT_V1.json', T2)

    def test_original_CPU_failure_is_not_erased_or_counted_as_pass(self):
        receipt = json.loads((ROOT / 'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V1.json').read_bytes())
        self.assertEqual(receipt['returncode'], 1)
        self.assertFalse(receipt['receipt']['passed'])
        self.assertIn('assert fresh_env.calls == fresh_env.fresh_initializations == 0', receipt['stderr'])
        self.assertEqual(receipt['native_expert_BPTT_steps'], 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ConstructorCorrectionSourceChecks))
    value = dict(kind='STDLIB_SOURCE_ONLY_CONSTRUCTOR_EXPECTATION_DELTA_V2_NOT_TORCH', passed=result.wasSuccessful(),
                 tests_run=result.testsRun, failures=[str(error) for _, error in result.failures], errors=[str(error) for _, error in result.errors],
                 elapsed_seconds=time.perf_counter() - started, Torch_imported='torch' in sys.modules,
                 SDK_imports=0, real_checkpoint_reads=0, actual_training_updates=0, native_expert_BPTT_updates=0)
    with Path(args.output).open('x', encoding='utf-8') as stream: json.dump(value, stream, indent=2)
    print(json.dumps(value, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__': main()

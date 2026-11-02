"""Eight focused v2 delta tests: real unchanged App/Base imports plus fake stage.

Prior 20 V1 tests are historical, not re-run or counted as new results.
"""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


s = load('close_dep_stager_v2', HERE / 'stage_a1_microbatch_eval_v2.py')
old_fixture = load('previous_fixture_constructor_only', PROJECT / 'source_stage_a1_microbatch_eval_v1' / 'test_stage_a1_microbatch_stdlib_v1.py')
# In-memory fixture destination override ONLY. No old-source or old-directory writes.
old_fixture.HERE = HERE
BASE = PROJECT / 'source_resume_runtime_v2' / 'resume_runtime_contracts_v3.py'
OLD_INDEX = PROJECT / 'source_frozen_eval_microbatch_parent_v1' / 'MICROBATCH_STAGE_INDEX_V1.json'
INDEX = HERE / 'MICROBATCH_STAGE_INDEX_V2.json'


class DeltaFixtures(unittest.TestCase):
    def setUp(self):
        old_fixture.StageFixtures.setUp(self)
        old_fixture.write(self.index, INDEX.read_bytes())
        if self._testMethodName != 'test_05_original_thirteen_real_import_fails_before_stage':
            old_fixture.write(self.flat / 'resume_runtime_contracts_v3.py', BASE.read_bytes())

    def tearDown(self):
        old_fixture.StageFixtures.tearDown(self)

    def prepare(self):
        return s.prepare(self.old, self.old_plan, self.flat, self.index, self.native, self.new,
                         self.new.name, 'GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', vendor_pin=self.vendor_pin)

    def test_01_fourteen_index_preserves_every_original_entry_and_pin(self):
        old = json.loads(OLD_INDEX.read_bytes()); new = json.loads(INDEX.read_bytes())
        self.assertEqual(new['entries'][:13], old['entries']); self.assertEqual(len(new['entries']), 14)
        self.assertEqual(new['entries'][13]['relative'], 'resume_runtime_contracts_v3.py')
        self.assertEqual((new['entries'][13]['bytes'], new['entries'][13]['SHA256']), s.DEPENDENCY_PIN)
        sources, _ = s.source_mappings(self.flat, self.index)
        self.assertEqual(set(sources), s.ALIASES); self.assertEqual(len(sources), 14)

    def test_02_real_App_and_full_contracts_import_in_preflight(self):
        prepared = self.prepare(); proof = prepared['metadata_validation']['dependency_completeness']
        self.assertTrue(proof['passed']); self.assertTrue(proof['helper_base_is_actual_imported_contracts'])
        self.assertEqual(proof['modules']['contracts']['bytes'], 22337)
        self.assertEqual(proof['modules']['contracts']['SHA256'], s.DEPENDENCY_PIN[1])
        self.assertTrue(proof['modules']['AppV6']['full_original_module'])
        self.assertFalse(proof['modules']['AppV6']['AST_cropped_or_stubbed'])
        self.assertFalse(self.new.exists()); self.assertNotIn('torch', sys.modules)
        self.assertNotIn('isaacsim', sys.modules); self.assertNotIn('omni', sys.modules)

    def test_03_fake_new_stage_installs_fourteenth_and_reimports_real_complete_helpers(self):
        prepared = self.prepare(); result = s.stage(prepared)
        proof = result['metadata_validation']['dependency_completeness']
        self.assertTrue(proof['passed']); self.assertEqual(result['source_files'], len(prepared['materials']))
        self.assertEqual((self.new / 'resume_runtime_contracts_v3.py').read_bytes(), BASE.read_bytes())
        plan = json.loads((self.new / 'GROUP_PLAN.json').read_bytes())
        rows = [r for r in plan['worker_files'] if r['relative'] == 'resume_runtime_contracts_v3.py']
        self.assertEqual(rows, [dict(relative='resume_runtime_contracts_v3.py', bytes=22337, SHA=s.DEPENDENCY_PIN[1])])
        self.assertTrue((self.new / 'STAGE_COMPLETE_MICROBATCH_V2.json').exists())
        self.assertEqual(plan['requested_roles'], ['E3', 'W35']); self.assertEqual(len(plan['roles']), 8)
        self.assertIsNone(plan['overall_eight_pass_rate']); self.assertEqual(result['parent_launches'], 0)
        for rel in s.ALIASES: self.assertEqual(s.identity(self.new / rel), prepared['materials'][rel][1])
        with self.assertRaisesRegex(ValueError, 'already exists'): s.stage(prepared)

    def test_04_real_transitive_import_closure_is_stdlib_plus_one_full_base(self):
        proof = self.prepare()['metadata_validation']['dependency_completeness']
        stdlib = set(sys.stdlib_module_names) | {'__future__'}
        self.assertLessEqual(set(proof['modules']['contracts']['import_roots']), stdlib)
        self.assertEqual(set(proof['modules']['AppV6']['import_roots']) - stdlib, {'resume_runtime_contracts_v3'})
        self.assertIsNone(proof['actual_SimulationApp_binding']); self.assertFalse(proof['actual_close_or_wait_performed'])
        self.assertEqual(proof['model_C_lock_SDK_GPU_operations'], 0)

    def test_05_original_thirteen_real_import_fails_before_stage(self):
        names = ('app_close_semantics_v5', 'resume_runtime_contracts_v3')
        before = {name: sys.modules.get(name) for name in names}; path = list(sys.path)
        try:
            for name in names: sys.modules.pop(name, None)
            sys.path.insert(0, str(self.flat))
            spec = importlib.util.spec_from_file_location(names[0], self.flat / 'app_close_semantics_v6.py')
            app = importlib.util.module_from_spec(spec); sys.modules[names[0]] = app
            with self.assertRaisesRegex(ModuleNotFoundError, "resume_runtime_contracts_v3"):
                spec.loader.exec_module(app)  # Actual complete V6 helper: reproduces original line-23 failure.
        finally:
            sys.path[:] = path
            for name, module in before.items():
                if module is None: sys.modules.pop(name, None)
                else: sys.modules[name] = module
        with self.assertRaises(FileNotFoundError): self.prepare()
        self.assertFalse(self.new.exists())

    def test_06_changed_base_bytes_are_blocked_not_stubbed_or_silently_repaired(self):
        old_fixture.write(self.flat / 'resume_runtime_contracts_v3.py', b'"""wrong incomplete base"""\n')
        with self.assertRaisesRegex(ValueError, 'flat source pin differs'): self.prepare()
        self.assertFalse(self.new.exists())

    def test_07_unrelated_stage_scope_model_resource_parent_functions_AST_unchanged(self):
        old_path = PROJECT / 'source_stage_a1_microbatch_eval_v1' / 'stage_a1_microbatch_eval_v1.py'
        old = old_path.read_bytes(); new = (HERE / 'stage_a1_microbatch_eval_v2.py').read_bytes()
        self.assertEqual((len(old), hashlib.sha256(old).hexdigest()),
            (29335, 'dff8143d2464f82f720497ddfe4c241cfd4846e938a9f975962defdaac8c893b'))
        functions = lambda raw: {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef)}
        left, right = functions(old), functions(new)
        self.assertEqual({name for name in left if left[name] != right[name]},
                         {'source_mappings', 'metadata_validate', 'preflight_summary', 'stage'})
        self.assertEqual(set(right) - set(left), {'verify_close_dependency_imports'})
        self.assertEqual((len(OLD_INDEX.read_bytes()), hashlib.sha256(OLD_INDEX.read_bytes()).hexdigest()),
            (4529, '42e4714c8adf4361351e052d4006f863452fbad557343cc22f9dbad21951beaf'))

    def test_08_metadata_IO_guards_remain_and_imported_modules_are_restored(self):
        names = ('a1_frozen_eval_runtime_v2', 'frozen_eval_microbatch_runtime_v1', 'app_close_semantics_v5', 'resume_runtime_contracts_v3')
        before = {name: sys.modules.get(name) for name in names}
        prepared = self.prepare(); value = prepared['metadata_validation']
        self.assertGreaterEqual(value['model_lstats_avoided'], 2)
        self.assertIsNone(value['physical_checkpoint_containment_observed'])
        self.assertEqual(value['model_opens'], value['resources_acquired']); self.assertEqual(value['model_opens'], 0)
        for name in names: self.assertIs(sys.modules.get(name), before[name])
        self.assertEqual(prepared['boundary']['checkpoint_stat_hash_open_decode'], 0)


if __name__ == '__main__':
    start = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DeltaFixtures))
    receipt = dict(kind='V2_CLOSE_DEPENDENCY_REAL_IMPORT_AND_SYNTHETIC_STAGE_TESTS', tests_run=result.testsRun,
        failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(), seconds=time.monotonic()-start,
        real_complete_AppV6_and_contracts_imported=True, original_thirteen_missing_dependency_reproduced=True,
        old_V1_tests_rerun=False, prior_twenty_tests_historical_only=True,
        torch_imported='torch' in sys.modules, actual_native_stage_dispatch_or_SDK_C_PT_operations=0,
        source_level_import_checks_not_actual_native_App_close=True)
    with (HERE / 'TEST_RESULTS_CLOSE_DEPENDENCY_V2.json').open('w', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=2)
    raise SystemExit(0 if result.wasSuccessful() else 1)

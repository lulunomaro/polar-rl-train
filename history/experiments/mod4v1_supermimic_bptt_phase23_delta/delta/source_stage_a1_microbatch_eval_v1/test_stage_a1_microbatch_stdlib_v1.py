"""Stdlib fixtures only; no real native directory, PT, NPZ, SDK, resource or dispatch."""
from pathlib import Path
import copy
import importlib.util
import json
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('new_microbatch_stager_tested', HERE / 'stage_a1_microbatch_eval_v1.py')
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
PROJECT = HERE.parent
INDEX = PROJECT / 'source_frozen_eval_microbatch_parent_v1' / 'MICROBATCH_STAGE_INDEX_V1.json'
OLD_METADATA = PROJECT.parent / 'mod4v1_experts_fulldr_rm70_20261101' / 'reports' / 'NINE_SINGLE_GPU_V8_CLOSED_20261102_101543' / 'GROUP_PLAN.json'


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)


def put(path, value):
    write(path, json.dumps(value, indent=2).encode())


class StageFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='_fixture_', dir=HERE)
        self.base = Path(self.temp.name).resolve()
        self.old = self.base / s.ORIGINAL_GROUP_ID
        self.native = self.base / s.NATIVE_RUN_ID
        self.flat = self.base / 'flat_sources'
        self.new = self.base / 'NEW_QUALITY_E3_W35_FIXTURE'
        index, _ = s.metadata(INDEX)
        self.index = self.base / 'portable_index.json'; write(self.index, INDEX.read_bytes())
        for entry in index['entries']:
            write(self.flat / entry['path'].replace('\\', '/').rsplit('/', 1)[-1], Path(entry['path']).read_bytes())
        old, _ = s.metadata(OLD_METADATA)
        # Synthetic static bytes only: never read a real asset, NPZ, NPY, model or runtime.
        old_files = []
        for item in old['worker_files']:
            raw = b'"""synthetic full source, never executed"""\n' if item['relative'].endswith('.py') else b'fixture-only-static'
            path = self.old / item['relative']; write(path, raw)
            old_files.append(dict(relative=item['relative'], **s.identity(path)))
        old['worker_files'] = old_files
        for row in old['roles']:
            role = row['role']; runtime = self.old / 'runtimes' / role
            row['runtime_root'] = str(runtime); row['asset_dir'] = str(runtime / 'runtime' / 'assets')
            write(runtime / 'runtime' / 'assets' / 'robot.usd', b'synthetic usd')
            write(runtime / 'runtime' / 'full_entry.py', b'"""unshortened fixture entry"""\n')
            write(runtime / 'lib' / 'all_dependency.py', b'"""whole fixture dependency"""\n')
            write(runtime / 'static_contact.npz', b'synthetic fixture NOT a real NPZ')
            write(runtime / 'static_physics.npy', b'synthetic fixture NOT a real NPY')
            (runtime / 'models').mkdir(parents=True)
            write(runtime / 'models' / 'DO_NOT_INSPECT', b'not inspected')
        self.old_plan = self.old / 'GROUP_PLAN.json'; put(self.old_plan, old)
        self.entries = []; rows = {}; go = {}
        for role in s.ROLES:
            key = 'supermimic_' + role.lower() + '_72'; job = self.native / 'roles' / role
            entry = dict(role=role, role_key=key, job_root=str(job)); self.entries.append(entry)
            count = 2182 if role == 'E3' else 1973 if role == 'W35' else 0
            counts = {name: 0 for name in s.COUNTS}
            for name in ('policy_attempts', 'pi_optimizer_steps', 'pi_bptt_optimizer_steps'): counts[name] = count
            checkpoint = dict(path=str(job / 'production' / 'checkpoints' / ('model_BPTT%06d_complete.pt' % count)),
                bytes=1000, SHA='a' * 64, counts=counts, teacher_unchanged=True,
                full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
            final = dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', passed_execution=True,
                teacher_unchanged=True, role=role, role_key=key, run_id=s.NATIVE_RUN_ID,
                actor_view='raw35_legacy_held_aux_v1', algorithm_family='a1_raw35_legacy_v1',
                algorithm_variant='A1_RAW35_FRESH', counts=counts, actual_BPTT_policy_steps=count,
                target_reached=False, parent_finite_saved_stop=True, checkpoint=checkpoint)
            semantic = dict(kind='ACTUAL_WAIT_APP_CLOSE_SEMANTIC_RESULT_V5', passed_execution=True,
                original_error=False, actual_wait_returned=True, returncode=0, reasons=[], error_sidefiles=[], final=final,
                original_V4_result=dict(original_error=True, reasons=['original_close_completion_missing']))
            row = dict(key=key, role=role, phase='terminal', terminal_all_own_children_waited=True,
                returncode=0, original_error=False, final=final, semantic_result=semantic)
            rows[key] = row; go[key] = dict(role=role, role_key=key, run_id=s.NATIVE_RUN_ID)
            put(job / 'PARENT_WAITED_ACTUAL.json', row); put(job / 'production' / 'FINAL.json', final)
        put(self.native / 'OWNER_PLAN.json', dict(run_id=s.NATIVE_RUN_ID, entries=self.entries))
        put(self.native / 'OWNER_EXIT_ACTUAL.json', dict(run_id=s.NATIVE_RUN_ID,
            all_own_children_waited=True, original_cost_settled=True, original_leases_released=True, errors=[], H1_excluded=True))
        put(self.native / 'COHORT_FINAL.json', dict(run_id=s.NATIVE_RUN_ID, rows=rows, go=go,
            all_own_children_waited=True, original_cost_settled=True, errors=[], H1_excluded=True, pending_unstarted_roles=[]))
        self.vendor = self.native / 'roles' / 'E3' / 'worker_sources' / 'supermimic_vendor_v2'
        for name in ('networks.py', 'geometry.py', 'contract.py'):
            write(self.vendor / name, (self.flat / name).read_bytes())
        for name in ('__init__.py', 'learner.py', 'replay.py', 'normalizer.py'):
            write(self.vendor / name, b'"""whole synthetic vendor module, never imported"""\n')
        self.vendor_pin = tuple(s.digest_tree(s.tree(self.vendor))[k] for k in ('files', 'SHA'))

    def tearDown(self):
        # Verify exact own computed absolute target before deleting test fixtures.
        self.assertEqual(Path(self.temp.name).resolve(), self.base)
        self.assertEqual(self.base.parent, HERE)
        self.assertTrue(self.base.name.startswith('_fixture_'))
        self.temp.cleanup()

    def prepare(self):
        return s.prepare(self.old, self.old_plan, self.flat, self.index, self.native, self.new,
                         self.new.name, 'GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', vendor_pin=self.vendor_pin)

    def mutate(self, path, change):
        obj, _ = s.metadata(path); change(obj); put(path, obj)

    def test_01_full_preflight_runs_complete_pinned_cli_without_new_root_or_PT(self):
        prepared = self.prepare()
        self.assertFalse(self.new.exists())
        self.assertEqual(prepared['metadata_validation']['requested_roles'], ['E3', 'W35'])
        self.assertGreaterEqual(prepared['metadata_validation']['model_lstats_avoided'], 2)
        self.assertEqual(prepared['metadata_validation']['model_opens'], 0)
        self.assertNotIn('torch', sys.modules)

    def test_02_stage_once_full_static_arrays_vendor_and_thirteen_aliases(self):
        prepared = self.prepare(); result = s.stage(prepared)
        self.assertTrue(result['staged']); self.assertEqual(result['parent_launches'], 0)
        self.assertEqual(result['metadata_validation']['resources_acquired'], 0)
        for rel in s.ALIASES:
            self.assertEqual(s.identity(self.new / rel), prepared['materials'][rel][1])
        for role in s.ROLES:
            self.assertEqual((self.new / 'runtimes' / role / 'static_contact.npz').read_bytes(), b'synthetic fixture NOT a real NPZ')
            self.assertTrue((self.new / 'runtimes' / role / 'lib' / 'all_dependency.py').is_file())
            self.assertFalse((self.new / 'runtimes' / role / 'models').exists())
        self.assertEqual(len(list((self.new / 'supermimic_vendor_v2').iterdir())), 7)
        with self.assertRaisesRegex(ValueError, 'already exists'): s.stage(prepared)

    def test_03_own_final_one_read_and_source_not_mother(self):
        prepared = self.prepare(); plan = prepared['plan']; by = {r['role']: r for r in plan['roles']}
        self.assertEqual(len(by), 8); self.assertEqual(by['E3']['source_path'], by['E3']['a1_producer']['FINAL']['checkpoint']['path'])
        self.assertNotEqual(by['E3']['source_path'], by['E3']['historical_mother_source']['source_path'])
        self.assertEqual(prepared['boundary']['producer_evidence']['E3']['FINAL_byte_reads'], 1)
        self.assertEqual(by['W35']['a1_producer']['FINAL']['actual_BPTT_policy_steps'], 1973)
        for role in s.ROLES[2:]: self.assertIsNone(by[role]['a1_producer'])
        self.assertIsNone(plan['overall_eight_pass_rate']); self.assertIsNone(plan['comparison'])
        self.assertIsNone(plan['W35_moving_or_standing_rate_from_combined_events'])

    def test_04_bad_native_lease_stops_before_any_new_root(self):
        self.mutate(self.native / 'OWNER_EXIT_ACTUAL.json', lambda d: d.update(original_leases_released=False))
        with self.assertRaisesRegex(ValueError, 'not closed'): self.prepare()
        self.assertFalse(self.new.exists())

    def test_05_original_error_and_nonzero_remain_errors(self):
        self.mutate(self.native / 'COHORT_FINAL.json', lambda d: d['rows'][self.entries[0]['role_key']].update(original_error=True))
        with self.assertRaisesRegex(ValueError, 'terminal row failed'): self.prepare()

    def test_06_waited_final_mismatch_stops(self):
        path = self.native / 'roles' / 'E3' / 'production' / 'FINAL.json'
        self.mutate(path, lambda d: d.update(parent_finite_saved_stop=False))
        with self.assertRaisesRegex(ValueError, 'actual FINAL differs'): self.prepare()

    def test_07_worker_error_sidefile_stops(self):
        put(self.native / 'roles' / 'W35' / 'production' / 'WORKER_ERROR.json', {'actual_error': True})
        with self.assertRaisesRegex(ValueError, 'error sidefile'): self.prepare()

    def test_08_wrong_flat_source_pin_stops(self):
        write(self.flat / 'frozen_eval_microbatch_runtime_v1.py', b'"""changed"""\n')
        with self.assertRaisesRegex(ValueError, 'source pin differs'): self.prepare()

    def test_09_index_paths_are_provenance_and_original_bytes_pinned(self):
        sources, receipt = s.source_mappings(self.flat, self.index)
        self.assertEqual(len(sources), 13); self.assertTrue(receipt['provenance_paths_not_dereferenced'])
        self.assertTrue(all(p.parent == self.flat for p, _ in sources.values()))
        self.index.write_bytes(self.index.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'index pin differs'): self.prepare()

    def test_10_static_pin_wrong_and_original_control_drift_stop(self):
        write(self.old / 'pinned_assets' / 'robot.usd', b'changed')
        with self.assertRaisesRegex(ValueError, 'worker-file pin differs'): self.prepare()

    def test_11_scope_drift_stops_full_metadata_validation(self):
        self.mutate(self.old_plan, lambda d: next(r for r in d['roles'] if r['role'] == 'E3').update(controls=159))
        with self.assertRaisesRegex(ValueError, 'controls differ'): self.prepare()

    def test_12_incomplete_vendor_does_not_get_repaired_or_cropped(self):
        write(self.vendor / '__init__.py', b'import torch\n')
        altered = s.digest_tree(s.tree(self.vendor)); self.vendor_pin = (altered['files'], altered['SHA'])
        with self.assertRaisesRegex(ValueError, 'docstring only'): self.prepare()

    def test_13_denied_entries_are_not_classified(self):
        class Entry:
            name = 'models'
            def is_symlink(self): raise AssertionError('denied name was classified')
        class Entries:
            def __enter__(self): return iter([Entry()])
            def __exit__(self, *args): return False
        with patch.object(s.os, 'scandir', return_value=Entries()): self.assertEqual(s.tree(self.old), {})

    def test_14_escaped_alias_invalid_and_model_identity_blocked(self):
        for value in ('../x.py', '/x.py', 'a\\b.py', 'a//b.py', 'F:/x.py'):
            with self.assertRaises(ValueError): s.safe_relative(value)
        with self.assertRaisesRegex(ValueError, 'denied path'): s.identity(self.base / 'does_not_exist.pt')

    def test_15_stage_failure_consumes_new_root_and_records_not_dispatch(self):
        prepared = self.prepare()
        with patch.object(s, 'metadata_validate', side_effect=ValueError('fixture metadata failure')):
            with self.assertRaisesRegex(ValueError, 'fixture metadata failure'): s.stage(prepared)
        self.assertTrue((self.new / 'STAGE_ERROR_MICROBATCH_V1.json').is_file())
        self.assertFalse((self.new / 'STAGE_COMPLETE_MICROBATCH_V1.json').exists())
        with self.assertRaisesRegex(ValueError, 'must not exist'): self.prepare()

    def test_16_model_resolution_is_lexical_only_under_full_cli_guard(self):
        prepared = self.prepare()
        self.assertIsNone(prepared['metadata_validation']['physical_checkpoint_containment_observed'])
        self.assertFalse(prepared['metadata_validation']['parent_or_worker_executed'])
        self.assertEqual(prepared['boundary']['checkpoint_stat_hash_open_decode'], 0)
        self.assertNotIn('frozen_a1_raw35_v1', sys.modules)


if __name__ == '__main__':
    started = time.monotonic(); suite = unittest.defaultTestLoader.loadTestsFromTestCase(StageFixtures)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = dict(kind='STDLIB_SYNTHETIC_MICROBATCH_STAGER_TESTS_V1', tests_run=result.testsRun,
        failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(),
        seconds=time.monotonic() - started, torch_imported='torch' in sys.modules,
        real_native_or_source_stage_or_dispatch=0, real_PT_stat_read_hash_decode=0,
        original_raw_NPZ_NPY_reads=0, real_C_locks_SDK_GPU_GO_operations=0,
        fixtures_only=True, full_sealed_microbatch_metadata_CLI_executed=True)
    put(HERE / 'TEST_RESULTS_STDLIB_STAGER_V1.json', receipt)
    raise SystemExit(0 if result.wasSuccessful() else 1)

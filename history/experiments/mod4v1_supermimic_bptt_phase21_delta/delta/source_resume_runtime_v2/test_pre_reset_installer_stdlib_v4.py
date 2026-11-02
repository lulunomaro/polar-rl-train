"""Stdlib fake stable installer + AST checks only; actual adapter/native is not run."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import resume_runtime_install_hook_v4 as hook

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = Path(tempfile.mkdtemp(prefix='PRE_RESET_HOOK_SYNTHETIC_CASES_', dir=HERE))
MODULE = 'pose_cache_runtime_adapter_v3'
FAKE_SOURCE = '''calls = []
def install_pose_cache_runtime_adapter_v3(robot, *, receipt_callback):
    calls.append(robot)
    receipt_callback({'event': 'installed', 'synthetic_fixture_only': True})
    return {'synthetic_handle': True}
'''


def fixture():
    job = Path(tempfile.mkdtemp(prefix='job_', dir=CASES))
    sources = job / 'worker_sources';sources.mkdir()
    raw = FAKE_SOURCE.encode('utf-8')
    (sources / (MODULE + '.py')).write_bytes(raw)
    descriptor = dict(kind='POSE_CACHE_RUNTIME_ADAPTER_V3', module=MODULE,
                      symbol='install_pose_cache_runtime_adapter_v3',
                      source_relative='worker_sources/' + MODULE + '.py',
                      SHA=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                      install_timing='after_build_env_before_only_original_reset')
    (job / 'INSTALL_MANIFEST.json').write_text(json.dumps({'files': [dict(relative=descriptor['source_relative'], SHA=descriptor['SHA'], bytes=descriptor['bytes'])]}), encoding='utf-8')
    class Scene:
        def __init__(self): self.lookups = []
        def __getitem__(self, key):
            self.lookups.append(key)
            if key != 'robot': raise AssertionError('unexpected scene access')
            return 'SYNTHETIC_ROBOT_HANDLE_NO_GETTERS'
    class Env:
        scene = Scene()
        def __getattr__(self, name): raise AssertionError('unexpected env getter ' + name)
    return job, descriptor, Env()


class InstallerTests(unittest.TestCase):
    def tearDown(self):
        module = sys.modules.get(MODULE)
        if module is not None:
            self.assertTrue(Path(module.__file__).resolve().is_relative_to(CASES.resolve()))
            sys.modules.pop(MODULE)

    def test_optional_absent_does_no_env_access(self):
        handle, receipt = hook.install_optional_pose_cache_runtime_adapter(object(), {}, CASES, callback=lambda event: self.fail('unexpected callback'))
        self.assertIsNone(handle);self.assertEqual(receipt['install_calls'], 0)

    def test_exact_stable_keyword_api_one_robot_lookup_and_callback(self):
        job, descriptor, env = fixture();events = []
        handle, receipt = hook.install_optional_pose_cache_runtime_adapter(env, {'pose_cache_runtime_adapter': descriptor}, job, callback=events.append)
        self.assertEqual(handle, {'synthetic_handle': True})
        self.assertEqual(env.scene.lookups, ['robot'])
        self.assertEqual(events, [{'event': 'installed', 'synthetic_fixture_only': True}])
        self.assertEqual(receipt['install_calls'], 1)

    def test_duplicate_import_install_is_not_retried(self):
        job, descriptor, env = fixture()
        hook.install_optional_pose_cache_runtime_adapter(env, {'pose_cache_runtime_adapter': descriptor}, job, callback=lambda event: None)
        with self.assertRaises(ValueError): hook.install_optional_pose_cache_runtime_adapter(env, {'pose_cache_runtime_adapter': descriptor}, job, callback=lambda event: None)
        self.assertEqual(len(sys.modules[MODULE].calls), 1)

    def test_wrong_module_or_api_is_rejected(self):
        job, descriptor, env = fixture()
        for key, value in [('module', '../other'), ('symbol', 'NativeTaskBridge'), ('source_relative', '../escape.py')]:
            bad = dict(descriptor);bad[key] = value
            with self.assertRaises(ValueError): hook.validate_pose_cache_installer_descriptor(bad)

    def test_wrong_timing_rejected(self):
        job, descriptor, env = fixture();descriptor['install_timing'] = 'after_reset'
        with self.assertRaises(ValueError): hook.validate_pose_cache_installer_descriptor(descriptor)

    def test_manifest_mismatch_before_any_robot_access(self):
        job, descriptor, env = fixture();descriptor['SHA'] = '0' * 64
        with self.assertRaises(ValueError): hook.install_optional_pose_cache_runtime_adapter(env, {'pose_cache_runtime_adapter': descriptor}, job, callback=lambda event: None)
        self.assertEqual(env.scene.lookups, [])

    def test_changed_source_before_import_and_robot_access(self):
        job, descriptor, env = fixture()
        with (job / descriptor['source_relative']).open('a', encoding='utf-8') as stream: stream.write('\n# changed synthetic source\n')
        with self.assertRaises(ValueError): hook.install_optional_pose_cache_runtime_adapter(env, {'pose_cache_runtime_adapter': descriptor}, job, callback=lambda event: None)
        self.assertEqual(env.scene.lookups, []);self.assertNotIn(MODULE, sys.modules)

    def test_pure_owner_a1_metadata_preserves_installer_and_no_resume(self):
        job, descriptor, env = fixture()
        entry = dict(actor_view=hook.RAW35_ACTOR_VIEW, algorithm_variant='A1_RAW35_FRESH', pose_cache_runtime_adapter=descriptor)
        out = hook.bind_future_task_extensions({'seed': 11}, entry)
        self.assertEqual(out['pose_cache_runtime_adapter'], descriptor)
        self.assertNotIn('resume_bptt', out)

    def test_installer_before_only_original_reset_before_command_bridge(self):
        path = HERE / 'worker_supermimic_bptt_pre_reset_candidate_v4.py'
        source = path.read_text(encoding='utf-8');tree = ast.parse(source)
        resets = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'env' and n.func.attr == 'reset']
        self.assertEqual(len(resets), 1)
        self.assertLess(source.index('install_optional_pose_cache_runtime_adapter(env,task,J'), source.index('reset=env.reset()'))
        self.assertLess(source.index('reset=env.reset()'), source.index('bind_original_command_after_fresh_reset(env,role,obs)'))
        self.assertLess(source.index('bind_original_command_after_fresh_reset(env,role,obs)'), source.index('bridge=BridgeClass('))
        self.assertIn('pose_cache_handle,pose_cache_adapter=', source)

    def test_original_owner_all_nonmain_functions_globals_unchanged(self):
        for new, old in [('supermimic_original_owner_pre_reset_candidate_v4.py', 'supermimic_original_owner.py'),
                         ('supermimic_original_owner_shared_pre_reset_candidate_v4.py', 'supermimic_original_owner_shared_v2.py')]:
            a = ast.parse((HERE / new).read_text(encoding='utf-8'))
            b = ast.parse((ROOT / 'source_runtime' / old).read_text(encoding='utf-8'))
            protected = lambda tree: [ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.Assign)) and getattr(n, 'name', None) != 'main']
            self.assertEqual(protected(a), protected(b))

    def test_original_cfg_and_finite_guard_unchanged(self):
        a = ast.parse((HERE / 'worker_supermimic_bptt_pre_reset_candidate_v4.py').read_text(encoding='utf-8'))
        b = ast.parse((ROOT / 'source_runtime/worker_supermimic_bptt.py').read_text(encoding='utf-8'))
        config = lambda tree: next(n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'SuperMimicConfig')
        self.assertEqual(ast.dump(config(a), include_attributes=False), ast.dump(config(b), include_attributes=False))
        first_guard = lambda tree: next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'before_action').body[0]
        self.assertEqual(ast.dump(first_guard(a), include_attributes=False), ast.dump(first_guard(b), include_attributes=False))

    def test_no_actual_adapter_torch_sdk_or_account(self):
        self.assertNotIn('torch', sys.modules)
        self.assertFalse(any(name.startswith(('isaaclab', 'isaacsim', 'omni.')) for name in sys.modules))
        source = (HERE / 'resume_runtime_install_hook_v4.py').read_text(encoding='utf-8')
        self.assertNotIn('env.reset(', source)
        self.assertNotIn('heading_w', source)
        self.assertNotIn('projected_gravity', source)
        self.assertNotIn('get_observations(', source)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(InstallerTests))
    receipt = dict(kind='STDLIB_SYNTHETIC_PRE_RESET_INSTALLER_API_AND_AST_NOT_ACTUAL_ADAPTER_OR_NATIVE', tests_run=result.testsRun,
                   passed=result.wasSuccessful(), failures=len(result.failures), errors=len(result.errors),
                   fixture_root=str(CASES), Torch_imported='torch' in sys.modules,
                   actual_pose_cache_adapter_installed=0, real_checkpoint_bytes_opened=0, SDK_imports=0,
                   GPU_operations=0, native_runs=0, training_updates=0, original_account_C_lock_operations=0)
    with (HERE / 'TEST_RESULTS_PRE_RESET_INSTALLER_STDLIB_V4.json').open('x', encoding='utf-8') as stream: json.dump(receipt, stream, indent=2)
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)

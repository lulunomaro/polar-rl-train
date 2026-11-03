"""Six NEW stdlib metadata/AST checks only. Never import/execute cpu_fixture.

No Torch, B4/Field/codec/original source module, old suite or parent runner import.
Compilation returns a code object only; all functional numerical results pending.
"""
import ast
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
TEXT = (HERE / 'cpu_fixture.py').read_text(encoding='utf-8')
TREE = ast.parse(TEXT)
PINS = json.loads((HERE / 'SOURCE_PINS.json').read_text(encoding='utf-8'))


def functions(tree):
    return [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]


class SourceFixtureTests(unittest.TestCase):
    def test01_compile_only_no_target_import(self):
        code = compile(TEXT, str(HERE / 'cpu_fixture.py'), 'exec', dont_inherit=True)
        self.assertEqual(code.co_name, '<module>')
        imports = set()
        for node in ast.walk(TREE):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom):
                imports.add(node.module)
        self.assertEqual(imports, {'collections', 'hashlib', 'json', 'pathlib', 'random', 'types'})
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                             and node.func.id in {'exec', 'eval', '__import__', 'runpy'}
                             for node in ast.walk(TREE)))
        self.assertNotIn("if __name__ ==", TEXT)

    def test02_exact_injection_and_default_verifier_before_attach(self):
        run = next(node for node in TREE.body if isinstance(node, ast.FunctionDef) and node.name == 'run_fixture')
        self.assertEqual([arg.arg for arg in run.args.args],
                         ['torch_module', 'real_sensor_class', 'real_delay_class'])
        self.assertEqual([arg.arg for arg in run.args.kwonlyargs],
                         ['codec_module', 'passive_module', 'field_module', 'dependency_module'])
        self.assertIsNone(run.args.vararg)
        self.assertIsNone(run.args.kwarg)
        pair = next(node for node in functions(run) if node.name == 'pair')
        verify = [node for node in ast.walk(pair) if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Attribute) and node.func.attr == 'verify_typed_dependency']
        self.assertEqual(len(verify), 1)
        self.assertEqual(verify[0].keywords, [])
        attach = [node for node in ast.walk(pair) if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Attribute) and node.func.attr == 'attach']
        self.assertEqual(len(attach), 1)
        self.assertLess(verify[0].lineno, attach[0].lineno)
        self.assertIn("len(dependency['checked_functions']) == 22", TEXT)
        self.assertIn("len(dependency['classes']) == 3", TEXT)
        forbidden = {'preflight', '_preflight_impl', 'install_passive_capture'}
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                             and node.func.attr in forbidden for node in ast.walk(TREE)))
        self.assertIn('native_binding_preflight_executed=False', TEXT)

    def test03_explicit_cpu_constructors_and_no_runtime_export_callback(self):
        constructors = {'arange', 'zeros', 'full', 'tensor'}
        for node in ast.walk(TREE):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in constructors:
                    device = next((kw.value for kw in node.keywords if kw.arg == 'device'), None)
                    self.assertIsInstance(device, ast.Constant)
                    self.assertEqual(device.value, 'cpu')
                self.assertNotIn(node.func.attr, {'cuda', 'to', 'item', 'tolist', 'cpu', 'is_initialized',
                                                  'manual_seed', 'set_rng_state', 'nonzero', 'write_text',
                                                  'write_bytes', 'unlink', 'mkdir'})
        env = next(node for node in TREE.body if isinstance(node, ast.ClassDef) and node.name == 'OWN_CPU_FAKE_ENV')
        self.assertNotIn('FakeTensor', TEXT)
        reset = next(node for node in env.body if isinstance(node, ast.FunctionDef) and node.name == '_reset_idx')
        self.assertIn("self.reset_mode != 'metadata_only_fake_return'", ast.unparse(reset))
        self.assertIn("raise self.reset_error", ast.unparse(reset))

    def test04_complete_pinned_callbacks_forward_once_without_oracle_operations(self):
        b4 = Path(PINS['B4']['directory'])
        tree = ast.parse((b4 / 'passive_capture.py').read_text(encoding='utf-8'))
        passive = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'PassiveCapture')
        attach = next(node for node in passive.body if isinstance(node, ast.FunctionDef) and node.name == 'attach')
        expected = {'feedback': 'original_feedback', 'sensor_apply': 'original_sensor',
                    'delay_apply': 'original_delay', 'update': 'original_update',
                    'terminal': 'original_term', 'reset': 'original_reset'}
        callbacks = {node.name: node for node in attach.body if isinstance(node, ast.FunctionDef)}
        self.assertEqual(set(callbacks), set(expected))
        forbidden = {'cpu', 'tolist', 'item', 'get_rng_state', 'getstate', 'get_state',
                     'state_dict', 'rand', 'randn', 'randint', 'nonzero', 'compute_observations',
                     'sensor_sdk_audit', 'clean_policy'}
        for name, original in expected.items():
            calls = [node for node in ast.walk(callbacks[name]) if isinstance(node, ast.Call)]
            forwarded = [node for node in calls if isinstance(node.func, ast.Name) and node.func.id == original]
            # Foreign env's feedback branch also has a separate early pass-through.
            self.assertEqual(len(forwarded), 2 if name == 'feedback' else 1)
            self.assertFalse(any(isinstance(node.func, ast.Attribute) and node.func.attr in forbidden for node in calls))
        field_tree = ast.parse((b4 / 'field_snapshot.py').read_text(encoding='utf-8'))
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                             and node.func.attr in forbidden for node in ast.walk(field_tree)))

    def test05_separate_denominators_pending_and_metadata_negative_scopes(self):
        labels = {node.args[0].value for node in ast.walk(TREE) if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Name) and node.func.id == 'pair'
                  and node.args and isinstance(node.args[0], ast.Constant)}
        self.assertEqual(labels, {'main64', 'idle_cache_partialreset', 'off_identity',
                                 'real_original_apply_exceptions', 'raised_partial_original_reset',
                                 'bad_ID_metadata_fake_original_return', 'missing_END_truncated_caller'})
        self.assertIn("main['normal_channel_records'] == owned_records == 640", TEXT)
        self.assertIn("normal_channel_records=0", TEXT)
        self.assertIn("reset_schedule = {0: [], 20: [79], 37: [78, 79], 40: list(range(79)), 50: list(range(80))}", TEXT)
        segment = TEXT[TEXT.index('# Synthetic original ENV reset'):TEXT.index('# Metadata-only negative')]
        self.assertNotIn('raised.end_control(', segment)
        self.assertNotIn('raised.finish(', segment)
        self.assertIn("error is env.reset_error", segment)
        self.assertIn("real_class_malformed_ID_reset_executed=False", TEXT)
        self.assertIn("'OBSERVED_METADATA_FAILED'", TEXT)
        self.assertIn("MISSING_NORMAL:end:", TEXT)
        self.assertIn("natural_clock_or_reset_evidence=False", TEXT)
        self.assertIn("exact=False, Gate1='UNKNOWN', stage2_GO=False", TEXT)

    def test06_full_source_pins_and_seals_unchanged(self):
        for section, count in (('B4', 21), ('codec', 7)):
            package = PINS[section]
            directory = Path(package['directory'])
            seal_blob = Path(package['seal']['path']).read_bytes()
            self.assertEqual((len(seal_blob), hashlib.sha256(seal_blob).hexdigest()),
                             (package['seal']['bytes'], package['seal']['sha256']))
            self.assertEqual(len(package['files']), count)
            root = hashlib.sha256(json.dumps(package['files'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            self.assertEqual(root, package['content_root_sha256'])
            for name, row in package['files'].items():
                blob = (directory / name).read_bytes()
                self.assertEqual((len(blob), hashlib.sha256(blob).hexdigest()), (row['bytes'], row['sha256']))
        for section in ('original_complete_cpu_sources', 'read_only_reference_sources'):
            for row in PINS[section].values():
                blob = Path(row['path']).read_bytes()
                self.assertEqual((len(blob), hashlib.sha256(blob).hexdigest()), (row['bytes'], row['sha256']))
        self.assertEqual(PINS['original_complete_cpu_sources']['sensor_mild_math.py']['sha256'],
                         'aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8')
        self.assertEqual(PINS['original_complete_cpu_sources']['feedback_delay_mild.py']['sha256'],
                         '90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665')


if __name__ == '__main__':
    unittest.main(verbosity=2)

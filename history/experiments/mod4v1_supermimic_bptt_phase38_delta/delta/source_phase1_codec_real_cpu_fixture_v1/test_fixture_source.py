"""Static SOURCE checks only: never import or invoke cpu_fixture or Torch."""
import ast
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


class FixtureSourceTests(unittest.TestCase):
    def setUp(self):
        self.text = (HERE / 'cpu_fixture.py').read_text(encoding='utf-8')
        self.tree = ast.parse(self.text)

    def test_01_injection_only_compiles_without_loading(self):
        self.assertLessEqual(len(self.text.splitlines()), 150)
        self.assertEqual([n.names[0].name for n in self.tree.body if isinstance(n, ast.Import)], ['json', 'random'])
        self.assertTrue(all(isinstance(n, (ast.Expr, ast.Import, ast.FunctionDef)) for n in self.tree.body))
        funcs = [n for n in self.tree.body if isinstance(n, ast.FunctionDef)]
        self.assertEqual([n.name for n in funcs], ['run_fixture'])
        self.assertEqual([a.arg for a in funcs[0].args.args], ['torch_module', 'codec_module'])
        self.assertFalse(any(isinstance(n, (ast.Call, ast.If)) for n in self.tree.body))
        compile(self.tree, str(HERE / 'cpu_fixture.py'), 'exec')  # code object only, not exec

    def test_02_explicit_cpu_constructors_rng_boundary_and_no_loader(self):
        calls = [n for n in ast.walk(self.tree) if isinstance(n, ast.Call)]
        attrs = [n.func.attr for n in calls if isinstance(n.func, ast.Attribute)]
        for forbidden in ('cuda', 'rand', 'randn', 'randint', 'manual_seed', 'seed', 'load', 'import_module',
                          'compute_observations', 'compute_obs', 'clean_policy', 'audit', 'state_dict', 'export_resume'):
            self.assertNotIn(forbidden, attrs)
        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr == 'cuda' for n in ast.walk(self.tree)))
        for node in calls:
            if isinstance(node.func, ast.Attribute) and node.func.attr in ('arange', 'zeros', 'full'):
                device = next(k.value for k in node.keywords if k.arg == 'device')
                self.assertIsInstance(device, ast.Constant)
                self.assertEqual(device.value, 'cpu')
            if isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, ('eval', 'exec', '__import__', 'open'))
        self.assertEqual(attrs.count('get_rng_state'), 2)
        self.assertEqual(attrs.count('getstate'), 2)
        first_input = min(n.lineno for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == 'arange')
        rng_lines = sorted(n.lineno for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == 'get_rng_state')
        self.assertLess(rng_lines[0], first_input)
        self.assertGreater(rng_lines[1], max(n.lineno for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == 'materialize'))

    def test_03_synthetic_protocol_and_copy_evidence(self):
        for token in ('ENV_ROWS_WITNESS', 'ENV_IDS_FULL', 'TERMINAL_BOOL_FULL', 'QUEUE_GROUP_FULL',
                      'range(64)', 'for k in (0, 1, 79, 80)', 'control == 37', "outcome='RAISED'",
                      'NOT_OBSERVED', 'OBSERVED', 'prior_termination_event_id', 'normal_channel_records=640',
                      '2 ** 60 + 7', 'is clean', 'is payload', 'untyped_storage', 'data_ptr'):
            self.assertIn(token, self.text)
        self.assertIn("source_ref='SYNTHETIC_CPU_NOT_SDK'", self.text)
        self.assertIn('physical_or_natural_reset_proof=False', self.text)
        pins = json.loads((HERE / 'SOURCE_PINS.json').read_text(encoding='utf-8'))
        codec_path = Path(pins['upstream_codec']['directory']) / 'typed_capture_codec.py'
        original = ast.parse(codec_path.read_text(encoding='utf-8'))
        ledger = next(n for n in original.body if isinstance(n, ast.ClassDef) and n.name == 'ControlLedger')
        for node in ast.walk(ledger):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, ('clone', 'index_select', 'capture', 'cpu', 'tolist'))

    def test_04_frozen_codec_design_and_source_references_unchanged(self):
        pins = json.loads((HERE / 'SOURCE_PINS.json').read_text(encoding='utf-8'))
        self.assertEqual(len(pins['upstream_codec']['files']), 8)
        self.assertEqual(len(pins['upstream_design']['files']), 7)
        for key in ('upstream_codec', 'upstream_design'):
            base = pins[key]
            for name, row in base['files'].items():
                raw = (Path(base['directory']) / name).read_bytes()
                self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (row['bytes'], row['sha256']))
        self.assertEqual(len(pins['unchanged_source_references']), 7)
        for row in pins['unchanged_source_references'].values():
            raw = Path(row['path']).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (row['bytes'], row['sha256']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
